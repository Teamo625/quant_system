import importlib
import unittest
from datetime import datetime

from quant.features.contracts import FeatureName
from quant.scanner import (
    FeatureReference,
    FilterOperator,
    FilterSpec,
    InvalidFilterSpecError,
    InvalidScanOutputError,
    InvalidScanRunnerInputError,
    MissingSymbolFeatureValuesError,
    ScanCandidateList,
    ScanRunMetadata,
    UniverseMembershipInput,
    run_scan,
)
from quant.scanner.contracts import validate_scan_candidate_list


class ScannerRunnerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = ScanRunMetadata(
            run_id="scan-2026-06-04-cn-core",
            scanner_id="foundation_scan",
            trade_date="2026-06-04",
            universe_id="cn-core",
            generated_at=datetime(2026, 6, 4, 9, 30, 0),
        )
        self.universe = UniverseMembershipInput(
            universe_id="cn-core",
            universe_name="CN Core",
            market="CN",
            as_of_date="2026-06-04",
            symbols=("600000.SH", "000001.SZ", "300750.SZ"),
        )
        self.filters = (
            FilterSpec(
                filter_id="above_ma20",
                feature_ref=FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0),
                operator=FilterOperator.GT,
                threshold=0.0,
            ),
            FilterSpec(
                filter_id="valuation_floor",
                feature_ref=FeatureReference(FeatureName.VALUATION, lag_days=1),
                operator=FilterOperator.GTE,
                threshold=0.08,
            ),
            FilterSpec(
                filter_id="flow_label",
                feature_ref=FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0),
                operator=FilterOperator.EQ,
                threshold="positive",
            ),
        )
        self.symbol_feature_values = {
            "600000.SH": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.02,
                FeatureReference(FeatureName.VALUATION, lag_days=1): 0.10,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
            },
            "000001.SZ": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.03,
                FeatureReference(FeatureName.VALUATION, lag_days=1): 0.09,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
            },
            "300750.SZ": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.05,
                FeatureReference(FeatureName.VALUATION, lag_days=1): 0.06,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
            },
        }

    def test_runner_helpers_are_exported(self) -> None:
        package = importlib.import_module("quant.scanner")
        module = importlib.import_module("quant.scanner.runner")

        self.assertTrue(hasattr(package, "run_scan"))
        self.assertTrue(hasattr(package, "InvalidScanRunnerInputError"))
        self.assertTrue(hasattr(module, "MissingSymbolFeatureValuesError"))

    def test_run_scan_builds_valid_candidate_list_with_stable_order(self) -> None:
        candidate_list = run_scan(
            metadata=self.metadata,
            universe=self.universe,
            filters=self.filters,
            symbol_feature_values=self.symbol_feature_values,
        )

        self.assertIsInstance(candidate_list, ScanCandidateList)
        self.assertEqual(validate_scan_candidate_list(candidate_list), ())
        self.assertEqual(
            tuple(candidate.symbol for candidate in candidate_list.candidates),
            ("000001.SZ", "600000.SH"),
        )
        self.assertEqual(
            candidate_list.feature_refs,
            (
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0),
                FeatureReference(FeatureName.VALUATION, lag_days=1),
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0),
            ),
        )
        self.assertEqual(
            candidate_list.candidates[0].matched_filter_ids,
            ("above_ma20", "valuation_floor", "flow_label"),
        )

    def test_run_scan_requires_feature_values_for_every_universe_symbol(self) -> None:
        symbol_feature_values = dict(self.symbol_feature_values)
        del symbol_feature_values["300750.SZ"]

        with self.assertRaisesRegex(
            MissingSymbolFeatureValuesError,
            r"missing symbol feature values for symbols: \['300750\.SZ'\]",
        ):
            run_scan(
                metadata=self.metadata,
                universe=self.universe,
                filters=self.filters,
                symbol_feature_values=symbol_feature_values,
            )

    def test_run_scan_rejects_malformed_symbol_feature_mapping(self) -> None:
        symbol_feature_values = dict(self.symbol_feature_values)
        symbol_feature_values["000001.SZ"] = {"price_technical": 0.03}

        with self.assertRaisesRegex(
            InvalidScanRunnerInputError,
            r"symbol_feature_values\['000001\.SZ'\] keys must be FeatureReference instances",
        ):
            run_scan(
                metadata=self.metadata,
                universe=self.universe,
                filters=self.filters,
                symbol_feature_values=symbol_feature_values,
            )

    def test_run_scan_rejects_malformed_metadata_payload(self) -> None:
        with self.assertRaisesRegex(
            InvalidScanRunnerInputError,
            r"invalid scan metadata: payload must be a dataclass instance or mapping",
        ):
            run_scan(
                metadata="scan-2026-06-04-cn-core",
                universe=self.universe,
                filters=self.filters,
                symbol_feature_values=self.symbol_feature_values,
            )

    def test_run_scan_rejects_duplicate_universe_symbols(self) -> None:
        duplicate_universe = UniverseMembershipInput(
            universe_id="cn-core",
            universe_name="CN Core",
            market="CN",
            as_of_date="2026-06-04",
            symbols=("000001.SZ", "000001.SZ"),
        )
        symbol_feature_values = {
            "000001.SZ": self.symbol_feature_values["000001.SZ"],
        }

        with self.assertRaisesRegex(
            InvalidScanRunnerInputError,
            r"invalid universe input: symbols: duplicate_symbol",
        ):
            run_scan(
                metadata=self.metadata,
                universe=duplicate_universe,
                filters=self.filters,
                symbol_feature_values=symbol_feature_values,
            )

    def test_run_scan_surfaces_invalid_filter_specs(self) -> None:
        filters = (
            {
                "filter_id": "broken",
                "feature_ref": {
                    "feature_name": FeatureName.PRICE_TECHNICAL,
                    "lag_days": 0,
                },
                "operator": "contains",
                "threshold": 1.0,
            },
        )
        symbol_feature_values = {
            "600000.SH": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.02,
            },
            "000001.SZ": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.03,
            },
            "300750.SZ": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.05,
            },
        }

        with self.assertRaisesRegex(
            InvalidFilterSpecError,
            r"invalid filter spec: operator: unsupported_operator",
        ):
            run_scan(
                metadata=self.metadata,
                universe=self.universe,
                filters=filters,
                symbol_feature_values=symbol_feature_values,
            )

    def test_run_scan_rejects_invalid_generated_candidate_list(self) -> None:
        mismatched_metadata = ScanRunMetadata(
            run_id="scan-2026-06-04-cn-core",
            scanner_id="foundation_scan",
            trade_date="2026-06-04",
            universe_id="wrong-universe",
            generated_at=datetime(2026, 6, 4, 9, 30, 0),
        )
        symbol_feature_values = {
            "000001.SZ": self.symbol_feature_values["000001.SZ"],
            "300750.SZ": self.symbol_feature_values["300750.SZ"],
            "600000.SH": self.symbol_feature_values["600000.SH"],
        }

        with self.assertRaisesRegex(
            InvalidScanOutputError,
            r"generated candidate list failed validation: candidates\[0\]\.universe_id: metadata_mismatch",
        ):
            run_scan(
                metadata=mismatched_metadata,
                universe=self.universe,
                filters=self.filters,
                symbol_feature_values=symbol_feature_values,
            )


if __name__ == "__main__":
    unittest.main()
