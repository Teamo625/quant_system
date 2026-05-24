from datetime import datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareIndexConstituentsAdapter,
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


class AkshareIndexConstituentsAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: []
        )
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_index_constituents(self) -> None:
        calls: list[dict] = []
        registry = DatasetRegistry()
        now = datetime(2024, 1, 12, 10, 0, 0, tzinfo=timezone.utc)

        def fake_fetch_weight(**kwargs):
            calls.append(kwargs)
            return [
                {
                    "成分券代码": "600000",
                    "纳入日期": "20200102",
                    "剔除日期": "",
                    "权重": "0.52",
                    "更新时间": "2024-01-12 09:31:00",
                }
            ]

        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=fake_fetch_weight,
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.INDEX_CONSTITUENTS,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("000300.CN_INDEX",),
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(adapter, request)

        self.assertEqual(calls, [{"symbol": "000300"}])
        self.assertEqual(result.record_count, 1)

        record = result.normalized_records[0]
        self.assertEqual(record["index_code"], "000300.CN_INDEX")
        self.assertEqual(record["symbol"], "600000.SH")
        self.assertEqual(record["market"], "CN_A")
        self.assertEqual(record["in_date"], "2020-01-02")
        self.assertEqual(record["weight"], 0.52)
        self.assertEqual(record["source_ts"], "2024-01-12T09:31:00")
        self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(record["schema_version"], "v1")
        self.assertEqual(record["ingested_at"], now.isoformat())
        self.assertEqual(
            registry.validate_record(DatasetName.INDEX_CONSTITUENTS, record),
            (),
        )

    def test_adapter_accepts_common_index_identifier_variants(self) -> None:
        for user_symbol in ("000300.CN_INDEX", "000300", "sh000300"):
            calls: list[dict] = []

            def fake_fetch_weight(**kwargs):
                calls.append(kwargs)
                return [{"成分券代码": "000001"}]

            adapter = AkshareIndexConstituentsAdapter(
                fetch_index_cons_weight_csindex=fake_fetch_weight,
            )
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_CONSTITUENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=(user_symbol,),
                ),
            )
            with self.subTest(symbol=user_symbol):
                self.assertEqual(calls, [{"symbol": "000300"}])
                self.assertEqual(
                    result.normalized_records[0]["index_code"],
                    "000300.CN_INDEX",
                )

    def test_adapter_uses_fallback_route_when_primary_network_unavailable(self) -> None:
        def fake_fetch_weight(**kwargs):
            raise OSError("proxy connect failed to csindex.com.cn")

        fallback_calls: list[dict] = []

        def fake_fetch_csindex(**kwargs):
            fallback_calls.append(kwargs)
            return [{"成分券代码": "600000"}]

        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=fake_fetch_weight,
            fetch_index_cons_csindex=fake_fetch_csindex,
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INDEX_CONSTITUENTS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000300",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(fallback_calls, [{"symbol": "000300"}])

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: []
        )
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000300",),
                ),
            )

    def test_adapter_rejects_missing_symbols(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: []
        )
        with self.assertRaisesRegex(ValueError, "requires exactly one index identifier, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_CONSTITUENTS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_multiple_symbols(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: []
        )
        with self.assertRaisesRegex(ValueError, "exactly one index identifier"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_CONSTITUENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000300", "000001"),
                ),
            )

    def test_adapter_rejects_invalid_market_suffix(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: []
        )
        with self.assertRaisesRegex(ValueError, "Unsupported index market suffix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_CONSTITUENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000300.SH",),
                ),
            )

    def test_adapter_rejects_invalid_index_identifier_format(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: []
        )
        with self.assertRaisesRegex(ValueError, "Unsupported index identifier format"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_CONSTITUENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("ABCDEF",),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: {"成分券代码": "000001"},
            fetch_index_cons_csindex=lambda **kwargs: {"成分券代码": "000001"},
            fetch_index_cons_sina=lambda **kwargs: {"成分券代码": "000001"},
            fetch_index_cons=lambda **kwargs: {"成分券代码": "000001"},
        )
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_CONSTITUENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000300",),
                ),
            )

    def test_adapter_rejects_non_mapping_payload_row(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: [1],
            fetch_index_cons_csindex=lambda **kwargs: [1],
            fetch_index_cons_sina=lambda **kwargs: [1],
            fetch_index_cons=lambda **kwargs: [1],
        )
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_CONSTITUENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000300",),
                ),
            )

    def test_adapter_rejects_missing_required_symbol_field(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: [{"名称": "浦发银行"}]
        )
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_CONSTITUENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000300",),
                ),
            )

    def test_adapter_symbol_normalization_is_stable(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: [
                {"成分券代码": "600000"},
                {"成分券代码": "000001"},
                {"成分券代码": "830799"},
                {"成分券代码": "sh600000"},
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INDEX_CONSTITUENTS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000300",),
            ),
        )
        symbols = {item["symbol"] for item in result.normalized_records}
        self.assertEqual(symbols, {"600000.SH", "000001.SZ", "830799.BJ"})

    def test_adapter_rejects_invalid_symbol_value(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: [{"成分券代码": "BAD"}]
        )
        with self.assertRaisesRegex(ValueError, "Invalid index constituent symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_CONSTITUENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000300",),
                ),
            )

    def test_adapter_in_date_falls_back_when_missing(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: [{"成分券代码": "000001"}]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INDEX_CONSTITUENTS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000300",),
            ),
        )
        self.assertEqual(result.normalized_records[0]["in_date"], "1900-01-01")

    def test_adapter_in_date_and_out_date_parsing(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: [
                {
                    "成分券代码": "000001",
                    "纳入日期": "2024-01-02",
                    "剔除日期": "20250103",
                }
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INDEX_CONSTITUENTS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000300",),
            ),
        )
        self.assertEqual(result.normalized_records[0]["in_date"], "2024-01-02")
        self.assertEqual(result.normalized_records[0]["out_date"], "2025-01-03")

    def test_adapter_rejects_invalid_out_date_value(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: [
                {"成分券代码": "000001", "剔除日期": "not-a-date"}
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid out_date value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_CONSTITUENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000300",),
                ),
            )

    def test_adapter_weight_parsing_and_optional_omission(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: [
                {"成分券代码": "000001", "权重": "0.52%"},
                {"成分券代码": "600000", "权重": " "},
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INDEX_CONSTITUENTS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000300",),
            ),
        )
        rows = {item["symbol"]: item for item in result.normalized_records}
        self.assertEqual(rows["000001.SZ"]["weight"], 0.52)
        self.assertNotIn("weight", rows["600000.SH"])

    def test_adapter_rejects_invalid_weight_value(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: [
                {"成分券代码": "000001", "权重": "bad"}
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid weight value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_CONSTITUENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000300",),
                ),
            )

    def test_adapter_rejects_out_of_range_weight_value(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: [
                {"成分券代码": "000001", "权重": "101"}
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid weight value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_CONSTITUENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000300",),
                ),
            )

    def test_adapter_rejects_invalid_optional_source_ts_value(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: [
                {"成分券代码": "000001", "更新时间": "not-a-datetime"}
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid source_ts value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_CONSTITUENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000300",),
                ),
            )

    def test_adapter_dedupes_benign_duplicates_deterministically(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: [
                {
                    "成分券代码": "000001",
                    "纳入日期": "2020-01-02",
                    "更新时间": "2024-01-12 09:30:00",
                },
                {
                    "成分券代码": "000001",
                    "纳入日期": "2020-01-02",
                    "更新时间": "2024-01-12 09:31:00",
                },
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INDEX_CONSTITUENTS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000300",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["source_ts"], "2024-01-12T09:31:00")

    def test_adapter_rejects_conflicting_duplicate_rows(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: [
                {"成分券代码": "000001", "纳入日期": "2020-01-02"},
                {"成分券代码": "000001", "纳入日期": "2020-01-03"},
            ]
        )
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate index constituent row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_CONSTITUENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000300",),
                ),
            )

    def test_adapter_handles_dataframe_like_payload(self) -> None:
        payload = _FakeDataFrame([{"成分券代码": "000001", "纳入日期": "20240102"}])
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: payload
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INDEX_CONSTITUENTS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000300",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["in_date"], "2024-01-02")


if __name__ == "__main__":
    unittest.main()
