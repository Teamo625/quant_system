import importlib
import math
import unittest

from quant.backtest import (
    ComparisonInput,
    ComparisonWorkflowError,
    ReplayAssumptions,
    ReplayCoverage,
    ReplayEndState,
    ReplayRejectionBreakdown,
    ReplayReport,
    ReplaySummary,
    SelectionReference,
    SelectionReferenceKind,
    build_multi_configuration_comparison,
    build_repeatable_experiment_config,
    run_historical_replay,
    validate_multi_configuration_comparison_inputs,
)


class MultiConfigurationComparisonTestCase(unittest.TestCase):
    def test_backtest_package_exports_comparison_workflow_tools(self) -> None:
        package = importlib.import_module("quant.backtest")

        self.assertTrue(hasattr(package, "ComparisonInput"))
        self.assertTrue(hasattr(package, "MultiConfigurationComparison"))
        self.assertTrue(hasattr(package, "build_multi_configuration_comparison"))
        self.assertTrue(hasattr(package, "validate_multi_configuration_comparison_inputs"))

    def test_build_multi_configuration_comparison_is_deterministic_and_order_independent(
        self,
    ) -> None:
        first_config = self._build_config(
            strategy_id="ma_crossover_long",
            parameter_overrides={"entry_buffer": 0.1},
        )
        second_config = self._build_config(
            strategy_id="ma_crossover_long",
            parameter_overrides={"entry_buffer": 0.3},
        )
        first_result = self._run_result(
            first_config,
            buy_close=10.0,
            sell_close=11.0,
        )
        second_result = self._run_result(
            second_config,
            buy_close=10.0,
            sell_close=10.4,
        )

        first_comparison = build_multi_configuration_comparison(
            (
                ComparisonInput(
                    experiment_config=first_config,
                    replay_result=first_result,
                ),
                ComparisonInput(
                    experiment_config=second_config,
                    replay_result=second_result,
                ),
            )
        )
        second_comparison = build_multi_configuration_comparison(
            (
                ComparisonInput(
                    experiment_config=second_config,
                    replay_result=second_result,
                ),
                ComparisonInput(
                    experiment_config=first_config,
                    replay_result=first_result,
                ),
            )
        )

        self.assertEqual(first_comparison.comparison_id, second_comparison.comparison_id)
        self.assertEqual(first_comparison.rows, second_comparison.rows)
        self.assertEqual(
            first_comparison.to_normalized_mapping(),
            second_comparison.to_normalized_mapping(),
        )
        self.assertEqual(
            first_comparison.configuration_ids,
            (
                first_config.experiment_id,
                second_config.experiment_id,
            ),
        )
        self.assertEqual(first_comparison.rows[0].rank, 1)
        self.assertEqual(
            first_comparison.rows[0].configuration_id,
            first_config.experiment_id,
        )
        self.assertAlmostEqual(
            first_comparison.rows[1].metric_deltas_vs_leader["total_return"],
            second_result.summary.total_return - first_result.summary.total_return,
        )

    def test_build_multi_configuration_comparison_uses_configuration_id_tie_breaker(
        self,
    ) -> None:
        first_config = self._build_config(
            strategy_id="ma_crossover_long",
            parameter_overrides={"entry_buffer": 0.1},
        )
        second_config = self._build_config(
            strategy_id="ma_crossover_long",
            parameter_overrides={"entry_buffer": 0.2},
        )
        first_report = self._build_report(
            first_config,
            total_return=0.10,
            max_drawdown=0.05,
            ending_total_equity=110000.0,
            win_rate=0.50,
            turnover_ratio=0.30,
        )
        second_report = self._build_report(
            second_config,
            total_return=0.10,
            max_drawdown=0.05,
            ending_total_equity=110000.0,
            win_rate=0.50,
            turnover_ratio=0.30,
        )

        comparison = build_multi_configuration_comparison(
            (
                ComparisonInput(
                    experiment_config=second_config,
                    replay_report=second_report,
                ),
                ComparisonInput(
                    experiment_config=first_config,
                    replay_report=first_report,
                ),
            )
        )

        self.assertEqual(
            comparison.configuration_ids,
            tuple(sorted((first_config.experiment_id, second_config.experiment_id))),
        )
        self.assertEqual(
            comparison.rows[0].rank_key["configuration_id_asc"],
            min(first_config.experiment_id, second_config.experiment_id),
        )

    def test_validate_multi_configuration_inputs_rejects_empty_single_duplicate_and_mismatched(
        self,
    ) -> None:
        empty_issues = validate_multi_configuration_comparison_inputs(())
        self.assertEqual(
            {(issue.field, issue.code) for issue in empty_issues},
            {("entries", "empty_entries")},
        )

        single_config = self._build_config(strategy_id="ma_crossover_long")
        single_report = self._build_report(single_config)
        single_issues = validate_multi_configuration_comparison_inputs(
            (ComparisonInput(experiment_config=single_config, replay_report=single_report),)
        )
        self.assertEqual(
            {(issue.field, issue.code) for issue in single_issues},
            {("entries", "single_entry")},
        )

        duplicate_issues = validate_multi_configuration_comparison_inputs(
            (
                ComparisonInput(
                    experiment_config=single_config,
                    replay_report=single_report,
                ),
                ComparisonInput(
                    experiment_config=single_config,
                    replay_report=single_report,
                ),
            )
        )
        self.assertEqual(
            {(issue.field, issue.code) for issue in duplicate_issues},
            {("entries[1].configuration_id", "duplicate_configuration_id")},
        )

        second_config = self._build_config(
            strategy_id="rsi_mean_reversion_long",
            parameter_overrides={"entry_rsi_max": 25.0},
            start_trade_date="2026-01-03",
            end_trade_date="2026-01-31",
            starting_capital=120000.0,
        )
        mismatched_issues = validate_multi_configuration_comparison_inputs(
            (
                ComparisonInput(
                    experiment_config=single_config,
                    replay_report=single_report,
                ),
                ComparisonInput(
                    experiment_config=second_config,
                    replay_report=self._build_report(second_config),
                ),
            )
        )
        self.assertEqual(
            {(issue.field, issue.code) for issue in mismatched_issues},
            {
                ("entries[1].replay_report", "comparison_window_mismatch"),
                (
                    "entries[1].replay_report.summary.starting_capital",
                    "starting_capital_mismatch",
                ),
            },
        )

    def test_validate_multi_configuration_inputs_rejects_stale_ids_and_bad_metrics(
        self,
    ) -> None:
        first_config = self._build_config(strategy_id="ma_crossover_long")
        second_config = self._build_config(
            strategy_id="rsi_mean_reversion_long",
            parameter_overrides={"entry_rsi_max": 25.0},
        )

        stale_config = first_config.to_normalized_mapping()
        stale_config["transaction_cost_bps"] = 7.0
        missing_metric_report = self._build_report(second_config).to_normalized_mapping()
        missing_metric_report["summary"].pop("win_rate")

        issues = validate_multi_configuration_comparison_inputs(
            (
                ComparisonInput(
                    experiment_config=stale_config,
                    replay_report=self._build_report(first_config),
                ),
                ComparisonInput(
                    experiment_config=second_config,
                    replay_report=missing_metric_report,
                ),
            )
        )
        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                ("entries[0].experiment_config.experiment_id", "experiment_id_mismatch"),
                ("entries[1].replay_report.summary.win_rate", "missing_metric"),
            },
        )

        invalid_metric_report = self._build_report(second_config).to_normalized_mapping()
        invalid_metric_report["summary"]["turnover_ratio"] = math.inf
        issues = validate_multi_configuration_comparison_inputs(
            (
                ComparisonInput(
                    experiment_config=first_config,
                    replay_report=self._build_report(first_config),
                ),
                ComparisonInput(
                    experiment_config=second_config,
                    replay_report=invalid_metric_report,
                ),
            )
        )
        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                (
                    "entries[1].replay_report.summary.turnover_ratio",
                    "invalid_value",
                ),
            },
        )

    def test_build_multi_configuration_comparison_propagates_assumptions_and_shape(
        self,
    ) -> None:
        first_config = self._build_config(strategy_id="ma_crossover_long")
        second_config = self._build_config(
            strategy_id="rsi_mean_reversion_long",
            parameter_overrides={"entry_rsi_max": 25.0},
        )
        first_report = self._build_report(
            first_config,
            total_return=0.12,
            price_adjustment="adjusted",
            corporate_action_source="caller_provided_prices",
            artifact_reference="artifacts/first.json",
        )
        second_report = self._build_report(
            second_config,
            total_return=0.08,
            price_adjustment="unadjusted",
            corporate_action_source="caller_provided_prices",
            artifact_reference="artifacts/second.json",
        )

        comparison = build_multi_configuration_comparison(
            (
                ComparisonInput(
                    experiment_config=first_config,
                    replay_report=first_report,
                ),
                ComparisonInput(
                    experiment_config=second_config,
                    replay_report=second_report,
                ),
            )
        )

        self.assertEqual(
            {difference.field for difference in comparison.assumption_differences},
            {"price_adjustment"},
        )
        self.assertEqual(
            comparison.rows[0].assumptions["price_adjustment"],
            "adjusted",
        )
        self.assertEqual(
            comparison.rows[0].assumptions["corporate_action_source"],
            "caller_provided_prices",
        )
        self.assertEqual(
            comparison.rows[1].artifact_reference,
            "artifacts/second.json",
        )
        self.assertEqual(
            set(comparison.to_normalized_mapping()),
            {
                "comparison_id",
                "start_trade_date",
                "end_trade_date",
                "starting_capital",
                "ranking_policy",
                "leader_configuration_id",
                "configuration_ids",
                "rows",
                "assumption_differences",
            },
        )

    def test_build_multi_configuration_comparison_raises_controlled_error(self) -> None:
        config = self._build_config(strategy_id="ma_crossover_long")

        with self.assertRaises(ComparisonWorkflowError) as context:
            build_multi_configuration_comparison(
                (
                    ComparisonInput(
                        experiment_config=config,
                        replay_report=self._build_report(config),
                    ),
                )
            )

        self.assertEqual(
            {(issue.field, issue.code) for issue in context.exception.issues},
            {("entries", "single_entry")},
        )

    def _build_config(
        self,
        *,
        strategy_id: str,
        parameter_overrides: dict[str, float] | None = None,
        start_trade_date: str = "2026-01-02",
        end_trade_date: str = "2026-01-31",
        starting_capital: float = 100000.0,
    ):
        return build_repeatable_experiment_config(
            strategy_id=strategy_id,
            selection_ref=SelectionReference(
                reference_kind=SelectionReferenceKind.UNIVERSE,
                reference_id="cn-core",
                reference_date="2026-01-31",
                market="CN",
            ),
            start_trade_date=start_trade_date,
            end_trade_date=end_trade_date,
            starting_capital=starting_capital,
            transaction_cost_bps=1.0,
            slippage_bps=1.0,
            parameter_overrides=parameter_overrides,
            parameter_set_version="2026Q1",
        )

    def _run_result(self, config, *, buy_close: float, sell_close: float):
        return run_historical_replay(
            config.to_backtest_request(),
            (
                self._market_bar("AAA", "2026-01-02", buy_close),
                self._market_bar("AAA", "2026-01-31", sell_close),
            ),
            (
                self._trade_intent("buy", "AAA", "2026-01-02", "buy"),
                self._trade_intent("sell", "AAA", "2026-01-31", "sell"),
            ),
        )

    def _build_report(
        self,
        config,
        *,
        total_return: float = 0.10,
        max_drawdown: float = 0.04,
        ending_total_equity: float = 110000.0,
        win_rate: float = 0.60,
        turnover_ratio: float = 0.25,
        executed_trade_count: int = 4,
        rejected_intent_count: int = 1,
        start_trade_date: str | None = None,
        end_trade_date: str | None = None,
        starting_capital: float | None = None,
        price_adjustment: str = "adjusted",
        corporate_action_source: str = "caller_provided_prices",
        artifact_reference: str | None = None,
    ) -> ReplayReport:
        resolved_start = start_trade_date or config.start_trade_date
        resolved_end = end_trade_date or config.end_trade_date
        resolved_capital = starting_capital or config.starting_capital
        summary = ReplaySummary(
            request_id=config.experiment_id,
            strategy_id=config.strategy_ref.strategy_id,
            strategy_version=config.strategy_ref.strategy_version,
            start_trade_date=resolved_start,
            end_trade_date=resolved_end,
            starting_capital=resolved_capital,
            ending_cash=90000.0,
            ending_market_value=ending_total_equity - 90000.0,
            ending_total_equity=ending_total_equity,
            realized_pnl=7500.0,
            unrealized_pnl=2500.0,
            total_return=total_return,
            max_drawdown=max_drawdown,
            executed_trade_count=executed_trade_count,
            rejected_intent_count=rejected_intent_count,
            snapshot_count=30,
            winning_trade_count=3,
            losing_trade_count=1,
            flat_trade_count=0,
            win_rate=win_rate,
            loss_rate=0.20,
            total_buy_notional=25000.0,
            total_sell_notional=25000.0,
            total_transaction_cost=30.0,
            total_slippage_cost=20.0,
            gross_turnover=50000.0,
            turnover_ratio=turnover_ratio,
            average_net_exposure=0.55,
            max_net_exposure=0.80,
            ending_position_count=2,
            coverage_calendar_day_count=30,
            covered_market_bar_count=40,
            missing_bar_day_count=1,
            unusable_bar_day_count=0,
        )
        return ReplayReport(
            request_id=config.experiment_id,
            strategy_id=config.strategy_ref.strategy_id,
            strategy_version=config.strategy_ref.strategy_version,
            start_trade_date=resolved_start,
            end_trade_date=resolved_end,
            assumptions=ReplayAssumptions(
                price_adjustment=price_adjustment,
                corporate_action_source=corporate_action_source,
            ),
            summary=summary,
            coverage=ReplayCoverage(
                requested_calendar_day_count=30,
                snapshot_count=30,
                market_bar_date_count=28,
                covered_market_bar_count=40,
                symbols=("AAA", "BBB"),
                missing_bar_dates=("2026-01-15",),
                unusable_bar_dates=(),
                first_bar_trade_date=resolved_start,
                last_bar_trade_date=resolved_end,
            ),
            end_state=ReplayEndState(
                ending_cash=90000.0,
                ending_market_value=ending_total_equity - 90000.0,
                ending_total_equity=ending_total_equity,
                realized_pnl=7500.0,
                unrealized_pnl=2500.0,
                ending_position_count=2,
                open_symbols=("AAA", "BBB"),
            ),
            rejection_breakdown=(
                ReplayRejectionBreakdown(code="missing_market_bar", count=rejected_intent_count),
            ),
            artifact_reference=artifact_reference,
        )

    def _market_bar(self, symbol: str, trade_date: str, close_price: float):
        from quant.backtest import MarketBar

        return MarketBar(
            symbol=symbol,
            trade_date=trade_date,
            open_price=close_price,
            high_price=close_price,
            low_price=close_price,
            close_price=close_price,
            volume=1000.0,
        )

    def _trade_intent(self, intent_id: str, symbol: str, trade_date: str, side: str):
        from quant.backtest import TradeIntent

        return TradeIntent(
            intent_id=intent_id,
            symbol=symbol,
            trade_date=trade_date,
            side=side,
            quantity=10.0,
        )


if __name__ == "__main__":
    unittest.main()
