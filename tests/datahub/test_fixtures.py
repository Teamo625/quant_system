from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from quant.datahub.config import DataHubConfig
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.storage import LocalStorage
from datahub_fixtures import (
    INVALID_REQUIRED_FIXTURE_RECORDS,
    INVALID_TYPED_FIXTURE_RECORDS,
    OFFLINE_FIXTURE_RECORDS,
)


class OfflineFixtureValidationTests(unittest.TestCase):
    def test_fixture_coverage_includes_required_datasets(self) -> None:
        required = {
            DatasetName.INSTRUMENT_MASTER,
            DatasetName.TRADING_CALENDAR,
            DatasetName.DAILY_BARS,
            DatasetName.DATA_QUALITY_REPORT,
        }

        self.assertTrue(required.issubset(set(OFFLINE_FIXTURE_RECORDS)))
        self.assertTrue(required.issubset(set(INVALID_REQUIRED_FIXTURE_RECORDS)))
        self.assertTrue(required.issubset(set(INVALID_TYPED_FIXTURE_RECORDS)))

    def test_valid_fixtures_pass_required_field_validation(self) -> None:
        registry = DatasetRegistry()

        for dataset, records in OFFLINE_FIXTURE_RECORDS.items():
            for record in records:
                with self.subTest(dataset=dataset.value):
                    missing = registry.validate_required_fields(dataset, record)
                    self.assertEqual(missing, ())

    def test_invalid_fixtures_fail_required_field_validation(self) -> None:
        registry = DatasetRegistry()

        for dataset, record in INVALID_REQUIRED_FIXTURE_RECORDS.items():
            with self.subTest(dataset=dataset.value):
                missing = registry.validate_required_fields(dataset, record)
                self.assertGreaterEqual(len(missing), 1)

    def test_invalid_typed_fixtures_fail_type_validation(self) -> None:
        registry = DatasetRegistry()

        for dataset, record in INVALID_TYPED_FIXTURE_RECORDS.items():
            with self.subTest(dataset=dataset.value):
                issues = registry.validate_record(dataset, record)
                self.assertTrue(any(issue.code == "type_mismatch" for issue in issues))

    def test_fixtures_round_trip_through_local_storage_offline(self) -> None:
        with TemporaryDirectory() as tmpdir:
            storage = LocalStorage(config=DataHubConfig(root_dir=Path(tmpdir)))

            with patch(
                "socket.create_connection",
                side_effect=AssertionError("Network access should not be used"),
            ):
                for dataset, records in OFFLINE_FIXTURE_RECORDS.items():
                    with self.subTest(dataset=dataset.value):
                        storage.write_records(
                            dataset,
                            records,
                            validate_schema=True,
                        )
                        loaded = storage.read_records(dataset)
                        self.assertEqual(loaded, records)

    def test_storage_validation_rejects_invalid_typed_fixture(self) -> None:
        with TemporaryDirectory() as tmpdir:
            storage = LocalStorage(config=DataHubConfig(root_dir=Path(tmpdir)))

            with self.assertRaisesRegex(ValueError, "type_mismatch"):
                storage.write_records(
                    DatasetName.DAILY_BARS,
                    [INVALID_TYPED_FIXTURE_RECORDS[DatasetName.DAILY_BARS]],
                    validate_schema=True,
                )
