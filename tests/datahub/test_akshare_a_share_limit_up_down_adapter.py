from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareLimitUpDownAdapter,
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
    fetch_limit_up_pool=None,
    fetch_limit_down_pool=None,
    now_fn=None,
) -> AkshareAShareLimitUpDownAdapter:
    return AkshareAShareLimitUpDownAdapter(
        fetch_limit_up_pool=fetch_limit_up_pool,
        fetch_limit_down_pool=fetch_limit_down_pool,
        now_fn=now_fn,
    )


class AkshareAShareLimitUpDownAdapterTests(unittest.TestCase):
    def test_unavailable_classifier_does_not_treat_route_signature_errors_as_unavailable(self) -> None:
        adapter = _build_adapter(
            fetch_limit_up_pool=lambda **kwargs: [],
            fetch_limit_down_pool=lambda **kwargs: [],
        )
        self.assertFalse(
            adapter._is_limit_up_down_route_unavailable(  # pylint: disable=protected-access
                RuntimeError(
                    "AKShare A-share limit-up/down route does not accept required argument: "
                    "route=stock_zt_pool_em, field=date"
                )
            )
        )

    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = _build_adapter(
            fetch_limit_up_pool=lambda **kwargs: [],
            fetch_limit_down_pool=lambda **kwargs: [],
        )
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_records_offline_only(self) -> None:
        up_calls: list[dict[str, str]] = []
        down_calls: list[dict[str, str]] = []
        now = datetime(2026, 6, 1, 8, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        def fake_fetch_limit_up_pool(*, date: str):
            up_calls.append({"date": date})
            return [
                {
                    "代码": "600000",
                    "最新价": "11.00",
                    "涨跌幅": "10.00",
                    "连板数": "2",
                    "首次封板时间": "093000",
                    "最后封板时间": "145700",
                    "封板资金": "1.2亿",
                    "所属行业": "银行",
                    "source_ts": "2026-05-29 15:30:00",
                },
                {
                    "代码": "600000",
                    "最新价": "11.00",
                    "涨跌幅": "10.00",
                    "连板数": "2",
                    "首次封板时间": "093000",
                    "最后封板时间": "145700",
                    "封板资金": "1.2亿",
                    "所属行业": "银行",
                    "source_ts": "2026-05-29 15:31:00",
                },
                {
                    "代码": "000001",
                    "最新价": "12.00",
                    "涨跌幅": "10.00",
                },
            ]

        def fake_fetch_limit_down_pool(*, date: str):
            down_calls.append({"date": date})
            return [
                {
                    "代码": "600000",
                    "最新价": "9.00",
                    "涨跌幅": "-10.00",
                    "连续跌停": "3",
                    "最后封板时间": "145000",
                    "封单资金": "2500万",
                    "所属行业": "银行",
                    "source_ts": "2026-05-29T15:32:00",
                }
            ]

        adapter = _build_adapter(
            fetch_limit_up_pool=fake_fetch_limit_up_pool,
            fetch_limit_down_pool=fake_fetch_limit_down_pool,
            now_fn=lambda: now,
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.LIMIT_UP_DOWN_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

        self.assertEqual(up_calls, [{"date": "20260529"}])
        self.assertEqual(down_calls, [{"date": "20260529"}])
        self.assertEqual(result.record_count, 2)

        records = list(result.normalized_records)
        self.assertEqual(
            [(r["trade_date"], r["symbol"], r["limit_type"]) for r in records],
            sorted((r["trade_date"], r["symbol"], r["limit_type"]) for r in records),
        )

        limit_down = next(r for r in records if r["limit_type"] == "limit_down")
        limit_up = next(r for r in records if r["limit_type"] == "limit_up")

        self.assertEqual(limit_up["symbol"], "600000.SH")
        self.assertEqual(limit_up["market"], "A_SHARE")
        self.assertEqual(limit_up["hit_limit_up"], True)
        self.assertEqual(limit_up["hit_limit_down"], False)
        self.assertEqual(limit_up["event_category"], "limit_up_pool")
        self.assertEqual(limit_up["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(limit_up["ingested_at"], now.isoformat())
        self.assertEqual(limit_up["schema_version"], "v1")
        self.assertEqual(limit_up["source_ts"], "2026-05-29T15:31:00")
        self.assertEqual(limit_up["consecutive_limit_count"], 2.0)

        self.assertEqual(limit_down["symbol"], "600000.SH")
        self.assertEqual(limit_down["hit_limit_up"], False)
        self.assertEqual(limit_down["hit_limit_down"], True)
        self.assertEqual(limit_down["event_category"], "limit_down_pool")
        self.assertEqual(limit_down["consecutive_limit_count"], 3.0)

        for record in records:
            self.assertGreater(record["up_limit_price"], 0)
            self.assertGreater(record["down_limit_price"], 0)
            self.assertEqual(
                registry.validate_record(DatasetName.LIMIT_UP_DOWN_EVENTS, record),
                (),
            )

    def test_adapter_supports_dataframe_like_and_list_payloads(self) -> None:
        adapter = _build_adapter(
            fetch_limit_up_pool=lambda **kwargs: _FakeDataFrame(
                [
                    {
                        "代码": "000001",
                        "最新价": "12",
                        "涨跌幅": "10",
                    }
                ]
            ),
            fetch_limit_down_pool=lambda **kwargs: [
                {
                    "代码": "000001",
                    "最新价": "9.8",
                    "涨跌幅": "-10",
                }
            ],
            now_fn=lambda: datetime(2026, 6, 1, 8, 0, 0, tzinfo=timezone.utc),
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.LIMIT_UP_DOWN_EVENTS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000001.SZ",),
                start_date=date(2026, 5, 29),
                end_date=date(2026, 5, 29),
            ),
        )
        self.assertEqual(result.record_count, 2)

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = _build_adapter(
            fetch_limit_up_pool=lambda **kwargs: [],
            fetch_limit_down_pool=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_adapter_requires_one_bounded_trade_date(self) -> None:
        adapter = _build_adapter(
            fetch_limit_up_pool=lambda **kwargs: [],
            fetch_limit_down_pool=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "requires bounded trade_date"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.LIMIT_UP_DOWN_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

        with self.assertRaisesRegex(ValueError, "requires both start_date and end_date"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.LIMIT_UP_DOWN_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 29),
                ),
            )

        with self.assertRaisesRegex(ValueError, "supports exactly one trade_date"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.LIMIT_UP_DOWN_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 28),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_adapter_accepts_canonical_prefixed_and_bare_symbols(self) -> None:
        adapter = _build_adapter(
            fetch_limit_up_pool=lambda **kwargs: [
                {"代码": "600000", "最新价": "11", "涨跌幅": "10"},
                {"代码": "000001", "最新价": "10", "涨跌幅": "10"},
                {"代码": "430047", "最新价": "8", "涨跌幅": "30"},
            ],
            fetch_limit_down_pool=lambda **kwargs: [],
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
                    dataset=DatasetName.LIMIT_UP_DOWN_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=(raw_symbol,),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )
            self.assertEqual(result.record_count, 1)
            self.assertEqual(result.normalized_records[0]["symbol"], canonical)

    def test_adapter_rejects_invalid_hk_etf_index_and_malformed_symbols(self) -> None:
        adapter = _build_adapter(
            fetch_limit_up_pool=lambda **kwargs: [],
            fetch_limit_down_pool=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "Unsupported symbol market suffix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.LIMIT_UP_DOWN_EVENTS,
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
                    dataset=DatasetName.LIMIT_UP_DOWN_EVENTS,
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
                    dataset=DatasetName.LIMIT_UP_DOWN_EVENTS,
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
                    dataset=DatasetName.LIMIT_UP_DOWN_EVENTS,
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
                    dataset=DatasetName.LIMIT_UP_DOWN_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("BAD_SYMBOL",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_adapter_rejects_invalid_numeric_values(self) -> None:
        adapter = _build_adapter(
            fetch_limit_up_pool=lambda **kwargs: [
                {
                    "代码": "600000",
                    "最新价": "bad-number",
                    "涨跌幅": "10",
                }
            ],
            fetch_limit_down_pool=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "Invalid latest_price value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.LIMIT_UP_DOWN_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape_and_non_mapping_rows(self) -> None:
        bad_shape_adapter = _build_adapter(
            fetch_limit_up_pool=lambda **kwargs: {"bad": "shape"},
            fetch_limit_down_pool=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                bad_shape_adapter,
                SourceRequest(
                    dataset=DatasetName.LIMIT_UP_DOWN_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

        bad_row_adapter = _build_adapter(
            fetch_limit_up_pool=lambda **kwargs: ["bad-row"],
            fetch_limit_down_pool=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                bad_row_adapter,
                SourceRequest(
                    dataset=DatasetName.LIMIT_UP_DOWN_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_adapter_rejects_missing_required_source_fields(self) -> None:
        adapter = _build_adapter(
            fetch_limit_up_pool=lambda **kwargs: [{"代码": "600000", "最新价": "11"}],
            fetch_limit_down_pool=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.LIMIT_UP_DOWN_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_route_signature_compatibility_errors_are_hard_failures(self) -> None:
        def incompatible_fetch(*, trade_day: str):
            return []

        adapter = _build_adapter(
            fetch_limit_up_pool=incompatible_fetch,
            fetch_limit_down_pool=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(RuntimeError, "does not accept required argument"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.LIMIT_UP_DOWN_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_adapter_rejects_conflicting_duplicate_rows(self) -> None:
        adapter = _build_adapter(
            fetch_limit_up_pool=lambda **kwargs: [
                {"代码": "600000", "最新价": "11", "涨跌幅": "10", "连板数": "1"},
                {"代码": "600000", "最新价": "11", "涨跌幅": "10", "连板数": "2"},
            ],
            fetch_limit_down_pool=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "Conflicting duplicate A-share limit-up/down row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.LIMIT_UP_DOWN_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )


if __name__ == "__main__":
    unittest.main()
