from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareFinancialDataAdapter,
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
    if statement_name == "资产负债表":
        base_rows = [
            {
                "报告日": "2024-12-31",
                "资产总计": "1,200",
                "负债合计": 500,
                "币种": "CNY",
                "更新日期": "2025-01-02 09:00:00",
            },
            {
                "报告日": "2024-12-31",
                "资产总计": "1,200",
                "负债合计": 500,
                "币种": "CNY",
                "更新日期": "2025-01-02 09:00:00",
            },
        ]
    elif statement_name == "利润表":
        base_rows = [
            {
                "报告日": "2024-09-30",
                "营业收入": "900",
                "归属于母公司的净利润": "150",
                "币种": "CNY",
                "公告日期": "2024-10-30",
            }
        ]
    elif statement_name == "现金流量表":
        base_rows = [
            {
                "报告日": "2024/09/30",
                "经营活动产生的现金流量净额": "80",
                "币种": "CNY",
            }
        ]
    else:
        raise AssertionError(f"Unexpected statement_name in fixture: {statement_name!r}")
    return base_rows


def _build_indicator_payload():
    return [
        {
            "REPORT_DATE": "2024-12-31",
            "REPORT_TYPE": "年报",
            "CURRENCY": "CNY",
            "EPSJB": "1.2",
            "TOTALOPERATEREVE": "1200",
            "ZCFZL": "40.5",
            "UPDATE_DATE": "2025-01-02 09:00:00",
        },
        {
            "REPORT_DATE": "2024-12-31",
            "REPORT_TYPE": "年报",
            "CURRENCY": "CNY",
            "EPSJB": "1.2",
            "TOTALOPERATEREVE": "1200",
            "ZCFZL": "40.5",
            "UPDATE_DATE": "2025-01-02 09:00:00",
        },
        {
            "REPORT_DATE": "2024-09-30",
            "REPORT_TYPE": "三季报",
            "CURRENCY": "CNY",
            "EPSJB": "1.0",
            "TOTALOPERATEREVE": "900",
            "PARENTNETPROFIT": "150",
        },
    ]


def _build_adapter(
    *,
    fetch_financial_report=None,
    fetch_financial_indicator=None,
    now_fn=None,
) -> AkshareAShareFinancialDataAdapter:
    return AkshareAShareFinancialDataAdapter(
        fetch_financial_report=fetch_financial_report,
        fetch_financial_indicator=fetch_financial_indicator,
        now_fn=now_fn,
    )


class AkshareAShareFinancialDataAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: [],
            fetch_financial_indicator=lambda **kwargs: [],
        )
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_financial_statements_validates_contract_and_offline_only(self) -> None:
        report_calls: list[dict[str, str]] = []
        now = datetime(2026, 5, 31, 10, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        def fake_fetch_financial_report(**kwargs):
            report_calls.append(kwargs)
            return _build_statement_payload(kwargs["symbol"])

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
                    symbols=("600000.SH",),
                ),
                fetched_at=datetime(2026, 5, 31, 10, 5, 0, tzinfo=timezone.utc),
            )

        self.assertEqual(len(report_calls), 3)
        self.assertEqual(report_calls[0]["stock"], "sh600000")
        self.assertEqual(report_calls[0]["symbol"], "资产负债表")
        self.assertEqual(report_calls[1]["symbol"], "利润表")
        self.assertEqual(report_calls[2]["symbol"], "现金流量表")

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
            self.assertEqual(record["symbol"], "600000.SH")
            self.assertEqual(record["market"], "A_SHARE")
            self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
            self.assertEqual(record["ingested_at"], now.isoformat())
            self.assertEqual(record["schema_version"], "v1")
            self.assertEqual(
                registry.validate_record(DatasetName.FINANCIAL_STATEMENTS, record),
                (),
            )

    def test_fetch_financial_indicators_validates_contract_and_deduplicates(self) -> None:
        now = datetime(2026, 5, 31, 10, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()
        indicator_calls: list[dict[str, str]] = []

        def fake_fetch_indicator(**kwargs):
            indicator_calls.append(kwargs)
            return _build_indicator_payload()

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
                symbols=("600000",),
            ),
        )

        self.assertEqual(indicator_calls, [{"symbol": "600000.SH", "indicator": "按报告期"}])
        self.assertEqual(result.record_count, 6)

        first = result.normalized_records[0]
        self.assertEqual(first["symbol"], "600000.SH")
        self.assertEqual(first["market"], "A_SHARE")
        self.assertEqual(first["source"], AKSHARE_SOURCE_ID)
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
        self.assertEqual(by_key[("2024-12-31", "annual", "TOTALOPERATEREVE")]["metric_value"], 1200.0)
        self.assertEqual(by_key[("2024-12-31", "annual", "ZCFZL")]["unit"], "percent")
        self.assertEqual(by_key[("2024-12-31", "annual", "EPSJB")]["unit"], "CNY_per_share")

        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.FINANCIAL_INDICATORS, record),
                (),
            )

    def test_adapter_accepts_dataframe_like_payload_for_both_routes(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: _FakeDataFrame(
                _build_statement_payload(kwargs["symbol"])
            ),
            fetch_financial_indicator=lambda **kwargs: _FakeDataFrame(_build_indicator_payload()),
        )

        statements_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FINANCIAL_STATEMENTS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000",),
            ),
        )
        indicators_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FINANCIAL_INDICATORS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000",),
            ),
        )
        self.assertEqual(statements_result.record_count, 3)
        self.assertEqual(indicators_result.record_count, 6)

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
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_requires_exactly_one_symbol(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: [],
            fetch_financial_indicator=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "requires exactly one symbol, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

        with self.assertRaisesRegex(ValueError, "exactly one symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH", "000001.SZ"),
                ),
            )

    def test_adapter_accepts_canonical_and_bare_a_share_symbols(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: _build_statement_payload(kwargs["symbol"]),
            fetch_financial_indicator=lambda **kwargs: _build_indicator_payload(),
        )

        accepted = {
            "600000.SH": "600000.SH",
            "000001.SZ": "000001.SZ",
            "430047.BJ": "430047.BJ",
            "600000": "600000.SH",
            "000001": "000001.SZ",
            "430047": "430047.BJ",
        }
        for raw_symbol, canonical in accepted.items():
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=(raw_symbol,),
                ),
            )
            self.assertEqual(result.normalized_records[0]["symbol"], canonical)

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
                    symbols=("00700.HK",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Invalid A-share stock code prefix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.SH",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Invalid A-share stock code prefix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("159915.SZ",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Invalid symbol filter market-code combination"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000300.SH",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Unsupported symbol format"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("HS300",),
                ),
            )

    def test_adapter_rejects_invalid_report_date(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: [
                {
                    "报告日": "2024-13-31",
                    "资产总计": "100",
                    "负债合计": "50",
                }
            ]
            if kwargs["symbol"] == "资产负债表"
            else [],
            fetch_financial_indicator=lambda **kwargs: [
                {
                    "REPORT_DATE": "2024-13-31",
                    "EPSJB": "1.2",
                }
            ],
        )

        with self.assertRaisesRegex(ValueError, "Invalid report_period_end value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Invalid report_period_end value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_INDICATORS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_invalid_numeric_values(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: [
                {
                    "报告日": "2024-12-31",
                    "资产总计": "bad-number",
                    "负债合计": "50",
                }
            ]
            if kwargs["symbol"] == "资产负债表"
            else [],
            fetch_financial_indicator=lambda **kwargs: [
                {
                    "REPORT_DATE": "2024-12-31",
                    "EPSJB": "not-a-number",
                }
            ],
        )

        with self.assertRaisesRegex(ValueError, "Invalid total_assets value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Invalid epsjb value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_INDICATORS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_conflicting_duplicate_rows(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: [
                {
                    "报告日": "2024-12-31",
                    "资产总计": "100",
                    "负债合计": "50",
                },
                {
                    "报告日": "2024-12-31",
                    "资产总计": "101",
                    "负债合计": "50",
                },
            ]
            if kwargs["symbol"] == "资产负债表"
            else [],
            fetch_financial_indicator=lambda **kwargs: [
                {
                    "REPORT_DATE": "2024-12-31",
                    "EPSJB": "1.0",
                },
                {
                    "REPORT_DATE": "2024-12-31",
                    "EPSJB": "1.1",
                },
            ],
        )

        with self.assertRaisesRegex(ValueError, "Conflicting duplicate A-share financial statement row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Conflicting duplicate A-share financial indicator row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_INDICATORS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape_and_non_mapping_rows(self) -> None:
        adapter_bad_shape = _build_adapter(
            fetch_financial_report=lambda **kwargs: {"报告日": "2024-12-31"},
            fetch_financial_indicator=lambda **kwargs: _build_indicator_payload(),
        )
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter_bad_shape,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
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
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_missing_required_source_fields(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: [
                {
                    "资产总计": "100",
                    "负债合计": "50",
                }
            ]
            if kwargs["symbol"] == "资产负债表"
            else [],
            fetch_financial_indicator=lambda **kwargs: [
                {
                    "EPSJB": "1.0",
                }
            ],
        )

        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_STATEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FINANCIAL_INDICATORS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_start_end_date_filtering_uses_report_period_end(self) -> None:
        adapter = _build_adapter(
            fetch_financial_report=lambda **kwargs: _build_statement_payload(kwargs["symbol"]),
            fetch_financial_indicator=lambda **kwargs: _build_indicator_payload(),
        )

        statements_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FINANCIAL_STATEMENTS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
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
                symbols=("600000.SH",),
                start_date=date(2024, 12, 1),
                end_date=date(2024, 12, 31),
            ),
        )
        self.assertTrue(
            all(r["report_period_end"] == "2024-12-31" for r in indicators_result.normalized_records)
        )


if __name__ == "__main__":
    unittest.main()
