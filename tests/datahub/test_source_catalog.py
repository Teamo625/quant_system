import unittest
from unittest.mock import patch

from quant.datahub.datasets import DatasetName
from quant.datahub.source_catalog import (
    AssetDomain,
    GeographyDomain,
    InformationCoverage,
    InformationDomain,
    MarketDomain,
    REQUIRED_ASSET_DOMAINS,
    REQUIRED_DATASETS,
    REQUIRED_GEOGRAPHY_DOMAINS,
    REQUIRED_INFORMATION_DOMAINS,
    REQUIRED_MARKET_DOMAINS,
    SourceCatalog,
    SourceCatalogEntry,
    SourceStage,
    build_default_source_catalog,
)


class SourceCatalogTests(unittest.TestCase):
    def test_default_catalog_covers_all_required_stable_datasets(self) -> None:
        catalog = build_default_source_catalog()

        self.assertTrue(catalog.has_full_dataset_coverage())
        self.assertEqual(catalog.missing_dataset_coverage(), ())

        covered = {
            dataset
            for source in catalog.all_sources()
            for dataset in source.dataset_coverage
        }
        self.assertEqual(covered, set(DatasetName))
        self.assertEqual(set(REQUIRED_DATASETS), set(DatasetName))

    def test_default_catalog_covers_market_asset_geography_and_information_domains(
        self,
    ) -> None:
        catalog = build_default_source_catalog()

        self.assertTrue(catalog.has_full_market_coverage())
        self.assertTrue(catalog.has_full_asset_coverage())
        self.assertTrue(catalog.has_full_geography_coverage())
        self.assertTrue(catalog.has_full_information_coverage())
        self.assertTrue(catalog.has_full_domain_coverage())

        self.assertEqual(catalog.missing_market_coverage(), ())
        self.assertEqual(catalog.missing_asset_coverage(), ())
        self.assertEqual(catalog.missing_geography_coverage(), ())
        self.assertEqual(catalog.missing_information_coverage(), ())

        self.assertEqual(set(REQUIRED_MARKET_DOMAINS), set(catalog.covered_market_domains()))
        self.assertEqual(set(REQUIRED_ASSET_DOMAINS), set(catalog.covered_asset_domains()))
        self.assertEqual(
            set(REQUIRED_GEOGRAPHY_DOMAINS),
            set(catalog.covered_geography_domains()),
        )

    def test_sources_for_dataset_and_information_domain(self) -> None:
        catalog = build_default_source_catalog()

        daily_bar_source_ids = {
            item.source_id
            for item in catalog.sources_for_dataset(DatasetName.DAILY_BARS)
        }
        trading_calendar_source_ids = {
            item.source_id
            for item in catalog.sources_for_dataset(DatasetName.TRADING_CALENDAR)
        }
        index_daily_source_ids = {
            item.source_id
            for item in catalog.sources_for_dataset(DatasetName.INDEX_DAILY_BARS)
        }
        index_constituents_source_ids = {
            item.source_id
            for item in catalog.sources_for_dataset(DatasetName.INDEX_CONSTITUENTS)
        }
        index_weight_history_source_ids = {
            item.source_id
            for item in catalog.sources_for_dataset(DatasetName.INDEX_WEIGHT_HISTORY)
        }
        fund_profile_source_ids = {
            item.source_id
            for item in catalog.sources_for_dataset(DatasetName.FUND_PROFILE)
        }
        fund_premium_discount_source_ids = {
            item.source_id
            for item in catalog.sources_for_dataset(DatasetName.FUND_PREMIUM_DISCOUNT)
        }
        adjustment_factor_source_ids = {
            item.source_id
            for item in catalog.sources_for_dataset(DatasetName.ADJUSTMENT_FACTORS)
        }
        margin_source_ids = {
            item.source_id
            for item in catalog.sources_for_dataset(DatasetName.MARGIN_FINANCING_LENDING)
        }
        minute_source_ids = {
            item.source_id
            for item in catalog.sources_for_dataset(DatasetName.MINUTE_BARS)
        }
        suspension_source_ids = {
            item.source_id
            for item in catalog.sources_for_dataset(
                DatasetName.SUSPENSION_RESUMPTION_EVENTS
            )
        }
        instrument_status_source_ids = {
            item.source_id
            for item in catalog.sources_for_dataset(DatasetName.INSTRUMENT_STATUS_HISTORY)
        }
        limit_up_down_source_ids = {
            item.source_id
            for item in catalog.sources_for_dataset(DatasetName.LIMIT_UP_DOWN_EVENTS)
        }
        major_activity_source_ids = {
            item.source_id
            for item in catalog.sources_for_dataset(DatasetName.MAJOR_ACTIVITY_EVENTS)
        }
        announcements_source_ids = {
            item.source_id
            for item in catalog.sources_for_dataset(DatasetName.COMPANY_ANNOUNCEMENTS)
        }
        northbound_source_ids = {
            item.source_id
            for item in catalog.sources_for_dataset(DatasetName.NORTHBOUND_FLOW_SNAPSHOT)
        }
        turnover_liquidity_source_ids = {
            item.source_id
            for item in catalog.sources_for_dataset(DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT)
        }
        news_source_ids = {
            item.source_id
            for item in catalog.sources_for_information_domain(InformationDomain.NEWS)
        }
        exchange_calendar_source_ids = {
            item.source_id
            for item in catalog.sources_for_information_domain(
                InformationDomain.EXCHANGE_CALENDAR
            )
        }
        index_domain_source_ids = {
            item.source_id
            for item in catalog.sources_for_information_domain(InformationDomain.INDEX_DATA)
        }

        self.assertIn("tushare_pro_cn_core", daily_bar_source_ids)
        self.assertIn("tushare_pro_cn_core", index_weight_history_source_ids)
        self.assertNotIn("akshare_cn_hk_public_family", index_weight_history_source_ids)
        self.assertIn("akshare_cn_hk_public_family", daily_bar_source_ids)
        self.assertIn("akshare_cn_hk_public_family", trading_calendar_source_ids)
        self.assertIn("akshare_cn_hk_public_family", index_daily_source_ids)
        self.assertIn("akshare_cn_hk_public_family", index_constituents_source_ids)
        self.assertIn("akshare_cn_hk_public_family", fund_profile_source_ids)
        self.assertIn("akshare_cn_hk_public_family", fund_premium_discount_source_ids)
        self.assertEqual(adjustment_factor_source_ids, {"akshare_cn_hk_public_family"})
        self.assertIn("akshare_cn_hk_public_family", margin_source_ids)
        self.assertIn("akshare_cn_hk_public_family", minute_source_ids)
        self.assertIn("baostock_public_cn", minute_source_ids)
        self.assertIn("akshare_cn_hk_public_family", suspension_source_ids)
        self.assertIn("tushare_pro_cn_core", suspension_source_ids)
        self.assertIn("akshare_cn_hk_public_family", instrument_status_source_ids)
        self.assertIn("tushare_pro_cn_core", instrument_status_source_ids)
        self.assertIn("akshare_cn_hk_public_family", limit_up_down_source_ids)
        self.assertIn("akshare_cn_hk_public_family", major_activity_source_ids)
        self.assertIn("tushare_pro_cn_core", major_activity_source_ids)
        self.assertIn("akshare_cn_hk_public_family", announcements_source_ids)
        self.assertEqual(northbound_source_ids, {"akshare_cn_hk_public_family"})
        self.assertIn("tushare_pro_cn_core", turnover_liquidity_source_ids)
        self.assertIn("akshare_cn_hk_public_family", turnover_liquidity_source_ids)
        self.assertIn("hkex_disclosure_and_calendar_family", announcements_source_ids)
        self.assertIn("akshare_cn_hk_public_family", news_source_ids)
        self.assertIn("akshare_cn_hk_public_family", exchange_calendar_source_ids)
        self.assertIn("akshare_cn_hk_public_family", index_domain_source_ids)
        self.assertIn("tushare_pro_cn_core", index_domain_source_ids)

    def test_baostock_public_source_truth_reflects_minute_bar_history_coverage(self) -> None:
        catalog = build_default_source_catalog()
        entry = next(
            source
            for source in catalog.all_sources()
            if source.source_id == "baostock_public_cn"
        )

        self.assertEqual(entry.stage, SourceStage.PRIORITIZED)
        self.assertFalse(entry.requires_credentials)
        self.assertTrue(entry.requires_live_network)
        self.assertEqual(entry.dataset_coverage, (DatasetName.MINUTE_BARS,))
        self.assertEqual(entry.market_coverage, (MarketDomain.A_SHARE,))
        self.assertEqual(entry.asset_coverage, (AssetDomain.STOCK,))
        self.assertIn("5/15/30/60-minute", entry.notes)
        self.assertIn(
            DatasetName.MINUTE_BARS,
            set(
                catalog.stable_datasets_for_information_domain(
                    InformationDomain.A_SHARE_FULL_DATA
                )
            ),
        )

    def test_akshare_public_source_notes_include_corporate_action_taxonomy(self) -> None:
        catalog = build_default_source_catalog()
        entry = next(
            source
            for source in catalog.all_sources()
            if source.source_id == "akshare_cn_hk_public_family"
        )

        self.assertIn("dividend/bonus/transfer", entry.notes)
        self.assertIn("rights-issue", entry.notes)
        self.assertIn("CNInfo-backed bounded", entry.notes)
        self.assertIn("stock_zh_a_hist", entry.notes)
        self.assertNotIn("planned", entry.notes.lower())
        self.assertIn("stock_hk_dividend_payout_em", entry.notes)
        self.assertIn("stock_hk_fhpx_detail_ths", entry.notes)
        self.assertIn("no-distribution decision history", entry.notes)
        self.assertIn("split/rights/consolidation", entry.notes)
        self.assertIn("stock_hk_hist", entry.notes)
        self.assertIn("stock_hk_daily", entry.notes)
        self.assertIn("independent public-source redundancy is still unproven", entry.notes)
        self.assertIn("HK turnover/liquidity proof currently exposes only dated volume", entry.notes)
        self.assertIn("traded amount", entry.notes)
        self.assertIn("turnover-rate", entry.notes)
        self.assertIn("source-route truth", entry.notes)
        self.assertIn("stock_hk_indicator_eniu", entry.notes)
        self.assertIn("stock_hk_valuation_baidu", entry.notes)
        self.assertIn("stale through 2022-07-13", entry.notes)
        self.assertIn("current-dated redundancy is still unproven", entry.notes)
        self.assertIn("stock_financial_hk_report_em", entry.notes)
        self.assertIn("stock_financial_hk_analysis_indicator_em", entry.notes)
        self.assertIn("report-period history", entry.notes)
        self.assertIn("source-route truth", entry.notes)
        self.assertIn("issuer breadth", entry.notes)
        self.assertIn("stock_hk_security_profile_em", entry.notes)
        self.assertIn("stock_hk_spot_em", entry.notes)
        self.assertIn("sina_hk_stock_spot_page1", entry.notes)
        self.assertIn("non-stock taxonomy", entry.notes)
        self.assertIn("delist/inactive lifecycle", entry.notes)

    def test_helper_reports_information_domains_without_stable_contracts(self) -> None:
        catalog = build_default_source_catalog()

        missing_contract_domains = set(
            catalog.information_domains_missing_stable_dataset_contracts()
        )

        self.assertEqual(missing_contract_domains, set())

        self.assertIn(
            DatasetName.SECTOR_MASTER,
            set(
                catalog.stable_datasets_for_information_domain(
                    InformationDomain.INDUSTRY_CONCEPT_SECTOR
                )
            ),
        )
        self.assertIn(
            DatasetName.VALUATION_SNAPSHOT,
            set(
                catalog.stable_datasets_for_information_domain(
                    InformationDomain.A_SHARE_FULL_DATA
                )
            ),
        )
        self.assertIn(
            DatasetName.CAPITAL_FLOW_SNAPSHOT,
            set(
                catalog.stable_datasets_for_information_domain(
                    InformationDomain.A_SHARE_FULL_DATA
                )
            ),
        )
        self.assertIn(
            DatasetName.NORTHBOUND_FLOW_SNAPSHOT,
            set(
                catalog.stable_datasets_for_information_domain(
                    InformationDomain.A_SHARE_FULL_DATA
                )
            ),
        )
        self.assertIn(
            DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT,
            set(
                catalog.stable_datasets_for_information_domain(
                    InformationDomain.A_SHARE_FULL_DATA
                )
            ),
        )
        self.assertIn(
            DatasetName.LIMIT_UP_DOWN_EVENTS,
            set(
                catalog.stable_datasets_for_information_domain(
                    InformationDomain.A_SHARE_FULL_DATA
                )
            ),
        )
        self.assertIn(
            DatasetName.MARGIN_FINANCING_LENDING,
            set(
                catalog.stable_datasets_for_information_domain(
                    InformationDomain.A_SHARE_FULL_DATA
                )
            ),
        )
        self.assertIn(
            DatasetName.MINUTE_BARS,
            set(
                catalog.stable_datasets_for_information_domain(
                    InformationDomain.A_SHARE_FULL_DATA
                )
            ),
        )
        self.assertIn(
            DatasetName.CORPORATE_ACTIONS,
            set(
                catalog.stable_datasets_for_information_domain(
                    InformationDomain.A_SHARE_FULL_DATA
                )
            ),
        )
        self.assertIn(
            DatasetName.ADJUSTMENT_FACTORS,
            set(
                catalog.stable_datasets_for_information_domain(
                    InformationDomain.A_SHARE_FULL_DATA
                )
            ),
        )
        self.assertIn(
            DatasetName.SUSPENSION_RESUMPTION_EVENTS,
            set(
                catalog.stable_datasets_for_information_domain(
                    InformationDomain.A_SHARE_FULL_DATA
                )
            ),
        )
        self.assertIn(
            DatasetName.INSTRUMENT_STATUS_HISTORY,
            set(
                catalog.stable_datasets_for_information_domain(
                    InformationDomain.A_SHARE_FULL_DATA
                )
            ),
        )
        self.assertIn(
            DatasetName.VALUATION_SNAPSHOT,
            set(
                catalog.stable_datasets_for_information_domain(
                    InformationDomain.HK_STOCK_FULL_DATA
                )
            ),
        )
        self.assertIn(
            DatasetName.FUND_PROFILE,
            set(
                catalog.stable_datasets_for_information_domain(
                    InformationDomain.ETF_FUND_FULL_DATA
                )
            ),
        )
        self.assertIn(
            DatasetName.FUND_PREMIUM_DISCOUNT,
            set(
                catalog.stable_datasets_for_information_domain(
                    InformationDomain.ETF_FUND_FULL_DATA
                )
            ),
        )
        self.assertIn(
            DatasetName.DAILY_BARS,
            set(
                catalog.stable_datasets_for_information_domain(
                    InformationDomain.ETF_FUND_FULL_DATA
                )
            ),
        )
        self.assertIn(
            DatasetName.MACRO_OBSERVATIONS,
            set(catalog.stable_datasets_for_information_domain(InformationDomain.GLOBAL_MACRO)),
        )
        self.assertIn(
            DatasetName.POLICY_DOCUMENTS,
            set(catalog.stable_datasets_for_information_domain(InformationDomain.POLICY)),
        )
        self.assertIn(
            DatasetName.NEWS_EVENTS,
            set(catalog.stable_datasets_for_information_domain(InformationDomain.NEWS)),
        )
        self.assertIn(
            DatasetName.COMPANY_ANNOUNCEMENTS,
            set(catalog.stable_datasets_for_information_domain(InformationDomain.ANNOUNCEMENT)),
        )
        self.assertIn(
            DatasetName.INDEX_CONSTITUENTS,
            set(catalog.stable_datasets_for_information_domain(InformationDomain.INDEX_DATA)),
        )
        self.assertIn(
            DatasetName.INDEX_WEIGHT_HISTORY,
            set(catalog.stable_datasets_for_information_domain(InformationDomain.INDEX_DATA)),
        )
        self.assertIn(
            DatasetName.DATA_QUALITY_REPORT,
            set(
                catalog.stable_datasets_for_information_domain(
                    InformationDomain.SOURCE_HEALTH_QUALITY
                )
            ),
        )

    def test_macro_policy_public_source_truth_reflects_implemented_bounded_coverage(self) -> None:
        catalog = build_default_source_catalog()
        entry = next(
            source
            for source in catalog.all_sources()
            if source.source_id == "macro_policy_public_sources"
        )

        self.assertEqual(entry.stage, SourceStage.PRIORITIZED)
        self.assertFalse(entry.requires_credentials)
        self.assertTrue(entry.requires_live_network)
        self.assertEqual(
            set(entry.dataset_coverage),
            {
                DatasetName.MACRO_INDICATOR_MASTER,
                DatasetName.MACRO_OBSERVATIONS,
                DatasetName.POLICY_DOCUMENTS,
            },
        )
        self.assertNotIn("planned", entry.notes.lower())
        self.assertIn("bounded", entry.notes.lower())

    def test_gap_helpers_can_find_missing_coverage(self) -> None:
        catalog = SourceCatalog(
            entries=(
                SourceCatalogEntry(
                    source_id="minimal_cn_equity",
                    source_name="Minimal CN Equity",
                    dataset_coverage=(DatasetName.DAILY_BARS,),
                    information_coverage=(
                        InformationCoverage(
                            InformationDomain.A_SHARE_FULL_DATA,
                            stable_datasets=(DatasetName.DAILY_BARS,),
                        ),
                    ),
                    market_coverage=(MarketDomain.A_SHARE,),
                    asset_coverage=(AssetDomain.STOCK,),
                    geography_coverage=(GeographyDomain.CN_MAINLAND,),
                    requires_credentials=False,
                    requires_live_network=False,
                    stage=SourceStage.PLANNED,
                    priority=9,
                    notes="Synthetic entry for missing coverage tests.",
                ),
            ),
            required_datasets=REQUIRED_DATASETS,
            required_market_domains=REQUIRED_MARKET_DOMAINS,
            required_asset_domains=REQUIRED_ASSET_DOMAINS,
            required_geography_domains=REQUIRED_GEOGRAPHY_DOMAINS,
            required_information_domains=REQUIRED_INFORMATION_DOMAINS,
        )

        self.assertIn(DatasetName.TRADING_CALENDAR, set(catalog.missing_dataset_coverage()))
        self.assertIn(MarketDomain.HONG_KONG, set(catalog.missing_market_coverage()))
        self.assertIn(AssetDomain.ETF, set(catalog.missing_asset_coverage()))
        self.assertIn(
            GeographyDomain.GLOBAL,
            set(catalog.missing_geography_coverage()),
        )
        self.assertIn(
            InformationDomain.NEWS,
            set(catalog.missing_information_coverage()),
        )
        self.assertFalse(catalog.has_full_domain_coverage())
        self.assertFalse(catalog.has_full_dataset_coverage())

    def test_catalog_queries_are_offline_only(self) -> None:
        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            catalog = build_default_source_catalog()
            _ = catalog.missing_dataset_coverage()
            _ = catalog.missing_market_coverage()
            _ = catalog.missing_asset_coverage()
            _ = catalog.missing_geography_coverage()
            _ = catalog.missing_information_coverage()
            _ = catalog.information_domains_missing_stable_dataset_contracts()


if __name__ == "__main__":
    unittest.main()
