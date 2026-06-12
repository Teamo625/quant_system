import importlib
import unittest

from quant.strategies import (
    SignalIntent,
    StrategyRuleError,
    evaluate_starter_strategy,
    get_starter_strategy_definition,
    list_starter_strategies,
    resolve_strategy_parameters,
)


class StarterStrategyRulesTestCase(unittest.TestCase):
    def test_strategy_package_exports_starter_rule_evaluation(self) -> None:
        package = importlib.import_module("quant.strategies")

        self.assertTrue(hasattr(package, "evaluate_starter_strategy"))
        self.assertTrue(hasattr(package, "resolve_strategy_parameters"))
        self.assertTrue(hasattr(package, "list_starter_strategies"))

    def test_starter_library_contains_expected_definitions(self) -> None:
        definitions = {
            definition.strategy_id: definition for definition in list_starter_strategies()
        }

        self.assertEqual(
            set(definitions),
            {"ma_crossover_long", "rsi_mean_reversion_long"},
        )
        self.assertEqual(
            definitions["ma_crossover_long"].input_features,
            ("close", "fast_ma", "slow_ma"),
        )
        self.assertEqual(
            tuple(parameter.name for parameter in definitions["rsi_mean_reversion_long"].parameters),
            ("entry_rsi_max", "exit_rsi_min"),
        )
        self.assertEqual(
            definitions["ma_crossover_long"].output_intent,
            SignalIntent.ENTRY_EXIT,
        )
        self.assertEqual(
            definitions["rsi_mean_reversion_long"].output_intent,
            SignalIntent.ENTRY_EXIT,
        )

    def test_ma_crossover_evaluation_is_deterministic(self) -> None:
        rows = (
            {
                "symbol": "600000.SH",
                "trade_date": "2026-01-02",
                "close": 10.0,
                "fast_ma": 9.8,
                "slow_ma": 10.1,
            },
            {
                "symbol": "600000.SH",
                "trade_date": "2026-01-03",
                "close": 10.6,
                "fast_ma": 10.3,
                "slow_ma": 10.0,
            },
            {
                "symbol": "600000.SH",
                "trade_date": "2026-01-04",
                "close": 9.7,
                "fast_ma": 9.6,
                "slow_ma": 10.0,
            },
        )

        first_result = evaluate_starter_strategy("ma_crossover_long", rows)
        second_result = evaluate_starter_strategy("ma_crossover_long", rows)

        self.assertEqual(first_result, second_result)
        self.assertEqual(
            [signal.intent for signal in first_result.signals],
            ["enter_long", "exit_long"],
        )
        self.assertEqual(
            [signal.trade_date for signal in first_result.signals],
            ["2026-01-03", "2026-01-04"],
        )
        self.assertEqual(
            first_result.signals[0].parameter_set_id,
            first_result.resolved_parameters.parameter_set_id,
        )

    def test_rsi_mean_reversion_evaluation_emits_entry_and_exit(self) -> None:
        rows = (
            {
                "symbol": "000001.SZ",
                "trade_date": "2026-02-01",
                "close": 8.8,
                "rsi_14": 25.0,
            },
            {
                "symbol": "000001.SZ",
                "trade_date": "2026-02-02",
                "close": 9.5,
                "rsi_14": 61.0,
            },
        )

        result = evaluate_starter_strategy(
            "rsi_mean_reversion_long",
            rows,
            {"entry_rsi_max": 28.0, "exit_rsi_min": 60.0},
        )

        self.assertEqual(
            [(signal.trade_date, signal.intent) for signal in result.signals],
            [("2026-02-01", "enter_long"), ("2026-02-02", "exit_long")],
        )
        self.assertEqual(result.resolved_parameters.parameter_set_version, "1.0.0")

    def test_starter_definition_output_intent_matches_emitted_signal_semantics(self) -> None:
        cases = (
            (
                "ma_crossover_long",
                (
                    {
                        "symbol": "600000.SH",
                        "trade_date": "2026-01-02",
                        "close": 10.0,
                        "fast_ma": 9.8,
                        "slow_ma": 10.1,
                    },
                    {
                        "symbol": "600000.SH",
                        "trade_date": "2026-01-03",
                        "close": 10.6,
                        "fast_ma": 10.3,
                        "slow_ma": 10.0,
                    },
                    {
                        "symbol": "600000.SH",
                        "trade_date": "2026-01-04",
                        "close": 9.7,
                        "fast_ma": 9.6,
                        "slow_ma": 10.0,
                    },
                ),
                None,
            ),
            (
                "rsi_mean_reversion_long",
                (
                    {
                        "symbol": "000001.SZ",
                        "trade_date": "2026-02-01",
                        "close": 8.8,
                        "rsi_14": 25.0,
                    },
                    {
                        "symbol": "000001.SZ",
                        "trade_date": "2026-02-02",
                        "close": 9.5,
                        "rsi_14": 61.0,
                    },
                ),
                {"entry_rsi_max": 28.0, "exit_rsi_min": 60.0},
            ),
        )

        for strategy_id, rows, overrides in cases:
            with self.subTest(strategy_id=strategy_id):
                definition = get_starter_strategy_definition(strategy_id)
                result = evaluate_starter_strategy(strategy_id, rows, overrides)

                self.assertEqual(definition.output_intent, SignalIntent.ENTRY_EXIT)
                self.assertEqual(result.strategy_definition.output_intent, SignalIntent.ENTRY_EXIT)
                self.assertEqual(
                    {signal.intent for signal in result.signals},
                    {"enter_long", "exit_long"},
                )

    def test_duplicate_dates_and_missing_inputs_raise_controlled_errors(self) -> None:
        duplicate_rows = (
            {
                "symbol": "600000.SH",
                "trade_date": "2026-01-02",
                "close": 10.0,
                "fast_ma": 9.9,
                "slow_ma": 10.1,
            },
            {
                "symbol": "600000.SH",
                "trade_date": "2026-01-02",
                "close": 10.1,
                "fast_ma": 10.0,
                "slow_ma": 10.1,
            },
        )
        missing_field_rows = (
            {
                "symbol": "600000.SH",
                "trade_date": "2026-01-02",
                "close": 10.0,
                "fast_ma": 9.9,
            },
        )

        with self.assertRaisesRegex(StrategyRuleError, "duplicate_trade_date"):
            evaluate_starter_strategy("ma_crossover_long", duplicate_rows)
        with self.assertRaisesRegex(StrategyRuleError, "missing_required_input"):
            evaluate_starter_strategy("ma_crossover_long", missing_field_rows)

    def test_parameter_resolution_rejects_unknown_and_out_of_range_values(self) -> None:
        with self.assertRaisesRegex(StrategyRuleError, "unknown_parameter"):
            resolve_strategy_parameters(
                "ma_crossover_long",
                {"not_a_parameter": 1.0},
            )
        with self.assertRaisesRegex(StrategyRuleError, "parameter_above_max"):
            resolve_strategy_parameters(
                "rsi_mean_reversion_long",
                {"exit_rsi_min": 120.0},
            )

    def test_empty_input_and_unsupported_strategy_raise_controlled_errors(self) -> None:
        with self.assertRaisesRegex(StrategyRuleError, "empty_input"):
            evaluate_starter_strategy("ma_crossover_long", ())
        with self.assertRaisesRegex(StrategyRuleError, "unsupported_strategy_id"):
            get_starter_strategy_definition("breakout_v2")


if __name__ == "__main__":
    unittest.main()
