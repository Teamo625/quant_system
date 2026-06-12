"""Deterministic local batch orchestration over existing FeatureHub primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from math import isfinite
from typing import Any, Iterable, Mapping

from quant.datahub.datasets import DatasetName

from .capital_flow import (
    calculate_fund_flow_activity_intensity,
    calculate_fund_net_inflow_change,
    calculate_latest_fund_net_inflow,
    calculate_latest_main_net_inflow,
    calculate_latest_northbound_net_buy,
    calculate_main_net_inflow_change,
    calculate_northbound_net_buy_change,
    calculate_trailing_fund_net_inflow_sum,
    calculate_trailing_main_net_inflow_sum,
    calculate_trailing_turnover_adjusted_main_net_inflow,
    calculate_turnover_adjusted_main_net_inflow,
    normalize_capital_flow_snapshots,
    normalize_fund_flow_inputs,
)
from .contracts import (
    FEATURE_VALUE_SCHEMA_VERSION,
    FeatureName,
    FeatureScalar,
    FeatureValueRecord,
    build_feature_metric_identity,
    validate_feature_value_record,
)
from .relative import (
    calculate_above_threshold_return_ratio,
    calculate_index_relative_performance,
    calculate_positive_return_ratio,
    calculate_relative_sector_momentum,
    calculate_sector_return_rankings,
    calculate_sector_strength,
    calculate_sector_strength_from_returns,
    calculate_stock_vs_sector_return_spread,
    calculate_top_bottom_sector_spread,
    normalize_entity_return_series,
    normalize_member_return_rows,
    normalize_relative_price_series,
)
from .storage import FeatureOutputManifest, build_feature_output_manifest
from .technical import (
    calculate_amihud_illiquidity,
    calculate_average_true_range,
    calculate_average_turnover,
    calculate_average_volume,
    calculate_bollinger_bands,
    calculate_breakout_ratio,
    calculate_close_to_close_return,
    calculate_exponential_moving_average,
    calculate_gap_return,
    calculate_macd,
    calculate_realized_volatility,
    calculate_relative_strength_index,
    calculate_simple_moving_average,
    calculate_stochastic_oscillator,
    normalize_daily_bars,
)
from .valuation import (
    calculate_book_to_price,
    calculate_earnings_yield,
    calculate_float_market_cap_ratio,
    calculate_latest_pb,
    calculate_latest_pe_ttm,
    calculate_latest_ps_ttm,
    calculate_relative_valuation_to_history_mean,
    calculate_valuation_percentile,
    normalize_valuation_snapshots,
)


@dataclass(frozen=True)
class FeatureBatchContextInput:
    """Additional caller-provided in-memory rows required by one batch job."""

    role: str
    source_dataset: DatasetName
    rows: tuple[Any, ...]


@dataclass(frozen=True)
class FeatureBatchJob:
    """One deterministic batch calculation request for one feature output record."""

    job_id: str
    symbol: str
    market: str
    feature_name: FeatureName
    metric_name: str
    source_dataset: DatasetName
    input_rows: tuple[Any, ...]
    parameters: Mapping[str, FeatureScalar] = field(default_factory=dict)
    context_inputs: tuple[FeatureBatchContextInput, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class FeatureBatchResult:
    """Deterministic local batch result ready for persistence."""

    records: tuple[FeatureValueRecord, ...]
    manifest: FeatureOutputManifest


@dataclass(frozen=True)
class _BatchOutcome:
    trade_date: date
    value: FeatureScalar
    metric_params: Mapping[str, FeatureScalar]


def calculate_feature_batch(
    jobs: Iterable[FeatureBatchJob | Mapping[str, Any]],
    *,
    created_at: datetime,
) -> FeatureBatchResult:
    """Calculate a deterministic offline feature batch over caller-provided rows."""
    if not isinstance(created_at, datetime):
        raise ValueError("created_at must be a datetime instance")

    normalized_jobs = tuple(_coerce_feature_batch_job(job) for job in jobs)
    if not normalized_jobs:
        raise ValueError("at least one batch job is required")

    seen_job_ids: set[str] = set()
    indexed_records: list[tuple[int, FeatureValueRecord]] = []
    seen_output_identities: set[tuple[str, str, date, str]] = set()

    for job_index, job in enumerate(normalized_jobs):
        if job.job_id in seen_job_ids:
            raise ValueError(f"duplicate batch job_id is not allowed: {job.job_id}")
        seen_job_ids.add(job.job_id)

        outcome = _calculate_job_outcome(job)
        record = FeatureValueRecord(
            symbol=job.symbol,
            market=job.market,
            trade_date=outcome.trade_date,
            feature_name=job.feature_name,
            metric_name=job.metric_name,
            value=outcome.value,
            source_dataset=job.source_dataset,
            created_at=created_at,
            metric_params=dict(sorted(outcome.metric_params.items())),
            schema_version=FEATURE_VALUE_SCHEMA_VERSION,
        )
        issues = validate_feature_value_record(record)
        if issues:
            raise ValueError(
                f"batch job {job.job_id} produced an invalid feature record: {issues!r}"
            )

        metric_identity = build_feature_metric_identity(record)
        output_identity = (
            record.market,
            record.symbol,
            record.trade_date,
            metric_identity,
        )
        if output_identity in seen_output_identities:
            raise ValueError(
                "duplicate output identity produced by batch jobs: "
                f"{record.market}/{record.symbol}/{record.trade_date.isoformat()}/"
                f"{metric_identity}"
            )
        seen_output_identities.add(output_identity)
        indexed_records.append((job_index, record))

    records = tuple(
        record
        for _, record in sorted(
            indexed_records,
            key=lambda item: (
                item[1].market,
                item[1].symbol,
                item[1].trade_date,
                item[1].feature_name.value,
                build_feature_metric_identity(item[1]),
                item[0],
            ),
        )
    )
    return FeatureBatchResult(
        records=records,
        manifest=build_feature_output_manifest(records),
    )


def _coerce_feature_batch_job(
    job: FeatureBatchJob | Mapping[str, Any],
) -> FeatureBatchJob:
    payload = dict(job) if isinstance(job, Mapping) else None
    if isinstance(job, FeatureBatchJob):
        payload = {
            "job_id": job.job_id,
            "symbol": job.symbol,
            "market": job.market,
            "feature_name": job.feature_name,
            "metric_name": job.metric_name,
            "source_dataset": job.source_dataset,
            "input_rows": job.input_rows,
            "parameters": job.parameters,
            "context_inputs": job.context_inputs,
        }
    if payload is None:
        raise ValueError("batch jobs must be FeatureBatchJob instances or mappings")

    job_id = _require_nonempty_text(payload.get("job_id"), field_name="job_id")
    symbol = _require_nonempty_text(payload.get("symbol"), field_name="symbol")
    market = _require_nonempty_text(payload.get("market"), field_name="market")
    feature_name = _coerce_feature_name(payload.get("feature_name"))
    metric_name = _require_nonempty_text(
        payload.get("metric_name"),
        field_name="metric_name",
    )
    source_dataset = _coerce_dataset_name(payload.get("source_dataset"))
    input_rows_value = payload.get("input_rows")
    if not isinstance(input_rows_value, Iterable):
        raise ValueError("input_rows must be an iterable of caller-provided rows")
    parameters = _coerce_parameters(payload.get("parameters"))
    context_inputs = tuple(
        sorted(
            (
                _coerce_context_input(context_input)
                for context_input in payload.get("context_inputs", ())
            ),
            key=lambda item: item.role,
        )
    )
    seen_roles: set[str] = set()
    for context_input in context_inputs:
        if context_input.role in seen_roles:
            raise ValueError(
                f"duplicate context input role is not allowed: {context_input.role}"
            )
        seen_roles.add(context_input.role)

    return FeatureBatchJob(
        job_id=job_id,
        symbol=symbol,
        market=market,
        feature_name=feature_name,
        metric_name=metric_name,
        source_dataset=source_dataset,
        input_rows=tuple(input_rows_value),
        parameters=parameters,
        context_inputs=context_inputs,
    )


def _coerce_context_input(
    context_input: FeatureBatchContextInput | Mapping[str, Any],
) -> FeatureBatchContextInput:
    payload = dict(context_input) if isinstance(context_input, Mapping) else None
    if isinstance(context_input, FeatureBatchContextInput):
        payload = {
            "role": context_input.role,
            "source_dataset": context_input.source_dataset,
            "rows": context_input.rows,
        }
    if payload is None:
        raise ValueError(
            "context inputs must be FeatureBatchContextInput instances or mappings"
        )

    role = _require_nonempty_text(payload.get("role"), field_name="role")
    source_dataset = _coerce_dataset_name(payload.get("source_dataset"))
    rows_value = payload.get("rows")
    if not isinstance(rows_value, Iterable):
        raise ValueError("context rows must be an iterable of caller-provided rows")
    return FeatureBatchContextInput(
        role=role,
        source_dataset=source_dataset,
        rows=tuple(rows_value),
    )


def _coerce_feature_name(value: Any) -> FeatureName:
    if isinstance(value, FeatureName):
        return value
    if isinstance(value, str):
        try:
            return FeatureName(value)
        except ValueError as exc:
            raise ValueError("feature_name must be a supported FeatureName value") from exc
    raise ValueError("feature_name must be a supported FeatureName value")


def _coerce_dataset_name(value: Any) -> DatasetName:
    if isinstance(value, DatasetName):
        return value
    if isinstance(value, str):
        try:
            return DatasetName(value)
        except ValueError as exc:
            raise ValueError("source_dataset must be a supported DatasetName value") from exc
    raise ValueError("source_dataset must be a supported DatasetName value")


def _coerce_parameters(value: Any) -> dict[str, FeatureScalar]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError("parameters must be a mapping of scalar calculation parameters")

    normalized: dict[str, FeatureScalar] = {}
    for key, item in value.items():
        normalized_key = _require_nonempty_text(key, field_name="parameter key")
        if isinstance(item, bool):
            raise ValueError(
                "parameters must contain only finite int, float, or string values"
            )
        if isinstance(item, str):
            normalized[normalized_key] = item
            continue
        if isinstance(item, int):
            normalized[normalized_key] = item
            continue
        if isinstance(item, float) and isfinite(item):
            normalized[normalized_key] = item
            continue
        raise ValueError(
            "parameters must contain only finite int, float, or string values"
        )
    return normalized


def _calculate_job_outcome(job: FeatureBatchJob) -> _BatchOutcome:
    if job.feature_name is FeatureName.PRICE_TECHNICAL:
        return _calculate_technical_outcome(job)
    if job.feature_name is FeatureName.VALUATION:
        return _calculate_valuation_outcome(job)
    if job.feature_name is FeatureName.CAPITAL_FLOW:
        return _calculate_capital_flow_outcome(job)
    if job.feature_name is FeatureName.RELATIVE:
        return _calculate_relative_outcome(job)
    raise ValueError(f"unsupported batch feature family: {job.feature_name.value}")


def _calculate_technical_outcome(job: FeatureBatchJob) -> _BatchOutcome:
    if job.source_dataset is not DatasetName.DAILY_BARS:
        raise ValueError("technical batch jobs must use source_dataset=daily_bars")
    if job.context_inputs:
        raise ValueError("technical batch jobs do not support context inputs")

    bars = normalize_daily_bars(job.input_rows)
    latest_bar = bars[-1]
    _require_symbol_market_match(
        expected_symbol=job.symbol,
        expected_market=job.market,
        actual_symbol=latest_bar.symbol,
        actual_market=latest_bar.market,
        context="technical batch job",
    )

    params = job.parameters
    if job.metric_name == "close_to_close_return":
        _require_allowed_parameters(params, allowed_keys=())
        value = calculate_close_to_close_return(bars)
        metric_params: dict[str, FeatureScalar] = {}
    elif job.metric_name == "simple_moving_average":
        window = _require_int_parameter(params, "window")
        value = calculate_simple_moving_average(bars, window=window)
        metric_params = {"window": window}
    elif job.metric_name == "realized_volatility":
        window = _require_int_parameter(params, "window")
        annualization_factor = _optional_float_parameter(
            params,
            "annualization_factor",
            default=252.0,
        )
        value = calculate_realized_volatility(
            bars,
            window=window,
            annualization_factor=annualization_factor,
        )
        metric_params = {
            "window": window,
            "annualization_factor": annualization_factor,
        }
    elif job.metric_name == "exponential_moving_average":
        window = _require_int_parameter(params, "window")
        value = calculate_exponential_moving_average(bars, window=window)
        metric_params = {"window": window}
    elif job.metric_name == "macd_line":
        short_window, long_window, signal_window = _macd_parameters(params)
        value = calculate_macd(
            bars,
            short_window=short_window,
            long_window=long_window,
            signal_window=signal_window,
        ).macd_line
        metric_params = {
            "short_window": short_window,
            "long_window": long_window,
            "signal_window": signal_window,
        }
    elif job.metric_name == "macd_signal_line":
        short_window, long_window, signal_window = _macd_parameters(params)
        value = calculate_macd(
            bars,
            short_window=short_window,
            long_window=long_window,
            signal_window=signal_window,
        ).signal_line
        metric_params = {
            "short_window": short_window,
            "long_window": long_window,
            "signal_window": signal_window,
        }
    elif job.metric_name == "macd_histogram":
        short_window, long_window, signal_window = _macd_parameters(params)
        value = calculate_macd(
            bars,
            short_window=short_window,
            long_window=long_window,
            signal_window=signal_window,
        ).histogram
        metric_params = {
            "short_window": short_window,
            "long_window": long_window,
            "signal_window": signal_window,
        }
    elif job.metric_name == "relative_strength_index":
        window = _optional_int_parameter(params, "window", default=14)
        value = calculate_relative_strength_index(bars, window=window)
        metric_params = {"window": window}
    elif job.metric_name == "stochastic_percent_k":
        k_window, d_window = _stochastic_parameters(params)
        value = calculate_stochastic_oscillator(
            bars,
            k_window=k_window,
            d_window=d_window,
        ).percent_k
        metric_params = {"k_window": k_window, "d_window": d_window}
    elif job.metric_name == "stochastic_percent_d":
        k_window, d_window = _stochastic_parameters(params)
        value = calculate_stochastic_oscillator(
            bars,
            k_window=k_window,
            d_window=d_window,
        ).percent_d
        metric_params = {"k_window": k_window, "d_window": d_window}
    elif job.metric_name == "stochastic_percent_j":
        k_window, d_window = _stochastic_parameters(params)
        value = calculate_stochastic_oscillator(
            bars,
            k_window=k_window,
            d_window=d_window,
        ).percent_j
        metric_params = {"k_window": k_window, "d_window": d_window}
    elif job.metric_name == "bollinger_middle_band":
        window, num_std_dev = _bollinger_parameters(params)
        value = calculate_bollinger_bands(
            bars,
            window=window,
            num_std_dev=num_std_dev,
        ).middle_band
        metric_params = {"window": window, "num_std_dev": num_std_dev}
    elif job.metric_name == "bollinger_upper_band":
        window, num_std_dev = _bollinger_parameters(params)
        value = calculate_bollinger_bands(
            bars,
            window=window,
            num_std_dev=num_std_dev,
        ).upper_band
        metric_params = {"window": window, "num_std_dev": num_std_dev}
    elif job.metric_name == "bollinger_lower_band":
        window, num_std_dev = _bollinger_parameters(params)
        value = calculate_bollinger_bands(
            bars,
            window=window,
            num_std_dev=num_std_dev,
        ).lower_band
        metric_params = {"window": window, "num_std_dev": num_std_dev}
    elif job.metric_name == "bollinger_bandwidth":
        window, num_std_dev = _bollinger_parameters(params)
        value = calculate_bollinger_bands(
            bars,
            window=window,
            num_std_dev=num_std_dev,
        ).bandwidth
        metric_params = {"window": window, "num_std_dev": num_std_dev}
    elif job.metric_name == "average_true_range":
        window = _require_int_parameter(params, "window")
        value = calculate_average_true_range(bars, window=window)
        metric_params = {"window": window}
    elif job.metric_name == "average_volume":
        window = _require_int_parameter(params, "window")
        value = calculate_average_volume(bars, window=window)
        metric_params = {"window": window}
    elif job.metric_name == "average_turnover":
        window = _require_int_parameter(params, "window")
        value = calculate_average_turnover(bars, window=window)
        metric_params = {"window": window}
    elif job.metric_name == "amihud_illiquidity":
        window = _require_int_parameter(params, "window")
        value = calculate_amihud_illiquidity(bars, window=window)
        metric_params = {"window": window}
    elif job.metric_name == "gap_return":
        _require_allowed_parameters(params, allowed_keys=())
        value = calculate_gap_return(bars)
        metric_params = {}
    elif job.metric_name == "breakout_ratio":
        window = _optional_int_parameter(params, "window", default=20)
        value = calculate_breakout_ratio(bars, window=window)
        metric_params = {"window": window}
    else:
        raise ValueError(f"unsupported technical metric_name: {job.metric_name}")

    return _BatchOutcome(
        trade_date=latest_bar.trade_date,
        value=value,
        metric_params=metric_params,
    )


def _calculate_valuation_outcome(job: FeatureBatchJob) -> _BatchOutcome:
    if job.source_dataset is not DatasetName.VALUATION_SNAPSHOT:
        raise ValueError("valuation batch jobs must use source_dataset=valuation_snapshot")
    if job.context_inputs:
        raise ValueError("valuation batch jobs do not support context inputs")

    snapshots = normalize_valuation_snapshots(job.input_rows)
    latest_snapshot = snapshots[-1]
    _require_symbol_market_match(
        expected_symbol=job.symbol,
        expected_market=job.market,
        actual_symbol=latest_snapshot.symbol,
        actual_market=latest_snapshot.market,
        context="valuation batch job",
    )

    params = job.parameters
    if job.metric_name == "latest_pe_ttm":
        _require_allowed_parameters(params, allowed_keys=())
        value = calculate_latest_pe_ttm(snapshots)
        metric_params: dict[str, FeatureScalar] = {}
    elif job.metric_name == "latest_pb":
        _require_allowed_parameters(params, allowed_keys=())
        value = calculate_latest_pb(snapshots)
        metric_params = {}
    elif job.metric_name == "latest_ps_ttm":
        _require_allowed_parameters(params, allowed_keys=())
        value = calculate_latest_ps_ttm(snapshots)
        metric_params = {}
    elif job.metric_name == "earnings_yield":
        _require_allowed_parameters(params, allowed_keys=())
        value = calculate_earnings_yield(snapshots)
        metric_params = {}
    elif job.metric_name == "book_to_price":
        _require_allowed_parameters(params, allowed_keys=())
        value = calculate_book_to_price(snapshots)
        metric_params = {}
    elif job.metric_name == "float_market_cap_ratio":
        _require_allowed_parameters(params, allowed_keys=())
        value = calculate_float_market_cap_ratio(snapshots)
        metric_params = {}
    elif job.metric_name == "valuation_percentile":
        metric_name = _require_string_parameter(params, "metric_name")
        window = _require_int_parameter(params, "window")
        value = calculate_valuation_percentile(
            snapshots,
            metric_name=metric_name,
            window=window,
        )
        metric_params = {"metric_name": metric_name, "window": window}
    elif job.metric_name == "relative_valuation_to_history_mean":
        metric_name = _require_string_parameter(params, "metric_name")
        window = _require_int_parameter(params, "window")
        value = calculate_relative_valuation_to_history_mean(
            snapshots,
            metric_name=metric_name,
            window=window,
        )
        metric_params = {"metric_name": metric_name, "window": window}
    else:
        raise ValueError(f"unsupported valuation metric_name: {job.metric_name}")

    return _BatchOutcome(
        trade_date=latest_snapshot.trade_date,
        value=value,
        metric_params=metric_params,
    )


def _calculate_capital_flow_outcome(job: FeatureBatchJob) -> _BatchOutcome:
    if job.context_inputs:
        raise ValueError("capital-flow batch jobs do not support context inputs")

    if job.source_dataset in (
        DatasetName.CAPITAL_FLOW_SNAPSHOT,
        DatasetName.NORTHBOUND_FLOW_SNAPSHOT,
    ):
        return _calculate_capital_flow_snapshot_outcome(job)
    if job.source_dataset is DatasetName.FUND_FLOW:
        return _calculate_fund_flow_outcome(job)
    raise ValueError(
        "capital-flow batch jobs must use source_dataset=capital_flow_snapshot, "
        "northbound_flow_snapshot, or fund_flow"
    )


def _calculate_capital_flow_snapshot_outcome(job: FeatureBatchJob) -> _BatchOutcome:
    snapshots = normalize_capital_flow_snapshots(job.input_rows)
    latest_snapshot = snapshots[-1]
    _require_symbol_market_match(
        expected_symbol=job.symbol,
        expected_market=job.market,
        actual_symbol=latest_snapshot.symbol,
        actual_market=latest_snapshot.market,
        context="capital-flow batch job",
    )

    params = job.parameters
    if job.metric_name == "latest_main_net_inflow":
        _require_allowed_parameters(params, allowed_keys=())
        value = calculate_latest_main_net_inflow(snapshots)
        metric_params: dict[str, FeatureScalar] = {}
    elif job.metric_name == "trailing_main_net_inflow_sum":
        window = _require_int_parameter(params, "window")
        value = calculate_trailing_main_net_inflow_sum(snapshots, window=window)
        metric_params = {"window": window}
    elif job.metric_name == "main_net_inflow_change":
        periods = _optional_int_parameter(params, "periods", default=1)
        value = calculate_main_net_inflow_change(snapshots, periods=periods)
        metric_params = {"periods": periods}
    elif job.metric_name == "latest_northbound_net_buy":
        _require_allowed_parameters(params, allowed_keys=())
        value = _require_non_null_output(
            calculate_latest_northbound_net_buy(snapshots),
            metric_name=job.metric_name,
        )
        metric_params = {}
    elif job.metric_name == "northbound_net_buy_change":
        periods = _optional_int_parameter(params, "periods", default=1)
        value = _require_non_null_output(
            calculate_northbound_net_buy_change(snapshots, periods=periods),
            metric_name=job.metric_name,
        )
        metric_params = {"periods": periods}
    elif job.metric_name == "turnover_adjusted_main_net_inflow":
        _require_allowed_parameters(params, allowed_keys=())
        value = _require_non_null_output(
            calculate_turnover_adjusted_main_net_inflow(snapshots),
            metric_name=job.metric_name,
        )
        metric_params = {}
    elif job.metric_name == "trailing_turnover_adjusted_main_net_inflow":
        window = _require_int_parameter(params, "window")
        value = _require_non_null_output(
            calculate_trailing_turnover_adjusted_main_net_inflow(
                snapshots,
                window=window,
            ),
            metric_name=job.metric_name,
        )
        metric_params = {"window": window}
    else:
        raise ValueError(f"unsupported capital-flow metric_name: {job.metric_name}")

    return _BatchOutcome(
        trade_date=latest_snapshot.trade_date,
        value=value,
        metric_params=metric_params,
    )


def _calculate_fund_flow_outcome(job: FeatureBatchJob) -> _BatchOutcome:
    snapshots = normalize_fund_flow_inputs(job.input_rows)
    latest_snapshot = snapshots[-1]
    _require_symbol_market_match(
        expected_symbol=job.symbol,
        expected_market=job.market,
        actual_symbol=latest_snapshot.fund_code,
        actual_market=latest_snapshot.market,
        context="fund-flow batch job",
    )

    params = job.parameters
    if job.metric_name == "latest_fund_net_inflow":
        _require_allowed_parameters(params, allowed_keys=())
        value = calculate_latest_fund_net_inflow(snapshots)
        metric_params: dict[str, FeatureScalar] = {}
    elif job.metric_name == "trailing_fund_net_inflow_sum":
        window = _require_int_parameter(params, "window")
        value = calculate_trailing_fund_net_inflow_sum(snapshots, window=window)
        metric_params = {"window": window}
    elif job.metric_name == "fund_net_inflow_change":
        periods = _optional_int_parameter(params, "periods", default=1)
        value = calculate_fund_net_inflow_change(snapshots, periods=periods)
        metric_params = {"periods": periods}
    elif job.metric_name == "fund_flow_activity_intensity":
        _require_allowed_parameters(params, allowed_keys=())
        value = _require_non_null_output(
            calculate_fund_flow_activity_intensity(snapshots),
            metric_name=job.metric_name,
        )
        metric_params = {}
    else:
        raise ValueError(f"unsupported fund-flow metric_name: {job.metric_name}")

    return _BatchOutcome(
        trade_date=latest_snapshot.trade_date,
        value=value,
        metric_params=metric_params,
    )


def _calculate_relative_outcome(job: FeatureBatchJob) -> _BatchOutcome:
    contexts = {context_input.role: context_input for context_input in job.context_inputs}
    params = job.parameters

    if job.metric_name == "stock_vs_sector_return_spread":
        _require_context_roles(contexts, required_roles=("sector_rows",))
        _require_allowed_source_dataset(
            job.source_dataset,
            allowed_datasets=(DatasetName.DAILY_BARS,),
            context="stock-vs-sector batch job",
        )
        _require_allowed_source_dataset(
            contexts["sector_rows"].source_dataset,
            allowed_datasets=(DatasetName.SECTOR_DAILY_BARS, DatasetName.DAILY_BARS),
            context="stock-vs-sector context input",
        )
        window = _require_int_parameter(params, "window")
        primary_rows = normalize_relative_price_series(job.input_rows)
        _require_relative_symbol_match(primary_rows[-1].entity_id, job.symbol, job.market, primary_rows[-1].market)
        value = calculate_stock_vs_sector_return_spread(
            primary_rows,
            contexts["sector_rows"].rows,
            window=window,
        )
        trade_date = _aligned_relative_trade_date(
            primary_rows,
            contexts["sector_rows"].rows,
            window=window,
            context="stock-vs-sector window",
        )
        metric_params = {"window": window}
    elif job.metric_name == "sector_strength":
        _require_context_roles(contexts, required_roles=())
        _require_allowed_source_dataset(
            job.source_dataset,
            allowed_datasets=(DatasetName.SECTOR_DAILY_BARS, DatasetName.DAILY_BARS),
            context="sector-strength batch job",
        )
        window = _require_int_parameter(params, "window")
        primary_rows = normalize_relative_price_series(job.input_rows)
        _require_relative_symbol_match(primary_rows[-1].entity_id, job.symbol, job.market, primary_rows[-1].market)
        value = calculate_sector_strength(primary_rows, window=window)
        trade_date = primary_rows[-1].trade_date
        metric_params = {"window": window}
    elif job.metric_name == "sector_strength_from_returns":
        _require_context_roles(contexts, required_roles=())
        _require_allowed_source_dataset(
            job.source_dataset,
            allowed_datasets=(DatasetName.SECTOR_DAILY_BARS,),
            context="sector-strength-return batch job",
        )
        window = _require_int_parameter(params, "window")
        primary_rows = normalize_entity_return_series(job.input_rows)
        _require_relative_symbol_match(primary_rows[-1].entity_id, job.symbol, job.market, primary_rows[-1].market)
        value = calculate_sector_strength_from_returns(primary_rows, window=window)
        trade_date = primary_rows[-1].trade_date
        metric_params = {"window": window}
    elif job.metric_name == "index_relative_performance":
        _require_context_roles(contexts, required_roles=("index_rows",))
        _require_allowed_source_dataset(
            job.source_dataset,
            allowed_datasets=(DatasetName.DAILY_BARS, DatasetName.INDEX_DAILY_BARS),
            context="index-relative batch job",
        )
        _require_allowed_source_dataset(
            contexts["index_rows"].source_dataset,
            allowed_datasets=(DatasetName.INDEX_DAILY_BARS, DatasetName.DAILY_BARS),
            context="index-relative context input",
        )
        window = _require_int_parameter(params, "window")
        primary_rows = normalize_relative_price_series(job.input_rows)
        _require_relative_symbol_match(primary_rows[-1].entity_id, job.symbol, job.market, primary_rows[-1].market)
        value = calculate_index_relative_performance(
            primary_rows,
            contexts["index_rows"].rows,
            window=window,
        )
        trade_date = _aligned_relative_trade_date(
            primary_rows,
            contexts["index_rows"].rows,
            window=window,
            context="index-relative window",
        )
        metric_params = {"window": window}
    elif job.metric_name == "positive_return_ratio":
        _require_context_roles(contexts, required_roles=())
        _require_allowed_source_dataset(
            job.source_dataset,
            allowed_datasets=(DatasetName.SECTOR_MEMBERSHIP,),
            context="breadth batch job",
        )
        member_rows = normalize_member_return_rows(job.input_rows)
        _require_relative_symbol_match(member_rows[0].universe_id, job.symbol, job.market, member_rows[0].market)
        value = calculate_positive_return_ratio(member_rows)
        trade_date = member_rows[0].trade_date
        metric_params = {}
    elif job.metric_name == "above_threshold_return_ratio":
        _require_context_roles(contexts, required_roles=())
        _require_allowed_source_dataset(
            job.source_dataset,
            allowed_datasets=(DatasetName.SECTOR_MEMBERSHIP,),
            context="breadth batch job",
        )
        threshold = _require_float_parameter(params, "threshold")
        member_rows = normalize_member_return_rows(job.input_rows)
        _require_relative_symbol_match(member_rows[0].universe_id, job.symbol, job.market, member_rows[0].market)
        value = calculate_above_threshold_return_ratio(member_rows, threshold=threshold)
        trade_date = member_rows[0].trade_date
        metric_params = {"threshold": threshold}
    elif job.metric_name == "relative_sector_momentum":
        _require_context_roles(contexts, required_roles=())
        _require_allowed_source_dataset(
            job.source_dataset,
            allowed_datasets=(DatasetName.SECTOR_DAILY_BARS,),
            context="relative-sector-momentum batch job",
        )
        window = _require_int_parameter(params, "window")
        value = calculate_relative_sector_momentum(
            job.input_rows,
            target_sector_id=job.symbol,
            window=window,
        )
        rankings = calculate_sector_return_rankings(job.input_rows, window=window)
        _require_uniform_market(job.market, rankings[0].market, context="relative-sector-momentum batch job")
        trade_date = rankings[0].trade_date
        metric_params = {"window": window}
    elif job.metric_name == "top_bottom_sector_spread":
        _require_context_roles(contexts, required_roles=())
        _require_allowed_source_dataset(
            job.source_dataset,
            allowed_datasets=(DatasetName.SECTOR_DAILY_BARS,),
            context="sector-spread batch job",
        )
        window = _require_int_parameter(params, "window")
        value = calculate_top_bottom_sector_spread(job.input_rows, window=window)
        rankings = calculate_sector_return_rankings(job.input_rows, window=window)
        _require_uniform_market(job.market, rankings[0].market, context="sector-spread batch job")
        trade_date = rankings[0].trade_date
        metric_params = {"window": window}
    else:
        raise ValueError(f"unsupported relative metric_name: {job.metric_name}")

    return _BatchOutcome(
        trade_date=trade_date,
        value=value,
        metric_params=metric_params,
    )


def _require_nonempty_text(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


def _require_symbol_market_match(
    *,
    expected_symbol: str,
    expected_market: str,
    actual_symbol: str,
    actual_market: str,
    context: str,
) -> None:
    if actual_symbol != expected_symbol:
        raise ValueError(f"{context} symbol does not match normalized input rows")
    if actual_market != expected_market:
        raise ValueError(f"{context} market does not match normalized input rows")


def _require_relative_symbol_match(
    actual_symbol: str,
    expected_symbol: str,
    expected_market: str,
    actual_market: str,
) -> None:
    _require_symbol_market_match(
        expected_symbol=expected_symbol,
        expected_market=expected_market,
        actual_symbol=actual_symbol,
        actual_market=actual_market,
        context="relative batch job",
    )


def _require_allowed_source_dataset(
    source_dataset: DatasetName,
    *,
    allowed_datasets: tuple[DatasetName, ...],
    context: str,
) -> None:
    if source_dataset not in allowed_datasets:
        supported = ", ".join(dataset.value for dataset in allowed_datasets)
        raise ValueError(
            f"{context} uses unsupported source_dataset={source_dataset.value}; "
            f"supported values: {supported}"
        )


def _require_context_roles(
    contexts: Mapping[str, FeatureBatchContextInput],
    *,
    required_roles: tuple[str, ...],
) -> None:
    context_roles = set(contexts)
    required = set(required_roles)
    missing = sorted(required - context_roles)
    extra = sorted(context_roles - required)
    if missing:
        raise ValueError(
            f"missing required context inputs: {', '.join(missing)}"
        )
    if extra:
        raise ValueError(f"unexpected context inputs: {', '.join(extra)}")


def _require_allowed_parameters(
    parameters: Mapping[str, FeatureScalar],
    *,
    allowed_keys: tuple[str, ...],
) -> None:
    extra_keys = sorted(set(parameters) - set(allowed_keys))
    if extra_keys:
        raise ValueError(
            f"unexpected calculation parameters: {', '.join(extra_keys)}"
        )


def _require_int_parameter(
    parameters: Mapping[str, FeatureScalar],
    name: str,
) -> int:
    if name not in parameters:
        raise ValueError(f"missing required calculation parameter: {name}")
    return _coerce_positive_int(parameters[name], name=name)


def _optional_int_parameter(
    parameters: Mapping[str, FeatureScalar],
    name: str,
    *,
    default: int,
) -> int:
    _require_allowed_parameters(parameters, allowed_keys=(name,))
    if name not in parameters:
        return default
    return _coerce_positive_int(parameters[name], name=name)


def _require_float_parameter(
    parameters: Mapping[str, FeatureScalar],
    name: str,
) -> float:
    if name not in parameters:
        raise ValueError(f"missing required calculation parameter: {name}")
    return _coerce_finite_float(parameters[name], name=name)


def _optional_float_parameter(
    parameters: Mapping[str, FeatureScalar],
    name: str,
    *,
    default: float,
) -> float:
    _require_allowed_parameters(parameters, allowed_keys=(name,))
    if name not in parameters:
        return default
    return _coerce_finite_float(parameters[name], name=name)


def _require_string_parameter(
    parameters: Mapping[str, FeatureScalar],
    name: str,
) -> str:
    if name not in parameters:
        raise ValueError(f"missing required calculation parameter: {name}")
    value = parameters[name]
    if not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _coerce_positive_int(value: FeatureScalar, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _coerce_finite_float(value: FeatureScalar, *, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    numeric_value = float(value)
    if not isfinite(numeric_value):
        raise ValueError(f"{name} must be a finite number")
    return numeric_value


def _macd_parameters(parameters: Mapping[str, FeatureScalar]) -> tuple[int, int, int]:
    _require_allowed_parameters(
        parameters,
        allowed_keys=("short_window", "long_window", "signal_window"),
    )
    return (
        _coerce_positive_int(parameters.get("short_window", 12), name="short_window"),
        _coerce_positive_int(parameters.get("long_window", 26), name="long_window"),
        _coerce_positive_int(parameters.get("signal_window", 9), name="signal_window"),
    )


def _stochastic_parameters(
    parameters: Mapping[str, FeatureScalar],
) -> tuple[int, int]:
    _require_allowed_parameters(parameters, allowed_keys=("k_window", "d_window"))
    return (
        _coerce_positive_int(parameters.get("k_window", 9), name="k_window"),
        _coerce_positive_int(parameters.get("d_window", 3), name="d_window"),
    )


def _bollinger_parameters(
    parameters: Mapping[str, FeatureScalar],
) -> tuple[int, float]:
    _require_allowed_parameters(parameters, allowed_keys=("window", "num_std_dev"))
    return (
        _coerce_positive_int(parameters.get("window", 20), name="window"),
        _coerce_finite_float(parameters.get("num_std_dev", 2.0), name="num_std_dev"),
    )


def _require_non_null_output(value: Any, *, metric_name: str) -> FeatureScalar:
    if value is None:
        raise ValueError(
            f"{metric_name} cannot be emitted because required input values are missing"
        )
    if isinstance(value, bool):
        raise ValueError(f"{metric_name} produced an unsupported boolean output")
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float) and isfinite(value):
        return value
    raise ValueError(f"{metric_name} produced an unsupported non-finite output")


def _aligned_relative_trade_date(
    left_rows: Iterable[Any],
    right_rows: Iterable[Any],
    *,
    window: int,
    context: str,
) -> date:
    left_series = normalize_relative_price_series(left_rows)
    right_series = normalize_relative_price_series(right_rows)
    _require_uniform_market(
        left_series[0].market,
        right_series[0].market,
        context="aligned relative calculation",
    )
    common_dates = sorted(
        {row.trade_date for row in left_series} & {row.trade_date for row in right_series}
    )
    if len(common_dates) < window:
        raise ValueError(f"insufficient aligned rows for requested {context}")
    return common_dates[-1]


def _require_uniform_market(expected_market: str, actual_market: str, *, context: str) -> None:
    if expected_market != actual_market:
        raise ValueError(f"{context} market does not match normalized input rows")
