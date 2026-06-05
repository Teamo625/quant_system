from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareMinuteBarsAdapter,
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
    fetch_hist_min_em=None,
    fetch_minute=None,
    now_fn=None,
    minute_period="1",
) -> AkshareAShareMinuteBarsAdapter:
    return AkshareAShareMinuteBarsAdapter(
        fetch_hist_min_em=fetch_hist_min_em,
        fetch_minute=fetch_minute,
        now_fn=now_fn,
        minute_period=minute_period,
    )


class AkshareAShareMinuteBarsAdapterTests(unittest.TestCase):
    def test_unavailable_classifier_treats_none_subscriptable_route_shape_as_unavailable(
        self,
    ) -> None:
        adapter = _build_adapter(fetch_hist_min_em=lambda **kwargs: [])
        self.assertTrue(
            adapter._is_minute_bars_route_unavailable(  # pylint: disable=protected-access
                TypeError("'NoneType' object is not subscriptable")
            )
        )

    def test_unavailable_classifier_does_not_treat_route_signature_errors_as_unavailable(self) -> None:
        adapter = _build_adapter(fetch_hist_min_em=lambda **kwargs: [])
        self.assertFalse(
            adapter._is_minute_bars_route_unavailable(  # pylint: disable=protected-access
                RuntimeError(
                    "AKShare A-share minute-bars route does not accept required argument: "
                    "route=stock_zh_a_hist_min_em, field=start_date"
                )
            )
        )

    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = _build_adapter(fetch_hist_min_em=lambda **kwargs: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_validates_contract_sorts_and_deduplicates_offline_only(self) -> None:
        calls: list[dict[str, str]] = []
        now = datetime(2026, 6, 1, 8, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        def fake_fetch_hist_min_em(**kwargs):
            calls.append(dict(kwargs))
            return [
                {
                    "时间": "2026-05-29 09:31:00",
                    "开盘": "10.11",
                    "收盘": "10.22",
                    "最高": "10.23",
                    "最低": "10.10",
                    "成交量": "10,000",
                    "成交额": "101100",
                    "均价": "10.15",
                    "source_ts": "2026-05-29 09:31:30",
                },
                {
                    "时间": "2026-05-29 09:30:00",
                    "开盘": 10.0,
                    "收盘": 10.1,
                    "最高": 10.2,
                    "最低": 9.9,
                    "成交量": 5000,
                    "成交额": 50000,
                    "均价": 10.0,
                    "symbol": "600000",
                },
                {
                    "时间": "2026-05-29 09:31:00",
                    "开盘": "10.11",
                    "收盘": "10.22",
                    "最高": "10.23",
                    "最低": "10.10",
                    "成交量": "10,000",
                    "成交额": "101100",
                    "均价": "10.15",
                    "source_ts": "2026-05-29 09:32:00",
                },
            ]

        adapter = _build_adapter(fetch_hist_min_em=fake_fetch_hist_min_em, now_fn=lambda: now)

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

        self.assertEqual(
            calls,
            [
                {
                    "symbol": "600000",
                    "start_date": "2026-05-29 09:30:00",
                    "end_date": "2026-05-29 15:00:00",
                    "period": "1",
                    "adjust": "",
                }
            ],
        )

        self.assertEqual(result.record_count, 2)
        records = list(result.normalized_records)
        self.assertEqual(
            [record["bar_time"] for record in records],
            ["2026-05-29T09:30:00", "2026-05-29T09:31:00"],
        )
        for record in records:
            self.assertEqual(record["symbol"], "600000.SH")
            self.assertEqual(record["market"], "A_SHARE")
            self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
            self.assertEqual(record["ingested_at"], now.isoformat())
            self.assertEqual(record["schema_version"], "v1")
            self.assertEqual(
                registry.validate_record(DatasetName.MINUTE_BARS, record),
                (),
            )

        self.assertEqual(records[1]["source_ts"], "2026-05-29T09:32:00")

    def test_adapter_supports_dataframe_like_payload_and_fallback_route(self) -> None:
        primary_calls: list[dict[str, str]] = []
        fallback_calls: list[dict[str, str]] = []

        def fake_primary(**kwargs):
            primary_calls.append(dict(kwargs))
            raise RuntimeError("ProxyError: proxy down")

        def fake_fallback(**kwargs):
            fallback_calls.append(dict(kwargs))
            return _FakeDataFrame(
                [
                    {
                        "day": "2026-05-29 09:30:00",
                        "open": "10",
                        "high": "10.1",
                        "low": "9.9",
                        "close": "10.0",
                        "volume": "1000",
                        "amount": "10000",
                    },
                    {
                        "day": "2026-05-28 09:30:00",
                        "open": "9.8",
                        "high": "9.9",
                        "low": "9.7",
                        "close": "9.8",
                        "volume": "800",
                        "amount": "8000",
                    },
                ]
            )

        adapter = _build_adapter(
            fetch_hist_min_em=fake_primary,
            fetch_minute=fake_fallback,
            now_fn=lambda: datetime(2026, 6, 1, 8, 0, 0, tzinfo=timezone.utc),
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.MINUTE_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000001.SZ",),
                start_date=date(2026, 5, 29),
                end_date=date(2026, 5, 29),
            ),
        )

        self.assertEqual(len(primary_calls), 1)
        self.assertEqual(
            fallback_calls,
            [{"symbol": "sz000001", "period": "1", "adjust": ""}],
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "000001.SZ")

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = _build_adapter(fetch_hist_min_em=lambda **kwargs: [])

        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_adapter_requires_bounded_date_window(self) -> None:
        adapter = _build_adapter(fetch_hist_min_em=lambda **kwargs: [])

        with self.assertRaisesRegex(ValueError, "requires bounded date window"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "requires both start_date and end_date"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 29),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Invalid SourceRequest date range"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 30),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_adapter_rejects_old_one_minute_history_beyond_public_recent_window(self) -> None:
        calls: list[dict[str, str]] = []

        def fake_fetch_hist_min_em(**kwargs):
            calls.append(dict(kwargs))
            return []

        adapter = _build_adapter(
            fetch_hist_min_em=fake_fetch_hist_min_em,
            now_fn=lambda: datetime(2026, 6, 15, 8, 0, 0, tzinfo=timezone.utc),
        )

        with self.assertRaisesRegex(
            ValueError,
            "1-minute bars public history is limited to a recent trailing window",
        ):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 20),
                    end_date=date(2026, 5, 21),
                ),
            )

        self.assertEqual(calls, [])

    def test_adapter_requires_at_least_one_symbol(self) -> None:
        adapter = _build_adapter(fetch_hist_min_em=lambda **kwargs: [])

        with self.assertRaisesRegex(ValueError, "requires at least one symbol, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_adapter_validates_full_batch_before_fetch(self) -> None:
        calls: list[dict[str, str]] = []

        def fake_fetch_hist_min_em(**kwargs):
            calls.append(dict(kwargs))
            return []

        adapter = _build_adapter(fetch_hist_min_em=fake_fetch_hist_min_em)
        with self.assertRaisesRegex(ValueError, "ETF or fund symbol is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH", "510300.SH"),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )
        self.assertEqual(calls, [])

    def test_adapter_accepts_canonical_prefixed_and_bare_symbols(self) -> None:
        adapter = _build_adapter(
            fetch_hist_min_em=lambda **kwargs: [
                {
                    "时间": "2026-05-29 09:30:00",
                    "开盘": "1",
                    "收盘": "1",
                    "最高": "1",
                    "最低": "1",
                    "成交量": "1",
                }
            ]
        )

        accepted = {
            "600000.SH": "600000.SH",
            "SH600000": "600000.SH",
            "600000": "600000.SH",
            "000001.SZ": "000001.SZ",
            "SZ000001": "000001.SZ",
            "000001": "000001.SZ",
            "430047.BJ": "430047.BJ",
            "430047": "430047.BJ",
        }

        for raw_symbol, canonical in accepted.items():
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=(raw_symbol,),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )
            self.assertEqual(result.record_count, 1)
            self.assertEqual(result.normalized_records[0]["symbol"], canonical)

    def test_adapter_fetches_multi_symbol_bounded_window_and_deduplicates(self) -> None:
        calls: list[dict[str, str]] = []
        now = datetime(2026, 6, 1, 8, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        def fake_fetch_hist_min_em(**kwargs):
            calls.append(dict(kwargs))
            if kwargs["symbol"] == "600000":
                return [
                    {
                        "时间": "2026-05-29 09:31:00",
                        "开盘": "10.11",
                        "收盘": "10.22",
                        "最高": "10.23",
                        "最低": "10.10",
                        "成交量": "10,000",
                        "成交额": "101100",
                        "均价": "10.15",
                        "source_ts": "2026-05-29 09:31:30",
                    },
                    {
                        "时间": "2026-05-28 09:30:00",
                        "开盘": 10.0,
                        "收盘": 10.1,
                        "最高": 10.2,
                        "最低": 9.9,
                        "成交量": 5000,
                        "成交额": 50000,
                        "均价": 10.0,
                        "symbol": "600000",
                    },
                    {
                        "时间": "2026-05-29 09:31:00",
                        "开盘": "10.11",
                        "收盘": "10.22",
                        "最高": "10.23",
                        "最低": "10.10",
                        "成交量": "10,000",
                        "成交额": "101100",
                        "均价": "10.15",
                        "source_ts": "2026-05-29 09:32:00",
                    },
                    {
                        "时间": "2026-05-30 09:30:00",
                        "开盘": "11",
                        "收盘": "11",
                        "最高": "11",
                        "最低": "11",
                        "成交量": "1",
                    },
                ]
            return [
                {
                    "时间": "2026-05-29 09:30:00",
                    "开盘": "20",
                    "收盘": "20.1",
                    "最高": "20.2",
                    "最低": "19.9",
                    "成交量": "2000",
                    "成交额": "40000",
                    "symbol": "000001",
                }
            ]

        adapter = _build_adapter(fetch_hist_min_em=fake_fetch_hist_min_em, now_fn=lambda: now)
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.MINUTE_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH", "000001.SZ", "600000.SH"),
                start_date=date(2026, 5, 28),
                end_date=date(2026, 5, 29),
            ),
        )

        self.assertEqual(
            calls,
            [
                {
                    "symbol": "600000",
                    "start_date": "2026-05-28 09:30:00",
                    "end_date": "2026-05-29 15:00:00",
                    "period": "1",
                    "adjust": "",
                },
                {
                    "symbol": "000001",
                    "start_date": "2026-05-28 09:30:00",
                    "end_date": "2026-05-29 15:00:00",
                    "period": "1",
                    "adjust": "",
                },
            ],
        )
        self.assertEqual(result.record_count, 3)
        records = list(result.normalized_records)
        self.assertEqual(
            [(record["symbol"], record["bar_time"]) for record in records],
            [
                ("000001.SZ", "2026-05-29T09:30:00"),
                ("600000.SH", "2026-05-28T09:30:00"),
                ("600000.SH", "2026-05-29T09:31:00"),
            ],
        )
        self.assertEqual(records[-1]["source_ts"], "2026-05-29T09:32:00")
        for record in records:
            self.assertEqual(
                registry.validate_record(DatasetName.MINUTE_BARS, record),
                (),
            )
            self.assertEqual(record["ingested_at"], now.isoformat())
            self.assertEqual(record["schema_version"], "v1")

    def test_adapter_fallback_filters_bounded_window_for_multiple_symbols(self) -> None:
        primary_calls: list[dict[str, str]] = []
        fallback_calls: list[dict[str, str]] = []

        def fake_primary(**kwargs):
            primary_calls.append(dict(kwargs))
            raise RuntimeError("ProxyError: proxy down")

        def fake_fallback(**kwargs):
            fallback_calls.append(dict(kwargs))
            if kwargs["symbol"] == "sh600000":
                return _FakeDataFrame(
                    [
                        {
                            "day": "2026-05-27 09:30:00",
                            "open": "9.8",
                            "high": "9.9",
                            "low": "9.7",
                            "close": "9.8",
                            "volume": "800",
                            "amount": "8000",
                        },
                        {
                            "day": "2026-05-29 09:30:00",
                            "open": "10",
                            "high": "10.1",
                            "low": "9.9",
                            "close": "10.0",
                            "volume": "1000",
                            "amount": "10000",
                        },
                    ]
                )
            return _FakeDataFrame(
                [
                    {
                        "day": "2026-05-29 09:31:00",
                        "open": "20",
                        "high": "20.1",
                        "low": "19.9",
                        "close": "20.0",
                        "volume": "2000",
                        "amount": "20000",
                    },
                    {
                        "day": "2026-05-30 09:30:00",
                        "open": "21",
                        "high": "21.1",
                        "low": "20.9",
                        "close": "21.0",
                        "volume": "2100",
                        "amount": "21000",
                    },
                ]
            )

        adapter = _build_adapter(
            fetch_hist_min_em=fake_primary,
            fetch_minute=fake_fallback,
            now_fn=lambda: datetime(2026, 6, 1, 8, 0, 0, tzinfo=timezone.utc),
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.MINUTE_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH", "000001.SZ"),
                start_date=date(2026, 5, 28),
                end_date=date(2026, 5, 29),
            ),
        )

        self.assertEqual(len(primary_calls), 2)
        self.assertEqual(
            fallback_calls,
            [
                {"symbol": "sh600000", "period": "1", "adjust": ""},
                {"symbol": "sz000001", "period": "1", "adjust": ""},
            ],
        )
        self.assertEqual(
            [(record["symbol"], record["bar_time"]) for record in result.normalized_records],
            [
                ("000001.SZ", "2026-05-29T09:31:00"),
                ("600000.SH", "2026-05-29T09:30:00"),
            ],
        )

    def test_adapter_allows_older_bounded_history_for_non_one_minute_periods(self) -> None:
        calls: list[dict[str, str]] = []

        def fake_fetch_hist_min_em(**kwargs):
            calls.append(dict(kwargs))
            return [
                {
                    "时间": "2026-04-10 10:00:00",
                    "开盘": "10",
                    "收盘": "10.1",
                    "最高": "10.2",
                    "最低": "9.9",
                    "成交量": "1000",
                    "成交额": "10000",
                }
            ]

        adapter = _build_adapter(
            fetch_hist_min_em=fake_fetch_hist_min_em,
            now_fn=lambda: datetime(2026, 6, 15, 8, 0, 0, tzinfo=timezone.utc),
            minute_period="5",
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.MINUTE_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
                start_date=date(2026, 4, 1),
                end_date=date(2026, 4, 30),
            ),
        )

        self.assertEqual(result.record_count, 1)
        self.assertEqual(
            calls,
            [
                {
                    "symbol": "600000",
                    "start_date": "2026-04-01 09:30:00",
                    "end_date": "2026-04-30 15:00:00",
                    "period": "5",
                    "adjust": "",
                }
            ],
        )
        self.assertEqual(result.normalized_records[0]["bar_time"], "2026-04-10T10:00:00")

    def test_adapter_does_not_use_fallback_for_old_historical_window_when_primary_is_unavailable(self) -> None:
        primary_calls: list[dict[str, str]] = []
        fallback_calls: list[dict[str, str]] = []

        def fake_primary(**kwargs):
            primary_calls.append(dict(kwargs))
            raise RuntimeError("ProxyError: proxy down")

        def fake_fallback(**kwargs):
            fallback_calls.append(dict(kwargs))
            return []

        adapter = _build_adapter(
            fetch_hist_min_em=fake_primary,
            fetch_minute=fake_fallback,
            now_fn=lambda: datetime(2026, 6, 15, 8, 0, 0, tzinfo=timezone.utc),
            minute_period="5",
        )

        with self.assertRaisesRegex(
            RuntimeError,
            "fallback route only supports recent bounded windows",
        ):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 4, 1),
                    end_date=date(2026, 4, 30),
                ),
            )

        self.assertEqual(len(primary_calls), 1)
        self.assertEqual(fallback_calls, [])

    def test_adapter_rejects_invalid_hk_etf_index_and_malformed_symbols(self) -> None:
        adapter = _build_adapter(fetch_hist_min_em=lambda **kwargs: [])

        with self.assertRaisesRegex(ValueError, "Unsupported symbol market suffix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

        with self.assertRaisesRegex(ValueError, "ETF or fund symbol is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.SH",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Index symbol is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("399001.SZ",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

        with self.assertRaisesRegex(ValueError, "market-code combination"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000001.SH",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Unsupported symbol format"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("BAD_SYMBOL",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_adapter_rejects_invalid_timestamps_and_invalid_numeric_values(self) -> None:
        bad_timestamp_adapter = _build_adapter(
            fetch_hist_min_em=lambda **kwargs: [
                {
                    "时间": "2026-13-29 09:30:00",
                    "开盘": "1",
                    "收盘": "1",
                    "最高": "1",
                    "最低": "1",
                    "成交量": "1",
                }
            ]
        )

        with self.assertRaisesRegex(ValueError, "Invalid bar_time value"):
            fetch_source_result(
                bad_timestamp_adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

        bad_numeric_adapter = _build_adapter(
            fetch_hist_min_em=lambda **kwargs: [
                {
                    "时间": "2026-05-29 09:30:00",
                    "开盘": "bad",
                    "收盘": "1",
                    "最高": "1",
                    "最低": "1",
                    "成交量": "1",
                }
            ]
        )

        with self.assertRaisesRegex(ValueError, "Invalid open value"):
            fetch_source_result(
                bad_numeric_adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_adapter_rejects_malformed_payload_and_missing_fields(self) -> None:
        bad_shape_adapter = _build_adapter(fetch_hist_min_em=lambda **kwargs: {"bad": "shape"})

        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                bad_shape_adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

        bad_row_adapter = _build_adapter(fetch_hist_min_em=lambda **kwargs: ["bad-row"])
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                bad_row_adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

        missing_field_adapter = _build_adapter(
            fetch_hist_min_em=lambda **kwargs: [{"时间": "2026-05-29 09:30:00", "开盘": "1"}]
        )
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                missing_field_adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_adapter_rejects_conflicting_duplicate_rows(self) -> None:
        adapter = _build_adapter(
            fetch_hist_min_em=lambda **kwargs: [
                {
                    "时间": "2026-05-29 09:30:00",
                    "开盘": "10",
                    "收盘": "10",
                    "最高": "10",
                    "最低": "10",
                    "成交量": "1",
                },
                {
                    "时间": "2026-05-29 09:30:00",
                    "开盘": "10.1",
                    "收盘": "10",
                    "最高": "10",
                    "最低": "10",
                    "成交量": "1",
                },
            ]
        )

        with self.assertRaisesRegex(ValueError, "Conflicting duplicate A-share minute-bars row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_route_signature_compatibility_errors_are_hard_failures(self) -> None:
        def bad_route(*, symbol: str):
            del symbol
            return []

        adapter = _build_adapter(fetch_hist_min_em=bad_route)
        with self.assertRaisesRegex(
            RuntimeError,
            "does not accept required argument",
        ):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )


if __name__ == "__main__":
    unittest.main()
