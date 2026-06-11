import socket
import unittest
from unittest.mock import patch

from quant.datahub.datasets import DatasetName
from quant.datahub.source_capabilities import (
    CapabilityDomain,
    CapabilityRequirement,
    CapabilityStatus,
    ResearchHorizon,
    build_default_source_capability_audit,
    get_capabilities_by_domain,
    get_capabilities_by_horizon,
    get_capabilities_with_planned_or_credentialed_sources,
    get_capabilities_without_dataset_mapping,
    get_missing_capabilities,
    get_partial_capabilities,
    get_required_capabilities,
)
from quant.datahub.source_catalog import build_default_source_catalog


class SourceCapabilityAuditTests(unittest.TestCase):
    def test_required_capability_groups_exist(self) -> None:
        audit = build_default_source_capability_audit()
        required = audit.required_capabilities()
        required_ids = {capability.capability_id for capability in required}

        expected_required_ids = {
            "a_share_universe_reference",
            "a_share_listing_delisting_st_status",
            "a_share_trading_calendar",
            "a_share_suspension_resumption",
            "a_share_daily_bars",
            "a_share_minute_bars",
            "a_share_adjustment_factors",
            "a_share_corporate_actions",
            "a_share_valuation_history",
            "a_share_capital_flow",
            "a_share_northbound_flow",
            "a_share_turnover_liquidity",
            "a_share_limit_up_down",
            "a_share_margin_financing_and_lending",
            "a_share_financial_statements",
            "a_share_financial_indicators",
            "a_share_company_announcements",
            "a_share_major_activity_events",
            "hk_universe_reference",
            "hk_trading_calendar",
            "hk_daily_bars",
            "hk_corporate_actions",
            "hk_valuation_history",
            "hk_announcements_disclosures",
            "hk_financial_data",
            "hk_turnover_liquidity",
            "fund_reference",
            "fund_daily_bars",
            "fund_nav",
            "fund_holdings_composition",
            "fund_scale_and_share",
            "fund_flow",
            "fund_premium_discount",
            "fund_profile_details",
            "index_daily_bars",
            "index_constituent_history",
            "index_weight_history",
            "index_rebalance_effective_dates",
            "index_china_hk_global_benchmarks",
            "sector_classification_master",
            "sector_membership",
            "sector_historical_changes",
            "sector_daily_bars",
            "macro_observations",
            "macro_indicator_definitions",
            "macro_release_metadata",
            "policy_documents",
            "news_events",
            "company_announcements_cross_market",
            "source_freshness",
            "source_coverage_metadata",
            "source_availability_health",
            "source_schema_validation",
            "source_refresh_metadata",
        }

        self.assertTrue(expected_required_ids.issubset(required_ids))

        for domain in (
            CapabilityDomain.A_SHARE,
            CapabilityDomain.HONG_KONG,
            CapabilityDomain.ETF_FUND,
            CapabilityDomain.INDEX,
            CapabilityDomain.SECTOR_CONCEPT,
            CapabilityDomain.MACRO,
            CapabilityDomain.POLICY_NEWS_ANNOUNCEMENT,
            CapabilityDomain.SOURCE_QUALITY,
        ):
            self.assertTrue(audit.capabilities_by_domain(domain, required_only=True))

    def test_horizons_cover_short_term_and_medium_long_term(self) -> None:
        short_term = get_capabilities_by_horizon(ResearchHorizon.SHORT_TERM)
        medium_long_term = get_capabilities_by_horizon(ResearchHorizon.MEDIUM_LONG_TERM)
        required = get_required_capabilities()

        self.assertTrue(short_term)
        self.assertTrue(medium_long_term)
        self.assertTrue(
            all(capability.horizons for capability in required),
            "Every required capability should declare at least one horizon.",
        )
        self.assertIn(
            "a_share_minute_bars",
            {capability.capability_id for capability in short_term},
        )
        self.assertIn(
            "a_share_financial_statements",
            {capability.capability_id for capability in medium_long_term},
        )

    def test_missing_and_partial_capabilities_are_reported(self) -> None:
        missing_ids = {capability.capability_id for capability in get_missing_capabilities()}
        partial_ids = {capability.capability_id for capability in get_partial_capabilities()}

        self.assertIn("hk_minute_bars", missing_ids)
        self.assertNotIn("a_share_minute_bars", missing_ids)
        self.assertNotIn("fund_flow", missing_ids)
        self.assertNotIn("a_share_margin_financing_and_lending", missing_ids)
        self.assertNotIn("a_share_daily_bars", partial_ids)
        self.assertIn("a_share_minute_bars", partial_ids)
        self.assertIn("a_share_margin_financing_and_lending", partial_ids)
        self.assertIn("hk_daily_bars", partial_ids)
        self.assertIn("source_coverage_metadata", partial_ids)
        self.assertNotIn("source_availability_health", partial_ids)

    def test_dataset_and_source_catalog_linkage_exists(self) -> None:
        audit = build_default_source_capability_audit()
        catalog = build_default_source_catalog()
        source_ids = {entry.source_id for entry in catalog.all_sources()}

        mapped_capabilities = [
            capability
            for capability in audit.all_capabilities(required_only=True)
            if capability.dataset_mappings
        ]
        self.assertTrue(mapped_capabilities)

        for capability in mapped_capabilities:
            for dataset in capability.dataset_mappings:
                self.assertIsInstance(dataset, DatasetName)
            for source_family_id in capability.source_family_ids:
                self.assertIn(source_family_id, source_ids)

    def test_helpers_for_no_contract_and_planned_or_credentialed_sources(self) -> None:
        no_contract_ids = {
            capability.capability_id
            for capability in get_capabilities_without_dataset_mapping()
        }
        planned_or_credentialed_ids = {
            capability.capability_id
            for capability in get_capabilities_with_planned_or_credentialed_sources()
        }

        self.assertIn("hk_minute_bars", no_contract_ids)
        self.assertNotIn("a_share_margin_financing_and_lending", no_contract_ids)
        self.assertNotIn("hk_financial_data", no_contract_ids)
        self.assertNotIn("fund_flow", no_contract_ids)
        self.assertIn("a_share_financial_statements", planned_or_credentialed_ids)
        self.assertIn("index_weight_history", planned_or_credentialed_ids)
        self.assertNotIn("macro_observations", planned_or_credentialed_ids)
        self.assertNotIn("macro_indicator_definitions", planned_or_credentialed_ids)
        self.assertNotIn("policy_documents", planned_or_credentialed_ids)

    def test_index_weight_history_uses_explicit_contract_and_remains_planned(self) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "index_weight_history"
        )

        self.assertEqual(
            capability.dataset_mappings,
            (DatasetName.INDEX_WEIGHT_HISTORY,),
        )
        self.assertEqual(capability.status, CapabilityStatus.PLANNED)
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)
        self.assertEqual(capability.source_family_ids, ("tushare_pro_cn_core",))
        self.assertIn("bounded tushare pro", capability.gap_reason.lower())
        self.assertIn("live pass", capability.gap_reason.lower())
        self.assertIn("tushare_token", capability.gap_reason.lower())
        self.assertNotIn("not implemented", capability.gap_reason.lower())
        self.assertIn("live smoke", capability.recommended_handoff_theme.lower())
        self.assertIn("promote only after", capability.recommended_handoff_theme.lower())

    def test_index_daily_bars_capability_truth_reflects_broader_cn_and_hk_slice(self) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "index_daily_bars"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertIn("CSI 500", capability.gap_reason)
        self.assertIn("Hang Seng", capability.gap_reason)
        self.assertIn("index_global_hist_sina", capability.gap_reason)
        self.assertIn("1000 rows", capability.gap_reason)
        self.assertIn("major US benchmark history", capability.gap_reason)
        self.assertIn("curated global slices", capability.recommended_handoff_theme)

    def test_sector_membership_capabilities_remain_conservative_after_batch_hardening(self) -> None:
        membership = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "sector_membership"
        )
        historical_changes = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "sector_historical_changes"
        )

        self.assertEqual(membership.status, CapabilityStatus.PARTIAL)
        self.assertIn("multi-sector", membership.gap_reason)
        self.assertIn("classification-version", membership.gap_reason)
        self.assertEqual(historical_changes.status, CapabilityStatus.PARTIAL)
        self.assertIn("change-event", historical_changes.gap_reason)

    def test_macro_and_policy_capabilities_are_partial_not_planned(self) -> None:
        required_by_id = {
            capability.capability_id: capability for capability in get_required_capabilities()
        }

        for capability_id in (
            "macro_observations",
            "macro_indicator_definitions",
            "policy_documents",
        ):
            capability = required_by_id[capability_id]
            self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
            self.assertIn("macro_policy_public_sources", capability.source_family_ids)
            self.assertNotEqual(capability.gap_reason, "")
            self.assertNotEqual(capability.recommended_handoff_theme, "")

    def test_a_share_corporate_actions_remain_partial_after_taxonomy_hardening(self) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "a_share_corporate_actions"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertIn("CNInfo rights-issue", capability.gap_reason)
        self.assertIn("split/consolidation", capability.gap_reason)
        self.assertIn("dividend/distribution", capability.recommended_handoff_theme)

    def test_task_042_required_no_mapping_capabilities_are_closed(self) -> None:
        no_contract_ids = {
            capability.capability_id
            for capability in get_capabilities_without_dataset_mapping()
        }
        required_gap_ids = {
            "a_share_minute_bars",
            "a_share_margin_financing_and_lending",
            "a_share_financial_statements",
            "a_share_financial_indicators",
            "a_share_major_activity_events",
            "hk_financial_data",
            "fund_flow",
        }

        self.assertTrue(required_gap_ids.isdisjoint(no_contract_ids))

    def test_margin_financing_lending_capability_uses_public_akshare_source_family(self) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "a_share_margin_financing_and_lending"
        )
        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertIn("tushare_pro_cn_core", capability.source_family_ids)
        self.assertIn("multi-symbol", capability.gap_reason.lower())
        self.assertIn("date-window", capability.gap_reason.lower())
        self.assertIn("sse", capability.gap_reason.lower())
        self.assertIn("szse", capability.gap_reason.lower())
        self.assertIn("route/exchange provenance", capability.gap_reason.lower())
        self.assertIn("bse", capability.gap_reason.lower())
        self.assertIn("exchange-summary", capability.recommended_handoff_theme.lower())
        self.assertIn("longer history continuity", capability.recommended_handoff_theme.lower())

    def test_minute_bars_capability_uses_public_akshare_source_family(self) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "a_share_minute_bars"
        )
        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertIn("baostock_public_cn", capability.source_family_ids)
        self.assertIn("tushare_pro_cn_core", capability.source_family_ids)
        self.assertIn("multi-symbol", capability.gap_reason.lower())
        self.assertIn("date-window", capability.gap_reason.lower())
        self.assertIn("5/15/30/60-minute", capability.gap_reason.lower())
        self.assertIn("1-minute history", capability.gap_reason.lower())
        self.assertIn("longer continuity", capability.recommended_handoff_theme.lower())
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)

    def test_a_share_daily_bars_capability_is_covered_after_batch_hardening(self) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "a_share_daily_bars"
        )

        self.assertEqual(capability.status, CapabilityStatus.COVERED)
        self.assertEqual(capability.dataset_mappings, (DatasetName.DAILY_BARS,))
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertEqual(capability.gap_reason, "")

    def test_index_constituent_and_rebalance_capabilities_remain_partial_after_batch_hardening(self) -> None:
        required_by_id = {
            capability.capability_id: capability for capability in get_required_capabilities()
        }

        constituent_history = required_by_id["index_constituent_history"]
        self.assertEqual(constituent_history.status, CapabilityStatus.PARTIAL)
        self.assertIn("multi-index", constituent_history.gap_reason.lower())
        self.assertIn("effective-date-like", constituent_history.gap_reason.lower())
        self.assertIn("star 50", constituent_history.gap_reason.lower())
        self.assertIn("sme board", constituent_history.gap_reason.lower())
        self.assertIn("longer constituent history continuity", constituent_history.recommended_handoff_theme.lower())

        rebalance_dates = required_by_id["index_rebalance_effective_dates"]
        self.assertEqual(rebalance_dates.status, CapabilityStatus.PARTIAL)
        self.assertEqual(rebalance_dates.dataset_mappings, (DatasetName.INDEX_CONSTITUENTS,))
        self.assertEqual(rebalance_dates.source_family_ids, ("akshare_cn_hk_public_family",))
        self.assertIn("effective-date-like", rebalance_dates.gap_reason.lower())
        self.assertIn("optional end dates", rebalance_dates.gap_reason.lower())
        self.assertIn("weights", rebalance_dates.gap_reason.lower())
        self.assertIn("rebalance calendar", rebalance_dates.gap_reason.lower())
        self.assertIn("stable public or credentialed source path", rebalance_dates.recommended_handoff_theme.lower())

    def test_index_daily_bars_capability_remains_partial_after_core_batch_hardening(self) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "index_daily_bars"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertEqual(capability.dataset_mappings, (DatasetName.INDEX_DAILY_BARS,))
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertIn("multi-index", capability.gap_reason.lower())
        self.assertIn("bounded", capability.gap_reason.lower())
        self.assertIn("curated key global benchmark slice", capability.gap_reason.lower())
        self.assertIn("major us/global benchmark", capability.recommended_handoff_theme.lower())

    def test_index_china_hk_global_benchmark_capability_truth_is_explicit(self) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "index_china_hk_global_benchmarks"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertEqual(
            capability.dataset_mappings,
            (DatasetName.INDEX_DAILY_BARS, DatasetName.GLOBAL_EQUITY_SNAPSHOT),
        )
        self.assertEqual(capability.source_family_ids, ("akshare_cn_hk_public_family",))
        self.assertIn("hang seng", capability.gap_reason.lower())
        self.assertIn("index_global_hist_sina", capability.gap_reason.lower())
        self.assertIn("major us benchmark history", capability.gap_reason.lower())
        self.assertIn("unsupported families explicit", capability.recommended_handoff_theme.lower())

    def test_hk_daily_bars_capability_remains_partial_after_batch_hardening(self) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "hk_daily_bars"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertEqual(capability.dataset_mappings, (DatasetName.DAILY_BARS,))
        self.assertIn("multi-symbol", capability.gap_reason.lower())
        self.assertIn("stock_hk_hist", capability.gap_reason)
        self.assertIn("stock_hk_daily", capability.gap_reason)
        self.assertIn("full-history fallback filtering", capability.gap_reason.lower())
        self.assertIn("independent second public hk daily-bar source", capability.gap_reason.lower())
        self.assertIn("independent no-credential hk daily-bar source", capability.recommended_handoff_theme.lower())
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)

    def test_hk_turnover_liquidity_capability_uses_dedicated_contract_profile(
        self,
    ) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "hk_turnover_liquidity"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertEqual(
            capability.dataset_mappings,
            (DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT,),
        )
        self.assertEqual(capability.source_family_ids, ("akshare_cn_hk_public_family",))
        self.assertIn("stock_hk_hist", capability.gap_reason)
        self.assertIn("stock_hk_daily", capability.gap_reason)
        self.assertIn("volume and traded amount", capability.gap_reason.lower())
        self.assertIn("turnover-rate", capability.gap_reason.lower())
        self.assertIn("public-source redundancy", capability.gap_reason.lower())
        self.assertIn("stock_hk_hist", capability.recommended_handoff_theme)
        self.assertIn("stock_hk_daily", capability.recommended_handoff_theme)
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)

    def test_hk_corporate_actions_capability_remains_partial_after_taxonomy_history_hardening(
        self,
    ) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "hk_corporate_actions"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertEqual(capability.dataset_mappings, (DatasetName.CORPORATE_ACTIONS,))
        self.assertIn("stock_hk_dividend_payout_em", capability.gap_reason)
        self.assertIn("stock_hk_fhpx_detail_ths", capability.gap_reason)
        self.assertIn("dividend_no_distribution", capability.gap_reason)
        self.assertIn("date-window", capability.gap_reason.lower())
        self.assertIn("multi-symbol", capability.gap_reason.lower())
        self.assertIn("split/rights/consolidation", capability.gap_reason.lower())
        self.assertIn("taxonomy", capability.recommended_handoff_theme.lower())
        self.assertIn("history", capability.recommended_handoff_theme.lower())
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)

    def test_hk_universe_reference_capability_remains_partial_after_batch_hardening(self) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "hk_universe_reference"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertEqual(capability.dataset_mappings, (DatasetName.INSTRUMENT_MASTER,))
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertIn("multi-symbol", capability.gap_reason.lower())
        self.assertIn("stock reference batches", capability.gap_reason.lower())
        self.assertIn("spot-list", capability.gap_reason.lower())
        self.assertIn("sina", capability.gap_reason.lower())
        self.assertIn("profile reconciliation", capability.gap_reason.lower())
        self.assertIn("stock_hk_security_profile_em", capability.gap_reason)
        self.assertIn("stock-only", capability.gap_reason.lower())
        self.assertIn("hard-fail", capability.gap_reason.lower())
        self.assertIn("inactive", capability.gap_reason.lower())
        self.assertIn("non-stock taxonomy", capability.recommended_handoff_theme.lower())
        self.assertIn("lifecycle metadata", capability.recommended_handoff_theme.lower())
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)

    def test_fund_daily_bars_capability_remains_partial_after_batch_hardening(self) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "fund_daily_bars"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertEqual(capability.dataset_mappings, (DatasetName.DAILY_BARS,))
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertIn("multi-symbol", capability.gap_reason.lower())
        self.assertIn("date-window", capability.gap_reason.lower())
        self.assertIn("listed-fund/lof", capability.gap_reason.lower())
        self.assertIn("161725.fund_cn", capability.gap_reason.lower())
        self.assertIn("broader listed-fund breadth", capability.gap_reason.lower())
        self.assertIn("off-exchange", capability.gap_reason.lower())
        self.assertIn("history continuity", capability.gap_reason.lower())
        self.assertIn("history continuity", capability.recommended_handoff_theme.lower())
        self.assertIn("161725.fund_cn", capability.recommended_handoff_theme.lower())
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)

    def test_fund_nav_capability_remains_partial_after_batch_hardening(self) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "fund_nav"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertEqual(capability.dataset_mappings, (DatasetName.FUND_NAV_SNAPSHOT,))
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertIn("exchange etf", capability.gap_reason.lower())
        self.assertIn("fund_cn", capability.gap_reason.lower())
        self.assertIn("0-prefix", capability.gap_reason.lower())
        self.assertIn("fund classes remain unproven", capability.gap_reason.lower())
        self.assertIn("fund_cn", capability.recommended_handoff_theme.lower())
        self.assertIn("route redundancy", capability.recommended_handoff_theme.lower())
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)

    def test_a_share_valuation_history_capability_remains_partial_after_batch_hardening(
        self,
    ) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "a_share_valuation_history"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertEqual(capability.dataset_mappings, (DatasetName.VALUATION_SNAPSHOT,))
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertIn("multi-symbol", capability.gap_reason.lower())
        self.assertIn("eastmoney", capability.gap_reason.lower())
        self.assertIn("full-history", capability.gap_reason.lower())
        self.assertIn("baidu plus eastmoney valuation routes", capability.recommended_handoff_theme.lower())
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)

    def test_a_share_capital_flow_capability_remains_partial_after_batch_hardening(
        self,
    ) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "a_share_capital_flow"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertEqual(
            capability.dataset_mappings,
            (DatasetName.CAPITAL_FLOW_SNAPSHOT,),
        )
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertIn("multi-symbol", capability.gap_reason.lower())
        self.assertIn("eastmoney", capability.gap_reason.lower())
        self.assertIn("latest-only snapshot coverage", capability.gap_reason.lower())
        self.assertIn("datacenter fallback", capability.recommended_handoff_theme.lower())
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)

    def test_hk_valuation_history_capability_remains_partial_after_history_hardening(
        self,
    ) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "hk_valuation_history"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertEqual(capability.dataset_mappings, (DatasetName.VALUATION_SNAPSHOT,))
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertIn("multi-symbol", capability.gap_reason.lower())
        self.assertIn("stock_hk_indicator_eniu", capability.gap_reason)
        self.assertIn("2022-07-13", capability.gap_reason)
        self.assertIn("current-dated", capability.gap_reason.lower())
        self.assertIn("stock_hk_valuation_baidu", capability.recommended_handoff_theme)
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)

    def test_a_share_northbound_flow_capability_uses_dedicated_contract_profile(self) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "a_share_northbound_flow"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertEqual(
            capability.dataset_mappings,
            (DatasetName.NORTHBOUND_FLOW_SNAPSHOT,),
        )
        self.assertEqual(capability.source_family_ids, ("akshare_cn_hk_public_family",))
        self.assertIn("symbol x date", capability.granularity.lower())
        self.assertIn("stock_hsgt_individual_em", capability.gap_reason)
        self.assertIn("market-level quota", capability.gap_reason.lower())
        self.assertIn("public-source redundancy", capability.recommended_handoff_theme.lower())
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)

    def test_a_share_turnover_liquidity_capability_uses_dedicated_contract_profile(
        self,
    ) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "a_share_turnover_liquidity"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertEqual(
            capability.dataset_mappings,
            (DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT,),
        )
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertIn("tushare_pro_cn_core", capability.source_family_ids)
        self.assertIn("stock_zh_a_hist", capability.gap_reason)
        self.assertIn("turnover-rate", capability.gap_reason.lower())
        self.assertIn("public-source redundancy", capability.gap_reason.lower())
        self.assertIn("stock_zh_a_hist", capability.recommended_handoff_theme)
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)

    def test_a_share_financial_statements_capability_remains_partial_after_batch_hardening(
        self,
    ) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "a_share_financial_statements"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertEqual(
            capability.dataset_mappings,
            (DatasetName.FINANCIAL_STATEMENTS,),
        )
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertIn("multi-symbol", capability.gap_reason.lower())
        self.assertIn("report-period", capability.gap_reason.lower())
        self.assertIn("sina", capability.gap_reason.lower())
        self.assertIn("source-route provenance", capability.gap_reason.lower())
        self.assertIn("breadth", capability.recommended_handoff_theme.lower())
        self.assertIn("history continuity", capability.recommended_handoff_theme.lower())
        self.assertIn("public-source redundancy", capability.recommended_handoff_theme.lower())
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)

    def test_a_share_financial_indicators_capability_remains_partial_after_batch_hardening(
        self,
    ) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "a_share_financial_indicators"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertEqual(
            capability.dataset_mappings,
            (DatasetName.FINANCIAL_INDICATORS,),
        )
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertIn("multi-symbol", capability.gap_reason.lower())
        self.assertIn("report-period", capability.gap_reason.lower())
        self.assertIn("stock_financial_analysis_indicator_em", capability.gap_reason)
        self.assertIn("source-route", capability.gap_reason.lower())
        self.assertIn("indicator-family", capability.gap_reason.lower())
        self.assertIn("breadth", capability.recommended_handoff_theme.lower())
        self.assertIn("history continuity", capability.recommended_handoff_theme.lower())
        self.assertIn("public-source redundancy", capability.recommended_handoff_theme.lower())
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)

    def test_hk_financial_data_capability_remains_partial_after_batch_hardening(self) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "hk_financial_data"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertEqual(
            capability.dataset_mappings,
            (DatasetName.FINANCIAL_STATEMENTS, DatasetName.FINANCIAL_INDICATORS),
        )
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertIn("multi-symbol", capability.gap_reason.lower())
        self.assertIn("report-period", capability.gap_reason.lower())
        self.assertIn("stock_financial_hk_report_em", capability.gap_reason)
        self.assertIn("stock_financial_hk_analysis_indicator_em", capability.gap_reason)
        self.assertIn("source-route", capability.gap_reason.lower())
        self.assertIn("metric-family", capability.gap_reason.lower())
        self.assertIn("breadth", capability.recommended_handoff_theme.lower())
        self.assertIn("history continuity", capability.recommended_handoff_theme.lower())
        self.assertIn("source-route", capability.recommended_handoff_theme.lower())
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)

    def test_fund_holdings_capability_remains_partial_after_batch_hardening(self) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "fund_holdings_composition"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertEqual(capability.dataset_mappings, (DatasetName.FUND_HOLDINGS,))
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertIn("multi-symbol", capability.gap_reason.lower())
        self.assertIn("report-period", capability.gap_reason.lower())
        self.assertIn("fund_portfolio_hold_em", capability.gap_reason)
        self.assertIn("explicit fund_cn", capability.gap_reason.lower())
        self.assertIn("non-a-share", capability.gap_reason.lower())
        self.assertIn("breadth", capability.recommended_handoff_theme.lower())
        self.assertIn("history continuity", capability.recommended_handoff_theme.lower())
        self.assertIn("route redundancy", capability.recommended_handoff_theme.lower())
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)

    def test_fund_flow_capability_remains_partial_after_batch_hardening(self) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "fund_flow"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertEqual(capability.dataset_mappings, (DatasetName.FUND_FLOW,))
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertIn("multi-symbol", capability.gap_reason.lower())
        self.assertIn("bounded date-window", capability.gap_reason.lower())
        self.assertIn("source-route truth", capability.gap_reason.lower())
        self.assertIn("fund_etf_scale_sse", capability.gap_reason)
        self.assertIn("fund_scale_daily_szse", capability.gap_reason)
        self.assertIn("fund_scale_change_em", capability.gap_reason)
        self.assertIn("fund_purchase_em", capability.gap_reason)
        self.assertIn("fund_etf_scale_szse", capability.gap_reason)
        self.assertIn("subscription/redemption", capability.gap_reason.lower())
        self.assertIn("per-fund dated", capability.recommended_handoff_theme.lower())
        self.assertIn("route limits", capability.recommended_handoff_theme.lower())
        self.assertIn("history continuity", capability.recommended_handoff_theme.lower())
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)

    def test_fund_scale_and_share_capability_uses_dedicated_contract_and_remains_partial(
        self,
    ) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "fund_scale_and_share"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertEqual(
            capability.dataset_mappings,
            (DatasetName.FUND_SCALE_SHARE_SNAPSHOT,),
        )
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertIn("tushare_pro_cn_core", capability.source_family_ids)
        self.assertIn("dedicated adapter-backed", capability.gap_reason.lower())
        self.assertIn("fund_etf_scale_sse", capability.gap_reason)
        self.assertIn("fund_scale_daily_szse", capability.gap_reason)
        self.assertIn("fund_scale_open_sina", capability.gap_reason)
        self.assertIn("fund_scale_close_sina", capability.gap_reason)
        self.assertIn("request-scoped", capability.gap_reason.lower())
        self.assertIn("fund families", capability.gap_reason.lower())
        self.assertIn("history continuity", capability.gap_reason.lower())
        self.assertIn("redundancy", capability.gap_reason.lower())
        self.assertIn("scale-unit semantics", capability.recommended_handoff_theme.lower())
        self.assertIn("latest snapshot fallback", capability.recommended_handoff_theme.lower())
        self.assertIn("route redundancy", capability.recommended_handoff_theme.lower())
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)

    def test_fund_premium_discount_capability_uses_dedicated_contract_and_remains_partial(
        self,
    ) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "fund_premium_discount"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertEqual(
            capability.dataset_mappings,
            (DatasetName.FUND_PREMIUM_DISCOUNT,),
        )
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertIn("latest-available", capability.gap_reason.lower())
        self.assertIn("historical premium-discount continuity", capability.gap_reason.lower())
        self.assertIn("161725.fund_cn", capability.gap_reason.lower())
        self.assertIn("off-exchange fund coverage", capability.gap_reason.lower())
        self.assertIn("request-scoped historical", capability.recommended_handoff_theme.lower())
        self.assertIn("direct public premium-discount redundancy", capability.recommended_handoff_theme.lower())
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)

    def test_adjustment_factors_capability_uses_dedicated_contract_and_remains_partial(
        self,
    ) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "a_share_adjustment_factors"
        )

        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertEqual(
            capability.dataset_mappings,
            (DatasetName.ADJUSTMENT_FACTORS,),
        )
        self.assertEqual(capability.source_family_ids, ("akshare_cn_hk_public_family",))
        self.assertIn("qfq/hfq", capability.gap_reason.lower())
        self.assertIn("per-trade-date continuity", capability.gap_reason.lower())
        self.assertIn("public-source redundancy", capability.recommended_handoff_theme.lower())
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)

    def test_company_announcements_capability_uses_public_akshare_source_family(self) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "a_share_company_announcements"
        )
        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertIn("tushare_pro_cn_core", capability.source_family_ids)
        self.assertIn("multi-symbol", capability.gap_reason)
        self.assertIn("route provenance", capability.gap_reason)
        self.assertIn("public-source redundancy", capability.recommended_handoff_theme)

    def test_cross_market_company_announcements_capability_keeps_a_share_conservative(self) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "company_announcements_cross_market"
        )
        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertIn("partial", capability.gap_reason)
        self.assertNotIn("planned", capability.gap_reason.lower())

    def test_major_activity_events_capability_uses_public_akshare_source_family(self) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "a_share_major_activity_events"
        )
        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertIn("tushare_pro_cn_core", capability.source_family_ids)

    def test_limit_up_down_capability_uses_dedicated_contract_and_is_partial(self) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "a_share_limit_up_down"
        )

        self.assertEqual(
            capability.dataset_mappings,
            (DatasetName.LIMIT_UP_DOWN_EVENTS,),
        )
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)
        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertIn("previous-day limit-up", capability.gap_reason.lower())
        self.assertIn("broken-board", capability.gap_reason.lower())
        self.assertIn("strong-pool/sub-new breadth", capability.recommended_handoff_theme.lower())
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)

    def test_suspension_resumption_capability_uses_dedicated_contract_and_is_partial(
        self,
    ) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "a_share_suspension_resumption"
        )

        self.assertEqual(
            capability.dataset_mappings,
            (DatasetName.SUSPENSION_RESUMPTION_EVENTS,),
        )
        self.assertNotEqual(capability.status, CapabilityStatus.COVERED)
        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertIn("breadth", capability.gap_reason.lower())
        self.assertIn("eastmoney", capability.gap_reason.lower())
        self.assertIn("baidu", capability.gap_reason.lower())
        self.assertIn("completed resumption continuity", capability.recommended_handoff_theme.lower())
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertIn("tushare_pro_cn_core", capability.source_family_ids)

    def test_listing_delisting_st_status_capability_uses_dedicated_contract_and_is_partial(
        self,
    ) -> None:
        capability = next(
            capability
            for capability in get_required_capabilities()
            if capability.capability_id == "a_share_listing_delisting_st_status"
        )

        self.assertEqual(
            capability.dataset_mappings,
            (DatasetName.INSTRUMENT_STATUS_HISTORY,),
        )
        self.assertEqual(capability.status, CapabilityStatus.PARTIAL)
        self.assertIn("current normal/st snapshots", capability.gap_reason.lower())
        self.assertIn("suspension-to-delist lifecycle evidence", capability.gap_reason.lower())
        self.assertIn("dated st/*st continuity", capability.recommended_handoff_theme.lower())
        self.assertIn("terminal lifecycle events", capability.recommended_handoff_theme.lower())
        self.assertIn("akshare_cn_hk_public_family", capability.source_family_ids)
        self.assertIn("tushare_pro_cn_core", capability.source_family_ids)

    def test_module_level_helpers_match_audit_methods(self) -> None:
        audit = build_default_source_capability_audit()

        self.assertEqual(get_required_capabilities(), audit.required_capabilities())
        self.assertEqual(
            get_capabilities_by_domain(CapabilityDomain.A_SHARE),
            audit.capabilities_by_domain(CapabilityDomain.A_SHARE),
        )
        self.assertEqual(
            get_missing_capabilities(),
            audit.missing_capabilities(),
        )
        self.assertEqual(
            get_partial_capabilities(),
            audit.partial_capabilities(),
        )

    def test_offline_only_no_network_use(self) -> None:
        with patch.object(
            socket,
            "create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            _ = get_required_capabilities()
            _ = get_capabilities_by_horizon(ResearchHorizon.SHORT_TERM)
            _ = get_capabilities_by_domain(CapabilityDomain.A_SHARE)
            _ = get_missing_capabilities()
            _ = get_partial_capabilities()
            _ = get_capabilities_without_dataset_mapping()
            _ = get_capabilities_with_planned_or_credentialed_sources()

    def test_status_enum_distribution_exists(self) -> None:
        audit = build_default_source_capability_audit()
        statuses = {capability.status for capability in audit.all_capabilities()}

        self.assertIn(CapabilityStatus.COVERED, statuses)
        self.assertIn(CapabilityStatus.PARTIAL, statuses)
        self.assertIn(CapabilityStatus.MISSING, statuses)
        self.assertIn(CapabilityStatus.PLANNED, statuses)
        self.assertTrue(
            any(
                capability.requirement == CapabilityRequirement.OPTIONAL
                for capability in audit.all_capabilities()
            )
        )
