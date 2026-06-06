from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareETFDailyBarAdapter,
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


class AkshareETFDailyBarAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = AkshareETFDailyBarAdapter(fetch_etf_hist=lambda **kwargs: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_etf_daily_bars(self) -> None:
        calls: list[dict] = []
        registry = DatasetRegistry()
        now = datetime(2024, 1, 12, 9, 0, 0, tzinfo=timezone.utc)

        def fake_fetch_etf_hist(**kwargs):
            calls.append(kwargs)
            return [
                {
                    "日期": "2024-01-09",
                    "开盘": "3.123",
                    "最高": 3.2,
                    "最低": "3.10",
                    "收盘": 3.18,
                    "成交量": "1,234,567",
                    "成交额": "9,876,543.21",
                }
            ]

        adapter = AkshareETFDailyBarAdapter(
            fetch_etf_hist=fake_fetch_etf_hist,
            now_fn=lambda: now,
            price_adjustment="raw",
        )
        request = SourceRequest(
            dataset=DatasetName.DAILY_BARS,
            source_name=AKSHARE_SOURCE_ID,
            start_date=date(2024, 1, 2),
            end_date=date(2024, 1, 10),
            symbols=("510300.ETF_CN",),
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                request,
                fetched_at=datetime(2024, 1, 12, 9, 5, 0, tzinfo=timezone.utc),
            )

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["symbol"], "510300")
        self.assertEqual(calls[0]["period"], "daily")
        self.assertEqual(calls[0]["start_date"], "20240102")
        self.assertEqual(calls[0]["end_date"], "20240110")
        self.assertEqual(calls[0]["adjust"], "")

        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["symbol"], "510300.ETF_CN")
        self.assertEqual(record["market"], "ETF_CN")
        self.assertEqual(record["trade_date"], "2024-01-09")
        self.assertEqual(record["adj_factor"], 1.0)
        self.assertEqual(record["price_adjustment"], "raw")
        self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(record["schema_version"], "v1")
        self.assertEqual(record["ingested_at"], now.isoformat())
        self.assertEqual(registry.validate_record(DatasetName.DAILY_BARS, record), ())

    def test_adapter_accepts_bare_symbol_and_normalizes_output_symbol(self) -> None:
        calls: list[dict] = []
        adapter = AkshareETFDailyBarAdapter(
            fetch_etf_hist=lambda **kwargs: calls.append(kwargs) or [
                {
                    "date": "2024-01-09",
                    "open": 3.1,
                    "high": 3.2,
                    "low": 3.0,
                    "close": 3.15,
                    "volume": 1000,
                    "amount": 3200,
                }
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("510300",),
            ),
        )
        self.assertEqual(calls[0]["symbol"], "510300")
        self.assertEqual(result.normalized_records[0]["symbol"], "510300.ETF_CN")

    def test_adapter_accepts_bare_listed_fund_symbol_and_normalizes_output_symbol(self) -> None:
        calls: list[dict] = []
        adapter = AkshareETFDailyBarAdapter(
            fetch_lof_hist=lambda **kwargs: calls.append(kwargs) or [
                {
                    "date": "2024-01-09",
                    "open": 1.1,
                    "high": 1.2,
                    "low": 1.0,
                    "close": 1.15,
                    "volume": 1000,
                    "amount": 1200,
                }
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("161725",),
            ),
        )
        self.assertEqual(calls[0]["symbol"], "161725")
        self.assertEqual(result.normalized_records[0]["symbol"], "161725.FUND_CN")
        self.assertEqual(result.normalized_records[0]["market"], "FUND_CN")

    def test_adapter_supports_multi_symbol_batches_and_sorts_by_symbol_then_trade_date(self) -> None:
        calls: list[dict] = []

        def fake_fetch_etf_hist(**kwargs):
            calls.append(kwargs)
            if kwargs["symbol"] == "510300":
                return [
                    {
                        "date": "2024-01-10",
                        "open": 3.2,
                        "high": 3.3,
                        "low": 3.1,
                        "close": 3.25,
                        "volume": 1200,
                        "amount": 3800,
                    },
                    {
                        "date": "2024-01-09",
                        "open": 3.1,
                        "high": 3.2,
                        "low": 3.0,
                        "close": 3.15,
                        "volume": 1000,
                        "amount": 3200,
                    },
                ]
            if kwargs["symbol"] == "159915":
                return [
                    {
                        "date": "2024-01-09",
                        "open": 1.8,
                        "high": 1.9,
                        "low": 1.7,
                        "close": 1.85,
                        "volume": 2200,
                        "amount": 4100,
                    }
                ]
            raise AssertionError(f"unexpected symbol: {kwargs['symbol']}")

        adapter = AkshareETFDailyBarAdapter(fetch_etf_hist=fake_fetch_etf_hist)
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 9),
                end_date=date(2024, 1, 10),
                symbols=("159915.ETF_CN", "510300", "510300.ETF_CN"),
            ),
        )

        self.assertEqual(
            calls,
            [
                {
                    "symbol": "159915",
                    "period": "daily",
                    "start_date": "20240109",
                    "end_date": "20240110",
                    "adjust": "",
                },
                {
                    "symbol": "510300",
                    "period": "daily",
                    "start_date": "20240109",
                    "end_date": "20240110",
                    "adjust": "",
                },
            ],
        )
        self.assertEqual(
            [(record["symbol"], record["trade_date"]) for record in result.normalized_records],
            [
                ("159915.ETF_CN", "2024-01-09"),
                ("510300.ETF_CN", "2024-01-09"),
                ("510300.ETF_CN", "2024-01-10"),
            ],
        )

    def test_adapter_handles_dataframe_like_payload(self) -> None:
        payload = _FakeDataFrame(
            [
                {
                    "date": "20240109",
                    "open": 3.1,
                    "high": 3.2,
                    "low": 3.0,
                    "close": 3.15,
                    "volume": 1000,
                    "amount": 3200,
                }
            ]
        )
        adapter = AkshareETFDailyBarAdapter(fetch_etf_hist=lambda **kwargs: payload)
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("510300",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["trade_date"], "2024-01-09")

    def test_adapter_sorts_and_deduplicates_exact_duplicate_rows(self) -> None:
        adapter = AkshareETFDailyBarAdapter(
            fetch_etf_hist=lambda **kwargs: [
                {
                    "date": "2024-01-10",
                    "open": 3.2,
                    "high": 3.3,
                    "low": 3.1,
                    "close": 3.25,
                    "volume": 1200,
                    "amount": 3800,
                },
                {
                    "date": "2024-01-09",
                    "open": 3.1,
                    "high": 3.2,
                    "low": 3.0,
                    "close": 3.15,
                    "volume": 1000,
                    "amount": 3200,
                },
                {
                    "date": "2024-01-10",
                    "open": 3.2,
                    "high": 3.3,
                    "low": 3.1,
                    "close": 3.25,
                    "volume": 1200,
                    "amount": 3800,
                },
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("510300",),
            ),
        )
        self.assertEqual(result.record_count, 2)
        self.assertEqual(
            [record["trade_date"] for record in result.normalized_records],
            ["2024-01-09", "2024-01-10"],
        )

    def test_adapter_rejects_conflicting_duplicate_trade_date_rows(self) -> None:
        adapter = AkshareETFDailyBarAdapter(
            fetch_etf_hist=lambda **kwargs: [
                {
                    "date": "2024-01-10",
                    "open": 3.2,
                    "high": 3.3,
                    "low": 3.1,
                    "close": 3.25,
                    "volume": 1200,
                    "amount": 3800,
                },
                {
                    "date": "2024-01-10",
                    "open": 3.21,
                    "high": 3.3,
                    "low": 3.1,
                    "close": 3.25,
                    "volume": 1200,
                    "amount": 3800,
                },
            ]
        )
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate ETF daily-bar row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )

    def test_adapter_filters_by_date_range_deterministically(self) -> None:
        adapter = AkshareETFDailyBarAdapter(
            fetch_etf_hist=lambda **kwargs: [
                {
                    "date": "2024-01-08",
                    "open": 3.0,
                    "high": 3.1,
                    "low": 2.9,
                    "close": 3.0,
                    "volume": 900,
                    "amount": 2800,
                },
                {
                    "date": "2024-01-09",
                    "open": 3.1,
                    "high": 3.2,
                    "low": 3.0,
                    "close": 3.15,
                    "volume": 1000,
                    "amount": 3200,
                },
                {
                    "date": "2024-01-10",
                    "open": 3.2,
                    "high": 3.3,
                    "low": 3.1,
                    "close": 3.25,
                    "volume": 1200,
                    "amount": 3800,
                },
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 9),
                end_date=date(2024, 1, 9),
                symbols=("510300",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["trade_date"], "2024-01-09")

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = AkshareETFDailyBarAdapter(fetch_etf_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_NAV_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )

    def test_adapter_rejects_missing_symbols(self) -> None:
        adapter = AkshareETFDailyBarAdapter(fetch_etf_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "requires at least one ETF/fund symbol, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_non_string_symbol_in_batch(self) -> None:
        adapter = AkshareETFDailyBarAdapter(fetch_etf_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Symbol at index 1 must be a non-empty string"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300", 123),  # type: ignore[arg-type]
                ),
            )

    def test_adapter_rejects_a_share_suffix(self) -> None:
        adapter = AkshareETFDailyBarAdapter(fetch_etf_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported ETF/fund market suffix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.SH",),
                ),
            )

    def test_adapter_rejects_hk_suffix(self) -> None:
        adapter = AkshareETFDailyBarAdapter(fetch_etf_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported ETF/fund market suffix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.HK",),
                ),
            )

    def test_adapter_accepts_explicit_listed_fund_suffix(self) -> None:
        calls: list[dict] = []
        adapter = AkshareETFDailyBarAdapter(
            fetch_lof_hist=lambda **kwargs: calls.append(kwargs) or [
                {
                    "date": "2024-01-09",
                    "open": 1.1,
                    "high": 1.2,
                    "low": 1.0,
                    "close": 1.15,
                    "volume": 1000,
                    "amount": 1200,
                }
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("161725.FUND_CN",),
            ),
        )
        self.assertEqual(calls[0]["symbol"], "161725")
        self.assertEqual(result.normalized_records[0]["symbol"], "161725.FUND_CN")
        self.assertEqual(result.normalized_records[0]["market"], "FUND_CN")

    def test_adapter_rejects_mismatched_fund_suffix_for_etf_code(self) -> None:
        adapter = AkshareETFDailyBarAdapter(fetch_etf_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Use '\\.ETF_CN' instead"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.FUND_CN",),
                ),
            )

    def test_adapter_rejects_mismatched_etf_suffix_for_listed_fund_code(self) -> None:
        adapter = AkshareETFDailyBarAdapter(fetch_etf_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Use '\\.FUND_CN' instead"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("161725.ETF_CN",),
                ),
            )

    def test_adapter_rejects_malformed_symbol_format(self) -> None:
        adapter = AkshareETFDailyBarAdapter(fetch_etf_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Expected 6-digit code"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("ETF510300",),
                ),
            )

    def test_adapter_rejects_a_share_stock_like_code(self) -> None:
        adapter = AkshareETFDailyBarAdapter(fetch_etf_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "A-share stock code is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.ETF_CN",),
                ),
            )

    def test_adapter_rejects_index_like_code(self) -> None:
        adapter = AkshareETFDailyBarAdapter(fetch_etf_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Index code is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("399001.ETF_CN",),
                ),
            )

    def test_adapter_rejects_unsupported_fund_code_prefix(self) -> None:
        adapter = AkshareETFDailyBarAdapter(fetch_etf_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported ETF/fund code prefix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("260108.ETF_CN",),
                ),
            )

    def test_adapter_rejects_unproven_listed_fund_code_families(self) -> None:
        adapter = AkshareETFDailyBarAdapter(fetch_etf_hist=lambda **kwargs: [])
        for symbol in (
            "160706.FUND_CN",
            "180012.FUND_CN",
            "150001.FUND_CN",
            "501018.FUND_CN",
        ):
            with self.subTest(symbol=symbol):
                with self.assertRaisesRegex(
                    ValueError,
                    "explicitly proven listed-fund code '161725'",
                ):
                    fetch_source_result(
                        adapter,
                        SourceRequest(
                            dataset=DatasetName.DAILY_BARS,
                            source_name=AKSHARE_SOURCE_ID,
                            symbols=(symbol,),
                        ),
                    )

    def test_adapter_rejects_malformed_payload_shape(self) -> None:
        adapter = AkshareETFDailyBarAdapter(
            fetch_etf_hist=lambda **kwargs: {"date": "2024-01-09"}
        )
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )

    def test_adapter_rejects_non_mapping_payload_row(self) -> None:
        adapter = AkshareETFDailyBarAdapter(fetch_etf_hist=lambda **kwargs: [1, 2, 3])
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )

    def test_adapter_rejects_missing_required_source_fields(self) -> None:
        adapter = AkshareETFDailyBarAdapter(
            fetch_etf_hist=lambda **kwargs: [
                {
                    "date": "2024-01-09",
                    "open": 3.1,
                    "high": 3.2,
                    "low": 3.0,
                    "close": 3.15,
                    "volume": 1000,
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )

    def test_adapter_rejects_invalid_trade_date_value(self) -> None:
        adapter = AkshareETFDailyBarAdapter(
            fetch_etf_hist=lambda **kwargs: [
                {
                    "date": "2024-99-09",
                    "open": 3.1,
                    "high": 3.2,
                    "low": 3.0,
                    "close": 3.15,
                    "volume": 1000,
                    "amount": 3200,
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid trade date value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )

    def test_adapter_accepts_supported_trade_date_formats(self) -> None:
        adapter = AkshareETFDailyBarAdapter(
            fetch_etf_hist=lambda **kwargs: [
                {
                    "date": "20240109",
                    "open": 3.1,
                    "high": 3.2,
                    "low": 3.0,
                    "close": 3.15,
                    "volume": 1000,
                    "amount": 3200,
                },
                {
                    "date": "2024-01-10T00:00:00",
                    "open": 3.2,
                    "high": 3.3,
                    "low": 3.1,
                    "close": 3.25,
                    "volume": 1200,
                    "amount": 3800,
                },
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("510300",),
            ),
        )
        self.assertEqual(
            [record["trade_date"] for record in result.normalized_records],
            ["2024-01-09", "2024-01-10"],
        )

    def test_adapter_rejects_invalid_numeric_value(self) -> None:
        adapter = AkshareETFDailyBarAdapter(
            fetch_etf_hist=lambda **kwargs: [
                {
                    "date": "2024-01-09",
                    "open": "nan",
                    "high": 3.2,
                    "low": 3.0,
                    "close": 3.15,
                    "volume": 1000,
                    "amount": 3200,
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid numeric value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )

    def test_adapter_rejects_inverted_date_range(self) -> None:
        adapter = AkshareETFDailyBarAdapter(fetch_etf_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Invalid date range"):
            adapter.fetch(
                DatasetName.DAILY_BARS,
                start_date=date(2024, 1, 10),
                end_date=date(2024, 1, 9),
                symbols=["510300.ETF_CN"],
            )

    def test_adapter_fails_when_any_requested_symbol_yields_no_usable_rows(self) -> None:
        def fake_fetch_etf_hist(**kwargs):
            if kwargs["symbol"] == "510300":
                return [
                    {
                        "date": "2024-01-09",
                        "open": 3.1,
                        "high": 3.2,
                        "low": 3.0,
                        "close": 3.15,
                        "volume": 1000,
                        "amount": 3200,
                    }
                ]
            if kwargs["symbol"] == "159915":
                return []
            raise AssertionError(f"unexpected symbol: {kwargs['symbol']}")

        adapter = AkshareETFDailyBarAdapter(fetch_etf_hist=fake_fetch_etf_hist)
        with self.assertRaisesRegex(ValueError, "yielded no usable rows.*159915\\.ETF_CN"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 9),
                    end_date=date(2024, 1, 10),
                    symbols=("510300.ETF_CN", "159915.ETF_CN"),
                ),
            )

    def test_adapter_supports_qfq_adjustment_mapping(self) -> None:
        calls: list[dict] = []
        adapter = AkshareETFDailyBarAdapter(
            fetch_etf_hist=lambda **kwargs: calls.append(kwargs) or [
                {
                    "date": "2024-01-09",
                    "open": 3.1,
                    "high": 3.2,
                    "low": 3.0,
                    "close": 3.15,
                    "volume": 1000,
                    "amount": 3200,
                }
            ],
            price_adjustment="qfq",
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("510300",),
            ),
        )
        self.assertEqual(calls[0]["adjust"], "qfq")
        self.assertEqual(result.normalized_records[0]["price_adjustment"], "qfq")

    def test_adapter_rejects_unsupported_price_adjustment(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported price_adjustment"):
            AkshareETFDailyBarAdapter(
                fetch_etf_hist=lambda **kwargs: [],
                price_adjustment="invalid",
            )

    def test_adapter_falls_back_to_sina_when_primary_route_unavailable(self) -> None:
        class ProxyError(Exception):
            pass

        primary_calls: list[dict] = []
        fallback_calls: list[dict] = []

        def failing_primary(**kwargs):
            primary_calls.append(kwargs)
            raise ProxyError("Unable to connect to proxy: push2his.eastmoney.com")

        def fallback_sina(**kwargs):
            fallback_calls.append(kwargs)
            return [
                {
                    "date": "2024-01-09",
                    "open": 3.1,
                    "high": 3.2,
                    "low": 3.0,
                    "close": 3.15,
                    "volume": 1000,
                    "amount": 3200,
                }
            ]

        adapter = AkshareETFDailyBarAdapter(
            fetch_etf_hist=failing_primary,
            fetch_etf_hist_sina=fallback_sina,
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("510300.ETF_CN",),
                start_date=date(2024, 1, 9),
                end_date=date(2024, 1, 10),
            ),
        )

        self.assertEqual(len(primary_calls), 1)
        self.assertEqual(len(fallback_calls), 1)
        self.assertEqual(fallback_calls[0]["symbol"], "sh510300")
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "510300.ETF_CN")

    def test_adapter_falls_back_to_sina_for_listed_fund_when_primary_route_unavailable(self) -> None:
        class ProxyError(Exception):
            pass

        primary_calls: list[dict] = []
        fallback_calls: list[dict] = []

        def failing_primary(**kwargs):
            primary_calls.append(kwargs)
            raise ProxyError("Unable to connect to proxy: fund_lof_hist_em")

        def fallback_sina(**kwargs):
            fallback_calls.append(kwargs)
            return [
                {
                    "date": "2024-01-09",
                    "open": 1.1,
                    "high": 1.2,
                    "low": 1.0,
                    "close": 1.15,
                    "volume": 1000,
                    "amount": 1200,
                }
            ]

        adapter = AkshareETFDailyBarAdapter(
            fetch_lof_hist=failing_primary,
            fetch_etf_hist_sina=fallback_sina,
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("161725.FUND_CN",),
                start_date=date(2024, 1, 9),
                end_date=date(2024, 1, 10),
            ),
        )

        self.assertEqual(len(primary_calls), 1)
        self.assertEqual(len(fallback_calls), 1)
        self.assertEqual(fallback_calls[0]["symbol"], "sz161725")
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "161725.FUND_CN")
        self.assertEqual(result.normalized_records[0]["market"], "FUND_CN")

    def test_adapter_uses_sz_prefix_for_sina_fallback_symbol(self) -> None:
        class ProxyError(Exception):
            pass

        fallback_calls: list[dict] = []

        def fallback_sina(**kwargs):
            fallback_calls.append(kwargs)
            return [
                {
                    "date": "2024-01-09",
                    "open": 1.1,
                    "high": 1.2,
                    "low": 1.0,
                    "close": 1.15,
                    "volume": 1000,
                    "amount": 1200,
                }
            ]

        adapter = AkshareETFDailyBarAdapter(
            fetch_etf_hist=lambda **kwargs: (_ for _ in ()).throw(
                ProxyError("fund_etf_hist_em unavailable")
            ),
            fetch_etf_hist_sina=fallback_sina,
        )
        fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("159915.ETF_CN",),
            ),
        )
        self.assertEqual(fallback_calls[0]["symbol"], "sz159915")

    def test_adapter_does_not_fallback_on_primary_contract_error(self) -> None:
        fallback_called = False

        def fallback_sina(**kwargs):
            nonlocal fallback_called
            fallback_called = True
            return []

        adapter = AkshareETFDailyBarAdapter(
            fetch_etf_hist=lambda **kwargs: {"not": "list-like payload"},
            fetch_etf_hist_sina=fallback_sina,
        )
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )
        self.assertFalse(fallback_called)

    def test_adapter_raises_when_all_routes_unavailable(self) -> None:
        class ProxyError(Exception):
            pass

        adapter = AkshareETFDailyBarAdapter(
            fetch_etf_hist=lambda **kwargs: (_ for _ in ()).throw(
                ProxyError("push2his.eastmoney.com route unavailable")
            ),
            fetch_etf_hist_sina=lambda **kwargs: (_ for _ in ()).throw(
                ProxyError("hq.sinajs.cn route unavailable")
            ),
        )
        with self.assertRaisesRegex(
            RuntimeError,
            "AKShare ETF daily-bar routes unavailable after bounded fallback",
        ):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300",),
                ),
            )


if __name__ == "__main__":
    unittest.main()
