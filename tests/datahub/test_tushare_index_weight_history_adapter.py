from datetime import date, datetime, timezone
import os
import unittest
from unittest.mock import patch

from quant.datahub.adapters.tushare import (
    TUSHARE_SOURCE_ID,
    TushareIndexWeightHistoryAdapter,
    is_tushare_live_environment_unavailable,
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


class TushareIndexWeightHistoryAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = TushareIndexWeightHistoryAdapter(index_weight_fetcher=lambda **kwargs: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_weight_history(self) -> None:
        calls: list[dict] = []
        registry = DatasetRegistry()
        now = datetime(2024, 1, 12, 10, 0, 0, tzinfo=timezone.utc)

        def fake_fetcher(**kwargs):
            calls.append(kwargs)
            return [
                {
                    "index_code": "399300.SZ",
                    "con_code": "600000.SH",
                    "trade_date": "20240102",
                    "weight": "0.8656",
                    "source_ts": "2024-01-12 09:31:00",
                }
            ]

        adapter = TushareIndexWeightHistoryAdapter(
            index_weight_fetcher=fake_fetcher,
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.INDEX_WEIGHT_HISTORY,
            source_name=TUSHARE_SOURCE_ID,
            start_date=date(2024, 1, 2),
            symbols=("000300.CN_INDEX",),
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(adapter, request)

        self.assertEqual(
            calls,
            [{"index_code": "399300.SZ", "trade_date": "20240102"}],
        )
        self.assertEqual(result.record_count, 1)

        record = result.normalized_records[0]
        self.assertEqual(record["index_code"], "000300.CN_INDEX")
        self.assertEqual(record["symbol"], "600000.SH")
        self.assertEqual(record["market"], "CN_A")
        self.assertEqual(record["effective_date"], "2024-01-02")
        self.assertEqual(record["weight"], 0.8656)
        self.assertEqual(record["weight_unit"], "percent")
        self.assertEqual(record["source_route"], "index_weight")
        self.assertEqual(record["source_ts"], "2024-01-12T09:31:00")
        self.assertEqual(record["source"], TUSHARE_SOURCE_ID)
        self.assertEqual(record["schema_version"], "v1")
        self.assertEqual(record["ingested_at"], now.isoformat())
        self.assertEqual(
            registry.validate_record(DatasetName.INDEX_WEIGHT_HISTORY, record),
            (),
        )

    def test_injected_fetcher_does_not_require_credentials(self) -> None:
        adapter = TushareIndexWeightHistoryAdapter(
            index_weight_fetcher=lambda **kwargs: [
                {
                    "index_code": "399300.SZ",
                    "con_code": "000001.SZ",
                    "trade_date": "20240102",
                    "weight": 0.5,
                }
            ]
        )
        with patch.dict(os.environ, {"TUSHARE_TOKEN": ""}, clear=False):
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                    source_name=TUSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    symbols=("000300.CN_INDEX",),
                ),
            )
        self.assertEqual(result.record_count, 1)

    def test_missing_credentials_fail_clearly_for_non_injected_fetch(self) -> None:
        adapter = TushareIndexWeightHistoryAdapter()
        with patch.dict(os.environ, {"TUSHARE_TOKEN": ""}, clear=False):
            with self.assertRaisesRegex(RuntimeError, "TUSHARE_TOKEN is required"):
                fetch_source_result(
                    adapter,
                    SourceRequest(
                        dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                        source_name=TUSHARE_SOURCE_ID,
                        start_date=date(2024, 1, 2),
                        symbols=("000300.CN_INDEX",),
                    ),
                )

    def test_single_trade_date_and_bounded_range_requests_are_supported(self) -> None:
        calls: list[dict] = []

        def fake_fetcher(**kwargs):
            calls.append(kwargs)
            return [
                {
                    "index_code": "399300.SZ",
                    "con_code": "000001.SZ",
                    "trade_date": "20240102",
                    "weight": 0.5,
                }
            ]

        adapter = TushareIndexWeightHistoryAdapter(index_weight_fetcher=fake_fetcher)

        fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                source_name=TUSHARE_SOURCE_ID,
                start_date=date(2024, 1, 2),
                symbols=("000300.CN_INDEX",),
            ),
        )
        fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                source_name=TUSHARE_SOURCE_ID,
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31),
                symbols=("000300.CN_INDEX",),
            ),
        )

        self.assertEqual(
            calls,
            [
                {"index_code": "399300.SZ", "trade_date": "20240102"},
                {
                    "index_code": "399300.SZ",
                    "start_date": "20240101",
                    "end_date": "20240131",
                },
            ],
        )

    def test_unbounded_and_end_date_only_requests_fail_clearly(self) -> None:
        adapter = TushareIndexWeightHistoryAdapter(index_weight_fetcher=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "requires a bounded request"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                    source_name=TUSHARE_SOURCE_ID,
                    symbols=("000300.CN_INDEX",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "end_date without start_date is unsupported"):
            adapter.fetch(
                DatasetName.INDEX_WEIGHT_HISTORY,
                end_date=date(2024, 1, 2),
                symbols=["000300.CN_INDEX"],
            )

    def test_adapter_accepts_supported_index_identifier_aliases(self) -> None:
        for user_symbol in ("000300.CN_INDEX", "000300.SH", "399300.SZ", "000300"):
            calls: list[dict] = []

            def fake_fetcher(**kwargs):
                calls.append(kwargs)
                return [
                    {
                        "index_code": "399300.SZ",
                        "con_code": "000001.SZ",
                        "trade_date": "20240102",
                        "weight": 0.5,
                    }
                ]

            adapter = TushareIndexWeightHistoryAdapter(index_weight_fetcher=fake_fetcher)
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                    source_name=TUSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    symbols=(user_symbol,),
                ),
            )
            with self.subTest(symbol=user_symbol):
                self.assertEqual(calls, [{"index_code": "399300.SZ", "trade_date": "20240102"}])
                self.assertEqual(
                    result.normalized_records[0]["index_code"],
                    "000300.CN_INDEX",
                )

    def test_adapter_rejects_invalid_index_identifiers(self) -> None:
        adapter = TushareIndexWeightHistoryAdapter(index_weight_fetcher=lambda **kwargs: [])
        invalid_cases = (
            ("600000.SH", "Unsupported China index identifier"),
            ("510300.SH", "Unsupported ETF/fund identifier"),
            ("HSI.HK", "Unsupported Hong Kong index identifier"),
            ("BAD", "Unsupported index identifier format"),
        )

        for symbol, message in invalid_cases:
            with self.subTest(symbol=symbol):
                with self.assertRaisesRegex(ValueError, message):
                    fetch_source_result(
                        adapter,
                        SourceRequest(
                            dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                            source_name=TUSHARE_SOURCE_ID,
                            start_date=date(2024, 1, 2),
                            symbols=(symbol,),
                        ),
                    )

    def test_adapter_rejects_missing_and_multiple_symbols(self) -> None:
        adapter = TushareIndexWeightHistoryAdapter(index_weight_fetcher=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "requires exactly one China index identifier"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                    source_name=TUSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                ),
            )
        with self.assertRaisesRegex(ValueError, "supports exactly one China index identifier"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                    source_name=TUSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    symbols=("000300.CN_INDEX", "000905.CN_INDEX"),
                ),
            )

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = TushareIndexWeightHistoryAdapter(index_weight_fetcher=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_CONSTITUENTS,
                    source_name=TUSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    symbols=("000300.CN_INDEX",),
                ),
            )

    def test_adapter_handles_dataframe_like_payload(self) -> None:
        payload = _FakeDataFrame(
            [
                {
                    "index_code": "399300.SZ",
                    "con_code": "000001",
                    "trade_date": 20240102,
                    "weight": "0.5%",
                }
            ]
        )
        adapter = TushareIndexWeightHistoryAdapter(index_weight_fetcher=lambda **kwargs: payload)
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                source_name=TUSHARE_SOURCE_ID,
                start_date=date(2024, 1, 2),
                symbols=("000300.CN_INDEX",),
            ),
        )
        self.assertEqual(result.normalized_records[0]["symbol"], "000001.SZ")
        self.assertEqual(result.normalized_records[0]["effective_date"], "2024-01-02")

    def test_fractional_weights_are_converted_to_percentage_units(self) -> None:
        adapter = TushareIndexWeightHistoryAdapter(
            index_weight_fetcher=lambda **kwargs: [
                {
                    "index_code": "399300.SZ",
                    "con_code": "000001.SZ",
                    "trade_date": "20240102",
                    "weight_ratio": 0.0123,
                }
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                source_name=TUSHARE_SOURCE_ID,
                start_date=date(2024, 1, 2),
                symbols=("000300.CN_INDEX",),
            ),
        )
        record = result.normalized_records[0]
        self.assertAlmostEqual(record["weight"], 1.23)
        self.assertEqual(record["weight_unit"], "percent")

    def test_optional_fields_are_only_populated_when_available(self) -> None:
        adapter = TushareIndexWeightHistoryAdapter(
            index_weight_fetcher=lambda **kwargs: [
                {
                    "index_code": "399300.SZ",
                    "con_code": "000001.SZ",
                    "trade_date": "20240102",
                    "weight": 0.5,
                    "rebalance_date": "20240101",
                    "out_date": "20240131",
                    "source_ts": "2024-01-12T09:31:00",
                },
                {
                    "index_code": "399300.SZ",
                    "con_code": "600000.SH",
                    "trade_date": "20240102",
                    "weight": 0.4,
                },
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                source_name=TUSHARE_SOURCE_ID,
                start_date=date(2024, 1, 2),
                symbols=("000300.CN_INDEX",),
            ),
        )
        rows = {item["symbol"]: item for item in result.normalized_records}
        self.assertEqual(rows["000001.SZ"]["rebalance_date"], "2024-01-01")
        self.assertEqual(rows["000001.SZ"]["out_date"], "2024-01-31")
        self.assertEqual(rows["000001.SZ"]["source_ts"], "2024-01-12T09:31:00")
        self.assertNotIn("rebalance_date", rows["600000.SH"])
        self.assertNotIn("out_date", rows["600000.SH"])
        self.assertNotIn("source_ts", rows["600000.SH"])

    def test_records_are_sorted_and_duplicates_are_deduplicated_deterministically(self) -> None:
        adapter = TushareIndexWeightHistoryAdapter(
            index_weight_fetcher=lambda **kwargs: [
                {
                    "index_code": "399300.SZ",
                    "con_code": "600000.SH",
                    "trade_date": "20240103",
                    "weight": 0.4,
                },
                {
                    "index_code": "399300.SZ",
                    "con_code": "000001.SZ",
                    "trade_date": "20240102",
                    "weight": 0.5,
                    "source_ts": "2024-01-12T09:30:00",
                },
                {
                    "index_code": "399300.SZ",
                    "con_code": "000001.SZ",
                    "trade_date": "20240102",
                    "weight": 0.5,
                    "source_ts": "2024-01-12T09:31:00",
                },
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                source_name=TUSHARE_SOURCE_ID,
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31),
                symbols=("000300.CN_INDEX",),
            ),
        )
        self.assertEqual(result.record_count, 2)
        self.assertEqual(
            [item["symbol"] for item in result.normalized_records],
            ["000001.SZ", "600000.SH"],
        )
        self.assertEqual(
            result.normalized_records[0]["source_ts"],
            "2024-01-12T09:31:00",
        )

    def test_conflicting_duplicate_rows_fail_clearly(self) -> None:
        adapter = TushareIndexWeightHistoryAdapter(
            index_weight_fetcher=lambda **kwargs: [
                {
                    "index_code": "399300.SZ",
                    "con_code": "000001.SZ",
                    "trade_date": "20240102",
                    "weight": 0.5,
                },
                {
                    "index_code": "399300.SZ",
                    "con_code": "000001.SZ",
                    "trade_date": "20240102",
                    "weight": 0.6,
                },
            ]
        )
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate index weight-history row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                    source_name=TUSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    symbols=("000300.CN_INDEX",),
                ),
            )

    def test_malformed_payload_shape_and_rows_fail_clearly(self) -> None:
        adapter = TushareIndexWeightHistoryAdapter(
            index_weight_fetcher=lambda **kwargs: {"index_code": "399300.SZ"}
        )
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                    source_name=TUSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    symbols=("000300.CN_INDEX",),
                ),
            )

        adapter = TushareIndexWeightHistoryAdapter(index_weight_fetcher=lambda **kwargs: [1])
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                    source_name=TUSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    symbols=("000300.CN_INDEX",),
                ),
            )

    def test_missing_required_fields_fail_clearly(self) -> None:
        missing_field_adapter = TushareIndexWeightHistoryAdapter(
            index_weight_fetcher=lambda **kwargs: [
                {
                    "index_code": "399300.SZ",
                    "trade_date": "20240102",
                    "weight": 0.5,
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                missing_field_adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                    source_name=TUSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    symbols=("000300.CN_INDEX",),
                ),
            )

    def test_invalid_symbol_value_fails_clearly(self) -> None:
        invalid_symbol_adapter = TushareIndexWeightHistoryAdapter(
            index_weight_fetcher=lambda **kwargs: [
                {
                    "index_code": "399300.SZ",
                    "con_code": "BAD",
                    "trade_date": "20240102",
                    "weight": 0.5,
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid index constituent symbol format"):
            fetch_source_result(
                invalid_symbol_adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                    source_name=TUSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    symbols=("000300.CN_INDEX",),
                ),
            )

    def test_invalid_date_and_weight_values_fail_clearly(self) -> None:
        invalid_date_adapter = TushareIndexWeightHistoryAdapter(
            index_weight_fetcher=lambda **kwargs: [
                {
                    "index_code": "399300.SZ",
                    "con_code": "000001.SZ",
                    "trade_date": "not-a-date",
                    "weight": 0.5,
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid effective_date value"):
            fetch_source_result(
                invalid_date_adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                    source_name=TUSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    symbols=("000300.CN_INDEX",),
                ),
            )

        invalid_weight_adapter = TushareIndexWeightHistoryAdapter(
            index_weight_fetcher=lambda **kwargs: [
                {
                    "index_code": "399300.SZ",
                    "con_code": "000001.SZ",
                    "trade_date": "20240102",
                    "weight": 120,
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid weight value"):
            fetch_source_result(
                invalid_weight_adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                    source_name=TUSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    symbols=("000300.CN_INDEX",),
                ),
            )

    def test_adapter_rejects_payload_index_code_mismatch(self) -> None:
        adapter = TushareIndexWeightHistoryAdapter(
            index_weight_fetcher=lambda **kwargs: [
                {
                    "index_code": "000905.SH",
                    "con_code": "000001.SZ",
                    "trade_date": "20240102",
                    "weight": 0.5,
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Unsupported source index_code value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                    source_name=TUSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    symbols=("000300.CN_INDEX",),
                ),
            )

    def test_route_signature_incompatibility_is_not_classified_as_environment_unavailable(
        self,
    ) -> None:
        def bad_fetcher(symbol=None):
            return []

        adapter = TushareIndexWeightHistoryAdapter(index_weight_fetcher=bad_fetcher)
        with self.assertRaisesRegex(RuntimeError, "does not accept required argument"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_WEIGHT_HISTORY,
                    source_name=TUSHARE_SOURCE_ID,
                    start_date=date(2024, 1, 2),
                    symbols=("000300.CN_INDEX",),
                ),
            )
        self.assertFalse(
            is_tushare_live_environment_unavailable(
                RuntimeError(
                    "Tushare index_weight route signature incompatibility: unexpected keyword "
                    "argument 'index_code'"
                )
            )
        )


if __name__ == "__main__":
    unittest.main()
