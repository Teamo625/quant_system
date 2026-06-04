"""BacktestEngine foundation contracts for offline request declarations."""

from .contracts import (
    BACKTEST_CONTRACT_SCHEMA_VERSION,
    BACKTEST_REQUEST_FIELDS,
    RESULT_SUMMARY_FIELDS,
    SELECTION_REFERENCE_FIELDS,
    STRATEGY_REFERENCE_FIELDS,
    BacktestContractIssue,
    BacktestRequest,
    BacktestResultSummary,
    ResultStatus,
    SelectionReference,
    SelectionReferenceKind,
    StrategyReference,
    validate_backtest_request,
    validate_backtest_result_summary,
    validate_selection_reference,
    validate_strategy_reference,
)

__all__ = [
    "BACKTEST_CONTRACT_SCHEMA_VERSION",
    "BACKTEST_REQUEST_FIELDS",
    "RESULT_SUMMARY_FIELDS",
    "SELECTION_REFERENCE_FIELDS",
    "STRATEGY_REFERENCE_FIELDS",
    "BacktestContractIssue",
    "BacktestRequest",
    "BacktestResultSummary",
    "ResultStatus",
    "SelectionReference",
    "SelectionReferenceKind",
    "StrategyReference",
    "validate_backtest_request",
    "validate_backtest_result_summary",
    "validate_selection_reference",
    "validate_strategy_reference",
]
