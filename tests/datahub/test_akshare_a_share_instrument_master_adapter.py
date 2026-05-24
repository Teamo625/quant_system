from datetime import datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareInstrumentMasterAdapter,
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
    fetch_sh_main=None,
    fetch_sh_kcb=None,
    fetch_sz_a=None,
    fetch_bj_a=None,
    now_fn=None,
) -> AkshareAShareInstrumentMasterAdapter:
    return AkshareAShareInstrumentMasterAdapter(
        fetch_sh_main=fetch_sh_main or (lambda: []),
        fetch_sh_kcb=fetch_sh_kcb or (lambda: []),
        fetch_sz_a=fetch_sz_a or (lambda: []),
        fetch_bj_a=fetch_bj_a or (lambda: []),
        now_fn=now_fn,
    )


class AkshareAShareInstrumentMasterAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = _build_adapter()
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_records(self) -> None:
        calls: list[str] = []
        now = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        def fake_fetch_sh_main():
            calls.append("sh_main")
            return _FakeDataFrame(
                [
                    {
                        "证券代码": "600000",
                        "证券简称": "浦发银行",
                        "上市日期": "19991110",
                        "更新时间": "2024-01-15 09:10:00",
                    }
                ]
            )

        def fake_fetch_sh_kcb():
            calls.append("sh_kcb")
            return [
                {
                    "证券代码": "688001",
                    "证券简称": "华兴源创",
                    "上市日期": "20190722",
                }
            ]

        def fake_fetch_sz_a():
            calls.append("sz_a")
            return [
                {
                    "A股代码": "000001",
                    "A股简称": "平安银行",
                    "A股上市日期": "19910403",
                }
            ]

        def fake_fetch_bj_a():
            calls.append("bj_a")
            return [
                {
                    "证券代码": "920001",
                    "证券简称": "北交样本",
                    "上市日期": "20231115",
                    "报告日期": "2024-01-15",
                }
            ]

        adapter = _build_adapter(
            fetch_sh_main=fake_fetch_sh_main,
            fetch_sh_kcb=fake_fetch_sh_kcb,
            fetch_sz_a=fake_fetch_sz_a,
            fetch_bj_a=fake_fetch_bj_a,
            now_fn=lambda: now,
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                ),
                fetched_at=datetime(2024, 1, 15, 10, 5, 0, tzinfo=timezone.utc),
            )

        self.assertEqual(calls, ["sh_main", "sh_kcb", "sz_a", "bj_a"])
        self.assertEqual(result.record_count, 4)

        records_by_symbol = {record["symbol"]: record for record in result.normalized_records}
        self.assertEqual(set(records_by_symbol), {"000001.SZ", "600000.SH", "688001.SH", "920001.BJ"})

        sh_record = records_by_symbol["600000.SH"]
        self.assertEqual(sh_record["exchange"], "SSE")
        self.assertEqual(sh_record["market"], "CN")
        self.assertEqual(sh_record["asset_type"], "stock")
        self.assertEqual(sh_record["currency"], "CNY")
        self.assertEqual(sh_record["raw_symbol"], "600000")
        self.assertEqual(sh_record["list_date"], "1999-11-10")
        self.assertEqual(sh_record["delist_date"], "9999-12-31")
        self.assertTrue(sh_record["is_active"])
        self.assertEqual(sh_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(sh_record["schema_version"], "v1")
        self.assertEqual(sh_record["ingested_at"], now.isoformat())
        self.assertEqual(sh_record["source_ts"], "2024-01-15T09:10:00")

        sz_record = records_by_symbol["000001.SZ"]
        self.assertEqual(sz_record["exchange"], "SZSE")
        self.assertEqual(sz_record["raw_symbol"], "000001")
        self.assertNotIn("source_ts", sz_record)

        bj_record = records_by_symbol["920001.BJ"]
        self.assertEqual(bj_record["exchange"], "BSE")
        self.assertEqual(bj_record["source_ts"], "2024-01-15T00:00:00")

        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.INSTRUMENT_MASTER, record),
                (),
            )

    def test_adapter_filters_by_canonical_and_raw_symbols(self) -> None:
        adapter = _build_adapter(
            fetch_sh_main=lambda: [{"证券代码": "600000", "证券简称": "浦发银行", "上市日期": "19991110"}],
            fetch_sz_a=lambda: [{"A股代码": "000001", "A股简称": "平安银行", "A股上市日期": "19910403"}],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INSTRUMENT_MASTER,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000001.SZ", "600000"),
            ),
        )
        self.assertEqual(result.record_count, 2)
        self.assertEqual(
            {record["symbol"] for record in result.normalized_records},
            {"000001.SZ", "600000.SH"},
        )

    def test_adapter_filters_by_prefixed_symbol_form(self) -> None:
        adapter = _build_adapter(
            fetch_sz_a=lambda: [{"A股代码": "000001", "A股简称": "平安银行", "A股上市日期": "19910403"}],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INSTRUMENT_MASTER,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("SZ000001",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "000001.SZ")

    def test_adapter_rejects_invalid_symbol_filter_value(self) -> None:
        adapter = _build_adapter()
        with self.assertRaisesRegex(ValueError, "Invalid symbol filter format"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("abc",),
                ),
            )

    def test_adapter_rejects_invalid_symbol_filter_market_code_combination(self) -> None:
        adapter = _build_adapter()
        with self.assertRaisesRegex(ValueError, "market-code combination"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SZ",),
                ),
            )

    def test_adapter_rejects_non_string_symbol_filter_value(self) -> None:
        adapter = _build_adapter()
        with self.assertRaisesRegex(ValueError, "value type"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=(123,),
                ),
            )

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = _build_adapter()
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape(self) -> None:
        adapter = _build_adapter(fetch_sh_main=lambda: {"证券代码": "600000"})
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_non_mapping_payload_row(self) -> None:
        adapter = _build_adapter(fetch_sh_main=lambda: [1])
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_missing_required_source_field(self) -> None:
        adapter = _build_adapter(
            fetch_sh_main=lambda: [{"证券代码": "600000", "证券简称": "浦发银行"}]
        )
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_invalid_required_name(self) -> None:
        adapter = _build_adapter(
            fetch_sh_main=lambda: [{"证券代码": "600000", "证券简称": " ", "上市日期": "19991110"}]
        )
        with self.assertRaisesRegex(ValueError, "Invalid name value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_invalid_list_date(self) -> None:
        adapter = _build_adapter(
            fetch_sh_main=lambda: [
                {"证券代码": "600000", "证券简称": "浦发银行", "上市日期": "2024/01/01"}
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid list_date value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_invalid_route_code_prefix(self) -> None:
        adapter = _build_adapter(
            fetch_sh_main=lambda: [
                {"证券代码": "000001", "证券简称": "平安银行", "上市日期": "19910403"}
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid A-share code prefix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_invalid_optional_source_ts_value(self) -> None:
        adapter = _build_adapter(
            fetch_sh_main=lambda: [
                {
                    "证券代码": "600000",
                    "证券简称": "浦发银行",
                    "上市日期": "19991110",
                    "更新时间": "not-a-datetime",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid source_ts value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_omits_optional_source_ts_when_blank(self) -> None:
        adapter = _build_adapter(
            fetch_sh_main=lambda: [
                {
                    "证券代码": "600000",
                    "证券简称": "浦发银行",
                    "上市日期": "19991110",
                    "更新时间": " ",
                }
            ],
            now_fn=lambda: datetime(2024, 1, 10, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INSTRUMENT_MASTER,
                source_name=AKSHARE_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertNotIn("source_ts", result.normalized_records[0])

    def test_adapter_deduplicates_benign_duplicates_prefers_latest_source_ts(self) -> None:
        adapter = _build_adapter(
            fetch_sh_main=lambda: [
                {
                    "证券代码": "600000",
                    "证券简称": "浦发银行",
                    "上市日期": "19991110",
                    "更新时间": "2024-01-11",
                }
            ],
            fetch_sh_kcb=lambda: [
                {
                    "证券代码": "600000",
                    "证券简称": "浦发银行",
                    "上市日期": "19991110",
                    "更新时间": "2024-01-12",
                }
            ],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INSTRUMENT_MASTER,
                source_name=AKSHARE_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "600000.SH")
        self.assertEqual(result.normalized_records[0]["source_ts"], "2024-01-12T00:00:00")

    def test_adapter_rejects_conflicting_duplicate_symbol(self) -> None:
        adapter = _build_adapter(
            fetch_sh_main=lambda: [
                {"证券代码": "600000", "证券简称": "浦发银行", "上市日期": "19991110"}
            ],
            fetch_sh_kcb=lambda: [
                {"证券代码": "600000", "证券简称": "冲突名称", "上市日期": "19991110"}
            ],
        )
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate A-share instrument row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_keeps_active_defaults(self) -> None:
        adapter = _build_adapter(
            fetch_sh_main=lambda: [{"证券代码": "600000", "证券简称": "浦发银行", "上市日期": "19991110"}],
            fetch_sz_a=lambda: [{"A股代码": "000001", "A股简称": "平安银行", "A股上市日期": "19910403"}],
            fetch_bj_a=lambda: [{"证券代码": "920001", "证券简称": "北交样本", "上市日期": "20231115"}],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INSTRUMENT_MASTER,
                source_name=AKSHARE_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 3)
        for record in result.normalized_records:
            self.assertEqual(record["delist_date"], "9999-12-31")
            self.assertTrue(record["is_active"])

    def test_adapter_wraps_network_related_route_failure_for_live_diagnostics(self) -> None:
        class ProxyError(Exception):
            pass

        def failing_fetch_sh_main():
            raise ProxyError("Unable to connect to proxy")

        adapter = _build_adapter(fetch_sh_main=failing_fetch_sh_main)
        with self.assertRaisesRegex(RuntimeError, "route unavailable"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_does_not_mask_non_network_route_errors(self) -> None:
        def failing_fetch_sh_main():
            raise ValueError("bad instrument payload")

        adapter = _build_adapter(fetch_sh_main=failing_fetch_sh_main)
        with self.assertRaisesRegex(ValueError, "bad instrument payload"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )


if __name__ == "__main__":
    unittest.main()
