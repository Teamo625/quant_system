from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from quant.datahub.config import DataHubConfig
from quant.datahub.datasets import DatasetName
from quant.datahub.storage import LocalStorage


class LocalStorageTests(unittest.TestCase):
    def test_storage_resolves_dataset_paths_without_writing(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            storage = LocalStorage(config=DataHubConfig(root_dir=root))

            path = storage.dataset_file(DatasetName.TRADING_CALENDAR)

            self.assertEqual(
                path,
                root / "curated" / "trading_calendar" / "trading_calendar.parquet",
            )
            self.assertFalse(path.exists())

    def test_storage_can_create_dirs_on_demand(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            storage = LocalStorage(config=DataHubConfig(root_dir=root))

            storage.ensure_base_dirs()
            target_dir = storage.dataset_dir(DatasetName.DAILY_BARS, ensure_exists=True)

            self.assertTrue((root / "raw").exists())
            self.assertTrue((root / "curated").exists())
            self.assertTrue((root / "meta").exists())
            self.assertTrue(target_dir.exists())

    def test_storage_rejects_unknown_layer(self) -> None:
        with TemporaryDirectory() as tmpdir:
            storage = LocalStorage(config=DataHubConfig(root_dir=Path(tmpdir)))

            with self.assertRaisesRegex(ValueError, "Unsupported layer"):
                storage.dataset_dir(DatasetName.DAILY_BARS, layer="invalid")

    def test_records_round_trip_jsonl(self) -> None:
        with TemporaryDirectory() as tmpdir:
            storage = LocalStorage(config=DataHubConfig(root_dir=Path(tmpdir)))

            records = [
                {
                    "symbol": "600000.SH",
                    "market": "CN",
                    "trade_date": "2024-01-02",
                    "open": 10.0,
                    "high": 10.2,
                    "low": 9.8,
                    "close": 10.1,
                    "volume": 1000,
                    "amount": 10000,
                    "adj_factor": 1.0,
                    "price_adjustment": "raw",
                    "source": "fixture",
                    "ingested_at": "2024-01-02T10:00:00",
                    "schema_version": "v1",
                }
            ]

            output_path = storage.write_records(DatasetName.DAILY_BARS, records)
            loaded = storage.read_records(DatasetName.DAILY_BARS)

            self.assertTrue(output_path.exists())
            self.assertEqual(loaded, records)

    def test_write_records_creates_parent_directories(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            storage = LocalStorage(config=DataHubConfig(root_dir=root))

            output_path = storage.write_records(
                DatasetName.TRADING_CALENDAR,
                [
                    {
                        "market": "CN",
                        "trade_date": "2024-01-02",
                        "is_open": True,
                        "session_type": "full",
                        "previous_trade_date": "2024-01-01",
                        "next_trade_date": "2024-01-03",
                        "source": "fixture",
                        "ingested_at": "2024-01-02T10:00:00",
                        "schema_version": "v1",
                    }
                ],
            )

            self.assertTrue((root / "curated" / "trading_calendar").exists())
            self.assertTrue(output_path.exists())

    def test_read_records_missing_file_behavior(self) -> None:
        with TemporaryDirectory() as tmpdir:
            storage = LocalStorage(config=DataHubConfig(root_dir=Path(tmpdir)))

            self.assertEqual(storage.read_records(DatasetName.CORPORATE_ACTIONS), [])

            with self.assertRaises(FileNotFoundError):
                storage.read_records(
                    DatasetName.CORPORATE_ACTIONS,
                    on_missing="raise",
                )

    def test_schema_validation_on_write_detects_missing_required_fields(self) -> None:
        with TemporaryDirectory() as tmpdir:
            storage = LocalStorage(config=DataHubConfig(root_dir=Path(tmpdir)))

            with self.assertRaisesRegex(ValueError, "missing_required_field"):
                storage.write_records(
                    DatasetName.DAILY_BARS,
                    [
                        {
                            "symbol": "600000.SH",
                            "market": "CN",
                            "trade_date": "2024-01-02",
                            "open": 10.0,
                        }
                    ],
                    validate_schema=True,
                )

    def test_metadata_round_trip_json(self) -> None:
        with TemporaryDirectory() as tmpdir:
            storage = LocalStorage(config=DataHubConfig(root_dir=Path(tmpdir)))

            metadata = {
                "dataset": "daily_bars",
                "schema_version": "v1",
                "updated_at": "2024-01-02T10:00:00",
            }

            output_path = storage.write_metadata(DatasetName.DAILY_BARS, metadata)
            loaded = storage.read_metadata(DatasetName.DAILY_BARS)

            self.assertTrue(output_path.exists())
            self.assertEqual(loaded, metadata)

    def test_read_metadata_missing_file_behavior(self) -> None:
        with TemporaryDirectory() as tmpdir:
            storage = LocalStorage(config=DataHubConfig(root_dir=Path(tmpdir)))

            self.assertEqual(storage.read_metadata(DatasetName.VALUATION_SNAPSHOT), {})

            with self.assertRaises(FileNotFoundError):
                storage.read_metadata(
                    DatasetName.VALUATION_SNAPSHOT,
                    on_missing="raise",
                )

    def test_storage_io_does_not_require_network(self) -> None:
        with TemporaryDirectory() as tmpdir:
            storage = LocalStorage(config=DataHubConfig(root_dir=Path(tmpdir)))
            with patch(
                "socket.create_connection",
                side_effect=AssertionError("Network access should not be used"),
            ):
                storage.write_records(
                    DatasetName.DATA_QUALITY_REPORT,
                    [
                        {
                            "dataset": "daily_bars",
                            "market": "CN",
                            "trade_date": "2024-01-02",
                            "check_name": "completeness",
                            "status": "pass",
                            "severity": "low",
                            "details": "ok",
                            "created_at": "2024-01-02T10:00:00",
                            "source": "fixture",
                            "ingested_at": "2024-01-02T10:00:01",
                            "schema_version": "v1",
                        }
                    ],
                )
                loaded = storage.read_records(DatasetName.DATA_QUALITY_REPORT)

            self.assertEqual(len(loaded), 1)
