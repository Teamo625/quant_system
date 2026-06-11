from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareSectorDailyBarAdapter,
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


class AkshareSectorDailyBarAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [],
        )
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_sector_daily_bars(self) -> None:
        concept_calls: list[dict] = []
        registry = DatasetRegistry()
        now = datetime(2024, 1, 12, 10, 0, 0, tzinfo=timezone.utc)

        def fake_fetch_concept_hist(**kwargs):
            concept_calls.append(kwargs)
            return [
                {
                    "日期": "2024-01-03",
                    "开盘": "1000.0",
                    "最高": 1020.0,
                    "最低": "990.0",
                    "收盘": 1010.0,
                    "成交量": "12345",
                    "成交额": "9876543.21",
                    "source_ts": "2024-01-03T16:00:00",
                }
            ]

        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=fake_fetch_concept_hist,
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.SECTOR_DAILY_BARS,
            source_name=AKSHARE_SOURCE_ID,
            start_date=date(2024, 1, 2),
            end_date=date(2024, 1, 5),
            symbols=("CONCEPT:绿色电力",),
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                request,
                fetched_at=datetime(2024, 1, 12, 10, 5, 0, tzinfo=timezone.utc),
            )

        self.assertEqual(len(concept_calls), 1)
        self.assertEqual(concept_calls[0]["symbol"], "绿色电力")
        self.assertEqual(concept_calls[0]["start_date"], "20240102")
        self.assertEqual(concept_calls[0]["end_date"], "20240105")
        self.assertEqual(concept_calls[0]["period"], "daily")
        self.assertEqual(concept_calls[0]["adjust"], "")

        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["sector_id"], "CONCEPT:绿色电力")
        self.assertEqual(record["market"], "CN_SECTOR")
        self.assertEqual(record["trade_date"], "2024-01-03")
        self.assertEqual(record["open"], 1000.0)
        self.assertEqual(record["high"], 1020.0)
        self.assertEqual(record["low"], 990.0)
        self.assertEqual(record["close"], 1010.0)
        self.assertEqual(record["volume"], 12345.0)
        self.assertEqual(record["amount"], 9876543.21)
        self.assertEqual(record["source_ts"], "2024-01-03T16:00:00")
        self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(record["schema_version"], "v1")
        self.assertEqual(record["ingested_at"], now.isoformat())
        self.assertEqual(
            registry.validate_record(DatasetName.SECTOR_DAILY_BARS, record),
            (),
        )

    def test_adapter_routes_industry_and_concept_identifiers(self) -> None:
        industry_calls: list[dict] = []
        concept_calls: list[dict] = []

        def fake_fetch_industry_hist(**kwargs):
            industry_calls.append(kwargs)
            return [
                {
                    "date": "2024-01-03",
                    "open": 100.0,
                    "high": 101.0,
                    "low": 99.0,
                    "close": 100.5,
                }
            ]

        def fake_fetch_concept_hist(**kwargs):
            concept_calls.append(kwargs)
            return [
                {
                    "date": "2024-01-03",
                    "open": 200.0,
                    "high": 201.0,
                    "low": 199.0,
                    "close": 200.5,
                }
            ]

        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=fake_fetch_industry_hist,
            fetch_concept_hist=fake_fetch_concept_hist,
        )

        industry_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("INDUSTRY:小金属",),
            ),
        )
        concept_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("CONCEPT:绿色电力",),
            ),
        )

        self.assertEqual(len(industry_calls), 1)
        self.assertEqual(len(concept_calls), 1)
        self.assertEqual(industry_calls[0]["symbol"], "小金属")
        self.assertEqual(concept_calls[0]["symbol"], "绿色电力")
        self.assertEqual(industry_result.normalized_records[0]["sector_id"], "INDUSTRY:小金属")
        self.assertEqual(concept_result.normalized_records[0]["sector_id"], "CONCEPT:绿色电力")

    def test_adapter_supports_multi_sector_batch_requests(self) -> None:
        industry_calls: list[dict] = []
        concept_calls: list[dict] = []

        def fake_fetch_industry_hist(**kwargs):
            industry_calls.append(kwargs)
            return [
                {
                    "date": "2024-01-03",
                    "open": 100.0,
                    "high": 101.0,
                    "low": 99.0,
                    "close": 100.5,
                }
            ]

        def fake_fetch_concept_hist(**kwargs):
            concept_calls.append(kwargs)
            return [
                {
                    "date": "2024-01-04",
                    "open": 200.0,
                    "high": 201.0,
                    "low": 199.0,
                    "close": 200.5,
                }
            ]

        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=fake_fetch_industry_hist,
            fetch_concept_hist=fake_fetch_concept_hist,
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=(" industry : 小金属 ", "concept:绿色电力"),
            ),
        )

        self.assertEqual(industry_calls, [{"symbol": "小金属", "period": "日k", "adjust": ""}])
        self.assertEqual(concept_calls, [{"symbol": "绿色电力", "period": "daily", "adjust": ""}])
        self.assertEqual(result.record_count, 2)
        self.assertEqual(
            [(record["sector_id"], record["trade_date"]) for record in result.normalized_records],
            [("CONCEPT:绿色电力", "2024-01-04"), ("INDUSTRY:小金属", "2024-01-03")],
        )

    def test_adapter_accepts_source_native_bk_identifiers(self) -> None:
        industry_calls: list[dict] = []
        concept_calls: list[dict] = []

        def fake_fetch_industry_hist(**kwargs):
            industry_calls.append(kwargs)
            return [
                {
                    "date": "2024-01-03",
                    "open": 100.0,
                    "high": 101.0,
                    "low": 99.0,
                    "close": 100.5,
                }
            ]

        def fake_fetch_concept_hist(**kwargs):
            concept_calls.append(kwargs)
            return [
                {
                    "date": "2024-01-03",
                    "open": 200.0,
                    "high": 201.0,
                    "low": 199.0,
                    "close": 200.5,
                }
            ]

        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=fake_fetch_industry_hist,
            fetch_concept_hist=fake_fetch_concept_hist,
        )

        industry_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("INDUSTRY:BK1027",),
            ),
        )
        concept_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("CONCEPT:BK0715",),
            ),
        )

        self.assertEqual(industry_calls[0]["symbol"], "BK1027")
        self.assertEqual(concept_calls[0]["symbol"], "BK0715")
        self.assertEqual(industry_result.normalized_records[0]["sector_id"], "INDUSTRY:BK1027")
        self.assertEqual(concept_result.normalized_records[0]["sector_id"], "CONCEPT:BK0715")

    def test_adapter_falls_back_to_ths_index_when_em_network_unavailable(self) -> None:
        concept_hist_calls: list[dict] = []
        concept_index_calls: list[dict] = []

        class ProxyError(Exception):
            pass

        def fake_fetch_concept_hist(**kwargs):
            concept_hist_calls.append(kwargs)
            raise ProxyError("Unable to connect to proxy")

        def fake_fetch_concept_index_ths(symbol, start_date="", end_date=""):
            concept_index_calls.append(
                {
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                }
            )
            return [
                {
                    "日期": "2024-01-01",
                    "开盘价": 1000.0,
                    "最高价": 1020.0,
                    "最低价": 990.0,
                    "收盘价": 1010.0,
                    "成交量": 1000,
                    "成交额": 1000000,
                },
                {
                    "日期": "2024-01-03",
                    "开盘价": 1011.0,
                    "最高价": 1030.0,
                    "最低价": 1001.0,
                    "收盘价": 1022.0,
                    "成交量": 1100,
                    "成交额": 1200000,
                },
                {
                    "日期": "2024-01-06",
                    "开盘价": 1020.0,
                    "最高价": 1035.0,
                    "最低价": 1008.0,
                    "收盘价": 1015.0,
                    "成交量": 1200,
                    "成交额": 1300000,
                },
            ]

        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=fake_fetch_concept_hist,
            fetch_concept_index_ths=fake_fetch_concept_index_ths,
            now_fn=lambda: datetime(2024, 1, 8, 10, 0, 0, tzinfo=timezone.utc),
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 2),
                end_date=date(2024, 1, 5),
                symbols=("CONCEPT:绿色电力",),
            ),
        )

        self.assertEqual(len(concept_hist_calls), 1)
        self.assertEqual(concept_hist_calls[0]["symbol"], "绿色电力")
        self.assertEqual(concept_hist_calls[0]["start_date"], "20240102")
        self.assertEqual(concept_hist_calls[0]["end_date"], "20240105")
        self.assertEqual(concept_hist_calls[0]["period"], "daily")
        self.assertEqual(concept_hist_calls[0]["adjust"], "")
        self.assertEqual(
            concept_index_calls,
            [{"symbol": "绿色电力", "start_date": "20240102", "end_date": "20240105"}],
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["sector_id"], "CONCEPT:绿色电力")
        self.assertEqual(result.normalized_records[0]["trade_date"], "2024-01-03")

    def test_adapter_does_not_mask_non_network_em_errors(self) -> None:
        concept_index_calls: list[dict] = []

        def fake_fetch_concept_hist(**kwargs):
            raise ValueError("bad period")

        def fake_fetch_concept_index_ths(**kwargs):
            concept_index_calls.append(kwargs)
            return []

        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=fake_fetch_concept_hist,
            fetch_concept_index_ths=fake_fetch_concept_index_ths,
        )

        with self.assertRaisesRegex(ValueError, "bad period"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("CONCEPT:绿色电力",),
                ),
            )
        self.assertEqual(concept_index_calls, [])

    def test_adapter_normalizes_prefix_and_whitespace_for_sector_identifier(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [
                {
                    "date": "2024-01-03",
                    "open": 100.0,
                    "high": 101.0,
                    "low": 99.0,
                    "close": 100.5,
                }
            ],
            fetch_concept_hist=lambda **kwargs: [],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=(" industry : 小金属 ",),
            ),
        )
        self.assertEqual(result.normalized_records[0]["sector_id"], "INDUSTRY:小金属")

    def test_adapter_filters_wide_history_locally_when_source_ignores_date_arguments(self) -> None:
        concept_calls: list[dict] = []

        def fake_fetch_concept_hist(symbol):
            concept_calls.append({"symbol": symbol})
            return [
                {"date": "2024-01-01", "open": 1, "high": 2, "low": 1, "close": 2},
                {"date": "2024-01-03", "open": 2, "high": 3, "low": 2, "close": 3},
                {"date": "2024-01-06", "open": 3, "high": 4, "low": 3, "close": 4},
            ]

        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=fake_fetch_concept_hist,
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 2),
                end_date=date(2024, 1, 5),
                symbols=("CONCEPT:绿色电力",),
            ),
        )
        self.assertEqual(concept_calls, [{"symbol": "绿色电力"}])
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["trade_date"], "2024-01-03")

    def test_adapter_only_includes_optional_fields_when_values_are_valid(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [
                {
                    "date": "2024-01-03",
                    "open": "1000",
                    "high": "1020",
                    "low": "990",
                    "close": "1010",
                    "volume": "",
                    "amount": None,
                    "source_ts": " ",
                }
            ],
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("CONCEPT:绿色电力",),
            ),
        )
        record = result.normalized_records[0]
        self.assertNotIn("volume", record)
        self.assertNotIn("amount", record)
        self.assertNotIn("source_ts", record)

    def test_adapter_handles_dataframe_like_payload(self) -> None:
        payload = _FakeDataFrame(
            [
                {
                    "date": "20240103",
                    "open": 1000.0,
                    "high": 1020.0,
                    "low": 990.0,
                    "close": 1010.0,
                    "volume": 12345,
                }
            ]
        )
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: payload,
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("CONCEPT:绿色电力",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["trade_date"], "2024-01-03")
        self.assertEqual(result.normalized_records[0]["volume"], 12345.0)

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("CONCEPT:绿色电力",),
                ),
            )

    def test_adapter_rejects_missing_symbols(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(
            ValueError,
            "requires at least one sector identifier, got none",
        ):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_duplicate_sector_identifier_after_normalization(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "Duplicate sector identifier after normalization"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY:小金属", " industry : 小金属 "),
                ),
            )

    def test_adapter_rejects_empty_identifier(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "non-empty string"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("  ",),
                ),
            )

    def test_adapter_rejects_untyped_identifier(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "Expected typed identifier"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("小金属",),
                ),
            )

    def test_adapter_rejects_untyped_stock_like_identifier(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "looks like a stock/ETF instrument code"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_untyped_fund_like_identifier(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "looks like an ETF/fund instrument code"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.OF",),
                ),
            )

    def test_adapter_rejects_untyped_hk_like_identifier(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "looks like a Hong Kong stock code"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_unsupported_identifier_prefix(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "Unsupported sector identifier prefix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("THEME:绿色电力",),
                ),
            )

    def test_adapter_rejects_malformed_identifier_without_name(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "must be non-empty"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY:",),
                ),
            )

    def test_adapter_rejects_malformed_identifier_with_extra_colon(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "must not contain ':'"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("CONCEPT:绿色:电力",),
                ),
            )

    def test_adapter_rejects_typed_stock_like_sector_name(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "sector name looks like a stock/ETF instrument code"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY:600000.SH",),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: {"date": "2024-01-03"},
        )
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("CONCEPT:绿色电力",),
                ),
            )

    def test_adapter_rejects_missing_required_source_field(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [
                {
                    "date": "2024-01-03",
                    "open": 1000.0,
                    "high": 1020.0,
                    "low": 990.0,
                }
            ],
        )
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("CONCEPT:绿色电力",),
                ),
            )

    def test_adapter_rejects_invalid_trade_date_value(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [
                {
                    "date": "2024-13-03",
                    "open": 1000.0,
                    "high": 1020.0,
                    "low": 990.0,
                    "close": 1010.0,
                }
            ],
        )
        with self.assertRaisesRegex(ValueError, "Invalid trade date value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("CONCEPT:绿色电力",),
                ),
            )

    def test_adapter_rejects_invalid_numeric_value(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [
                {
                    "date": "2024-01-03",
                    "open": "bad",
                    "high": 1020.0,
                    "low": 990.0,
                    "close": 1010.0,
                }
            ],
        )
        with self.assertRaisesRegex(ValueError, "Invalid numeric value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("CONCEPT:绿色电力",),
                ),
            )

    def test_adapter_rejects_invalid_optional_numeric_value(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [
                {
                    "date": "2024-01-03",
                    "open": 1000.0,
                    "high": 1020.0,
                    "low": 990.0,
                    "close": 1010.0,
                    "volume": "bad",
                }
            ],
        )
        with self.assertRaisesRegex(ValueError, "Invalid numeric value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("CONCEPT:绿色电力",),
                ),
            )

    def test_adapter_rejects_invalid_optional_source_ts_value(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [
                {
                    "date": "2024-01-03",
                    "open": 1000.0,
                    "high": 1020.0,
                    "low": 990.0,
                    "close": 1010.0,
                    "source_ts": "not-a-datetime",
                }
            ],
        )
        with self.assertRaisesRegex(ValueError, "Invalid source_ts value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("CONCEPT:绿色电力",),
                ),
            )

    def test_adapter_dedupes_benign_duplicate_rows_deterministically(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [
                {
                    "date": "2024-01-03",
                    "open": 1000.0,
                    "high": 1020.0,
                    "low": 990.0,
                    "close": 1010.0,
                    "source_ts": "2024-01-03T15:00:00",
                },
                {
                    "date": "2024-01-03",
                    "open": 1000.0,
                    "high": 1020.0,
                    "low": 990.0,
                    "close": 1010.0,
                    "source_ts": "2024-01-03T16:00:00",
                },
            ],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("CONCEPT:绿色电力",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["source_ts"], "2024-01-03T16:00:00")

    def test_adapter_rejects_conflicting_duplicate_rows(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [
                {
                    "date": "2024-01-03",
                    "open": 1000.0,
                    "high": 1020.0,
                    "low": 990.0,
                    "close": 1010.0,
                },
                {
                    "date": "2024-01-03",
                    "open": 1001.0,
                    "high": 1020.0,
                    "low": 990.0,
                    "close": 1010.0,
                },
            ],
        )
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate sector daily-bar record"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("CONCEPT:绿色电力",),
                ),
            )

    def test_adapter_fails_batch_when_one_sector_returns_no_rows(self) -> None:
        industry_calls: list[dict] = []
        concept_calls: list[dict] = []

        def fake_fetch_industry_hist(**kwargs):
            industry_calls.append(kwargs)
            return [{"date": "2024-01-03", "open": 1, "high": 2, "low": 1, "close": 2}]

        def fake_fetch_concept_hist(**kwargs):
            concept_calls.append(kwargs)
            return []

        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=fake_fetch_industry_hist,
            fetch_concept_hist=fake_fetch_concept_hist,
        )

        with self.assertRaisesRegex(ValueError, "partial batch results are not allowed"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY:小金属", "CONCEPT:绿色电力"),
                ),
            )

        self.assertEqual(industry_calls, [{"symbol": "小金属", "period": "日k", "adjust": ""}])
        self.assertEqual(concept_calls, [{"symbol": "绿色电力", "period": "daily", "adjust": ""}])

    def test_adapter_rejects_invalid_ohlc_semantics(self) -> None:
        adapter = AkshareSectorDailyBarAdapter(
            fetch_industry_hist=lambda **kwargs: [],
            fetch_concept_hist=lambda **kwargs: [
                {
                    "date": "2024-01-03",
                    "open": 1000.0,
                    "high": 980.0,
                    "low": 990.0,
                    "close": 1010.0,
                }
            ],
        )
        with self.assertRaisesRegex(ValueError, "Invalid OHLC range"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("CONCEPT:绿色电力",),
                ),
            )


if __name__ == "__main__":
    unittest.main()
