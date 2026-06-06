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
            "delisting dates, current normal/ST snapshots, SZ short-name status "
            "deltas, and dated suspension-to-delist lifecycle evidence where the "
            "public exchange tables expose it for caller-provided symbols, but full "
            "dated ST/*ST continuity, explicit SH terminal delist dates, and broader "
            "lifecycle taxonomy remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand dated ST/*ST continuity and broader lifecycle taxonomy for "
            "A-share instrument-status-history coverage, especially where public "
            "routes still lack explicit dated terminal lifecycle events"
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
            "Public AKShare bounded Eastmoney suspension-table coverage is validated, "
            "and Baidu trade-notify reminders now add exact announced SH/SZ resumption "
            "dates plus some Baidu-only A-share reminder breadth, but full exchange-wide "
            "breadth, exact completed resumption continuity, and deeper suspension "
            "taxonomy remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand A-share suspension/resumption breadth and completed resumption "
            "continuity beyond current Eastmoney plus Baidu public-route coverage"
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
        source_family_ids=(
            "akshare_cn_hk_public_family",
            "baostock_public_cn",
            "tushare_pro_cn_core",
        ),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare supports caller-provided multi-symbol bounded date-window "
            "minute-bar access where Eastmoney routes are reachable, and BaoStock now "
            "provides no-credential multi-symbol explicit-date-window 5/15/30/60-minute "
            "historical bars; 1-minute history, full-market breadth, full long-history "
            "continuity, and deeper source redundancy remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand A-share minute-bars 1-minute history, full-market breadth, and "
            "longer continuity beyond current AKShare/Eastmoney and BaoStock public routes"
        ),
    ),
    SourceCapability(
        capability_id="a_share_adjustment_factors",
        capability_name="A-share adjustment factors",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.A_SHARE,
        granularity="symbol x date adjustment factor",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.ADJUSTMENT_FACTORS,),
        source_family_ids=("akshare_cn_hk_public_family",),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare now exposes caller-provided multi-symbol qfq/hfq "
            "adjustment-factor change-point series through the Sina-backed "
            "factor route, but the public source does not guarantee full "
            "per-trade-date continuity and no second no-credential source has "
            "been validated yet."
        ),
        recommended_handoff_theme=(
            "expand A-share adjustment-factor continuity and public-source "
            "redundancy beyond the current AKShare/Sina factor route"
        ),
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
        gap_reason=(
            "Public AKShare now proves caller-provided dividend/cash-bonus/"
            "transfer-share distribution events plus bounded CNInfo rights-issue "
            "implementation events, but split/consolidation and broader "
            "corporate-action family breadth remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand A-share corporate-actions breadth beyond the current public "
            "dividend/distribution and rights-issue event families"
        ),
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
            "Public AKShare now supports caller-provided multi-symbol bounded valuation "
            "date windows across the public Baidu multi-period selectors plus "
            "Eastmoney dated continuity from 2018 onward, but standardized "
            "pre-2018 second-source redundancy, full-history continuity, and "
            "route-shape stability remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand valuation history continuity and pre-2018 public-source "
            "redundancy beyond the current Baidu plus Eastmoney valuation routes"
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
            "batches through the Eastmoney dated symbol-history route, but no stable "
            "second dated symbol-history route is proven and the datacenter fallback "
            "remains latest-only snapshot coverage."
        ),
        recommended_handoff_theme=(
            "expand capital-flow history continuity beyond the Eastmoney dated route "
            "and latest-only datacenter fallback coverage"
        ),
    ),
    SourceCapability(
        capability_id="a_share_northbound_flow",
        capability_name="A-share northbound flow",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.A_SHARE,
        granularity="symbol x date northbound holding and daily-change facts",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.NORTHBOUND_FLOW_SNAPSHOT,),
        source_family_ids=("akshare_cn_hk_public_family",),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare now exposes caller-provided symbol/date northbound "
            "holding snapshots plus today's增持资金/增持股数 deltas through the "
            "Eastmoney-backed stock_hsgt_individual_em route, but only one "
            "public no-credential route is proven and it does not establish "
            "market-level quota or buy/sell decomposition coverage."
        ),
        recommended_handoff_theme=(
            "expand northbound public-source redundancy and broader northbound "
            "metric coverage beyond the current stock_hsgt_individual_em route"
        ),
    ),
    SourceCapability(
        capability_id="a_share_turnover_liquidity",
        capability_name="A-share turnover and liquidity",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.A_SHARE,
        granularity="symbol x date turnover/liquidity metrics",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT,),
        source_family_ids=("akshare_cn_hk_public_family", "tushare_pro_cn_core"),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare now exposes caller-provided symbol/date bounded daily "
            "volume, amount, and turnover-rate facts through the Eastmoney-backed "
            "stock_zh_a_hist route and the canonical contract is explicit, but only "
            "one public no-credential route is proven and broader liquidity breadth, "
            "long-history continuity, and public-source redundancy remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand turnover/liquidity public-source redundancy and broader "
            "liquidity breadth beyond the current stock_zh_a_hist route"
        ),
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
            "Public AKShare now validates bounded multi-date current limit-up/current "
            "limit-down pools plus previous-day limit-up and broken-board breadth, "
            "but strong-pool/sub-new breadth, explicit route provenance in the formal "
            "contract, and longer history continuity remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand A-share limit-up/down strong-pool/sub-new breadth, explicit route "
            "provenance, and longer history continuity"
        ),
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
            "Public AKShare now supports caller-provided multi-symbol bounded "
            "date-window margin-detail history batches across the validated SSE and "
            "SZSE public routes with explicit route/exchange provenance, but no "
            "validated public BSE symbol-level margin-detail route, no symbol-compatible "
            "exchange-summary normalization path, and no proven long-history continuity "
            "beyond the current bounded detail-route iteration."
        ),
        recommended_handoff_theme=(
            "expand A-share margin financing/lending BSE-compatible public coverage, "
            "symbol-compatible exchange-summary reconciliation, and longer history continuity"
        ),
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
            "Public AKShare now validates caller-provided multi-symbol bounded "
            "report-period financial-statement history across the Sina balance-sheet, "
            "income-statement, and cash-flow families with explicit statement-type and "
            "source-route provenance, but no second no-credential public statement route, "
            "full long-history continuity, and stronger route-shape resilience are proven."
        ),
        recommended_handoff_theme=(
            "expand A-share financial-statements breadth, longer history continuity, "
            "and public-source redundancy beyond the current Sina statement families"
        ),
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
            "Public AKShare now validates caller-provided multi-symbol bounded "
            "report-period financial-indicator history through "
            "stock_financial_analysis_indicator_em with explicit source-route and "
            "indicator-family provenance, but no validated second no-credential "
            "indicator route, full long-history continuity, and full cross-industry "
            "metric-family completeness are proven."
        ),
        recommended_handoff_theme=(
            "expand A-share financial-indicator breadth, longer history continuity, "
            "and public-source redundancy beyond the current Eastmoney indicator "
            "route and currently proven indicator-family coverage"
        ),
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
            "Public AKShare caller-provided bounded multi-symbol/date-window announcement "
            "coverage with route provenance is validated; category breadth, broader "
            "history continuity, and second-route public redundancy remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand A-share company-announcement category breadth, broader history "
            "continuity, and public-source redundancy beyond the currently proven "
            "bounded AKShare routes"
        ),
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
            "Public AKShare now validates caller-provided bounded date-window block-trade "
            "detail rows plus symbol-date summary rows with explicit route provenance, but "
            "broader major-activity taxonomies, longer-history continuity, and no-credential "
            "second-source redundancy remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand A-share major-activity breadth, longer-history continuity, and public "
            "source redundancy beyond the current bounded AKShare block-trade detail and "
            "symbol-date summary routes"
        ),
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
            "reference batches with explicit stock_hk_security_profile_em provenance, "
            "and a bounded current-listed HK stock sample through Eastmoney spot-list "
            "with bounded Sina page-1 fallback plus per-symbol profile reconciliation, "
            "but the proven no-credential routes remain stock-only: typical non-stock "
            "ETF/REIT/index candidates still hard-fail under the stock profile route, "
            "the Sina page-1 sample does not expose reusable taxonomy truth, and no "
            "local AKShare HK route exposes trustworthy dated delist/inactive lifecycle "
            "metadata. Full-market breadth therefore remains incomplete."
        ),
        recommended_handoff_theme=(
            "expand HK universe breadth only if a stable no-credential HK route proves "
            "non-stock taxonomy truth and dated delisting/inactive lifecycle metadata"
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
            "date-window HK daily-bar access through stock_hk_hist, plus "
            "stock_hk_daily full-history fallback filtering when the bounded route "
            "is unavailable or returns no rows. This improves practical no-credential "
            "history continuity for HK stocks, but the proven paths remain within one "
            "AKShare source family and no independent second public HK daily-bar "
            "source is catalog-validated yet."
        ),
        recommended_handoff_theme=(
            "prove an independent no-credential HK daily-bar source or additional "
            "history continuity evidence beyond the current AKShare same-family routes"
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
        gap_reason=(
            "Public AKShare now proves one-symbol HK dividend/distribution "
            "implementation history through stock_hk_dividend_payout_em plus "
            "same-family stock_hk_fhpx_detail_ths dividend-plan and explicit "
            "dividend_no_distribution decision history, with route-distinct "
            "source truth and date-window filtering, but caller-provided "
            "multi-symbol breadth and non-dividend corporate-action families "
            "such as split/rights/consolidation remain incomplete."
        ),
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
        gap_reason=(
            "Public AKShare now supports caller-provided multi-symbol bounded dated "
            "HK PE/PB/market-cap history through stock_hk_indicator_eniu, with "
            "optional same-date Baidu ps_ttm/float-market-cap supplementation where "
            "the route is reachable, but observed public history continuity is stale "
            "through 2022-07-13 in the accepted live environment and independent "
            "current-dated public-source redundancy remains unproven."
        ),
        recommended_handoff_theme=(
            "prove current-dated HK valuation continuity and stronger second-source "
            "redundancy beyond stock_hk_indicator_eniu plus optional dated "
            "stock_hk_valuation_baidu supplementation"
        ),
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
            "Public AKShare now proves caller-provided multi-symbol HK stock "
            "financial statement and indicator report-period history through "
            "stock_financial_hk_report_em and stock_financial_hk_analysis_indicator_em, "
            "with deterministic report-period filtering, explicit source-route truth, "
            "statement-family truth, and indicator metric-family truth where stable; "
            "broader HK stock breadth beyond sampled liquid issuers, non-stock support, "
            "long-history continuity, and independent public-source redundancy remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand HK financial breadth, issuer sampling, and longer history continuity "
            "beyond the current Eastmoney report/indicator routes while preserving "
            "source-route and metric-family truth"
        ),
    ),
    SourceCapability(
        capability_id="hk_turnover_liquidity",
        capability_name="Hong Kong turnover and liquidity",
        horizons=(ResearchHorizon.SHORT_TERM, ResearchHorizon.MEDIUM_LONG_TERM),
        domain=CapabilityDomain.HONG_KONG,
        granularity="symbol x date turnover/liquidity metrics",
        requirement=CapabilityRequirement.REQUIRED,
        dataset_mappings=(DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT,),
        source_family_ids=("akshare_cn_hk_public_family",),
        status=CapabilityStatus.PARTIAL,
        gap_reason=(
            "Public AKShare now supports caller-provided multi-symbol bounded "
            "HK turnover/liquidity source-fact records through stock_hk_hist, "
            "with stock_hk_daily full-history fallback filtering when the "
            "bounded route is unavailable or empty. Proven source-backed HK "
            "liquidity facts are limited to dated volume and traded amount "
            "with explicit source-route truth; turnover-rate, float-share, "
            "spread, and independent public-source redundancy remain unproven."
        ),
        recommended_handoff_theme=(
            "expand HK turnover/liquidity breadth or public-source redundancy "
            "beyond stock_hk_hist plus stock_hk_daily, especially if stable "
            "turnover-rate or deeper microstructure facts become publicly provable"
        ),
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
            "date-window exchange ETF daily-bar access plus listed-fund/LOF "
            "daily-bar history through the same public family, but off-exchange "
            "fund breadth, longer history continuity, and broader route "
            "redundancy remain incomplete."
        ),
        recommended_handoff_theme=(
            "expand ETF/fund daily-bars breadth and history continuity beyond the "
            "current bounded exchange ETF plus listed-fund/LOF public routes"
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
        gap_reason=(
            "HK coverage is stronger; A-share announcement capability remains partial "
            "despite bounded AKShare route hardening."
        ),
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
        status=CapabilityStatus.COVERED,
        gap_reason="",
        recommended_handoff_theme="",
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
