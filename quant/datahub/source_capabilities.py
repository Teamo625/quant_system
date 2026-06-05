"""Deterministic trading-grade source capability audit for DataHub Phase 2.5."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .datasets import DatasetName
from .source_catalog import SourceCatalog, SourceStage, build_default_source_catalog


class ResearchHorizon(str, Enum):
    """Research horizon classification used by capability requirements."""

    SHORT_TERM = "short_term"
    MEDIUM_LONG_TERM = "medium_long_term"


class CapabilityDomain(str, Enum):
    """Capability domain classification used by the Phase 2.5 audit."""

    A_SHARE = "a_share"
    HONG_KONG = "hong_kong"
    ETF_FUND = "etf_fund"
    INDEX = "index"
    SECTOR_CONCEPT = "sector_concept"
    MACRO = "macro"
    POLICY_NEWS_ANNOUNCEMENT = "policy_news_announcement"
    SOURCE_QUALITY = "source_quality"


class CapabilityStatus(str, Enum):
    """Current capability state in the trading-grade source readiness audit."""

    COVERED = "covered"
    PARTIAL = "partial"
    MISSING = "missing"
    PLANNED = "planned"


class CapabilityRequirement(str, Enum):
    """Requirement level of one source capability."""

    REQUIRED = "required"
    OPTIONAL = "optional"


@dataclass(frozen=True)
class SourceCapability:
    """One auditable source capability requirement entry."""

    capability_id: str
    capability_name: str
    horizons: tuple[ResearchHorizon, ...]
    domain: CapabilityDomain
    granularity: str
    requirement: CapabilityRequirement
    dataset_mappings: tuple[DatasetName, ...]
    source_family_ids: tuple[str, ...]
    status: CapabilityStatus
    gap_reason: str
    recommended_handoff_theme: str


DEFAULT_REQUIRED_SOURCE_CAPABILITIES: tuple[SourceCapability, ...] = (
    SourceCapability(
        capability_id="a_share_universe_reference",
        capability_name="A-share reference universe",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.A_SHARE,
        granularity="instrument-level reference snapshot",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.INSTRUMENT_MASTER,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.COVERED,
        gap_reason="",
        recommended_handoff_theme="",
    ),
    SourceCapability(
        capability_id="a_share_listing_delisting_st_status",
        capability_name="A-share listing, delisting, and ST status",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.A_SHARE,
        granularity="instrument lifecycle and status history",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.INSTRUMENT_STATUS_HISTORY,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare bounded coverage now proves listing dates, terminal "
            "delisting dates, current normal/ST snapshots, and SZ short-name status "
            "deltas for caller-provided symbols, but full dated ST/*ST continuity and "
            "broader lifecycle taxonomy remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand dated ST/*ST continuity and broader lifecycle taxonomy for "
            "A-share instrument-status-history coverage"
        ),
    ),
    SourceCapability(
        capability_id="a_share_trading_calendar",
        capability_name="A-share trading calendar",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.A_SHARE,
        granularity="exchange-session daily schedule",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.TRADING_CALENDAR,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.COVERED,
        gap_reason="",
        recommended_handoff_theme="",
    ),
    SourceCapability(
        capability_id="a_share_suspension_resumption",
        capability_name="A-share suspension and resumption events",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.A_SHARE,
        granularity="event-level timeline",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.SUSPENSION_RESUMPTION_EVENTS,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare bounded suspension-table coverage is validated, but "
            "trading-grade breadth, exact resumption confirmation, and taxonomy depth "
            "remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand A-share suspension/resumption breadth and confirm resumption taxonomy "
            "coverage"
        ),
    ),
    SourceCapability(
        capability_id="a_share_daily_bars",
        capability_name="A-share daily bars",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.A_SHARE,
        granularity="symbol x trading-day OHLCV",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.DAILY_BARS,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.COVERED,
        gap_reason="",
        recommended_handoff_theme="",
    ),
    SourceCapability(
        capability_id="a_share_minute_bars",
        capability_name="A-share minute bars",
        horizons=(ResearchHorizon.SHORT_TERM,),
        domain=CapabilityDomain.A_SHARE,
        granularity="intraday minute OHLCV",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.MINUTE_BARS,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare now supports caller-provided multi-symbol bounded "
            "date-window minute-bar access, but broader intraday history continuity "
            "and trading-grade source breadth remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand A-share minute-bars history continuity and broader public-source "
            "breadth beyond bounded date-window coverage"
        ),
    ),
    SourceCapability(
        capability_id="a_share_adjustment_factors",
        capability_name="A-share adjustment factors",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.A_SHARE,
        granularity="symbol x date adjustment factor",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.CORPORATE_ACTIONS,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.PARTIAL,
        gap_reason="Adjustment-factor specific contract is merged into generic corporate actions.",
        recommended_handoff_theme="separate adjustment-factor contract fields or dedicated dataset",
    ),
    SourceCapability(
        capability_id="a_share_corporate_actions",
        capability_name="A-share corporate actions",
        horizons=(ResearchHorizon.MEDIUM_LONG_TERM, ResearchHorizon.SHORT_TERM),
        domain=CapabilityDomain.A_SHARE,
        granularity="event-level corporate actions",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.CORPORATE_ACTIONS,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.PARTIAL,
        gap_reason="Breadth across split/dividend/rights event families remains incomplete.",
        recommended_handoff_theme="corporate-actions event taxonomy completion",
    ),
    SourceCapability(
        capability_id="a_share_valuation_history",
        capability_name="A-share valuation history",
        horizons=(ResearchHorizon.MEDIUM_LONG_TERM, ResearchHorizon.SHORT_TERM),
        domain=CapabilityDomain.A_SHARE,
        granularity="symbol x date valuation series",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.VALUATION_SNAPSHOT,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare now supports caller-provided multi-symbol bounded near-year "
            "valuation date windows, but longer history breadth and standardized "
            "pagination beyond the bounded route remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand valuation history breadth beyond bounded near-year public coverage"
        ),
    ),
    SourceCapability(
        capability_id="a_share_capital_flow",
        capability_name="A-share capital flow",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.A_SHARE,
        granularity="symbol x date capital flow metrics",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.CAPITAL_FLOW_SNAPSHOT,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare now supports caller-provided multi-symbol capital-flow "
            "batches with deterministic bounded date-window filtering, but broader "
            "historical continuity and latest-only fallback dependence remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand capital-flow history continuity beyond bounded public routes and "
            "latest-snapshot fallback coverage"
        ),
    ),
    SourceCapability(
        capability_id="a_share_northbound_flow",
        capability_name="A-share northbound flow",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.A_SHARE,
        granularity="market/date northbound net buy metrics",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.CAPITAL_FLOW_SNAPSHOT,),
        source_family_ids=("tushare_pro_cn_core",),
        status=CapabilityStatus.PARTIAL,
        gap_reason="Northbound-specific fields are not guaranteed as a dedicated contract slice.",
        recommended_handoff_theme="add dedicated northbound-flow contract profile",
    ),
    SourceCapability(
        capability_id="a_share_turnover_liquidity",
        capability_name="A-share turnover and liquidity",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.A_SHARE,
        granularity="symbol x date turnover/liquidity metrics",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.DAILY_BARS, DatasetName.CAPITAL_FLOW_SNAPSHOT),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.PARTIAL,
        gap_reason="Liquidity fields exist but not yet normalized into one explicit contract slice.",
        recommended_handoff_theme="turnover and liquidity canonical field set",
    ),
    SourceCapability(
        capability_id="a_share_limit_up_down",
        capability_name="A-share limit-up/limit-down",
        horizons=(ResearchHorizon.SHORT_TERM,),
        domain=CapabilityDomain.A_SHARE,
        granularity="symbol x date limit threshold and hit status",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.LIMIT_UP_DOWN_EVENTS,),
        source_family_ids=("akshare_cn_hk_public_family",),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare bounded trade-date pool routes are validated; "
            "trading-grade breadth/history coverage remains incomplete."
        ),
        recommended_handoff_theme="expand A-share limit-up/down breadth and history coverage",
    ),
    SourceCapability(
        capability_id="a_share_margin_financing_and_lending",
        capability_name="A-share margin financing and securities lending",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.A_SHARE,
        granularity="symbol x date margin balances and flows",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.MARGIN_FINANCING_LENDING,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare one-symbol adapter slice is validated; "
            "trading-grade breadth/history coverage remains incomplete."
        ),
        recommended_handoff_theme="expand A-share margin financing/lending breadth and history coverage",
    ),
    SourceCapability(
        capability_id="a_share_financial_statements",
        capability_name="A-share financial statements",
        horizons=(ResearchHorizon.MEDIUM_LONG_TERM,),
        domain=CapabilityDomain.A_SHARE,
        granularity="quarterly/annual statement-level fundamentals",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.FINANCIAL_STATEMENTS,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare caller-provided multi-symbol bounded report-period adapter slice is validated; "
            "trading-grade breadth/history coverage remains incomplete."
        ),
        recommended_handoff_theme="expand A-share financial-statements breadth and history coverage",
    ),
    SourceCapability(
        capability_id="a_share_financial_indicators",
        capability_name="A-share financial indicators",
        horizons=(ResearchHorizon.MEDIUM_LONG_TERM, ResearchHorizon.SHORT_TERM),
        domain=CapabilityDomain.A_SHARE,
        granularity="symbol x report-period indicator panel",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.FINANCIAL_INDICATORS,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare caller-provided multi-symbol bounded report-period adapter slice is validated; "
            "trading-grade breadth/history coverage remains incomplete."
        ),
        recommended_handoff_theme="expand A-share financial-indicator breadth and history coverage",
    ),
    SourceCapability(
        capability_id="a_share_company_announcements",
        capability_name="A-share company announcements",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.A_SHARE,
        granularity="announcement-level metadata and content linkage",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.COMPANY_ANNOUNCEMENTS,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare one-symbol adapter slice is validated; "
            "trading-grade breadth/history coverage remains incomplete."
        ),
        recommended_handoff_theme="expand A-share company-announcement breadth and history coverage",
    ),
    SourceCapability(
        capability_id="a_share_major_activity_events",
        capability_name="A-share major activity events (block trades, insider changes)",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.A_SHARE,
        granularity="event-level corporate activity timeline",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.MAJOR_ACTIVITY_EVENTS,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare bounded trade-date block-trade detail coverage is validated; "
            "trading-grade breadth/history and broader activity coverage remain incomplete."
        ),
        recommended_handoff_theme="expand A-share major-activity breadth and history coverage",
    ),
    SourceCapability(
        capability_id="hk_universe_reference",
        capability_name="Hong Kong stock reference universe",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.HONG_KONG,
        granularity="instrument-level reference snapshot",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.INSTRUMENT_MASTER,),
        source_family_ids=("akshare_cn_hk_public_family", "hkex_disclosure_and_calendar_family"),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare now supports caller-provided bounded multi-symbol HK stock "
            "reference batches, but full-market breadth, non-stock taxonomy coverage, "
            "and dated delisting/lifecycle metadata remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand HK universe breadth and dated delisting/lifecycle metadata coverage"
        ),
    ),
    SourceCapability(
        capability_id="hk_trading_calendar",
        capability_name="Hong Kong trading calendar",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.HONG_KONG,
        granularity="exchange-session daily schedule",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.TRADING_CALENDAR,),
        source_family_ids=("hkex_disclosure_and_calendar_family", "akshare_cn_hk_public_family"),
        status=CapabilityStatus.COVERED,
        gap_reason="",
        recommended_handoff_theme="",
    ),
    SourceCapability(
        capability_id="hk_daily_bars",
        capability_name="Hong Kong daily bars",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.HONG_KONG,
        granularity="symbol x trading-day OHLCV",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.DAILY_BARS,),
        source_family_ids=("akshare_cn_hk_public_family",),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare now supports caller-provided multi-symbol bounded "
            "date-window HK daily-bar access with bounded fallback filtering, but "
            "trading-grade breadth/history continuity and broader source redundancy "
            "remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand HK daily-bars history continuity and broader public-source "
            "redundancy beyond bounded batch coverage"
        ),
    ),
    SourceCapability(
        capability_id="hk_minute_bars",
        capability_name="Hong Kong minute bars (if available)",
        horizons=(ResearchHorizon.SHORT_TERM,),
        domain=CapabilityDomain.HONG_KONG,
        granularity="intraday minute OHLCV",
        requirement=CapabilityRequirement.OPTIONAL,
        dataset_mappings=(),
        source_family_ids=("akshare_cn_hk_public_family",),
        status=CapabilityStatus.MISSING,
        gap_reason="No stable intraday HK dataset contract is defined in DataHub.",
        recommended_handoff_theme="evaluate HK minute-bars source feasibility and contract design",
    ),
    SourceCapability(
        capability_id="hk_corporate_actions",
        capability_name="Hong Kong corporate actions",
        horizons=(ResearchHorizon.MEDIUM_LONG_TERM, ResearchHorizon.SHORT_TERM),
        domain=CapabilityDomain.HONG_KONG,
        granularity="event-level corporate actions",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.CORPORATE_ACTIONS,),
        source_family_ids=("akshare_cn_hk_public_family", "hkex_disclosure_and_calendar_family"),
        status=CapabilityStatus.PARTIAL,
        gap_reason="Coverage exists but event-family depth is not fully standardized.",
        recommended_handoff_theme="HK corporate-action taxonomy and history coverage",
    ),
    SourceCapability(
        capability_id="hk_valuation_history",
        capability_name="Hong Kong valuation history",
        horizons=(ResearchHorizon.MEDIUM_LONG_TERM, ResearchHorizon.SHORT_TERM),
        domain=CapabilityDomain.HONG_KONG,
        granularity="symbol x date valuation series",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.VALUATION_SNAPSHOT,),
        source_family_ids=("akshare_cn_hk_public_family",),
        status=CapabilityStatus.PARTIAL,
        gap_reason="Valuation snapshots exist; historical depth and field standardization are limited.",
        recommended_handoff_theme="HK valuation history contract hardening",
    ),
    SourceCapability(
        capability_id="hk_announcements_disclosures",
        capability_name="Hong Kong announcements and disclosures",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.HONG_KONG,
        granularity="announcement-level metadata and filing linkage",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.COMPANY_ANNOUNCEMENTS,),
        source_family_ids=("hkex_disclosure_and_calendar_family",),
        status=CapabilityStatus.COVERED,
        gap_reason="",
        recommended_handoff_theme="",
    ),
    SourceCapability(
        capability_id="hk_financial_data",
        capability_name="Hong Kong financial statements and indicators",
        horizons=(ResearchHorizon.MEDIUM_LONG_TERM,),
        domain=CapabilityDomain.HONG_KONG,
        granularity="periodic fundamentals panel",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(
            DatasetName.FINANCIAL_STATEMENTS,
            DatasetName.FINANCIAL_INDICATORS,
        ),
        source_family_ids=("akshare_cn_hk_public_family",),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Multi-symbol HK financial statements and indicators are implemented with bounded "
            "report-period filtering, but broader market breadth and long-history coverage remain pending."
        ),
        recommended_handoff_theme="expand HK financial market breadth and history coverage",
    ),
    SourceCapability(
        capability_id="hk_turnover_liquidity",
        capability_name="Hong Kong turnover and liquidity",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.HONG_KONG,
        granularity="symbol x date turnover/liquidity metrics",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.DAILY_BARS,),
        source_family_ids=("akshare_cn_hk_public_family",),
        status=CapabilityStatus.PARTIAL,
        gap_reason="Turnover metrics are available but not normalized as an explicit liquidity contract.",
        recommended_handoff_theme="HK liquidity canonical field definitions and checks",
    ),
    SourceCapability(
        capability_id="fund_reference",
        capability_name="ETF/fund reference metadata",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.ETF_FUND,
        granularity="instrument-level fund profile metadata",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.FUND_PROFILE,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.COVERED,
        gap_reason="",
        recommended_handoff_theme="",
    ),
    SourceCapability(
        capability_id="fund_daily_bars",
        capability_name="ETF/fund daily bars",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.ETF_FUND,
        granularity="instrument x trading-day OHLCV",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.DAILY_BARS,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare now supports caller-provided multi-symbol bounded "
            "date-window ETF daily-bar access, but broader fund breadth, longer "
            "history continuity, and non-ETF public-route coverage remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand ETF/fund daily-bars breadth and history continuity beyond bounded "
            "public exchange ETF coverage"
        ),
    ),
    SourceCapability(
        capability_id="fund_nav",
        capability_name="ETF/fund NAV",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.ETF_FUND,
        granularity="instrument x date NAV series",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.FUND_NAV_SNAPSHOT,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare now supports caller-provided multi-symbol bounded "
            "date-window ETF/fund NAV access, but broader fund breadth, longer "
            "history continuity, and non-exchange public-route coverage remain "
            "incomplete."
        ),
        recommended_handoff_theme=(
            "expand ETF/fund NAV breadth and history continuity beyond bounded "
            "public exchange ETF coverage"
        ),
    ),
    SourceCapability(
        capability_id="fund_holdings_composition",
        capability_name="ETF/fund holdings and composition",
        horizons=(ResearchHorizon.MEDIUM_LONG_TERM, ResearchHorizon.SHORT_TERM),
        domain=CapabilityDomain.ETF_FUND,
        granularity="holding-level periodic composition",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.FUND_HOLDINGS,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare now supports caller-provided multi-symbol bounded "
            "report-period fund-holdings access, but broader fund breadth, longer "
            "history continuity, and non-exchange public-route coverage remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand ETF/fund holdings breadth and history continuity beyond bounded "
            "public report-period coverage"
        ),
    ),
    SourceCapability(
        capability_id="fund_scale_and_share",
        capability_name="ETF/fund scale and share data",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.ETF_FUND,
        granularity="instrument x date AUM/share metrics",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.FUND_PROFILE, DatasetName.FUND_NAV_SNAPSHOT),
        source_family_ids=("tushare_pro_cn_core", "akshare_cn_hk_public_family"),
        status=CapabilityStatus.PARTIAL,
        gap_reason="Scale/share metrics are not a dedicated normalized contract slice.",
        recommended_handoff_theme="fund scale/share canonical schema extension",
    ),
    SourceCapability(
        capability_id="fund_flow",
        capability_name="ETF/fund flow data",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.ETF_FUND,
        granularity="instrument x date flow metrics",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.FUND_FLOW,),
        source_family_ids=("tushare_pro_cn_core", "akshare_cn_hk_public_family"),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare now supports caller-provided multi-symbol bounded "
            "date-window ETF/fund exchange scale/share slices, but broader "
            "net inflow/subscription/redemption coverage, non-exchange breadth, "
            "and longer history continuity remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand ETF/fund flow breadth beyond bounded exchange scale/share "
            "date-window slices into richer flow metrics and longer history continuity"
        ),
    ),
    SourceCapability(
        capability_id="fund_premium_discount",
        capability_name="ETF premium/discount",
        horizons=(ResearchHorizon.SHORT_TERM,),
        domain=CapabilityDomain.ETF_FUND,
        granularity="instrument x date premium-discount metrics",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.FUND_PREMIUM_DISCOUNT,),
        source_family_ids=("akshare_cn_hk_public_family",),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare now supports caller-provided multi-symbol bounded "
            "latest-available exchange ETF/fund premium-discount source facts, "
            "but broader fund breadth, longer history continuity, and non-exchange "
            "public-route redundancy remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand ETF/fund premium-discount breadth beyond bounded latest-available "
            "exchange snapshots into longer history continuity and broader public "
            "fund coverage"
        ),
    ),
    SourceCapability(
        capability_id="fund_profile_details",
        capability_name="Fund profile details",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.ETF_FUND,
        granularity="instrument-level static and slowly changing metadata",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.FUND_PROFILE,),
        source_family_ids=("akshare_cn_hk_public_family", "hkex_disclosure_and_calendar_family"),
        status=CapabilityStatus.COVERED,
        gap_reason="",
        recommended_handoff_theme="",
    ),
    SourceCapability(
        capability_id="index_daily_bars",
        capability_name="Index daily bars",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.INDEX,
        granularity="index x trading-day OHLCV",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.INDEX_DAILY_BARS,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare now supports caller-provided multi-index bounded "
            "daily-bar access for core China benchmark symbols, but broader "
            "benchmark breadth, longer history continuity, and non-mainland/global "
            "benchmark coverage remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand benchmark breadth and broader China/HK/global index daily-bar "
            "coverage beyond the bounded core benchmark slice"
        ),
    ),
    SourceCapability(
        capability_id="index_constituent_history",
        capability_name="Index constituent history",
        horizons=(ResearchHorizon.MEDIUM_LONG_TERM, ResearchHorizon.SHORT_TERM),
        domain=CapabilityDomain.INDEX,
        granularity="index x symbol membership timeline",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.INDEX_CONSTITUENTS,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare now supports caller-provided multi-index bounded constituent "
            "access for a core China benchmark slice with effective-date-like membership "
            "fields when exposed by the source, but broader benchmark breadth and long-history "
            "constituent continuity remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand benchmark breadth and longer constituent history continuity beyond "
            "the bounded core China index slice"
        ),
    ),
    SourceCapability(
        capability_id="index_weight_history",
        capability_name="Index weight history",
        horizons=(ResearchHorizon.MEDIUM_LONG_TERM, ResearchHorizon.SHORT_TERM),
        domain=CapabilityDomain.INDEX,
        granularity="index x symbol x effective-date weight",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.INDEX_WEIGHT_HISTORY,),
        source_family_ids=("tushare_pro_cn_core",),
        status=CapabilityStatus.PLANNED,
        gap_reason=(
            "A bounded Tushare Pro index weight-history adapter path exists, but "
            "credentialed live source coverage remains unproven because no "
            "TUSHARE_TOKEN-enabled live PASS has yet validated at least one "
            "INDEX_WEIGHT_HISTORY record."
        ),
        recommended_handoff_theme=(
            "run credentialed Tushare Pro index weight-history live smoke and promote "
            "only after a live PASS validates at least one bounded record"
        ),
    ),
    SourceCapability(
        capability_id="index_rebalance_effective_dates",
        capability_name="Index rebalance/effective dates",
        horizons=(ResearchHorizon.MEDIUM_LONG_TERM, ResearchHorizon.SHORT_TERM),
        domain=CapabilityDomain.INDEX,
        granularity="index-level rebalance calendar and effective timeline",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.INDEX_CONSTITUENTS,),
        source_family_ids=("akshare_cn_hk_public_family",),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare bounded constituent routes now preserve effective-date-like "
            "membership fields when exposed, but an explicit index-level rebalance calendar "
            "and guaranteed dated rebalance history are still not available in the current "
            "INDEX_CONSTITUENTS contract slice."
        ),
        recommended_handoff_theme=(
            "extend dated rebalance metadata and index-level rebalance calendar coverage "
            "when a stable public or credentialed source path is proven"
        ),
    ),
    SourceCapability(
        capability_id="index_china_hk_global_benchmarks",
        capability_name="Key China/HK/global benchmark index coverage",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.INDEX,
        granularity="benchmark family coverage map",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.INDEX_DAILY_BARS, DatasetName.GLOBAL_EQUITY_SNAPSHOT),
        source_family_ids=("akshare_cn_hk_public_family",),
        status=CapabilityStatus.PARTIAL,
        gap_reason="Current global benchmark support is concise and not yet exhaustive.",
        recommended_handoff_theme="benchmark universe definition and source-capability extension",
    ),
    SourceCapability(
        capability_id="sector_classification_master",
        capability_name="Industry/concept classification master",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.SECTOR_CONCEPT,
        granularity="sector-level metadata and taxonomy",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.SECTOR_MASTER,),
        source_family_ids=("akshare_cn_hk_public_family",),
        status=CapabilityStatus.COVERED,
        gap_reason="",
        recommended_handoff_theme="",
    ),
    SourceCapability(
        capability_id="sector_membership",
        capability_name="Sector membership mapping",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.SECTOR_CONCEPT,
        granularity="symbol x sector membership map",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.SECTOR_MEMBERSHIP,),
        source_family_ids=("akshare_cn_hk_public_family",),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare now supports caller-provided bounded multi-sector "
            "industry/concept membership batches and preserves dated membership "
            "fields when upstream rows expose them, but full history completeness "
            "and classification-version metadata remain limited."
        ),
        recommended_handoff_theme=(
            "expand sector membership history continuity and classification-version "
            "metadata coverage"
        ),
    ),
    SourceCapability(
        capability_id="sector_historical_changes",
        capability_name="Historical membership/classification changes",
        horizons=(ResearchHorizon.MEDIUM_LONG_TERM, ResearchHorizon.SHORT_TERM),
        domain=CapabilityDomain.SECTOR_CONCEPT,
        granularity="classification-change event timeline",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.SECTOR_MEMBERSHIP,),
        source_family_ids=("akshare_cn_hk_public_family",),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public sector-membership rows may expose bounded in/out dates, but "
            "explicit change-event timelines, full taxonomy history, and "
            "classification-version metadata are still incomplete."
        ),
        recommended_handoff_theme=(
            "add explicit sector membership-change timeline coverage and "
            "classification-version metadata"
        ),
    ),
    SourceCapability(
        capability_id="sector_daily_bars",
        capability_name="Sector daily bars",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.SECTOR_CONCEPT,
        granularity="sector x trading-day quote series",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.SECTOR_DAILY_BARS,),
        source_family_ids=("akshare_cn_hk_public_family",),
        status=CapabilityStatus.PARTIAL,
        gap_reason="Sector quote datasets are available with narrow sample coverage only.",
        recommended_handoff_theme="sector daily-bars breadth and continuity",
    ),
    SourceCapability(
        capability_id="macro_observations",
        capability_name="Macro observations",
        horizons=(ResearchHorizon.MEDIUM_LONG_TERM, ResearchHorizon.SHORT_TERM),
        domain=CapabilityDomain.MACRO,
        granularity="indicator x date observation series",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.MACRO_OBSERVATIONS,),
        source_family_ids=("macro_policy_public_sources",),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public China macro observation coverage is validated for a bounded set of "
            "indicators/routes only; broader indicator breadth, revision depth, and "
            "release-calendar completeness remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand macro observation breadth, revision history, and release-metadata "
            "coverage"
        ),
    ),
    SourceCapability(
        capability_id="macro_indicator_definitions",
        capability_name="Macro indicator definitions",
        horizons=(ResearchHorizon.MEDIUM_LONG_TERM,),
        domain=CapabilityDomain.MACRO,
        granularity="indicator metadata dictionary",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.MACRO_INDICATOR_MASTER,),
        source_family_ids=("macro_policy_public_sources",),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Macro indicator master coverage is implemented for a bounded China macro "
            "dictionary only; wider indicator breadth and richer release metadata remain "
            "incomplete."
        ),
        recommended_handoff_theme=(
            "expand macro indicator dictionary breadth and release-metadata coverage"
        ),
    ),
    SourceCapability(
        capability_id="macro_release_metadata",
        capability_name="Macro release metadata",
        horizons=(ResearchHorizon.MEDIUM_LONG_TERM, ResearchHorizon.SHORT_TERM),
        domain=CapabilityDomain.MACRO,
        granularity="release calendar and revision metadata",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.MACRO_INDICATOR_MASTER,),
        source_family_ids=("macro_policy_public_sources",),
        status=CapabilityStatus.PARTIAL,
        gap_reason="Release metadata is not complete as a first-class contract slice.",
        recommended_handoff_theme="extend macro indicator master with release metadata fields",
    ),
    SourceCapability(
        capability_id="policy_documents",
        capability_name="Policy documents",
        horizons=(ResearchHorizon.MEDIUM_LONG_TERM, ResearchHorizon.SHORT_TERM),
        domain=CapabilityDomain.POLICY_NEWS_ANNOUNCEMENT,
        granularity="document-level policy release metadata",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.POLICY_DOCUMENTS,),
        source_family_ids=("macro_policy_public_sources",),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public gov.cn policy-document metadata coverage is validated for selected "
            "routes only; broader authority coverage, pagination depth, and full "
            "historical completeness remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand policy-document source breadth, pagination depth, and history "
            "coverage"
        ),
    ),
    SourceCapability(
        capability_id="news_events",
        capability_name="News events",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.POLICY_NEWS_ANNOUNCEMENT,
        granularity="event-level news metadata",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.NEWS_EVENTS,),
        source_family_ids=("akshare_cn_hk_public_family",),
        status=CapabilityStatus.COVERED,
        gap_reason="",
        recommended_handoff_theme="",
    ),
    SourceCapability(
        capability_id="company_announcements_cross_market",
        capability_name="Company announcements across markets",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.POLICY_NEWS_ANNOUNCEMENT,
        granularity="announcement-level cross-market metadata",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.COMPANY_ANNOUNCEMENTS,),
        source_family_ids=("hkex_disclosure_and_calendar_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.PARTIAL,
        gap_reason="HK coverage is stronger; A-share announcement capability remains planned.",
        recommended_handoff_theme="cross-market announcement parity and normalization",
    ),
    SourceCapability(
        capability_id="source_freshness",
        capability_name="Source freshness metadata",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.SOURCE_QUALITY,
        granularity="dataset/source refresh timestamp metadata",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.DATA_QUALITY_REPORT,),
        source_family_ids=("local_data_quality_engine",),
        status=CapabilityStatus.COVERED,
        gap_reason="",
        recommended_handoff_theme="",
    ),
    SourceCapability(
        capability_id="source_coverage_metadata",
        capability_name="Source coverage metadata",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.SOURCE_QUALITY,
        granularity="dataset/source scope and completeness indicators",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.DATA_QUALITY_REPORT,),
        source_family_ids=("local_data_quality_engine",),
        status=CapabilityStatus.PARTIAL,
        gap_reason="Coverage metadata exists but requires richer capability-gap metrics.",
        recommended_handoff_theme="enhance quality report with coverage KPIs",
    ),
    SourceCapability(
        capability_id="source_availability_health",
        capability_name="Source availability health",
        horizons=(ResearchHorizon.SHORT_TERM,),
        domain=CapabilityDomain.SOURCE_QUALITY,
        granularity="source heartbeat and failure-state metadata",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.DATA_QUALITY_REPORT,),
        source_family_ids=("local_data_quality_engine",),
        status=CapabilityStatus.PARTIAL,
        gap_reason="Availability states are not yet a standardized first-class contract section.",
        recommended_handoff_theme="source health signal schema and checks",
    ),
    SourceCapability(
        capability_id="source_schema_validation",
        capability_name="Schema validation coverage",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.SOURCE_QUALITY,
        granularity="dataset-level schema/semantic validation status",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.DATA_QUALITY_REPORT,),
        source_family_ids=("local_data_quality_engine",),
        status=CapabilityStatus.COVERED,
        gap_reason="",
        recommended_handoff_theme="",
    ),
    SourceCapability(
        capability_id="source_refresh_metadata",
        capability_name="Refresh metadata and run observability",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.SOURCE_QUALITY,
        granularity="refresh-run outcome metadata",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.DATA_QUALITY_REPORT,),
        source_family_ids=("local_data_quality_engine",),
        status=CapabilityStatus.COVERED,
        gap_reason="",
        recommended_handoff_theme="",
    ),
)


class SourceCapabilityAudit:
    """Deterministic helper API over the Phase 2.5 capability matrix."""

    def __init__(
        self,
        capabilities: Iterable[SourceCapability],
        *,
        source_catalog: SourceCatalog | None = None,
    ) -> None:
        self._capabilities: tuple[SourceCapability, ...] = tuple(capabilities)
        self._source_catalog = (
            source_catalog if source_catalog is not None else build_default_source_catalog()
        )
        self._source_index = {
            source.source_id: source for source in self._source_catalog.all_sources()
        }

    def all_capabilities(
        self,
        *,
        required_only: bool = False,
    ) -> tuple[SourceCapability, ...]:
        if not required_only:
            return self._capabilities
        return tuple(
            capability
            for capability in self._capabilities
            if capability.requirement == CapabilityRequirement.REQUIRED
        )

    def required_capabilities(self) -> tuple[SourceCapability, ...]:
        return self.all_capabilities(required_only=True)

    def capabilities_by_horizon(
        self,
        horizon: ResearchHorizon,
        *,
        required_only: bool = False,
    ) -> tuple[SourceCapability, ...]:
        return tuple(
            capability
            for capability in self.all_capabilities(required_only=required_only)
            if horizon in capability.horizons
        )

    def capabilities_by_domain(
        self,
        domain: CapabilityDomain,
        *,
        required_only: bool = False,
    ) -> tuple[SourceCapability, ...]:
        return tuple(
            capability
            for capability in self.all_capabilities(required_only=required_only)
            if capability.domain == domain
        )

    def missing_capabilities(
        self,
        *,
        required_only: bool = False,
    ) -> tuple[SourceCapability, ...]:
        return tuple(
            capability
            for capability in self.all_capabilities(required_only=required_only)
            if capability.status == CapabilityStatus.MISSING
        )

    def partial_capabilities(
        self,
        *,
        required_only: bool = False,
    ) -> tuple[SourceCapability, ...]:
        return tuple(
            capability
            for capability in self.all_capabilities(required_only=required_only)
            if capability.status == CapabilityStatus.PARTIAL
        )

    def capabilities_without_dataset_mapping(
        self,
        *,
        required_only: bool = False,
    ) -> tuple[SourceCapability, ...]:
        return tuple(
            capability
            for capability in self.all_capabilities(required_only=required_only)
            if not capability.dataset_mappings
        )

    def capabilities_with_planned_or_credentialed_sources(
        self,
        *,
        required_only: bool = False,
    ) -> tuple[SourceCapability, ...]:
        gaps: list[SourceCapability] = []
        for capability in self.all_capabilities(required_only=required_only):
            for source_family_id in capability.source_family_ids:
                source = self._source_index.get(source_family_id)
                if source is None:
                    continue
                if source.stage == SourceStage.PLANNED or source.requires_credentials:
                    gaps.append(capability)
                    break
        return tuple(gaps)


def build_default_source_capability_audit() -> SourceCapabilityAudit:
    """Build the deterministic source capability matrix for TASK-041."""

    return SourceCapabilityAudit(
        capabilities=DEFAULT_REQUIRED_SOURCE_CAPABILITIES,
        source_catalog=build_default_source_catalog(),
    )


DEFAULT_SOURCE_CAPABILITY_AUDIT = build_default_source_capability_audit()


def get_required_capabilities() -> tuple[SourceCapability, ...]:
    """Return required trading-grade source capabilities."""

    return DEFAULT_SOURCE_CAPABILITY_AUDIT.required_capabilities()


def get_capabilities_by_horizon(
    horizon: ResearchHorizon,
) -> tuple[SourceCapability, ...]:
    """Return capabilities for one research horizon."""

    return DEFAULT_SOURCE_CAPABILITY_AUDIT.capabilities_by_horizon(horizon)


def get_capabilities_by_domain(
    domain: CapabilityDomain,
) -> tuple[SourceCapability, ...]:
    """Return capabilities for one market/domain area."""

    return DEFAULT_SOURCE_CAPABILITY_AUDIT.capabilities_by_domain(domain)


def get_missing_capabilities() -> tuple[SourceCapability, ...]:
    """Return missing capabilities from the default audit."""

    return DEFAULT_SOURCE_CAPABILITY_AUDIT.missing_capabilities()


def get_partial_capabilities() -> tuple[SourceCapability, ...]:
    """Return partial capabilities from the default audit."""

    return DEFAULT_SOURCE_CAPABILITY_AUDIT.partial_capabilities()


def get_capabilities_without_dataset_mapping() -> tuple[SourceCapability, ...]:
    """Return capabilities that have no stable DatasetName mapping yet."""

    return DEFAULT_SOURCE_CAPABILITY_AUDIT.capabilities_without_dataset_mapping()


def get_capabilities_with_planned_or_credentialed_sources() -> tuple[SourceCapability, ...]:
    """Return capabilities depending on planned or credentialed source families."""

    return (
        DEFAULT_SOURCE_CAPABILITY_AUDIT.capabilities_with_planned_or_credentialed_sources()
    )


__all__ = [
    "CapabilityDomain",
    "CapabilityRequirement",
    "CapabilityStatus",
    "DEFAULT_REQUIRED_SOURCE_CAPABILITIES",
    "DEFAULT_SOURCE_CAPABILITY_AUDIT",
    "ResearchHorizon",
    "SourceCapability",
    "SourceCapabilityAudit",
    "build_default_source_capability_audit",
    "get_capabilities_by_domain",
    "get_capabilities_by_horizon",
    "get_capabilities_with_planned_or_credentialed_sources",
    "get_capabilities_without_dataset_mapping",
    "get_missing_capabilities",
    "get_partial_capabilities",
    "get_required_capabilities",
]
