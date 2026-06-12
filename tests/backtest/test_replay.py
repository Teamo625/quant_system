import unittest

from quant.backtest import (
    BacktestRequest,
    MarketBar,
    ReplayConfig,
    SelectionReference,
    SelectionReferenceKind,
    StrategyReference,
    TradeIntent,
    TradeSide,
    run_historical_replay,
)


class HistoricalReplayTestCase(unittest.TestCase):
    def test_run_historical_replay_tracks_cash_positions_and_equity(self) -> None:
        request = BacktestRequest(
            request_id="replay-001",
            strategy_ref=StrategyReference(
                strategy_id="mean_reversion_research",
                strategy_version="0.1.0",
            ),
            selection_ref=SelectionReference(
                reference_kind=SelectionReferenceKind.UNIVERSE,
                reference_id="cn-core",
                reference_date="2026-01-01",
                market="CN",
            ),
            start_trade_date="2026-01-02",
            end_trade_date="2026-01-03",
            starting_capital=1000.0,
            transaction_cost_bps=10.0,
            slippage_bps=20.0,
        )
        bars = (
            MarketBar(
                symbol="600000.SH",
                trade_date="2026-01-02",
                open_price=9.8,
                high_price=10.2,
                low_price=9.7,
                close_price=10.0,
                volume=1000.0,
            ),
            MarketBar(
                symbol="600000.SH",
                trade_date="2026-01-03",
                open_price=10.5,
                high_price=11.2,
                low_price=10.3,
                close_price=11.0,
                volume=1200.0,
            ),
        )
        intents = (
            TradeIntent(
                intent_id="intent-buy",
                symbol="600000.SH",
                trade_date="2026-01-02",
                side=TradeSide.BUY,
                quantity=10.0,
            ),
            TradeIntent(
                intent_id="intent-sell",
                symbol="600000.SH",
                trade_date="2026-01-03",
                side=TradeSide.SELL,
                quantity=4.0,
            ),
        )

        result = run_historical_replay(request, bars, intents)

        self.assertEqual(result.config, ReplayConfig.from_backtest_request(request))
        self.assertEqual([snapshot.trade_date for snapshot in result.snapshots], ["2026-01-02", "2026-01-03"])
        self.assertEqual(len(result.rejected_intents), 0)

        day_one = result.snapshots[0]
        self.assertAlmostEqual(day_one.cash, 899.6998)
        self.assertAlmostEqual(day_one.market_value, 100.0)
        self.assertAlmostEqual(day_one.unrealized_pnl, -0.3002)
        self.assertAlmostEqual(day_one.total_equity, 999.6998)
        self.assertEqual(len(day_one.positions), 1)
        self.assertAlmostEqual(day_one.positions[0].average_cost, 10.03002)

        day_two = result.snapshots[1]
        self.assertAlmostEqual(day_two.cash, 943.567888)
        self.assertAlmostEqual(day_two.realized_pnl, 3.748008)
        self.assertAlmostEqual(day_two.unrealized_pnl, 5.81988)
        self.assertAlmostEqual(day_two.market_value, 66.0)
        self.assertAlmostEqual(day_two.total_equity, 1009.567888)
        self.assertAlmostEqual(day_two.positions[0].quantity, 6.0)

        self.assertAlmostEqual(result.summary.ending_cash, 943.567888)
        self.assertAlmostEqual(result.summary.ending_market_value, 66.0)
        self.assertAlmostEqual(result.summary.ending_total_equity, 1009.567888)
        self.assertAlmostEqual(result.summary.realized_pnl, 3.748008)
        self.assertAlmostEqual(result.summary.unrealized_pnl, 5.81988)
        self.assertAlmostEqual(result.summary.total_return, 0.009567888)
        self.assertAlmostEqual(result.summary.max_drawdown, 0.0003002)
        self.assertEqual(result.summary.executed_trade_count, 2)
        self.assertEqual(result.summary.rejected_intent_count, 0)
        self.assertEqual(result.summary.snapshot_count, 2)

    def test_run_historical_replay_reports_missing_or_unusable_market_bars(self) -> None:
        config = ReplayConfig(
            request_id="replay-002",
            strategy_id="s1",
            strategy_version="1.0.0",
            start_trade_date="2026-01-02",
            end_trade_date="2026-01-02",
            starting_capital=1000.0,
            transaction_cost_bps=0.0,
            slippage_bps=0.0,
        )
        bars = (
            MarketBar(
                symbol="AAA",
                trade_date="2026-01-02",
                open_price=10.0,
                high_price=10.0,
                low_price=10.0,
                close_price=10.0,
                volume=0.0,
            ),
        )
        intents = (
            TradeIntent(
                intent_id="missing-bar",
                symbol="BBB",
                trade_date="2026-01-02",
                side=TradeSide.BUY,
                quantity=1.0,
            ),
            TradeIntent(
                intent_id="zero-volume",
                symbol="AAA",
                trade_date="2026-01-02",
                side=TradeSide.BUY,
                quantity=1.0,
            ),
        )

        result = run_historical_replay(config, bars, intents)

        self.assertEqual(
            [(entry.intent.intent_id, entry.code) for entry in result.rejected_intents],
            [("missing-bar", "missing_market_bar"), ("zero-volume", "unusable_market_bar")],
        )
        self.assertEqual(result.summary.executed_trade_count, 0)
        self.assertEqual(result.summary.rejected_intent_count, 2)
        self.assertAlmostEqual(result.summary.ending_total_equity, 1000.0)

    def test_run_historical_replay_rejects_invalid_inputs_before_processing(self) -> None:
        config = ReplayConfig(
            request_id="replay-003",
            strategy_id="s1",
            strategy_version="1.0.0",
            start_trade_date="2026-01-02",
            end_trade_date="2026-01-05",
            starting_capital=1000.0,
            transaction_cost_bps=0.0,
            slippage_bps=0.0,
        )
        bars = (
            MarketBar(
                symbol="AAA",
                trade_date="2026-01-02",
                open_price=10.0,
                high_price=10.0,
                low_price=10.0,
                close_price=10.0,
                volume=100.0,
            ),
        )
        intents = (
            TradeIntent(
                intent_id="late-intent",
                symbol="AAA",
                trade_date="2026-01-06",
                side=TradeSide.BUY,
                quantity=1.0,
            ),
        )

        with self.assertRaisesRegex(ValueError, "outside_replay_window"):
            run_historical_replay(config, bars, intents)

    def test_run_historical_replay_executes_validated_string_buy_side_as_buy(self) -> None:
        config = ReplayConfig(
            request_id="replay-004",
            strategy_id="s1",
            strategy_version="1.0.0",
            start_trade_date="2026-01-02",
            end_trade_date="2026-01-02",
            starting_capital=1000.0,
            transaction_cost_bps=0.0,
            slippage_bps=0.0,
        )
        bars = (
            MarketBar(
                symbol="AAA",
                trade_date="2026-01-02",
                open_price=10.0,
                high_price=10.0,
                low_price=10.0,
                close_price=10.0,
                volume=100.0,
            ),
        )
        intents = (
            TradeIntent(
                intent_id="string-buy",
                symbol="AAA",
                trade_date="2026-01-02",
                side="buy",
                quantity=2.0,
            ),
        )

        result = run_historical_replay(config, bars, intents)

        self.assertEqual(result.summary.executed_trade_count, 1)
        self.assertEqual(result.summary.rejected_intent_count, 0)
        self.assertEqual(result.rejected_intents, ())
        self.assertAlmostEqual(result.snapshots[0].cash, 980.0)
        self.assertEqual(len(result.snapshots[0].positions), 1)
        self.assertAlmostEqual(result.snapshots[0].positions[0].quantity, 2.0)
        self.assertAlmostEqual(result.snapshots[0].positions[0].average_cost, 10.0)

    def test_run_historical_replay_executes_validated_string_sell_side_as_sell(self) -> None:
        config = ReplayConfig(
            request_id="replay-005",
            strategy_id="s1",
            strategy_version="1.0.0",
            start_trade_date="2026-01-02",
            end_trade_date="2026-01-03",
            starting_capital=1000.0,
            transaction_cost_bps=0.0,
            slippage_bps=0.0,
        )
        bars = (
            MarketBar(
                symbol="AAA",
                trade_date="2026-01-02",
                open_price=10.0,
                high_price=10.0,
                low_price=10.0,
                close_price=10.0,
                volume=100.0,
            ),
            MarketBar(
                symbol="AAA",
                trade_date="2026-01-03",
                open_price=11.0,
                high_price=11.0,
                low_price=11.0,
                close_price=11.0,
                volume=100.0,
            ),
        )
        intents = (
            TradeIntent(
                intent_id="seed-position",
                symbol="AAA",
                trade_date="2026-01-02",
                side=TradeSide.BUY,
                quantity=2.0,
            ),
            TradeIntent(
                intent_id="string-sell",
                symbol="AAA",
                trade_date="2026-01-03",
                side="sell",
                quantity=2.0,
            ),
        )

        result = run_historical_replay(config, bars, intents)

        self.assertEqual(result.summary.executed_trade_count, 2)
        self.assertEqual(result.summary.rejected_intent_count, 0)
        self.assertEqual(result.rejected_intents, ())
        self.assertEqual(result.snapshots[1].positions, ())
        self.assertAlmostEqual(result.snapshots[1].cash, 1002.0)
        self.assertAlmostEqual(result.snapshots[1].realized_pnl, 2.0)


if __name__ == "__main__":
    unittest.main()
