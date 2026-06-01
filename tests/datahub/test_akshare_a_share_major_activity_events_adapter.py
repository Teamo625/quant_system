from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareMajorActivityEventsAdapter,
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
    fetch_major_activity=None,
    now_fn=None,
    route_symbol="A股",
) -> AkshareAShareMajorActivityEventsAdapter:
    return AkshareAShareMajorActivityEventsAdapter(
        fetch_major_activity=fetch_major_activity,
        now_fn=now_fn,
        route_symbol=route_symbol,
    )


class AkshareAShareMajorActivityEventsAdapterTests(unittest.TestCase):
    def test_unavailable_classifier_treats_none_subscriptable_route_shape_as_unavailable(
        self,
    ) -> None:
        adapter = _build_adapter(fetch_major_activity=lambda **kwargs: [])
        self.assertTrue(
            adapter._is_major_activity_route_unavailable(  # pylint: disable=protected-access
                TypeError("'NoneType' object is not subscriptable")
            )
        )

    def test_unavailable_classifier_does_not_treat_route_signature_errors_as_unavailable(self) -> None:
        adapter = _build_adapter(fetch_major_activity=lambda **kwargs: [])
        self.assertFalse(
            adapter._is_major_activity_route_unavailable(  # pylint: disable=protected-access
                RuntimeError(
                    "AKShare A-share major-activity route does not accept required argument: "
                    "route=stock_dzjy_mrmx, field=start_date"
                )
            )
        )

    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = _build_adapter(fetch_major_activity=lambda **kwargs: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_sorts_deduplicates_and_validates_offline_only(self) -> None:
        calls: list[dict[str, str]] = []
        now = datetime(2026, 6, 1, 8, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        def fake_fetch_major_activity(**kwargs):
            calls.append(dict(kwargs))
            return [
                {
                    "交易日期": "2026-05-25",
                    "证券代码": "000001",
                    "证券简称": "平安银行",
                    "成交价": "12.30",
                    "收盘价": "12.40",
                    "折溢率": "-0.81",
                    "成交量": "120万",
                    "成交额": "1476万",
                    "买方营业部": "机构专用A",
                    "卖方营业部": "机构专用B",
                    "source_ts": "2026-05-25 16:00:00",
                },
                {
                    "交易日期": "2026-05-25",
                    "证券代码": "000001",
                    "证券简称": "平安银行",
                    "成交价": "12.30",
                    "收盘价": "12.40",
                    "折溢率": "-0.81",
                    "成交量": "120万",
                    "成交额": "1476万",
                    "买方营业部": "机构专用A",
                    "卖方营业部": "机构专用B",
                    "source_ts": "2026-05-25 16:05:00",
                },
                {
                    "交易日期": date(2026, 5, 25),
                    "证券代码": "600000",
                    "证券简称": "浦发银行",
                    "成交价": 11.2,
                    "收盘价": "11.30",
                    "折溢率": "-0.88%",
                    "成交量": "300000",
                    "成交额": "3360000",
                    "卖方营业部": "机构专用C",
                },
                {
                    "交易日期": "2026-05-25",
                    "证券代码": "430047",
                    "证券简称": "诺思兰德",
                    "成交价": "8.00",
                    "收盘价": "8.10",
                    "折溢率": "-1.23",
                    "成交量": "10万",
                    "成交额": "80万",
                    "买方营业部": "机构专用D",
                    "卖方营业部": "机构专用E",
                },
            ]

        adapter = _build_adapter(fetch_major_activity=fake_fetch_major_activity, now_fn=lambda: now)

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000001.SZ", "600000.SH"),
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )

        self.assertEqual(
            calls,
            [{"symbol": "A股", "start_date": "20260525", "end_date": "20260525"}],
        )

        self.assertEqual(result.record_count, 2)
        records = list(result.normalized_records)
        self.assertEqual(
            [(r["event_date"], r["symbol"], r["event_type"], r["event_id"]) for r in records],
            sorted((r["event_date"], r["symbol"], r["event_type"], r["event_id"]) for r in records),
        )

        sz_record = next(r for r in records if r["symbol"] == "000001.SZ")
        sh_record = next(r for r in records if r["symbol"] == "600000.SH")

        self.assertEqual(sz_record["market"], "A_SHARE")
        self.assertEqual(sz_record["event_type"], "block_trade")
        self.assertEqual(sz_record["participant"], "机构专用A")
        self.assertEqual(sz_record["direction"], "buy")
        self.assertEqual(sz_record["event_value"], 14760000.0)
        self.assertEqual(sz_record["event_volume"], 1200000.0)
        self.assertEqual(sz_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(sz_record["ingested_at"], now.isoformat())
        self.assertEqual(sz_record["schema_version"], "v1")
        self.assertEqual(sz_record["source_ts"], "2026-05-25T16:05:00")
        self.assertIn("seller=机构专用B", sz_record["summary"])

        self.assertEqual(sh_record["direction"], "sell")
        self.assertEqual(sh_record["participant"], "机构专用C")

        for record in records:
            self.assertEqual(
                registry.validate_record(DatasetName.MAJOR_ACTIVITY_EVENTS, record),
                (),
            )

    def test_adapter_supports_dataframe_like_payload(self) -> None:
        adapter = _build_adapter(
            fetch_major_activity=lambda **kwargs: _FakeDataFrame(
                [
                    {
                        "交易日期": "2026-05-25",
                        "证券代码": "000001",
                        "成交量": "10000",
                        "成交额": "100000",
                    }
                ]
            ),
            now_fn=lambda: datetime(2026, 6, 1, 8, 0, 0, tzinfo=timezone.utc),
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000001.SZ",),
                start_date=date(2026, 5, 25),
                end_date=date(2026, 5, 25),
            ),
        )
        self.assertEqual(result.record_count, 1)

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = _build_adapter(fetch_major_activity=lambda **kwargs: [])

        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )

    def test_adapter_requires_one_bounded_trade_date(self) -> None:
        adapter = _build_adapter(fetch_major_activity=lambda **kwargs: [])

        with self.assertRaisesRegex(ValueError, "requires bounded trade_date"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

        with self.assertRaisesRegex(ValueError, "requires both start_date and end_date"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 25),
                ),
            )

        with self.assertRaisesRegex(ValueError, "supports exactly one trade_date"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 24),
                    end_date=date(2026, 5, 25),
                ),
            )

    def test_adapter_accepts_canonical_prefixed_and_bare_symbols(self) -> None:
        adapter = _build_adapter(
            fetch_major_activity=lambda **kwargs: [
                {"交易日期": "2026-05-25", "证券代码": "600000", "成交量": "1", "成交额": "2"},
                {"交易日期": "2026-05-25", "证券代码": "000001", "成交量": "1", "成交额": "2"},
                {"交易日期": "2026-05-25", "证券代码": "430047", "成交量": "1", "成交额": "2"},
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
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=(raw_symbol,),
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )
            self.assertEqual(result.record_count, 1)
            self.assertEqual(result.normalized_records[0]["symbol"], canonical)

    def test_adapter_rejects_invalid_hk_etf_index_and_malformed_symbols(self) -> None:
        adapter = _build_adapter(fetch_major_activity=lambda **kwargs: [])

        with self.assertRaisesRegex(ValueError, "Unsupported symbol market suffix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )

        with self.assertRaisesRegex(ValueError, "ETF or fund symbol is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.SH",),
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Index symbol is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("399001.SZ",),
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )

        with self.assertRaisesRegex(ValueError, "market-code combination"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000001.SH",),
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Unsupported symbol format"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("BAD_SYMBOL",),
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )

    def test_adapter_rejects_invalid_event_date(self) -> None:
        adapter = _build_adapter(
            fetch_major_activity=lambda **kwargs: [
                {"交易日期": "2026-13-01", "证券代码": "600000", "成交量": "1", "成交额": "2"}
            ]
        )

        with self.assertRaisesRegex(ValueError, "Invalid event_date value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )

    def test_adapter_rejects_invalid_numeric_values(self) -> None:
        bad_value_adapter = _build_adapter(
            fetch_major_activity=lambda **kwargs: [
                {"交易日期": "2026-05-25", "证券代码": "600000", "成交量": "abc", "成交额": "2"}
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid event_volume value"):
            fetch_source_result(
                bad_value_adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )

        negative_value_adapter = _build_adapter(
            fetch_major_activity=lambda **kwargs: [
                {"交易日期": "2026-05-25", "证券代码": "600000", "成交量": "1", "成交额": "-2"}
            ]
        )
        with self.assertRaisesRegex(ValueError, "Expected non-negative"):
            fetch_source_result(
                negative_value_adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )

    def test_route_signature_compatibility_errors_are_hard_failures(self) -> None:
        def incompatible_fetch(*, start_date: str, end_date: str):
            return []

        adapter = _build_adapter(fetch_major_activity=incompatible_fetch)

        with self.assertRaisesRegex(RuntimeError, "does not accept required argument"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape_and_non_mapping_rows(self) -> None:
        bad_shape_adapter = _build_adapter(fetch_major_activity=lambda **kwargs: {"bad": "shape"})
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                bad_shape_adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )

        bad_row_adapter = _build_adapter(fetch_major_activity=lambda **kwargs: ["bad-row"])
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                bad_row_adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )

    def test_adapter_rejects_missing_required_source_fields(self) -> None:
        adapter = _build_adapter(fetch_major_activity=lambda **kwargs: [{"交易日期": "2026-05-25"}])
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )

    def test_adapter_rejects_conflicting_duplicate_rows(self) -> None:
        adapter = _build_adapter(
            fetch_major_activity=lambda **kwargs: [
                {
                    "交易日期": "2026-05-25",
                    "证券代码": "600000",
                    "证券简称": "浦发银行A",
                    "成交量": "1000",
                    "成交额": "2000",
                    "买方营业部": "机构专用A",
                },
                {
                    "交易日期": "2026-05-25",
                    "证券代码": "600000",
                    "证券简称": "浦发银行B",
                    "成交量": "1000",
                    "成交额": "2000",
                    "买方营业部": "机构专用A",
                },
            ]
        )

        with self.assertRaisesRegex(ValueError, "Conflicting duplicate A-share major-activity row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )


if __name__ == "__main__":
    unittest.main()
