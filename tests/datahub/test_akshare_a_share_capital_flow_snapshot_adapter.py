from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareCapitalFlowSnapshotAdapter,
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


def _build_adapter(
    *,
    fetch_capital_flow=None,
    fetch_turnover_hist=None,
    fetch_northbound=None,
    now_fn=None,
) -> AkshareAShareCapitalFlowSnapshotAdapter:
    return AkshareAShareCapitalFlowSnapshotAdapter(
        fetch_capital_flow=fetch_capital_flow,
        fetch_turnover_hist=fetch_turnover_hist,
        fetch_northbound=fetch_northbound,
        now_fn=now_fn,
    )


class AkshareAShareCapitalFlowSnapshotAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = _build_adapter(fetch_capital_flow=lambda **kwargs: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_capital_flow_snapshot(self) -> None:
        capital_flow_calls: list[dict[str, str]] = []
        turnover_calls: list[dict[str, str]] = []
        northbound_calls: list[dict[str, str]] = []
        now = datetime(2024, 6, 12, 16, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        def fake_fetch_capital_flow(*, stock: str, market: str):
            capital_flow_calls.append({"stock": stock, "market": market})
            return [
                {
                    "日期": "2024-06-10",
                    "主力净流入-净额": "123.50",
                    "净流入-净额": "100.0",
                },
                {
                    "日期": "2024-06-11",
                    "主力净流入-净额": 90.0,
                },
            ]

        def fake_fetch_turnover_hist(
            *,
            symbol: str,
            period: str,
            start_date: str,
            end_date: str,
            adjust: str,
        ):
            turnover_calls.append(
                {
                    "symbol": symbol,
                    "period": period,
                    "start_date": start_date,
                    "end_date": end_date,
                    "adjust": adjust,
                }
            )
            return [
                {"日期": "2024-06-10", "换手率": "2.10"},
                {"日期": "2024-06-11", "换手率": "2.20"},
            ]

        def fake_fetch_northbound(*, symbol: str):
            northbound_calls.append({"symbol": symbol})
            return [
                {"持股日期": "2024-06-10", "今日增持资金": "15.30"},
                {"持股日期": "2024-05-31", "今日增持资金": 8.0},
            ]

        adapter = _build_adapter(
            fetch_capital_flow=fake_fetch_capital_flow,
            fetch_turnover_hist=fake_fetch_turnover_hist,
            fetch_northbound=fake_fetch_northbound,
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("600000.SH",),
            start_date=date(2024, 6, 10),
            end_date=date(2024, 6, 11),
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                request,
                fetched_at=datetime(2024, 6, 12, 16, 5, 0, tzinfo=timezone.utc),
            )

        self.assertEqual(capital_flow_calls, [{"stock": "600000", "market": "sh"}])
        self.assertEqual(
            turnover_calls,
            [
                {
                    "symbol": "600000",
                    "period": "daily",
                    "start_date": "20240610",
                    "end_date": "20240611",
                    "adjust": "",
                }
            ],
        )
        self.assertEqual(northbound_calls, [{"symbol": "600000"}])

        self.assertEqual(result.record_count, 2)
        record_0 = result.normalized_records[0]
        record_1 = result.normalized_records[1]

        self.assertEqual(record_0["symbol"], "600000.SH")
        self.assertEqual(record_0["market"], "CN")
        self.assertEqual(record_0["trade_date"], "2024-06-10")
        self.assertEqual(record_0["main_net_inflow"], 123.5)
        self.assertEqual(record_0["net_inflow"], 100.0)
        self.assertEqual(record_0["turnover_rate"], 2.1)
        self.assertEqual(record_0["northbound_net_buy"], 15.3)
        self.assertEqual(record_0["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(record_0["schema_version"], "v1")
        self.assertEqual(record_0["ingested_at"], now.isoformat())

        self.assertEqual(record_1["trade_date"], "2024-06-11")
        self.assertEqual(record_1["main_net_inflow"], 90.0)
        self.assertNotIn("northbound_net_buy", record_1)
        self.assertEqual(record_1["turnover_rate"], 2.2)

        self.assertEqual(
            registry.validate_record(DatasetName.CAPITAL_FLOW_SNAPSHOT, record_0),
            (),
        )
        self.assertEqual(
            registry.validate_record(DatasetName.CAPITAL_FLOW_SNAPSHOT, record_1),
            (),
        )

    def test_adapter_supports_dataframe_like_payloads(self) -> None:
        adapter = _build_adapter(
            fetch_capital_flow=lambda **kwargs: _FakeDataFrame(
                [
                    {
                        "日期": "2024-06-10",
                        "主力净流入-净额": 101.0,
                    }
                ]
            ),
            fetch_turnover_hist=lambda **kwargs: _FakeDataFrame(
                [{"日期": "2024-06-10", "换手率": 1.8}]
            ),
            fetch_northbound=lambda **kwargs: _FakeDataFrame(
                [{"持股日期": "2024-06-10", "今日增持资金": 5.0}]
            ),
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000001.SZ",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "000001.SZ")
        self.assertEqual(result.normalized_records[0]["turnover_rate"], 1.8)
        self.assertEqual(result.normalized_records[0]["northbound_net_buy"], 5.0)

    def test_symbol_normalization_accepts_canonical_prefix_and_raw_6_digit(self) -> None:
        adapter = _build_adapter(
            fetch_capital_flow=lambda **kwargs: [
                {"日期": "2024-06-10", "主力净流入-净额": 1.0}
            ],
            fetch_turnover_hist=lambda **kwargs: [],
            fetch_northbound=lambda **kwargs: [],
        )

        canonical_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
            ),
        )
        self.assertEqual(canonical_result.normalized_records[0]["symbol"], "600000.SH")

        prefixed_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("sh600000",),
            ),
        )
        self.assertEqual(prefixed_result.normalized_records[0]["symbol"], "600000.SH")

        raw_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000",),
            ),
        )
        self.assertEqual(raw_result.normalized_records[0]["symbol"], "600000.SH")

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = _build_adapter(fetch_capital_flow=lambda **kwargs: [])
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
        adapter = _build_adapter(fetch_capital_flow=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "requires exactly one symbol, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )
        with self.assertRaisesRegex(ValueError, "exactly one symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH", "000001.SZ"),
                ),
            )

    def test_adapter_rejects_invalid_hk_etf_and_index_like_symbols(self) -> None:
        adapter = _build_adapter(fetch_capital_flow=lambda **kwargs: [])

        with self.assertRaisesRegex(ValueError, "market suffix|Invalid symbol filter format"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "ETF or fund symbol is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.SH",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Index symbol is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("399001.SZ",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "market-code combination"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SZ",),
                ),
            )

    def test_route_symbol_market_conversion_is_deterministic(self) -> None:
        calls: list[dict[str, str]] = []

        def fake_fetch_capital_flow(*, stock: str, market: str):
            calls.append({"stock": stock, "market": market})
            return [{"日期": "2024-06-10", "主力净流入-净额": 1.0}]

        adapter = _build_adapter(
            fetch_capital_flow=fake_fetch_capital_flow,
            fetch_turnover_hist=lambda **kwargs: [],
            fetch_northbound=lambda **kwargs: [],
        )

        fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000001",),
            ),
        )
        fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("920000.BJ",),
            ),
        )

        self.assertEqual(
            calls,
            [
                {"stock": "000001", "market": "sz"},
                {"stock": "920000", "market": "bj"},
            ],
        )

    def test_start_end_date_filtering_uses_normalized_trade_date(self) -> None:
        adapter = _build_adapter(
            fetch_capital_flow=lambda **kwargs: [
                {"日期": "2024-06-10", "主力净流入-净额": 1.0},
                {"日期": "2024-06-11", "主力净流入-净额": 2.0},
                {"日期": "2024-06-12", "主力净流入-净额": 3.0},
            ],
            fetch_turnover_hist=lambda **kwargs: [],
            fetch_northbound=lambda **kwargs: [],
        )

        in_range = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
                start_date=date(2024, 6, 11),
                end_date=date(2024, 6, 11),
            ),
        )
        self.assertEqual(in_range.record_count, 1)
        self.assertEqual(in_range.normalized_records[0]["trade_date"], "2024-06-11")

        out_range = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
                start_date=date(2024, 6, 20),
                end_date=date(2024, 6, 21),
            ),
        )
        self.assertEqual(out_range.record_count, 0)

    def test_turnover_route_uses_bounded_dates_from_primary_when_request_not_given(self) -> None:
        turnover_calls: list[dict[str, str]] = []

        def fake_fetch_turnover_hist(
            *,
            symbol: str,
            period: str,
            start_date: str,
            end_date: str,
            adjust: str,
        ):
            turnover_calls.append(
                {
                    "symbol": symbol,
                    "period": period,
                    "start_date": start_date,
                    "end_date": end_date,
                    "adjust": adjust,
                }
            )
            return []

        adapter = _build_adapter(
            fetch_capital_flow=lambda **kwargs: [
                {"日期": "2024-06-10", "主力净流入-净额": 1.0},
                {"日期": "2024-06-11", "主力净流入-净额": 2.0},
            ],
            fetch_turnover_hist=fake_fetch_turnover_hist,
            fetch_northbound=lambda **kwargs: [],
        )

        fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
            ),
        )
        self.assertEqual(
            turnover_calls,
            [
                {
                    "symbol": "600000",
                    "period": "daily",
                    "start_date": "20240610",
                    "end_date": "20240611",
                    "adjust": "",
                }
            ],
        )

    def test_optional_metrics_are_not_invented_when_unavailable(self) -> None:
        registry = DatasetRegistry()
        adapter = _build_adapter(
            fetch_capital_flow=lambda **kwargs: [
                {"日期": "2024-06-10", "主力净流入-净额": 120.0}
            ],
            fetch_turnover_hist=lambda **kwargs: [],
            fetch_northbound=lambda **kwargs: [],
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
            ),
        )
        record = result.normalized_records[0]
        self.assertNotIn("net_inflow", record)
        self.assertNotIn("turnover_rate", record)
        self.assertNotIn("northbound_net_buy", record)
        self.assertEqual(
            registry.validate_record(DatasetName.CAPITAL_FLOW_SNAPSHOT, record),
            (),
        )

    def test_adapter_deduplicates_benign_exact_duplicate_rows(self) -> None:
        row = {"日期": "2024-06-10", "主力净流入-净额": 120.0}
        adapter = _build_adapter(
            fetch_capital_flow=lambda **kwargs: [row, dict(row)],
            fetch_turnover_hist=lambda **kwargs: [],
            fetch_northbound=lambda **kwargs: [],
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
            ),
        )
        self.assertEqual(result.record_count, 1)

    def test_adapter_merges_duplicate_rows_with_complementary_optional_values(self) -> None:
        adapter = _build_adapter(
            fetch_capital_flow=lambda **kwargs: [
                {"日期": "2024-06-10", "主力净流入-净额": 120.0},
                {"日期": "2024-06-10", "主力净流入-净额": 120.0, "净流入-净额": 80.0},
            ],
            fetch_turnover_hist=lambda **kwargs: [],
            fetch_northbound=lambda **kwargs: [],
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["net_inflow"], 80.0)

    def test_adapter_rejects_conflicting_duplicate_same_identity(self) -> None:
        adapter = _build_adapter(
            fetch_capital_flow=lambda **kwargs: [
                {"日期": "2024-06-10", "主力净流入-净额": 120.0},
                {"日期": "2024-06-10", "主力净流入-净额": 121.0},
            ],
            fetch_turnover_hist=lambda **kwargs: [],
            fetch_northbound=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "Conflicting duplicate A-share capital-flow row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_conflicting_duplicate_turnover_row(self) -> None:
        adapter = _build_adapter(
            fetch_capital_flow=lambda **kwargs: [
                {"日期": "2024-06-10", "主力净流入-净额": 120.0}
            ],
            fetch_turnover_hist=lambda **kwargs: [
                {"日期": "2024-06-10", "换手率": 1.0},
                {"日期": "2024-06-10", "换手率": 2.0},
            ],
            fetch_northbound=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "Conflicting duplicate A-share turnover row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape(self) -> None:
        adapter = _build_adapter(fetch_capital_flow=lambda **kwargs: {"日期": "2024-06-10"})
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_non_mapping_payload_row(self) -> None:
        adapter = _build_adapter(fetch_capital_flow=lambda **kwargs: ["bad-row"])
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_missing_required_source_field(self) -> None:
        adapter = _build_adapter(
            fetch_capital_flow=lambda **kwargs: [{"日期": "2024-06-10"}],
            fetch_turnover_hist=lambda **kwargs: [],
            fetch_northbound=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_invalid_trade_date(self) -> None:
        adapter = _build_adapter(
            fetch_capital_flow=lambda **kwargs: [
                {"日期": "not-a-date", "主力净流入-净额": 12.0}
            ],
            fetch_turnover_hist=lambda **kwargs: [],
            fetch_northbound=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "Invalid trade_date value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_invalid_numeric_values(self) -> None:
        adapter = _build_adapter(
            fetch_capital_flow=lambda **kwargs: [
                {"日期": "2024-06-10", "主力净流入-净额": "not-a-number"}
            ],
            fetch_turnover_hist=lambda **kwargs: [],
            fetch_northbound=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "Invalid main_net_inflow value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_supplemental_network_unavailable_keeps_core_record(self) -> None:
        registry = DatasetRegistry()
        adapter = _build_adapter(
            fetch_capital_flow=lambda **kwargs: [
                {"日期": "2024-06-10", "主力净流入-净额": 120.0}
            ],
            fetch_turnover_hist=lambda **kwargs: (_ for _ in ()).throw(
                OSError(111, "connection refused to eastmoney endpoint")
            ),
            fetch_northbound=lambda **kwargs: (_ for _ in ()).throw(
                RuntimeError("ProxyError: proxy down")
            ),
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["main_net_inflow"], 120.0)
        self.assertNotIn("turnover_rate", record)
        self.assertNotIn("northbound_net_buy", record)
        self.assertEqual(
            registry.validate_record(DatasetName.CAPITAL_FLOW_SNAPSHOT, record),
            (),
        )

    def test_supplemental_contract_issue_does_not_get_hidden(self) -> None:
        adapter = _build_adapter(
            fetch_capital_flow=lambda **kwargs: [
                {"日期": "2024-06-10", "主力净流入-净额": 120.0}
            ],
            fetch_turnover_hist=lambda **kwargs: [
                {"日期": "2024-06-10", "换手率": "abc"}
            ],
            fetch_northbound=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "Invalid turnover_rate value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )


if __name__ == "__main__":
    unittest.main()
