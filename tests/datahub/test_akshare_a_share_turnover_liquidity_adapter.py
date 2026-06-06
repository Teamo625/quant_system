from datetime import date, datetime, timezone
import socket
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


def _build_adapter(*, fetch_turnover_hist=None, now_fn=None):
    return AkshareAShareCapitalFlowSnapshotAdapter(
        fetch_turnover_hist=fetch_turnover_hist,
        now_fn=now_fn,
    )


class AkshareAShareTurnoverLiquidityAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = _build_adapter(fetch_turnover_hist=lambda **kwargs: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_turnover_liquidity(self) -> None:
        calls: list[dict[str, str]] = []
        registry = DatasetRegistry()
        now = datetime(2024, 6, 12, 16, 0, 0, tzinfo=timezone.utc)

        def fake_fetch_turnover_hist(
            *,
            symbol: str,
            period: str,
            start_date: str,
            end_date: str,
            adjust: str,
        ):
            calls.append(
                {
                    "symbol": symbol,
                    "period": period,
                    "start_date": start_date,
                    "end_date": end_date,
                    "adjust": adjust,
                }
            )
            if symbol == "600000":
                return _FakeDataFrame(
                    [
                        {
                            "日期": "2024-06-10",
                            "成交量": 125000000,
                            "成交额": 1380000000,
                            "换手率": 2.16,
                        }
                    ]
                )
            if symbol == "000001":
                return [
                    {
                        "日期": "2024-06-10",
                        "成交量": "98000000",
                        "成交额": "1120000000",
                        "换手率": "1.82",
                    },
                    {
                        "日期": "2024-06-10",
                        "成交量": "98000000",
                        "成交额": "1120000000",
                        "换手率": "1.82",
                    },
                ]
            raise AssertionError(f"Unexpected turnover request: {symbol!r}")

        adapter = _build_adapter(fetch_turnover_hist=fake_fetch_turnover_hist, now_fn=lambda: now)
        request = SourceRequest(
            dataset=DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("600000.SH", "000001", "600000"),
            start_date=date(2024, 6, 10),
            end_date=date(2024, 6, 10),
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(adapter, request)

        self.assertEqual(
            calls,
            [
                {
                    "symbol": "600000",
                    "period": "daily",
                    "start_date": "20240610",
                    "end_date": "20240610",
                    "adjust": "",
                },
                {
                    "symbol": "000001",
                    "period": "daily",
                    "start_date": "20240610",
                    "end_date": "20240610",
                    "adjust": "",
                },
            ],
        )
        self.assertEqual(
            [(record["symbol"], record["trade_date"]) for record in result.normalized_records],
            [
                ("000001.SZ", "2024-06-10"),
                ("600000.SH", "2024-06-10"),
            ],
        )

        for record in result.normalized_records:
            self.assertEqual(record["market"], "CN")
            self.assertEqual(record["metric_granularity"], "daily")
            self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
            self.assertEqual(record["source_route"], "stock_zh_a_hist")
            self.assertEqual(record["schema_version"], "v1")
            self.assertEqual(record["ingested_at"], now.isoformat())
            self.assertEqual(
                registry.validate_record(DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT, record),
                (),
            )

    def test_adapter_rejects_missing_symbols(self) -> None:
        adapter = _build_adapter(fetch_turnover_hist=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "requires at least one symbol, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_missing_turnover_route_when_dataset_requested(self) -> None:
        adapter = _build_adapter(fetch_turnover_hist=lambda **kwargs: [])
        with patch.object(adapter, "_resolve_fetch_turnover_hist", return_value=None):
            with self.assertRaisesRegex(
                RuntimeError,
                "turnover/liquidity function is unavailable",
            ):
                fetch_source_result(
                    adapter,
                    SourceRequest(
                        dataset=DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT,
                        source_name=AKSHARE_SOURCE_ID,
                        symbols=("600000.SH",),
                    ),
                )

    def test_adapter_rejects_conflicting_duplicate_turnover_liquidity_row(self) -> None:
        adapter = _build_adapter(
            fetch_turnover_hist=lambda **kwargs: [
                {
                    "日期": "2024-06-10",
                    "成交量": 125000000,
                    "成交额": 1380000000,
                    "换手率": 2.16,
                },
                {
                    "日期": "2024-06-10",
                    "成交量": 125000000,
                    "成交额": 1380000001,
                    "换手率": 2.16,
                },
            ]
        )

        with self.assertRaisesRegex(
            ValueError,
            "Conflicting duplicate A-share capital-flow row detected",
        ):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_missing_required_turnover_field(self) -> None:
        adapter = _build_adapter(
            fetch_turnover_hist=lambda **kwargs: [
                {
                    "日期": "2024-06-10",
                    "成交量": 125000000,
                    "成交额": 1380000000,
                }
            ]
        )

        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_network_access_in_default_tests(self) -> None:
        adapter = _build_adapter(
            fetch_turnover_hist=lambda **kwargs: [
                {
                    "日期": "2024-06-10",
                    "成交量": 125000000,
                    "成交额": 1380000000,
                    "换手率": 2.16,
                }
            ]
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

        self.assertEqual(result.record_count, 1)


if __name__ == "__main__":
    unittest.main()
