import importlib
import unittest
from datetime import datetime

from quant.features.contracts import FeatureName
from quant.scanner.contracts import (
    SCANNER_CONTRACT_SCHEMA_VERSION,
    FeatureReference,
    FilterOperator,
    FilterSpec,
    ScanCandidateList,
    ScanCandidateRecord,
    ScanRunMetadata,
    UniverseMembershipInput,
    validate_feature_reference,
    validate_filter_spec,
    validate_scan_candidate_list,
    validate_universe_membership_input,
)


class ScannerContractsTestCase(unittest.TestCase):
    def test_scanner_package_imports_cleanly(self) -> None:
        package = importlib.import_module("quant.scanner")
        module = importlib.import_module("quant.scanner.contracts")

        self.assertTrue(hasattr(package, "UniverseMembershipInput"))
        self.assertTrue(hasattr(package, "FeatureReference"))
        self.assertTrue(hasattr(package, "FilterSpec"))
        self.assertTrue(hasattr(package, "ScanCandidateList"))
        self.assertTrue(hasattr(module, "FilterOperator"))

    def test_valid_scan_candidate_list_passes_validation(self) -> None:
        payload = ScanCandidateList(
            metadata=ScanRunMetadata(
                run_id="scan-2026-06-04-cn-core",
                scanner_id="value_breakout_watchlist",
                trade_date="2026-06-04",
                universe_id="cn-core",
                generated_at=datetime(2026, 6, 4, 9, 30, 0),
            ),
            feature_refs=(
                FeatureReference(
                    feature_name=FeatureName.PRICE_TECHNICAL,
                    lag_days=0,
                ),
                FeatureReference(
                    feature_name=FeatureName.VALUATION,
                    lag_days=1,
                ),
            ),
            filters=(
                FilterSpec(
                    filter_id="close_above_ma20",
                    feature_ref=FeatureReference(
                        feature_name=FeatureName.PRICE_TECHNICAL,
                    ),
                    operator=FilterOperator.GT,
                    threshold=0.0,
                ),
                FilterSpec(
                    filter_id="earnings_yield_floor",
                    feature_ref=FeatureReference(
                        feature_name=FeatureName.VALUATION,
                        lag_days=1,
                    ),
                    operator=FilterOperator.GTE,
                    threshold=0.08,
                ),
            ),
            candidates=(
                ScanCandidateRecord(
                    run_id="scan-2026-06-04-cn-core",
                    trade_date="2026-06-04",
                    symbol="000001.SZ",
                    market="CN",
                    universe_id="cn-core",
                    matched_filter_ids=(
                        "close_above_ma20",
                        "earnings_yield_floor",
                    ),
                ),
                ScanCandidateRecord(
                    run_id="scan-2026-06-04-cn-core",
                    trade_date="2026-06-04",
                    symbol="600000.SH",
                    market="CN",
                    universe_id="cn-core",
                    matched_filter_ids=("close_above_ma20",),
                ),
            ),
        )

        self.assertEqual(validate_scan_candidate_list(payload), ())

    def test_universe_membership_requires_iso_trade_date_and_unique_symbols(self) -> None:
        issues = validate_universe_membership_input(
            UniverseMembershipInput(
                universe_id="cn-core",
                universe_name="CN Core",
                market="CN",
                as_of_date="2026/06/04",
                symbols=("600000.SH", "600000.SH"),
            )
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                ("as_of_date", "invalid_date_string"),
                ("symbols", "duplicate_symbol"),
            },
        )

    def test_feature_reference_rejects_non_declarative_extra_fields(self) -> None:
        issues = validate_feature_reference(
            {
                "feature_name": FeatureName.CAPITAL_FLOW,
                "lag_days": 0,
                "loader": "read_feature_records_jsonl",
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {("loader", "unexpected_field")},
        )

    def test_filter_spec_rejects_unsupported_operators_and_bad_thresholds(self) -> None:
        unsupported_operator_issues = validate_filter_spec(
            {
                "filter_id": "mystery",
                "feature_ref": {
                    "feature_name": FeatureName.PRICE_TECHNICAL,
                    "lag_days": 0,
                },
                "operator": "contains",
                "threshold": 1.0,
            }
        )
        malformed_threshold_issues = validate_filter_spec(
            {
                "filter_id": "band",
                "feature_ref": {
                    "feature_name": FeatureName.VALUATION,
                    "lag_days": 0,
                },
                "operator": FilterOperator.BETWEEN,
                "threshold": (2.0, 1.0),
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in unsupported_operator_issues},
            {("operator", "unsupported_operator")},
        )
        self.assertEqual(
            {(issue.field, issue.code) for issue in malformed_threshold_issues},
            {("threshold", "invalid_threshold")},
        )

    def test_candidate_list_enforces_metadata_alignment_and_deterministic_order(self) -> None:
        issues = validate_scan_candidate_list(
            {
                "metadata": {
                    "run_id": "scan-2026-06-04-cn-core",
                    "scanner_id": "value_breakout_watchlist",
                    "trade_date": "2026-06-04",
                    "universe_id": "cn-core",
                    "generated_at": datetime(2026, 6, 4, 9, 30, 0),
                    "schema_version": SCANNER_CONTRACT_SCHEMA_VERSION,
                },
                "feature_refs": [
                    {"feature_name": FeatureName.PRICE_TECHNICAL, "lag_days": 0},
                ],
                "filters": [
                    {
                        "filter_id": "close_above_ma20",
                        "feature_ref": {
                            "feature_name": FeatureName.PRICE_TECHNICAL,
                            "lag_days": 0,
                        },
                        "operator": FilterOperator.GT,
                        "threshold": 0.0,
                    }
                ],
                "candidates": [
                    {
                        "run_id": "wrong-run",
                        "trade_date": "2026-06-04",
                        "symbol": "600000.SH",
                        "market": "CN",
                        "universe_id": "cn-core",
                        "matched_filter_ids": ("close_above_ma20",),
                    },
                    {
                        "run_id": "scan-2026-06-04-cn-core",
                        "trade_date": "2026-06-04",
                        "symbol": "000001.SZ",
                        "market": "CN",
                        "universe_id": "cn-core",
                        "matched_filter_ids": ("unknown_filter",),
                    },
                ],
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                ("candidates", "non_deterministic_order"),
                ("candidates[0].run_id", "metadata_mismatch"),
                ("candidates[1].matched_filter_ids", "unknown_filter_id"),
            },
        )


if __name__ == "__main__":
    unittest.main()
