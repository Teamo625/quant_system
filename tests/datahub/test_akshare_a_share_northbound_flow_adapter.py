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
    fetch_northbound=None,
    fetch_capital_flow=None,
    fetch_turnover_hist=None,
    now_fn=None,
) -> AkshareAShareCapitalFlowSnapshotAdapter:
    return AkshareAShareCapitalFlowSnapshotAdapter(
        fetch_northbound=fetch_northbound,
        fetch_capital_flow=fetch_capital_flow,
        fetch_turnover_hist=fetch_turnover_hist,
        now_fn=now_fn,
    )


class AkshareAShareNorthboundFlowAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = _build_adapter(fetch_northbound=lambda **kwargs: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_northbound_flow_snapshot(self) -> None:
        northbound_calls: list[dict[str, str]] = []
        now = datetime(2024, 6, 12, 16, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        def fake_fetch_northbound(*, symbol: str):
            northbound_calls.append({"symbol": symbol})
            return [
                {
                    "持股日期": "2024-06-10",
                    "持股数量": 101786169,
                    "持股市值": 1658096693.01,
                    "持股数量占A股百分比": 0.49,
                },
                {
                    "持股日期": "2024-06-11",
                    "持股数量": "102064808",
                    "持股市值": "1653449889.6",
                    "持股数量占A股百分比": "0.49",
                    "今日增持股数": 278639,
                    "今日增持资金": "4525598.9102",
                    "今日持股市值变化": -4646803.41,
                },
            ]

        adapter = _build_adapter(
            fetch_northbound=fake_fetch_northbound,
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.NORTHBOUND_FLOW_SNAPSHOT,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("600000.SH",),
            start_date=date(2024, 6, 10),
            end_date=date(2024, 6, 11),
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(adapter, request)

        self.assertEqual(northbound_calls, [{"symbol": "600000"}])
        self.assertEqual(result.record_count, 2)

        first_record = result.normalized_records[0]
        second_record = result.normalized_records[1]

        self.assertEqual(first_record["symbol"], "600000.SH")
        self.assertEqual(first_record["market"], "CN")
        self.assertEqual(first_record["trade_date"], "2024-06-10")
        self.assertEqual(first_record["northbound_shares_held"], 101786169.0)
        self.assertEqual(first_record["northbound_holding_market_value"], 1658096693.01)
        self.assertEqual(first_record["northbound_holding_ratio_a_share_pct"], 0.49)
        self.assertEqual(first_record["source_route"], "stock_hsgt_individual_em")
        self.assertNotIn("northbound_net_buy", first_record)

        self.assertEqual(second_record["trade_date"], "2024-06-11")
        self.assertEqual(second_record["northbound_share_change"], 278639.0)
        self.assertEqual(second_record["northbound_net_buy"], 4525598.9102)
        self.assertEqual(
            second_record["northbound_holding_market_value_change"],
            -4646803.41,
        )
        self.assertEqual(second_record["ingested_at"], now.isoformat())

        self.assertEqual(
            registry.validate_record(DatasetName.NORTHBOUND_FLOW_SNAPSHOT, first_record),
            (),
        )
        self.assertEqual(
            registry.validate_record(DatasetName.NORTHBOUND_FLOW_SNAPSHOT, second_record),
            (),
        )

    def test_adapter_supports_dataframe_like_payloads(self) -> None:
        adapter = _build_adapter(
            fetch_northbound=lambda **kwargs: _FakeDataFrame(
                [
                    {
                        "持股日期": "2024-06-10",
                        "持股数量": 101.0,
                        "持股市值": 202.0,
                        "持股数量占A股百分比": 0.01,
                    }
                ]
            )
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.NORTHBOUND_FLOW_SNAPSHOT,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000001.SZ",),
            ),
        )

        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "000001.SZ")
        self.assertEqual(result.normalized_records[0]["source_route"], "stock_hsgt_individual_em")

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = _build_adapter(fetch_northbound=lambda **kwargs: [])

        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_requires_at_least_one_symbol(self) -> None:
        adapter = _build_adapter(fetch_northbound=lambda **kwargs: [])

        with self.assertRaisesRegex(ValueError, "requires at least one symbol, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.NORTHBOUND_FLOW_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_route_unavailability_is_not_silently_hidden_for_dedicated_dataset(self) -> None:
        adapter = _build_adapter(
            fetch_northbound=lambda **kwargs: (_ for _ in ()).throw(
                RuntimeError("ProxyError: proxy down")
            )
        )

        with self.assertRaisesRegex(RuntimeError, "ProxyError: proxy down"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.NORTHBOUND_FLOW_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_missing_required_northbound_field_is_reported(self) -> None:
        adapter = _build_adapter(
            fetch_northbound=lambda **kwargs: [{"持股日期": "2024-06-10", "持股市值": 1.0}]
        )

        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.NORTHBOUND_FLOW_SNAPSHOT,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )


if __name__ == "__main__":
    unittest.main()
