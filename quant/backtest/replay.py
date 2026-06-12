"""Deterministic offline historical replay primitives."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from .contracts import (
    BacktestRequest,
    MarketBar,
    PortfolioSnapshot,
    PositionSnapshot,
    RejectedTradeIntent,
    ReplayConfig,
    ReplayResult,
    ReplaySummary,
    TradeIntent,
    TradeSide,
    coerce_replay_config,
    ensure_valid_contracts,
)


@dataclass
class _PositionState:
    quantity: float
    average_cost: float


def run_historical_replay(
    config: ReplayConfig | BacktestRequest,
    market_bars: Iterable[MarketBar],
    trade_intents: Iterable[TradeIntent],
) -> ReplayResult:
    """Replay caller-provided bars and intents without persistence or network access.

    The primitive is intentionally simple:
    - trades execute against the same-day close with symmetric slippage
    - transaction costs are modeled in basis points on traded notional
    - positions are marked to the latest close seen on or before each snapshot date
    - rejected intents are reported, not retried
    """

    resolved_config = coerce_replay_config(config)
    ordered_bars = tuple(market_bars)
    ordered_intents = tuple(trade_intents)
    ensure_valid_contracts(resolved_config, ordered_bars, ordered_intents)

    bar_map = {(bar.symbol.strip(), bar.trade_date): bar for bar in ordered_bars}
    intents_by_date: dict[str, list[TradeIntent]] = {}
    replay_dates: set[str] = set()

    for bar in ordered_bars:
        if _date_in_window(
            bar.trade_date,
            start_trade_date=resolved_config.start_trade_date,
            end_trade_date=resolved_config.end_trade_date,
        ):
            replay_dates.add(bar.trade_date)

    for trade_intent in ordered_intents:
        intents_by_date.setdefault(trade_intent.trade_date, []).append(trade_intent)
        replay_dates.add(trade_intent.trade_date)

    sorted_dates = sorted(replay_dates)

    cash = resolved_config.starting_capital
    realized_pnl = 0.0
    positions: dict[str, _PositionState] = {}
    last_prices: dict[str, float] = {}
    rejected_intents: list[RejectedTradeIntent] = []
    snapshots: list[PortfolioSnapshot] = []
    executed_trade_count = 0
    peak_equity = resolved_config.starting_capital
    max_drawdown = 0.0
    transaction_cost_rate = resolved_config.transaction_cost_bps / 10_000.0
    slippage_rate = resolved_config.slippage_bps / 10_000.0

    for trade_date in sorted_dates:
        for trade_intent in intents_by_date.get(trade_date, []):
            bar = bar_map.get((trade_intent.symbol.strip(), trade_date))
            if bar is None:
                rejected_intents.append(
                    RejectedTradeIntent(
                        intent=trade_intent,
                        code="missing_market_bar",
                        message="no caller-provided market bar exists for the symbol and trade date",
                    )
                )
                continue
            if bar.volume is not None and bar.volume <= 0:
                rejected_intents.append(
                    RejectedTradeIntent(
                        intent=trade_intent,
                        code="unusable_market_bar",
                        message="market bar volume is zero so the replay will not execute the intent",
                    )
                )
                continue

            if trade_intent.side is TradeSide.BUY:
                execution_price = bar.close_price * (1.0 + slippage_rate)
                gross_notional = execution_price * trade_intent.quantity
                transaction_cost = gross_notional * transaction_cost_rate
                total_debit = gross_notional + transaction_cost
                if cash + 1e-12 < total_debit:
                    rejected_intents.append(
                        RejectedTradeIntent(
                            intent=trade_intent,
                            code="insufficient_cash",
                            message="cash is insufficient to execute the buy intent after cost and slippage",
                        )
                    )
                    continue

                state = positions.get(trade_intent.symbol)
                prior_quantity = state.quantity if state is not None else 0.0
                prior_cost = state.average_cost if state is not None else 0.0
                new_quantity = prior_quantity + trade_intent.quantity
                new_average_cost = ((prior_quantity * prior_cost) + total_debit) / new_quantity

                cash -= total_debit
                positions[trade_intent.symbol] = _PositionState(
                    quantity=new_quantity,
                    average_cost=new_average_cost,
                )
                executed_trade_count += 1
                continue

            state = positions.get(trade_intent.symbol)
            if state is None or state.quantity + 1e-12 < trade_intent.quantity:
                rejected_intents.append(
                    RejectedTradeIntent(
                        intent=trade_intent,
                        code="insufficient_position",
                        message="held quantity is insufficient to execute the sell intent",
                    )
                )
                continue

            execution_price = bar.close_price * (1.0 - slippage_rate)
            gross_notional = execution_price * trade_intent.quantity
            transaction_cost = gross_notional * transaction_cost_rate
            net_credit = gross_notional - transaction_cost
            cost_basis = state.average_cost * trade_intent.quantity

            cash += net_credit
            realized_pnl += net_credit - cost_basis
            remaining_quantity = state.quantity - trade_intent.quantity
            if remaining_quantity <= 1e-12:
                positions.pop(trade_intent.symbol, None)
            else:
                positions[trade_intent.symbol] = _PositionState(
                    quantity=remaining_quantity,
                    average_cost=state.average_cost,
                )
            executed_trade_count += 1

        for bar in ordered_bars:
            if bar.trade_date == trade_date:
                last_prices[bar.symbol] = bar.close_price

        snapshot = _build_snapshot(
            trade_date=trade_date,
            cash=cash,
            realized_pnl=realized_pnl,
            positions=positions,
            last_prices=last_prices,
        )
        snapshots.append(snapshot)

        peak_equity = max(peak_equity, snapshot.total_equity)
        if peak_equity > 0:
            max_drawdown = max(max_drawdown, (peak_equity - snapshot.total_equity) / peak_equity)

    ending_snapshot = snapshots[-1] if snapshots else _empty_snapshot(
        trade_date=resolved_config.end_trade_date,
        cash=resolved_config.starting_capital,
    )

    summary = ReplaySummary(
        request_id=resolved_config.request_id,
        strategy_id=resolved_config.strategy_id,
        strategy_version=resolved_config.strategy_version,
        start_trade_date=resolved_config.start_trade_date,
        end_trade_date=resolved_config.end_trade_date,
        starting_capital=resolved_config.starting_capital,
        ending_cash=ending_snapshot.cash,
        ending_market_value=ending_snapshot.market_value,
        ending_total_equity=ending_snapshot.total_equity,
        realized_pnl=ending_snapshot.realized_pnl,
        unrealized_pnl=ending_snapshot.unrealized_pnl,
        total_return=(ending_snapshot.total_equity - resolved_config.starting_capital)
        / resolved_config.starting_capital,
        max_drawdown=max_drawdown,
        executed_trade_count=executed_trade_count,
        rejected_intent_count=len(rejected_intents),
        snapshot_count=len(snapshots),
    )

    return ReplayResult(
        config=resolved_config,
        snapshots=tuple(snapshots),
        summary=summary,
        rejected_intents=tuple(rejected_intents),
    )


def _build_snapshot(
    *,
    trade_date: str,
    cash: float,
    realized_pnl: float,
    positions: dict[str, _PositionState],
    last_prices: dict[str, float],
) -> PortfolioSnapshot:
    marked_positions: list[PositionSnapshot] = []
    market_value = 0.0
    unrealized_pnl = 0.0

    for symbol in sorted(positions):
        state = positions[symbol]
        market_price = last_prices.get(symbol, state.average_cost)
        symbol_market_value = state.quantity * market_price
        symbol_unrealized = (market_price - state.average_cost) * state.quantity
        marked_positions.append(
            PositionSnapshot(
                symbol=symbol,
                quantity=state.quantity,
                average_cost=state.average_cost,
                market_price=market_price,
                market_value=symbol_market_value,
                unrealized_pnl=symbol_unrealized,
            )
        )
        market_value += symbol_market_value
        unrealized_pnl += symbol_unrealized

    return PortfolioSnapshot(
        trade_date=trade_date,
        cash=cash,
        positions=tuple(marked_positions),
        realized_pnl=realized_pnl,
        unrealized_pnl=unrealized_pnl,
        market_value=market_value,
        total_equity=cash + market_value,
    )


def _empty_snapshot(*, trade_date: str, cash: float) -> PortfolioSnapshot:
    return PortfolioSnapshot(
        trade_date=trade_date,
        cash=cash,
        positions=(),
        realized_pnl=0.0,
        unrealized_pnl=0.0,
        market_value=0.0,
        total_equity=cash,
    )


def _date_in_window(
    trade_date: str,
    *,
    start_trade_date: str,
    end_trade_date: str,
) -> bool:
    current_date = date.fromisoformat(trade_date)
    return date.fromisoformat(start_trade_date) <= current_date <= date.fromisoformat(end_trade_date)
