from datetime import date, datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from quant.datahub.config import DataHubConfig
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.quality import LocalRefreshQualityHelper
from quant.datahub.refresh import LocalWarehouseRefreshError, run_local_warehouse_refresh
from quant.datahub.source import SOURCE_AVAILABILITY_HEALTH_CHECK_NAME, SourceRequest
from quant.datahub.storage import LocalStorage


class FixtureDailyBarsAdapter:
    source_name = "fixture_daily_bars_adapter"

    def fetch(self, dataset, *, start_date=None, end_date=None, symbols=None):
        if dataset != DatasetName.DAILY_BARS:
            raise ValueError("Unsupported dataset")
        return [
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


class EmptyDailyBarsAdapter:
    source_name = "fixture_empty_daily_bars"

    def fetch(self, dataset, *, start_date=None, end_date=None, symbols=None):
        if dataset != DatasetName.DAILY_BARS:
            raise ValueError("Unsupported dataset")
        return []


class InvalidDailyBarsAdapter:
    source_name = "fixture_invalid_daily_bars"

    def fetch(self, dataset, *, start_date=None, end_date=None, symbols=None):
        if dataset != DatasetName.DAILY_BARS:
            raise ValueError("Unsupported dataset")
        return [
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": "2024-01-02",
                "open": 10.0,
                "high": 10.2,
                "low": 9.8,
                "volume": 1000.0,
                "amount": 10000.0,
                "adj_factor": 1.0,
                "price_adjustment": "raw",
                "source": "fixture",
                "ingested_at": "2024-01-02T10:00:00",
                "schema_version": "v1",
            }
        ]


class FetchFailureDailyBarsAdapter:
    source_name = "fixture_fetch_failure_daily_bars"

    def fetch(self, dataset, *, start_date=None, end_date=None, symbols=None):
        raise ConnectionError("upstream timeout contacting fixture source")


class UnsupportedRequestDailyBarsAdapter:
    source_name = "fixture_unsupported_request_daily_bars"

    def fetch(self, dataset, *, start_date=None, end_date=None):
        return []


class MetadataFailingStorage(LocalStorage):
    def write_metadata(
        self,
        dataset,
        metadata,
        *,
        layer="meta",
        ext="json",
    ):
        if dataset == DatasetName.DAILY_BARS:
            raise OSError("metadata disk full")
        return super().write_metadata(dataset, metadata, layer=layer, ext=ext)


class QualityReportFailingStorage(LocalStorage):
    def write_records(
        self,
        dataset,
        records,
        *,
        layer="curated",
        ext="jsonl",
        validate_schema=False,
        registry=None,
    ):
        if dataset == DatasetName.DATA_QUALITY_REPORT and layer == "curated":
            raise OSError("quality report disk full")
        return super().write_records(
            dataset,
            records,
            layer=layer,
            ext=ext,
            validate_schema=validate_schema,
            registry=registry,
        )


class LocalWarehouseRefreshRunnerTests(unittest.TestCase):
    def _build_components(self, tmpdir: str, now: datetime):
        registry = DatasetRegistry()
        storage = LocalStorage(config=DataHubConfig(root_dir=Path(tmpdir)))
        quality_helper = LocalRefreshQualityHelper(
            registry=registry,
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.DAILY_BARS,
            source_name="fixture_daily_bars_adapter",
            source_id="fixture_source_id",
            source_catalog_entry_id="fixture_catalog_entry",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 2),
            symbols=("600000.SH",),
        )
        return registry, storage, quality_helper, request

    def test_refresh_success_writes_raw_curated_metadata_and_quality(self) -> None:
        now = datetime(2024, 2, 1, 9, 0, 0, tzinfo=timezone.utc)
        with TemporaryDirectory() as tmpdir:
            registry, storage, quality_helper, request = self._build_components(tmpdir, now)

            result = run_local_warehouse_refresh(
                FixtureDailyBarsAdapter(),
                request,
                storage,
                registry=registry,
                quality_helper=quality_helper,
                fetched_at=datetime(2024, 1, 2, 10, 0, 0, tzinfo=timezone.utc),
            )

            self.assertEqual(result.dataset, DatasetName.DAILY_BARS)
            self.assertEqual(result.source_name, "fixture_daily_bars_adapter")
            self.assertEqual(result.source_id, "fixture_source_id")
            self.assertEqual(result.record_count, 1)
            self.assertEqual(result.refresh_status, "success")
            self.assertTrue(result.success)
            self.assertTrue(result.raw_path.exists())
            self.assertIsNotNone(result.curated_path)
            self.assertTrue(result.curated_path.exists())
            self.assertIsNotNone(result.metadata_path)
            self.assertTrue(result.metadata_path.exists())
            self.assertTrue(result.quality_path.exists())

            curated_records = storage.read_records(DatasetName.DAILY_BARS, layer="curated")
            raw_records = storage.read_records(DatasetName.DAILY_BARS, layer="raw")
            quality_records = storage.read_records(DatasetName.DATA_QUALITY_REPORT, layer="curated")
            metadata = storage.read_metadata(DatasetName.DAILY_BARS)

            self.assertEqual(raw_records, curated_records)
            self.assertEqual(len(curated_records), 1)
            self.assertEqual(registry.validate_record(DatasetName.DAILY_BARS, curated_records[0]), ())

            by_check = {record["check_name"]: record for record in quality_records}
            self.assertEqual(by_check["record_count"]["status"], "pass")
            self.assertEqual(by_check["schema_validation"]["status"], "pass")
            self.assertEqual(by_check["metadata_written"]["status"], "pass")
            self.assertEqual(
                by_check[SOURCE_AVAILABILITY_HEALTH_CHECK_NAME]["status"],
                "pass",
            )
            self.assertEqual(
                by_check[SOURCE_AVAILABILITY_HEALTH_CHECK_NAME]["details"]["failure_category"],
                "success",
            )

            for quality_record in quality_records:
                self.assertEqual(
                    registry.validate_record(DatasetName.DATA_QUALITY_REPORT, quality_record),
                    (),
                )

            self.assertEqual(metadata["dataset"], DatasetName.DAILY_BARS.value)
            self.assertEqual(metadata["source_id"], "fixture_source_id")
            self.assertEqual(metadata["source_name"], "fixture_daily_bars_adapter")
            self.assertEqual(metadata["record_count"], 1)
            self.assertEqual(metadata["status"], "success")
            self.assertEqual(
                metadata["details"]["source_health"]["failure_category"],
                "success",
            )

    def test_empty_records_warn_behavior_is_returned_and_persisted(self) -> None:
        now = datetime(2024, 2, 1, 9, 0, 0, tzinfo=timezone.utc)
        with TemporaryDirectory() as tmpdir:
            registry, storage, quality_helper, request = self._build_components(tmpdir, now)
            request = SourceRequest(
                dataset=request.dataset,
                source_name="fixture_empty_daily_bars",
                source_id=request.source_id,
                source_catalog_entry_id=request.source_catalog_entry_id,
                start_date=request.start_date,
                end_date=request.end_date,
                symbols=request.symbols,
            )

            result = run_local_warehouse_refresh(
                EmptyDailyBarsAdapter(),
                request,
                storage,
                registry=registry,
                quality_helper=quality_helper,
                empty_record_status="warn",
            )

            self.assertEqual(result.record_count, 0)
            self.assertEqual(result.refresh_status, "warning")
            self.assertTrue(result.success)

            quality_records = storage.read_records(DatasetName.DATA_QUALITY_REPORT, layer="curated")
            by_check = {record["check_name"]: record for record in quality_records}
            self.assertEqual(by_check["record_count"]["status"], "warn")
            self.assertEqual(by_check["schema_validation"]["status"], "pass")
            self.assertEqual(by_check["metadata_written"]["status"], "pass")
            self.assertEqual(
                by_check[SOURCE_AVAILABILITY_HEALTH_CHECK_NAME]["status"],
                "warn",
            )
            self.assertEqual(
                by_check[SOURCE_AVAILABILITY_HEALTH_CHECK_NAME]["details"]["failure_category"],
                "empty_result",
            )

    def test_empty_records_fail_behavior_marks_failed_status(self) -> None:
        now = datetime(2024, 2, 1, 9, 0, 0, tzinfo=timezone.utc)
        with TemporaryDirectory() as tmpdir:
            registry, storage, quality_helper, request = self._build_components(tmpdir, now)
            request = SourceRequest(
                dataset=request.dataset,
                source_name="fixture_empty_daily_bars",
                source_id=request.source_id,
                source_catalog_entry_id=request.source_catalog_entry_id,
                start_date=request.start_date,
                end_date=request.end_date,
                symbols=request.symbols,
            )

            result = run_local_warehouse_refresh(
                EmptyDailyBarsAdapter(),
                request,
                storage,
                registry=registry,
                quality_helper=quality_helper,
                empty_record_status="fail",
            )

            self.assertEqual(result.record_count, 0)
            self.assertEqual(result.refresh_status, "failed")
            self.assertFalse(result.success)

            metadata = storage.read_metadata(DatasetName.DAILY_BARS)
            self.assertEqual(metadata["status"], "failed")

            quality_records = storage.read_records(DatasetName.DATA_QUALITY_REPORT, layer="curated")
            by_check = {record["check_name"]: record for record in quality_records}
            self.assertEqual(by_check["record_count"]["status"], "fail")
            self.assertEqual(
                by_check[SOURCE_AVAILABILITY_HEALTH_CHECK_NAME]["status"],
                "fail",
            )

    def test_invalid_curated_records_raise_and_write_failure_metadata_and_quality(self) -> None:
        now = datetime(2024, 2, 1, 9, 0, 0, tzinfo=timezone.utc)
        with TemporaryDirectory() as tmpdir:
            registry, storage, quality_helper, request = self._build_components(tmpdir, now)
            request = SourceRequest(
                dataset=request.dataset,
                source_name="fixture_invalid_daily_bars",
                source_id=request.source_id,
                source_catalog_entry_id=request.source_catalog_entry_id,
                start_date=request.start_date,
                end_date=request.end_date,
                symbols=request.symbols,
            )

            with self.assertRaises(LocalWarehouseRefreshError):
                run_local_warehouse_refresh(
                    InvalidDailyBarsAdapter(),
                    request,
                    storage,
                    registry=registry,
                    quality_helper=quality_helper,
                )

            raw_records = storage.read_records(DatasetName.DAILY_BARS, layer="raw")
            self.assertEqual(len(raw_records), 1)

            curated_path = storage.dataset_file(
                DatasetName.DAILY_BARS,
                layer="curated",
                ext="jsonl",
            )
            self.assertFalse(curated_path.exists())

            metadata = storage.read_metadata(DatasetName.DAILY_BARS)
            self.assertEqual(metadata["status"], "failed")
            self.assertIn("missing_required_field", metadata["details"]["error"])

            quality_records = storage.read_records(DatasetName.DATA_QUALITY_REPORT, layer="curated")
            by_check = {record["check_name"]: record for record in quality_records}
            self.assertEqual(by_check["schema_validation"]["status"], "fail")
            self.assertEqual(by_check["metadata_written"]["status"], "pass")
            self.assertEqual(
                by_check[SOURCE_AVAILABILITY_HEALTH_CHECK_NAME]["details"]["failure_category"],
                "schema_validation_failed",
            )
            self.assertTrue(
                by_check[SOURCE_AVAILABILITY_HEALTH_CHECK_NAME]["details"][
                    "schema_or_data_quality_like"
                ]
            )

    def test_fetch_failures_still_write_standardized_health_metadata_and_quality(self) -> None:
        now = datetime(2024, 2, 1, 9, 0, 0, tzinfo=timezone.utc)
        with TemporaryDirectory() as tmpdir:
            registry, storage, quality_helper, request = self._build_components(tmpdir, now)
            request = SourceRequest(
                dataset=request.dataset,
                source_name="fixture_fetch_failure_daily_bars",
                source_id=request.source_id,
                source_catalog_entry_id=request.source_catalog_entry_id,
                start_date=request.start_date,
                end_date=request.end_date,
                symbols=request.symbols,
            )

            with self.assertRaises(LocalWarehouseRefreshError):
                run_local_warehouse_refresh(
                    FetchFailureDailyBarsAdapter(),
                    request,
                    storage,
                    registry=registry,
                    quality_helper=quality_helper,
                )

            metadata = storage.read_metadata(DatasetName.DAILY_BARS)
            quality_records = storage.read_records(DatasetName.DATA_QUALITY_REPORT, layer="curated")
            by_check = {record["check_name"]: record for record in quality_records}
            health_details = by_check[SOURCE_AVAILABILITY_HEALTH_CHECK_NAME]["details"]

            self.assertEqual(metadata["status"], "failed")
            self.assertEqual(health_details["failure_category"], "fetch_failed")
            self.assertEqual(health_details["availability_status"], "unavailable")
            self.assertTrue(health_details["upstream_or_network_like"])
            self.assertFalse(storage.dataset_file(DatasetName.DAILY_BARS, layer="raw", ext="jsonl").exists())

    def test_unsupported_request_failures_are_not_classified_as_upstream_unavailable(
        self,
    ) -> None:
        now = datetime(2024, 2, 1, 9, 0, 0, tzinfo=timezone.utc)
        with TemporaryDirectory() as tmpdir:
            registry, storage, quality_helper, request = self._build_components(tmpdir, now)
            request = SourceRequest(
                dataset=request.dataset,
                source_name="fixture_unsupported_request_daily_bars",
                source_id=request.source_id,
                source_catalog_entry_id=request.source_catalog_entry_id,
                start_date=request.start_date,
                end_date=request.end_date,
                symbols=request.symbols,
            )

            with self.assertRaises(LocalWarehouseRefreshError):
                run_local_warehouse_refresh(
                    UnsupportedRequestDailyBarsAdapter(),
                    request,
                    storage,
                    registry=registry,
                    quality_helper=quality_helper,
                )

            quality_records = storage.read_records(DatasetName.DATA_QUALITY_REPORT, layer="curated")
            health_details = {
                record["check_name"]: record for record in quality_records
            }[SOURCE_AVAILABILITY_HEALTH_CHECK_NAME]["details"]
            self.assertEqual(health_details["failure_category"], "unsupported_request")
            self.assertEqual(health_details["availability_status"], "unsupported")
            self.assertFalse(health_details["upstream_or_network_like"])
            self.assertTrue(health_details["request_or_configuration_like"])

    def test_metadata_write_failures_surface_standardized_health_quality(self) -> None:
        now = datetime(2024, 2, 1, 9, 0, 0, tzinfo=timezone.utc)
        with TemporaryDirectory() as tmpdir:
            registry = DatasetRegistry()
            storage = MetadataFailingStorage(config=DataHubConfig(root_dir=Path(tmpdir)))
            quality_helper = LocalRefreshQualityHelper(registry=registry, now_fn=lambda: now)
            request = SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                source_name="fixture_daily_bars_adapter",
                source_id="fixture_source_id",
                source_catalog_entry_id="fixture_catalog_entry",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 2),
                symbols=("600000.SH",),
            )

            with self.assertRaises(LocalWarehouseRefreshError):
                run_local_warehouse_refresh(
                    FixtureDailyBarsAdapter(),
                    request,
                    storage,
                    registry=registry,
                    quality_helper=quality_helper,
                )

            quality_records = storage.read_records(DatasetName.DATA_QUALITY_REPORT, layer="curated")
            by_check = {record["check_name"]: record for record in quality_records}
            self.assertEqual(by_check["metadata_written"]["status"], "fail")
            self.assertEqual(
                by_check[SOURCE_AVAILABILITY_HEALTH_CHECK_NAME]["details"]["failure_category"],
                "metadata_write_failed",
            )
            self.assertIn("metadata disk full", by_check["metadata_written"]["details"]["metadata_error"])

    def test_quality_report_persistence_failures_rewrite_metadata_with_health_context(
        self,
    ) -> None:
        now = datetime(2024, 2, 1, 9, 0, 0, tzinfo=timezone.utc)
        with TemporaryDirectory() as tmpdir:
            registry = DatasetRegistry()
            storage = QualityReportFailingStorage(config=DataHubConfig(root_dir=Path(tmpdir)))
            quality_helper = LocalRefreshQualityHelper(registry=registry, now_fn=lambda: now)
            request = SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                source_name="fixture_daily_bars_adapter",
                source_id="fixture_source_id",
                source_catalog_entry_id="fixture_catalog_entry",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 2),
                symbols=("600000.SH",),
            )

            with self.assertRaises(LocalWarehouseRefreshError):
                run_local_warehouse_refresh(
                    FixtureDailyBarsAdapter(),
                    request,
                    storage,
                    registry=registry,
                    quality_helper=quality_helper,
                )

            metadata = storage.read_metadata(DatasetName.DAILY_BARS)
            self.assertEqual(metadata["status"], "failed")
            self.assertEqual(
                metadata["details"]["source_health"]["failure_category"],
                "persistence_failed",
            )
            self.assertNotIn(
                "secondary_failure_categories",
                metadata["details"]["source_health"],
            )
            self.assertFalse(
                storage.dataset_file(
                    DatasetName.DATA_QUALITY_REPORT,
                    layer="curated",
                    ext="jsonl",
                ).exists()
            )

    def test_runner_is_offline_safe_and_does_not_open_network_connections(self) -> None:
        now = datetime(2024, 2, 1, 9, 0, 0, tzinfo=timezone.utc)
        with TemporaryDirectory() as tmpdir:
            registry, storage, quality_helper, request = self._build_components(tmpdir, now)

            with patch(
                "socket.create_connection",
                side_effect=AssertionError("Network access should not be used"),
            ):
                result = run_local_warehouse_refresh(
                    FixtureDailyBarsAdapter(),
                    request,
                    storage,
                    registry=registry,
                    quality_helper=quality_helper,
                )

            self.assertTrue(result.success)
            self.assertEqual(result.record_count, 1)


if __name__ == "__main__":
    unittest.main()
