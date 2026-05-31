from datetime import date, datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from quant.datahub.config import DataHubConfig
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.quality import LocalRefreshQualityHelper
from quant.datahub.refresh import LocalWarehouseRefreshError, run_local_warehouse_refresh
from quant.datahub.source import SourceRequest
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
