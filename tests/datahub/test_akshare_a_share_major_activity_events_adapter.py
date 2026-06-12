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
    fetch_major_activity_summary=None,
    fetch_insider_change_sse=None,
    fetch_insider_change_szse=None,
    fetch_insider_change_bse=None,
    now_fn=None,
    route_symbol="A股",
) -> AkshareAShareMajorActivityEventsAdapter:
    if fetch_major_activity is None:
        fetch_major_activity = lambda **kwargs: []
    if fetch_major_activity_summary is None:
        fetch_major_activity_summary = lambda **kwargs: []
    if fetch_insider_change_sse is None:
        fetch_insider_change_sse = lambda **kwargs: []
    if fetch_insider_change_szse is None:
        fetch_insider_change_szse = lambda **kwargs: []
    if fetch_insider_change_bse is None:
        fetch_insider_change_bse = lambda **kwargs: []
    return AkshareAShareMajorActivityEventsAdapter(
        fetch_major_activity=fetch_major_activity,
        fetch_major_activity_summary=fetch_major_activity_summary,
        fetch_insider_change_sse=fetch_insider_change_sse,
        fetch_insider_change_szse=fetch_insider_change_szse,
        fetch_insider_change_bse=fetch_insider_change_bse,
        now_fn=now_fn,
        route_symbol=route_symbol,
    )


class AkshareAShareMajorActivityEventsAdapterTests(unittest.TestCase):
    def test_unavailable_classifier_treats_none_subscriptable_route_shape_as_unavailable(
        self,
    ) -> None:
        adapter = _build_adapter()
        self.assertTrue(
            adapter._is_major_activity_route_unavailable(  # pylint: disable=protected-access
                TypeError("'NoneType' object is not subscriptable")
            )
        )

    def test_unavailable_classifier_does_not_treat_route_signature_errors_as_unavailable(self) -> None:
        adapter = _build_adapter()
        self.assertFalse(
            adapter._is_major_activity_route_unavailable(  # pylint: disable=protected-access
                RuntimeError(
                    "AKShare A-share major-activity route does not accept required argument: "
                    "route=stock_dzjy_mrtj, field=start_date"
                )
            )
        )

    def test_adapter_is_source_protocol_compatible(self) -> None:
        self.assertIsInstance(_build_adapter(), SourceAdapter)

    def test_fetch_source_result_normalizes_block_trade_and_insider_routes_offline_only(
        self,
    ) -> None:
        detail_calls: list[dict[str, str]] = []
        summary_calls: list[dict[str, str]] = []
        insider_sse_calls: list[dict[str, str]] = []
        insider_szse_calls: list[dict[str, str]] = []
        insider_bse_calls: list[dict[str, str]] = []
        now = datetime(2026, 6, 1, 8, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        def fake_fetch_major_activity(**kwargs):
            detail_calls.append(dict(kwargs))
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

        def fake_fetch_major_activity_summary(**kwargs):
            summary_calls.append(dict(kwargs))
            return [
                {
                    "交易日期": "2026-05-25",
                    "证券代码": "600000",
                    "证券简称": "浦发银行",
                    "成交价": "11.20",
                    "收盘价": "11.30",
                    "折溢率": "-0.88%",
                    "成交笔数": "2",
                    "成交总量": "30",
                    "成交总额": "336",
                    "成交总额/流通市值": "0.66",
                    "source_ts": "2026-05-25 16:30:00",
                },
                {
                    "交易日期": "2026-05-25",
                    "证券代码": "430047",
                    "证券简称": "诺思兰德",
                    "成交价": "8.00",
                    "收盘价": "8.10",
                    "折溢率": "-1.23",
                    "成交笔数": "1",
                    "成交总量": "10",
                    "成交总额": "80",
                },
            ]

        def fake_fetch_insider_sse(**kwargs):
            insider_sse_calls.append(dict(kwargs))
            return [
                {
                    "公司代码": "600000",
                    "公司名称": "浦发银行",
                    "姓名": "谢伟",
                    "职务": "高级管理人员",
                    "本次变动前持股数": "158000",
                    "变动数": "-59000",
                    "本次变动平均价格": "9.93",
                    "变动后持股数": "99000",
                    "变动原因": "二级市场卖出",
                    "变动日期": "2026-05-25",
                    "填报日期": "2026-05-26",
                }
            ]

        def fake_fetch_insider_szse(**kwargs):
            insider_szse_calls.append(dict(kwargs))
            return [
                {
                    "证券代码": "000001",
                    "证券简称": "平安银行",
                    "董监高姓名": "张三",
                    "变动日期": "2026-05-25",
                    "变动股份数量": "1.5万",
                    "成交均价": "12.00",
                    "变动原因": "竞价交易",
                    "变动比例": "0.10",
                    "当日结存股数": "35,000",
                    "股份变动人姓名": "张三",
                    "职务": "董事",
                    "变动人与董监高的关系": "本人",
                }
            ]

        def fake_fetch_insider_bse(**kwargs):
            insider_bse_calls.append(dict(kwargs))
            return [
                {
                    "代码": "430047",
                    "简称": "诺思兰德",
                    "姓名": "李四",
                    "职务": "董事",
                    "变动日期": "2026-05-25",
                    "变动股数": "2万",
                    "变动前持股数": "10万",
                    "变动后持股数": "12万",
                    "变动均价": "8.00",
                    "变动原因": "竞价交易",
                }
            ]

        adapter = _build_adapter(
            fetch_major_activity=fake_fetch_major_activity,
            fetch_major_activity_summary=fake_fetch_major_activity_summary,
            fetch_insider_change_sse=fake_fetch_insider_sse,
            fetch_insider_change_szse=fake_fetch_insider_szse,
            fetch_insider_change_bse=fake_fetch_insider_bse,
            now_fn=lambda: now,
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000001.SZ", "600000.SH", "430047.BJ"),
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )

        self.assertEqual(
            detail_calls,
            [{"symbol": "A股", "start_date": "20260525", "end_date": "20260525"}],
        )
        self.assertEqual(
            summary_calls,
            [{"start_date": "20260525", "end_date": "20260525"}],
        )
        self.assertEqual(insider_sse_calls, [{"symbol": "600000"}])
        self.assertEqual(insider_szse_calls, [{"symbol": "000001"}])
        self.assertEqual(insider_bse_calls, [{"symbol": "430047"}])

        self.assertEqual(result.record_count, 8)
        records = list(result.normalized_records)
        self.assertEqual(
            [
                (
                    record["event_date"],
                    record["symbol"],
                    record["event_type"],
                    record["source_route"],
                    record["event_id"],
                )
                for record in records
            ],
            sorted(
                (
                    record["event_date"],
                    record["symbol"],
                    record["event_type"],
                    record["source_route"],
                    record["event_id"],
                )
                for record in records
            ),
        )

        detail_buy_record = next(
            record
            for record in records
            if record["symbol"] == "000001.SZ"
            and record["event_type"] == "block_trade"
        )
        detail_sell_record = next(
            record
            for record in records
            if record["symbol"] == "600000.SH"
            and record["event_type"] == "block_trade"
        )
        summary_record = next(
            record
            for record in records
            if record["symbol"] == "600000.SH"
            and record["event_type"] == "block_trade_summary"
        )
        insider_buy_record = next(
            record
            for record in records
            if record["symbol"] == "000001.SZ"
            and record["event_type"] == "insider_holding_change"
        )
        insider_sell_record = next(
            record
            for record in records
            if record["symbol"] == "600000.SH"
            and record["event_type"] == "insider_holding_change"
        )
        insider_bj_record = next(
            record
            for record in records
            if record["symbol"] == "430047.BJ"
            and record["event_type"] == "insider_holding_change"
        )

        self.assertEqual(detail_buy_record["market"], "A_SHARE")
        self.assertEqual(detail_buy_record["source_route"], "stock_dzjy_mrmx")
        self.assertEqual(detail_buy_record["participant"], "机构专用A")
        self.assertEqual(detail_buy_record["direction"], "buy")
        self.assertEqual(detail_buy_record["event_value"], 14760000.0)
        self.assertEqual(detail_buy_record["event_volume"], 1200000.0)
        self.assertEqual(detail_buy_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(detail_buy_record["ingested_at"], now.isoformat())
        self.assertEqual(detail_buy_record["schema_version"], "v1")
        self.assertEqual(detail_buy_record["source_ts"], "2026-05-25T16:05:00")
        self.assertIn("seller=机构专用B", detail_buy_record["summary"])

        self.assertEqual(detail_sell_record["direction"], "sell")
        self.assertEqual(detail_sell_record["participant"], "机构专用C")
        self.assertEqual(detail_sell_record["source_route"], "stock_dzjy_mrmx")

        self.assertEqual(summary_record["source_route"], "stock_dzjy_mrtj")
        self.assertEqual(summary_record["event_value"], 3360000.0)
        self.assertEqual(summary_record["event_volume"], 300000.0)
        self.assertEqual(summary_record["source_ts"], "2026-05-25T16:30:00")
        self.assertIn("aggregation=symbol_daily_summary", summary_record["summary"])
        self.assertIn("trade_count=2", summary_record["summary"])
        self.assertIn("turnover_ratio=0.66", summary_record["summary"])

        self.assertEqual(insider_buy_record["source_route"], "stock_share_hold_change_szse")
        self.assertEqual(insider_buy_record["direction"], "buy")
        self.assertEqual(insider_buy_record["participant"], "张三")
        self.assertEqual(insider_buy_record["event_volume"], 15000.0)
        self.assertEqual(insider_buy_record["event_value"], 180000.0)
        self.assertIn("reason=竞价交易", insider_buy_record["summary"])
        self.assertIn("after_hold=35000.0", insider_buy_record["summary"])

        self.assertEqual(insider_sell_record["source_route"], "stock_share_hold_change_sse")
        self.assertEqual(insider_sell_record["direction"], "sell")
        self.assertEqual(insider_sell_record["participant"], "谢伟")
        self.assertEqual(insider_sell_record["event_volume"], 59000.0)
        self.assertEqual(insider_sell_record["event_value"], 585870.0)
        self.assertEqual(insider_sell_record["source_ts"], "2026-05-26T00:00:00")

        self.assertEqual(insider_bj_record["source_route"], "stock_share_hold_change_bse")
        self.assertEqual(insider_bj_record["direction"], "buy")
        self.assertEqual(insider_bj_record["participant"], "李四")
        self.assertEqual(insider_bj_record["event_value"], 160000.0)
        self.assertNotIn("source_ts", insider_bj_record)

        for record in records:
            self.assertEqual(
                registry.validate_record(DatasetName.MAJOR_ACTIVITY_EVENTS, record),
                (),
            )

    def test_adapter_supports_dataframe_like_payload_for_detail_and_summary_routes(self) -> None:
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
            fetch_major_activity_summary=lambda **kwargs: _FakeDataFrame([]),
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
        adapter = _build_adapter()

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

    def test_adapter_requires_bounded_date_window_and_allows_multi_day_requests(self) -> None:
        detail_calls: list[dict[str, str]] = []
        summary_calls: list[dict[str, str]] = []

        adapter = _build_adapter(
            fetch_major_activity=lambda **kwargs: detail_calls.append(dict(kwargs)) or [],
            fetch_major_activity_summary=lambda **kwargs: summary_calls.append(dict(kwargs)) or [],
        )

        with self.assertRaisesRegex(ValueError, "requires bounded date window"):
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

        with self.assertRaisesRegex(ValueError, "Invalid SourceRequest date range"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 26),
                    end_date=date(2026, 5, 25),
                ),
            )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2026, 5, 24),
                end_date=date(2026, 5, 25),
            ),
        )
        self.assertEqual(result.record_count, 0)
        self.assertEqual(
            detail_calls,
            [{"symbol": "A股", "start_date": "20260524", "end_date": "20260525"}],
        )
        self.assertEqual(
            summary_calls,
            [{"start_date": "20260524", "end_date": "20260525"}],
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
        adapter = _build_adapter()

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

    def test_adapter_rejects_invalid_numeric_values_from_detail_and_summary_routes(self) -> None:
        bad_detail_adapter = _build_adapter(
            fetch_major_activity=lambda **kwargs: [
                {"交易日期": "2026-05-25", "证券代码": "600000", "成交量": "abc", "成交额": "2"}
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid event_volume value"):
            fetch_source_result(
                bad_detail_adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )

        negative_summary_adapter = _build_adapter(
            fetch_major_activity_summary=lambda **kwargs: [
                {
                    "交易日期": "2026-05-25",
                    "证券代码": "600000",
                    "成交笔数": "2",
                    "成交总量": "30",
                    "成交总额": "-336",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Expected non-negative"):
            fetch_source_result(
                negative_summary_adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )

        non_integer_count_adapter = _build_adapter(
            fetch_major_activity_summary=lambda **kwargs: [
                {
                    "交易日期": "2026-05-25",
                    "证券代码": "600000",
                    "成交笔数": "2.5",
                    "成交总量": "30",
                    "成交总额": "336",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Expected integer-like"):
            fetch_source_result(
                non_integer_count_adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )

    def test_route_signature_compatibility_errors_are_hard_failures_for_detail_and_summary(self) -> None:
        def incompatible_detail_fetch(*, start_date: str, end_date: str):
            return []

        def incompatible_summary_fetch(*, symbol: str):
            return []

        detail_adapter = _build_adapter(fetch_major_activity=incompatible_detail_fetch)
        with self.assertRaisesRegex(RuntimeError, "route=stock_dzjy_mrmx"):
            fetch_source_result(
                detail_adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )

        summary_adapter = _build_adapter(fetch_major_activity_summary=incompatible_summary_fetch)
        with self.assertRaisesRegex(RuntimeError, "route=stock_dzjy_mrtj"):
            fetch_source_result(
                summary_adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape_and_non_mapping_rows_for_both_routes(self) -> None:
        bad_detail_shape_adapter = _build_adapter(
            fetch_major_activity=lambda **kwargs: {"bad": "shape"}
        )
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                bad_detail_shape_adapter,
                SourceRequest(
                    dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 25),
                    end_date=date(2026, 5, 25),
                ),
            )

        bad_summary_row_adapter = _build_adapter(
            fetch_major_activity_summary=lambda **kwargs: ["bad-row"]
        )
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                bad_summary_row_adapter,
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
