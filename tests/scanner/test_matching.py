import importlib
import unittest

from quant.features.contracts import FeatureName
from quant.scanner import (
    FeatureReference,
    FilterOperator,
    FilterSpec,
    InvalidFeatureValueError,
    InvalidFilterSpecError,
    MissingFeatureValueError,
    collect_matched_filter_ids,
    match_filter_spec,
)


class ScannerMatchingTestCase(unittest.TestCase):
    def test_matching_helpers_are_exported(self) -> None:
        package = importlib.import_module("quant.scanner")
        module = importlib.import_module("quant.scanner.matching")

        self.assertTrue(hasattr(package, "match_filter_spec"))
        self.assertTrue(hasattr(package, "collect_matched_filter_ids"))
        self.assertTrue(hasattr(module, "InvalidFilterSpecError"))

    def test_collect_matched_filter_ids_is_deterministic(self) -> None:
        filters = (
            FilterSpec(
                filter_id="above_ma20",
                feature_ref=FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0),
                operator=FilterOperator.GT,
                threshold=0.0,
            ),
            {
                "filter_id": "valuation_band",
                "feature_ref": {
                    "feature_name": FeatureName.VALUATION,
                    "lag_days": 1,
                },
                "operator": FilterOperator.BETWEEN,
                "threshold": [0.08, 0.12],
            },
            FilterSpec(
                filter_id="positive_flow_label",
                feature_ref=FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0),
                operator=FilterOperator.EQ,
                threshold="positive",
            ),
        )
        feature_values = {
            FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.03,
            FeatureReference(FeatureName.VALUATION, lag_days=1): 0.10,
            FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "neutral",
        }

        self.assertEqual(
            collect_matched_filter_ids(filters, feature_values),
            ("above_ma20", "valuation_band"),
        )
        self.assertFalse(match_filter_spec(filters[2], feature_values))

    def test_missing_feature_value_raises_clear_error(self) -> None:
        filter_spec = FilterSpec(
            filter_id="valuation_floor",
            feature_ref=FeatureReference(FeatureName.VALUATION, lag_days=1),
            operator=FilterOperator.GTE,
            threshold=0.08,
        )
        feature_values = {
            FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.03,
        }

        with self.assertRaisesRegex(
            MissingFeatureValueError,
            r"missing feature value for valuation\[lag_days=1\]",
        ):
            match_filter_spec(filter_spec, feature_values)

    def test_invalid_filter_spec_is_rejected_before_evaluation(self) -> None:
        filter_spec = {
            "filter_id": "broken_filter",
            "feature_ref": {
                "feature_name": FeatureName.PRICE_TECHNICAL,
                "lag_days": 0,
            },
            "operator": "contains",
            "threshold": 1.0,
        }
        feature_values = {
            FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.03,
        }

        with self.assertRaisesRegex(
            InvalidFilterSpecError,
            r"invalid filter spec: operator: unsupported_operator",
        ):
            match_filter_spec(filter_spec, feature_values)

    def test_malformed_numeric_feature_value_is_rejected(self) -> None:
        filter_spec = FilterSpec(
            filter_id="above_zero",
            feature_ref=FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0),
            operator=FilterOperator.GT,
            threshold=0.0,
        )
        feature_values = {
            FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): float("nan"),
        }

        with self.assertRaisesRegex(
            InvalidFeatureValueError,
            r"must be a finite numeric value",
        ):
            match_filter_spec(filter_spec, feature_values)

    def test_duplicate_filter_ids_are_rejected(self) -> None:
        filters = (
            FilterSpec(
                filter_id="duplicate",
                feature_ref=FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0),
                operator=FilterOperator.GT,
                threshold=0.0,
            ),
            FilterSpec(
                filter_id="duplicate",
                feature_ref=FeatureReference(FeatureName.VALUATION, lag_days=0),
                operator=FilterOperator.GTE,
                threshold=0.08,
            ),
        )
        feature_values = {
            FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.03,
            FeatureReference(FeatureName.VALUATION, lag_days=0): 0.10,
        }

        with self.assertRaisesRegex(
            InvalidFilterSpecError,
            r"duplicate filter_id 'duplicate' at filters\[1\]",
        ):
            collect_matched_filter_ids(filters, feature_values)


if __name__ == "__main__":
    unittest.main()
