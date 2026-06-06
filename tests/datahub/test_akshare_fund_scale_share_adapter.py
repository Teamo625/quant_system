from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareETFFundFlowAdapter,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceRequest, fetch_source_result


def _sse_row(**overrides):
    row = {
        "基金代码": "510300",
        "统计日期": "2024-01-05",
        "基金份额": "1.25亿份",
    }
    row.update(overrides)
    return row


def _open_scale_row(**overrides):
    row = {
        "基金代码": "510300",
        "基金简称": "沪深300ETF",
        "总募集规模": 3296860.0,
        "最近总份额": 44828600000.0,
        "更新日期": "2024-01-06",
    }
    row.update(overrides)
    return row


class AkshareFundScaleShareAdapterTests(unittest.TestCase):
    def test_bounded_etf_history_request_does_not_call_snapshot_routes(self) -> None:
        open_calls: list[str] = []
        close_calls: list[str] = []
        adapter = AkshareETFFundFlowAdapter(
            fetch_sse_scale=lambda **kwargs: [_sse_row(source_ts="2024-01-05T18:00:00")],
            fetch_open_scale_snapshot=lambda **kwargs: open_calls.append(kwargs["symbol"]) or [],
            fetch_close_scale_snapshot=lambda: close_calls.append("close") or [],
        )
        request = SourceRequest(
            dataset=DatasetName.FUND_SCALE_SHARE_SNAPSHOT,
            source_name=AKSHARE_SOURCE_ID,
            start_date=date(2024, 1, 5),
            end_date=date(2024, 1, 5),
            symbols=("510300",),
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(adapter, request)

        self.assertEqual(open_calls, [])
        self.assertEqual(close_calls, [])
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["source_route"], "fund_etf_scale_sse")

    def test_fetch_source_result_normalizes_scale_share_records_from_history_and_fund_snapshot(
        self,
    ) -> None:
        registry = DatasetRegistry()
        now = datetime(2024, 1, 7, 9, 0, 0, tzinfo=timezone.utc)
        open_calls: list[str] = []

        def fake_open_scale_snapshot(*, symbol):
            open_calls.append(symbol)
            if symbol == "股票型基金":
                return [_open_scale_row()]
            if symbol == "混合型基金":
                return [
                    _open_scale_row(
                        基金代码="000001",
                        基金简称="华夏成长混合A",
                        总募集规模=323683.0,
                        最近总份额=2592340000.0,
                    )
                ]
            return []

        adapter = AkshareETFFundFlowAdapter(
            fetch_sse_scale=lambda **kwargs: [_sse_row(source_ts="2024-01-05T18:00:00")],
            fetch_open_scale_snapshot=fake_open_scale_snapshot,
            fetch_close_scale_snapshot=lambda: [],
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.FUND_SCALE_SHARE_SNAPSHOT,
            source_name=AKSHARE_SOURCE_ID,
            start_date=date(2024, 1, 5),
            end_date=date(2024, 1, 6),
            symbols=("510300", "000001.FUND_CN"),
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(adapter, request)

        self.assertEqual(
            open_calls,
            ["股票型基金", "混合型基金", "债券型基金", "货币型基金", "QDII基金"],
        )
        self.assertEqual(result.record_count, 3)
        self.assertEqual(
            [
                (
                    record["fund_code"],
                    record["observation_date"],
                    record["source_route"],
                    record["metric_code"],
                )
                for record in result.normalized_records
            ],
            [
                (
                    "000001.FUND_CN",
                    "2024-01-06",
                    "fund_scale_open_sina[混合型基金]",
                    "shares_outstanding",
                ),
                (
                    "000001.FUND_CN",
                    "2024-01-06",
                    "fund_scale_open_sina[混合型基金]",
                    "total_raised_scale",
                ),
                (
                    "510300.ETF_CN",
                    "2024-01-05",
                    "fund_etf_scale_sse",
                    "shares_outstanding",
                ),
            ],
        )
        exchange_record = next(
            record
            for record in result.normalized_records
            if record["source_route"] == "fund_etf_scale_sse"
        )
        self.assertEqual(exchange_record["metric_value"], 125000000.0)
        self.assertEqual(exchange_record["metric_unit"], "share")
        self.assertEqual(exchange_record["source_ts"], "2024-01-05T18:00:00")
        self.assertEqual(exchange_record["ingested_at"], now.isoformat())
        snapshot_record = next(
            record
            for record in result.normalized_records
            if record["fund_code"] == "000001.FUND_CN"
            and record["metric_code"] == "shares_outstanding"
        )
        self.assertEqual(snapshot_record["market"], "FUND_CN")
        self.assertEqual(snapshot_record["observation_type"], "snapshot_update_date")
        self.assertEqual(snapshot_record["metric_unit"], "share")
        self.assertEqual(snapshot_record["source_ts"], "2024-01-06T00:00:00")
        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.FUND_SCALE_SHARE_SNAPSHOT, record),
                (),
            )

    def test_adapter_allows_snapshot_route_redundancy_when_exchange_route_is_unavailable(
        self,
    ) -> None:
        def flaky_sse(**kwargs):
            raise OSError(111, "connection refused to sse.com.cn endpoint")

        def fake_open_scale_snapshot(*, symbol):
            if symbol == "股票型基金":
                return [_open_scale_row(更新日期="2024-01-06")]
            return []

        adapter = AkshareETFFundFlowAdapter(
            fetch_sse_scale=flaky_sse,
            fetch_open_scale_snapshot=fake_open_scale_snapshot,
            fetch_close_scale_snapshot=lambda: [],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_SCALE_SHARE_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 6),
                end_date=date(2024, 1, 6),
                symbols=("510300.ETF_CN",),
            ),
        )
        self.assertEqual(result.record_count, 2)
        self.assertTrue(
            all(record["source_route"] == "fund_scale_open_sina[股票型基金]" for record in result.normalized_records)
        )

    def test_adapter_rejects_partial_batch_success_for_scale_share(self) -> None:
        adapter = AkshareETFFundFlowAdapter(
            fetch_sse_scale=lambda **kwargs: [_sse_row()],
            fetch_open_scale_snapshot=lambda **kwargs: [],
            fetch_close_scale_snapshot=lambda: [],
        )
        with self.assertRaisesRegex(
            ValueError,
            "yielded no usable rows for requested symbol",
        ):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_SCALE_SHARE_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 5),
                    end_date=date(2024, 1, 5),
                    symbols=("510300.ETF_CN", "161725.FUND_CN"),
                ),
            )

    def test_adapter_skips_malformed_unrequested_snapshot_codes(self) -> None:
        adapter = AkshareETFFundFlowAdapter(
            fetch_open_scale_snapshot=lambda **kwargs: [
                _open_scale_row(基金代码="37001B"),
                _open_scale_row(基金代码="000001", 基金简称="华夏成长混合A"),
            ]
            if kwargs["symbol"] == "混合型基金"
            else [],
            fetch_close_scale_snapshot=lambda: [],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FUND_SCALE_SHARE_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 6),
                end_date=date(2024, 1, 6),
                symbols=("000001.FUND_CN",),
            ),
        )
        self.assertEqual(result.record_count, 2)
        self.assertTrue(
            all(record["fund_code"] == "000001.FUND_CN" for record in result.normalized_records)
        )

    def test_adapter_rejects_invalid_scale_share_symbol_inputs(self) -> None:
        adapter = AkshareETFFundFlowAdapter(
            fetch_sse_scale=lambda **kwargs: [],
            fetch_open_scale_snapshot=lambda **kwargs: [],
            fetch_close_scale_snapshot=lambda: [],
        )
        invalid_cases = (
            (("000001",), "Ambiguous bare 0-prefix fund code"),
            (("510300.FUND_CN",), "Exchange ETF code is unsupported"),
            (("161725.ETF_CN",), "Non-ETF fund code is unsupported"),
            (("399001",), "Index code is unsupported"),
            (("600000",), "A-share stock code is unsupported"),
        )
        for symbols, message in invalid_cases:
            with self.subTest(symbols=symbols):
                with self.assertRaisesRegex(ValueError, message):
                    fetch_source_result(
                        adapter,
                        SourceRequest(
                            dataset=DatasetName.FUND_SCALE_SHARE_SNAPSHOT,
                            source_name=AKSHARE_SOURCE_ID,
                            start_date=date(2024, 1, 5),
                            end_date=date(2024, 1, 6),
                            symbols=symbols,
                        ),
                    )

    def test_route_signature_incompatibility_is_not_scale_share_live_unavailable(
        self,
    ) -> None:
        def bad_open_scale_snapshot():
            return []

        adapter = AkshareETFFundFlowAdapter(
            fetch_open_scale_snapshot=bad_open_scale_snapshot,
            fetch_close_scale_snapshot=lambda: [],
        )
        with self.assertRaisesRegex(RuntimeError, "does not accept symbol argument") as context:
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_SCALE_SHARE_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 5),
                    end_date=date(2024, 1, 6),
                    symbols=("000001.FUND_CN",),
                ),
            )
        self.assertFalse(adapter._is_fund_flow_route_unavailable(context.exception))

    def test_adapter_rejects_conflicting_duplicate_scale_share_rows(self) -> None:
        adapter = AkshareETFFundFlowAdapter(
            fetch_open_scale_snapshot=lambda **kwargs: [
                _open_scale_row(基金代码="000001", 更新日期="2024-01-06", 最近总份额=10.0),
                _open_scale_row(基金代码="000001", 更新日期="2024-01-06", 最近总份额=11.0),
            ]
            if kwargs["symbol"] == "混合型基金"
            else [],
            fetch_close_scale_snapshot=lambda: [],
        )
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate ETF/fund scale/share row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.FUND_SCALE_SHARE_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 6),
                    end_date=date(2024, 1, 6),
                    symbols=("000001.FUND_CN",),
                ),
            )


if __name__ == "__main__":
    unittest.main()
