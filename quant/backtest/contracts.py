"""Offline-safe BacktestEngine contracts and replay primitives."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
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
)
REJECTED_TRADE_INTENT_FIELDS: tuple[str, ...] = (
    "intent",
    "code",
    "message",
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


@dataclass(frozen=True)
class RejectedTradeIntent:
    """Rejected intent plus deterministic error metadata."""

    intent: TradeIntent
    code: str
    message: str


@dataclass(frozen=True)
class ReplayResult:
    """Structured replay output with no persistence side effects."""

    config: ReplayConfig
    snapshots: tuple[PortfolioSnapshot, ...]
    summary: ReplaySummary
    rejected_intents: tuple[RejectedTradeIntent, ...]


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
