import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from quant.features.contracts import FeatureName
from quant.scanner.contracts import (
    SCANNER_CONTRACT_SCHEMA_VERSION,
    FeatureReference,
    FilterOperator,
    FilterSpec,
    ScanCandidateList,
    ScanCandidateRecord,
    ScanRunMetadata,
)
from quant.scanner.storage import (
    SCANNER_CANDIDATE_LIST_MANIFEST_VERSION,
    ScannerCandidateListManifest,
    build_scanner_candidate_list_manifest,
    serialize_scanner_candidate_list_manifest,
    write_scan_candidate_list_jsonl,
    write_scanner_candidate_list_manifest,
)


class ScannerStorageTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.candidate_list = ScanCandidateList(
            metadata=ScanRunMetadata(
                run_id="scan-2026-06-04-cn-core",
                scanner_id="foundation_scan",
                trade_date="2026-06-04",
                universe_id="cn-core",
                generated_at=datetime(2026, 6, 4, 9, 30, 0),
            ),
            feature_refs=(
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0),
            ),
            filters=(
                FilterSpec(
                    filter_id="above_ma20",
                    feature_ref=FeatureReference(FeatureName.PRICE_TECHNICAL),
                    operator=FilterOperator.GT,
                    threshold=0.0,
                ),
            ),
            candidates=(
                ScanCandidateRecord(
                    run_id="scan-2026-06-04-cn-core",
                    trade_date="2026-06-04",
                    symbol="000001.SZ",
                    market="CN",
                    universe_id="cn-core",
                    matched_filter_ids=("above_ma20",),
                ),
                ScanCandidateRecord(
                    run_id="scan-2026-06-04-cn-core",
                    trade_date="2026-06-04",
                    symbol="600000.SH",
                    market="CN",
                    universe_id="cn-core",
                    matched_filter_ids=("above_ma20",),
                ),
            ),
        )

    def test_write_candidate_list_jsonl_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "scan.jsonl"
            manifest_path = Path(temp_dir) / "scan.manifest.json"

            manifest = write_scan_candidate_list_jsonl(
                output_path,
                self.candidate_list,
                manifest_path=manifest_path,
            )

            rows = [
                json.loads(line)
                for line in output_path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(
                rows,
                [
                    {
                        "matched_filter_ids": ["above_ma20"],
                        "market": "CN",
                        "run_id": "scan-2026-06-04-cn-core",
                        "symbol": "000001.SZ",
                        "trade_date": "2026-06-04",
                        "universe_id": "cn-core",
                    },
                    {
                        "matched_filter_ids": ["above_ma20"],
                        "market": "CN",
                        "run_id": "scan-2026-06-04-cn-core",
                        "symbol": "600000.SH",
                        "trade_date": "2026-06-04",
                        "universe_id": "cn-core",
                    },
                ],
            )
            manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest_payload["candidate_count"], 2)
            self.assertEqual(manifest_payload["content_checksum"], manifest.content_checksum)
            self.assertEqual(manifest_payload["generated_at"], "2026-06-04T09:30:00")
            self.assertEqual(manifest_payload["schema_version"], SCANNER_CONTRACT_SCHEMA_VERSION)

    def test_manifest_builder_is_deterministic(self) -> None:
        manifest = build_scanner_candidate_list_manifest(self.candidate_list)

        self.assertEqual(
            serialize_scanner_candidate_list_manifest(manifest),
            {
                "candidate_count": 2,
                "content_checksum": manifest.content_checksum,
                "feature_refs": [
                    {"feature_name": "price_technical", "lag_days": 0},
                ],
                "filters": [
                    {
                        "feature_ref": {
                            "feature_name": "price_technical",
                            "lag_days": 0,
                        },
                        "filter_id": "above_ma20",
                        "operator": "gt",
                        "threshold": 0.0,
                    },
                ],
                "generated_at": "2026-06-04T09:30:00",
                "manifest_version": SCANNER_CANDIDATE_LIST_MANIFEST_VERSION,
                "run_id": "scan-2026-06-04-cn-core",
                "scanner_id": "foundation_scan",
                "schema_version": SCANNER_CONTRACT_SCHEMA_VERSION,
                "trade_date": "2026-06-04",
                "universe_id": "cn-core",
            },
        )

    def test_manifest_write_honors_overwrite_flag(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path = Path(temp_dir) / "scan.manifest.json"
            manifest = ScannerCandidateListManifest(
                manifest_version=SCANNER_CANDIDATE_LIST_MANIFEST_VERSION,
                schema_version=SCANNER_CONTRACT_SCHEMA_VERSION,
                run_id="scan-2026-06-04-cn-core",
                scanner_id="foundation_scan",
                trade_date="2026-06-04",
                universe_id="cn-core",
                generated_at="2026-06-04T09:30:00",
                candidate_count=0,
                content_checksum="0" * 64,
                feature_refs=(),
                filters=(),
            )

            write_scanner_candidate_list_manifest(manifest_path, manifest)

            with self.assertRaisesRegex(FileExistsError, "output file already exists"):
                write_scanner_candidate_list_manifest(manifest_path, manifest)

            write_scanner_candidate_list_manifest(
                manifest_path,
                manifest,
                overwrite=True,
            )

    def test_manifest_conflict_does_not_create_partial_records_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "scan.jsonl"
            manifest_path = Path(temp_dir) / "scan.manifest.json"
            manifest_path.write_text("existing manifest\n", encoding="utf-8")

            with self.assertRaisesRegex(FileExistsError, "output file already exists"):
                write_scan_candidate_list_jsonl(
                    output_path,
                    self.candidate_list,
                    manifest_path=manifest_path,
                )

            self.assertFalse(output_path.exists())
            self.assertEqual(
                manifest_path.read_text(encoding="utf-8"),
                "existing manifest\n",
            )

    def test_same_records_and_manifest_path_is_rejected_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "scan.jsonl"

            with self.assertRaisesRegex(ValueError, "must be different"):
                write_scan_candidate_list_jsonl(
                    output_path,
                    self.candidate_list,
                    manifest_path=output_path,
                )

            self.assertFalse(output_path.exists())

    def test_invalid_candidate_list_is_rejected_before_writing(self) -> None:
        invalid_candidate_list = ScanCandidateList(
            metadata=self.candidate_list.metadata,
            feature_refs=self.candidate_list.feature_refs,
            filters=self.candidate_list.filters,
            candidates=(
                self.candidate_list.candidates[1],
                self.candidate_list.candidates[0],
            ),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "scan.jsonl"

            with self.assertRaisesRegex(ValueError, "candidate list failed validation"):
                write_scan_candidate_list_jsonl(output_path, invalid_candidate_list)

            self.assertFalse(output_path.exists())


if __name__ == "__main__":
    unittest.main()
