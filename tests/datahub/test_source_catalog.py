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
        fund_profile_source_ids = {
            item.source_id
            for item in catalog.sources_for_dataset(DatasetName.FUND_PROFILE)
        }
        margin_source_ids = {
            item.source_id
            for item in catalog.sources_for_dataset(DatasetName.MARGIN_FINANCING_LENDING)
        }
        minute_source_ids = {
            item.source_id
            for item in catalog.sources_for_dataset(DatasetName.MINUTE_BARS)
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
        self.assertIn("akshare_cn_hk_public_family", daily_bar_source_ids)
        self.assertIn("akshare_cn_hk_public_family", trading_calendar_source_ids)
        self.assertIn("akshare_cn_hk_public_family", index_daily_source_ids)
        self.assertIn("akshare_cn_hk_public_family", index_constituents_source_ids)
        self.assertIn("akshare_cn_hk_public_family", fund_profile_source_ids)
        self.assertIn("akshare_cn_hk_public_family", margin_source_ids)
        self.assertIn("akshare_cn_hk_public_family", minute_source_ids)
        self.assertIn("akshare_cn_hk_public_family", limit_up_down_source_ids)
        self.assertIn("akshare_cn_hk_public_family", major_activity_source_ids)
        self.assertIn("tushare_pro_cn_core", major_activity_source_ids)
        self.assertIn("akshare_cn_hk_public_family", announcements_source_ids)
        self.assertIn("hkex_disclosure_and_calendar_family", announcements_source_ids)
        self.assertIn("akshare_cn_hk_public_family", news_source_ids)
        self.assertIn("akshare_cn_hk_public_family", exchange_calendar_source_ids)
        self.assertIn("akshare_cn_hk_public_family", index_domain_source_ids)

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
            DatasetName.DATA_QUALITY_REPORT,
            set(
                catalog.stable_datasets_for_information_domain(
                    InformationDomain.SOURCE_HEALTH_QUALITY
                )
            ),
        )

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
