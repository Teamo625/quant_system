import importlib
import unittest

from quant.strategies import (
    ParameterDefinition,
    ParameterType,
    SignalIntent,
    StrategyDefinition,
    validate_parameter_definition,
    validate_strategy_definition,
)


class StrategyContractsTestCase(unittest.TestCase):
    def test_strategy_package_exports_contracts(self) -> None:
        package = importlib.import_module("quant.strategies")
        module = importlib.import_module("quant.strategies.contracts")

        self.assertTrue(hasattr(package, "StrategyDefinition"))
        self.assertTrue(hasattr(package, "ParameterDefinition"))
        self.assertTrue(hasattr(module, "SignalIntent"))

    def test_valid_strategy_definition_passes_validation(self) -> None:
        payload = StrategyDefinition(
            strategy_id="mean_reversion_research",
            strategy_name="Mean Reversion Research",
            strategy_version="0.1.0",
            input_features=("close", "volume", "rolling_zscore_20"),
            parameters=(
                ParameterDefinition(
                    name="lookback_days",
                    parameter_type=ParameterType.INTEGER,
                    default=20,
                    min_value=5,
                    max_value=60,
                ),
                ParameterDefinition(
                    name="entry_threshold",
                    parameter_type=ParameterType.FLOAT,
                    default=1.5,
                    min_value=0.5,
                    max_value=3.0,
                ),
                ParameterDefinition(
                    name="side",
                    parameter_type=ParameterType.STRING,
                    default="long_only",
                    choices=("long_only", "long_short"),
                ),
            ),
            output_intent=SignalIntent.ENTRY,
            signal_kind="rebalance_signal",
        )

        self.assertEqual(validate_strategy_definition(payload), ())

    def test_strategy_definition_rejects_duplicate_features_and_parameters(self) -> None:
        issues = validate_strategy_definition(
            {
                "strategy_id": "s1",
                "strategy_name": "Strategy One",
                "strategy_version": "1.0.0",
                "input_features": ["close", "close"],
                "parameters": [
                    {
                        "name": "window",
                        "parameter_type": ParameterType.INTEGER,
                        "default": 10,
                        "min_value": 1,
                        "max_value": 20,
                        "choices": (),
                    },
                    {
                        "name": "window",
                        "parameter_type": ParameterType.INTEGER,
                        "default": 12,
                        "min_value": 1,
                        "max_value": 20,
                        "choices": (),
                    },
                ],
                "output_intent": SignalIntent.SCORE,
                "signal_kind": "alpha_score",
                "schema_version": "1.0.0",
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                ("input_features", "duplicate_feature_name"),
                ("parameters[1].name", "duplicate_parameter_name"),
            },
        )

    def test_parameter_definition_rejects_unsupported_type(self) -> None:
        issues = validate_parameter_definition(
            {
                "name": "window",
                "parameter_type": "decimal",
                "default": 10,
                "min_value": 1,
                "max_value": 20,
                "choices": (),
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {("parameter_type", "unsupported_parameter_type")},
        )

    def test_parameter_definition_rejects_inconsistent_constraints(self) -> None:
        issues = validate_parameter_definition(
            {
                "name": "mode",
                "parameter_type": ParameterType.STRING,
                "default": "slow",
                "min_value": 1,
                "max_value": 5,
                "choices": ("fast", "medium"),
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                ("default", "inconsistent_constraints"),
                ("min_value", "inconsistent_constraints"),
            },
        )

    def test_strategy_definition_rejects_empty_identifiers_and_extra_fields(self) -> None:
        issues = validate_strategy_definition(
            {
                "strategy_id": " ",
                "strategy_name": "",
                "strategy_version": " ",
                "input_features": ("close",),
                "parameters": (),
                "output_intent": "mystery",
                "signal_kind": "",
                "schema_version": "2.0.0",
                "runner": "live",
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                ("strategy_id", "empty_text"),
                ("strategy_name", "empty_text"),
                ("strategy_version", "empty_text"),
                ("signal_kind", "empty_text"),
                ("output_intent", "unsupported_output_intent"),
                ("schema_version", "unsupported_schema_version"),
                ("runner", "unexpected_field"),
            },
        )


if __name__ == "__main__":
    unittest.main()
