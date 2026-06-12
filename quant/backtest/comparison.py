"""Deterministic offline comparison workflows for multiple backtest configurations."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from hashlib import sha256
import json
from math import isfinite
from typing import Any, Mapping, Sequence

from .contracts import ReplayReport, validate_replay_report
from .experiments import (
    RepeatableExperimentConfig,
    normalize_repeatable_experiment_config,
    validate_repeatable_experiment_config,
)


COMPARISON_INPUT_FIELDS: tuple[str, ...] = (
    "experiment_config",
    "replay_result",
    "replay_report",
)
COMPARISON_RANKING_POLICY: tuple[str, ...] = (
    "total_return_desc",
    "max_drawdown_asc",
    "win_rate_desc",
    "ending_total_equity_desc",
    "configuration_id_asc",
)
COMPARISON_REQUIRED_METRICS: tuple[str, ...] = (
    "total_return",
    "max_drawdown",
    "ending_total_equity",
    "win_rate",
    "turnover_ratio",
    "executed_trade_count",
    "rejected_intent_count",
)
COMPARISON_DELTA_METRICS: tuple[str, ...] = (
    "total_return",
    "max_drawdown",
    "ending_total_equity",
    "win_rate",
    "turnover_ratio",
)
COMPARISON_ASSUMPTION_FIELDS: tuple[str, ...] = (
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


class ComparisonWorkflowError(ValueError):
    """Controlled error raised for invalid multi-configuration comparisons."""

    def __init__(self, issues: tuple["ComparisonIssue", ...]) -> None:
        message = "; ".join(
            f"{issue.field}:{issue.code}" for issue in issues
        ) or "invalid multi-configuration comparison"
        super().__init__(message)
        self.issues = issues


@dataclass(frozen=True)
class ComparisonIssue:
    """Structured validation issue for deterministic comparison tests."""

    field: str
    code: str
    message: str


@dataclass(frozen=True)
class ComparisonInput:
    """One local comparison input with no external artifact reads."""

    experiment_config: RepeatableExperimentConfig | Mapping[str, Any] | None = None
    replay_result: Any | None = None
    replay_report: ReplayReport | Mapping[str, Any] | None = None


@dataclass(frozen=True)
class ComparisonAssumptionDifference:
    """One assumption field that differs across compared configurations."""

    field: str
    values_by_configuration: dict[str, str]


@dataclass(frozen=True)
class ComparisonRow:
    """One deterministic comparison row derived from an existing replay/report."""

    rank: int
    configuration_id: str
    request_id: str
    strategy_id: str
    strategy_version: str
    parameter_set_version: str | None
    parameter_set_id: str | None
    start_trade_date: str
    end_trade_date: str
    starting_capital: float
    rank_key: dict[str, str | float]
    metrics: dict[str, float | int]
    metric_deltas_vs_leader: dict[str, float]
    assumptions: dict[str, str]
    coverage: dict[str, int | str | None]
    artifact_reference: str | None


@dataclass(frozen=True)
class MultiConfigurationComparison:
    """Serialization-friendly deterministic comparison summary."""

    comparison_id: str
    start_trade_date: str
    end_trade_date: str
    starting_capital: float
    ranking_policy: tuple[str, ...]
    leader_configuration_id: str
    configuration_ids: tuple[str, ...]
    rows: tuple[ComparisonRow, ...]
    assumption_differences: tuple[ComparisonAssumptionDifference, ...]

    def to_normalized_mapping(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class _ResolvedComparisonEntry:
    configuration_id: str
    experiment_config: dict[str, Any] | None
    replay_report: dict[str, Any]
    parameter_set_version: str | None
    parameter_set_id: str | None


def validate_multi_configuration_comparison_inputs(
    entries: Sequence[ComparisonInput | Mapping[str, Any]],
) -> tuple[ComparisonIssue, ...]:
    """Return deterministic validation issues for a comparison build request."""
    _, issues = _resolve_comparison_entries(entries)
    return issues


def build_multi_configuration_comparison(
    entries: Sequence[ComparisonInput | Mapping[str, Any]],
) -> MultiConfigurationComparison:
    """Build a deterministic offline comparison over multiple local replay outputs.

    Ranking is stable and documented:
    1. higher total_return
    2. lower max_drawdown
    3. higher win_rate
    4. higher ending_total_equity
    5. lexicographically smaller configuration_id
    """

    resolved_entries, issues = _resolve_comparison_entries(entries)
    if issues:
        raise ComparisonWorkflowError(issues)

    ranked_entries = tuple(sorted(resolved_entries, key=_comparison_sort_key))
    leader_report = ranked_entries[0].replay_report
    leader_summary = _mapping(leader_report["summary"])
    rows = tuple(
        _build_comparison_row(
            entry=entry,
            leader_summary=leader_summary,
            rank=index + 1,
        )
        for index, entry in enumerate(ranked_entries)
    )
    comparison_id = _build_comparison_id(resolved_entries)

    return MultiConfigurationComparison(
        comparison_id=comparison_id,
        start_trade_date=ranked_entries[0].replay_report["start_trade_date"],
        end_trade_date=ranked_entries[0].replay_report["end_trade_date"],
        starting_capital=float(leader_summary["starting_capital"]),
        ranking_policy=COMPARISON_RANKING_POLICY,
        leader_configuration_id=rows[0].configuration_id,
        configuration_ids=tuple(row.configuration_id for row in rows),
        rows=rows,
        assumption_differences=_build_assumption_differences(ranked_entries),
    )


def _resolve_comparison_entries(
    entries: Sequence[ComparisonInput | Mapping[str, Any]],
) -> tuple[tuple[_ResolvedComparisonEntry, ...], tuple[ComparisonIssue, ...]]:
    issues: list[ComparisonIssue] = []
    if not isinstance(entries, (list, tuple)) or isinstance(entries, str):
        return (), (
            ComparisonIssue(
                field="entries",
                code="invalid_type",
                message="entries must be a sequence of comparison inputs",
            ),
        )
    if not entries:
        return (), (
            ComparisonIssue(
                field="entries",
                code="empty_entries",
                message="at least two comparison entries are required",
            ),
        )
    if len(entries) == 1:
        return (), (
            ComparisonIssue(
                field="entries",
                code="single_entry",
                message="at least two comparison entries are required",
            ),
        )

    resolved_entries: list[_ResolvedComparisonEntry] = []
    seen_configuration_ids: dict[str, int] = {}
    baseline_window: tuple[str, str] | None = None
    baseline_capital: float | None = None

    for index, entry in enumerate(entries):
        entry_prefix = f"entries[{index}]"
        resolved_entry, entry_issues = _resolve_single_entry(entry, index=index)
        issues.extend(entry_issues)
        if resolved_entry is None:
            continue

        if resolved_entry.configuration_id in seen_configuration_ids:
            first_index = seen_configuration_ids[resolved_entry.configuration_id]
            issues.append(
                ComparisonIssue(
                    field=f"{entry_prefix}.configuration_id",
                    code="duplicate_configuration_id",
                    message=(
                        "configuration_id must be unique across entries; "
                        f"already seen at entries[{first_index}]"
                    ),
                )
            )
        else:
            seen_configuration_ids[resolved_entry.configuration_id] = index

        report = resolved_entry.replay_report
        summary = _mapping(report["summary"])
        window = (
            str(report["start_trade_date"]),
            str(report["end_trade_date"]),
        )
        starting_capital = float(summary["starting_capital"])
        if baseline_window is None:
            baseline_window = window
        elif window != baseline_window:
            issues.append(
                ComparisonIssue(
                    field=f"{entry_prefix}.replay_report",
                    code="comparison_window_mismatch",
                    message="all comparison entries must share the same start/end trade window",
                )
            )
        if baseline_capital is None:
            baseline_capital = starting_capital
        elif not _numbers_equal(starting_capital, baseline_capital):
            issues.append(
                ComparisonIssue(
                    field=f"{entry_prefix}.replay_report.summary.starting_capital",
                    code="starting_capital_mismatch",
                    message="all comparison entries must share the same starting_capital",
                )
            )

        resolved_entries.append(resolved_entry)

    return tuple(resolved_entries), tuple(issues)


def _resolve_single_entry(
    entry: ComparisonInput | Mapping[str, Any],
    *,
    index: int,
) -> tuple[_ResolvedComparisonEntry | None, tuple[ComparisonIssue, ...]]:
    issues: list[ComparisonIssue] = []
    entry_prefix = f"entries[{index}]"
    record = _mapping(entry)
    issues.extend(
        _validate_expected_fields(
            record,
            COMPARISON_INPUT_FIELDS,
            prefix=entry_prefix,
        )
    )

    experiment_config_payload = record.get("experiment_config")
    experiment_config: dict[str, Any] | None = None
    parameter_set_version: str | None = None
    parameter_set_id: str | None = None

    if experiment_config_payload is not None:
        experiment_issues = validate_repeatable_experiment_config(experiment_config_payload)
        issues.extend(
            ComparisonIssue(
                field=f"{entry_prefix}.experiment_config.{issue.field}",
                code=issue.code,
                message=issue.message,
            )
            for issue in experiment_issues
        )
        if not experiment_issues:
            experiment_config = normalize_repeatable_experiment_config(
                experiment_config_payload
            )
            experiment_config["experiment_id"] = _mapping(experiment_config_payload).get(
                "experiment_id"
            )
            parameter_set_version = experiment_config.get("parameter_set_version")
            parameter_set_id = experiment_config.get("parameter_set_id")

    replay_report_payload = record.get("replay_report")
    if replay_report_payload is None:
        replay_report_payload = _extract_report_from_replay_result(record.get("replay_result"))
        if record.get("replay_result") is not None and replay_report_payload is None:
            issues.append(
                ComparisonIssue(
                    field=f"{entry_prefix}.replay_result",
                    code="missing_replay_report",
                    message="replay_result must include a replay_report for comparison",
                )
            )

    if replay_report_payload is None:
        issues.append(
            ComparisonIssue(
                field=f"{entry_prefix}.replay_report",
                code="missing_replay_payload",
                message="each comparison entry must provide replay_report or replay_result",
            )
        )
        return None, tuple(issues)

    replay_issues = validate_replay_report(replay_report_payload)
    issues.extend(
        ComparisonIssue(
            field=f"{entry_prefix}.replay_report.{issue.field}",
            code=issue.code,
            message=issue.message,
        )
        for issue in replay_issues
    )
    if replay_issues:
        return None, tuple(issues)

    replay_report = _mapping(replay_report_payload)
    summary = _mapping(replay_report["summary"])

    issues.extend(_validate_report_consistency(replay_report, prefix=f"{entry_prefix}.replay_report"))
    issues.extend(
        _validate_required_metrics(
            summary,
            prefix=f"{entry_prefix}.replay_report.summary",
        )
    )
    if issues:
        return None, tuple(issues)

    if experiment_config is not None:
        _validate_experiment_and_report_alignment(
            experiment_config=experiment_config,
            replay_report=replay_report,
            issues=issues,
            prefix=entry_prefix,
        )
        if issues:
            return None, tuple(issues)
        configuration_id = str(experiment_config["experiment_id"])
    else:
        configuration_id = str(replay_report["request_id"])

    return (
        _ResolvedComparisonEntry(
            configuration_id=configuration_id,
            experiment_config=experiment_config,
            replay_report=replay_report,
            parameter_set_version=parameter_set_version,
            parameter_set_id=parameter_set_id,
        ),
        tuple(issues),
    )


def _validate_report_consistency(
    replay_report: Mapping[str, Any],
    *,
    prefix: str,
) -> list[ComparisonIssue]:
    issues: list[ComparisonIssue] = []
    summary = _mapping(replay_report.get("summary"))
    expected_pairs = (
        ("request_id", replay_report.get("request_id"), summary.get("request_id")),
        ("strategy_id", replay_report.get("strategy_id"), summary.get("strategy_id")),
        (
            "strategy_version",
            replay_report.get("strategy_version"),
            summary.get("strategy_version"),
        ),
        (
            "start_trade_date",
            replay_report.get("start_trade_date"),
            summary.get("start_trade_date"),
        ),
        ("end_trade_date", replay_report.get("end_trade_date"), summary.get("end_trade_date")),
    )
    for field_name, top_level_value, summary_value in expected_pairs:
        if top_level_value != summary_value:
            issues.append(
                ComparisonIssue(
                    field=f"{prefix}.summary.{field_name}",
                    code="summary_mismatch",
                    message=f"summary.{field_name} must match replay_report.{field_name}",
                )
            )
    return issues


def _validate_required_metrics(
    summary: Mapping[str, Any],
    *,
    prefix: str,
) -> list[ComparisonIssue]:
    issues: list[ComparisonIssue] = []
    for metric_name in COMPARISON_REQUIRED_METRICS:
        if metric_name not in summary or summary[metric_name] is None:
            issues.append(
                ComparisonIssue(
                    field=f"{prefix}.{metric_name}",
                    code="missing_metric",
                    message=f"{metric_name} is required for deterministic comparison",
                )
            )
            continue
        value = summary[metric_name]
        if metric_name.endswith("_count"):
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                issues.append(
                    ComparisonIssue(
                        field=f"{prefix}.{metric_name}",
                        code="invalid_metric_value",
                        message=f"{metric_name} must be a non-negative integer",
                    )
                )
        elif not _is_finite_number(value):
            issues.append(
                ComparisonIssue(
                    field=f"{prefix}.{metric_name}",
                    code="invalid_metric_value",
                    message=f"{metric_name} must be a finite number",
                )
            )
    return issues


def _validate_experiment_and_report_alignment(
    *,
    experiment_config: Mapping[str, Any],
    replay_report: Mapping[str, Any],
    issues: list[ComparisonIssue],
    prefix: str,
) -> None:
    summary = _mapping(replay_report["summary"])
    strategy_ref = _mapping(experiment_config["strategy_ref"])
    expected_pairs = (
        (
            "request_id",
            experiment_config.get("experiment_id"),
            replay_report.get("request_id"),
            "request_id_mismatch",
        ),
        (
            "strategy_id",
            strategy_ref.get("strategy_id"),
            replay_report.get("strategy_id"),
            "strategy_id_mismatch",
        ),
        (
            "strategy_version",
            strategy_ref.get("strategy_version"),
            replay_report.get("strategy_version"),
            "strategy_version_mismatch",
        ),
        (
            "start_trade_date",
            experiment_config.get("start_trade_date"),
            replay_report.get("start_trade_date"),
            "window_mismatch",
        ),
        (
            "end_trade_date",
            experiment_config.get("end_trade_date"),
            replay_report.get("end_trade_date"),
            "window_mismatch",
        ),
    )
    for field_name, config_value, report_value, code in expected_pairs:
        if config_value != report_value:
            issues.append(
                ComparisonIssue(
                    field=f"{prefix}.replay_report.{field_name}",
                    code=code,
                    message=f"replay_report.{field_name} must match experiment_config.{field_name}",
                )
            )

    starting_capital = experiment_config.get("starting_capital")
    report_starting_capital = summary.get("starting_capital")
    if not _numbers_equal(starting_capital, report_starting_capital):
        issues.append(
            ComparisonIssue(
                field=f"{prefix}.replay_report.summary.starting_capital",
                code="starting_capital_mismatch",
                message=(
                    "replay_report.summary.starting_capital must match "
                    "experiment_config.starting_capital"
                ),
            )
        )


def _comparison_sort_key(entry: _ResolvedComparisonEntry) -> tuple[float, float, float, float, str]:
    summary = _mapping(entry.replay_report["summary"])
    return (
        -float(summary["total_return"]),
        float(summary["max_drawdown"]),
        -float(summary["win_rate"]),
        -float(summary["ending_total_equity"]),
        entry.configuration_id,
    )


def _build_comparison_row(
    *,
    entry: _ResolvedComparisonEntry,
    leader_summary: Mapping[str, Any],
    rank: int,
) -> ComparisonRow:
    report = entry.replay_report
    summary = _mapping(report["summary"])
    coverage = _mapping(report["coverage"])
    assumptions = _mapping(report["assumptions"])

    return ComparisonRow(
        rank=rank,
        configuration_id=entry.configuration_id,
        request_id=str(report["request_id"]),
        strategy_id=str(report["strategy_id"]),
        strategy_version=str(report["strategy_version"]),
        parameter_set_version=entry.parameter_set_version,
        parameter_set_id=entry.parameter_set_id,
        start_trade_date=str(report["start_trade_date"]),
        end_trade_date=str(report["end_trade_date"]),
        starting_capital=float(summary["starting_capital"]),
        rank_key={
            "total_return_desc": float(summary["total_return"]),
            "max_drawdown_asc": float(summary["max_drawdown"]),
            "win_rate_desc": float(summary["win_rate"]),
            "ending_total_equity_desc": float(summary["ending_total_equity"]),
            "configuration_id_asc": entry.configuration_id,
        },
        metrics={
            "total_return": float(summary["total_return"]),
            "max_drawdown": float(summary["max_drawdown"]),
            "ending_total_equity": float(summary["ending_total_equity"]),
            "win_rate": float(summary["win_rate"]),
            "turnover_ratio": float(summary["turnover_ratio"]),
            "executed_trade_count": int(summary["executed_trade_count"]),
            "rejected_intent_count": int(summary["rejected_intent_count"]),
        },
        metric_deltas_vs_leader={
            metric_name: float(summary[metric_name]) - float(leader_summary[metric_name])
            for metric_name in COMPARISON_DELTA_METRICS
        },
        assumptions={
            field_name: str(assumptions[field_name])
            for field_name in COMPARISON_ASSUMPTION_FIELDS
        },
        coverage={
            "requested_calendar_day_count": int(coverage["requested_calendar_day_count"]),
            "snapshot_count": int(coverage["snapshot_count"]),
            "market_bar_date_count": int(coverage["market_bar_date_count"]),
            "covered_market_bar_count": int(coverage["covered_market_bar_count"]),
            "missing_bar_day_count": len(tuple(coverage["missing_bar_dates"])),
            "unusable_bar_day_count": len(tuple(coverage["unusable_bar_dates"])),
            "first_bar_trade_date": coverage.get("first_bar_trade_date"),
            "last_bar_trade_date": coverage.get("last_bar_trade_date"),
        },
        artifact_reference=report.get("artifact_reference"),
    )


def _build_assumption_differences(
    entries: Sequence[_ResolvedComparisonEntry],
) -> tuple[ComparisonAssumptionDifference, ...]:
    differences: list[ComparisonAssumptionDifference] = []
    for field_name in COMPARISON_ASSUMPTION_FIELDS:
        values_by_configuration = {
            entry.configuration_id: str(_mapping(entry.replay_report["assumptions"])[field_name])
            for entry in sorted(entries, key=lambda item: item.configuration_id)
        }
        if len(set(values_by_configuration.values())) > 1:
            differences.append(
                ComparisonAssumptionDifference(
                    field=field_name,
                    values_by_configuration=values_by_configuration,
                )
            )
    return tuple(differences)


def _build_comparison_id(entries: Sequence[_ResolvedComparisonEntry]) -> str:
    normalized_payload = {
        "ranking_policy": COMPARISON_RANKING_POLICY,
        "entries": [
            {
                "configuration_id": entry.configuration_id,
                "experiment_config": entry.experiment_config,
                "replay_report": entry.replay_report,
            }
            for entry in sorted(entries, key=lambda item: item.configuration_id)
        ],
    }
    return sha256(
        json.dumps(normalized_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _extract_report_from_replay_result(payload: Any) -> Any | None:
    if payload is None:
        return None
    if isinstance(payload, Mapping):
        return payload.get("report")
    return getattr(payload, "report", None)


def _validate_expected_fields(
    record: Mapping[str, Any],
    allowed_fields: tuple[str, ...],
    *,
    prefix: str,
) -> list[ComparisonIssue]:
    allowed = set(allowed_fields)
    return [
        ComparisonIssue(
            field=f"{prefix}.{field_name}",
            code="unexpected_field",
            message=f"{field_name} is not part of this comparison contract",
        )
        for field_name in record
        if field_name not in allowed
    ]


def _mapping(payload: Any) -> Mapping[str, Any]:
    if isinstance(payload, Mapping):
        return payload
    if is_dataclass(payload):
        return asdict(payload)
    return {}


def _is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)


def _numbers_equal(left: Any, right: Any) -> bool:
    return _is_finite_number(left) and _is_finite_number(right) and float(left) == float(right)


__all__ = [
    "COMPARISON_ASSUMPTION_FIELDS",
    "COMPARISON_DELTA_METRICS",
    "COMPARISON_INPUT_FIELDS",
    "COMPARISON_RANKING_POLICY",
    "COMPARISON_REQUIRED_METRICS",
    "ComparisonAssumptionDifference",
    "ComparisonInput",
    "ComparisonIssue",
    "ComparisonRow",
    "ComparisonWorkflowError",
    "MultiConfigurationComparison",
    "build_multi_configuration_comparison",
    "validate_multi_configuration_comparison_inputs",
]
