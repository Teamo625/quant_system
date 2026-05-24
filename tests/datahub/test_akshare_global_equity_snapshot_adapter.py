from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareGlobalEquitySnapshotAdapter,
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


class AkshareGlobalEquitySnapshotAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = AkshareGlobalEquitySnapshotAdapter(fetch_global_equity_spot=lambda: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_records(self) -> None:
        calls: list[str] = []
        registry = DatasetRegistry()
        now = datetime(2024, 1, 12, 10, 0, 0, tzinfo=timezone.utc)

        def fake_fetch_global_equity_spot():
            calls.append("called")
            return [
                {
                    "代码": "105.AAPL",
                    "最新价": "185.10",
                    "涨跌幅": "0.80%",
                    "trade_date": "2024-01-11",
                    "source_ts": "2024-01-12 09:31:00",
                },
                {
                    "代码": "106.MSFT",
                    "最新价": 410.2,
                    "涨跌幅": -0.2,
                    "date": "20240111",
                    "currency": "usd",
                    "exchange": "nasdaq",
                    "region": "global",
                },
            ]

        adapter = AkshareGlobalEquitySnapshotAdapter(
            fetch_global_equity_spot=fake_fetch_global_equity_spot,
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("AAPL.US", "MSFT"),
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(adapter, request)

        self.assertEqual(calls, ["called"])
        self.assertEqual(result.record_count, 2)

        first_record = result.normalized_records[0]
        self.assertEqual(first_record["symbol"], "AAPL.US")
        self.assertEqual(first_record["market"], "US")
        self.assertEqual(first_record["trade_date"], "2024-01-11")
        self.assertEqual(first_record["close"], 185.1)
        self.assertEqual(first_record["change_pct"], 0.8)
        self.assertEqual(first_record["currency"], "USD")
        self.assertEqual(first_record["exchange"], "NASDAQ")
        self.assertEqual(first_record["region"], "GLOBAL")
        self.assertEqual(first_record["source_ts"], "2024-01-12T09:31:00")
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(first_record["schema_version"], "v1")
        self.assertEqual(first_record["ingested_at"], now.isoformat())

        second_record = result.normalized_records[1]
        self.assertEqual(second_record["symbol"], "MSFT.US")
        self.assertEqual(second_record["currency"], "USD")
        self.assertEqual(second_record["exchange"], "NASDAQ")
        self.assertEqual(second_record["region"], "GLOBAL")
        self.assertNotIn("source_ts", second_record)

        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.GLOBAL_EQUITY_SNAPSHOT, record),
                (),
            )

    def test_adapter_accepts_common_symbol_forms(self) -> None:
        for user_symbol in ("AAPL.US", "AAPL", "105.AAPL", "aapl.us"):
            adapter = AkshareGlobalEquitySnapshotAdapter(
                fetch_global_equity_spot=lambda: [
                    {"代码": "105.AAPL", "最新价": 185.1, "涨跌幅": "0.8"},
                    {"代码": "106.MSFT", "最新价": 410.2, "涨跌幅": "-0.2"},
                ],
                now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
            )
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=(user_symbol,),
                ),
            )
            with self.subTest(symbol=user_symbol):
                self.assertEqual(result.record_count, 1)
                self.assertEqual(result.normalized_records[0]["symbol"], "AAPL.US")

    def test_adapter_supports_stock_us_spot_fallback_payload_shape(self) -> None:
        adapter = AkshareGlobalEquitySnapshotAdapter(
            fetch_global_equity_spot=lambda: [
                {
                    "symbol": "NVDA",
                    "price": "219.51",
                    "chg": "-1.77",
                    "market": "NASDAQ",
                }
            ],
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("NVDA",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["symbol"], "NVDA.US")
        self.assertEqual(record["close"], 219.51)
        self.assertEqual(record["change_pct"], -1.77)
        self.assertEqual(record["exchange"], "NASDAQ")

    def test_adapter_uses_runtime_fallback_when_primary_route_network_unavailable(self) -> None:
        call_trace: list[str] = []

        class ProxyError(Exception):
            pass

        def fake_fetch_em():
            call_trace.append("em")
            raise ProxyError("proxy connect failed to push2.eastmoney.com")

        def fake_fetch_sina():
            call_trace.append("sina")
            return [{"symbol": "AAPL", "price": 185.1, "chg": "0.8", "market": "NASDAQ"}]

        adapter = AkshareGlobalEquitySnapshotAdapter(
            fetch_global_equity_spot_em=fake_fetch_em,
            fetch_global_equity_spot_sina=fake_fetch_sina,
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("AAPL.US",),
            ),
        )
        self.assertEqual(call_trace, ["em", "sina"])
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "AAPL.US")

    def test_adapter_does_not_mask_non_network_primary_route_error(self) -> None:
        call_trace: list[str] = []

        def fake_fetch_em():
            call_trace.append("em")
            raise ValueError("bad payload")

        def fake_fetch_sina():
            call_trace.append("sina")
            return [{"symbol": "AAPL", "price": 185.1, "chg": "0.8"}]

        adapter = AkshareGlobalEquitySnapshotAdapter(
            fetch_global_equity_spot_em=fake_fetch_em,
            fetch_global_equity_spot_sina=fake_fetch_sina,
        )
        with self.assertRaisesRegex(ValueError, "bad payload"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("AAPL",),
                ),
            )
        self.assertEqual(call_trace, ["em"])

    def test_adapter_keeps_contract_failures_as_failures_on_fallback_route(self) -> None:
        class ProxyError(Exception):
            pass

        def fake_fetch_em():
            raise ProxyError("proxy timeout on eastmoney")

        def fake_fetch_sina():
            return [{"symbol": "AAPL", "price": "bad", "chg": "0.8"}]

        adapter = AkshareGlobalEquitySnapshotAdapter(
            fetch_global_equity_spot_em=fake_fetch_em,
            fetch_global_equity_spot_sina=fake_fetch_sina,
        )
        with self.assertRaisesRegex(ValueError, "Invalid close value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("AAPL",),
                ),
            )

    def test_adapter_treats_stock_us_spot_keyerror_data_as_route_unavailable(self) -> None:
        def fake_fetch_sina():
            raise KeyError("data")

        adapter = AkshareGlobalEquitySnapshotAdapter(
            fetch_global_equity_spot_sina=fake_fetch_sina,
        )
        with self.assertRaisesRegex(
            RuntimeError,
            "stock_us_spot -> KeyError: 'data'",
        ):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("AAPL",),
                ),
            )

    def test_adapter_does_not_mask_non_data_keyerror_on_stock_us_spot(self) -> None:
        def fake_fetch_sina():
            raise KeyError("close")

        adapter = AkshareGlobalEquitySnapshotAdapter(
            fetch_global_equity_spot_sina=fake_fetch_sina,
        )
        with self.assertRaisesRegex(KeyError, "'close'"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("AAPL",),
                ),
            )

    def test_adapter_skips_unparseable_unrelated_symbols_when_symbol_filter_is_provided(
        self,
    ) -> None:
        adapter = AkshareGlobalEquitySnapshotAdapter(
            fetch_global_equity_spot=lambda: [
                {"symbol": "HUDA U", "price": 1.23, "chg": "0.1"},
                {"symbol": "AAPL", "price": 185.1, "chg": "0.8", "market": "NASDAQ"},
            ],
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("AAPL.US",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "AAPL.US")

    def test_adapter_surfaces_route_level_network_diagnostics_when_all_routes_unavailable(
        self,
    ) -> None:
        class ProxyError(Exception):
            pass

        def fake_fetch_em():
            raise ProxyError("proxy failed for 72.push2.eastmoney.com")

        def fake_fetch_sina():
            raise ProxyError("proxy failed for stock.finance.sina.com.cn")

        adapter = AkshareGlobalEquitySnapshotAdapter(
            fetch_global_equity_spot_em=fake_fetch_em,
            fetch_global_equity_spot_sina=fake_fetch_sina,
        )
        with self.assertRaisesRegex(RuntimeError, "global-equity fetch routes unavailable"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("AAPL",),
                ),
            )

    def test_adapter_network_unavailable_classifier_boundaries(self) -> None:
        adapter = AkshareGlobalEquitySnapshotAdapter(fetch_global_equity_spot=lambda: [])
        self.assertTrue(
            adapter._is_global_equity_network_unavailable(
                OSError(111, "connection refused to stock.finance.sina.com.cn")
            )
        )
        self.assertFalse(
            adapter._is_global_equity_network_unavailable(
                ValueError("schema parsing failed")
            )
        )
        self.assertTrue(
            adapter._is_global_equity_route_unavailable(
                route_name="stock_us_spot",
                exc=KeyError("data"),
            )
        )
        self.assertFalse(
            adapter._is_global_equity_route_unavailable(
                route_name="stock_us_spot",
                exc=KeyError("close"),
            )
        )
        self.assertFalse(
            adapter._is_global_equity_route_unavailable(
                route_name="stock_us_spot_em",
                exc=KeyError("data"),
            )
        )

    def test_adapter_rejects_ambiguous_fetch_injection_configuration(self) -> None:
        with self.assertRaisesRegex(ValueError, "Provide either fetch_global_equity_spot"):
            AkshareGlobalEquitySnapshotAdapter(
                fetch_global_equity_spot=lambda: [],
                fetch_global_equity_spot_em=lambda: [],
            )

    def test_adapter_bounds_default_subset_when_symbols_missing(self) -> None:
        adapter = AkshareGlobalEquitySnapshotAdapter(
            fetch_global_equity_spot=lambda: [
                {"代码": "106.MSFT", "最新价": 410.2, "涨跌幅": -0.2},
                {"代码": "105.AAPL", "最新价": 185.1, "涨跌幅": 0.8},
                {"代码": "105.NVDA", "最新价": 920.4, "涨跌幅": 1.6},
            ],
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
            max_records_without_symbols=2,
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 2)
        self.assertEqual(
            [record["symbol"] for record in result.normalized_records],
            ["AAPL.US", "MSFT.US"],
        )

    def test_adapter_falls_back_trade_date_from_clock_when_source_date_missing(self) -> None:
        now = datetime(2024, 1, 12, 10, 0, 0, tzinfo=timezone.utc)
        adapter = AkshareGlobalEquitySnapshotAdapter(
            fetch_global_equity_spot=lambda: [
                {"代码": "105.AAPL", "最新价": 185.1, "涨跌幅": "0.8%"}
            ],
            now_fn=lambda: now,
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("AAPL",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["trade_date"], "2024-01-12")

    def test_adapter_filters_records_by_date_range_when_requested(self) -> None:
        adapter = AkshareGlobalEquitySnapshotAdapter(
            fetch_global_equity_spot=lambda: [
                {"代码": "105.AAPL", "最新价": 185.1, "涨跌幅": "0.8%", "date": "2024-01-10"},
                {"代码": "106.MSFT", "最新价": 410.2, "涨跌幅": "-0.2%", "date": "2024-01-11"},
            ],
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 11),
                end_date=date(2024, 1, 11),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "MSFT.US")

    def test_adapter_omits_optional_source_ts_when_empty(self) -> None:
        adapter = AkshareGlobalEquitySnapshotAdapter(
            fetch_global_equity_spot=lambda: [
                {
                    "代码": "105.AAPL",
                    "最新价": 185.1,
                    "涨跌幅": "0.8%",
                    "source_ts": " ",
                }
            ],
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("AAPL",),
            ),
        )
        self.assertNotIn("source_ts", result.normalized_records[0])

    def test_adapter_dedupes_benign_duplicates_deterministically(self) -> None:
        adapter = AkshareGlobalEquitySnapshotAdapter(
            fetch_global_equity_spot=lambda: [
                {
                    "代码": "105.AAPL",
                    "最新价": 185.1,
                    "涨跌幅": "0.8%",
                    "date": "2024-01-11",
                    "source_ts": "2024-01-12 09:30:00",
                },
                {
                    "代码": "105.AAPL",
                    "最新价": 185.1,
                    "涨跌幅": "0.8%",
                    "date": "2024-01-11",
                    "source_ts": "2024-01-12 09:31:00",
                },
            ],
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("AAPL",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(
            result.normalized_records[0]["source_ts"],
            "2024-01-12T09:31:00",
        )

    def test_adapter_rejects_conflicting_duplicate_rows(self) -> None:
        adapter = AkshareGlobalEquitySnapshotAdapter(
            fetch_global_equity_spot=lambda: [
                {
                    "代码": "105.AAPL",
                    "最新价": 185.1,
                    "涨跌幅": "0.8%",
                    "date": "2024-01-11",
                },
                {
                    "代码": "105.AAPL",
                    "最新价": 188.2,
                    "涨跌幅": "0.8%",
                    "date": "2024-01-11",
                },
            ],
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        with self.assertRaisesRegex(
            ValueError,
            "Conflicting duplicate global equity snapshot row",
        ):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("AAPL",),
                ),
            )

    def test_adapter_handles_dataframe_like_payload(self) -> None:
        payload = _FakeDataFrame(
            [{"代码": "106.MSFT", "最新价": "410.20", "涨跌幅": "-0.20%"}]
        )
        adapter = AkshareGlobalEquitySnapshotAdapter(
            fetch_global_equity_spot=lambda: payload,
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("MSFT.US",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "MSFT.US")
        self.assertEqual(result.normalized_records[0]["close"], 410.2)
        self.assertEqual(result.normalized_records[0]["change_pct"], -0.2)

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = AkshareGlobalEquitySnapshotAdapter(fetch_global_equity_spot=lambda: [])
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("AAPL.US",),
                ),
            )

    def test_adapter_rejects_unsupported_market_suffix_filter(self) -> None:
        adapter = AkshareGlobalEquitySnapshotAdapter(fetch_global_equity_spot=lambda: [])
        with self.assertRaisesRegex(ValueError, "Unsupported global equity market suffix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("AAPL.HK",),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape(self) -> None:
        adapter = AkshareGlobalEquitySnapshotAdapter(
            fetch_global_equity_spot=lambda: {"代码": "105.AAPL", "最新价": 185.1, "涨跌幅": 0.8}
        )
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_non_mapping_payload_row(self) -> None:
        adapter = AkshareGlobalEquitySnapshotAdapter(
            fetch_global_equity_spot=lambda: [1]
        )
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_invalid_numeric_or_date_values(self) -> None:
        bad_close_adapter = AkshareGlobalEquitySnapshotAdapter(
            fetch_global_equity_spot=lambda: [
                {"代码": "105.AAPL", "最新价": "bad", "涨跌幅": "0.8%"}
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid close value"):
            fetch_source_result(
                bad_close_adapter,
                SourceRequest(
                    dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("AAPL",),
                ),
            )

        bad_change_pct_adapter = AkshareGlobalEquitySnapshotAdapter(
            fetch_global_equity_spot=lambda: [
                {"代码": "105.AAPL", "最新价": 185.1, "涨跌幅": "bad%"}
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid change_pct value"):
            fetch_source_result(
                bad_change_pct_adapter,
                SourceRequest(
                    dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("AAPL",),
                ),
            )

        bad_date_adapter = AkshareGlobalEquitySnapshotAdapter(
            fetch_global_equity_spot=lambda: [
                {
                    "代码": "105.AAPL",
                    "最新价": 185.1,
                    "涨跌幅": "0.8%",
                    "trade_date": "2024-13-11",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid trade date value"):
            fetch_source_result(
                bad_date_adapter,
                SourceRequest(
                    dataset=DatasetName.GLOBAL_EQUITY_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("AAPL",),
                ),
            )


if __name__ == "__main__":
    unittest.main()
