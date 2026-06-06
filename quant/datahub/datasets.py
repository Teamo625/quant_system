"""Dataset registry and schema contracts for DataHub."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, Mapping


class DatasetName(str, Enum):
    """Canonical dataset identifiers for downstream contracts."""

    INSTRUMENT_MASTER = "instrument_master"
    TRADING_CALENDAR = "trading_calendar"
    DAILY_BARS = "daily_bars"
    CORPORATE_ACTIONS = "corporate_actions"
    ADJUSTMENT_FACTORS = "adjustment_factors"
    VALUATION_SNAPSHOT = "valuation_snapshot"
    CAPITAL_FLOW_SNAPSHOT = "capital_flow_snapshot"
    NORTHBOUND_FLOW_SNAPSHOT = "northbound_flow_snapshot"
    TURNOVER_LIQUIDITY_SNAPSHOT = "turnover_liquidity_snapshot"
    DATA_QUALITY_REPORT = "data_quality_report"
    INDEX_DAILY_BARS = "index_daily_bars"
    INDEX_CONSTITUENTS = "index_constituents"
    INDEX_WEIGHT_HISTORY = "index_weight_history"
    FUND_PROFILE = "fund_profile"
    FUND_NAV_SNAPSHOT = "fund_nav_snapshot"
    FUND_HOLDINGS = "fund_holdings"
    FUND_SCALE_SHARE_SNAPSHOT = "fund_scale_share_snapshot"
    FUND_PREMIUM_DISCOUNT = "fund_premium_discount"
    SECTOR_MASTER = "sector_master"
    SECTOR_MEMBERSHIP = "sector_membership"
    SECTOR_DAILY_BARS = "sector_daily_bars"
    MACRO_INDICATOR_MASTER = "macro_indicator_master"
    MACRO_OBSERVATIONS = "macro_observations"
    POLICY_DOCUMENTS = "policy_documents"
    NEWS_EVENTS = "news_events"
    COMPANY_ANNOUNCEMENTS = "company_announcements"
    GLOBAL_EQUITY_SNAPSHOT = "global_equity_snapshot"
    MINUTE_BARS = "minute_bars"
    LIMIT_UP_DOWN_EVENTS = "limit_up_down_events"
    SUSPENSION_RESUMPTION_EVENTS = "suspension_resumption_events"
    INSTRUMENT_STATUS_HISTORY = "instrument_status_history"
    MARGIN_FINANCING_LENDING = "margin_financing_lending"
    FINANCIAL_STATEMENTS = "financial_statements"
    FINANCIAL_INDICATORS = "financial_indicators"
    MAJOR_ACTIVITY_EVENTS = "major_activity_events"
    FUND_FLOW = "fund_flow"


@dataclass(frozen=True)
class DatasetInfo:
    """Minimal metadata for dataset contract tracking."""

    name: DatasetName
    schema_version: str
    description: str


@dataclass(frozen=True)
class FieldSpec:
    """Field-level schema metadata for a dataset contract."""

    name: str
    dtype: str = "any"
    required: bool = True
    description: str = ""


@dataclass(frozen=True)
class ValidationIssue:
    """Simple validation issue for offline contract checks."""

    field: str
    code: str
    message: str


@dataclass(frozen=True)
class SemanticRuleSet:
    """Explicit semantic validation rules for one dataset contract."""

    nonempty_required_strings: tuple[str, ...] = ()
    nonnegative_numeric_fields: tuple[str, ...] = ()
    weight_percentage_fields: tuple[str, ...] = ()
    ohlc_pairs: tuple[tuple[str, str], ...] = ()
    ordered_date_pairs: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class DatasetSchema:
    """Versioned schema contract for one dataset."""

    dataset: DatasetName
    schema_version: str
    fields: tuple[FieldSpec, ...]

    def field_names(self) -> tuple[str, ...]:
        return tuple(field.name for field in self.fields)

    def required_fields(self) -> tuple[str, ...]:
        return tuple(field.name for field in self.fields if field.required)

    def validate_required_fields(self, record: Mapping[str, Any]) -> tuple[str, ...]:
        """Return required field names missing in one in-memory record."""
        missing: list[str] = []
        for field in self.fields:
            if field.required and field.name not in record:
                missing.append(field.name)
        return tuple(missing)

    def validate_types(self, record: Mapping[str, Any]) -> tuple[ValidationIssue, ...]:
        """Return structured type mismatch issues for one in-memory record."""
        issues: list[ValidationIssue] = []
        for field in self.fields:
            if field.name not in record:
                continue

            value = record[field.name]
            if self._value_matches_dtype(value=value, dtype=field.dtype):
                continue

            issues.append(
                ValidationIssue(
                    field=field.name,
                    code="type_mismatch",
                    message=(
                        f"Field {field.name!r} expects dtype={field.dtype}, "
                        f"got value={value!r} ({type(value).__name__})"
                    ),
                )
            )
        return tuple(issues)

    def _value_matches_dtype(self, *, value: Any, dtype: str) -> bool:
        if dtype == "any":
            return True
        if dtype == "str":
            return isinstance(value, str)
        if dtype == "bool":
            return isinstance(value, bool)
        if dtype == "float":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        if dtype == "date":
            return self._is_date_value(value)
        if dtype == "datetime":
            return self._is_datetime_value(value)
        return False

    def _is_date_value(self, value: Any) -> bool:
        if isinstance(value, date) and not isinstance(value, datetime):
            return True
        if not isinstance(value, str):
            return False
        try:
            date.fromisoformat(value)
        except ValueError:
            return False
        return True

    def _is_datetime_value(self, value: Any) -> bool:
        if isinstance(value, datetime):
            return True
        if not isinstance(value, str):
            return False
        try:
            datetime.fromisoformat(value)
        except ValueError:
            return False
        return True


class DatasetRegistry:
    """In-memory registry for known datasets, versions, and schema contracts."""

    def __init__(self) -> None:
        self._datasets: dict[DatasetName, DatasetInfo] = {
            DatasetName.INSTRUMENT_MASTER: DatasetInfo(
                name=DatasetName.INSTRUMENT_MASTER,
                schema_version="v1",
                description="Canonical instrument reference records.",
            ),
            DatasetName.TRADING_CALENDAR: DatasetInfo(
                name=DatasetName.TRADING_CALENDAR,
                schema_version="v1",
                description="Market open or close calendar records.",
            ),
            DatasetName.DAILY_BARS: DatasetInfo(
                name=DatasetName.DAILY_BARS,
                schema_version="v1",
                description="Normalized daily OHLCV dataset.",
            ),
            DatasetName.CORPORATE_ACTIONS: DatasetInfo(
                name=DatasetName.CORPORATE_ACTIONS,
                schema_version="v1",
                description="Corporate-action source-fact events with explicit event-family semantics.",
            ),
            DatasetName.ADJUSTMENT_FACTORS: DatasetInfo(
                name=DatasetName.ADJUSTMENT_FACTORS,
                schema_version="v1",
                description="A-share adjustment-factor source-fact records by factor date.",
            ),
            DatasetName.VALUATION_SNAPSHOT: DatasetInfo(
                name=DatasetName.VALUATION_SNAPSHOT,
                schema_version="v1",
                description="Valuation metrics by trade date.",
            ),
            DatasetName.CAPITAL_FLOW_SNAPSHOT: DatasetInfo(
                name=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                schema_version="v1",
                description="Capital flow metrics by trade date.",
            ),
            DatasetName.NORTHBOUND_FLOW_SNAPSHOT: DatasetInfo(
                name=DatasetName.NORTHBOUND_FLOW_SNAPSHOT,
                schema_version="v1",
                description=(
                    "A-share northbound holding and daily-change source-fact "
                    "records by symbol and trade date."
                ),
            ),
            DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT: DatasetInfo(
                name=DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT,
                schema_version="v1",
                description=(
                    "Daily turnover and liquidity source-fact records by "
                    "symbol and trade date."
                ),
            ),
            DatasetName.DATA_QUALITY_REPORT: DatasetInfo(
                name=DatasetName.DATA_QUALITY_REPORT,
                schema_version="v1",
                description="Data quality check outcomes.",
            ),
            DatasetName.INDEX_DAILY_BARS: DatasetInfo(
                name=DatasetName.INDEX_DAILY_BARS,
                schema_version="v1",
                description="Normalized daily OHLCV data for market indexes.",
            ),
            DatasetName.INDEX_CONSTITUENTS: DatasetInfo(
                name=DatasetName.INDEX_CONSTITUENTS,
                schema_version="v1",
                description="Index membership and rebalancing records.",
            ),
            DatasetName.INDEX_WEIGHT_HISTORY: DatasetInfo(
                name=DatasetName.INDEX_WEIGHT_HISTORY,
                schema_version="v1",
                description="Index constituent weight-history source-fact records.",
            ),
            DatasetName.FUND_PROFILE: DatasetInfo(
                name=DatasetName.FUND_PROFILE,
                schema_version="v1",
                description="Fund and ETF profile reference records.",
            ),
            DatasetName.FUND_NAV_SNAPSHOT: DatasetInfo(
                name=DatasetName.FUND_NAV_SNAPSHOT,
                schema_version="v1",
                description="Fund and ETF NAV snapshots by trade date.",
            ),
            DatasetName.FUND_HOLDINGS: DatasetInfo(
                name=DatasetName.FUND_HOLDINGS,
                schema_version="v1",
                description="Fund and ETF portfolio composition snapshots.",
            ),
            DatasetName.FUND_SCALE_SHARE_SNAPSHOT: DatasetInfo(
                name=DatasetName.FUND_SCALE_SHARE_SNAPSHOT,
                schema_version="v1",
                description=(
                    "ETF/fund scale and share source-fact observations by "
                    "observation date and metric code."
                ),
            ),
            DatasetName.FUND_PREMIUM_DISCOUNT: DatasetInfo(
                name=DatasetName.FUND_PREMIUM_DISCOUNT,
                schema_version="v1",
                description="ETF/fund premium-discount source-fact metrics by trade date.",
            ),
            DatasetName.SECTOR_MASTER: DatasetInfo(
                name=DatasetName.SECTOR_MASTER,
                schema_version="v1",
                description="Industry and concept sector reference records.",
            ),
            DatasetName.SECTOR_MEMBERSHIP: DatasetInfo(
                name=DatasetName.SECTOR_MEMBERSHIP,
                schema_version="v1",
                description="Symbol-to-sector membership mapping records.",
            ),
            DatasetName.SECTOR_DAILY_BARS: DatasetInfo(
                name=DatasetName.SECTOR_DAILY_BARS,
                schema_version="v1",
                description="Industry and concept daily quote dataset.",
            ),
            DatasetName.MACRO_INDICATOR_MASTER: DatasetInfo(
                name=DatasetName.MACRO_INDICATOR_MASTER,
                schema_version="v1",
                description="Macroeconomic indicator definition metadata.",
            ),
            DatasetName.MACRO_OBSERVATIONS: DatasetInfo(
                name=DatasetName.MACRO_OBSERVATIONS,
                schema_version="v1",
                description="Macroeconomic time-series observations.",
            ),
            DatasetName.POLICY_DOCUMENTS: DatasetInfo(
                name=DatasetName.POLICY_DOCUMENTS,
                schema_version="v1",
                description="Policy document and release metadata.",
            ),
            DatasetName.NEWS_EVENTS: DatasetInfo(
                name=DatasetName.NEWS_EVENTS,
                schema_version="v1",
                description="News event metadata and lightweight linkage.",
            ),
            DatasetName.COMPANY_ANNOUNCEMENTS: DatasetInfo(
                name=DatasetName.COMPANY_ANNOUNCEMENTS,
                schema_version="v1",
                description="Listed-company announcement metadata.",
            ),
            DatasetName.GLOBAL_EQUITY_SNAPSHOT: DatasetInfo(
                name=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                schema_version="v1",
                description="Concise global equity daily snapshot dataset.",
            ),
            DatasetName.MINUTE_BARS: DatasetInfo(
                name=DatasetName.MINUTE_BARS,
                schema_version="v1",
                description="Normalized intraday minute OHLCV bars across markets.",
            ),
            DatasetName.LIMIT_UP_DOWN_EVENTS: DatasetInfo(
                name=DatasetName.LIMIT_UP_DOWN_EVENTS,
                schema_version="v1",
                description="A-share limit-up/down source-fact event snapshots.",
            ),
            DatasetName.SUSPENSION_RESUMPTION_EVENTS: DatasetInfo(
                name=DatasetName.SUSPENSION_RESUMPTION_EVENTS,
                schema_version="v1",
                description="A-share suspension and resumption source-fact events.",
            ),
            DatasetName.INSTRUMENT_STATUS_HISTORY: DatasetInfo(
                name=DatasetName.INSTRUMENT_STATUS_HISTORY,
                schema_version="v1",
                description=(
                    "Instrument lifecycle and status-history source-fact events "
                    "across listing states and risk labels."
                ),
            ),
            DatasetName.MARGIN_FINANCING_LENDING: DatasetInfo(
                name=DatasetName.MARGIN_FINANCING_LENDING,
                schema_version="v1",
                description="Margin financing and securities lending snapshots.",
            ),
            DatasetName.FINANCIAL_STATEMENTS: DatasetInfo(
                name=DatasetName.FINANCIAL_STATEMENTS,
                schema_version="v1",
                description="Cross-market periodic financial statement records.",
            ),
            DatasetName.FINANCIAL_INDICATORS: DatasetInfo(
                name=DatasetName.FINANCIAL_INDICATORS,
                schema_version="v1",
                description="Cross-market periodic financial indicator observations.",
            ),
            DatasetName.MAJOR_ACTIVITY_EVENTS: DatasetInfo(
                name=DatasetName.MAJOR_ACTIVITY_EVENTS,
                schema_version="v1",
                description="Major listed-company activity events and disclosures.",
            ),
            DatasetName.FUND_FLOW: DatasetInfo(
                name=DatasetName.FUND_FLOW,
                schema_version="v1",
                description="ETF/fund subscription-redemption and net-flow metrics.",
            ),
        }
        self._schemas: dict[DatasetName, DatasetSchema] = {
            DatasetName.INSTRUMENT_MASTER: DatasetSchema(
                dataset=DatasetName.INSTRUMENT_MASTER,
                schema_version="v1",
                fields=(
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("raw_symbol", dtype="str"),
                    FieldSpec("name", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("asset_type", dtype="str"),
                    FieldSpec("currency", dtype="str"),
                    FieldSpec("exchange", dtype="str"),
                    FieldSpec("list_date", dtype="date"),
                    FieldSpec("delist_date", dtype="date"),
                    FieldSpec("is_active", dtype="bool"),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_route", dtype="str", required=False),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.TRADING_CALENDAR: DatasetSchema(
                dataset=DatasetName.TRADING_CALENDAR,
                schema_version="v1",
                fields=(
                    FieldSpec("market", dtype="str"),
                    FieldSpec("trade_date", dtype="date"),
                    FieldSpec("is_open", dtype="bool"),
                    FieldSpec("session_type", dtype="str"),
                    FieldSpec("previous_trade_date", dtype="date"),
                    FieldSpec("next_trade_date", dtype="date"),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.DAILY_BARS: DatasetSchema(
                dataset=DatasetName.DAILY_BARS,
                schema_version="v1",
                fields=(
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("trade_date", dtype="date"),
                    FieldSpec("open", dtype="float"),
                    FieldSpec("high", dtype="float"),
                    FieldSpec("low", dtype="float"),
                    FieldSpec("close", dtype="float"),
                    FieldSpec("volume", dtype="float"),
                    FieldSpec("amount", dtype="float"),
                    FieldSpec("adj_factor", dtype="float"),
                    FieldSpec("price_adjustment", dtype="str"),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.MINUTE_BARS: DatasetSchema(
                dataset=DatasetName.MINUTE_BARS,
                schema_version="v1",
                fields=(
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("trade_date", dtype="date"),
                    FieldSpec("bar_time", dtype="datetime"),
                    FieldSpec("open", dtype="float"),
                    FieldSpec("high", dtype="float"),
                    FieldSpec("low", dtype="float"),
                    FieldSpec("close", dtype="float"),
                    FieldSpec("volume", dtype="float"),
                    FieldSpec("amount", dtype="float", required=False),
                    FieldSpec("vwap", dtype="float", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.CORPORATE_ACTIONS: DatasetSchema(
                dataset=DatasetName.CORPORATE_ACTIONS,
                schema_version="v1",
                fields=(
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("event_date", dtype="date"),
                    FieldSpec("event_type", dtype="str"),
                    FieldSpec("action_family", dtype="str"),
                    FieldSpec("source_route", dtype="str"),
                    FieldSpec("announcement_date", dtype="date", required=False),
                    FieldSpec("record_date", dtype="date", required=False),
                    FieldSpec("ex_date", dtype="date", required=False),
                    FieldSpec("value", dtype="any"),
                    FieldSpec("raw_payload_ref", dtype="str"),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.ADJUSTMENT_FACTORS: DatasetSchema(
                dataset=DatasetName.ADJUSTMENT_FACTORS,
                schema_version="v1",
                fields=(
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("factor_date", dtype="date"),
                    FieldSpec("adjustment_basis", dtype="str"),
                    FieldSpec("adjustment_factor", dtype="float"),
                    FieldSpec("raw_payload_ref", dtype="str"),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.VALUATION_SNAPSHOT: DatasetSchema(
                dataset=DatasetName.VALUATION_SNAPSHOT,
                schema_version="v1",
                fields=(
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("trade_date", dtype="date"),
                    FieldSpec("pe_ttm", dtype="float"),
                    FieldSpec("pb", dtype="float"),
                    FieldSpec("ps_ttm", dtype="float", required=False),
                    FieldSpec("dividend_yield", dtype="float", required=False),
                    FieldSpec("market_cap", dtype="float"),
                    FieldSpec("float_market_cap", dtype="float", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_route", dtype="str", required=False),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.CAPITAL_FLOW_SNAPSHOT: DatasetSchema(
                dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                schema_version="v1",
                fields=(
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("trade_date", dtype="date"),
                    FieldSpec("net_inflow", dtype="float", required=False),
                    FieldSpec("main_net_inflow", dtype="float"),
                    FieldSpec("northbound_net_buy", dtype="float", required=False),
                    FieldSpec("turnover_rate", dtype="float", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_route", dtype="str", required=False),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.NORTHBOUND_FLOW_SNAPSHOT: DatasetSchema(
                dataset=DatasetName.NORTHBOUND_FLOW_SNAPSHOT,
                schema_version="v1",
                fields=(
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("trade_date", dtype="date"),
                    FieldSpec("northbound_shares_held", dtype="float"),
                    FieldSpec("northbound_holding_market_value", dtype="float"),
                    FieldSpec("northbound_holding_ratio_a_share_pct", dtype="float"),
                    FieldSpec("northbound_share_change", dtype="float", required=False),
                    FieldSpec("northbound_net_buy", dtype="float", required=False),
                    FieldSpec(
                        "northbound_holding_market_value_change",
                        dtype="float",
                        required=False,
                    ),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_route", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.LIMIT_UP_DOWN_EVENTS: DatasetSchema(
                dataset=DatasetName.LIMIT_UP_DOWN_EVENTS,
                schema_version="v1",
                fields=(
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("trade_date", dtype="date"),
                    FieldSpec("limit_type", dtype="str"),
                    FieldSpec("up_limit_price", dtype="float"),
                    FieldSpec("down_limit_price", dtype="float"),
                    FieldSpec("hit_limit_up", dtype="bool"),
                    FieldSpec("hit_limit_down", dtype="bool"),
                    FieldSpec("open_status", dtype="str", required=False),
                    FieldSpec("close_status", dtype="str", required=False),
                    FieldSpec("seal_status", dtype="str", required=False),
                    FieldSpec("consecutive_limit_count", dtype="float", required=False),
                    FieldSpec("event_category", dtype="str", required=False),
                    FieldSpec("raw_event_type", dtype="str", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.SUSPENSION_RESUMPTION_EVENTS: DatasetSchema(
                dataset=DatasetName.SUSPENSION_RESUMPTION_EVENTS,
                schema_version="v1",
                fields=(
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("event_date", dtype="date"),
                    FieldSpec("event_type", dtype="str"),
                    FieldSpec("start_date", dtype="date", required=False),
                    FieldSpec("end_date", dtype="date", required=False),
                    FieldSpec("reason", dtype="str", required=False),
                    FieldSpec("raw_status", dtype="str", required=False),
                    FieldSpec("exchange", dtype="str", required=False),
                    FieldSpec("board", dtype="str", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.INSTRUMENT_STATUS_HISTORY: DatasetSchema(
                dataset=DatasetName.INSTRUMENT_STATUS_HISTORY,
                schema_version="v1",
                fields=(
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("effective_start_date", dtype="date"),
                    FieldSpec("effective_end_date", dtype="date", required=False),
                    FieldSpec("status_type", dtype="str"),
                    FieldSpec("status", dtype="str"),
                    FieldSpec("raw_status", dtype="str", required=False),
                    FieldSpec("status_reason", dtype="str", required=False),
                    FieldSpec("exchange", dtype="str", required=False),
                    FieldSpec("board", dtype="str", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.MARGIN_FINANCING_LENDING: DatasetSchema(
                dataset=DatasetName.MARGIN_FINANCING_LENDING,
                schema_version="v1",
                fields=(
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("exchange", dtype="str", required=False),
                    FieldSpec("trade_date", dtype="date"),
                    FieldSpec("financing_balance", dtype="float"),
                    FieldSpec("financing_buy_amount", dtype="float", required=False),
                    FieldSpec("financing_repay_amount", dtype="float", required=False),
                    FieldSpec("securities_lending_balance", dtype="float", required=False),
                    FieldSpec("securities_lending_sell_volume", dtype="float", required=False),
                    FieldSpec("securities_lending_repay_volume", dtype="float", required=False),
                    FieldSpec("margin_balance_total", dtype="float", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_route", dtype="str", required=False),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT: DatasetSchema(
                dataset=DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT,
                schema_version="v1",
                fields=(
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("trade_date", dtype="date"),
                    FieldSpec("metric_granularity", dtype="str"),
                    FieldSpec("volume", dtype="float"),
                    FieldSpec("amount", dtype="float"),
                    FieldSpec("turnover_rate", dtype="float", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_route", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.DATA_QUALITY_REPORT: DatasetSchema(
                dataset=DatasetName.DATA_QUALITY_REPORT,
                schema_version="v1",
                fields=(
                    FieldSpec("dataset", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("trade_date", dtype="date"),
                    FieldSpec("check_name", dtype="str"),
                    FieldSpec("status", dtype="str"),
                    FieldSpec("severity", dtype="str"),
                    FieldSpec("details", dtype="any"),
                    FieldSpec("created_at", dtype="datetime"),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.INDEX_DAILY_BARS: DatasetSchema(
                dataset=DatasetName.INDEX_DAILY_BARS,
                schema_version="v1",
                fields=(
                    FieldSpec("index_code", dtype="str"),
                    FieldSpec("index_name", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("trade_date", dtype="date"),
                    FieldSpec("open", dtype="float"),
                    FieldSpec("high", dtype="float"),
                    FieldSpec("low", dtype="float"),
                    FieldSpec("close", dtype="float"),
                    FieldSpec("volume", dtype="float", required=False),
                    FieldSpec("amount", dtype="float", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.INDEX_CONSTITUENTS: DatasetSchema(
                dataset=DatasetName.INDEX_CONSTITUENTS,
                schema_version="v1",
                fields=(
                    FieldSpec("index_code", dtype="str"),
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("in_date", dtype="date"),
                    FieldSpec("out_date", dtype="date", required=False),
                    FieldSpec("weight", dtype="float", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.INDEX_WEIGHT_HISTORY: DatasetSchema(
                dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                schema_version="v1",
                fields=(
                    FieldSpec("index_code", dtype="str"),
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("effective_date", dtype="date"),
                    FieldSpec("weight", dtype="float"),
                    FieldSpec("weight_unit", dtype="str", required=False),
                    FieldSpec("rebalance_date", dtype="date", required=False),
                    FieldSpec("out_date", dtype="date", required=False),
                    FieldSpec("source_route", dtype="str", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.FUND_PROFILE: DatasetSchema(
                dataset=DatasetName.FUND_PROFILE,
                schema_version="v1",
                fields=(
                    FieldSpec("fund_code", dtype="str"),
                    FieldSpec("fund_name", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("fund_type", dtype="str"),
                    FieldSpec("management_company", dtype="str"),
                    FieldSpec("inception_date", dtype="date"),
                    FieldSpec("currency", dtype="str"),
                    FieldSpec("benchmark", dtype="str", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.FUND_NAV_SNAPSHOT: DatasetSchema(
                dataset=DatasetName.FUND_NAV_SNAPSHOT,
                schema_version="v1",
                fields=(
                    FieldSpec("fund_code", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("trade_date", dtype="date"),
                    FieldSpec("nav", dtype="float"),
                    FieldSpec("accumulated_nav", dtype="float", required=False),
                    FieldSpec("shares_outstanding", dtype="float", required=False),
                    FieldSpec("fund_scale", dtype="float", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.FUND_HOLDINGS: DatasetSchema(
                dataset=DatasetName.FUND_HOLDINGS,
                schema_version="v1",
                fields=(
                    FieldSpec("fund_code", dtype="str"),
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("report_date", dtype="date"),
                    FieldSpec("weight", dtype="float"),
                    FieldSpec("shares", dtype="float", required=False),
                    FieldSpec("position_value", dtype="float", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.FUND_SCALE_SHARE_SNAPSHOT: DatasetSchema(
                dataset=DatasetName.FUND_SCALE_SHARE_SNAPSHOT,
                schema_version="v1",
                fields=(
                    FieldSpec("fund_code", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("observation_date", dtype="date"),
                    FieldSpec("observation_type", dtype="str"),
                    FieldSpec("metric_code", dtype="str"),
                    FieldSpec("metric_value", dtype="float"),
                    FieldSpec("metric_unit", dtype="str", required=False),
                    FieldSpec("value_currency", dtype="str", required=False),
                    FieldSpec("source_route", dtype="str", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.FUND_PREMIUM_DISCOUNT: DatasetSchema(
                dataset=DatasetName.FUND_PREMIUM_DISCOUNT,
                schema_version="v1",
                fields=(
                    FieldSpec("fund_code", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("trade_date", dtype="date"),
                    FieldSpec("market_price", dtype="float", required=False),
                    FieldSpec("nav", dtype="float", required=False),
                    FieldSpec("iopv", dtype="float", required=False),
                    FieldSpec("premium_discount_rate", dtype="float"),
                    FieldSpec("premium_discount_amount", dtype="float", required=False),
                    FieldSpec("source_route", dtype="str", required=False),
                    FieldSpec("source_category", dtype="str", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.FUND_FLOW: DatasetSchema(
                dataset=DatasetName.FUND_FLOW,
                schema_version="v1",
                fields=(
                    FieldSpec("fund_code", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("trade_date", dtype="date"),
                    FieldSpec("net_inflow", dtype="float", required=False),
                    FieldSpec("subscription_amount", dtype="float", required=False),
                    FieldSpec("redemption_amount", dtype="float", required=False),
                    FieldSpec("shares_change", dtype="float", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.FINANCIAL_STATEMENTS: DatasetSchema(
                dataset=DatasetName.FINANCIAL_STATEMENTS,
                schema_version="v1",
                fields=(
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("report_period_end", dtype="date"),
                    FieldSpec("statement_type", dtype="str"),
                    FieldSpec("period_type", dtype="str"),
                    FieldSpec("source_route", dtype="str", required=False),
                    FieldSpec("currency", dtype="str", required=False),
                    FieldSpec("revenue", dtype="float", required=False),
                    FieldSpec("net_profit", dtype="float", required=False),
                    FieldSpec("total_assets", dtype="float", required=False),
                    FieldSpec("total_liabilities", dtype="float", required=False),
                    FieldSpec("net_cash_operating", dtype="float", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.FINANCIAL_INDICATORS: DatasetSchema(
                dataset=DatasetName.FINANCIAL_INDICATORS,
                schema_version="v1",
                fields=(
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("report_period_end", dtype="date"),
                    FieldSpec("period_type", dtype="str"),
                    FieldSpec("metric_code", dtype="str"),
                    FieldSpec("metric_name", dtype="str", required=False),
                    FieldSpec("metric_value", dtype="float"),
                    FieldSpec("unit", dtype="str", required=False),
                    FieldSpec("source_route", dtype="str", required=False),
                    FieldSpec("metric_family", dtype="str", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.MAJOR_ACTIVITY_EVENTS: DatasetSchema(
                dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                schema_version="v1",
                fields=(
                    FieldSpec("event_id", dtype="str"),
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("event_date", dtype="date"),
                    FieldSpec("event_type", dtype="str"),
                    FieldSpec("source_route", dtype="str", required=False),
                    FieldSpec("participant", dtype="str", required=False),
                    FieldSpec("direction", dtype="str", required=False),
                    FieldSpec("event_value", dtype="float", required=False),
                    FieldSpec("event_volume", dtype="float", required=False),
                    FieldSpec("summary", dtype="str", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.SECTOR_MASTER: DatasetSchema(
                dataset=DatasetName.SECTOR_MASTER,
                schema_version="v1",
                fields=(
                    FieldSpec("sector_id", dtype="str"),
                    FieldSpec("sector_name", dtype="str"),
                    FieldSpec("sector_type", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("is_active", dtype="bool"),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.SECTOR_MEMBERSHIP: DatasetSchema(
                dataset=DatasetName.SECTOR_MEMBERSHIP,
                schema_version="v1",
                fields=(
                    FieldSpec("sector_id", dtype="str"),
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("in_date", dtype="date"),
                    FieldSpec("out_date", dtype="date", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.SECTOR_DAILY_BARS: DatasetSchema(
                dataset=DatasetName.SECTOR_DAILY_BARS,
                schema_version="v1",
                fields=(
                    FieldSpec("sector_id", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("trade_date", dtype="date"),
                    FieldSpec("open", dtype="float"),
                    FieldSpec("high", dtype="float"),
                    FieldSpec("low", dtype="float"),
                    FieldSpec("close", dtype="float"),
                    FieldSpec("volume", dtype="float", required=False),
                    FieldSpec("amount", dtype="float", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.MACRO_INDICATOR_MASTER: DatasetSchema(
                dataset=DatasetName.MACRO_INDICATOR_MASTER,
                schema_version="v1",
                fields=(
                    FieldSpec("indicator_id", dtype="str"),
                    FieldSpec("indicator_name", dtype="str"),
                    FieldSpec("region", dtype="str"),
                    FieldSpec("frequency", dtype="str"),
                    FieldSpec("unit", dtype="str"),
                    FieldSpec("category", dtype="str"),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.MACRO_OBSERVATIONS: DatasetSchema(
                dataset=DatasetName.MACRO_OBSERVATIONS,
                schema_version="v1",
                fields=(
                    FieldSpec("indicator_id", dtype="str"),
                    FieldSpec("region", dtype="str"),
                    FieldSpec("observation_date", dtype="date"),
                    FieldSpec("value", dtype="float"),
                    FieldSpec("release_date", dtype="date", required=False),
                    FieldSpec("is_preliminary", dtype="bool", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.POLICY_DOCUMENTS: DatasetSchema(
                dataset=DatasetName.POLICY_DOCUMENTS,
                schema_version="v1",
                fields=(
                    FieldSpec("policy_id", dtype="str"),
                    FieldSpec("region", dtype="str"),
                    FieldSpec("publish_date", dtype="date"),
                    FieldSpec("title", dtype="str"),
                    FieldSpec("authority", dtype="str"),
                    FieldSpec("document_type", dtype="str"),
                    FieldSpec("summary", dtype="str", required=False),
                    FieldSpec("url", dtype="str", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.NEWS_EVENTS: DatasetSchema(
                dataset=DatasetName.NEWS_EVENTS,
                schema_version="v1",
                fields=(
                    FieldSpec("news_id", dtype="str"),
                    FieldSpec("region", dtype="str"),
                    FieldSpec("publish_time", dtype="datetime"),
                    FieldSpec("title", dtype="str"),
                    FieldSpec("source_name", dtype="str"),
                    FieldSpec("related_symbol", dtype="str", required=False),
                    FieldSpec("sentiment_label", dtype="str", required=False),
                    FieldSpec("summary", dtype="str", required=False),
                    FieldSpec("url", dtype="str", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.COMPANY_ANNOUNCEMENTS: DatasetSchema(
                dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                schema_version="v1",
                fields=(
                    FieldSpec("announcement_id", dtype="str"),
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("publish_time", dtype="datetime"),
                    FieldSpec("announcement_type", dtype="str"),
                    FieldSpec("title", dtype="str"),
                    FieldSpec("url", dtype="str", required=False),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_route", dtype="str", required=False),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
            DatasetName.GLOBAL_EQUITY_SNAPSHOT: DatasetSchema(
                dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                schema_version="v1",
                fields=(
                    FieldSpec("symbol", dtype="str"),
                    FieldSpec("market", dtype="str"),
                    FieldSpec("trade_date", dtype="date"),
                    FieldSpec("close", dtype="float"),
                    FieldSpec("change_pct", dtype="float"),
                    FieldSpec("currency", dtype="str"),
                    FieldSpec("exchange", dtype="str"),
                    FieldSpec("region", dtype="str"),
                    FieldSpec("source", dtype="str"),
                    FieldSpec("source_ts", dtype="datetime", required=False),
                    FieldSpec("ingested_at", dtype="datetime"),
                    FieldSpec("schema_version", dtype="str"),
                ),
            ),
        }
        self._semantic_rules: dict[DatasetName, SemanticRuleSet] = self._build_semantic_rules()
        self._ensure_schema_coverage()
        self._ensure_semantic_rule_integrity()

    def get(self, name: DatasetName) -> DatasetInfo:
        return self._datasets[name]

    def all(self) -> tuple[DatasetInfo, ...]:
        return tuple(self._datasets.values())

    def get_schema(self, name: DatasetName) -> DatasetSchema:
        return self._schemas[name]

    def all_schemas(self) -> tuple[DatasetSchema, ...]:
        return tuple(self._schemas.values())

    def get_semantic_rules(self, name: DatasetName) -> SemanticRuleSet:
        return self._semantic_rules[name]

    def all_semantic_rules(self) -> tuple[tuple[DatasetName, SemanticRuleSet], ...]:
        return tuple(self._semantic_rules.items())

    def validate_required_fields(
        self,
        dataset: DatasetName,
        record: Mapping[str, Any],
    ) -> tuple[str, ...]:
        """Validate one in-memory record and report missing required fields."""
        return self.get_schema(dataset).validate_required_fields(record)

    def validate_record(
        self,
        dataset: DatasetName,
        record: Mapping[str, Any],
    ) -> tuple[ValidationIssue, ...]:
        """Return lightweight validation issues for required fields and dtypes."""
        schema = self.get_schema(dataset)
        missing = self.validate_required_fields(dataset, record)
        issues = list(
            ValidationIssue(
                field=field,
                code="missing_required_field",
                message=f"Required field is missing: {field}",
            )
            for field in missing
        )
        issues.extend(schema.validate_types(record))
        issues.extend(self._validate_semantics(dataset=dataset, schema=schema, record=record))
        return tuple(issues)

    def validate_records(
        self,
        dataset: DatasetName,
        records: list[Mapping[str, Any]],
    ) -> tuple[tuple[ValidationIssue, ...], ...]:
        """Validate a batch of records and return per-record issues."""
        return tuple(self.validate_record(dataset, record) for record in records)

    def _ensure_schema_coverage(self) -> None:
        dataset_names = set(self._datasets)
        schema_names = set(self._schemas)
        if dataset_names != schema_names:
            missing_schemas = sorted(name.value for name in dataset_names - schema_names)
            extra_schemas = sorted(name.value for name in schema_names - dataset_names)
            raise ValueError(
                "Dataset schema coverage mismatch: "
                f"missing={missing_schemas}, extra={extra_schemas}"
            )

        for name, info in self._datasets.items():
            schema = self._schemas[name]
            if schema.schema_version != info.schema_version:
                raise ValueError(
                    f"Schema version mismatch for {name.value}: "
                    f"info={info.schema_version}, schema={schema.schema_version}"
                )

    def _ensure_semantic_rule_integrity(self) -> None:
        for dataset, rules in self._semantic_rules.items():
            if dataset not in self._schemas:
                raise ValueError(
                    "Semantic rule integrity check failed: "
                    f"dataset={dataset!r}, rule=dataset_registration, field=<dataset>"
                )

            schema = self._schemas[dataset]
            fields_by_name = {field.name: field for field in schema.fields}

            self._check_rule_fields(
                dataset=dataset,
                rule_name="nonempty_required_strings",
                field_names=rules.nonempty_required_strings,
                fields_by_name=fields_by_name,
                expected_dtypes={"str"},
                require_required=True,
            )
            self._check_rule_fields(
                dataset=dataset,
                rule_name="nonnegative_numeric_fields",
                field_names=rules.nonnegative_numeric_fields,
                fields_by_name=fields_by_name,
                expected_dtypes={"float"},
            )
            self._check_rule_fields(
                dataset=dataset,
                rule_name="weight_percentage_fields",
                field_names=rules.weight_percentage_fields,
                fields_by_name=fields_by_name,
                expected_dtypes={"float"},
            )

            for high_field, low_field in rules.ohlc_pairs:
                self._check_rule_fields(
                    dataset=dataset,
                    rule_name="ohlc_pairs",
                    field_names=(high_field, low_field),
                    fields_by_name=fields_by_name,
                    expected_dtypes={"float"},
                )

            for in_date_field, out_date_field in rules.ordered_date_pairs:
                self._check_rule_fields(
                    dataset=dataset,
                    rule_name="ordered_date_pairs",
                    field_names=(in_date_field, out_date_field),
                    fields_by_name=fields_by_name,
                    expected_dtypes={"date", "datetime"},
                )

    def _check_rule_fields(
        self,
        *,
        dataset: DatasetName,
        rule_name: str,
        field_names: tuple[str, ...],
        fields_by_name: dict[str, FieldSpec],
        expected_dtypes: set[str],
        require_required: bool = False,
    ) -> None:
        for field_name in field_names:
            if field_name not in fields_by_name:
                raise ValueError(
                    "Semantic rule integrity check failed: "
                    f"dataset={dataset.value}, rule={rule_name}, field={field_name}, reason=unknown_field"
                )

            field_spec = fields_by_name[field_name]
            if field_spec.dtype not in expected_dtypes:
                allowed = ",".join(sorted(expected_dtypes))
                raise ValueError(
                    "Semantic rule integrity check failed: "
                    f"dataset={dataset.value}, rule={rule_name}, field={field_name}, "
                    f"reason=dtype_mismatch, expected={allowed}, actual={field_spec.dtype}"
                )

            if require_required and not field_spec.required:
                raise ValueError(
                    "Semantic rule integrity check failed: "
                    f"dataset={dataset.value}, rule={rule_name}, field={field_name}, "
                    "reason=must_be_required"
                )

    def _build_semantic_rules(self) -> dict[DatasetName, SemanticRuleSet]:
        return {
            DatasetName.INSTRUMENT_MASTER: SemanticRuleSet(
                nonempty_required_strings=("symbol", "raw_symbol", "name")
            ),
            DatasetName.DAILY_BARS: SemanticRuleSet(
                nonnegative_numeric_fields=(
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "amount",
                    "adj_factor",
                ),
                ohlc_pairs=(("high", "low"),),
            ),
            DatasetName.MINUTE_BARS: SemanticRuleSet(
                nonempty_required_strings=("symbol",),
                nonnegative_numeric_fields=(
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "amount",
                    "vwap",
                ),
                ohlc_pairs=(("high", "low"),),
            ),
            DatasetName.LIMIT_UP_DOWN_EVENTS: SemanticRuleSet(
                nonempty_required_strings=("symbol", "limit_type"),
                nonnegative_numeric_fields=(
                    "up_limit_price",
                    "down_limit_price",
                    "consecutive_limit_count",
                ),
            ),
            DatasetName.SUSPENSION_RESUMPTION_EVENTS: SemanticRuleSet(
                nonempty_required_strings=("symbol", "event_type"),
                ordered_date_pairs=(("start_date", "end_date"),),
            ),
            DatasetName.INSTRUMENT_STATUS_HISTORY: SemanticRuleSet(
                nonempty_required_strings=("symbol", "market", "status_type", "status"),
                ordered_date_pairs=(("effective_start_date", "effective_end_date"),),
            ),
            DatasetName.ADJUSTMENT_FACTORS: SemanticRuleSet(
                nonempty_required_strings=("symbol", "adjustment_basis"),
                nonnegative_numeric_fields=("adjustment_factor",),
            ),
            DatasetName.VALUATION_SNAPSHOT: SemanticRuleSet(
                nonnegative_numeric_fields=("market_cap", "float_market_cap")
            ),
            DatasetName.NORTHBOUND_FLOW_SNAPSHOT: SemanticRuleSet(
                nonempty_required_strings=("symbol", "source_route"),
                nonnegative_numeric_fields=(
                    "northbound_shares_held",
                    "northbound_holding_market_value",
                    "northbound_holding_ratio_a_share_pct",
                ),
            ),
            DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT: SemanticRuleSet(
                nonempty_required_strings=("symbol", "metric_granularity", "source_route"),
                nonnegative_numeric_fields=("volume", "amount", "turnover_rate"),
            ),
            DatasetName.MARGIN_FINANCING_LENDING: SemanticRuleSet(
                nonempty_required_strings=("symbol",),
                nonnegative_numeric_fields=(
                    "financing_balance",
                    "financing_buy_amount",
                    "financing_repay_amount",
                    "securities_lending_balance",
                    "securities_lending_sell_volume",
                    "securities_lending_repay_volume",
                    "margin_balance_total",
                ),
            ),
            DatasetName.INDEX_DAILY_BARS: SemanticRuleSet(
                nonempty_required_strings=("index_code", "index_name"),
                nonnegative_numeric_fields=("open", "high", "low", "close", "volume", "amount"),
                ohlc_pairs=(("high", "low"),),
            ),
            DatasetName.INDEX_CONSTITUENTS: SemanticRuleSet(
                nonempty_required_strings=("index_code", "symbol"),
                weight_percentage_fields=("weight",),
                ordered_date_pairs=(("in_date", "out_date"),),
            ),
            DatasetName.INDEX_WEIGHT_HISTORY: SemanticRuleSet(
                nonempty_required_strings=("index_code", "symbol"),
                weight_percentage_fields=("weight",),
                ordered_date_pairs=(("effective_date", "out_date"),),
            ),
            DatasetName.FUND_PROFILE: SemanticRuleSet(
                nonempty_required_strings=("fund_code", "fund_name")
            ),
            DatasetName.FUND_NAV_SNAPSHOT: SemanticRuleSet(
                nonempty_required_strings=("fund_code",),
                nonnegative_numeric_fields=(
                    "nav",
                    "accumulated_nav",
                    "shares_outstanding",
                    "fund_scale",
                ),
            ),
            DatasetName.FUND_HOLDINGS: SemanticRuleSet(
                nonempty_required_strings=("fund_code", "symbol"),
                nonnegative_numeric_fields=("shares", "position_value"),
                weight_percentage_fields=("weight",),
            ),
            DatasetName.FUND_SCALE_SHARE_SNAPSHOT: SemanticRuleSet(
                nonempty_required_strings=(
                    "fund_code",
                    "market",
                    "observation_type",
                    "metric_code",
                ),
            ),
            DatasetName.FUND_PREMIUM_DISCOUNT: SemanticRuleSet(
                nonempty_required_strings=("fund_code",),
                nonnegative_numeric_fields=("market_price", "nav", "iopv"),
            ),
            DatasetName.FUND_FLOW: SemanticRuleSet(
                nonempty_required_strings=("fund_code",),
                nonnegative_numeric_fields=("subscription_amount", "redemption_amount"),
            ),
            DatasetName.FINANCIAL_STATEMENTS: SemanticRuleSet(
                nonempty_required_strings=("symbol", "statement_type", "period_type"),
                nonnegative_numeric_fields=("total_assets", "total_liabilities"),
            ),
            DatasetName.FINANCIAL_INDICATORS: SemanticRuleSet(
                nonempty_required_strings=("symbol", "period_type", "metric_code"),
            ),
            DatasetName.MAJOR_ACTIVITY_EVENTS: SemanticRuleSet(
                nonempty_required_strings=("event_id", "symbol", "event_type"),
                nonnegative_numeric_fields=("event_value", "event_volume"),
            ),
            DatasetName.SECTOR_MASTER: SemanticRuleSet(
                nonempty_required_strings=("sector_id", "sector_name")
            ),
            DatasetName.SECTOR_MEMBERSHIP: SemanticRuleSet(
                nonempty_required_strings=("sector_id", "symbol"),
                ordered_date_pairs=(("in_date", "out_date"),),
            ),
            DatasetName.SECTOR_DAILY_BARS: SemanticRuleSet(
                nonempty_required_strings=("sector_id",),
                nonnegative_numeric_fields=("open", "high", "low", "close", "volume", "amount"),
                ohlc_pairs=(("high", "low"),),
            ),
            DatasetName.MACRO_INDICATOR_MASTER: SemanticRuleSet(
                nonempty_required_strings=("indicator_id", "indicator_name")
            ),
            DatasetName.MACRO_OBSERVATIONS: SemanticRuleSet(
                nonempty_required_strings=("indicator_id",),
            ),
            DatasetName.POLICY_DOCUMENTS: SemanticRuleSet(
                nonempty_required_strings=("policy_id", "title")
            ),
            DatasetName.NEWS_EVENTS: SemanticRuleSet(
                nonempty_required_strings=("news_id", "title")
            ),
            DatasetName.COMPANY_ANNOUNCEMENTS: SemanticRuleSet(
                nonempty_required_strings=("announcement_id", "symbol", "title")
            ),
            DatasetName.GLOBAL_EQUITY_SNAPSHOT: SemanticRuleSet(
                nonempty_required_strings=("symbol",),
                nonnegative_numeric_fields=("close",),
            ),
        }

    def _validate_semantics(
        self,
        *,
        dataset: DatasetName,
        schema: DatasetSchema,
        record: Mapping[str, Any],
    ) -> list[ValidationIssue]:
        rules = self.get_semantic_rules(dataset) if dataset in self._semantic_rules else SemanticRuleSet()
        issues: list[ValidationIssue] = []
        issues.extend(self._validate_schema_version(schema=schema, record=record))
        issues.extend(
            self._validate_explicit_nonempty_string_fields(
                schema=schema,
                rules=rules,
                record=record,
            )
        )
        issues.extend(self._validate_ohlc_ranges(rules=rules, record=record))
        issues.extend(self._validate_nonnegative_fields(rules=rules, record=record))
        issues.extend(self._validate_weight_range(rules=rules, record=record))
        issues.extend(self._validate_date_ranges(rules=rules, record=record))
        if dataset == DatasetName.FUND_SCALE_SHARE_SNAPSHOT:
            issues.extend(self._validate_fund_scale_share_metric_value(record=record))
        return issues

    def _validate_schema_version(
        self,
        *,
        schema: DatasetSchema,
        record: Mapping[str, Any],
    ) -> list[ValidationIssue]:
        value = record.get("schema_version")
        if value is None or not isinstance(value, str):
            return []
        if value == schema.schema_version:
            return []
        return [
            ValidationIssue(
                field="schema_version",
                code="schema_version_mismatch",
                message=(
                    f"schema_version={value!r} does not match expected "
                    f"{schema.schema_version!r}"
                ),
            )
        ]

    def _validate_explicit_nonempty_string_fields(
        self,
        *,
        schema: DatasetSchema,
        rules: SemanticRuleSet,
        record: Mapping[str, Any],
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        required_string_fields = {
            field.name
            for field in schema.fields
            if field.required and field.dtype == "str"
        }
        explicit_rule_fields = {
            field_name
            for field_name in rules.nonempty_required_strings
            if field_name in required_string_fields
        }

        for field_name in explicit_rule_fields:
            if field_name not in record:
                continue
            value = record.get(field_name)
            if not isinstance(value, str):
                continue
            if value.strip() != "":
                continue
            issues.append(
                ValidationIssue(
                    field=field_name,
                    code="empty_required_identifier",
                    message=f"Required explicit non-empty field is empty: {field_name}",
                )
            )
        return issues

    def _validate_ohlc_ranges(
        self,
        *,
        rules: SemanticRuleSet,
        record: Mapping[str, Any],
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for high_field, low_field in rules.ohlc_pairs:
            high = self._to_number(record.get(high_field))
            low = self._to_number(record.get(low_field))
            if high is None or low is None:
                continue
            if high >= low:
                continue
            issues.append(
                ValidationIssue(
                    field=high_field,
                    code="invalid_price_range",
                    message=f"{high_field} ({high}) must be greater than or equal to {low_field} ({low})",
                )
            )
        return issues

    def _validate_nonnegative_fields(
        self,
        *,
        rules: SemanticRuleSet,
        record: Mapping[str, Any],
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for field_name in rules.nonnegative_numeric_fields:
            if field_name not in record:
                continue
            value = self._to_number(record.get(field_name))
            if value is None or value >= 0:
                continue
            issues.append(
                ValidationIssue(
                    field=field_name,
                    code="negative_value",
                    message=f"{field_name} must be nonnegative, got {value}",
                )
            )
        return issues

    def _validate_weight_range(
        self,
        *,
        rules: SemanticRuleSet,
        record: Mapping[str, Any],
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for field_name in rules.weight_percentage_fields:
            if field_name not in record:
                continue
            weight = self._to_number(record.get(field_name))
            if weight is None:
                continue
            if 0 <= weight <= 100:
                continue
            issues.append(
                ValidationIssue(
                    field=field_name,
                    code="weight_out_of_range",
                    message=f"{field_name} must be within [0, 100], got {weight}",
                )
            )
        return issues

    def _validate_fund_scale_share_metric_value(
        self,
        *,
        record: Mapping[str, Any],
    ) -> list[ValidationIssue]:
        value = self._to_number(record.get("metric_value"))
        if value is None or value >= 0:
            return []

        metric_code = self._normalize_metric_token(record.get("metric_code"))
        observation_type = self._normalize_metric_token(record.get("observation_type"))
        if "change" in metric_code or "change" in observation_type:
            return []
        return [
            ValidationIssue(
                field="metric_value",
                code="negative_value",
                message=(
                    "metric_value must be nonnegative for non-change "
                    f"fund scale/share metrics, got {value}"
                ),
            )
        ]

    def _validate_date_ranges(
        self,
        *,
        rules: SemanticRuleSet,
        record: Mapping[str, Any],
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for in_date_field, out_date_field in rules.ordered_date_pairs:
            in_date = self._to_date(record.get(in_date_field))
            out_date = self._to_date(record.get(out_date_field))
            if in_date is None or out_date is None:
                continue
            if out_date >= in_date:
                continue
            issues.append(
                ValidationIssue(
                    field=out_date_field,
                    code="invalid_date_range",
                    message=(
                        f"{out_date_field} ({out_date.isoformat()}) must be greater than or equal to "
                        f"{in_date_field} ({in_date.isoformat()})"
                    ),
                )
            )
        return issues

    def _to_number(self, value: Any) -> float | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        return None

    def _to_date(self, value: Any) -> date | None:
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if not isinstance(value, str):
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None

    def _normalize_metric_token(self, value: Any) -> str:
        if not isinstance(value, str):
            return ""
        normalized = value.strip().lower()
        for char in ("-", " ", "/"):
            normalized = normalized.replace(char, "_")
        return normalized
