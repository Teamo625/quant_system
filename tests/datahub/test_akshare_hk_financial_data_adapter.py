from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareHKFinancialDataAdapter,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceAdapter, SourceRequest, fetch_source_result


class _FakeDataFrame:
    def __init__(self, records):
        self._records = list(records)

    def to_dict(self, orient="records"):
        if orient != "records":
            raise ValueError("Only orient='records' is supported in test fixture.")
        return list(self._records)


def _build_statement_payload(statement_name: str):
    return _build_statement_payload_for_stock(statement_name, "00700")


def _build_statement_payload_for_stock(statement_name: str, stock_code: str):
    stock_offset = int(stock_code) % 10
    if statement_name == "资产负债表":
        base_rows = [
            {
                "REPORT_DATE": "2024-12-31 00:00:00",
                "DATE_TYPE_CODE": "001",
                "STD_ITEM_NAME": "资产总计",
                "AMOUNT": str(1200 + stock_offset),
                "CURRENCY": "HKD",
                "STD_REPORT_DATE": "2025-01-02 09:00:00",
            },
            {
                "REPORT_DATE": "2024-12-31",
                "DATE_TYPE_CODE": "001",
                "STD_ITEM_NAME": "负债总额",
                "AMOUNT": 500 + stock_offset,
                "CURRENCY": "HKD",
                "STD_REPORT_DATE": "2025-01-02 09:00:00",
            },
            {
                "REPORT_DATE": "2024-12-31",
                "DATE_TYPE_CODE": "001",
                "STD_ITEM_NAME": "负债总额",
                "AMOUNT": 500 + stock_offset,
                "CURRENCY": "HKD",
                "STD_REPORT_DATE": "2025-01-02 09:00:00",
            },
        ]
    elif statement_name == "利润表":
        base_rows = [
            {
                "REPORT_DATE": "2024-09-30",
                "DATE_TYPE_CODE": "003",
                "STD_ITEM_NAME": "本期溢利",
                "AMOUNT": str(150 + stock_offset),
                "CURRENCY": "HKD",
            },
            {
                "REPORT_DATE": "2024-09-30",
                "DATE_TYPE_CODE": "003",
                "STD_ITEM_NAME": "营业额",
                "AMOUNT": str(900 + stock_offset),
                "CURRENCY": "HKD",
            },
        ]
    elif statement_name == "现金流量表":
        base_rows = [
            {
                "REPORT_DATE": "2024/09/30",
                "DATE_TYPE_CODE": "003",
                "STD_ITEM_NAME": "经营业务现金净额",
                "AMOUNT": str(80 + stock_offset),
                "CURRENCY": "HKD",
            }
        ]
    else:
        raise AssertionError(f"Unexpected statement_name in fixture: {statement_name!r}")
    return base_rows


def _build_indicator_payload():
    return _build_indicator_payload_for_stock("00700")


def _build_indicator_payload_for_stock(stock_code: str):
    stock_offset = int(stock_code) % 10
    return [
        {
            "REPORT_DATE": "2024-12-31",
            "DATE_TYPE_CODE": "001",
            "CURRENCY": "HKD",
            "OPERATE_INCOME": str(1200 + stock_offset),
            "HOLDER_PROFIT": 200 + stock_offset,
            "DEBT_ASSET_RATIO": "40.5",
            "BASIC_EPS": "12.3",
            "OPERATE_INCOME_YOY": "9.5",
        },
        {
            "REPORT_DATE": "2024-12-31",
            "DATE_TYPE_CODE": "001",
            "CURRENCY": "HKD",
            "OPERATE_INCOME": str(1200 + stock_offset),
            "HOLDER_PROFIT": 200 + stock_offset,
            "DEBT_ASSET_RATIO": "40.5",
            "BASIC_EPS": "12.3",
            "OPERATE_INCOME_YOY": "9.5",
        },
        {
            "REPORT_DATE": "2024-09-30",
            "DATE_TYPE_CODE": "003",
            "CURRENCY": "HKD",
            "OPERATE_INCOME": str(900 + stock_offset),
            "HOLDER_PROFIT": str(150 + stock_offset),
            "DEBT_ASSET_RATIO": "39.0",
            "BASIC_EPS": "10.1",
        },
    ]


def _build_adapter(
    *,
    fetch_financial_report=None,
    fetch_financial_indicator=None,
    now_fn=None,
) -> AkshareHKFinancialDataAdapter:
    return AkshareHKFinancialDataAdapter(
        fetch_financial_report=fetch_financial_report,
        fetch_financial_indicator=fetch_financial_indicator,
        now_fn=now_fn,
    )


class AkshareHKFinancialDataAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: [],
            fetch_financial_indicator=lambda **kwargs: [],
        )
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_financial_statements_validates_contract_and_offline_only(self) -> None:
        calls: list[dict[str, str]] = []
        now = datetime(2026, 5, 31, 10, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        def fake_fetch_financial_report(**kwargs):
            calls.append(kwargs)
            return _build_statement_payload_for_stock(kwargs["symbol"], kwargs["stock"])

        adapter = _build_adapter(
            fetch_financial_report=fake_fetch_financial_report,
            fetch_financial_indicator=lambda **kwargs: [],
            now_fn=lambda: now,
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
                fetched_at=datetime(2026, 5, 31, 10, 5, 0, tzinfo=timezone.utc),
            )

        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[0]["stock"], "00700")
        self.assertEqual(calls[0]["indicator"], "报告期")
        self.assertEqual(calls[1]["symbol"], "利润表")
        self.assertEqual(calls[2]["symbol"], "现金流量表")

        self.assertEqual(result.record_count, 3)
        records = list(result.normalized_records)
        self.assertEqual(
            [
                (record["report_period_end"], record["statement_type"], record["period_type"])
                for record in records
            ],
            [
                ("2024-09-30", "cash_flow_statement", "quarterly"),
                ("2024-09-30", "income_statement", "quarterly"),
                ("2024-12-31", "balance_sheet", "annual"),
            ],
        )

        by_type = {record["statement_type"]: record for record in records}
        self.assertEqual(by_type["income_statement"]["revenue"], 900.0)
        self.assertEqual(by_type["income_statement"]["net_profit"], 150.0)
        self.assertEqual(by_type["balance_sheet"]["total_assets"], 1200.0)
        self.assertEqual(by_type["balance_sheet"]["total_liabilities"], 500.0)
        self.assertEqual(by_type["cash_flow_statement"]["net_cash_operating"], 80.0)

        for record in records:
            self.assertEqual(record["symbol"], "00700.HK")
            self.assertEqual(record["market"], "HK")
            self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
            self.assertEqual(record["source_route"], "stock_financial_hk_report_em")
            self.assertEqual(record["ingested_at"], now.isoformat())
            self.assertEqual(record["schema_version"], "v1")
            self.assertEqual(
                registry.validate_record(DatasetName.FINANCIAL_STATEMENTS, record),
                (),
            )

    def test_fetch_financial_indicators_validates_contract_and_deduplicates(self) -> None:
        now = datetime(2026, 5, 31, 10, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()
        calls: list[dict[str, str]] = []

        def fake_fetch_indicator(**kwargs):
            calls.append(kwargs)
            return _build_indicator_payload_for_stock(kwargs["symbol"])

        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: [],
            fetch_financial_indicator=fake_fetch_indicator,
            now_fn=lambda: now,
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FINANCIAL_INDICATORS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("700",),
            ),
        )

        self.assertEqual(calls, [{"symbol": "00700", "indicator": "报告期"}])
        self.assertGreaterEqual(result.record_count, 9)

        first = result.normalized_records[0]
        self.assertEqual(first["symbol"], "00700.HK")
        self.assertEqual(first["market"], "HK")
        self.assertEqual(first["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(first["source_route"], "stock_financial_hk_analysis_indicator_em")
        self.assertEqual(first["ingested_at"], now.isoformat())
        self.assertEqual(first["schema_version"], "v1")

        by_key = {
            (
                record["report_period_end"],
                record["period_type"],
                record["metric_code"],
            ): record
            for record in result.normalized_records
        }
        self.assertEqual(by_key[("2024-12-31", "annual", "OPERATE_INCOME")]["metric_value"], 1200.0)
        self.assertEqual(
            by_key[("2024-12-31", "annual", "OPERATE_INCOME")]["metric_family"],
            "income_scale",
        )
        self.assertEqual(by_key[("2024-12-31", "annual", "DEBT_ASSET_RATIO")]["unit"], "percent")
        self.assertEqual(
            by_key[("2024-12-31", "annual", "DEBT_ASSET_RATIO")]["metric_family"],
            "leverage_liquidity",
        )
        self.assertEqual(by_key[("2024-12-31", "annual", "BASIC_EPS")]["unit"], "HKD_per_share")
        self.assertEqual(
            by_key[("2024-12-31", "annual", "BASIC_EPS")]["metric_family"],
            "per_share",
        )

        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.FINANCIAL_INDICATORS, record),
                (),
            )

    def test_statement_alias_priority_prefers_route_consistent_income_metrics(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: [
                {
                    "REPORT_DATE": "2025-12-31",
                    "DATE_TYPE_CODE": "001",
                    "STD_ITEM_NAME": "营业额",
                    "AMOUNT": "100",
                },
                {
                    "REPORT_DATE": "2025-12-31",
                    "DATE_TYPE_CODE": "001",
                    "STD_ITEM_NAME": "营运收入",
                    "AMOUNT": "120",
                },
                {
                    "REPORT_DATE": "2025-12-31",
                    "DATE_TYPE_CODE": "001",
                    "STD_ITEM_NAME": "除税后溢利",
                    "AMOUNT": "30",
                },
                {
                    "REPORT_DATE": "2025-12-31",
                    "DATE_TYPE_CODE": "001",
                    "STD_ITEM_NAME": "股东应占溢利",
                    "AMOUNT": "25",
                },
            ]
            if kwargs["symbol"] == "利润表"
            else [],
            fetch_financial_indicator=lambda **kwargs: [],
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FINANCIAL_STATEMENTS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
            ),
        )

        record = result.normalized_records[0]
        self.assertEqual(record["statement_type"], "income_statement")
        self.assertEqual(record["revenue"], 120.0)
        self.assertEqual(record["net_profit"], 25.0)
        self.assertEqual(record["source_route"], "stock_financial_hk_report_em")

    def test_statement_aliases_cover_bank_style_income_labels(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: [
                {
                    "REPORT_DATE": "2025-12-31",
                    "DATE_TYPE_CODE": "001",
                    "STD_ITEM_NAME": "经营收入总额",
                    "AMOUNT": "452823411200",
                },
                {
                    "REPORT_DATE": "2025-12-31",
                    "DATE_TYPE_CODE": "001",
                    "STD_ITEM_NAME": "股东应占溢利",
                    "AMOUNT": "148321737600",
                },
            ]
            if kwargs["symbol"] == "利润表"
            else [],
            fetch_financial_indicator=lambda **kwargs: [],
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FINANCIAL_STATEMENTS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00005.HK",),
            ),
        )

        record = result.normalized_records[0]
        self.assertEqual(record["revenue"], 452823411200.0)
        self.assertEqual(record["net_profit"], 148321737600.0)

    def test_adapter_accepts_dataframe_like_payload_for_both_routes(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: _FakeDataFrame(
                _build_statement_payload_for_stock(kwargs["symbol"], kwargs["stock"])
            ),
            fetch_financial_indicator=lambda **kwargs: _FakeDataFrame(
                _build_indicator_payload_for_stock(kwargs["symbol"])
            ),
        )

        statements_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FINANCIAL_STATEMENTS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700",),
            ),
        )
        indicators_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FINANCIAL_INDICATORS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700",),
            ),
        )
        self.assertEqual(statements_result.record_count, 3)
        self.assertGreaterEqual(indicators_result.record_count, 9)

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: [],
            fetch_financial_indicator=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_requires_at_least_one_symbol(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: [],
            fetch_financial_indicator=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "requires at least one symbol, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

        with self.assertRaisesRegex(ValueError, "requires at least one symbol, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=(),
                ),
            )

    def test_adapter_accepts_batch_symbols_and_deduplicates_requested_list(self) -> None:
        statement_calls: list[dict[str, str]] = []
        indicator_calls: list[dict[str, str]] = []
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: statement_calls.append(kwargs)
            or _build_statement_payload_for_stock(kwargs["symbol"], kwargs["stock"]),
            fetch_financial_indicator=lambda **kwargs: indicator_calls.append(kwargs)
            or _build_indicator_payload_for_stock(kwargs["symbol"]),
        )

        statements_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FINANCIAL_STATEMENTS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK", "700", "00005.HK"),
            ),
        )
        indicators_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FINANCIAL_INDICATORS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00005.HK", "5", "00700"),
            ),
        )

        self.assertEqual(
            [call["stock"] for call in statement_calls],
            ["00700", "00700", "00700", "00005", "00005", "00005"],
        )
        self.assertEqual(
            [call["symbol"] for call in indicator_calls],
            ["00005", "00700"],
        )
        self.assertEqual(
            [
                (
                    record["symbol"],
                    record["report_period_end"],
                    record.get("statement_type", record.get("metric_code")),
                )
                for record in statements_result.normalized_records[:6]
            ],
            [
                ("00005.HK", "2024-09-30", "cash_flow_statement"),
                ("00005.HK", "2024-09-30", "income_statement"),
                ("00005.HK", "2024-12-31", "balance_sheet"),
                ("00700.HK", "2024-09-30", "cash_flow_statement"),
                ("00700.HK", "2024-09-30", "income_statement"),
                ("00700.HK", "2024-12-31", "balance_sheet"),
            ],
        )
        self.assertEqual(
            [
                (
                    record["symbol"],
                    record["report_period_end"],
                    record["metric_code"],
                )
                for record in indicators_result.normalized_records[:4]
            ],
            [
                ("00005.HK", "2024-09-30", "BASIC_EPS"),
                ("00005.HK", "2024-09-30", "DEBT_ASSET_RATIO"),
                ("00005.HK", "2024-09-30", "HOLDER_PROFIT"),
                ("00005.HK", "2024-09-30", "OPERATE_INCOME"),
            ],
        )
        self.assertEqual(statements_result.record_count, 6)
        self.assertGreaterEqual(indicators_result.record_count, 18)

    def test_adapter_rejects_partial_batch_success_when_symbol_has_no_rows(self) -> None:
        def fake_fetch_financial_report(**kwargs):
            if kwargs["stock"] == "02800":
                return []
            return _build_statement_payload_for_stock(kwargs["symbol"], kwargs["stock"])

        def fake_fetch_indicator(**kwargs):
            if kwargs["symbol"] == "02800":
                return []
            return _build_indicator_payload_for_stock(kwargs["symbol"])

        adapter = _build_adapter(
            fetch_financial_report=fake_fetch_financial_report,
            fetch_financial_indicator=fake_fetch_indicator,
        )

        with self.assertRaisesRegex(ValueError, "unsupported, non-stock, or route returned no rows"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK", "02800.HK"),
                ),
            )

    def test_adapter_accepts_canonical_and_bare_hk_symbols(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: _build_statement_payload_for_stock(
                kwargs["symbol"], kwargs["stock"]
            ),
            fetch_financial_indicator=lambda **kwargs: _build_indicator_payload_for_stock(
                kwargs["symbol"]
            ),
        )

        for raw_symbol in ("00700.HK", "00700", "700"):
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=(raw_symbol,),
                ),
            )
            self.assertEqual(result.normalized_records[0]["symbol"], "00700.HK")

    def test_adapter_rejects_invalid_symbols(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: [],
            fetch_financial_indicator=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "Unsupported symbol market suffix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Unsupported HK symbol format"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("HSI.HK",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Expected 1-5 digit HK stock code"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.HK",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Symbol at index 0 must be a non-empty string"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("",),
                ),
            )

    def test_adapter_rejects_invalid_report_date(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: [
                {
                    "REPORT_DATE": "2024-13-31",
                    "DATE_TYPE_CODE": "001",
                    "STD_ITEM_NAME": "资产总计",
                    "AMOUNT": "100",
                }
            ]
            if kwargs["symbol"] == "资产负债表"
            else [],
            fetch_financial_indicator=lambda **kwargs: _build_indicator_payload(),
        )

        with self.assertRaisesRegex(ValueError, "Invalid report_period_end value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_invalid_numeric_values(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: [
                {
                    "REPORT_DATE": "2024-12-31",
                    "DATE_TYPE_CODE": "001",
                    "STD_ITEM_NAME": "资产总计",
                    "AMOUNT": "bad-number",
                }
            ]
            if kwargs["symbol"] == "资产负债表"
            else [],
            fetch_financial_indicator=lambda **kwargs: [
                {
                    "REPORT_DATE": "2024-12-31",
                    "DATE_TYPE_CODE": "001",
                    "OPERATE_INCOME": "not-a-number",
                }
            ],
        )

        with self.assertRaisesRegex(ValueError, "Invalid total_assets value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Invalid operate_income value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_INDICATORS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_conflicting_duplicate_rows(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: [
                {
                    "REPORT_DATE": "2024-12-31",
                    "DATE_TYPE_CODE": "001",
                    "STD_ITEM_NAME": "资产总计",
                    "AMOUNT": "100",
                },
                {
                    "REPORT_DATE": "2024-12-31",
                    "DATE_TYPE_CODE": "001",
                    "STD_ITEM_NAME": "资产总计",
                    "AMOUNT": "101",
                },
            ]
            if kwargs["symbol"] == "资产负债表"
            else [],
            fetch_financial_indicator=lambda **kwargs: [
                {
                    "REPORT_DATE": "2024-12-31",
                    "DATE_TYPE_CODE": "001",
                    "OPERATE_INCOME": "100",
                },
                {
                    "REPORT_DATE": "2024-12-31",
                    "DATE_TYPE_CODE": "001",
                    "OPERATE_INCOME": "101",
                },
            ],
        )

        with self.assertRaisesRegex(ValueError, "Conflicting duplicate HK financial statement row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Conflicting duplicate HK financial indicator row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_INDICATORS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape_and_non_mapping_rows(self) -> None:
        adapter_bad_shape = _build_adapter(
            fetch_financial_report=lambda **kwargs: {"REPORT_DATE": "2024-12-31"},
            fetch_financial_indicator=lambda **kwargs: _build_indicator_payload(),
        )
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter_bad_shape,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

        adapter_bad_row = _build_adapter(
            fetch_financial_report=lambda **kwargs: ["bad-row"],
            fetch_financial_indicator=lambda **kwargs: _build_indicator_payload(),
        )
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                adapter_bad_row,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_missing_required_source_fields(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: [
                {
                    "DATE_TYPE_CODE": "001",
                    "STD_ITEM_NAME": "资产总计",
                    "AMOUNT": "100",
                }
            ]
            if kwargs["symbol"] == "资产负债表"
            else [],
            fetch_financial_indicator=lambda **kwargs: [
                {
                    "DATE_TYPE_CODE": "001",
                    "OPERATE_INCOME": "100",
                }
            ],
        )

        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_INDICATORS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_start_end_date_filtering_uses_report_period_end(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: _build_statement_payload_for_stock(
                kwargs["symbol"], kwargs["stock"]
            ),
            fetch_financial_indicator=lambda **kwargs: _build_indicator_payload_for_stock(
                kwargs["symbol"]
            ),
        )

        statements_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FINANCIAL_STATEMENTS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
                start_date=date(2024, 12, 1),
                end_date=date(2024, 12, 31),
            ),
        )
        self.assertEqual(statements_result.record_count, 1)
        self.assertEqual(statements_result.normalized_records[0]["report_period_end"], "2024-12-31")

        indicators_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FINANCIAL_INDICATORS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
                start_date=date(2024, 12, 1),
                end_date=date(2024, 12, 31),
            ),
        )
        self.assertTrue(all(r["report_period_end"] == "2024-12-31" for r in indicators_result.normalized_records))

    def test_start_end_date_filtering_applies_across_multiple_symbols(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: _build_statement_payload_for_stock(
                kwargs["symbol"], kwargs["stock"]
            ),
            fetch_financial_indicator=lambda **kwargs: _build_indicator_payload_for_stock(
                kwargs["symbol"]
            ),
        )

        statements_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FINANCIAL_STATEMENTS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK", "00005.HK"),
                start_date=date(2024, 9, 1),
                end_date=date(2024, 9, 30),
            ),
        )
        indicators_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FINANCIAL_INDICATORS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK", "00005.HK"),
                start_date=date(2024, 9, 1),
                end_date=date(2024, 9, 30),
            ),
        )

        self.assertEqual(
            {
                (record["symbol"], record["report_period_end"])
                for record in statements_result.normalized_records
            },
            {
                ("00700.HK", "2024-09-30"),
                ("00005.HK", "2024-09-30"),
            },
        )
        self.assertEqual(
            {record["symbol"] for record in indicators_result.normalized_records},
            {"00005.HK", "00700.HK"},
        )
        self.assertTrue(
            all(record["report_period_end"] == "2024-09-30" for record in indicators_result.normalized_records)
        )


if __name__ == "__main__":
    unittest.main()
