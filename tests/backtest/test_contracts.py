import importlib
import math
import unittest
from datetime import datetime

from quant.backtest import (
    BacktestRequest,
    BacktestResultSummary,
    MarketBar,
    PortfolioSnapshot,
    PositionSnapshot,
    ReplayConfig,
    ReplaySummary,
    ResultStatus,
    SelectionReference,
    SelectionReferenceKind,
    StrategyReference,
    TradeIntent,
    TradeSide,
    validate_backtest_request,
    validate_backtest_result_summary,
    validate_market_bar,
    validate_portfolio_snapshot,
    validate_replay_config,
    validate_replay_summary,
    validate_trade_intent,
)


class BacktestContractsTestCase(unittest.TestCase):
    def test_backtest_package_exports_contracts_and_replay_primitives(self) -> None:
        package = importlib.import_module("quant.backtest")
        module = importlib.import_module("quant.backtest.contracts")

        self.assertTrue(hasattr(package, "BacktestRequest"))
        self.assertTrue(hasattr(package, "ReplayConfig"))
        self.assertTrue(hasattr(package, "run_historical_replay"))
        self.assertTrue(hasattr(module, "TradeSide"))

    def test_valid_backtest_request_and_summary_pass_validation(self) -> None:
        request = BacktestRequest(
            request_id="bt-2026q2-cn-core",
            strategy_ref=StrategyReference(
                strategy_id="mean_reversion_research",
                strategy_version="0.1.0",
            ),
            selection_ref=SelectionReference(
                reference_kind=SelectionReferenceKind.UNIVERSE,
                reference_id="cn-core",
                reference_date="2026-06-01",
                market="CN",
            ),
            start_trade_date="2026-01-02",
            end_trade_date="2026-05-29",
            starting_capital=1_000_000.0,
            transaction_cost_bps=5.0,
            slippage_bps=3.5,
        )
        summary = BacktestResultSummary(
            summary_id="bt-2026q2-cn-core-summary",
            request_id="bt-2026q2-cn-core",
            strategy_id="mean_reversion_research",
            strategy_version="0.1.0",
            start_trade_date="2026-01-02",
            end_trade_date="2026-05-29",
            result_status=ResultStatus.DECLARED,
            generated_at=datetime(2026, 6, 4, 9, 30, 0),
            metric_keys=("net_return", "max_drawdown"),
            artifact_reference="summary-placeholder",
        )

        self.assertEqual(validate_backtest_request(request), ())
        self.assertEqual(validate_backtest_result_summary(summary), ())
        self.assertEqual(validate_replay_config(ReplayConfig.from_backtest_request(request)), ())

    def test_backtest_request_rejects_missing_strategy_reference(self) -> None:
        issues = validate_backtest_request(
            {
                "request_id": "bt-001",
                "strategy_ref": None,
                "selection_ref": {
                    "reference_kind": SelectionReferenceKind.CANDIDATE_LIST,
                    "reference_id": "scan-2026-06-04",
                    "reference_date": "2026-06-04",
                    "market": "CN",
                },
                "start_trade_date": "2026-01-01",
                "end_trade_date": "2026-01-31",
                "starting_capital": 100000.0,
                "transaction_cost_bps": 1.0,
                "slippage_bps": 1.0,
                "schema_version": "1.0.0",
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {("strategy_ref", "missing_required")},
        )

    def test_backtest_request_rejects_bad_dates_and_negative_costs(self) -> None:
        issues = validate_backtest_request(
            {
                "request_id": "bt-002",
                "strategy_ref": {
                    "strategy_id": "s1",
                    "strategy_version": "1.0.0",
                },
                "selection_ref": {
                    "reference_kind": SelectionReferenceKind.UNIVERSE,
                    "reference_id": "cn-core",
                    "reference_date": "2026/06/01",
                    "market": "CN",
                },
                "start_trade_date": "2026-02-01",
                "end_trade_date": "2026-01-01",
                "starting_capital": 0,
                "transaction_cost_bps": -0.1,
                "slippage_bps": -1,
                "schema_version": "1.0.0",
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                ("selection_ref.reference_date", "invalid_date_string"),
                ("end_trade_date", "invalid_date_order"),
                ("starting_capital", "invalid_value"),
                ("transaction_cost_bps", "invalid_value"),
                ("slippage_bps", "invalid_value"),
            },
        )

    def test_backtest_request_rejects_empty_ids_and_unknown_reference_kind(self) -> None:
        issues = validate_backtest_request(
            {
                "request_id": "",
                "strategy_ref": {
                    "strategy_id": "",
                    "strategy_version": " ",
                },
                "selection_ref": {
                    "reference_kind": "watchlist",
                    "reference_id": " ",
                    "reference_date": "2026-06-01",
                    "market": "",
                },
                "start_trade_date": "bad-date",
                "end_trade_date": "2026-06-30",
                "starting_capital": 100000.0,
                "transaction_cost_bps": 0.0,
                "slippage_bps": 0.0,
                "schema_version": "2.0.0",
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                ("request_id", "empty_text"),
                ("strategy_ref.strategy_id", "empty_text"),
                ("strategy_ref.strategy_version", "empty_text"),
                ("selection_ref.reference_kind", "unsupported_reference_kind"),
                ("selection_ref.reference_id", "empty_text"),
                ("selection_ref.market", "empty_text"),
                ("start_trade_date", "invalid_date_string"),
                ("schema_version", "unsupported_schema_version"),
            },
        )

    def test_result_summary_rejects_duplicate_metric_keys_and_bad_metadata(self) -> None:
        issues = validate_backtest_result_summary(
            {
                "summary_id": " ",
                "request_id": "bt-001",
                "strategy_id": "s1",
                "strategy_version": "1.0.0",
                "start_trade_date": "2026-01-01",
                "end_trade_date": "2025-12-31",
                "result_status": "unknown",
                "generated_at": "2026-06-04T09:30:00",
                "metric_keys": ("net_return", "net_return"),
                "artifact_reference": "",
                "extra": True,
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                ("summary_id", "empty_text"),
                ("end_trade_date", "invalid_date_order"),
                ("result_status", "unsupported_result_status"),
                ("generated_at", "invalid_type"),
                ("metric_keys", "duplicate_metric_key"),
                ("artifact_reference", "empty_text"),
                ("extra", "unexpected_field"),
            },
        )

    def test_replay_input_contracts_reject_invalid_market_bar_and_trade_intent(self) -> None:
        config = ReplayConfig(
            request_id="replay-001",
            strategy_id="s1",
            strategy_version="1.0.0",
            start_trade_date="2026-01-01",
            end_trade_date="2026-01-31",
            starting_capital=100000.0,
            transaction_cost_bps=2.0,
            slippage_bps=1.0,
        )

        market_bar_issues = validate_market_bar(
            {
                "symbol": " ",
                "trade_date": "2026/01/02",
                "open_price": 10.0,
                "high_price": 9.0,
                "low_price": 11.0,
                "close_price": 0.0,
                "volume": -1.0,
            }
        )
        trade_intent_issues = validate_trade_intent(
            {
                "intent_id": "intent-001",
                "symbol": "",
                "trade_date": "2026-02-01",
                "side": "hold",
                "quantity": math.inf,
            },
            config=config,
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in market_bar_issues},
            {
                ("symbol", "empty_text"),
                ("trade_date", "invalid_date_string"),
                ("high_price", "invalid_price_range"),
                ("open_price", "invalid_price_range"),
                ("close_price", "invalid_value"),
                ("volume", "invalid_value"),
            },
        )
        self.assertEqual(
            {(issue.field, issue.code) for issue in trade_intent_issues},
            {
                ("symbol", "empty_text"),
                ("trade_date", "outside_replay_window"),
                ("side", "unsupported_trade_side"),
                ("quantity", "invalid_value"),
            },
        )

    def test_portfolio_snapshot_and_replay_summary_validate(self) -> None:
        snapshot = PortfolioSnapshot(
            trade_date="2026-01-02",
            cash=900.0,
            positions=(
                PositionSnapshot(
                    symbol="600000.SH",
                    quantity=10.0,
                    average_cost=10.05,
                    market_price=10.2,
                    market_value=102.0,
                    unrealized_pnl=1.5,
                ),
            ),
            realized_pnl=0.0,
            unrealized_pnl=1.5,
            market_value=102.0,
            total_equity=1002.0,
        )
        summary = ReplaySummary(
            request_id="replay-001",
            strategy_id="s1",
            strategy_version="1.0.0",
            start_trade_date="2026-01-01",
            end_trade_date="2026-01-31",
            starting_capital=1000.0,
            ending_cash=900.0,
            ending_market_value=102.0,
            ending_total_equity=1002.0,
            realized_pnl=0.0,
            unrealized_pnl=1.5,
            total_return=0.002,
            max_drawdown=0.01,
            executed_trade_count=1,
            rejected_intent_count=0,
            snapshot_count=1,
        )

        self.assertEqual(validate_portfolio_snapshot(snapshot), ())
        self.assertEqual(validate_replay_summary(summary), ())


if __name__ == "__main__":
    unittest.main()
