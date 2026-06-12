import importlib
import unittest
from datetime import date, datetime

from quant.datahub.datasets import DatasetName
from quant.features.contracts import (
    FEATURE_VALUE_SCHEMA_VERSION,
    FeatureName,
    FeatureValueRecord,
    build_feature_metric_identity,
    validate_feature_value_record,
)


class FeatureContractsTestCase(unittest.TestCase):
    def test_feature_package_imports_cleanly(self) -> None:
        package = importlib.import_module("quant.features")
        module = importlib.import_module("quant.features.contracts")

        self.assertTrue(hasattr(package, "FeatureValueRecord"))
        self.assertTrue(hasattr(package, "ValuationSnapshotInput"))
        self.assertTrue(hasattr(package, "CapitalFlowSnapshotInput"))
        self.assertTrue(hasattr(package, "FeatureOutputManifest"))
        self.assertTrue(hasattr(package, "FeatureBatchJob"))
        self.assertTrue(hasattr(package, "calculate_feature_batch"))
        self.assertTrue(hasattr(package, "write_feature_records_jsonl"))
        self.assertTrue(hasattr(module, "FeatureName"))

    def test_valid_feature_value_record_passes_validation(self) -> None:
        record = FeatureValueRecord(
            symbol="600000.SH",
            market="CN",
            trade_date=date(2026, 6, 3),
            feature_name=FeatureName.PRICE_TECHNICAL,
            metric_name="simple_moving_average",
            value=1.25,
            source_dataset=DatasetName.DAILY_BARS,
            created_at=datetime(2026, 6, 4, 9, 30, 0),
            metric_params={"window": 5},
        )

        self.assertEqual(validate_feature_value_record(record), ())
        self.assertEqual(
            build_feature_metric_identity(record),
            'price_technical:simple_moving_average:{"window":5}',
        )

    def test_missing_required_fields_fail_validation(self) -> None:
        issues = validate_feature_value_record(
            {
                "symbol": "600000.SH",
                "trade_date": date(2026, 6, 3),
                "feature_name": FeatureName.PRICE_TECHNICAL,
                "metric_name": "close_to_close_return",
                "metric_params": {},
                "value": 2.0,
                "source_dataset": DatasetName.DAILY_BARS,
                "created_at": datetime(2026, 6, 4, 9, 30, 0),
                "schema_version": FEATURE_VALUE_SCHEMA_VERSION,
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {("market", "missing_required")},
        )

    def test_trade_date_datetime_value_fails_validation(self) -> None:
        issues = validate_feature_value_record(
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": datetime(2026, 6, 3, 9, 30, 0),
                "feature_name": FeatureName.PRICE_TECHNICAL,
                "metric_name": "close_to_close_return",
                "metric_params": {},
                "value": 2.0,
                "source_dataset": DatasetName.DAILY_BARS,
                "created_at": datetime(2026, 6, 4, 9, 30, 0),
                "schema_version": FEATURE_VALUE_SCHEMA_VERSION,
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {("trade_date", "invalid_type")},
        )

    def test_invalid_metric_params_and_value_type_fail_validation(self) -> None:
        issues = validate_feature_value_record(
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 3),
                "feature_name": FeatureName.PRICE_TECHNICAL,
                "metric_name": "intraday_magic",
                "metric_params": {"window": object()},
                "value": {"raw": 1.0},
                "source_dataset": DatasetName.DAILY_BARS,
                "created_at": datetime(2026, 6, 4, 9, 30, 0),
                "schema_version": FEATURE_VALUE_SCHEMA_VERSION,
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                ("metric_params.window", "unsupported_param_value"),
                ("value", "unsupported_value_type"),
            },
        )

    def test_source_dataset_must_be_approved_datahub_input(self) -> None:
        issues = validate_feature_value_record(
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 3),
                "feature_name": FeatureName.VALUATION,
                "metric_name": "earnings_yield",
                "metric_params": {},
                "value": "cheap",
                "source_dataset": DatasetName.COMPANY_ANNOUNCEMENTS,
                "created_at": datetime(2026, 6, 4, 9, 30, 0),
                "schema_version": FEATURE_VALUE_SCHEMA_VERSION,
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {("source_dataset", "unsupported_source_dataset")},
        )

    def test_legacy_schema_record_without_metric_fields_remains_readable(self) -> None:
        payload = {
            "symbol": "600000.SH",
            "market": "CN",
            "trade_date": date(2026, 6, 3),
            "feature_name": FeatureName.PRICE_TECHNICAL,
            "value": 1.0,
            "source_dataset": DatasetName.DAILY_BARS,
            "created_at": datetime(2026, 6, 4, 9, 30, 0),
            "schema_version": "1.0.0",
        }

        self.assertEqual(validate_feature_value_record(payload), ())
        self.assertEqual(
            build_feature_metric_identity(payload),
            "price_technical:price_technical:{}",
        )


if __name__ == "__main__":
    unittest.main()
