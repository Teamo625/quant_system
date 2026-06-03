import unittest
from datetime import date, datetime
from unittest.mock import patch

from quant.datahub.datasets import DatasetName, DatasetRegistry, SemanticRuleSet


EXPECTED_REQUIRED_FIELDS = {
    DatasetName.INSTRUMENT_MASTER: {
        "symbol",
        "raw_symbol",
        "name",
        "market",
        "asset_type",
        "currency",
        "exchange",
        "list_date",
        "delist_date",
        "is_active",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.TRADING_CALENDAR: {
        "market",
        "trade_date",
        "is_open",
        "session_type",
        "previous_trade_date",
        "next_trade_date",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.DAILY_BARS: {
        "symbol",
        "market",
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "amount",
        "adj_factor",
        "price_adjustment",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.MINUTE_BARS: {
        "symbol",
        "market",
        "trade_date",
        "bar_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.LIMIT_UP_DOWN_EVENTS: {
        "symbol",
        "market",
        "trade_date",
        "limit_type",
        "up_limit_price",
        "down_limit_price",
        "hit_limit_up",
        "hit_limit_down",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.SUSPENSION_RESUMPTION_EVENTS: {
        "symbol",
        "market",
        "event_date",
        "event_type",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.CORPORATE_ACTIONS: {
        "symbol",
        "market",
        "event_date",
        "event_type",
        "value",
        "raw_payload_ref",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.MARGIN_FINANCING_LENDING: {
        "symbol",
        "market",
        "trade_date",
        "financing_balance",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.VALUATION_SNAPSHOT: {
        "symbol",
        "market",
        "trade_date",
        "pe_ttm",
        "pb",
        "market_cap",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.CAPITAL_FLOW_SNAPSHOT: {
        "symbol",
        "market",
        "trade_date",
        "main_net_inflow",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.DATA_QUALITY_REPORT: {
        "dataset",
        "market",
        "trade_date",
        "check_name",
        "status",
        "severity",
        "details",
        "created_at",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.INDEX_DAILY_BARS: {
        "index_code",
        "index_name",
        "market",
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.INDEX_CONSTITUENTS: {
        "index_code",
        "symbol",
        "market",
        "in_date",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.FUND_PROFILE: {
        "fund_code",
        "fund_name",
        "market",
        "fund_type",
        "management_company",
        "inception_date",
        "currency",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.FUND_NAV_SNAPSHOT: {
        "fund_code",
        "market",
        "trade_date",
        "nav",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.FUND_HOLDINGS: {
        "fund_code",
        "symbol",
        "market",
        "report_date",
        "weight",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.FUND_FLOW: {
        "fund_code",
        "market",
        "trade_date",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.FINANCIAL_STATEMENTS: {
        "symbol",
        "market",
        "report_period_end",
        "statement_type",
        "period_type",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.FINANCIAL_INDICATORS: {
        "symbol",
        "market",
        "report_period_end",
        "period_type",
        "metric_code",
        "metric_value",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.MAJOR_ACTIVITY_EVENTS: {
        "event_id",
        "symbol",
        "market",
        "event_date",
        "event_type",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.SECTOR_MASTER: {
        "sector_id",
        "sector_name",
        "sector_type",
        "market",
        "is_active",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.SECTOR_MEMBERSHIP: {
        "sector_id",
        "symbol",
        "market",
        "in_date",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.SECTOR_DAILY_BARS: {
        "sector_id",
        "market",
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.MACRO_INDICATOR_MASTER: {
        "indicator_id",
        "indicator_name",
        "region",
        "frequency",
        "unit",
        "category",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.MACRO_OBSERVATIONS: {
        "indicator_id",
        "region",
        "observation_date",
        "value",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.POLICY_DOCUMENTS: {
        "policy_id",
        "region",
        "publish_date",
        "title",
        "authority",
        "document_type",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.NEWS_EVENTS: {
        "news_id",
        "region",
        "publish_time",
        "title",
        "source_name",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.COMPANY_ANNOUNCEMENTS: {
        "announcement_id",
        "symbol",
        "market",
        "publish_time",
        "announcement_type",
        "title",
        "source",
        "ingested_at",
        "schema_version",
    },
    DatasetName.GLOBAL_EQUITY_SNAPSHOT: {
        "symbol",
        "market",
        "trade_date",
        "close",
        "change_pct",
        "currency",
        "exchange",
        "region",
        "source",
        "ingested_at",
        "schema_version",
    },
}


NEW_DATASET_VALID_RECORDS = {
    DatasetName.MINUTE_BARS: {
        "symbol": "600000.SH",
        "market": "CN",
        "trade_date": "2024-01-02",
        "bar_time": "2024-01-02T09:31:00",
        "open": 10.0,
        "high": 10.1,
        "low": 9.9,
        "close": 10.05,
        "volume": 100000,
        "amount": 1000000,
        "source": "fixture",
        "ingested_at": "2024-01-02T10:00:00",
        "schema_version": "v1",
    },
    DatasetName.MARGIN_FINANCING_LENDING: {
        "symbol": "600000.SH",
        "market": "CN",
        "trade_date": "2024-01-02",
        "financing_balance": 3_000_000_000,
        "financing_buy_amount": 120_000_000,
        "financing_repay_amount": 90_000_000,
        "source": "fixture",
        "ingested_at": "2024-01-02T10:00:00",
        "schema_version": "v1",
    },
    DatasetName.LIMIT_UP_DOWN_EVENTS: {
        "symbol": "600000.SH",
        "market": "CN",
        "trade_date": "2024-01-02",
        "limit_type": "one_word_limit_up",
        "up_limit_price": 11.2,
        "down_limit_price": 9.2,
        "hit_limit_up": True,
        "hit_limit_down": False,
        "open_status": "open_board",
        "close_status": "sealed",
        "seal_status": "strong",
        "consecutive_limit_count": 2,
        "event_category": "limit_up_pool",
        "raw_event_type": "zha_ban",
        "source": "fixture",
        "ingested_at": "2024-01-02T16:00:00",
        "schema_version": "v1",
    },
    DatasetName.SUSPENSION_RESUMPTION_EVENTS: {
        "symbol": "600000.SH",
        "market": "CN",
        "event_date": "2024-01-03",
        "event_type": "resumption",
        "start_date": "2024-01-02",
        "end_date": "2024-01-03",
        "reason": "major asset restructuring disclosure",
        "raw_status": "resume_trading",
        "exchange": "SSE",
        "board": "main_board",
        "source": "fixture",
        "ingested_at": "2024-01-03T09:20:00",
        "schema_version": "v1",
    },
    DatasetName.INDEX_DAILY_BARS: {
        "index_code": "000300.SH",
        "index_name": "CSI 300",
        "market": "CN",
        "trade_date": "2024-01-02",
        "open": 3300.0,
        "high": 3310.0,
        "low": 3290.0,
        "close": 3305.0,
        "source": "fixture",
        "ingested_at": "2024-01-02T10:00:00",
        "schema_version": "v1",
    },
    DatasetName.INDEX_CONSTITUENTS: {
        "index_code": "000300.SH",
        "symbol": "600000.SH",
        "market": "CN",
        "in_date": "2020-01-01",
        "weight": 0.52,
        "source": "fixture",
        "ingested_at": "2024-01-02T10:00:00",
        "schema_version": "v1",
    },
    DatasetName.FUND_PROFILE: {
        "fund_code": "510300.SH",
        "fund_name": "CSI 300 ETF",
        "market": "CN",
        "fund_type": "ETF",
        "management_company": "Example AMC",
        "inception_date": "2012-05-01",
        "currency": "CNY",
        "source": "fixture",
        "ingested_at": "2024-01-02T10:00:00",
        "schema_version": "v1",
    },
    DatasetName.FUND_NAV_SNAPSHOT: {
        "fund_code": "510300.SH",
        "market": "CN",
        "trade_date": "2024-01-02",
        "nav": 3.21,
        "accumulated_nav": 5.68,
        "source": "fixture",
        "ingested_at": "2024-01-02T10:00:00",
        "schema_version": "v1",
    },
    DatasetName.FUND_HOLDINGS: {
        "fund_code": "510300.SH",
        "symbol": "600519.SH",
        "market": "CN",
        "report_date": "2024-03-31",
        "weight": 0.05,
        "shares": 1000000,
        "source": "fixture",
        "ingested_at": "2024-04-01T10:00:00",
        "schema_version": "v1",
    },
    DatasetName.FUND_FLOW: {
        "fund_code": "510300.SH",
        "market": "CN",
        "trade_date": "2024-01-02",
        "net_inflow": 12000000,
        "subscription_amount": 30000000,
        "redemption_amount": 18000000,
        "shares_change": 4000000,
        "source": "fixture",
        "ingested_at": "2024-01-02T16:00:00",
        "schema_version": "v1",
    },
    DatasetName.FINANCIAL_STATEMENTS: {
        "symbol": "600000.SH",
        "market": "CN",
        "report_period_end": "2023-12-31",
        "statement_type": "income_statement",
        "period_type": "annual",
        "currency": "CNY",
        "revenue": 230000000000,
        "net_profit": 38000000000,
        "total_assets": 9500000000000,
        "total_liabilities": 8700000000000,
        "source": "fixture",
        "ingested_at": "2024-03-31T12:00:00",
        "schema_version": "v1",
    },
    DatasetName.FINANCIAL_INDICATORS: {
        "symbol": "00700.HK",
        "market": "HK",
        "report_period_end": "2023-12-31",
        "period_type": "annual",
        "metric_code": "roe",
        "metric_name": "Return On Equity",
        "metric_value": 12.5,
        "unit": "pct",
        "source": "fixture",
        "ingested_at": "2024-03-31T12:30:00",
        "schema_version": "v1",
    },
    DatasetName.MAJOR_ACTIVITY_EVENTS: {
        "event_id": "ACT-2024-001",
        "symbol": "600000.SH",
        "market": "CN",
        "event_date": "2024-01-10",
        "event_type": "block_trade",
        "participant": "institutional",
        "direction": "buy",
        "event_value": 22000000,
        "event_volume": 1800000,
        "source": "fixture",
        "ingested_at": "2024-01-10T16:30:00",
        "schema_version": "v1",
    },
    DatasetName.SECTOR_MASTER: {
        "sector_id": "BK001",
        "sector_name": "Semiconductor",
        "sector_type": "industry",
        "market": "CN",
        "is_active": True,
        "source": "fixture",
        "ingested_at": "2024-01-02T10:00:00",
        "schema_version": "v1",
    },
    DatasetName.SECTOR_MEMBERSHIP: {
        "sector_id": "BK001",
        "symbol": "688981.SH",
        "market": "CN",
        "in_date": "2022-01-01",
        "source": "fixture",
        "ingested_at": "2024-01-02T10:00:00",
        "schema_version": "v1",
    },
    DatasetName.SECTOR_DAILY_BARS: {
        "sector_id": "BK001",
        "market": "CN",
        "trade_date": "2024-01-02",
        "open": 1200.0,
        "high": 1220.0,
        "low": 1190.0,
        "close": 1210.0,
        "source": "fixture",
        "ingested_at": "2024-01-02T10:00:00",
        "schema_version": "v1",
    },
    DatasetName.MACRO_INDICATOR_MASTER: {
        "indicator_id": "CPI_CN_YOY",
        "indicator_name": "China CPI YoY",
        "region": "CN",
        "frequency": "monthly",
        "unit": "pct",
        "category": "inflation",
        "source": "fixture",
        "ingested_at": "2024-01-02T10:00:00",
        "schema_version": "v1",
    },
    DatasetName.MACRO_OBSERVATIONS: {
        "indicator_id": "CPI_CN_YOY",
        "region": "CN",
        "observation_date": "2024-01-01",
        "value": 0.2,
        "release_date": "2024-01-10",
        "source": "fixture",
        "ingested_at": "2024-01-10T10:00:00",
        "schema_version": "v1",
    },
    DatasetName.POLICY_DOCUMENTS: {
        "policy_id": "POLICY-2024-001",
        "region": "CN",
        "publish_date": "2024-01-15",
        "title": "Sample Policy",
        "authority": "NDRC",
        "document_type": "guideline",
        "source": "fixture",
        "ingested_at": "2024-01-15T10:00:00",
        "schema_version": "v1",
    },
    DatasetName.NEWS_EVENTS: {
        "news_id": "NEWS-2024-001",
        "region": "GLOBAL",
        "publish_time": "2024-01-15T08:00:00",
        "title": "Market update",
        "source_name": "ExampleWire",
        "source": "fixture",
        "ingested_at": "2024-01-15T09:00:00",
        "schema_version": "v1",
    },
    DatasetName.COMPANY_ANNOUNCEMENTS: {
        "announcement_id": "ANN-2024-001",
        "symbol": "00700.HK",
        "market": "HK",
        "publish_time": "2024-01-20T19:00:00",
        "announcement_type": "earnings",
        "title": "Annual Results",
        "source": "fixture",
        "ingested_at": "2024-01-20T19:30:00",
        "schema_version": "v1",
    },
    DatasetName.GLOBAL_EQUITY_SNAPSHOT: {
        "symbol": "AAPL.US",
        "market": "US",
        "trade_date": "2024-01-02",
        "close": 185.1,
        "change_pct": 0.8,
        "currency": "USD",
        "exchange": "NASDAQ",
        "region": "GLOBAL",
        "source": "fixture",
        "ingested_at": "2024-01-03T08:00:00",
        "schema_version": "v1",
    },
}


class DatasetRegistryTests(unittest.TestCase):
    def test_registry_contains_contract_datasets(self) -> None:
        registry = DatasetRegistry()

        self.assertEqual(registry.get(DatasetName.DAILY_BARS).schema_version, "v1")
        self.assertEqual(
            registry.get(DatasetName.INSTRUMENT_MASTER).name,
            DatasetName.INSTRUMENT_MASTER,
        )

    def test_registry_all_is_stable_tuple(self) -> None:
        registry = DatasetRegistry()
        datasets = registry.all()

        self.assertIsInstance(datasets, tuple)
        self.assertEqual({item.name for item in datasets}, set(DatasetName))

    def test_every_dataset_has_schema_contract(self) -> None:
        registry = DatasetRegistry()

        schemas = registry.all_schemas()

        self.assertIsInstance(schemas, tuple)
        self.assertEqual({schema.dataset for schema in schemas}, set(DatasetName))

    def test_schema_versions_match_dataset_info(self) -> None:
        registry = DatasetRegistry()

        for info in registry.all():
            with self.subTest(dataset=info.name.value):
                schema = registry.get_schema(info.name)
                self.assertEqual(schema.schema_version, info.schema_version)

    def test_required_fields_align_with_dataset_contracts(self) -> None:
        registry = DatasetRegistry()

        self.assertEqual(set(EXPECTED_REQUIRED_FIELDS), set(DatasetName))
        for dataset_name, expected_fields in EXPECTED_REQUIRED_FIELDS.items():
            with self.subTest(dataset=dataset_name.value):
                schema = registry.get_schema(dataset_name)
                required_fields = set(schema.required_fields())
                self.assertTrue(expected_fields.issubset(required_fields))

    def test_validate_required_fields_detects_missing_fields(self) -> None:
        registry = DatasetRegistry()

        missing = registry.validate_required_fields(
            DatasetName.DAILY_BARS,
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": "2024-01-02",
                "open": 10.0,
            },
        )

        self.assertIn("close", missing)
        self.assertIn("volume", missing)
        self.assertIn("source", missing)

    def test_validate_record_returns_structured_missing_field_issues(self) -> None:
        registry = DatasetRegistry()

        issues = registry.validate_record(
            DatasetName.TRADING_CALENDAR,
            {
                "market": "CN",
                "trade_date": "2024-01-02",
            },
        )

        self.assertGreaterEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "missing_required_field")
        self.assertTrue(issues[0].field)

    def test_validate_record_detects_type_mismatch(self) -> None:
        registry = DatasetRegistry()

        issues = registry.validate_record(
            DatasetName.DAILY_BARS,
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": "2024-01-02",
                "open": "10.0",
                "high": 10.2,
                "low": 9.8,
                "close": 10.1,
                "volume": 1000,
                "amount": 10000,
                "adj_factor": 1.0,
                "price_adjustment": "raw",
                "source": "fixture",
                "ingested_at": "2024-01-02T10:00:00",
                "schema_version": "v1",
            },
        )

        self.assertTrue(any(issue.code == "type_mismatch" for issue in issues))

    def test_validate_record_accepts_iso_and_native_date_types(self) -> None:
        registry = DatasetRegistry()

        iso_issues = registry.validate_record(
            DatasetName.TRADING_CALENDAR,
            {
                "market": "CN",
                "trade_date": "2024-01-02",
                "is_open": True,
                "session_type": "full",
                "previous_trade_date": "2024-01-01",
                "next_trade_date": "2024-01-03",
                "source": "fixture",
                "ingested_at": "2024-01-02T10:00:00",
                "schema_version": "v1",
            },
        )
        native_issues = registry.validate_record(
            DatasetName.TRADING_CALENDAR,
            {
                "market": "CN",
                "trade_date": date(2024, 1, 2),
                "is_open": True,
                "session_type": "full",
                "previous_trade_date": date(2024, 1, 1),
                "next_trade_date": date(2024, 1, 3),
                "source": "fixture",
                "source_ts": datetime(2024, 1, 2, 10, 0, 0),
                "ingested_at": datetime(2024, 1, 2, 10, 0, 0),
                "schema_version": "v1",
            },
        )

        self.assertEqual(iso_issues, ())
        self.assertEqual(native_issues, ())

    def test_validate_record_allows_missing_optional_field(self) -> None:
        registry = DatasetRegistry()

        issues = registry.validate_record(
            DatasetName.DATA_QUALITY_REPORT,
            {
                "dataset": "daily_bars",
                "market": "CN",
                "trade_date": "2024-01-02",
                "check_name": "completeness",
                "status": "pass",
                "severity": "low",
                "details": "ok",
                "created_at": "2024-01-02T10:00:00",
                "source": "fixture",
                "ingested_at": "2024-01-02T10:00:01",
                "schema_version": "v1",
            },
        )

        self.assertEqual(issues, ())

    def test_new_dataset_schemas_accept_representative_valid_records(self) -> None:
        registry = DatasetRegistry()

        for dataset_name, record in NEW_DATASET_VALID_RECORDS.items():
            with self.subTest(dataset=dataset_name.value):
                issues = registry.validate_record(dataset_name, record)
                self.assertEqual(issues, ())

    def test_new_dataset_missing_fields_are_reported(self) -> None:
        registry = DatasetRegistry()

        issues = registry.validate_record(
            DatasetName.COMPANY_ANNOUNCEMENTS,
            {
                "announcement_id": "ANN-2024-001",
                "source": "fixture",
                "ingested_at": "2024-01-20T19:30:00",
                "schema_version": "v1",
            },
        )

        missing_fields = {
            issue.field
            for issue in issues
            if issue.code == "missing_required_field"
        }
        self.assertIn("symbol", missing_fields)
        self.assertIn("market", missing_fields)
        self.assertIn("publish_time", missing_fields)
        self.assertIn("announcement_type", missing_fields)
        self.assertIn("title", missing_fields)

    def test_new_dataset_type_mismatch_is_reported(self) -> None:
        registry = DatasetRegistry()

        issues = registry.validate_record(
            DatasetName.MACRO_OBSERVATIONS,
            {
                "indicator_id": "CPI_CN_YOY",
                "region": "CN",
                "observation_date": "2024-01-01",
                "value": "0.2",
                "source": "fixture",
                "ingested_at": "2024-01-10T10:00:00",
                "schema_version": "v1",
            },
        )

        self.assertTrue(
            any(issue.code == "type_mismatch" and issue.field == "value" for issue in issues)
        )

    def test_task_042_contract_missing_required_field_is_reported(self) -> None:
        registry = DatasetRegistry()

        issues = registry.validate_record(
            DatasetName.MINUTE_BARS,
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": "2024-01-02",
                "open": 10.0,
                "high": 10.1,
                "low": 9.9,
                "close": 10.05,
                "volume": 100000,
                "source": "fixture",
                "ingested_at": "2024-01-02T10:00:00",
                "schema_version": "v1",
            },
        )

        self.assertTrue(
            any(
                issue.code == "missing_required_field"
                and issue.field == "bar_time"
                for issue in issues
            )
        )

    def test_task_042_contract_type_mismatch_is_reported(self) -> None:
        registry = DatasetRegistry()

        issues = registry.validate_record(
            DatasetName.FINANCIAL_INDICATORS,
            {
                "symbol": "00700.HK",
                "market": "HK",
                "report_period_end": "2023-12-31",
                "period_type": "annual",
                "metric_code": "roe",
                "metric_value": "12.5",
                "source": "fixture",
                "ingested_at": "2024-03-31T12:30:00",
                "schema_version": "v1",
            },
        )

        self.assertTrue(
            any(
                issue.code == "type_mismatch"
                and issue.field == "metric_value"
                for issue in issues
            )
        )

    def test_limit_up_down_contract_missing_required_field_is_reported(self) -> None:
        registry = DatasetRegistry()

        issues = registry.validate_record(
            DatasetName.LIMIT_UP_DOWN_EVENTS,
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": "2024-01-02",
                "up_limit_price": 11.2,
                "down_limit_price": 9.2,
                "hit_limit_up": True,
                "hit_limit_down": False,
                "source": "fixture",
                "ingested_at": "2024-01-02T16:00:00",
                "schema_version": "v1",
            },
        )

        self.assertTrue(
            any(
                issue.code == "missing_required_field"
                and issue.field == "limit_type"
                for issue in issues
            )
        )

    def test_limit_up_down_contract_type_mismatch_is_reported(self) -> None:
        registry = DatasetRegistry()
        record = dict(NEW_DATASET_VALID_RECORDS[DatasetName.LIMIT_UP_DOWN_EVENTS])
        record["hit_limit_up"] = "True"

        issues = registry.validate_record(DatasetName.LIMIT_UP_DOWN_EVENTS, record)

        self.assertTrue(
            any(
                issue.code == "type_mismatch"
                and issue.field == "hit_limit_up"
                for issue in issues
            )
        )

    def test_suspension_resumption_contract_missing_required_field_is_reported(self) -> None:
        registry = DatasetRegistry()

        issues = registry.validate_record(
            DatasetName.SUSPENSION_RESUMPTION_EVENTS,
            {
                "symbol": "600000.SH",
                "market": "CN",
                "event_date": "2024-01-03",
                "source": "fixture",
                "ingested_at": "2024-01-03T09:20:00",
                "schema_version": "v1",
            },
        )

        self.assertTrue(
            any(
                issue.code == "missing_required_field"
                and issue.field == "event_type"
                for issue in issues
            )
        )

    def test_suspension_resumption_contract_type_mismatch_is_reported(self) -> None:
        registry = DatasetRegistry()
        record = dict(NEW_DATASET_VALID_RECORDS[DatasetName.SUSPENSION_RESUMPTION_EVENTS])
        record["event_date"] = "2024/01/03"

        issues = registry.validate_record(DatasetName.SUSPENSION_RESUMPTION_EVENTS, record)

        self.assertTrue(
            any(
                issue.code == "type_mismatch"
                and issue.field == "event_date"
                for issue in issues
            )
        )

    def test_suspension_resumption_semantics_reject_invalid_date_range(self) -> None:
        registry = DatasetRegistry()
        record = dict(NEW_DATASET_VALID_RECORDS[DatasetName.SUSPENSION_RESUMPTION_EVENTS])
        record["end_date"] = "2024-01-01"

        issues = registry.validate_record(DatasetName.SUSPENSION_RESUMPTION_EVENTS, record)

        self.assertTrue(
            any(
                issue.code == "invalid_date_range"
                and issue.field == "end_date"
                for issue in issues
            )
        )

    def test_semantic_validation_schema_version_mismatch_is_reported(self) -> None:
        registry = DatasetRegistry()
        record = dict(NEW_DATASET_VALID_RECORDS[DatasetName.GLOBAL_EQUITY_SNAPSHOT])
        record["schema_version"] = "v2"

        issues = registry.validate_record(DatasetName.GLOBAL_EQUITY_SNAPSHOT, record)

        self.assertTrue(
            any(
                issue.code == "schema_version_mismatch"
                and issue.field == "schema_version"
                for issue in issues
            )
        )

    def test_semantic_validation_rejects_empty_required_identifier_or_title(self) -> None:
        registry = DatasetRegistry()

        policy_record = dict(NEW_DATASET_VALID_RECORDS[DatasetName.POLICY_DOCUMENTS])
        policy_record["title"] = "   "
        news_record = dict(NEW_DATASET_VALID_RECORDS[DatasetName.NEWS_EVENTS])
        news_record["title"] = ""
        announcement_record = dict(
            NEW_DATASET_VALID_RECORDS[DatasetName.COMPANY_ANNOUNCEMENTS]
        )
        announcement_record["title"] = ""

        policy_issues = registry.validate_record(DatasetName.POLICY_DOCUMENTS, policy_record)
        news_issues = registry.validate_record(DatasetName.NEWS_EVENTS, news_record)
        announcement_issues = registry.validate_record(
            DatasetName.COMPANY_ANNOUNCEMENTS,
            announcement_record,
        )

        self.assertTrue(
            any(issue.code == "empty_required_identifier" and issue.field == "title" for issue in policy_issues)
        )
        self.assertTrue(
            any(issue.code == "empty_required_identifier" and issue.field == "title" for issue in news_issues)
        )
        self.assertTrue(
            any(
                issue.code == "empty_required_identifier" and issue.field == "title"
                for issue in announcement_issues
            )
        )

    def test_semantic_validation_rejects_invalid_ohlc_range(self) -> None:
        registry = DatasetRegistry()
        record = dict(NEW_DATASET_VALID_RECORDS[DatasetName.INDEX_DAILY_BARS])
        record["high"] = 100.0
        record["low"] = 120.0

        issues = registry.validate_record(DatasetName.INDEX_DAILY_BARS, record)

        self.assertTrue(
            any(issue.code == "invalid_price_range" and issue.field == "high" for issue in issues)
        )

    def test_semantic_validation_rejects_negative_size_or_price_fields(self) -> None:
        registry = DatasetRegistry()

        fund_nav_record = dict(NEW_DATASET_VALID_RECORDS[DatasetName.FUND_NAV_SNAPSHOT])
        fund_nav_record["nav"] = -1.0

        fund_holdings_record = dict(NEW_DATASET_VALID_RECORDS[DatasetName.FUND_HOLDINGS])
        fund_holdings_record["shares"] = -10

        global_equity_record = dict(NEW_DATASET_VALID_RECORDS[DatasetName.GLOBAL_EQUITY_SNAPSHOT])
        global_equity_record["close"] = -0.01

        fund_nav_issues = registry.validate_record(DatasetName.FUND_NAV_SNAPSHOT, fund_nav_record)
        fund_holdings_issues = registry.validate_record(DatasetName.FUND_HOLDINGS, fund_holdings_record)
        global_equity_issues = registry.validate_record(
            DatasetName.GLOBAL_EQUITY_SNAPSHOT,
            global_equity_record,
        )

        self.assertTrue(any(issue.code == "negative_value" and issue.field == "nav" for issue in fund_nav_issues))
        self.assertTrue(
            any(issue.code == "negative_value" and issue.field == "shares" for issue in fund_holdings_issues)
        )
        self.assertTrue(
            any(issue.code == "negative_value" and issue.field == "close" for issue in global_equity_issues)
        )

    def test_semantic_validation_rejects_weight_out_of_range(self) -> None:
        registry = DatasetRegistry()
        record = dict(NEW_DATASET_VALID_RECORDS[DatasetName.FUND_HOLDINGS])
        record["weight"] = 150.0

        issues = registry.validate_record(DatasetName.FUND_HOLDINGS, record)

        self.assertTrue(
            any(issue.code == "weight_out_of_range" and issue.field == "weight" for issue in issues)
        )

    def test_semantic_validation_rejects_invalid_out_date_range(self) -> None:
        registry = DatasetRegistry()
        record = dict(NEW_DATASET_VALID_RECORDS[DatasetName.SECTOR_MEMBERSHIP])
        record["out_date"] = "2021-12-31"

        issues = registry.validate_record(DatasetName.SECTOR_MEMBERSHIP, record)

        self.assertTrue(
            any(issue.code == "invalid_date_range" and issue.field == "out_date" for issue in issues)
        )

    def test_semantic_rules_are_explicit_and_inspectable(self) -> None:
        registry = DatasetRegistry()

        news_rules = registry.get_semantic_rules(DatasetName.NEWS_EVENTS)
        index_rules = registry.get_semantic_rules(DatasetName.INDEX_DAILY_BARS)
        sector_member_rules = registry.get_semantic_rules(DatasetName.SECTOR_MEMBERSHIP)

        self.assertIn("title", news_rules.nonempty_required_strings)
        self.assertIn(("high", "low"), index_rules.ohlc_pairs)
        self.assertIn(("in_date", "out_date"), sector_member_rules.ordered_date_pairs)

    def test_nonempty_validation_is_not_driven_by_field_name_keywords(self) -> None:
        registry = DatasetRegistry()
        record = dict(NEW_DATASET_VALID_RECORDS[DatasetName.NEWS_EVENTS])

        record["source_name"] = ""
        record["related_symbol"] = ""

        issues = registry.validate_record(DatasetName.NEWS_EVENTS, record)

        self.assertFalse(
            any(
                issue.code == "empty_required_identifier" and issue.field == "source_name"
                for issue in issues
            )
        )
        self.assertFalse(
            any(
                issue.code == "empty_required_identifier" and issue.field == "related_symbol"
                for issue in issues
            )
        )

    def test_semantic_issue_codes_are_stable_for_assertions(self) -> None:
        registry = DatasetRegistry()

        schema_record = dict(NEW_DATASET_VALID_RECORDS[DatasetName.GLOBAL_EQUITY_SNAPSHOT])
        schema_record["schema_version"] = "v2"

        high_low_record = dict(NEW_DATASET_VALID_RECORDS[DatasetName.INDEX_DAILY_BARS])
        high_low_record["high"] = 100.0
        high_low_record["low"] = 120.0

        weight_record = dict(NEW_DATASET_VALID_RECORDS[DatasetName.FUND_HOLDINGS])
        weight_record["weight"] = -1

        date_range_record = dict(NEW_DATASET_VALID_RECORDS[DatasetName.SECTOR_MEMBERSHIP])
        date_range_record["out_date"] = "2021-12-31"

        all_codes = {
            issue.code
            for issue in (
                *registry.validate_record(DatasetName.GLOBAL_EQUITY_SNAPSHOT, schema_record),
                *registry.validate_record(DatasetName.INDEX_DAILY_BARS, high_low_record),
                *registry.validate_record(DatasetName.FUND_HOLDINGS, weight_record),
                *registry.validate_record(DatasetName.SECTOR_MEMBERSHIP, date_range_record),
            )
        }

        self.assertIn("schema_version_mismatch", all_codes)
        self.assertIn("invalid_price_range", all_codes)
        self.assertIn("weight_out_of_range", all_codes)
        self.assertIn("invalid_date_range", all_codes)

    def test_default_semantic_rules_align_with_registered_schemas(self) -> None:
        registry = DatasetRegistry()

        rules = dict(registry.all_semantic_rules())

        self.assertIn(DatasetName.NEWS_EVENTS, rules)
        self.assertIn(DatasetName.INDEX_DAILY_BARS, rules)
        self.assertIn(DatasetName.MINUTE_BARS, rules)
        self.assertIn(DatasetName.LIMIT_UP_DOWN_EVENTS, rules)
        self.assertIn(DatasetName.SUSPENSION_RESUMPTION_EVENTS, rules)
        self.assertIn(DatasetName.FINANCIAL_STATEMENTS, rules)
        self.assertIn("title", rules[DatasetName.NEWS_EVENTS].nonempty_required_strings)
        self.assertIn(
            "limit_type",
            rules[DatasetName.LIMIT_UP_DOWN_EVENTS].nonempty_required_strings,
        )
        self.assertIn(
            ("start_date", "end_date"),
            rules[DatasetName.SUSPENSION_RESUMPTION_EVENTS].ordered_date_pairs,
        )
        self.assertIn(("high", "low"), rules[DatasetName.INDEX_DAILY_BARS].ohlc_pairs)
        self.assertIn(("high", "low"), rules[DatasetName.MINUTE_BARS].ohlc_pairs)

    def test_semantic_rule_integrity_rejects_unknown_field(self) -> None:
        broken_rules = {
            DatasetName.NEWS_EVENTS: SemanticRuleSet(
                nonempty_required_strings=("not_existing_field",)
            )
        }

        with patch.object(DatasetRegistry, "_build_semantic_rules", return_value=broken_rules):
            with self.assertRaisesRegex(
                ValueError,
                "dataset=news_events, rule=nonempty_required_strings, field=not_existing_field",
            ):
                DatasetRegistry()

    def test_semantic_rule_integrity_rejects_incompatible_dtype_field(self) -> None:
        broken_rules = {
            DatasetName.NEWS_EVENTS: SemanticRuleSet(
                nonnegative_numeric_fields=("title",)
            )
        }

        with patch.object(DatasetRegistry, "_build_semantic_rules", return_value=broken_rules):
            with self.assertRaisesRegex(
                ValueError,
                "dataset=news_events, rule=nonnegative_numeric_fields, field=title, reason=dtype_mismatch",
            ):
                DatasetRegistry()

    def test_semantic_rule_integrity_rejects_optional_string_for_nonempty_required_rule(
        self,
    ) -> None:
        broken_rules = {
            DatasetName.NEWS_EVENTS: SemanticRuleSet(
                nonempty_required_strings=("summary",)
            )
        }

        with patch.object(DatasetRegistry, "_build_semantic_rules", return_value=broken_rules):
            with self.assertRaisesRegex(
                ValueError,
                "dataset=news_events, rule=nonempty_required_strings, field=summary, reason=must_be_required",
            ):
                DatasetRegistry()

    def test_semantic_rule_integrity_rejects_unregistered_dataset_rule(self) -> None:
        broken_rules = {
            "ghost_dataset": SemanticRuleSet(
                nonempty_required_strings=("id",)
            )
        }

        with patch.object(DatasetRegistry, "_build_semantic_rules", return_value=broken_rules):
            with self.assertRaisesRegex(
                ValueError,
                r"dataset='ghost_dataset', rule=dataset_registration, field=<dataset>",
            ):
                DatasetRegistry()
