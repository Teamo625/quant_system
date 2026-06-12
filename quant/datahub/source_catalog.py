"""DataHub comprehensive source catalog for Phase 2 coverage planning."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .datasets import DatasetName


class MarketDomain(str, Enum):
    """Required market-level domains for Phase 2 coverage."""

    A_SHARE = "a_share"
    HONG_KONG = "hong_kong"
    ETF_FUND = "etf_fund"
    INDEX = "index"
    GLOBAL_EQUITY = "global_equity"


class AssetDomain(str, Enum):
    """Required asset-level domains for Phase 2 coverage."""

    STOCK = "stock"
    ETF = "etf"
    FUND = "fund"
    INDEX = "index"
    SECTOR_CONCEPT = "sector_concept"
    MACRO_SERIES = "macro_series"
    POLICY_DOCUMENT = "policy_document"
    NEWS_EVENT = "news_event"
    ANNOUNCEMENT = "announcement"


class GeographyDomain(str, Enum):
    """Required geography coverage domains for Phase 2 coverage."""

    CN_MAINLAND = "cn_mainland"
    HONG_KONG = "hong_kong"
    GLOBAL = "global"


class InformationDomain(str, Enum):
    """Expanded information domains required by TASK-006."""

    A_SHARE_FULL_DATA = "a_share_full_data"
    HK_STOCK_FULL_DATA = "hong_kong_stock_full_data"
    ETF_FUND_FULL_DATA = "etf_and_fund_full_data"
    INDEX_DATA = "index_data"
    GLOBAL_EQUITY_CONCISE = "global_equity_concise_data"
    INDUSTRY_CONCEPT_SECTOR = "industry_concept_sector_data"
    GLOBAL_MACRO = "global_macro_data"
    CHINA_MACRO = "china_macro_data"
    POLICY = "policy_data"
    NEWS = "news_data"
    ANNOUNCEMENT = "listed_company_announcement_data"
    EXCHANGE_CALENDAR = "exchange_calendar_and_trading_schedule"
    SOURCE_HEALTH_QUALITY = "source_health_and_data_quality_metadata"


class SourceStage(str, Enum):
    """Implementation stage for one source family."""

    PLANNED = "planned"
    PRIORITIZED = "prioritized"
    READY_FOR_ADAPTER = "ready_for_adapter"


@dataclass(frozen=True)
class InformationCoverage:
    """Information-domain coverage and stable-contract linkage."""

    domain: InformationDomain
    stable_datasets: tuple[DatasetName, ...] = ()


@dataclass(frozen=True)
class SourceCatalogEntry:
    """One source family record in the catalog."""

    source_id: str
    source_name: str
    dataset_coverage: tuple[DatasetName, ...]
    information_coverage: tuple[InformationCoverage, ...]
    market_coverage: tuple[MarketDomain, ...]
    asset_coverage: tuple[AssetDomain, ...]
    geography_coverage: tuple[GeographyDomain, ...]
    requires_credentials: bool
    requires_live_network: bool
    stage: SourceStage
    priority: int
    notes: str = ""


REQUIRED_DATASETS: tuple[DatasetName, ...] = tuple(DatasetName)

REQUIRED_MARKET_DOMAINS: tuple[MarketDomain, ...] = (
    MarketDomain.A_SHARE,
    MarketDomain.HONG_KONG,
    MarketDomain.ETF_FUND,
    MarketDomain.INDEX,
    MarketDomain.GLOBAL_EQUITY,
)

REQUIRED_ASSET_DOMAINS: tuple[AssetDomain, ...] = (
    AssetDomain.STOCK,
    AssetDomain.ETF,
    AssetDomain.FUND,
    AssetDomain.INDEX,
    AssetDomain.SECTOR_CONCEPT,
    AssetDomain.MACRO_SERIES,
    AssetDomain.POLICY_DOCUMENT,
    AssetDomain.NEWS_EVENT,
    AssetDomain.ANNOUNCEMENT,
)

REQUIRED_GEOGRAPHY_DOMAINS: tuple[GeographyDomain, ...] = (
    GeographyDomain.CN_MAINLAND,
    GeographyDomain.HONG_KONG,
    GeographyDomain.GLOBAL,
)

REQUIRED_INFORMATION_DOMAINS: tuple[InformationDomain, ...] = (
    InformationDomain.A_SHARE_FULL_DATA,
    InformationDomain.HK_STOCK_FULL_DATA,
    InformationDomain.ETF_FUND_FULL_DATA,
    InformationDomain.INDEX_DATA,
    InformationDomain.GLOBAL_EQUITY_CONCISE,
    InformationDomain.INDUSTRY_CONCEPT_SECTOR,
    InformationDomain.GLOBAL_MACRO,
    InformationDomain.CHINA_MACRO,
    InformationDomain.POLICY,
    InformationDomain.NEWS,
    InformationDomain.ANNOUNCEMENT,
    InformationDomain.EXCHANGE_CALENDAR,
    InformationDomain.SOURCE_HEALTH_QUALITY,
)


DEFAULT_SOURCE_CATALOG_ENTRIES: tuple[SourceCatalogEntry, ...] = (
    SourceCatalogEntry(
        source_id="tushare_pro_cn_core",
        source_name="Tushare Pro CN Core",
        dataset_coverage=(
            DatasetName.INSTRUMENT_MASTER,
            DatasetName.TRADING_CALENDAR,
            DatasetName.DAILY_BARS,
            DatasetName.MINUTE_BARS,
            DatasetName.CORPORATE_ACTIONS,
            DatasetName.SUSPENSION_RESUMPTION_EVENTS,
            DatasetName.INSTRUMENT_STATUS_HISTORY,
            DatasetName.VALUATION_SNAPSHOT,
            DatasetName.CAPITAL_FLOW_SNAPSHOT,
            DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT,
            DatasetName.MARGIN_FINANCING_LENDING,
            DatasetName.INDEX_DAILY_BARS,
            DatasetName.INDEX_CONSTITUENTS,
            DatasetName.INDEX_WEIGHT_HISTORY,
            DatasetName.FUND_PROFILE,
            DatasetName.FUND_NAV_SNAPSHOT,
            DatasetName.FUND_HOLDINGS,
            DatasetName.FUND_SCALE_SHARE_SNAPSHOT,
            DatasetName.FUND_FLOW,
            DatasetName.FINANCIAL_STATEMENTS,
            DatasetName.FINANCIAL_INDICATORS,
            DatasetName.MAJOR_ACTIVITY_EVENTS,
        ),
        information_coverage=(
            InformationCoverage(
                InformationDomain.A_SHARE_FULL_DATA,
                stable_datasets=(
                    DatasetName.INSTRUMENT_MASTER,
                    DatasetName.DAILY_BARS,
                    DatasetName.MINUTE_BARS,
                    DatasetName.CORPORATE_ACTIONS,
                    DatasetName.SUSPENSION_RESUMPTION_EVENTS,
                    DatasetName.INSTRUMENT_STATUS_HISTORY,
                    DatasetName.VALUATION_SNAPSHOT,
                    DatasetName.CAPITAL_FLOW_SNAPSHOT,
                    DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT,
                    DatasetName.MARGIN_FINANCING_LENDING,
                    DatasetName.FINANCIAL_STATEMENTS,
                    DatasetName.FINANCIAL_INDICATORS,
                    DatasetName.MAJOR_ACTIVITY_EVENTS,
                ),
            ),
            InformationCoverage(
                InformationDomain.ETF_FUND_FULL_DATA,
                stable_datasets=(
                    DatasetName.DAILY_BARS,
                    DatasetName.FUND_PROFILE,
                    DatasetName.FUND_NAV_SNAPSHOT,
                    DatasetName.FUND_HOLDINGS,
                    DatasetName.FUND_SCALE_SHARE_SNAPSHOT,
                    DatasetName.FUND_FLOW,
                ),
            ),
            InformationCoverage(
                InformationDomain.INDEX_DATA,
                stable_datasets=(
                    DatasetName.INDEX_DAILY_BARS,
                    DatasetName.INDEX_CONSTITUENTS,
                    DatasetName.INDEX_WEIGHT_HISTORY,
                ),
            ),
            InformationCoverage(
                InformationDomain.EXCHANGE_CALENDAR,
                stable_datasets=(DatasetName.TRADING_CALENDAR,),
            ),
        ),
        market_coverage=(
            MarketDomain.A_SHARE,
            MarketDomain.ETF_FUND,
            MarketDomain.INDEX,
        ),
        asset_coverage=(
            AssetDomain.STOCK,
            AssetDomain.ETF,
            AssetDomain.FUND,
            AssetDomain.INDEX,
            AssetDomain.MACRO_SERIES,
        ),
        geography_coverage=(GeographyDomain.CN_MAINLAND,),
        requires_credentials=True,
        requires_live_network=True,
        stage=SourceStage.PRIORITIZED,
        priority=1,
        notes=(
            "Primary CN source family for equity, ETF/fund, index, valuation, "
            "capital flow, turnover/liquidity, and calendar-related fields."
        ),
    ),
    SourceCatalogEntry(
        source_id="akshare_cn_hk_public_family",
        source_name="AKShare CN/HK Public Family",
        dataset_coverage=(
            DatasetName.INSTRUMENT_MASTER,
            DatasetName.TRADING_CALENDAR,
            DatasetName.DAILY_BARS,
            DatasetName.MINUTE_BARS,
            DatasetName.INDEX_DAILY_BARS,
            DatasetName.INDEX_CONSTITUENTS,
            DatasetName.CORPORATE_ACTIONS,
            DatasetName.ADJUSTMENT_FACTORS,
            DatasetName.SUSPENSION_RESUMPTION_EVENTS,
            DatasetName.INSTRUMENT_STATUS_HISTORY,
            DatasetName.VALUATION_SNAPSHOT,
            DatasetName.CAPITAL_FLOW_SNAPSHOT,
            DatasetName.NORTHBOUND_FLOW_SNAPSHOT,
            DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT,
            DatasetName.LIMIT_UP_DOWN_EVENTS,
            DatasetName.MARGIN_FINANCING_LENDING,
            DatasetName.FUND_PROFILE,
            DatasetName.FUND_NAV_SNAPSHOT,
            DatasetName.FUND_HOLDINGS,
            DatasetName.FUND_SCALE_SHARE_SNAPSHOT,
            DatasetName.FUND_PREMIUM_DISCOUNT,
            DatasetName.FUND_FLOW,
            DatasetName.FINANCIAL_STATEMENTS,
            DatasetName.FINANCIAL_INDICATORS,
            DatasetName.MAJOR_ACTIVITY_EVENTS,
            DatasetName.SECTOR_MASTER,
            DatasetName.SECTOR_MEMBERSHIP,
            DatasetName.SECTOR_DAILY_BARS,
            DatasetName.NEWS_EVENTS,
            DatasetName.COMPANY_ANNOUNCEMENTS,
            DatasetName.GLOBAL_EQUITY_SNAPSHOT,
        ),
        information_coverage=(
            InformationCoverage(
                InformationDomain.A_SHARE_FULL_DATA,
                stable_datasets=(
                    DatasetName.INSTRUMENT_MASTER,
                    DatasetName.DAILY_BARS,
                    DatasetName.MINUTE_BARS,
                    DatasetName.CORPORATE_ACTIONS,
                    DatasetName.ADJUSTMENT_FACTORS,
                    DatasetName.SUSPENSION_RESUMPTION_EVENTS,
                    DatasetName.INSTRUMENT_STATUS_HISTORY,
                    DatasetName.VALUATION_SNAPSHOT,
                    DatasetName.CAPITAL_FLOW_SNAPSHOT,
                    DatasetName.NORTHBOUND_FLOW_SNAPSHOT,
                    DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT,
                    DatasetName.LIMIT_UP_DOWN_EVENTS,
                    DatasetName.MARGIN_FINANCING_LENDING,
                    DatasetName.FINANCIAL_STATEMENTS,
                    DatasetName.FINANCIAL_INDICATORS,
                    DatasetName.MAJOR_ACTIVITY_EVENTS,
                ),
            ),
            InformationCoverage(
                InformationDomain.HK_STOCK_FULL_DATA,
                stable_datasets=(
                    DatasetName.INSTRUMENT_MASTER,
                    DatasetName.DAILY_BARS,
                    DatasetName.CORPORATE_ACTIONS,
                    DatasetName.VALUATION_SNAPSHOT,
                    DatasetName.FINANCIAL_STATEMENTS,
                    DatasetName.FINANCIAL_INDICATORS,
                ),
            ),
            InformationCoverage(
                InformationDomain.ETF_FUND_FULL_DATA,
                stable_datasets=(
                    DatasetName.FUND_PROFILE,
                    DatasetName.FUND_NAV_SNAPSHOT,
                    DatasetName.FUND_HOLDINGS,
                    DatasetName.FUND_SCALE_SHARE_SNAPSHOT,
                    DatasetName.FUND_PREMIUM_DISCOUNT,
                    DatasetName.FUND_FLOW,
                ),
            ),
            InformationCoverage(
                InformationDomain.INDEX_DATA,
                stable_datasets=(
                    DatasetName.INDEX_DAILY_BARS,
                    DatasetName.INDEX_CONSTITUENTS,
                ),
            ),
            InformationCoverage(
                InformationDomain.GLOBAL_EQUITY_CONCISE,
                stable_datasets=(
                    DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                ),
            ),
            InformationCoverage(
                InformationDomain.INDUSTRY_CONCEPT_SECTOR,
                stable_datasets=(
                    DatasetName.SECTOR_MASTER,
                    DatasetName.SECTOR_MEMBERSHIP,
                    DatasetName.SECTOR_DAILY_BARS,
                ),
            ),
            InformationCoverage(
                InformationDomain.NEWS,
                stable_datasets=(DatasetName.NEWS_EVENTS,),
            ),
            InformationCoverage(
                InformationDomain.ANNOUNCEMENT,
                stable_datasets=(DatasetName.COMPANY_ANNOUNCEMENTS,),
            ),
            InformationCoverage(
                InformationDomain.EXCHANGE_CALENDAR,
                stable_datasets=(DatasetName.TRADING_CALENDAR,),
            ),
        ),
        market_coverage=(
            MarketDomain.A_SHARE,
            MarketDomain.HONG_KONG,
            MarketDomain.ETF_FUND,
            MarketDomain.INDEX,
            MarketDomain.GLOBAL_EQUITY,
        ),
        asset_coverage=(
            AssetDomain.STOCK,
            AssetDomain.ETF,
            AssetDomain.FUND,
            AssetDomain.INDEX,
            AssetDomain.SECTOR_CONCEPT,
            AssetDomain.NEWS_EVENT,
            AssetDomain.ANNOUNCEMENT,
        ),
        geography_coverage=(
            GeographyDomain.CN_MAINLAND,
            GeographyDomain.HONG_KONG,
            GeographyDomain.GLOBAL,
        ),
        requires_credentials=False,
        requires_live_network=True,
        stage=SourceStage.PRIORITIZED,
        priority=1,
        notes=(
            "Public-source family for CN/HK coverage and concise global "
            "equity snapshots; includes A-share corporate-action dividend/"
            "bonus/transfer distributions plus explicit no-distribution "
            "decisions via CNInfo, CNInfo-backed bounded rights-issue "
            "implementation records with Sina detail fallback, "
            "caller-provided A-share lifecycle/status evidence through "
            "stock_info_sh_name_code, stock_info_sz_name_code, "
            "stock_info_bj_name_code, stock_info_sh_delist, "
            "stock_info_sz_delist, and stock_info_sz_change_name with "
            "deterministic effective_start_date filtering, but full dated "
            "ST/*ST continuity and explicit SH terminal delist dates remain "
            "unproven. A-share suspension/resumption proof currently uses "
            "one-day bounded stock_tfp_em windows plus "
            "news_trade_notify_suspend_baidu exact-resumption supplementation; "
            "multi-day public windows, full exchange breadth, and complete "
            "resumption continuity remain incomplete. A-share minute-bar proof "
            "currently combines bounded stock_zh_a_hist_min_em, direct "
            "Eastmoney kline fallback, and limited recent stock_zh_a_minute "
            "fallback; older 1-minute continuity and deeper public-source "
            "redundancy remain unproven. "
            "caller-provided exchange ETF daily bars through fund_etf_hist_em, "
            "the explicitly proven listed-fund/LOF symbol 161725.FUND_CN "
            "through fund_lof_hist_em, and bounded fund_etf_hist_sina fallback "
            "history for both accepted listed route families, but broader "
            "listed-fund breadth, off-exchange fund daily-bar breadth, and "
            "independent public-route redundancy remain unproven. "
            "ETF/fund NAV proof currently uses bounded fund_etf_fund_info_em "
            "windows for exchange ETF codes plus explicit FUND_CN history from "
            "fund_open_fund_info_em, with same-family open-route fallback when "
            "bounded ETF windows are empty; ambiguous bare 0-prefix fund codes "
            "still require explicit .FUND_CN and some fund classes remain "
            "unproven. ETF/fund premium-discount proof now combines latest-"
            "available direct snapshots from fund_etf_fund_daily_em and "
            "fund_etf_spot_em with request-scoped historical listed-price plus "
            "NAV composites through fund_etf_hist_em or fund_lof_hist_em, "
            "bounded fund_etf_hist_sina fallback history, "
            "fund_etf_fund_info_em, and explicit 161725.FUND_CN coverage "
            "through fund_open_fund_info_em, but broader listed-fund breadth, "
            "off-exchange fund support, and independent direct public premium-"
            "discount redundancy remain unproven. ETF/fund scale/share proof "
            "now has a dedicated adapter-backed normalized path through bounded "
            "exchange ETF share history "
            "from fund_etf_scale_sse and fund_scale_daily_szse plus request-"
            "scoped latest per-fund snapshot scale/share fallback from "
            "fund_scale_open_sina and fund_scale_close_sina when bounded "
            "requests still have uncovered target symbols, but structured/other "
            "fund families, clear raised-scale unit semantics, source-side "
            "caller-parameterized snapshot endpoints, and independent public-"
            "route redundancy remain incomplete. "
            "ETF/fund flow proof remains limited to bounded exchange share-"
            "slice records from fund_etf_scale_sse and fund_scale_daily_szse "
            "with source-route truth; broader per-fund dated flow history is "
            "not currently proven because fund_scale_change_em is aggregate "
            "market-wide only, fund_purchase_em is status-only, and "
            "fund_etf_scale_szse is latest-only and currently call-"
            "incompatible in the accepted local environment. "
            "ETF/fund holdings proof currently uses "
            "fund_portfolio_hold_em for exchange ETFs plus explicit FUND_CN "
            "public funds such as 000001.FUND_CN where the route returns "
            "domestic A-share/BJ holdings, but bare 0-prefix fund codes still "
            "require explicit .FUND_CN, some fund classes emit non-A-share "
            "holding symbols, and independent holdings-route redundancy is "
            "still unproven. "
            "Sina-backed stock_zh_a_daily qfq/hfq adjustment-factor "
            "change-point series remain the only validated public no-credential "
            "A-share factor route; full per-trade-date continuity and "
            "independent redundancy are still unproven. "
            "bounded Eastmoney-backed stock_dzjy_mrmx block-trade detail "
            "rows plus stock_dzjy_mrtj symbol-date summary rows, "
            "Eastmoney-backed northbound symbol-date holding/daily-change facts "
            "through stock_hsgt_individual_em with bounded "
            "stock_hsgt_individual_detail_em fallback for holding/value/A-share-ratio "
            "facts, Eastmoney-backed stock_zh_a_hist daily turnover/liquidity facts, "
            "and bounded stock_zt_pool_em / stock_zt_pool_dtgc_em / "
            "stock_zt_pool_previous_em / stock_zt_pool_strong_em / "
            "stock_zt_pool_sub_new_em / stock_zt_pool_zbgc_em limit-up/down topic "
            "pools with source-route truth. A-share financial-statement proof "
            "currently combines stock_financial_report_sina plus "
            "stock_financial_debt_new_ths / stock_financial_benefit_new_ths / "
            "stock_financial_cash_new_ths statement-backed metric routes, but "
            "cross-route reconciliation and full long-history breadth remain "
            "incomplete. A-share valuation proof currently "
            "combines stock_zh_valuation_baidu multi-period history, "
            "stock_value_em dated overlap from 2018 onward, and latest-only "
            "stock_individual_info_em plus stock_zh_valuation_comparison_em "
            "same-date enrichment, but pre-2018 public-source redundancy, "
            "full-history continuity, and route-shape stability remain "
            "incomplete. HK valuation proof currently uses "
            "caller-provided stock_hk_indicator_eniu dated PE/PB/market-cap "
            "history with optional same-date stock_hk_valuation_baidu "
            "ps_ttm/float-market-cap supplementation when reachable, but the "
            "proven public history observed in the accepted live environment "
            "is stale through 2022-07-13 and current-dated redundancy is "
            "still unproven. HK financial proof currently uses "
            "caller-provided stock_financial_hk_report_em and "
            "stock_financial_hk_analysis_indicator_em multi-symbol bounded "
            "report-period history with explicit source-route truth plus "
            "deterministic income-statement alias selection for operating-"
            "income and shareholder-profit fields, but broader HK issuer "
            "breadth, non-stock support, longer continuity, and independent "
            "public-source redundancy remain unproven. Index daily-bar proof "
            "currently covers bounded mainland benchmark windows through "
            "stock_zh_index_daily_tx, stock_zh_index_daily, "
            "stock_zh_index_daily_em, and index_zh_a_hist for the explicitly "
            "validated CSI/SSE/SZSE benchmark slice, plus major Hang Seng "
            "benchmark history through stock_hk_index_daily_sina with "
            "source-route truth, plus a curated key global benchmark slice "
            "through index_global_hist_sina. The accepted global public slice "
            "is still limited to the route's recent 1000-row history window, "
            "does not yet prove stable major US benchmark history, and has no "
            "independent public-route redundancy; broader HK index families "
            "also remain unproven. HK corporate-actions proof currently "
            "covers one-symbol stock_hk_dividend_payout_em dividend/"
            "distribution implementation history plus same-family "
            "stock_hk_fhpx_detail_ths dividend-plan and explicit "
            "no-distribution decision history; broader HK split/rights/"
            "consolidation taxonomy and multi-symbol breadth remain unproven. "
            "HK daily-bar proof currently uses stock_hk_hist bounded windows "
            "with stock_hk_daily full-history fallback filtering inside the "
            "same AKShare family, so independent public-source redundancy is "
            "still unproven. HK turnover/liquidity proof currently exposes "
            "only dated volume and traded amount through those same "
            "stock_hk_hist plus stock_hk_daily routes with explicit "
            "source-route truth; public turnover-rate, float-share, spread, "
            "and other deeper liquidity facts are not source-validated yet. "
            "HK instrument-master proof is currently limited "
            "to stock_hk_security_profile_em stock profiles plus bounded "
            "stock_hk_spot_em or sina_hk_stock_spot_page1 current-listed stock "
            "sampling; no proven no-credential HK non-stock taxonomy or dated "
            "delist/inactive lifecycle route is catalog-validated yet. "
            "Sector/concept proof currently covers caller-provided bounded "
            "industry/concept membership batches through "
            "stock_board_industry_cons_em and stock_board_concept_cons_em with "
            "THS detail-page fallback when public network conditions break the "
            "Eastmoney route family, plus caller-provided bounded sector daily-"
            "bar batches through stock_board_industry_hist_em and "
            "stock_board_concept_hist_em with same-family THS history fallback "
            "and deterministic requested-window filtering. These public routes "
            "still do not prove explicit sector change-event timelines, "
            "classification-version metadata, or independent non-AKShare route "
            "redundancy. A-share company-announcement proof currently uses "
            "caller-provided bounded stock_individual_notice_report windows "
            "with stock_notice_report per-day fallback, explicit source-route "
            "truth, and deterministic requested-window filtering, but broader "
            "category breadth, longer continuity, and independent public-route "
            "redundancy remain incomplete."
        ),
    ),
    SourceCatalogEntry(
        source_id="hkex_disclosure_and_calendar_family",
        source_name="HKEX Disclosure and Calendar Family",
        dataset_coverage=(
            DatasetName.INSTRUMENT_MASTER,
            DatasetName.TRADING_CALENDAR,
            DatasetName.DAILY_BARS,
            DatasetName.CORPORATE_ACTIONS,
            DatasetName.FUND_PROFILE,
            DatasetName.COMPANY_ANNOUNCEMENTS,
        ),
        information_coverage=(
            InformationCoverage(
                InformationDomain.HK_STOCK_FULL_DATA,
                stable_datasets=(
                    DatasetName.INSTRUMENT_MASTER,
                    DatasetName.DAILY_BARS,
                    DatasetName.CORPORATE_ACTIONS,
                    DatasetName.COMPANY_ANNOUNCEMENTS,
                ),
            ),
            InformationCoverage(
                InformationDomain.ETF_FUND_FULL_DATA,
                stable_datasets=(DatasetName.FUND_PROFILE,),
            ),
            InformationCoverage(
                InformationDomain.EXCHANGE_CALENDAR,
                stable_datasets=(DatasetName.TRADING_CALENDAR,),
            ),
            InformationCoverage(
                InformationDomain.ANNOUNCEMENT,
                stable_datasets=(DatasetName.COMPANY_ANNOUNCEMENTS,),
            ),
        ),
        market_coverage=(MarketDomain.HONG_KONG, MarketDomain.ETF_FUND),
        asset_coverage=(
            AssetDomain.STOCK,
            AssetDomain.ETF,
            AssetDomain.FUND,
            AssetDomain.ANNOUNCEMENT,
        ),
        geography_coverage=(GeographyDomain.HONG_KONG,),
        requires_credentials=False,
        requires_live_network=True,
        stage=SourceStage.PRIORITIZED,
        priority=1,
        notes=(
            "HK exchange listing, schedule, and disclosure-related family with "
            "predefineddoc.xhtml company-announcement metadata, explicit "
            "source-route truth, and fund profile support; broader historical "
            "pagination depth and independent public-route redundancy remain "
            "incomplete."
        ),
    ),
    SourceCatalogEntry(
        source_id="baostock_public_cn",
        source_name="BaoStock Public CN",
        dataset_coverage=(DatasetName.MINUTE_BARS,),
        information_coverage=(
            InformationCoverage(
                InformationDomain.A_SHARE_FULL_DATA,
                stable_datasets=(DatasetName.MINUTE_BARS,),
            ),
        ),
        market_coverage=(MarketDomain.A_SHARE,),
        asset_coverage=(AssetDomain.STOCK,),
        geography_coverage=(GeographyDomain.CN_MAINLAND,),
        requires_credentials=False,
        requires_live_network=True,
        stage=SourceStage.PRIORITIZED,
        priority=1,
        notes=(
            "No-credential BaoStock public route for bounded A-share 5/15/30/60-minute "
            "historical bars; 1-minute history and full-market collection remain out of scope."
        ),
    ),
    SourceCatalogEntry(
        source_id="macro_policy_public_sources",
        source_name="Macro and Policy Public Sources",
        dataset_coverage=(
            DatasetName.MACRO_INDICATOR_MASTER,
            DatasetName.MACRO_OBSERVATIONS,
            DatasetName.POLICY_DOCUMENTS,
        ),
        information_coverage=(
            InformationCoverage(
                InformationDomain.GLOBAL_MACRO,
                stable_datasets=(
                    DatasetName.MACRO_INDICATOR_MASTER,
                    DatasetName.MACRO_OBSERVATIONS,
                ),
            ),
            InformationCoverage(
                InformationDomain.CHINA_MACRO,
                stable_datasets=(
                    DatasetName.MACRO_INDICATOR_MASTER,
                    DatasetName.MACRO_OBSERVATIONS,
                ),
            ),
            InformationCoverage(
                InformationDomain.POLICY,
                stable_datasets=(DatasetName.POLICY_DOCUMENTS,),
            ),
        ),
        market_coverage=(MarketDomain.GLOBAL_EQUITY, MarketDomain.A_SHARE),
        asset_coverage=(AssetDomain.MACRO_SERIES, AssetDomain.POLICY_DOCUMENT),
        geography_coverage=(GeographyDomain.CN_MAINLAND, GeographyDomain.GLOBAL),
        requires_credentials=False,
        requires_live_network=True,
        stage=SourceStage.PRIORITIZED,
        priority=2,
        notes=(
            "Implemented public-source family for bounded China plus selected "
            "US/Euro macro indicator definitions/observations, source-backed "
            "per-observation release_date facts where upstream routes expose "
            "them, and gov.cn policy-document metadata with deterministic "
            "server-side date-window query parameters; broader macro breadth, "
            "release/revision depth, policy authority coverage, pagination "
            "depth, and durable history remain incomplete."
        ),
    ),
    SourceCatalogEntry(
        source_id="local_data_quality_engine",
        source_name="Local Data Quality Engine",
        dataset_coverage=(DatasetName.DATA_QUALITY_REPORT,),
        information_coverage=(
            InformationCoverage(
                InformationDomain.SOURCE_HEALTH_QUALITY,
                stable_datasets=(DatasetName.DATA_QUALITY_REPORT,),
            ),
        ),
        market_coverage=(
            MarketDomain.A_SHARE,
            MarketDomain.HONG_KONG,
            MarketDomain.ETF_FUND,
            MarketDomain.INDEX,
            MarketDomain.GLOBAL_EQUITY,
        ),
        asset_coverage=(
            AssetDomain.STOCK,
            AssetDomain.ETF,
            AssetDomain.FUND,
            AssetDomain.INDEX,
            AssetDomain.SECTOR_CONCEPT,
            AssetDomain.MACRO_SERIES,
            AssetDomain.POLICY_DOCUMENT,
            AssetDomain.NEWS_EVENT,
            AssetDomain.ANNOUNCEMENT,
        ),
        geography_coverage=(
            GeographyDomain.CN_MAINLAND,
            GeographyDomain.HONG_KONG,
            GeographyDomain.GLOBAL,
        ),
        requires_credentials=False,
        requires_live_network=False,
        stage=SourceStage.READY_FOR_ADAPTER,
        priority=1,
        notes=(
            "Local quality metadata emitter. Deterministic, no remote fetch, "
            "available in default offline checks, and now exposes readiness "
            "coverage KPIs for domain/capability/follow-up observability only; "
            "these metrics do not prove that any real-source adapter became complete."
        ),
    ),
)


class SourceCatalog:
    """Runtime catalog with dataset/domain coverage helper methods."""

    def __init__(
        self,
        entries: Iterable[SourceCatalogEntry],
        *,
        required_datasets: Iterable[DatasetName] | None = None,
        required_market_domains: Iterable[MarketDomain] | None = None,
        required_asset_domains: Iterable[AssetDomain] | None = None,
        required_geography_domains: Iterable[GeographyDomain] | None = None,
        required_information_domains: Iterable[InformationDomain] | None = None,
    ) -> None:
        self._entries: tuple[SourceCatalogEntry, ...] = tuple(entries)
        self._required_datasets: tuple[DatasetName, ...] = tuple(
            required_datasets if required_datasets is not None else REQUIRED_DATASETS
        )
        self._required_market_domains: tuple[MarketDomain, ...] = tuple(
            required_market_domains
            if required_market_domains is not None
            else REQUIRED_MARKET_DOMAINS
        )
        self._required_asset_domains: tuple[AssetDomain, ...] = tuple(
            required_asset_domains
            if required_asset_domains is not None
            else REQUIRED_ASSET_DOMAINS
        )
        self._required_geography_domains: tuple[GeographyDomain, ...] = tuple(
            required_geography_domains
            if required_geography_domains is not None
            else REQUIRED_GEOGRAPHY_DOMAINS
        )
        self._required_information_domains: tuple[InformationDomain, ...] = tuple(
            required_information_domains
            if required_information_domains is not None
            else REQUIRED_INFORMATION_DOMAINS
        )

    def all_sources(self) -> tuple[SourceCatalogEntry, ...]:
        return self._entries

    def sources_for_dataset(self, dataset: DatasetName) -> tuple[SourceCatalogEntry, ...]:
        return tuple(
            entry for entry in self._entries if dataset in entry.dataset_coverage
        )

    def missing_dataset_coverage(
        self,
        required_datasets: Iterable[DatasetName] | None = None,
    ) -> tuple[DatasetName, ...]:
        required = (
            tuple(required_datasets)
            if required_datasets is not None
            else self._required_datasets
        )
        return tuple(dataset for dataset in required if not self.sources_for_dataset(dataset))

    def has_full_dataset_coverage(
        self,
        required_datasets: Iterable[DatasetName] | None = None,
    ) -> bool:
        return not self.missing_dataset_coverage(required_datasets)

    def sources_for_information_domain(
        self,
        domain: InformationDomain,
    ) -> tuple[SourceCatalogEntry, ...]:
        return tuple(
            entry
            for entry in self._entries
            if any(coverage.domain == domain for coverage in entry.information_coverage)
        )

    def stable_datasets_for_information_domain(
        self,
        domain: InformationDomain,
    ) -> tuple[DatasetName, ...]:
        datasets: list[DatasetName] = []
        for entry in self._entries:
            for coverage in entry.information_coverage:
                if coverage.domain != domain:
                    continue
                for dataset in coverage.stable_datasets:
                    if dataset not in datasets:
                        datasets.append(dataset)
        return tuple(datasets)

    def missing_information_coverage(
        self,
        required_information_domains: Iterable[InformationDomain] | None = None,
    ) -> tuple[InformationDomain, ...]:
        required = (
            tuple(required_information_domains)
            if required_information_domains is not None
            else self._required_information_domains
        )
        return tuple(
            domain
            for domain in required
            if not self.sources_for_information_domain(domain)
        )

    def has_full_information_coverage(
        self,
        required_information_domains: Iterable[InformationDomain] | None = None,
    ) -> bool:
        return not self.missing_information_coverage(required_information_domains)

    def information_domains_missing_stable_dataset_contracts(
        self,
        required_information_domains: Iterable[InformationDomain] | None = None,
    ) -> tuple[InformationDomain, ...]:
        required = (
            tuple(required_information_domains)
            if required_information_domains is not None
            else self._required_information_domains
        )
        return tuple(
            domain
            for domain in required
            if self.sources_for_information_domain(domain)
            and not self.stable_datasets_for_information_domain(domain)
        )

    def covered_market_domains(self) -> frozenset[MarketDomain]:
        domains: set[MarketDomain] = set()
        for entry in self._entries:
            domains.update(entry.market_coverage)
        return frozenset(domains)

    def missing_market_coverage(
        self,
        required_market_domains: Iterable[MarketDomain] | None = None,
    ) -> tuple[MarketDomain, ...]:
        required = (
            tuple(required_market_domains)
            if required_market_domains is not None
            else self._required_market_domains
        )
        covered = self.covered_market_domains()
        return tuple(domain for domain in required if domain not in covered)

    def has_full_market_coverage(
        self,
        required_market_domains: Iterable[MarketDomain] | None = None,
    ) -> bool:
        return not self.missing_market_coverage(required_market_domains)

    def covered_asset_domains(self) -> frozenset[AssetDomain]:
        domains: set[AssetDomain] = set()
        for entry in self._entries:
            domains.update(entry.asset_coverage)
        return frozenset(domains)

    def missing_asset_coverage(
        self,
        required_asset_domains: Iterable[AssetDomain] | None = None,
    ) -> tuple[AssetDomain, ...]:
        required = (
            tuple(required_asset_domains)
            if required_asset_domains is not None
            else self._required_asset_domains
        )
        covered = self.covered_asset_domains()
        return tuple(domain for domain in required if domain not in covered)

    def has_full_asset_coverage(
        self,
        required_asset_domains: Iterable[AssetDomain] | None = None,
    ) -> bool:
        return not self.missing_asset_coverage(required_asset_domains)

    def covered_geography_domains(self) -> frozenset[GeographyDomain]:
        domains: set[GeographyDomain] = set()
        for entry in self._entries:
            domains.update(entry.geography_coverage)
        return frozenset(domains)

    def missing_geography_coverage(
        self,
        required_geography_domains: Iterable[GeographyDomain] | None = None,
    ) -> tuple[GeographyDomain, ...]:
        required = (
            tuple(required_geography_domains)
            if required_geography_domains is not None
            else self._required_geography_domains
        )
        covered = self.covered_geography_domains()
        return tuple(domain for domain in required if domain not in covered)

    def has_full_geography_coverage(
        self,
        required_geography_domains: Iterable[GeographyDomain] | None = None,
    ) -> bool:
        return not self.missing_geography_coverage(required_geography_domains)

    def has_full_domain_coverage(
        self,
        *,
        required_market_domains: Iterable[MarketDomain] | None = None,
        required_asset_domains: Iterable[AssetDomain] | None = None,
        required_geography_domains: Iterable[GeographyDomain] | None = None,
        required_information_domains: Iterable[InformationDomain] | None = None,
    ) -> bool:
        return (
            self.has_full_market_coverage(required_market_domains)
            and self.has_full_asset_coverage(required_asset_domains)
            and self.has_full_geography_coverage(required_geography_domains)
            and self.has_full_information_coverage(required_information_domains)
        )


def build_default_source_catalog() -> SourceCatalog:
    """Build the deterministic default source catalog for TASK-006."""
    return SourceCatalog(
        entries=DEFAULT_SOURCE_CATALOG_ENTRIES,
        required_datasets=REQUIRED_DATASETS,
        required_market_domains=REQUIRED_MARKET_DOMAINS,
        required_asset_domains=REQUIRED_ASSET_DOMAINS,
        required_geography_domains=REQUIRED_GEOGRAPHY_DOMAINS,
        required_information_domains=REQUIRED_INFORMATION_DOMAINS,
    )


DEFAULT_SOURCE_CATALOG = build_default_source_catalog()


__all__ = [
    "AssetDomain",
    "DEFAULT_SOURCE_CATALOG",
    "DEFAULT_SOURCE_CATALOG_ENTRIES",
    "GeographyDomain",
    "InformationCoverage",
    "InformationDomain",
    "MarketDomain",
    "REQUIRED_ASSET_DOMAINS",
    "REQUIRED_DATASETS",
    "REQUIRED_GEOGRAPHY_DOMAINS",
    "REQUIRED_INFORMATION_DOMAINS",
    "REQUIRED_MARKET_DOMAINS",
    "SourceCatalog",
    "SourceCatalogEntry",
    "SourceStage",
    "build_default_source_catalog",
]
