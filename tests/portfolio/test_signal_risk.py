import unittest

from quant.portfolio import (
    BacktestSupportInput,
    BlacklistRiskRule,
    BlockedInstrument,
    CashExposureSnapshot,
    ConcentrationRiskRule,
    DrawdownRiskRule,
    ExposureRiskRule,
    HoldingState,
    LiquidityRiskRule,
    MarketConstraintRiskRule,
    MarketLotConstraint,
    PositionSizingRule,
    RiskRuleOutcomeStatus,
    RiskRuleSet,
    ScannerCandidateInput,
    SignalDecisionStatus,
    SignalIntent,
    SignalMarketContext,
    StrategySignalInput,
    StructuredSignalCompositionRequest,
    SuspensionRiskRule,
    WatchlistItem,
    build_holding_snapshot,
    build_watchlist_snapshot,
    compose_structured_signals,
    evaluate_signal_risk,
)


def _build_composition_request() -> StructuredSignalCompositionRequest:
    watchlist_snapshot = build_watchlist_snapshot(
        snapshot_id="watchlist-1",
        watchlist_id="phase6-watchlist",
        as_of_date="2026-06-12",
        items=(
            WatchlistItem(
                item_id="wl-600519",
                watchlist_id="phase6-watchlist",
                symbol="600519",
                market="CN",
                added_on="2026-06-10",
                rank=1,
            ),
            WatchlistItem(
                item_id="wl-00700",
                watchlist_id="phase6-watchlist",
                symbol="00700",
                market="HK",
                added_on="2026-06-10",
                rank=2,
            ),
        ),
    )
    holding_snapshot = build_holding_snapshot(
        snapshot_id="holding-1",
        portfolio_id="paper-account",
        as_of_date="2026-06-12",
        holdings=(
            HoldingState(
                holding_id="holding-00700",
                portfolio_id="paper-account",
                symbol="00700",
                market="HK",
                quantity=100,
                average_cost=320.0,
                cost_basis=32000.0,
                portfolio_weight=0.08,
                updated_at="2026-06-12T09:30:00",
            ),
        ),
    )
    cash_snapshot = CashExposureSnapshot(
        snapshot_id="cash-1",
        portfolio_id="paper-account",
        as_of_date="2026-06-12",
        total_equity=100000.0,
        available_cash=30000.0,
        reserved_cash=5000.0,
        gross_exposure=0.30,
        net_exposure=0.30,
    )
    return StructuredSignalCompositionRequest(
        composition_id="composition-1",
        portfolio_id="paper-account",
        effective_date="2026-06-12",
        composed_at="2026-06-12T10:00:00",
        scanner_candidates=(
            ScannerCandidateInput(
                candidate_id="scanner-00700",
                symbol="00700",
                market="HK",
                as_of_date="2026-06-12",
                ranked_at="2026-06-12T09:22:00",
                summary="scanner ranked the HK holding for add-on sizing",
                rank=2,
                score=0.8,
            ),
            ScannerCandidateInput(
                candidate_id="scanner-600519",
                symbol="600519",
                market="CN",
                as_of_date="2026-06-12",
                ranked_at="2026-06-12T09:20:00",
                summary="scanner selected the A-share symbol",
                rank=1,
                score=0.9,
            ),
        ),
        strategy_signals=(
            StrategySignalInput(
                strategy_signal_id="strategy-600519",
                strategy_id="breakout-v1",
                symbol="600519",
                market="CN",
                intent=SignalIntent.ENTER,
                as_of_date="2026-06-12",
                generated_at="2026-06-12T09:25:00",
                rationale="strategy wants a fresh long entry",
                conviction_score=0.7,
            ),
            StrategySignalInput(
                strategy_signal_id="strategy-00700",
                strategy_id="breakout-v1",
                symbol="00700",
                market="HK",
                intent=SignalIntent.INCREASE,
                as_of_date="2026-06-12",
                generated_at="2026-06-12T09:26:00",
                rationale="strategy wants to add to the existing winner",
                conviction_score=0.6,
            ),
        ),
        backtest_support=(
            BacktestSupportInput(
                report_id="backtest-600519",
                strategy_id="breakout-v1",
                symbol="600519",
                market="CN",
                as_of_date="2026-06-12",
                generated_at="2026-06-12T09:27:00",
                summary="backtest stayed within drawdown budget",
                support_score=0.5,
            ),
            BacktestSupportInput(
                report_id="backtest-00700",
                strategy_id="breakout-v1",
                symbol="00700",
                market="HK",
                as_of_date="2026-06-12",
                generated_at="2026-06-12T09:28:00",
                summary="backtest supports incremental adds",
                support_score=0.4,
            ),
        ),
        watchlist_snapshot=watchlist_snapshot,
        holding_snapshot=holding_snapshot,
        cash_exposure_snapshot=cash_snapshot,
    )


class StructuredSignalCompositionTestCase(unittest.TestCase):
    def test_composition_is_deterministic_and_preserves_provenance(self) -> None:
        result = compose_structured_signals(_build_composition_request())

        self.assertEqual(
            [signal.signal_id for signal in result.signals],
            [
                "signal:CN:600519:enter:scanner-600519:strategy-600519",
                "signal:HK:00700:increase:scanner-00700:strategy-00700",
            ],
        )
        self.assertEqual(
            [signal.priority_rank for signal in result.signals],
            [1, 2],
        )
        self.assertAlmostEqual(result.signals[0].signal_score or 0.0, 0.7)
        self.assertEqual(
            result.signals[0].decision_audit[0].decision_status,
            SignalDecisionStatus.PASSED,
        )
        self.assertEqual(
            {link.source_type.value for link in result.signals[0].source_links},
            {
                "scanner_candidate",
                "strategy_definition",
                "backtest_report",
                "watchlist_snapshot",
                "portfolio_cash_exposure_snapshot",
            },
        )
        self.assertEqual(
            {link.source_type.value for link in result.signals[1].source_links},
            {
                "scanner_candidate",
                "strategy_definition",
                "backtest_report",
                "watchlist_snapshot",
                "portfolio_holding_snapshot",
                "portfolio_cash_exposure_snapshot",
            },
        )

    def test_stale_inputs_warn_instead_of_silently_passing(self) -> None:
        request = StructuredSignalCompositionRequest(
            composition_id="composition-stale",
            portfolio_id="paper-account",
            effective_date="2026-06-12",
            composed_at="2026-06-12T10:00:00",
            stale_after_days=2,
            scanner_candidates=(
                ScannerCandidateInput(
                    candidate_id="scanner-600519",
                    symbol="600519",
                    market="CN",
                    as_of_date="2026-06-08",
                    ranked_at="2026-06-12T09:20:00",
                    summary="scanner selected the symbol",
                    rank=1,
                    score=0.9,
                ),
            ),
            strategy_signals=(
                StrategySignalInput(
                    strategy_signal_id="strategy-600519",
                    strategy_id="breakout-v1",
                    symbol="600519",
                    market="CN",
                    intent=SignalIntent.ENTER,
                    as_of_date="2026-06-08",
                    generated_at="2026-06-12T09:25:00",
                    rationale="strategy wants to enter",
                    conviction_score=0.7,
                ),
            ),
            backtest_support=(
                BacktestSupportInput(
                    report_id="backtest-600519",
                    strategy_id="breakout-v1",
                    symbol="600519",
                    market="CN",
                    as_of_date="2026-06-08",
                    generated_at="2026-06-12T09:27:00",
                    summary="backtest remains positive",
                    support_score=0.5,
                ),
            ),
        )

        result = compose_structured_signals(request)

        self.assertEqual(
            result.signals[0].decision_audit[0].decision_status,
            SignalDecisionStatus.WARNED,
        )
        self.assertIn("stale_inputs=", result.signals[0].decision_audit[0].reason_summary)

    def test_composition_rejects_duplicate_ids_and_inconsistent_holdings(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate scanner candidate ids"):
            StructuredSignalCompositionRequest(
                composition_id="composition-duplicates",
                portfolio_id="paper-account",
                effective_date="2026-06-12",
                composed_at="2026-06-12T10:00:00",
                scanner_candidates=(
                    ScannerCandidateInput(
                        candidate_id="dup-id",
                        symbol="600519",
                        market="CN",
                        as_of_date="2026-06-12",
                        ranked_at="2026-06-12T09:20:00",
                        summary="first",
                    ),
                    ScannerCandidateInput(
                        candidate_id="dup-id",
                        symbol="000001",
                        market="CN",
                        as_of_date="2026-06-12",
                        ranked_at="2026-06-12T09:21:00",
                        summary="second",
                    ),
                ),
                strategy_signals=(
                    StrategySignalInput(
                        strategy_signal_id="strategy-1",
                        strategy_id="breakout-v1",
                        symbol="600519",
                        market="CN",
                        intent=SignalIntent.ENTER,
                        as_of_date="2026-06-12",
                        generated_at="2026-06-12T09:25:00",
                        rationale="enter",
                    ),
                    StrategySignalInput(
                        strategy_signal_id="strategy-2",
                        strategy_id="breakout-v1",
                        symbol="000001",
                        market="CN",
                        intent=SignalIntent.ENTER,
                        as_of_date="2026-06-12",
                        generated_at="2026-06-12T09:26:00",
                        rationale="enter",
                    ),
                ),
            )

        request = _build_composition_request()
        bad_request = StructuredSignalCompositionRequest(
            composition_id=request.composition_id,
            portfolio_id=request.portfolio_id,
            effective_date=request.effective_date,
            composed_at=request.composed_at,
            scanner_candidates=(
                ScannerCandidateInput(
                    candidate_id="scanner-600519",
                    symbol="600519",
                    market="CN",
                    as_of_date="2026-06-12",
                    ranked_at="2026-06-12T09:20:00",
                    summary="scanner selected the symbol",
                    rank=1,
                    score=0.9,
                ),
            ),
            strategy_signals=(
                StrategySignalInput(
                    strategy_signal_id="strategy-600519",
                    strategy_id="breakout-v1",
                    symbol="600519",
                    market="CN",
                    intent=SignalIntent.EXIT,
                    as_of_date="2026-06-12",
                    generated_at="2026-06-12T09:25:00",
                    rationale="strategy wants to exit",
                ),
            ),
            holding_snapshot=None,
        )
        with self.assertRaisesRegex(ValueError, "exit intent requires an existing holding snapshot entry"):
            compose_structured_signals(bad_request)

class RiskRuleEvaluationTestCase(unittest.TestCase):
    def test_risk_evaluation_covers_all_rule_families_and_can_pass(self) -> None:
        signal = compose_structured_signals(_build_composition_request()).signals[0]
        cash_snapshot = CashExposureSnapshot(
            snapshot_id="cash-pass",
            portfolio_id="paper-account",
            as_of_date="2026-06-12",
            total_equity=100000.0,
            available_cash=30000.0,
            reserved_cash=5000.0,
            gross_exposure=0.30,
            net_exposure=0.30,
        )
        rule_set = RiskRuleSet(
            rule_set_id="rules-pass",
            portfolio_id="paper-account",
            exposure_rules=(
                ExposureRiskRule(
                    rule_id="exposure-pass",
                    max_gross_exposure=0.55,
                    max_net_exposure_abs=0.55,
                    warn_gross_exposure=0.50,
                    warn_net_exposure_abs=0.50,
                ),
            ),
            concentration_rules=(
                ConcentrationRiskRule(
                    rule_id="concentration-pass",
                    max_position_weight=0.25,
                    warn_position_weight=0.20,
                ),
            ),
            liquidity_rules=(
                LiquidityRiskRule(
                    rule_id="liquidity-pass",
                    min_average_daily_value=1_000_000.0,
                    max_participation_rate=0.10,
                    warn_min_average_daily_value=5_000_000.0,
                    warn_max_participation_rate=0.05,
                ),
            ),
            drawdown_rules=(
                DrawdownRiskRule(
                    rule_id="drawdown-pass",
                    max_drawdown=0.20,
                    warn_drawdown=0.10,
                ),
            ),
            position_sizing_rules=(
                PositionSizingRule(
                    rule_id="sizing-pass",
                    min_target_weight=0.05,
                    default_target_weight=0.15,
                    max_target_weight=0.20,
                    increment_weight=0.05,
                ),
            ),
            blacklist_rules=(
                BlacklistRiskRule(
                    rule_id="blacklist-pass",
                    blocked_instruments=(),
                ),
            ),
            suspension_rules=(
                SuspensionRiskRule(rule_id="suspension-pass"),
            ),
            market_constraint_rules=(
                MarketConstraintRiskRule(
                    rule_id="market-pass",
                    allowed_markets=("CN", "HK"),
                    lot_constraints=(MarketLotConstraint(market="CN", lot_size=1),),
                ),
            ),
        )
        result = evaluate_signal_risk(
            signal=signal,
            rule_set=rule_set,
            market_context=SignalMarketContext(
                symbol="600519",
                market="CN",
                as_of_date="2026-06-12",
                latest_price=100.0,
                average_daily_value=10_000_000.0,
                current_drawdown=0.05,
            ),
            evaluated_at="2026-06-12T10:30:00",
            cash_exposure_snapshot=cash_snapshot,
        )

        self.assertEqual(result.overall_status, SignalDecisionStatus.PASSED)
        self.assertEqual(result.signal.version, 2)
        self.assertEqual(result.signal.decision_audit[-1].decision_status, SignalDecisionStatus.PASSED)
        self.assertEqual(
            {outcome.rule_type.value for outcome in result.rule_outcomes},
            {
                "exposure",
                "concentration",
                "liquidity",
                "drawdown",
                "position_sizing",
                "blacklist",
                "suspension",
                "market_constraint",
            },
        )

    def test_risk_evaluation_can_warn_and_block(self) -> None:
        signal = compose_structured_signals(_build_composition_request()).signals[0]
        warn_rule_set = RiskRuleSet(
            rule_set_id="rules-warn",
            portfolio_id="paper-account",
            exposure_rules=(
                ExposureRiskRule(
                    rule_id="exposure-warn",
                    max_gross_exposure=0.60,
                    max_net_exposure_abs=0.60,
                    warn_gross_exposure=0.34,
                    warn_net_exposure_abs=0.34,
                ),
            ),
            drawdown_rules=(
                DrawdownRiskRule(
                    rule_id="drawdown-warn",
                    max_drawdown=0.20,
                    warn_drawdown=0.10,
                ),
            ),
            position_sizing_rules=(
                PositionSizingRule(
                    rule_id="sizing-warn",
                    min_target_weight=0.05,
                    default_target_weight=0.15,
                    max_target_weight=0.20,
                    increment_weight=0.05,
                ),
            ),
        )
        warn_result = evaluate_signal_risk(
            signal=signal,
            rule_set=warn_rule_set,
            market_context=SignalMarketContext(
                symbol="600519",
                market="CN",
                as_of_date="2026-06-12",
                latest_price=100.0,
                average_daily_value=10_000_000.0,
                current_drawdown=0.12,
            ),
            evaluated_at="2026-06-12T10:30:00",
            cash_exposure_snapshot=CashExposureSnapshot(
                snapshot_id="cash-warn",
                portfolio_id="paper-account",
                as_of_date="2026-06-12",
                total_equity=100000.0,
                available_cash=5000.0,
                reserved_cash=5000.0,
                gross_exposure=0.30,
                net_exposure=0.30,
            ),
        )

        self.assertEqual(warn_result.overall_status, SignalDecisionStatus.WARNED)
        self.assertIn(
            RiskRuleOutcomeStatus.WARN,
            {outcome.status for outcome in warn_result.rule_outcomes},
        )

        block_rule_set = RiskRuleSet(
            rule_set_id="rules-block",
            portfolio_id="paper-account",
            concentration_rules=(
                ConcentrationRiskRule(
                    rule_id="concentration-block",
                    max_position_weight=0.04,
                    warn_position_weight=0.03,
                ),
            ),
            drawdown_rules=(
                DrawdownRiskRule(
                    rule_id="drawdown-block",
                    max_drawdown=0.20,
                    warn_drawdown=0.10,
                ),
            ),
            position_sizing_rules=(
                PositionSizingRule(
                    rule_id="sizing-block",
                    min_target_weight=0.05,
                    default_target_weight=0.05,
                    max_target_weight=0.05,
                    increment_weight=0.05,
                ),
            ),
            blacklist_rules=(
                BlacklistRiskRule(
                    rule_id="blacklist-block",
                    blocked_instruments=(
                        BlockedInstrument(
                            symbol="600519",
                            market="CN",
                            reason="owner blacklist",
                        ),
                    ),
                ),
            ),
            suspension_rules=(
                SuspensionRiskRule(rule_id="suspension-block"),
            ),
            market_constraint_rules=(
                MarketConstraintRiskRule(
                    rule_id="market-block",
                    allowed_markets=("CN",),
                    lot_constraints=(MarketLotConstraint(market="CN", lot_size=100),),
                ),
            ),
        )
        block_result = evaluate_signal_risk(
            signal=signal,
            rule_set=block_rule_set,
            market_context=SignalMarketContext(
                symbol="600519",
                market="CN",
                as_of_date="2026-06-12",
                latest_price=91.0,
                average_daily_value=10_000_000.0,
                current_drawdown=0.25,
                is_suspended=True,
            ),
            evaluated_at="2026-06-12T10:30:00",
            cash_exposure_snapshot=CashExposureSnapshot(
                snapshot_id="cash-block",
                portfolio_id="paper-account",
                as_of_date="2026-06-12",
                total_equity=100000.0,
                available_cash=30000.0,
                reserved_cash=5000.0,
                gross_exposure=0.30,
                net_exposure=0.30,
            ),
        )

        self.assertEqual(block_result.overall_status, SignalDecisionStatus.BLOCKED)
        self.assertIn(
            RiskRuleOutcomeStatus.BLOCK,
            {outcome.status for outcome in block_result.rule_outcomes},
        )
        self.assertEqual(
            block_result.signal.decision_audit[-1].decision_status,
            SignalDecisionStatus.BLOCKED,
        )

    def test_enter_without_sizing_guidance_blocks_exposure_and_concentration_explicitly(self) -> None:
        signal = compose_structured_signals(_build_composition_request()).signals[0]
        result = evaluate_signal_risk(
            signal=signal,
            rule_set=RiskRuleSet(
                rule_set_id="rules-no-sizing-enter",
                portfolio_id="paper-account",
                exposure_rules=(
                    ExposureRiskRule(
                        rule_id="exposure-no-sizing",
                        max_gross_exposure=0.55,
                        max_net_exposure_abs=0.55,
                    ),
                ),
                concentration_rules=(
                    ConcentrationRiskRule(
                        rule_id="concentration-no-sizing",
                        max_position_weight=0.25,
                    ),
                ),
            ),
            market_context=SignalMarketContext(
                symbol="600519",
                market="CN",
                as_of_date="2026-06-12",
                latest_price=100.0,
                average_daily_value=10_000_000.0,
            ),
            evaluated_at="2026-06-12T10:30:00",
            cash_exposure_snapshot=CashExposureSnapshot(
                snapshot_id="cash-no-sizing-enter",
                portfolio_id="paper-account",
                as_of_date="2026-06-12",
                total_equity=100000.0,
                available_cash=30000.0,
                reserved_cash=5000.0,
                gross_exposure=0.30,
                net_exposure=0.30,
            ),
        )

        self.assertIsNone(result.sizing_guidance)
        self.assertEqual(result.overall_status, SignalDecisionStatus.BLOCKED)
        self.assertEqual(
            {
                (outcome.rule_type.value, outcome.status.value, outcome.reason_code)
                for outcome in result.rule_outcomes
            },
            {
                ("exposure", "block", "exposure_missing_sizing_guidance"),
                ("concentration", "block", "concentration_missing_sizing_guidance"),
            },
        )

    def test_increase_without_sizing_guidance_blocks_lot_size_explicitly(self) -> None:
        signal = compose_structured_signals(_build_composition_request()).signals[1]
        result = evaluate_signal_risk(
            signal=signal,
            rule_set=RiskRuleSet(
                rule_set_id="rules-no-sizing-increase",
                portfolio_id="paper-account",
                market_constraint_rules=(
                    MarketConstraintRiskRule(
                        rule_id="market-no-sizing",
                        allowed_markets=("HK",),
                        lot_constraints=(MarketLotConstraint(market="HK", lot_size=100),),
                    ),
                ),
            ),
            market_context=SignalMarketContext(
                symbol="00700",
                market="HK",
                as_of_date="2026-06-12",
                latest_price=320.0,
                average_daily_value=20_000_000.0,
            ),
            evaluated_at="2026-06-12T10:30:00",
            holding_snapshot=_build_composition_request().holding_snapshot,
        )

        self.assertIsNone(result.sizing_guidance)
        self.assertEqual(result.overall_status, SignalDecisionStatus.BLOCKED)
        self.assertEqual(len(result.rule_outcomes), 1)
        self.assertEqual(result.rule_outcomes[0].status, RiskRuleOutcomeStatus.BLOCK)
        self.assertEqual(
            result.rule_outcomes[0].reason_code,
            "market_constraint_missing_sizing_guidance",
        )
        self.assertIn("lot-size evaluation unavailable", result.rule_outcomes[0].reason_summary)

    def test_invalid_risk_configuration_and_non_finite_inputs_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate risk rule ids"):
            RiskRuleSet(
                rule_set_id="rules-invalid",
                portfolio_id="paper-account",
                exposure_rules=(
                    ExposureRiskRule(
                        rule_id="duplicate-id",
                        max_gross_exposure=0.5,
                        max_net_exposure_abs=0.5,
                    ),
                ),
                concentration_rules=(
                    ConcentrationRiskRule(
                        rule_id="duplicate-id",
                        max_position_weight=0.2,
                    ),
                ),
            )

        with self.assertRaisesRegex(ValueError, "latest_price must be finite"):
            SignalMarketContext(
                symbol="600519",
                market="CN",
                as_of_date="2026-06-12",
                latest_price=float("nan"),
                average_daily_value=10_000_000.0,
            )

if __name__ == "__main__":
    unittest.main()
