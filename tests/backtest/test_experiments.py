import importlib
import math
import unittest

from quant.backtest import (
    ExperimentConfigError,
    SelectionReference,
    SelectionReferenceKind,
    build_repeatable_experiment_config,
    validate_repeatable_experiment_config,
)


class RepeatableExperimentConfigTestCase(unittest.TestCase):
    def test_backtest_package_exports_repeatable_experiment_config_tools(self) -> None:
        package = importlib.import_module("quant.backtest")

        self.assertTrue(hasattr(package, "RepeatableExperimentConfig"))
        self.assertTrue(hasattr(package, "build_repeatable_experiment_config"))
        self.assertTrue(hasattr(package, "validate_repeatable_experiment_config"))

    def test_build_repeatable_experiment_config_is_deterministic_and_serializable(self) -> None:
        selection_ref = SelectionReference(
            reference_kind=SelectionReferenceKind.CANDIDATE_LIST,
            reference_id="scan-2026-06-01",
            reference_date="2026-06-01",
            market="CN",
        )

        first_config = build_repeatable_experiment_config(
            strategy_id="ma_crossover_long",
            selection_ref=selection_ref,
            start_trade_date="2026-01-02",
            end_trade_date="2026-03-31",
            starting_capital=500000.0,
            transaction_cost_bps=3.0,
            slippage_bps=2.0,
            parameter_overrides={"entry_buffer": 0.2},
            parameter_set_version="2026Q1",
        )
        second_config = build_repeatable_experiment_config(
            strategy_id="ma_crossover_long",
            selection_ref=selection_ref,
            start_trade_date="2026-01-02",
            end_trade_date="2026-03-31",
            starting_capital=500000.0,
            transaction_cost_bps=3.0,
            slippage_bps=2.0,
            parameter_overrides={"entry_buffer": 0.2},
            parameter_set_version="2026Q1",
        )

        self.assertEqual(first_config, second_config)
        self.assertEqual(
            first_config.to_normalized_mapping(),
            second_config.to_normalized_mapping(),
        )
        self.assertEqual(
            first_config.to_backtest_request().request_id,
            first_config.experiment_id,
        )
        self.assertEqual(
            [parameter["name"] for parameter in first_config.to_normalized_mapping()["parameters"]],
            ["entry_buffer", "exit_buffer"],
        )

    def test_build_repeatable_experiment_config_rejects_invalid_parameter_overrides(self) -> None:
        selection_ref = SelectionReference(
            reference_kind=SelectionReferenceKind.UNIVERSE,
            reference_id="cn-core",
            reference_date="2026-06-01",
            market="CN",
        )

        with self.assertRaisesRegex(ExperimentConfigError, "parameters:unknown_parameter"):
            build_repeatable_experiment_config(
                strategy_id="ma_crossover_long",
                selection_ref=selection_ref,
                start_trade_date="2026-01-02",
                end_trade_date="2026-03-31",
                starting_capital=500000.0,
                parameter_overrides={"mystery": 1.0},
            )
        with self.assertRaisesRegex(ExperimentConfigError, "parameters:invalid_parameter_type"):
            build_repeatable_experiment_config(
                strategy_id="rsi_mean_reversion_long",
                selection_ref=selection_ref,
                start_trade_date="2026-01-02",
                end_trade_date="2026-03-31",
                starting_capital=500000.0,
                parameter_overrides={"entry_rsi_max": "low"},
            )

    def test_validate_repeatable_experiment_config_rejects_invalid_window_and_values(self) -> None:
        issues = validate_repeatable_experiment_config(
            {
                "experiment_id": "exp-001",
                "strategy_ref": {
                    "strategy_id": "ma_crossover_long",
                    "strategy_version": "1.0.0",
                },
                "parameter_set_version": "v1",
                "parameter_set_id": "p1",
                "parameters": [
                    {"name": "entry_buffer", "value": 0.0},
                    {"name": "exit_buffer", "value": 0.0},
                ],
                "selection_ref": {
                    "reference_kind": SelectionReferenceKind.UNIVERSE,
                    "reference_id": "cn-core",
                    "reference_date": "2026-06-01",
                    "market": "CN",
                },
                "start_trade_date": "2026-04-01",
                "end_trade_date": "2026-03-01",
                "starting_capital": math.inf,
                "transaction_cost_bps": -1.0,
                "slippage_bps": -2.0,
                "schema_version": "9.9.9",
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                ("end_trade_date", "invalid_date_order"),
                ("starting_capital", "invalid_value"),
                ("transaction_cost_bps", "invalid_value"),
                ("slippage_bps", "invalid_value"),
                ("parameter_set_id", "parameter_set_id_mismatch"),
                ("schema_version", "unsupported_schema_version"),
            },
        )

    def test_validate_repeatable_experiment_config_rejects_unknown_parameter_and_version_mismatch(self) -> None:
        issues = validate_repeatable_experiment_config(
            {
                "experiment_id": "exp-002",
                "strategy_ref": {
                    "strategy_id": "rsi_mean_reversion_long",
                    "strategy_version": "9.9.9",
                },
                "parameter_set_version": "v1",
                "parameter_set_id": "p2",
                "parameters": [
                    {"name": "entry_rsi_max", "value": 30.0},
                    {"name": "unknown_field", "value": 60.0},
                ],
                "selection_ref": {
                    "reference_kind": SelectionReferenceKind.CANDIDATE_LIST,
                    "reference_id": "scan-2026-06-01",
                    "reference_date": "2026-06-01",
                    "market": "CN",
                },
                "start_trade_date": "2026-01-02",
                "end_trade_date": "2026-03-31",
                "starting_capital": 100000.0,
                "transaction_cost_bps": 1.0,
                "slippage_bps": 1.0,
                "schema_version": "1.0.0",
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                ("strategy_ref.strategy_version", "strategy_version_mismatch"),
            },
        )

    def test_validate_repeatable_experiment_config_rejects_choice_and_range_failures(self) -> None:
        config = build_repeatable_experiment_config(
            strategy_id="rsi_mean_reversion_long",
            selection_ref=SelectionReference(
                reference_kind=SelectionReferenceKind.UNIVERSE,
                reference_id="cn-core",
                reference_date="2026-06-01",
                market="CN",
            ),
            start_trade_date="2026-01-02",
            end_trade_date="2026-03-31",
            starting_capital=200000.0,
        ).to_normalized_mapping()
        config["parameters"][0]["value"] = -5.0

        issues = validate_repeatable_experiment_config(config)

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                ("parameters", "parameter_below_min"),
            },
        )

    def test_validate_repeatable_experiment_config_accepts_unchanged_valid_config(self) -> None:
        config = build_repeatable_experiment_config(
            strategy_id="ma_crossover_long",
            selection_ref=SelectionReference(
                reference_kind=SelectionReferenceKind.CANDIDATE_LIST,
                reference_id="scan-2026-06-01",
                reference_date="2026-06-01",
                market="CN",
            ),
            start_trade_date="2026-01-02",
            end_trade_date="2026-03-31",
            starting_capital=500000,
            transaction_cost_bps=3,
            slippage_bps=2,
            parameter_overrides={"entry_buffer": 0.2},
            parameter_set_version="2026Q1",
        ).to_normalized_mapping()

        self.assertEqual(validate_repeatable_experiment_config(config), ())

    def test_validate_repeatable_experiment_config_rejects_stale_experiment_id_after_material_change(
        self,
    ) -> None:
        config = build_repeatable_experiment_config(
            strategy_id="ma_crossover_long",
            selection_ref=SelectionReference(
                reference_kind=SelectionReferenceKind.CANDIDATE_LIST,
                reference_id="scan-2026-06-01",
                reference_date="2026-06-01",
                market="CN",
            ),
            start_trade_date="2026-01-02",
            end_trade_date="2026-03-31",
            starting_capital=500000.0,
            transaction_cost_bps=3.0,
            slippage_bps=2.0,
            parameter_overrides={"entry_buffer": 0.2},
            parameter_set_version="2026Q1",
        ).to_normalized_mapping()
        config["transaction_cost_bps"] = 7.0

        issues = validate_repeatable_experiment_config(config)

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                ("experiment_id", "experiment_id_mismatch"),
            },
        )


if __name__ == "__main__":
    unittest.main()
