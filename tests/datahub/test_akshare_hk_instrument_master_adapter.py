from datetime import datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareHKInstrumentMasterAdapter,
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


def _build_adapter(*, fetch_hk_security_profile=None, now_fn=None) -> AkshareHKInstrumentMasterAdapter:
    return AkshareHKInstrumentMasterAdapter(
        fetch_hk_security_profile=fetch_hk_security_profile or (lambda **kwargs: []),
        now_fn=now_fn,
    )


class AkshareHKInstrumentMasterAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = _build_adapter()
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_record(self) -> None:
        calls: list[dict] = []
        now = datetime(2024, 2, 1, 9, 30, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        def fake_fetch_hk_security_profile(**kwargs):
            calls.append(kwargs)
            return [
                {
                    "证券代码": "00700.HK",
                    "证券简称": "腾讯控股",
                    "上市日期": "2004-06-16",
                    "证券类型": "普通股",
                    "交易所": "香港交易所",
                    "更新时间": "2024-01-31 20:15:00",
                }
            ]

        adapter = _build_adapter(
            fetch_hk_security_profile=fake_fetch_hk_security_profile,
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
                    symbols=("00700.HK",),
                ),
                fetched_at=datetime(2024, 2, 1, 9, 35, 0, tzinfo=timezone.utc),
            )

        self.assertEqual(calls, [{"symbol": "00700"}])
        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["symbol"], "00700.HK")
        self.assertEqual(record["raw_symbol"], "00700")
        self.assertEqual(record["name"], "腾讯控股")
        self.assertEqual(record["market"], "HK")
        self.assertEqual(record["asset_type"], "stock")
        self.assertEqual(record["currency"], "HKD")
        self.assertEqual(record["exchange"], "HKEX")
        self.assertEqual(record["list_date"], "2004-06-16")
        self.assertEqual(record["delist_date"], "9999-12-31")
        self.assertTrue(record["is_active"])
        self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(record["source_ts"], "2024-01-31T20:15:00")
        self.assertEqual(record["ingested_at"], now.isoformat())
        self.assertEqual(record["schema_version"], "v1")
        self.assertEqual(
            registry.validate_record(DatasetName.INSTRUMENT_MASTER, record),
            (),
        )

    def test_adapter_accepts_raw_numeric_hk_symbol(self) -> None:
        adapter = _build_adapter(
            fetch_hk_security_profile=lambda **kwargs: [
                {
                    "证券代码": "00700",
                    "证券简称": "腾讯控股",
                    "上市日期": "20040616",
                    "证券类型": "stock",
                    "交易所": "HKEX",
                }
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INSTRUMENT_MASTER,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "00700.HK")
        self.assertEqual(result.normalized_records[0]["raw_symbol"], "00700")
        self.assertEqual(result.normalized_records[0]["list_date"], "2004-06-16")

    def test_adapter_supports_dataframe_payload_and_source_item_value_shape(self) -> None:
        adapter = _build_adapter(
            fetch_hk_security_profile=lambda **kwargs: _FakeDataFrame(
                [
                    {"项目": "证券代码", "值": "00005.HK"},
                    {"项目": "证券简称", "值": "汇丰控股"},
                    {"项目": "上市日期", "值": "2000-01-03"},
                    {"项目": "证券类型", "值": "普通股"},
                    {"项目": "交易所", "值": "港交所"},
                ]
            )
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INSTRUMENT_MASTER,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00005.HK",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "00005.HK")
        self.assertEqual(result.normalized_records[0]["name"], "汇丰控股")

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = _build_adapter()
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_missing_symbols(self) -> None:
        adapter = _build_adapter()
        with self.assertRaisesRegex(ValueError, "requires exactly one symbol, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_multiple_symbols(self) -> None:
        adapter = _build_adapter()
        with self.assertRaisesRegex(ValueError, "exactly one symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK", "00005.HK"),
                ),
            )

    def test_adapter_rejects_invalid_hk_symbol_and_a_share_symbol(self) -> None:
        adapter = _build_adapter()
        with self.assertRaisesRegex(ValueError, "Unsupported HK symbol format"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("HSI.HK",),
                ),
            )
        with self.assertRaisesRegex(ValueError, "Unsupported symbol market suffix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape_and_row(self) -> None:
        adapter = _build_adapter(fetch_hk_security_profile=lambda **kwargs: {"证券代码": "00700"})
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

        adapter = _build_adapter(fetch_hk_security_profile=lambda **kwargs: [1])
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_missing_required_field(self) -> None:
        adapter = _build_adapter(
            fetch_hk_security_profile=lambda **kwargs: [
                {
                    "证券代码": "00700.HK",
                    "证券简称": "腾讯控股",
                    "证券类型": "普通股",
                    "交易所": "港交所",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_invalid_list_date_and_invalid_name(self) -> None:
        adapter = _build_adapter(
            fetch_hk_security_profile=lambda **kwargs: [
                {
                    "证券代码": "00700.HK",
                    "证券简称": 123,
                    "上市日期": "2024-02-30",
                    "证券类型": "普通股",
                    "交易所": "港交所",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid name value type"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

        adapter = _build_adapter(
            fetch_hk_security_profile=lambda **kwargs: [
                {
                    "证券代码": "00700.HK",
                    "证券简称": "腾讯控股",
                    "上市日期": "2024/02/01",
                    "证券类型": "普通股",
                    "交易所": "港交所",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid list_date value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_non_stock_security_type_and_etf_like_symbol(self) -> None:
        adapter = _build_adapter(
            fetch_hk_security_profile=lambda **kwargs: [
                {
                    "证券代码": "02800.HK",
                    "证券简称": "盈富基金",
                    "上市日期": "1999-11-12",
                    "证券类型": "ETF",
                    "交易所": "香港交易所",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "No stock-like HK instrument profile row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("02800.HK",),
                ),
            )

    def test_adapter_rejects_invalid_exchange_for_hk_stock_slice(self) -> None:
        adapter = _build_adapter(
            fetch_hk_security_profile=lambda **kwargs: [
                {
                    "证券代码": "00700.HK",
                    "证券简称": "腾讯控股",
                    "上市日期": "2004-06-16",
                    "证券类型": "普通股",
                    "交易所": "NYSE",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid exchange value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_omits_optional_source_ts_when_blank(self) -> None:
        adapter = _build_adapter(
            fetch_hk_security_profile=lambda **kwargs: [
                {
                    "证券代码": "00700.HK",
                    "证券简称": "腾讯控股",
                    "上市日期": "2004-06-16",
                    "证券类型": "普通股",
                    "交易所": "港交所",
                    "更新时间": " ",
                }
            ],
            now_fn=lambda: datetime(2024, 2, 1, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INSTRUMENT_MASTER,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertNotIn("source_ts", result.normalized_records[0])

    def test_adapter_rejects_invalid_source_ts(self) -> None:
        adapter = _build_adapter(
            fetch_hk_security_profile=lambda **kwargs: [
                {
                    "证券代码": "00700.HK",
                    "证券简称": "腾讯控股",
                    "上市日期": "2004-06-16",
                    "证券类型": "普通股",
                    "交易所": "港交所",
                    "更新时间": "invalid-ts",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid source_ts value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_unexpected_source_symbol(self) -> None:
        adapter = _build_adapter(
            fetch_hk_security_profile=lambda **kwargs: [
                {
                    "证券代码": "00005.HK",
                    "证券简称": "汇丰控股",
                    "上市日期": "2000-01-03",
                    "证券类型": "普通股",
                    "交易所": "港交所",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "source returned unexpected symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_deduplicates_benign_duplicates_prefers_latest_source_ts(self) -> None:
        adapter = _build_adapter(
            fetch_hk_security_profile=lambda **kwargs: [
                {
                    "证券代码": "00700.HK",
                    "证券简称": "腾讯控股",
                    "上市日期": "2004-06-16",
                    "证券类型": "普通股",
                    "交易所": "港交所",
                    "更新时间": "2024-02-01",
                },
                {
                    "证券代码": "00700",
                    "证券简称": "腾讯控股",
                    "上市日期": "2004-06-16",
                    "证券类型": "stock",
                    "交易所": "HKEX",
                    "更新时间": "2024-02-02",
                },
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INSTRUMENT_MASTER,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["source_ts"], "2024-02-02T00:00:00")

    def test_adapter_rejects_conflicting_duplicate_symbol(self) -> None:
        adapter = _build_adapter(
            fetch_hk_security_profile=lambda **kwargs: [
                {
                    "证券代码": "00700.HK",
                    "证券简称": "腾讯控股",
                    "上市日期": "2004-06-16",
                    "证券类型": "普通股",
                    "交易所": "港交所",
                },
                {
                    "证券代码": "00700.HK",
                    "证券简称": "冲突名称",
                    "上市日期": "2004-06-16",
                    "证券类型": "普通股",
                    "交易所": "港交所",
                },
            ]
        )
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate HK instrument row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_wraps_network_related_route_failure_for_live_diagnostics(self) -> None:
        class ProxyError(Exception):
            pass

        def failing_fetch(**kwargs):
            raise ProxyError("Unable to connect to proxy eastmoney")

        adapter = _build_adapter(fetch_hk_security_profile=failing_fetch)
        with self.assertRaisesRegex(RuntimeError, "route unavailable"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_does_not_mask_non_network_route_errors(self) -> None:
        def failing_fetch(**kwargs):
            raise ValueError("bad hk instrument payload")

        adapter = _build_adapter(fetch_hk_security_profile=failing_fetch)
        with self.assertRaisesRegex(ValueError, "bad hk instrument payload"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )


if __name__ == "__main__":
    unittest.main()
