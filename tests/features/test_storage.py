import json
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from quant.datahub.datasets import DatasetName
from quant.features.contracts import (
    FEATURE_VALUE_SCHEMA_VERSION,
    FeatureName,
    FeatureValueRecord,
)
from quant.features.storage import (
    FEATURE_OUTPUT_MANIFEST_VERSION,
    FeatureOutputManifest,
    build_feature_output_manifest,
    deserialize_feature_value_record,
    read_feature_records_jsonl,
    serialize_feature_output_manifest,
    serialize_feature_value_record,
    write_feature_output_manifest,
    write_feature_records_jsonl,
)


class FeatureStorageTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.record = FeatureValueRecord(
            symbol="600000.SH",
            market="CN",
            trade_date=date(2026, 6, 3),
            feature_name=FeatureName.PRICE_TECHNICAL,
            value=1.25,
            source_dataset=DatasetName.DAILY_BARS,
            created_at=datetime(2026, 6, 4, 9, 30, 0, 123456),
            schema_version=FEATURE_VALUE_SCHEMA_VERSION,
        )
        self.second_record = FeatureValueRecord(
            symbol="600000.SH",
            market="CN",
            trade_date=date(2026, 6, 3),
            feature_name=FeatureName.VALUATION,
            value="cheap",
            source_dataset=DatasetName.VALUATION_SNAPSHOT,
            created_at=datetime(2026, 6, 4, 9, 30, 1),
            schema_version=FEATURE_VALUE_SCHEMA_VERSION,
        )

    def test_serialize_and_deserialize_round_trip(self) -> None:
        payload = serialize_feature_value_record(self.record)

        self.assertEqual(
            payload,
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": "2026-06-03",
                "feature_name": "price_technical",
                "value": 1.25,
                "source_dataset": "daily_bars",
                "created_at": "2026-06-04T09:30:00.123456",
                "schema_version": FEATURE_VALUE_SCHEMA_VERSION,
            },
        )
        self.assertEqual(deserialize_feature_value_record(payload), self.record)

    def test_write_and_read_jsonl_round_trip_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "features.jsonl"
            manifest_path = Path(temp_dir) / "features.manifest.json"

            manifest = write_feature_records_jsonl(
                output_path,
                [self.second_record, self.record],
                manifest_path=manifest_path,
            )

            self.assertEqual(
                manifest,
                FeatureOutputManifest(
                    manifest_version=FEATURE_OUTPUT_MANIFEST_VERSION,
                    schema_version=FEATURE_VALUE_SCHEMA_VERSION,
                    record_count=2,
                    feature_names=("price_technical", "valuation"),
                ),
            )
            self.assertEqual(
                read_feature_records_jsonl(output_path),
                (self.second_record, self.record),
            )

            manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(
                manifest_payload,
                {
                    "feature_names": ["price_technical", "valuation"],
                    "manifest_version": FEATURE_OUTPUT_MANIFEST_VERSION,
                    "record_count": 2,
                    "schema_version": FEATURE_VALUE_SCHEMA_VERSION,
                },
            )

    def test_empty_record_list_writes_empty_file_and_zero_count_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "empty.jsonl"

            manifest = write_feature_records_jsonl(output_path, [])

            self.assertEqual(read_feature_records_jsonl(output_path), ())
            self.assertEqual(output_path.read_text(encoding="utf-8"), "")
            self.assertEqual(manifest.record_count, 0)
            self.assertEqual(manifest.feature_names, ())

    def test_manifest_helpers_are_deterministic(self) -> None:
        manifest = build_feature_output_manifest(
            [self.second_record, serialize_feature_value_record(self.record)]
        )

        self.assertEqual(
            serialize_feature_output_manifest(manifest),
            {
                "manifest_version": FEATURE_OUTPUT_MANIFEST_VERSION,
                "schema_version": FEATURE_VALUE_SCHEMA_VERSION,
                "record_count": 2,
                "feature_names": ["price_technical", "valuation"],
            },
        )

    def test_invalid_schema_version_trade_date_and_created_at_are_rejected(self) -> None:
        invalid_payloads = (
            (
                {
                    **serialize_feature_value_record(self.record),
                    "schema_version": "",
                },
                "schema_version must be a non-empty string",
            ),
            (
                {
                    **serialize_feature_value_record(self.record),
                    "schema_version": "9.9.9",
                },
                "unsupported schema_version",
            ),
            (
                {
                    **serialize_feature_value_record(self.record),
                    "trade_date": "2026-06-03T09:30:00",
                },
                "trade_date must be an ISO date string",
            ),
            (
                {
                    **serialize_feature_value_record(self.record),
                    "created_at": "not-a-datetime",
                },
                "created_at must be an ISO datetime string",
            ),
        )

        for payload, expected_message in invalid_payloads:
            with self.assertRaisesRegex(ValueError, expected_message):
                deserialize_feature_value_record(payload)

    def test_invalid_feature_dataset_and_value_are_rejected(self) -> None:
        invalid_payloads = (
            (
                {
                    **serialize_feature_value_record(self.record),
                    "feature_name": "intraday_magic",
                },
                "feature_name must be a supported FeatureName string",
            ),
            (
                {
                    **serialize_feature_value_record(self.record),
                    "source_dataset": "company_announcements",
                },
                "source_dataset must reference an approved DataHub dataset input",
            ),
            (
                {
                    **serialize_feature_value_record(self.record),
                    "value": float("nan"),
                },
                "value must be a finite int, float, or string",
            ),
        )

        for payload, expected_message in invalid_payloads:
            with self.assertRaisesRegex(ValueError, expected_message):
                deserialize_feature_value_record(payload)

    def test_malformed_jsonl_and_invalid_record_rows_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            malformed_path = Path(temp_dir) / "malformed.jsonl"
            malformed_path.write_text("{bad json}\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "malformed JSONL row at line 1"):
                read_feature_records_jsonl(malformed_path)

            invalid_path = Path(temp_dir) / "invalid.jsonl"
            invalid_path.write_text(
                json.dumps(
                    {
                        **serialize_feature_value_record(self.record),
                        "market": "   ",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "market must be a non-empty string"):
                read_feature_records_jsonl(invalid_path)

    def test_parent_directory_missing_and_existing_file_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_parent_path = Path(temp_dir) / "missing" / "features.jsonl"
            existing_path = Path(temp_dir) / "existing.jsonl"
            existing_path.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(
                FileNotFoundError,
                "parent directory does not exist",
            ):
                write_feature_records_jsonl(missing_parent_path, [self.record])

            with self.assertRaisesRegex(FileExistsError, "output file already exists"):
                write_feature_records_jsonl(existing_path, [self.record])

    def test_manifest_write_honors_overwrite_flag(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path = Path(temp_dir) / "manifest.json"
            manifest = build_feature_output_manifest([self.record])

            write_feature_output_manifest(manifest_path, manifest)

            with self.assertRaisesRegex(FileExistsError, "output file already exists"):
                write_feature_output_manifest(manifest_path, manifest)

            write_feature_output_manifest(manifest_path, manifest, overwrite=True)

    def test_manifest_conflict_does_not_create_partial_records_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "features.jsonl"
            manifest_path = Path(temp_dir) / "features.manifest.json"
            manifest_path.write_text("existing manifest\n", encoding="utf-8")

            with self.assertRaisesRegex(FileExistsError, "output file already exists"):
                write_feature_records_jsonl(
                    output_path,
                    [self.record],
                    manifest_path=manifest_path,
                )

            self.assertFalse(output_path.exists())
            self.assertEqual(
                manifest_path.read_text(encoding="utf-8"),
                "existing manifest\n",
            )


if __name__ == "__main__":
    unittest.main()
