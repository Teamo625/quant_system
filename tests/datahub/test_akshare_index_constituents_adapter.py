from datetime import date, datetime, timezone
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

    def test_fetch_source_result_normalizes_and_validates_batch_index_constituents(self) -> None:
        calls: list[tuple[str, str]] = []
        registry = DatasetRegistry()
        now = datetime(2024, 1, 12, 10, 0, 0, tzinfo=timezone.utc)

        def fake_fetch_weight(**kwargs):
            calls.append(("weight", kwargs["symbol"]))
            if kwargs["symbol"] == "000300":
                return [
                    {
                        "成分券代码": "600000",
                        "日期": date(2024, 1, 10),
                        "权重": "0.52",
                    }
                ]
            raise OSError("proxy connect failed to csindex.com.cn")

        def fake_fetch_csindex(**kwargs):
            calls.append(("csindex", kwargs["symbol"]))
            raise OSError("connection reset by peer from csindex.com.cn")

        def fake_fetch_index_cons(**kwargs):
            calls.append(("index_cons", kwargs["symbol"]))
            self.assertEqual(kwargs["symbol"], "399001")
            return [
                {
                    "品种代码": "000001",
                    "纳入日期": "2024-01-09",
                }
            ]

        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=fake_fetch_weight,
            fetch_index_cons_csindex=fake_fetch_csindex,
            fetch_index_cons=fake_fetch_index_cons,
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.INDEX_CONSTITUENTS,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("399001", "000300.CN_INDEX", "000300"),
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(adapter, request)

        self.assertEqual(
            calls,
            [
                ("weight", "399001"),
                ("csindex", "399001"),
                ("index_cons", "399001"),
                ("weight", "000300"),
            ],
        )
        self.assertEqual(result.record_count, 2)

        first_record, second_record = result.normalized_records
        self.assertEqual(first_record["index_code"], "000300.CN_INDEX")
        self.assertEqual(first_record["symbol"], "600000.SH")
        self.assertEqual(first_record["in_date"], "2024-01-10")
        self.assertEqual(first_record["weight"], 0.52)
        self.assertEqual(first_record["market"], "CN_A")
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(first_record["ingested_at"], now.isoformat())
        self.assertEqual(
            registry.validate_record(DatasetName.INDEX_CONSTITUENTS, first_record),
            (),
        )

        self.assertEqual(second_record["index_code"], "399001.CN_INDEX")
        self.assertEqual(second_record["symbol"], "000001.SZ")
        self.assertEqual(second_record["in_date"], "2024-01-09")
        self.assertEqual(second_record["market"], "CN_A")
        self.assertEqual(
            registry.validate_record(DatasetName.INDEX_CONSTITUENTS, second_record),
            (),
        )

    def test_adapter_accepts_supported_identifier_variants(self) -> None:
        for user_symbol, expected_code in (
            ("000905.CN_INDEX", "000905.CN_INDEX"),
            ("000905", "000905.CN_INDEX"),
            ("sh000905", "000905.CN_INDEX"),
            ("399001.CN_INDEX", "399001.CN_INDEX"),
            ("399001", "399001.CN_INDEX"),
            ("sz399001", "399001.CN_INDEX"),
            ("000001.CN_INDEX", "000001.CN_INDEX"),
            ("sh000001", "000001.CN_INDEX"),
        ):
            calls: list[dict] = []

            def fake_fetch_weight(**kwargs):
                calls.append(kwargs)
                return [{"成分券代码": "000001", "日期": "20240110"}]

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
                self.assertEqual(len(calls), 1)
                self.assertEqual(
                    result.normalized_records[0]["index_code"],
                    expected_code,
                )

    def test_adapter_rejects_missing_symbols(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: []
        )
        with self.assertRaisesRegex(ValueError, "requires at least one index identifier, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_CONSTITUENTS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_ambiguous_bare_identifier(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: []
        )
        with self.assertRaisesRegex(ValueError, "Ambiguous bare index identifier"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_CONSTITUENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000001",),
                ),
            )

    def test_adapter_rejects_stock_like_etf_hk_and_malformed_identifiers(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: []
        )
        for symbol, message in (
            ("600000.SH", "A-share stock-like identifier is unsupported"),
            ("00700.HK", "Hong Kong stock identifier is unsupported"),
            ("510300.ETF_CN", "ETF/fund identifier is unsupported"),
            ("ABCDEF", "Unsupported index identifier format"),
        ):
            with self.subTest(symbol=symbol):
                with self.assertRaisesRegex(ValueError, message):
                    fetch_source_result(
                        adapter,
                        SourceRequest(
                            dataset=DatasetName.INDEX_CONSTITUENTS,
                            source_name=AKSHARE_SOURCE_ID,
                            symbols=(symbol,),
                        ),
                    )

    def test_adapter_rejects_invalid_identifier_type(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: []
        )
        with self.assertRaisesRegex(ValueError, "Invalid index identifier value type"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_CONSTITUENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=(123,),  # type: ignore[arg-type]
                ),
            )

    def test_adapter_rejects_invalid_identifier_before_partial_batch_fetch(self) -> None:
        calls: list[dict] = []
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: calls.append(kwargs) or []
        )
        with self.assertRaisesRegex(ValueError, "A-share stock-like identifier is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_CONSTITUENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000300", "600000.SH"),
                ),
            )
        self.assertEqual(calls, [])

    def test_adapter_rejects_partial_batch_when_one_symbol_has_no_rows(self) -> None:
        def fake_fetch_weight(**kwargs):
            if kwargs["symbol"] == "000300":
                return [{"成分券代码": "000001", "日期": "20240110"}]
            return []

        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=fake_fetch_weight,
            fetch_index_cons_csindex=lambda **kwargs: [],
            fetch_index_cons=lambda **kwargs: [],
            fetch_index_cons_sina=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "yielded no usable rows for requested symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_CONSTITUENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000300", "000905"),
                ),
            )

    def test_adapter_uses_snapshot_fallback_when_date_routes_unavailable(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: (_ for _ in ()).throw(
                OSError("proxy connect failed to csindex.com.cn")
            ),
            fetch_index_cons_csindex=lambda **kwargs: (_ for _ in ()).throw(
                OSError("connection reset by peer from csindex.com.cn")
            ),
            fetch_index_cons=lambda **kwargs: [],
            fetch_index_cons_sina=lambda **kwargs: [{"code": "600000"}],
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
        self.assertEqual(result.normalized_records[0]["symbol"], "600000.SH")
        self.assertEqual(result.normalized_records[0]["in_date"], "1900-01-01")

    def test_adapter_hard_fails_on_signature_incompatibility(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda: [],
            fetch_index_cons_csindex=lambda **kwargs: [{"成分券代码": "000001"}],
        )
        with self.assertRaisesRegex(RuntimeError, "does not accept required argument"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INDEX_CONSTITUENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000300",),
                ),
            )

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
                {"成分券代码": "600000", "日期": "20240110"},
                {"成分券代码": "000001", "日期": "20240110"},
                {"成分券代码": "830799", "日期": "20240110"},
                {"成分券代码": "sh600000", "日期": "20240110"},
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

    def test_adapter_in_date_uses_effective_like_fields_and_falls_back_when_missing(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: [
                {"成分券代码": "000001", "日期": "2024-01-02"},
                {"成分券代码": "600000"},
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
        self.assertEqual(rows["000001.SZ"]["in_date"], "2024-01-02")
        self.assertEqual(rows["600000.SH"]["in_date"], "1900-01-01")

    def test_adapter_in_date_and_out_date_parsing(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: [
                {
                    "成分券代码": "000001",
                    "生效日期": "2024-01-02",
                    "结束日期": "20250103",
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
                {"成分券代码": "000001", "权重": "0.52%", "日期": "20240110"},
                {"成分券代码": "600000", "权重": " ", "日期": "20240110"},
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
                {"成分券代码": "000001", "权重": "bad", "日期": "20240110"}
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
                {"成分券代码": "000001", "权重": "101", "日期": "20240110"}
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
                {
                    "成分券代码": "000001",
                    "日期": "20240110",
                    "更新时间": "not-a-datetime",
                }
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

    def test_adapter_dedupes_by_effective_date_and_sorts_deterministically(self) -> None:
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
                    "权重": "0.52",
                },
                {
                    "成分券代码": "000001",
                    "纳入日期": "2021-01-02",
                },
                {
                    "成分券代码": "600000",
                    "纳入日期": "2019-01-02",
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
        self.assertEqual(result.record_count, 3)
        self.assertEqual(
            [
                (row["index_code"], row["in_date"], row["symbol"])
                for row in result.normalized_records
            ],
            [
                ("000300.CN_INDEX", "2019-01-02", "600000.SH"),
                ("000300.CN_INDEX", "2020-01-02", "000001.SZ"),
                ("000300.CN_INDEX", "2021-01-02", "000001.SZ"),
            ],
        )
        self.assertEqual(result.normalized_records[1]["source_ts"], "2024-01-12T09:31:00")
        self.assertEqual(result.normalized_records[1]["weight"], 0.52)

    def test_adapter_rejects_conflicting_duplicate_rows(self) -> None:
        adapter = AkshareIndexConstituentsAdapter(
            fetch_index_cons_weight_csindex=lambda **kwargs: [
                {"成分券代码": "000001", "纳入日期": "2020-01-02", "权重": "0.52"},
                {"成分券代码": "000001", "纳入日期": "2020-01-02", "权重": "0.53"},
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
