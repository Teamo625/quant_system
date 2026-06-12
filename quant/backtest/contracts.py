"""Offline-safe BacktestEngine contracts and replay primitives."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import date, datetime
from enum import Enum
from math import isfinite
from typing import Any, Mapping, Sequence


BACKTEST_CONTRACT_SCHEMA_VERSION = "1.0.0"

STRATEGY_REFERENCE_FIELDS: tuple[str, ...] = (
    "strategy_id",
    "strategy_version",
)
SELECTION_REFERENCE_FIELDS: tuple[str, ...] = (
    "reference_kind",
    "reference_id",
    "reference_date",
    "market",
)
BACKTEST_REQUEST_FIELDS: tuple[str, ...] = (
    "request_id",
    "strategy_ref",
    "selection_ref",
    "start_trade_date",
    "end_trade_date",
    "starting_capital",
    "transaction_cost_bps",
    "slippage_bps",
    "schema_version",
)
RESULT_SUMMARY_FIELDS: tuple[str, ...] = (
    "summary_id",
    "request_id",
    "strategy_id",
    "strategy_version",
    "start_trade_date",
    "end_trade_date",
    "result_status",
    "generated_at",
    "metric_keys",
    "artifact_reference",
)
MARKET_BAR_FIELDS: tuple[str, ...] = (
    "symbol",
    "trade_date",
    "open_price",
    "high_price",
    "low_price",
    "close_price",
    "volume",
)
TRADE_INTENT_FIELDS: tuple[str, ...] = (
    "intent_id",
    "symbol",
    "trade_date",
    "side",
    "quantity",
)
REPLAY_CONFIG_FIELDS: tuple[str, ...] = (
    "request_id",
    "strategy_id",
    "strategy_version",
    "start_trade_date",
    "end_trade_date",
    "starting_capital",
    "transaction_cost_bps",
    "slippage_bps",
    "assumptions",
)
REPLAY_ASSUMPTION_FIELDS: tuple[str, ...] = (
    "calendar_source",
    "price_adjustment",
    "corporate_action_source",
    "fill_timing",
    "fill_price_field",
    "transaction_cost_model",
    "slippage_model",
    "missing_bar_policy",
    "non_trading_day_policy",
    "unusable_bar_policy",
    "position_marking_policy",
    "cash_carry_forward_policy",
    "data_ownership",
)
POSITION_SNAPSHOT_FIELDS: tuple[str, ...] = (
    "symbol",
    "quantity",
    "average_cost",
    "market_price",
    "market_value",
    "unrealized_pnl",
)
PORTFOLIO_SNAPSHOT_FIELDS: tuple[str, ...] = (
    "trade_date",
    "cash",
    "positions",
    "realized_pnl",
    "unrealized_pnl",
    "market_value",
    "total_equity",
)
REPLAY_SUMMARY_FIELDS: tuple[str, ...] = (
    "request_id",
    "strategy_id",
    "strategy_version",
    "start_trade_date",
    "end_trade_date",
    "starting_capital",
    "ending_cash",
    "ending_market_value",
    "ending_total_equity",
    "realized_pnl",
    "unrealized_pnl",
    "total_return",
    "max_drawdown",
    "executed_trade_count",
    "rejected_intent_count",
    "snapshot_count",
    "winning_trade_count",
    "losing_trade_count",
    "flat_trade_count",
    "win_rate",
    "loss_rate",
    "total_buy_notional",
    "total_sell_notional",
    "total_transaction_cost",
    "total_slippage_cost",
    "gross_turnover",
    "turnover_ratio",
    "average_net_exposure",
    "max_net_exposure",
    "ending_position_count",
    "coverage_calendar_day_count",
    "covered_market_bar_count",
    "missing_bar_day_count",
    "unusable_bar_day_count",
)
REJECTED_TRADE_INTENT_FIELDS: tuple[str, ...] = (
    "intent",
    "code",
    "message",
)
REPLAY_COVERAGE_FIELDS: tuple[str, ...] = (
    "requested_calendar_day_count",
    "snapshot_count",
    "market_bar_date_count",
    "covered_market_bar_count",
    "symbols",
    "missing_bar_dates",
    "unusable_bar_dates",
    "first_bar_trade_date",
    "last_bar_trade_date",
)
REPLAY_END_STATE_FIELDS: tuple[str, ...] = (
    "ending_cash",
    "ending_market_value",
    "ending_total_equity",
    "realized_pnl",
    "unrealized_pnl",
    "ending_position_count",
    "open_symbols",
)
REPLAY_REJECTION_BREAKDOWN_FIELDS: tuple[str, ...] = (
    "code",
    "count",
)
REPLAY_REPORT_FIELDS: tuple[str, ...] = (
    "request_id",
    "strategy_id",
    "strategy_version",
    "start_trade_date",
    "end_trade_date",
    "assumptions",
    "summary",
    "coverage",
    "end_state",
    "rejection_breakdown",
    "artifact_reference",
)


class SelectionReferenceKind(str, Enum):
    """Supported declarative backtest input reference kinds."""

    UNIVERSE = "universe"
    CANDIDATE_LIST = "candidate_list"


class ResultStatus(str, Enum):
    """Supported summary lifecycle states."""

    DECLARED = "declared"
    COMPLETED = "completed"
    FAILED = "failed"


class TradeSide(str, Enum):
    """Supported caller-supplied replay order sides."""

    BUY = "buy"
    SELL = "sell"


@dataclass(frozen=True)
class BacktestContractIssue:
    """Structured validation issue for deterministic backtest tests."""

    field: str
    code: str
    message: str


@dataclass(frozen=True)
class StrategyReference:
    """Stable identifier for one strategy contract version."""

    strategy_id: str
    strategy_version: str


@dataclass(frozen=True)
class SelectionReference:
    """Universe or candidate-list reference metadata without any reads."""

    reference_kind: SelectionReferenceKind
    reference_id: str
    reference_date: str | None = None
    market: str | None = None


@dataclass(frozen=True)
class BacktestRequest:
    """Declarative backtest request contract with no replay behavior."""

    request_id: str
    strategy_ref: StrategyReference
    selection_ref: SelectionReference
    start_trade_date: str
    end_trade_date: str
    starting_capital: float
    transaction_cost_bps: float = 0.0
    slippage_bps: float = 0.0
    schema_version: str = BACKTEST_CONTRACT_SCHEMA_VERSION


@dataclass(frozen=True)
class BacktestResultSummary:
    """Result summary metadata placeholder for future replay outputs."""

    summary_id: str
    request_id: str
    strategy_id: str
    strategy_version: str
    start_trade_date: str
    end_trade_date: str
    result_status: ResultStatus
    generated_at: datetime
    metric_keys: tuple[str, ...] = ()
    artifact_reference: str | None = None


@dataclass(frozen=True)
class MarketBar:
    """One caller-provided bar keyed by symbol and trade date."""

    symbol: str
    trade_date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float | None = None


@dataclass(frozen=True)
class TradeIntent:
    """One caller-provided dated trading intent for replay."""

    intent_id: str
    symbol: str
    trade_date: str
    side: TradeSide
    quantity: float


@dataclass(frozen=True)
class ReplayAssumptions:
    """Explicit replay semantics recorded in config and report outputs."""

    calendar_source: str = "caller_provided_window"
    price_adjustment: str = "as_provided"
    corporate_action_source: str = "caller_provided_prices"
    fill_timing: str = "same_day"
    fill_price_field: str = "close_price"
    transaction_cost_model: str = "bps_notional"
    slippage_model: str = "symmetric_bps"
    missing_bar_policy: str = "reject_intent_and_carry_forward"
    non_trading_day_policy: str = "calendar_day_snapshot_without_bar"
    unusable_bar_policy: str = "reject_intent_and_hold_last_usable_price"
    position_marking_policy: str = "latest_usable_close_on_or_before_date"
    cash_carry_forward_policy: str = "deterministic_daily_carry_forward"
    data_ownership: str = "caller_provided_bars_only"


@dataclass(frozen=True)
class ReplayConfig:
    """Replay configuration derived from a validated BacktestRequest."""

    request_id: str
    strategy_id: str
    strategy_version: str
    start_trade_date: str
    end_trade_date: str
    starting_capital: float
    transaction_cost_bps: float = 0.0
    slippage_bps: float = 0.0
    assumptions: ReplayAssumptions = field(default_factory=ReplayAssumptions)

    @classmethod
    def from_backtest_request(cls, request: BacktestRequest) -> "ReplayConfig":
        return cls(
            request_id=request.request_id,
            strategy_id=request.strategy_ref.strategy_id,
            strategy_version=request.strategy_ref.strategy_version,
            start_trade_date=request.start_trade_date,
            end_trade_date=request.end_trade_date,
            starting_capital=request.starting_capital,
            transaction_cost_bps=request.transaction_cost_bps,
            slippage_bps=request.slippage_bps,
        )


@dataclass(frozen=True)
class PositionSnapshot:
    """Per-symbol marked position state for one replay date."""

    symbol: str
    quantity: float
    average_cost: float
    market_price: float
    market_value: float
    unrealized_pnl: float


@dataclass(frozen=True)
class PortfolioSnapshot:
    """Per-date replay portfolio state and equity."""

    trade_date: str
    cash: float
    positions: tuple[PositionSnapshot, ...]
    realized_pnl: float
    unrealized_pnl: float
    market_value: float
    total_equity: float


@dataclass(frozen=True)
class ReplaySummary:
    """Final replay metrics for later reporting work."""

    request_id: str
    strategy_id: str
    strategy_version: str
    start_trade_date: str
    end_trade_date: str
    starting_capital: float
    ending_cash: float
    ending_market_value: float
    ending_total_equity: float
    realized_pnl: float
    unrealized_pnl: float
    total_return: float
    max_drawdown: float
    executed_trade_count: int
    rejected_intent_count: int
    snapshot_count: int
    winning_trade_count: int = 0
    losing_trade_count: int = 0
    flat_trade_count: int = 0
    win_rate: float = 0.0
    loss_rate: float = 0.0
    total_buy_notional: float = 0.0
    total_sell_notional: float = 0.0
    total_transaction_cost: float = 0.0
    total_slippage_cost: float = 0.0
    gross_turnover: float = 0.0
    turnover_ratio: float = 0.0
    average_net_exposure: float = 0.0
    max_net_exposure: float = 0.0
    ending_position_count: int = 0
    coverage_calendar_day_count: int = 0
    covered_market_bar_count: int = 0
    missing_bar_day_count: int = 0
    unusable_bar_day_count: int = 0


@dataclass(frozen=True)
class RejectedTradeIntent:
    """Rejected intent plus deterministic error metadata."""

    intent: TradeIntent
    code: str
    message: str


@dataclass(frozen=True)
class ReplayCoverage:
    """Window and bar-coverage facts for report-ready replay outputs."""

    requested_calendar_day_count: int
    snapshot_count: int
    market_bar_date_count: int
    covered_market_bar_count: int
    symbols: tuple[str, ...]
    missing_bar_dates: tuple[str, ...]
    unusable_bar_dates: tuple[str, ...]
    first_bar_trade_date: str | None = None
    last_bar_trade_date: str | None = None


@dataclass(frozen=True)
class ReplayEndState:
    """End-state facts for report-ready replay outputs."""

    ending_cash: float
    ending_market_value: float
    ending_total_equity: float
    realized_pnl: float
    unrealized_pnl: float
    ending_position_count: int
    open_symbols: tuple[str, ...]


@dataclass(frozen=True)
class ReplayRejectionBreakdown:
    """Grouped rejected-intent counts by deterministic rejection code."""

    code: str
    count: int


@dataclass(frozen=True)
class ReplayReport:
    """Serialization-friendly report payload for later comparison workflows."""

    request_id: str
    strategy_id: str
    strategy_version: str
    start_trade_date: str
    end_trade_date: str
    assumptions: ReplayAssumptions
    summary: ReplaySummary
    coverage: ReplayCoverage
    end_state: ReplayEndState
    rejection_breakdown: tuple[ReplayRejectionBreakdown, ...]
    artifact_reference: str | None = None

    def to_normalized_mapping(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReplayResult:
    """Structured replay output with no persistence side effects."""

    config: ReplayConfig
    snapshots: tuple[PortfolioSnapshot, ...]
    summary: ReplaySummary
    rejected_intents: tuple[RejectedTradeIntent, ...]
    report: ReplayReport | None = None


def validate_strategy_reference(
    payload: StrategyReference | Mapping[str, Any],
) -> tuple[BacktestContractIssue, ...]:
    """Return deterministic validation issues for one strategy reference."""
    record = _record_mapping(payload)
    issues: list[BacktestContractIssue] = []
    issues.extend(_validate_expected_fields(record, STRATEGY_REFERENCE_FIELDS))
    issues.extend(
        _validate_required_nonempty_texts(
            record,
            ("strategy_id", "strategy_version"),
        )
    )
    return tuple(issues)


def validate_selection_reference(
    payload: SelectionReference | Mapping[str, Any],
) -> tuple[BacktestContractIssue, ...]:
    """Return deterministic validation issues for universe/candidate references."""
    record = _record_mapping(payload)
    issues: list[BacktestContractIssue] = []
    issues.extend(_validate_expected_fields(record, SELECTION_REFERENCE_FIELDS))

    if "reference_kind" not in record or record["reference_kind"] is None:
        issues.append(_missing_required("reference_kind"))
    elif _coerce_selection_reference_kind(record["reference_kind"]) is None:
        issues.append(
            BacktestContractIssue(
                field="reference_kind",
                code="unsupported_reference_kind",
                message="reference_kind must be a supported SelectionReferenceKind value",
            )
        )

    issues.extend(_validate_required_nonempty_texts(record, ("reference_id",)))

    if "reference_date" in record and record["reference_date"] is not None:
        if not _is_iso_date_text(record["reference_date"]):
            issues.append(
                BacktestContractIssue(
                    field="reference_date",
                    code="invalid_date_string",
                    message="reference_date must be an ISO date string when provided",
                )
            )

    if "market" in record and record["market"] is not None and not _is_nonempty_text(record["market"]):
        issues.append(
            BacktestContractIssue(
                field="market",
                code="empty_text",
                message="market must be a non-empty string when provided",
            )
        )

    return tuple(issues)


def validate_backtest_request(
    payload: BacktestRequest | Mapping[str, Any],
) -> tuple[BacktestContractIssue, ...]:
    """Return deterministic validation issues for one backtest request."""
    record = _record_mapping(payload)
    issues: list[BacktestContractIssue] = []
    issues.extend(_validate_expected_fields(record, BACKTEST_REQUEST_FIELDS))

    if "request_id" not in record or record["request_id"] is None:
        issues.append(_missing_required("request_id"))
    elif not _is_nonempty_text(record["request_id"]):
        issues.append(
            BacktestContractIssue(
                field="request_id",
                code="empty_text",
                message="request_id must be a non-empty string",
            )
        )

    if "strategy_ref" not in record or record["strategy_ref"] is None:
        issues.append(_missing_required("strategy_ref"))
    else:
        nested_issues = validate_strategy_reference(record["strategy_ref"])
        if nested_issues:
            for issue in nested_issues:
                issues.append(_prefix_issue(issue, prefix="strategy_ref"))

    if "selection_ref" not in record or record["selection_ref"] is None:
        issues.append(_missing_required("selection_ref"))
    else:
        for issue in validate_selection_reference(record["selection_ref"]):
            issues.append(_prefix_issue(issue, prefix="selection_ref"))

    issues.extend(
        _validate_trade_date_range(
            record,
            start_field="start_trade_date",
            end_field="end_trade_date",
        )
    )

    if "starting_capital" not in record or record["starting_capital"] is None:
        issues.append(_missing_required("starting_capital"))
    elif not _is_positive_number(record["starting_capital"]):
        issues.append(
            BacktestContractIssue(
                field="starting_capital",
                code="invalid_value",
                message="starting_capital must be a positive finite number",
            )
        )

    for field_name in ("transaction_cost_bps", "slippage_bps"):
        if field_name not in record or record[field_name] is None:
            issues.append(_missing_required(field_name))
        elif not _is_non_negative_number(record[field_name]):
            issues.append(
                BacktestContractIssue(
                    field=field_name,
                    code="invalid_value",
                    message=f"{field_name} must be a non-negative finite number",
                )
            )

    if "schema_version" in record and record["schema_version"] != BACKTEST_CONTRACT_SCHEMA_VERSION:
        issues.append(
            BacktestContractIssue(
                field="schema_version",
                code="unsupported_schema_version",
                message="schema_version must match the BacktestEngine contract schema",
            )
        )

    return tuple(issues)


def validate_backtest_result_summary(
    payload: BacktestResultSummary | Mapping[str, Any],
) -> tuple[BacktestContractIssue, ...]:
    """Return deterministic validation issues for one summary placeholder."""
    record = _record_mapping(payload)
    issues: list[BacktestContractIssue] = []
    issues.extend(_validate_expected_fields(record, RESULT_SUMMARY_FIELDS))
    issues.extend(
        _validate_required_nonempty_texts(
            record,
            (
                "summary_id",
                "request_id",
                "strategy_id",
                "strategy_version",
            ),
        )
    )
    issues.extend(
        _validate_trade_date_range(
            record,
            start_field="start_trade_date",
            end_field="end_trade_date",
        )
    )

    if "result_status" not in record or record["result_status"] is None:
        issues.append(_missing_required("result_status"))
    elif _coerce_result_status(record["result_status"]) is None:
        issues.append(
            BacktestContractIssue(
                field="result_status",
                code="unsupported_result_status",
                message="result_status must be a supported ResultStatus value",
            )
        )

    if "generated_at" not in record or record["generated_at"] is None:
        issues.append(_missing_required("generated_at"))
    elif not isinstance(record["generated_at"], datetime):
        issues.append(
            BacktestContractIssue(
                field="generated_at",
                code="invalid_type",
                message="generated_at must be a datetime instance",
            )
        )

    if "metric_keys" not in record or record["metric_keys"] is None:
        issues.append(_missing_required("metric_keys"))
    else:
        issues.extend(
            _validate_text_sequence(
                record["metric_keys"],
                field_name="metric_keys",
                duplicate_code="duplicate_metric_key",
            )
        )

    if (
        "artifact_reference" in record
        and record["artifact_reference"] is not None
        and not _is_nonempty_text(record["artifact_reference"])
    ):
        issues.append(
            BacktestContractIssue(
                field="artifact_reference",
                code="empty_text",
                message="artifact_reference must be a non-empty string when provided",
            )
        )

    return tuple(issues)


def validate_market_bar(
    payload: MarketBar | Mapping[str, Any],
) -> tuple[BacktestContractIssue, ...]:
    """Return deterministic validation issues for one replay market bar."""
    record = _record_mapping(payload)
    issues: list[BacktestContractIssue] = []
    issues.extend(_validate_expected_fields(record, MARKET_BAR_FIELDS))
    issues.extend(_validate_required_nonempty_texts(record, ("symbol",)))

    if "trade_date" not in record or record["trade_date"] is None:
        issues.append(_missing_required("trade_date"))
    elif not _is_iso_date_text(record["trade_date"]):
        issues.append(
            BacktestContractIssue(
                field="trade_date",
                code="invalid_date_string",
                message="trade_date must be an ISO date string",
            )
        )

    for field_name in ("open_price", "high_price", "low_price", "close_price"):
        if field_name not in record or record[field_name] is None:
            issues.append(_missing_required(field_name))
        elif not _is_positive_number(record[field_name]):
            issues.append(
                BacktestContractIssue(
                    field=field_name,
                    code="invalid_value",
                    message=f"{field_name} must be a positive finite number",
                )
            )

    low_price = record.get("low_price")
    high_price = record.get("high_price")
    if _is_positive_number(low_price) and _is_positive_number(high_price) and low_price > high_price:
        issues.append(
            BacktestContractIssue(
                field="high_price",
                code="invalid_price_range",
                message="high_price must not be lower than low_price",
            )
        )

    if _is_positive_number(low_price) and _is_positive_number(high_price):
        for field_name in ("open_price", "close_price"):
            value = record.get(field_name)
            if _is_positive_number(value) and not (low_price <= value <= high_price):
                issues.append(
                    BacktestContractIssue(
                        field=field_name,
                        code="invalid_price_range",
                        message=f"{field_name} must be between low_price and high_price",
                    )
                )

    if "volume" in record and record["volume"] is not None and not _is_non_negative_number(record["volume"]):
        issues.append(
            BacktestContractIssue(
                field="volume",
                code="invalid_value",
                message="volume must be a non-negative finite number when provided",
            )
        )

    return tuple(issues)


def validate_trade_intent(
    payload: TradeIntent | Mapping[str, Any],
    *,
    config: ReplayConfig | Mapping[str, Any] | None = None,
) -> tuple[BacktestContractIssue, ...]:
    """Return deterministic validation issues for one replay trade intent."""
    record = _record_mapping(payload)
    issues: list[BacktestContractIssue] = []
    issues.extend(_validate_expected_fields(record, TRADE_INTENT_FIELDS))
    issues.extend(_validate_required_nonempty_texts(record, ("intent_id", "symbol")))

    if "trade_date" not in record or record["trade_date"] is None:
        issues.append(_missing_required("trade_date"))
    elif not _is_iso_date_text(record["trade_date"]):
        issues.append(
            BacktestContractIssue(
                field="trade_date",
                code="invalid_date_string",
                message="trade_date must be an ISO date string",
            )
        )

    if "side" not in record or record["side"] is None:
        issues.append(_missing_required("side"))
    elif _coerce_trade_side(record["side"]) is None:
        issues.append(
            BacktestContractIssue(
                field="side",
                code="unsupported_trade_side",
                message="side must be a supported TradeSide value",
            )
        )

    if "quantity" not in record or record["quantity"] is None:
        issues.append(_missing_required("quantity"))
    elif not _is_positive_number(record["quantity"]):
        issues.append(
            BacktestContractIssue(
                field="quantity",
                code="invalid_value",
                message="quantity must be a positive finite number",
            )
        )

    if config is not None:
        config_record = _record_mapping(config)
        trade_date_value = _coerce_iso_date(record.get("trade_date"))
        start_date = _coerce_iso_date(config_record.get("start_trade_date"))
        end_date = _coerce_iso_date(config_record.get("end_trade_date"))
        if trade_date_value is not None and start_date is not None and end_date is not None:
            if trade_date_value < start_date or trade_date_value > end_date:
                issues.append(
                    BacktestContractIssue(
                        field="trade_date",
                        code="outside_replay_window",
                        message="trade_date must fall within the configured replay date range",
                    )
                )

    return tuple(issues)


def validate_replay_config(
    payload: ReplayConfig | Mapping[str, Any],
) -> tuple[BacktestContractIssue, ...]:
    """Return deterministic validation issues for one replay configuration."""
    record = _record_mapping(payload)
    issues: list[BacktestContractIssue] = []
    issues.extend(_validate_expected_fields(record, REPLAY_CONFIG_FIELDS))
    issues.extend(
        _validate_required_nonempty_texts(
            record,
            ("request_id", "strategy_id", "strategy_version"),
        )
    )
    issues.extend(
        _validate_trade_date_range(
            record,
            start_field="start_trade_date",
            end_field="end_trade_date",
        )
    )

    if "starting_capital" not in record or record["starting_capital"] is None:
        issues.append(_missing_required("starting_capital"))
    elif not _is_positive_number(record["starting_capital"]):
        issues.append(
            BacktestContractIssue(
                field="starting_capital",
                code="invalid_value",
                message="starting_capital must be a positive finite number",
            )
        )

    for field_name in ("transaction_cost_bps", "slippage_bps"):
        if field_name not in record or record[field_name] is None:
            issues.append(_missing_required(field_name))
        elif not _is_non_negative_number(record[field_name]):
            issues.append(
                BacktestContractIssue(
                    field=field_name,
                    code="invalid_value",
                    message=f"{field_name} must be a non-negative finite number",
                )
            )

    if "assumptions" not in record or record["assumptions"] is None:
        issues.append(_missing_required("assumptions"))
    else:
        issues.extend(_prefix_issues(validate_replay_assumptions(record["assumptions"]), prefix="assumptions"))

    return tuple(issues)


def validate_replay_assumptions(
    payload: ReplayAssumptions | Mapping[str, Any],
) -> tuple[BacktestContractIssue, ...]:
    """Return deterministic validation issues for structured replay assumptions."""
    record = _record_mapping(payload)
    issues: list[BacktestContractIssue] = []
    issues.extend(_validate_expected_fields(record, REPLAY_ASSUMPTION_FIELDS))
    issues.extend(_validate_required_nonempty_texts(record, REPLAY_ASSUMPTION_FIELDS))

    issues.extend(
        _validate_choice_field(
            record,
            field_name="calendar_source",
            allowed_values=("caller_provided_window",),
        )
    )
    issues.extend(
        _validate_choice_field(
            record,
            field_name="price_adjustment",
            allowed_values=("adjusted", "unadjusted", "as_provided"),
        )
    )
    issues.extend(
        _validate_choice_field(
            record,
            field_name="corporate_action_source",
            allowed_values=("caller_provided_prices",),
        )
    )
    issues.extend(
        _validate_choice_field(
            record,
            field_name="fill_timing",
            allowed_values=("same_day",),
        )
    )
    issues.extend(
        _validate_choice_field(
            record,
            field_name="fill_price_field",
            allowed_values=("close_price",),
        )
    )
    issues.extend(
        _validate_choice_field(
            record,
            field_name="transaction_cost_model",
            allowed_values=("bps_notional",),
        )
    )
    issues.extend(
        _validate_choice_field(
            record,
            field_name="slippage_model",
            allowed_values=("symmetric_bps",),
        )
    )
    issues.extend(
        _validate_choice_field(
            record,
            field_name="missing_bar_policy",
            allowed_values=("reject_intent_and_carry_forward",),
        )
    )
    issues.extend(
        _validate_choice_field(
            record,
            field_name="non_trading_day_policy",
            allowed_values=("calendar_day_snapshot_without_bar",),
        )
    )
    issues.extend(
        _validate_choice_field(
            record,
            field_name="unusable_bar_policy",
            allowed_values=("reject_intent_and_hold_last_usable_price",),
        )
    )
    issues.extend(
        _validate_choice_field(
            record,
            field_name="position_marking_policy",
            allowed_values=("latest_usable_close_on_or_before_date",),
        )
    )
    issues.extend(
        _validate_choice_field(
            record,
            field_name="cash_carry_forward_policy",
            allowed_values=("deterministic_daily_carry_forward",),
        )
    )
    issues.extend(
        _validate_choice_field(
            record,
            field_name="data_ownership",
            allowed_values=("caller_provided_bars_only",),
        )
    )

    return tuple(issues)


def validate_position_snapshot(
    payload: PositionSnapshot | Mapping[str, Any],
) -> tuple[BacktestContractIssue, ...]:
    """Return deterministic validation issues for one marked position snapshot."""
    record = _record_mapping(payload)
    issues: list[BacktestContractIssue] = []
    issues.extend(_validate_expected_fields(record, POSITION_SNAPSHOT_FIELDS))
    issues.extend(_validate_required_nonempty_texts(record, ("symbol",)))

    for field_name in ("quantity", "average_cost", "market_price", "market_value"):
        if field_name not in record or record[field_name] is None:
            issues.append(_missing_required(field_name))
        elif not _is_positive_number(record[field_name]):
            issues.append(
                BacktestContractIssue(
                    field=field_name,
                    code="invalid_value",
                    message=f"{field_name} must be a positive finite number",
                )
            )

    if "unrealized_pnl" not in record or record["unrealized_pnl"] is None:
        issues.append(_missing_required("unrealized_pnl"))
    elif not _is_finite_number(record["unrealized_pnl"]):
        issues.append(
            BacktestContractIssue(
                field="unrealized_pnl",
                code="invalid_value",
                message="unrealized_pnl must be a finite number",
            )
        )

    return tuple(issues)


def validate_portfolio_snapshot(
    payload: PortfolioSnapshot | Mapping[str, Any],
) -> tuple[BacktestContractIssue, ...]:
    """Return deterministic validation issues for one per-date replay snapshot."""
    record = _record_mapping(payload)
    issues: list[BacktestContractIssue] = []
    issues.extend(_validate_expected_fields(record, PORTFOLIO_SNAPSHOT_FIELDS))

    if "trade_date" not in record or record["trade_date"] is None:
        issues.append(_missing_required("trade_date"))
    elif not _is_iso_date_text(record["trade_date"]):
        issues.append(
            BacktestContractIssue(
                field="trade_date",
                code="invalid_date_string",
                message="trade_date must be an ISO date string",
            )
        )

    for field_name in ("cash", "realized_pnl", "unrealized_pnl", "market_value", "total_equity"):
        if field_name not in record or record[field_name] is None:
            issues.append(_missing_required(field_name))
        elif not _is_finite_number(record[field_name]):
            issues.append(
                BacktestContractIssue(
                    field=field_name,
                    code="invalid_value",
                    message=f"{field_name} must be a finite number",
                )
            )

    if "positions" not in record or record["positions"] is None:
        issues.append(_missing_required("positions"))
    elif not isinstance(record["positions"], (list, tuple)):
        issues.append(
            BacktestContractIssue(
                field="positions",
                code="invalid_type",
                message="positions must be a sequence of PositionSnapshot records",
            )
        )
    else:
        seen_symbols: set[str] = set()
        for index, position in enumerate(record["positions"]):
            for issue in validate_position_snapshot(position):
                issues.append(_prefix_issue(issue, prefix=f"positions[{index}]"))
            position_record = _record_mapping(position)
            symbol = position_record.get("symbol")
            if _is_nonempty_text(symbol):
                symbol_key = symbol.strip()
                if symbol_key in seen_symbols:
                    issues.append(
                        BacktestContractIssue(
                            field=f"positions[{index}].symbol",
                            code="duplicate_symbol",
                            message="positions must not contain duplicate symbols",
                        )
                    )
                else:
                    seen_symbols.add(symbol_key)

    return tuple(issues)


def validate_replay_summary(
    payload: ReplaySummary | Mapping[str, Any],
) -> tuple[BacktestContractIssue, ...]:
    """Return deterministic validation issues for one final replay summary."""
    record = _record_mapping(payload)
    issues: list[BacktestContractIssue] = []
    issues.extend(_validate_expected_fields(record, REPLAY_SUMMARY_FIELDS))
    issues.extend(
        _validate_required_nonempty_texts(
            record,
            ("request_id", "strategy_id", "strategy_version"),
        )
    )
    issues.extend(
        _validate_trade_date_range(
            record,
            start_field="start_trade_date",
            end_field="end_trade_date",
        )
    )

    if "starting_capital" not in record or record["starting_capital"] is None:
        issues.append(_missing_required("starting_capital"))
    elif not _is_positive_number(record["starting_capital"]):
        issues.append(
            BacktestContractIssue(
                field="starting_capital",
                code="invalid_value",
                message="starting_capital must be a positive finite number",
            )
        )

    for field_name in (
        "ending_cash",
        "ending_market_value",
        "ending_total_equity",
        "realized_pnl",
        "unrealized_pnl",
        "total_return",
        "max_drawdown",
    ):
        if field_name not in record or record[field_name] is None:
            issues.append(_missing_required(field_name))
        elif not _is_finite_number(record[field_name]):
            issues.append(
                BacktestContractIssue(
                    field=field_name,
                    code="invalid_value",
                    message=f"{field_name} must be a finite number",
                )
            )

    max_drawdown = record.get("max_drawdown")
    if _is_finite_number(max_drawdown) and not 0.0 <= float(max_drawdown) <= 1.0:
        issues.append(
            BacktestContractIssue(
                field="max_drawdown",
                code="invalid_value",
                message="max_drawdown must be between 0.0 and 1.0",
            )
        )

    for field_name in ("executed_trade_count", "rejected_intent_count", "snapshot_count"):
        if field_name not in record or record[field_name] is None:
            issues.append(_missing_required(field_name))
        elif not _is_non_negative_integer(record[field_name]):
            issues.append(
                BacktestContractIssue(
                    field=field_name,
                    code="invalid_value",
                    message=f"{field_name} must be a non-negative integer",
                )
            )

    for field_name in (
        "winning_trade_count",
        "losing_trade_count",
        "flat_trade_count",
        "ending_position_count",
        "coverage_calendar_day_count",
        "covered_market_bar_count",
        "missing_bar_day_count",
        "unusable_bar_day_count",
    ):
        if field_name in record and record[field_name] is not None and not _is_non_negative_integer(record[field_name]):
            issues.append(
                BacktestContractIssue(
                    field=field_name,
                    code="invalid_value",
                    message=f"{field_name} must be a non-negative integer when provided",
                )
            )

    for field_name in (
        "win_rate",
        "loss_rate",
        "total_buy_notional",
        "total_sell_notional",
        "total_transaction_cost",
        "total_slippage_cost",
        "gross_turnover",
        "turnover_ratio",
        "average_net_exposure",
        "max_net_exposure",
    ):
        if field_name in record and record[field_name] is not None and not _is_finite_number(record[field_name]):
            issues.append(
                BacktestContractIssue(
                    field=field_name,
                    code="invalid_value",
                    message=f"{field_name} must be a finite number when provided",
                )
            )

    for field_name in ("win_rate", "loss_rate", "turnover_ratio", "average_net_exposure", "max_net_exposure"):
        value = record.get(field_name)
        if _is_finite_number(value) and not 0.0 <= float(value) <= 1.0:
            issues.append(
                BacktestContractIssue(
                    field=field_name,
                    code="invalid_value",
                    message=f"{field_name} must be between 0.0 and 1.0 when provided",
                )
            )

    return tuple(issues)


def validate_rejected_trade_intent(
    payload: RejectedTradeIntent | Mapping[str, Any],
) -> tuple[BacktestContractIssue, ...]:
    """Return deterministic validation issues for one rejected replay intent."""
    record = _record_mapping(payload)
    issues: list[BacktestContractIssue] = []
    issues.extend(_validate_expected_fields(record, REJECTED_TRADE_INTENT_FIELDS))

    if "intent" not in record or record["intent"] is None:
        issues.append(_missing_required("intent"))
    else:
        for issue in validate_trade_intent(record["intent"]):
            issues.append(_prefix_issue(issue, prefix="intent"))

    issues.extend(_validate_required_nonempty_texts(record, ("code", "message")))
    return tuple(issues)


def validate_replay_report(
    payload: ReplayReport | Mapping[str, Any],
) -> tuple[BacktestContractIssue, ...]:
    """Return deterministic validation issues for one report-ready replay payload."""
    record = _record_mapping(payload)
    issues: list[BacktestContractIssue] = []
    issues.extend(_validate_expected_fields(record, REPLAY_REPORT_FIELDS))
    issues.extend(
        _validate_required_nonempty_texts(
            record,
            ("request_id", "strategy_id", "strategy_version"),
        )
    )
    issues.extend(
        _validate_trade_date_range(
            record,
            start_field="start_trade_date",
            end_field="end_trade_date",
        )
    )

    if "assumptions" not in record or record["assumptions"] is None:
        issues.append(_missing_required("assumptions"))
    else:
        issues.extend(_prefix_issues(validate_replay_assumptions(record["assumptions"]), prefix="assumptions"))

    if "summary" not in record or record["summary"] is None:
        issues.append(_missing_required("summary"))
    else:
        issues.extend(_prefix_issues(validate_replay_summary(record["summary"]), prefix="summary"))

    coverage = record.get("coverage")
    if coverage is None:
        issues.append(_missing_required("coverage"))
    else:
        issues.extend(_prefix_issues(_validate_replay_coverage(coverage), prefix="coverage"))

    end_state = record.get("end_state")
    if end_state is None:
        issues.append(_missing_required("end_state"))
    else:
        issues.extend(_prefix_issues(_validate_replay_end_state(end_state), prefix="end_state"))

    if "rejection_breakdown" not in record or record["rejection_breakdown"] is None:
        issues.append(_missing_required("rejection_breakdown"))
    elif not isinstance(record["rejection_breakdown"], (list, tuple)):
        issues.append(
            BacktestContractIssue(
                field="rejection_breakdown",
                code="invalid_type",
                message="rejection_breakdown must be a sequence of replay rejection summary records",
            )
        )
    else:
        for index, item in enumerate(record["rejection_breakdown"]):
            issues.extend(
                _prefix_issues(
                    _validate_replay_rejection_breakdown(item),
                    prefix=f"rejection_breakdown[{index}]",
                )
            )

    if (
        "artifact_reference" in record
        and record["artifact_reference"] is not None
        and not _is_nonempty_text(record["artifact_reference"])
    ):
        issues.append(
            BacktestContractIssue(
                field="artifact_reference",
                code="empty_text",
                message="artifact_reference must be a non-empty string when provided",
            )
        )

    return tuple(issues)


def _validate_replay_coverage(
    payload: ReplayCoverage | Mapping[str, Any],
) -> tuple[BacktestContractIssue, ...]:
    record = _record_mapping(payload)
    issues: list[BacktestContractIssue] = []
    issues.extend(_validate_expected_fields(record, REPLAY_COVERAGE_FIELDS))

    for field_name in (
        "requested_calendar_day_count",
        "snapshot_count",
        "market_bar_date_count",
        "covered_market_bar_count",
    ):
        if field_name not in record or record[field_name] is None:
            issues.append(_missing_required(field_name))
        elif not _is_non_negative_integer(record[field_name]):
            issues.append(
                BacktestContractIssue(
                    field=field_name,
                    code="invalid_value",
                    message=f"{field_name} must be a non-negative integer",
                )
            )

    if "symbols" not in record or record["symbols"] is None:
        issues.append(_missing_required("symbols"))
    else:
        issues.extend(_validate_text_sequence(record["symbols"], field_name="symbols", duplicate_code="duplicate_symbol"))

    for field_name in ("missing_bar_dates", "unusable_bar_dates"):
        if field_name not in record or record[field_name] is None:
            issues.append(_missing_required(field_name))
        elif not isinstance(record[field_name], (list, tuple)):
            issues.append(
                BacktestContractIssue(
                    field=field_name,
                    code="invalid_type",
                    message=f"{field_name} must be a sequence of ISO date strings",
                )
            )
        else:
            for value in record[field_name]:
                if not _is_iso_date_text(value):
                    issues.append(
                        BacktestContractIssue(
                            field=field_name,
                            code="invalid_date_string",
                            message=f"{field_name} must contain only ISO date strings",
                        )
                    )
                    break

    for field_name in ("first_bar_trade_date", "last_bar_trade_date"):
        if field_name in record and record[field_name] is not None and not _is_iso_date_text(record[field_name]):
            issues.append(
                BacktestContractIssue(
                    field=field_name,
                    code="invalid_date_string",
                    message=f"{field_name} must be an ISO date string when provided",
                )
            )

    return tuple(issues)


def _validate_replay_end_state(
    payload: ReplayEndState | Mapping[str, Any],
) -> tuple[BacktestContractIssue, ...]:
    record = _record_mapping(payload)
    issues: list[BacktestContractIssue] = []
    issues.extend(_validate_expected_fields(record, REPLAY_END_STATE_FIELDS))

    for field_name in (
        "ending_cash",
        "ending_market_value",
        "ending_total_equity",
        "realized_pnl",
        "unrealized_pnl",
    ):
        if field_name not in record or record[field_name] is None:
            issues.append(_missing_required(field_name))
        elif not _is_finite_number(record[field_name]):
            issues.append(
                BacktestContractIssue(
                    field=field_name,
                    code="invalid_value",
                    message=f"{field_name} must be a finite number",
                )
            )

    if "ending_position_count" not in record or record["ending_position_count"] is None:
        issues.append(_missing_required("ending_position_count"))
    elif not _is_non_negative_integer(record["ending_position_count"]):
        issues.append(
            BacktestContractIssue(
                field="ending_position_count",
                code="invalid_value",
                message="ending_position_count must be a non-negative integer",
            )
        )

    if "open_symbols" not in record or record["open_symbols"] is None:
        issues.append(_missing_required("open_symbols"))
    else:
        issues.extend(
            _validate_text_sequence(
                record["open_symbols"],
                field_name="open_symbols",
                duplicate_code="duplicate_symbol",
            )
        )

    return tuple(issues)


def _validate_replay_rejection_breakdown(
    payload: ReplayRejectionBreakdown | Mapping[str, Any],
) -> tuple[BacktestContractIssue, ...]:
    record = _record_mapping(payload)
    issues: list[BacktestContractIssue] = []
    issues.extend(_validate_expected_fields(record, REPLAY_REJECTION_BREAKDOWN_FIELDS))
    issues.extend(_validate_required_nonempty_texts(record, ("code",)))
    if "count" not in record or record["count"] is None:
        issues.append(_missing_required("count"))
    elif not _is_non_negative_integer(record["count"]):
        issues.append(
            BacktestContractIssue(
                field="count",
                code="invalid_value",
                message="count must be a non-negative integer",
            )
        )
    return tuple(issues)


def _validate_trade_date_range(
    record: Mapping[str, Any],
    *,
    start_field: str,
    end_field: str,
) -> list[BacktestContractIssue]:
    issues: list[BacktestContractIssue] = []
    start_date = _coerce_iso_date(record.get(start_field))
    end_date = _coerce_iso_date(record.get(end_field))

    if start_field not in record or record[start_field] is None:
        issues.append(_missing_required(start_field))
    elif start_date is None:
        issues.append(
            BacktestContractIssue(
                field=start_field,
                code="invalid_date_string",
                message=f"{start_field} must be an ISO date string",
            )
        )

    if end_field not in record or record[end_field] is None:
        issues.append(_missing_required(end_field))
    elif end_date is None:
        issues.append(
            BacktestContractIssue(
                field=end_field,
                code="invalid_date_string",
                message=f"{end_field} must be an ISO date string",
            )
        )

    if start_date is not None and end_date is not None and start_date > end_date:
        issues.append(
            BacktestContractIssue(
                field=end_field,
                code="invalid_date_order",
                message=f"{end_field} must not be earlier than {start_field}",
            )
        )
    return issues


def _validate_text_sequence(
    payload: Any,
    *,
    field_name: str,
    duplicate_code: str,
) -> list[BacktestContractIssue]:
    if not isinstance(payload, (list, tuple)) or isinstance(payload, str):
        return [
            BacktestContractIssue(
                field=field_name,
                code="invalid_type",
                message=f"{field_name} must be a sequence of non-empty strings",
            )
        ]

    issues: list[BacktestContractIssue] = []
    seen_values: set[str] = set()
    for value in payload:
        if not _is_nonempty_text(value):
            issues.append(
                BacktestContractIssue(
                    field=field_name,
                    code="invalid_value",
                    message=f"{field_name} must contain only non-empty strings",
                )
            )
            continue
        normalized_value = value.strip()
        if normalized_value in seen_values:
            issues.append(
                BacktestContractIssue(
                    field=field_name,
                    code=duplicate_code,
                    message=f"{field_name} must not contain duplicates",
                )
            )
        else:
            seen_values.add(normalized_value)
    return issues


def _validate_required_nonempty_texts(
    record: Mapping[str, Any],
    fields: tuple[str, ...],
) -> list[BacktestContractIssue]:
    issues: list[BacktestContractIssue] = []
    for field_name in fields:
        if field_name not in record or record[field_name] is None:
            issues.append(_missing_required(field_name))
        elif not _is_nonempty_text(record[field_name]):
            issues.append(
                BacktestContractIssue(
                    field=field_name,
                    code="empty_text",
                    message=f"{field_name} must be a non-empty string",
                )
            )
    return issues


def _validate_choice_field(
    record: Mapping[str, Any],
    *,
    field_name: str,
    allowed_values: tuple[str, ...],
) -> list[BacktestContractIssue]:
    value = record.get(field_name)
    if value is None or not _is_nonempty_text(value) or value in allowed_values:
        return []
    return [
        BacktestContractIssue(
            field=field_name,
            code="unsupported_value",
            message=f"{field_name} must be one of {allowed_values!r}",
        )
    ]


def _validate_expected_fields(
    record: Mapping[str, Any],
    allowed_fields: tuple[str, ...],
) -> list[BacktestContractIssue]:
    allowed = set(allowed_fields)
    return [
        BacktestContractIssue(
            field=field_name,
            code="unexpected_field",
            message=f"{field_name} is not part of this contract",
        )
        for field_name in record
        if field_name not in allowed
    ]


def _coerce_selection_reference_kind(value: Any) -> SelectionReferenceKind | None:
    if isinstance(value, SelectionReferenceKind):
        return value
    if isinstance(value, str):
        try:
            return SelectionReferenceKind(value)
        except ValueError:
            return None
    return None


def _coerce_result_status(value: Any) -> ResultStatus | None:
    if isinstance(value, ResultStatus):
        return value
    if isinstance(value, str):
        try:
            return ResultStatus(value)
        except ValueError:
            return None
    return None


def _coerce_trade_side(value: Any) -> TradeSide | None:
    if isinstance(value, TradeSide):
        return value
    if isinstance(value, str):
        try:
            return TradeSide(value)
        except ValueError:
            return None
    return None


def _coerce_iso_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _is_iso_date_text(value: Any) -> bool:
    return _coerce_iso_date(value) is not None


def _is_positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value) and value > 0


def _is_non_negative_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value) and value >= 0


def _is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)


def _is_non_negative_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _is_nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _missing_required(field_name: str) -> BacktestContractIssue:
    return BacktestContractIssue(
        field=field_name,
        code="missing_required",
        message=f"{field_name} is required",
    )


def _prefix_issue(issue: BacktestContractIssue, *, prefix: str) -> BacktestContractIssue:
    return BacktestContractIssue(
        field=f"{prefix}.{issue.field}",
        code=issue.code,
        message=issue.message,
    )


def _record_mapping(payload: Any) -> Mapping[str, Any]:
    if isinstance(payload, Mapping):
        return payload
    if is_dataclass(payload):
        return asdict(payload)
    return {}


def coerce_replay_config(payload: ReplayConfig | BacktestRequest) -> ReplayConfig:
    """Normalize replay entry-point config inputs."""
    if isinstance(payload, ReplayConfig):
        return payload
    if isinstance(payload, BacktestRequest):
        return ReplayConfig.from_backtest_request(payload)
    raise TypeError("payload must be ReplayConfig or BacktestRequest")


def ensure_valid_contracts(
    config: ReplayConfig,
    market_bars: Sequence[MarketBar],
    trade_intents: Sequence[TradeIntent],
) -> None:
    """Raise ValueError when replay contracts contain deterministic validation errors."""
    issues: list[BacktestContractIssue] = []
    issues.extend(validate_replay_config(config))

    seen_bar_keys: set[tuple[str, str]] = set()
    for index, market_bar in enumerate(market_bars):
        issues.extend(_prefix_issues(validate_market_bar(market_bar), prefix=f"market_bars[{index}]"))
        key = (market_bar.symbol.strip(), market_bar.trade_date)
        if key in seen_bar_keys:
            issues.append(
                BacktestContractIssue(
                    field=f"market_bars[{index}]",
                    code="duplicate_symbol_trade_date",
                    message="market bars must not contain duplicate symbol/trade_date keys",
                )
            )
        else:
            seen_bar_keys.add(key)

    for index, trade_intent in enumerate(trade_intents):
        issues.extend(
            _prefix_issues(
                validate_trade_intent(trade_intent, config=config),
                prefix=f"trade_intents[{index}]",
            )
        )

    if issues:
        raise ValueError(_format_contract_issues(issues))


def _prefix_issues(
    issues: Sequence[BacktestContractIssue],
    *,
    prefix: str,
) -> list[BacktestContractIssue]:
    return [_prefix_issue(issue, prefix=prefix) for issue in issues]


def _format_contract_issues(issues: Sequence[BacktestContractIssue]) -> str:
    return "; ".join(f"{issue.field}:{issue.code}" for issue in issues)
