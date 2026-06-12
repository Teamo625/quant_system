from datetime import date, datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from quant.datahub.config import DataHubConfig
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.personal_readiness import (
    build_default_personal_trading_readiness_report,
    build_personal_trading_readiness_quality_kpi_checks,
)
from quant.datahub.quality import LOCAL_QUALITY_SOURCE_ID, LocalRefreshQualityHelper
from quant.datahub.source import SOURCE_AVAILABILITY_HEALTH_CHECK_NAME
from quant.datahub.storage import LocalStorage


class LocalRefreshQualityHelperTests(unittest.TestCase):
    def test_build_refresh_metadata_uses_injectable_clock_and_schema_version(self) -> None:
        now = datetime(2024, 2, 1, 8, 30, 0, tzinfo=timezone.utc)
        helper = LocalRefreshQualityHelper(now_fn=lambda: now)

        metadata = helper.build_refresh_metadata(
            DatasetName.DAILY_BARS,
            layer="curated",
            source_id="akshare_cn_hk_public_family",
            source_name="AKShare CN/HK Public Family",
            record_count=12,
            status="success",
            details={"batch": "unit-test"},
        )

        self.assertEqual(metadata["dataset"], DatasetName.DAILY_BARS.value)
        self.assertEqual(metadata["layer"], "curated")
        self.assertEqual(metadata["source_id"], "akshare_cn_hk_public_family")
        self.assertEqual(metadata["source_name"], "AKShare CN/HK Public Family")
        self.assertEqual(metadata["record_count"], 12)
        self.assertEqual(metadata["status"], "success")
        self.assertEqual(metadata["schema_version"], "v1")
        self.assertEqual(metadata["started_at"], now.isoformat())
        self.assertEqual(metadata["completed_at"], now.isoformat())
        self.assertEqual(metadata["refreshed_at"], now.isoformat())
        self.assertEqual(metadata["details"], {"batch": "unit-test"})

    def test_refresh_metadata_can_be_persisted_and_read_back(self) -> None:
        now = datetime(2024, 2, 1, 8, 30, 0, tzinfo=timezone.utc)
        helper = LocalRefreshQualityHelper(now_fn=lambda: now)

        with TemporaryDirectory() as tmpdir:
            storage = LocalStorage(config=DataHubConfig(root_dir=Path(tmpdir)))
            metadata = helper.build_refresh_metadata(
                DatasetName.MACRO_OBSERVATIONS,
                layer="raw",
                source_id="macro_policy_public_sources",
                record_count=3,
                status="warning",
                details={"note": "partial refresh"},
            )
            output_path = helper.persist_refresh_metadata(
                storage=storage,
                dataset=DatasetName.MACRO_OBSERVATIONS,
                metadata=metadata,
            )
            loaded = helper.read_refresh_metadata(
                storage=storage,
                dataset=DatasetName.MACRO_OBSERVATIONS,
            )

            self.assertTrue(output_path.exists())
            self.assertEqual(loaded, metadata)

    def test_quality_records_pass_for_non_empty_valid_records(self) -> None:
        now = datetime(2024, 2, 1, 9, 0, 0, tzinfo=timezone.utc)
        helper = LocalRefreshQualityHelper(now_fn=lambda: now)
        registry = DatasetRegistry()

        records = [
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": "2024-01-02",
                "open": 10.0,
                "high": 10.2,
                "low": 9.8,
                "close": 10.1,
                "volume": 1000.0,
                "amount": 10000.0,
                "adj_factor": 1.0,
                "price_adjustment": "raw",
                "source": "fixture",
                "ingested_at": "2024-01-02T10:00:00",
                "schema_version": "v1",
            }
        ]
        quality_records = helper.build_quality_report_records(
            dataset=DatasetName.DAILY_BARS,
            market="CN",
            trade_date=date(2024, 1, 2),
            records=records,
            metadata_written=True,
        )

        self.assertEqual(len(quality_records), 3)
        by_check = {record["check_name"]: record for record in quality_records}
        self.assertEqual(by_check["record_count"]["status"], "pass")
        self.assertEqual(by_check["schema_validation"]["status"], "pass")
        self.assertEqual(by_check["metadata_written"]["status"], "pass")

        for record in quality_records:
            self.assertEqual(record["source"], LOCAL_QUALITY_SOURCE_ID)
            self.assertEqual(record["created_at"], now.isoformat())
            self.assertEqual(record["ingested_at"], now.isoformat())
            self.assertEqual(record["schema_version"], "v1")
            self.assertEqual(
                registry.validate_record(DatasetName.DATA_QUALITY_REPORT, record),
                (),
            )

    def test_empty_records_supports_warning_or_failure_policy(self) -> None:
        helper = LocalRefreshQualityHelper(
            now_fn=lambda: datetime(2024, 2, 1, 9, 0, 0, tzinfo=timezone.utc)
        )
        warn_records = helper.build_quality_report_records(
            dataset=DatasetName.MACRO_INDICATOR_MASTER,
            market="CN",
            trade_date=date(2024, 1, 31),
            records=[],
            empty_record_status="warn",
        )
        fail_records = helper.build_quality_report_records(
            dataset=DatasetName.MACRO_INDICATOR_MASTER,
            market="CN",
            trade_date=date(2024, 1, 31),
            records=[],
            empty_record_status="fail",
        )

        warn_by_check = {record["check_name"]: record for record in warn_records}
        fail_by_check = {record["check_name"]: record for record in fail_records}

        self.assertEqual(warn_by_check["record_count"]["status"], "warn")
        self.assertEqual(warn_by_check["record_count"]["severity"], "medium")
        self.assertEqual(warn_by_check["schema_validation"]["status"], "pass")

        self.assertEqual(fail_by_check["record_count"]["status"], "fail")
        self.assertEqual(fail_by_check["record_count"]["severity"], "high")
        self.assertEqual(fail_by_check["schema_validation"]["status"], "pass")

    def test_invalid_dataset_records_produce_schema_validation_failure(self) -> None:
        helper = LocalRefreshQualityHelper(
            now_fn=lambda: datetime(2024, 2, 1, 9, 0, 0, tzinfo=timezone.utc)
        )
        invalid_records = [
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": "2024-01-02",
                "open": 10.0,
            }
        ]
        quality_records = helper.build_quality_report_records(
            dataset=DatasetName.DAILY_BARS,
            market="CN",
            trade_date=date(2024, 1, 2),
            records=invalid_records,
            metadata_written=False,
            metadata_error="metadata write failed",
        )
        by_check = {record["check_name"]: record for record in quality_records}

        schema_record = by_check["schema_validation"]
        self.assertEqual(schema_record["status"], "fail")
        self.assertEqual(schema_record["severity"], "high")
        self.assertGreater(schema_record["details"]["issue_count"], 0)
        self.assertGreater(schema_record["details"]["invalid_record_count"], 0)
        self.assertIn("invalid_records", schema_record["details"])

        metadata_record = by_check["metadata_written"]
        self.assertEqual(metadata_record["status"], "fail")
        self.assertEqual(metadata_record["severity"], "high")
        self.assertEqual(metadata_record["details"]["metadata_written"], False)
        self.assertEqual(metadata_record["details"]["metadata_error"], "metadata write failed")

    def test_quality_records_can_include_standardized_source_health_details(self) -> None:
        helper = LocalRefreshQualityHelper(
            now_fn=lambda: datetime(2024, 2, 1, 9, 0, 0, tzinfo=timezone.utc)
        )
        quality_records = helper.build_quality_report_records(
            dataset=DatasetName.DAILY_BARS,
            market="CN",
            trade_date=date(2024, 1, 2),
            records=[],
            empty_record_status="warn",
            source_health_details={
                "source_id": "fixture_source_id",
                "source_name": "fixture_source",
                "source_catalog_entry_id": "fixture_catalog",
                "requested_dataset": DatasetName.DAILY_BARS.value,
                "requested_date_range": {"start_date": "2024-01-01", "end_date": "2024-01-02"},
                "requested_symbols_count": 0,
                "requested_symbols_preview": [],
                "normalized_record_count": 0,
                "fetch_status": "empty_result",
                "availability_status": "available",
                "failure_category": "empty_result",
                "failure_message": None,
                "operator_actionable": False,
                "upstream_or_network_like": False,
                "schema_or_data_quality_like": False,
                "request_or_configuration_like": False,
                "started_at": "2024-02-01T09:00:00+00:00",
                "fetched_at": None,
                "completed_at": "2024-02-01T09:00:00+00:00",
            },
        )

        by_check = {record["check_name"]: record for record in quality_records}
        source_health_record = by_check[SOURCE_AVAILABILITY_HEALTH_CHECK_NAME]
        self.assertEqual(source_health_record["status"], "warn")
        self.assertEqual(source_health_record["severity"], "medium")
        self.assertEqual(
            source_health_record["details"]["failure_category"],
            "empty_result",
        )

    def test_quality_records_can_include_personal_readiness_kpis(self) -> None:
        now = datetime(2024, 2, 1, 9, 0, 0, tzinfo=timezone.utc)
        helper = LocalRefreshQualityHelper(now_fn=lambda: now)
        registry = DatasetRegistry()
        readiness_report = build_default_personal_trading_readiness_report()

        quality_records = helper.build_quality_report_records(
            dataset=DatasetName.DATA_QUALITY_REPORT,
            market="multi_market",
            trade_date=date(2024, 2, 1),
            records=[
                {
                    "dataset": "daily_bars",
                    "market": "CN",
                    "trade_date": "2024-01-02",
                    "check_name": "record_count",
                    "status": "pass",
                    "severity": "low",
                    "details": {"record_count": 1},
                    "created_at": "2024-01-02T10:00:00",
                    "source": LOCAL_QUALITY_SOURCE_ID,
                    "ingested_at": "2024-01-02T10:00:00",
                    "schema_version": "v1",
                }
            ],
            metadata_written=True,
            additional_checks=build_personal_trading_readiness_quality_kpi_checks(
                report=readiness_report,
            ),
        )

        by_check = {record["check_name"]: record for record in quality_records}
        self.assertEqual(len(quality_records), 7)

        domain_kpi = by_check["personal_trading_readiness_domain_coverage_kpi"]
        self.assertEqual(domain_kpi["status"], "blocked")
        self.assertEqual(
            domain_kpi["details"]["domain_status_counts"],
            {"pass": 4, "warn": 5, "blocked": 1, "fail": 0},
        )
        self.assertTrue(domain_kpi["details"]["observability_only"])
        self.assertFalse(domain_kpi["details"]["proves_adapter_completeness"])

        capability_kpi = by_check["personal_trading_readiness_capability_coverage_kpi"]
        self.assertEqual(capability_kpi["status"], "blocked")
        self.assertEqual(
            capability_kpi["details"]["source_quality_required_capability_status_counts"],
            {"covered": 5, "partial": 0, "missing": 0, "planned": 0},
        )

        queue_kpi = by_check["personal_trading_readiness_follow_up_queue_kpi"]
        self.assertEqual(
            queue_kpi["details"]["follow_up_disposition_counts"]["datahub_hardening"],
            39,
        )
        self.assertEqual(
            queue_kpi["details"]["owner_credential_blocker_follow_up_ids"],
            [
                "index__index_capability_readiness__index_weight_history",
            ],
        )

        batches_kpi = by_check["personal_trading_readiness_follow_up_batches_kpi"]
        self.assertNotIn(
            "quality_reports__datahub_hardening__source__batch_01",
            batches_kpi["details"]["follow_up_batch_ids"],
        )
        self.assertEqual(
            batches_kpi["details"]["owner_waiver_required_batch_ids"],
            [],
        )

        for record in quality_records:
            self.assertEqual(
                registry.validate_record(DatasetName.DATA_QUALITY_REPORT, record),
                (),
            )

    def test_rejects_invalid_empty_record_status(self) -> None:
        helper = LocalRefreshQualityHelper(
            now_fn=lambda: datetime(2024, 2, 1, 9, 0, 0, tzinfo=timezone.utc)
        )
        with self.assertRaisesRegex(ValueError, "Unsupported empty_record_status"):
            helper.build_quality_report_records(
                dataset=DatasetName.DAILY_BARS,
                market="CN",
                trade_date=date(2024, 1, 2),
                records=[],
                empty_record_status="pass",
            )

    def test_rejects_additional_quality_checks_without_required_fields(self) -> None:
        helper = LocalRefreshQualityHelper(
            now_fn=lambda: datetime(2024, 2, 1, 9, 0, 0, tzinfo=timezone.utc)
        )
        with self.assertRaisesRegex(ValueError, "non-empty check_name string"):
            helper.build_quality_report_records(
                dataset=DatasetName.DAILY_BARS,
                market="CN",
                trade_date=date(2024, 1, 2),
                records=[],
                additional_checks=(
                    {
                        "check_name": "",
                        "status": "pass",
                        "severity": "low",
                        "details": {},
                    },
                ),
            )

    def test_quality_helper_is_local_only(self) -> None:
        helper = LocalRefreshQualityHelper(
            now_fn=lambda: datetime(2024, 2, 1, 9, 0, 0, tzinfo=timezone.utc)
        )
        with TemporaryDirectory() as tmpdir:
            storage = LocalStorage(config=DataHubConfig(root_dir=Path(tmpdir)))
            with patch(
                "socket.create_connection",
                side_effect=AssertionError("Network access should not be used"),
            ):
                metadata = helper.build_refresh_metadata(
                    DatasetName.DATA_QUALITY_REPORT,
                    layer="meta",
                    source_id=LOCAL_QUALITY_SOURCE_ID,
                    record_count=1,
                )
                helper.persist_refresh_metadata(
                    storage=storage,
                    dataset=DatasetName.DATA_QUALITY_REPORT,
                    metadata=metadata,
                )
                records = helper.build_quality_report_records(
                    dataset=DatasetName.DATA_QUALITY_REPORT,
                    market="CN",
                    trade_date=date(2024, 2, 1),
                    records=[
                        {
                            "dataset": "daily_bars",
                            "market": "CN",
                            "trade_date": "2024-01-02",
                            "check_name": "record_count",
                            "status": "pass",
                            "severity": "low",
                            "details": {"record_count": 1},
                            "created_at": "2024-01-02T10:00:00",
                            "source": LOCAL_QUALITY_SOURCE_ID,
                            "ingested_at": "2024-01-02T10:00:00",
                            "schema_version": "v1",
                        }
                    ],
                    metadata_written=True,
                )
                loaded = helper.read_refresh_metadata(
                    storage=storage,
                    dataset=DatasetName.DATA_QUALITY_REPORT,
                )

            self.assertEqual(len(records), 3)
            self.assertEqual(loaded["source_id"], LOCAL_QUALITY_SOURCE_ID)


if __name__ == "__main__":
    unittest.main()
