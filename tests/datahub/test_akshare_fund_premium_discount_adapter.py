from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareETFFundPremiumDiscountAdapter,
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


def _daily_row(**overrides):
    row = {
        "基金代码": "510300",
        "基金简称": "沪深300ETF",
        "类型": "指数型-股票",
        "2024-01-05-单位净值": "3.2100",
        "2024-01-05-累计净值": "3.4300",
        "2024-01-04-单位净值": "3.1980",
        "2024-01-04-累计净值": "3.4180",
        "增长值": "0.0120",
        "增长率": "0.38%",
        "市价": "3.2270",
        "折价率": "0.53%",
    }
    row.update(overrides)
    return row


def _spot_row(**overrides):
    row = {
        "代码": "510300",
        "名称": "沪深300ETF",
        "最新价": 3.227,
        "IOPV实时估值": 3.208,
        "基金折价率": 0.59,
        "数据日期": "2024-01-05",
        "更新时间": "2024-01-05T14:58:00+08:00",
    }
    row.update(overrides)
    return row


def _hist_price_row(**overrides):
    row = {
        "date": "2024-01-04",
        "close": 3.415,
    }
    row.update(overrides)
    return row


def _nav_row(**overrides):
    row = {
        "净值日期": "2024-01-04",
        "单位净值": 3.398,
    }
    row.update(overrides)
    return row


class AkshareETFFundPremiumDiscountAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = AkshareETFFundPremiumDiscountAdapter(fetch_fund_daily=lambda: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_daily_route(self) -> None:
        registry = DatasetRegistry()
        now = datetime(2024, 1, 5, 9, 0, 0, tzinfo=timezone.utc)

        adapter = AkshareETFFundPremiumDiscountAdapter(
            fetch_fund_daily=lambda: [
                _daily_row(),
                _daily_row(
                    基金代码="159915",
                    市价="1.2340",
                    折价率="-0.12%",
                    **{"2024-01-05-单位净值": "1.2355"},
                ),
            ],
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.FUND_PREMIUM_DISCOUNT,
            source_name=AKSHARE_SOURCE_ID,
            start_date=date(2024, 1, 5),
            end_date=date(2024, 1, 5),
            symbols=("510300.ETF_CN",),
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(adapter, request)

        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["fund_code"], "510300.ETF_CN")
        self.assertEqual(record["market"], "ETF_FUND")
        self.assertEqual(record["trade_date"], "2024-01-05")
        self.assertEqual(record["market_price"], 3.227)
        self.assertEqual(record["nav"], 3.21)
        self.assertEqual(record["premium_discount_rate"], 0.53)
        self.assertAlmostEqual(record["premium_discount_amount"], 0.017)
        self.assertEqual(record["source_route"], "fund_etf_fund_daily_em")
        self.assertEqual(
            record["source_category"],
            "exchange_traded_fund_daily_summary",
        )
        self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(record["schema_version"], "v1")
        self.assertEqual(record["ingested_at"], now.isoformat())
        self.assertEqual(
            registry.validate_record(DatasetName.FUND_PREMIUM_DISCOUNT, record),
            (),
        )

    def test_adapter_supports_multi_symbol_batch_with_bounded_window(self) -> None:
        registry = DatasetRegistry()
        adapter = AkshareETFFundPremiumDiscountAdapter(
            fetch_fund_daily=lambda: _FakeDataFrame(
                [
                    _daily_row(
                        基金代码="159915",
                        市价="1.2360",
                        折价率="-0.12%",
                        **{"2024-01-05-单位净值": "1.2375"},
                    ),
                    _daily_row(),
                    _daily_row(),
                    _daily_row(
                        基金代码="512000",
                        市价="0.8880",
                        折价率="0.04%",
                        **{"2024-01-05-单位净值": "0.8876"},
                    ),
                ]
            )
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_PREMIUM_DISCOUNT,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 5),
                end_date=date(2024, 1, 5),
                symbols=("159915.ETF_CN", "510300", "159915"),
            ),
        )

        self.assertEqual(
            [
                (record["fund_code"], record["trade_date"])
                for record in result.normalized_records
            ],
            [
                ("159915.ETF_CN", "2024-01-05"),
                ("510300.ETF_CN", "2024-01-05"),
            ],
        )
        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.FUND_PREMIUM_DISCOUNT, record),
                (),
            )

    def test_adapter_falls_back_to_spot_route_when_daily_route_is_network_unavailable(
        self,
    ) -> None:
        adapter = AkshareETFFundPremiumDiscountAdapter(
            fetch_fund_daily=lambda: (_ for _ in ()).throw(
                OSError(111, "connection refused to fund.eastmoney.com")
            ),
            fetch_etf_spot=lambda: [
                _spot_row(),
                _spot_row(
                    代码="159915",
                    最新价=1.236,
                    IOPV实时估值=1.2375,
                    基金折价率=-0.12,
                ),
            ],
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_PREMIUM_DISCOUNT,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 5),
                end_date=date(2024, 1, 5),
                symbols=("510300.ETF_CN", "159915.ETF_CN"),
            ),
        )

        by_code = {record["fund_code"]: record for record in result.normalized_records}
        self.assertEqual(by_code["510300.ETF_CN"]["source_route"], "fund_etf_spot_em")
        self.assertEqual(by_code["510300.ETF_CN"]["market_price"], 3.227)
        self.assertEqual(by_code["510300.ETF_CN"]["iopv"], 3.208)
        self.assertEqual(
            by_code["510300.ETF_CN"]["source_ts"],
            "2024-01-05T14:58:00+08:00",
        )
        self.assertAlmostEqual(
            by_code["510300.ETF_CN"]["premium_discount_amount"],
            0.019,
        )

    def test_adapter_adds_historical_continuity_for_multi_day_etf_window(self) -> None:
        adapter = AkshareETFFundPremiumDiscountAdapter(
            fetch_fund_daily=lambda: [_daily_row()],
            fetch_etf_hist=lambda **_: [
                _hist_price_row(date="2024-01-04", close=3.415),
                _hist_price_row(date="2024-01-05", close=3.43),
            ],
            fetch_fund_nav=lambda **_: [
                _nav_row(净值日期="2024-01-04", 单位净值=3.398),
                _nav_row(净值日期="2024-01-05", 单位净值=3.401),
            ],
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_PREMIUM_DISCOUNT,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 4),
                end_date=date(2024, 1, 5),
                symbols=("510300.ETF_CN",),
            ),
        )

        self.assertEqual(
            [(record["trade_date"], record["source_route"]) for record in result.normalized_records],
            [
                ("2024-01-04", "fund_etf_hist_em+fund_etf_fund_info_em"),
                ("2024-01-05", "fund_etf_fund_daily_em"),
            ],
        )
        self.assertAlmostEqual(result.normalized_records[0]["premium_discount_rate"], 0.5002942907592733)
        self.assertEqual(
            result.normalized_records[0]["source_category"],
            "historical_market_price_nav_composite",
        )

    def test_adapter_supports_explicit_proven_fund_cn_history(self) -> None:
        registry = DatasetRegistry()
        adapter = AkshareETFFundPremiumDiscountAdapter(
            fetch_fund_daily=lambda: [],
            fetch_lof_hist=lambda **_: (_ for _ in ()).throw(
                OSError(111, "connection refused to push2his.eastmoney.com")
            ),
            fetch_etf_hist_sina=lambda **_: [
                _hist_price_row(date="2024-01-04", close=1.401),
                _hist_price_row(date="2024-01-05", close=1.423),
            ],
            fetch_open_fund_nav=lambda **_: [
                _nav_row(净值日期="2024-01-04", 单位净值=1.395),
                _nav_row(净值日期="2024-01-05", 单位净值=1.417),
            ],
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_PREMIUM_DISCOUNT,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 4),
                end_date=date(2024, 1, 5),
                symbols=("161725.FUND_CN",),
            ),
        )

        self.assertEqual(
            [(record["fund_code"], record["trade_date"]) for record in result.normalized_records],
            [
                ("161725.FUND_CN", "2024-01-04"),
                ("161725.FUND_CN", "2024-01-05"),
            ],
        )
        self.assertEqual(
            result.normalized_records[0]["source_route"],
            "fund_etf_hist_sina+fund_open_fund_info_em",
        )
        self.assertEqual(
            registry.validate_record(
                DatasetName.FUND_PREMIUM_DISCOUNT,
                result.normalized_records[0],
            ),
            (),
        )

    def test_adapter_returns_empty_when_window_has_no_snapshot_or_historical_overlap(
        self,
    ) -> None:
        adapter = AkshareETFFundPremiumDiscountAdapter(
            fetch_fund_daily=lambda: [_daily_row()],
            fetch_etf_hist=lambda **_: [],
            fetch_fund_nav=lambda **_: [],
            fetch_open_fund_nav=lambda **_: [],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_PREMIUM_DISCOUNT,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 4),
                symbols=("510300.ETF_CN",),
            ),
        )
        self.assertEqual(result.record_count, 0)

    def test_adapter_requires_bounded_dates_and_symbols(self) -> None:
        adapter = AkshareETFFundPremiumDiscountAdapter(fetch_fund_daily=lambda: [])

        with self.assertRaisesRegex(ValueError, "requires bounded trade_date"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_PREMIUM_DISCOUNT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.ETF_CN",),
                ),
            )
        with self.assertRaisesRegex(ValueError, "requires both start_date and end_date"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_PREMIUM_DISCOUNT,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 5),
                    symbols=("510300.ETF_CN",),
                ),
            )
        with self.assertRaisesRegex(ValueError, "at least one ETF/fund code"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_PREMIUM_DISCOUNT,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 5),
                    end_date=date(2024, 1, 5),
                    symbols=(),
                ),
            )

    def test_adapter_rejects_invalid_or_unsupported_symbols(self) -> None:
        adapter = AkshareETFFundPremiumDiscountAdapter(fetch_fund_daily=lambda: [])

        bad_symbols = (
            "600000.SH",
            "399001",
            "00700.HK",
            "abc",
            "510300.FUND_CN",
            "161725",
        )
        for symbol in bad_symbols:
            with self.subTest(symbol=symbol):
                with self.assertRaises(ValueError):
                    fetch_source_result(
                        adapter,
                        SourceRequest(
                            dataset=DatasetName.FUND_PREMIUM_DISCOUNT,
                            source_name=AKSHARE_SOURCE_ID,
                            start_date=date(2024, 1, 5),
                            end_date=date(2024, 1, 5),
                            symbols=(symbol,),
                        ),
                    )

    def test_adapter_fails_clearly_on_partial_batch_success(self) -> None:
        adapter = AkshareETFFundPremiumDiscountAdapter(
            fetch_fund_daily=lambda: [_daily_row()],
            fetch_etf_hist=lambda **_: [],
            fetch_fund_nav=lambda **_: [],
            fetch_open_fund_nav=lambda **_: [],
        )

        with self.assertRaisesRegex(ValueError, "no usable rows for requested symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_PREMIUM_DISCOUNT,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 5),
                    end_date=date(2024, 1, 5),
                    symbols=("510300.ETF_CN", "159915.ETF_CN"),
                ),
            )

    def test_route_signature_incompatibility_is_hard_failure(self) -> None:
        def bad_signature(required_arg):
            raise AssertionError(required_arg)

        adapter = AkshareETFFundPremiumDiscountAdapter(fetch_fund_daily=bad_signature)

        with self.assertRaises(TypeError):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_PREMIUM_DISCOUNT,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 5),
                    end_date=date(2024, 1, 5),
                    symbols=("510300.ETF_CN",),
                ),
            )


if __name__ == "__main__":
    unittest.main()
