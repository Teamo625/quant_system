from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareMarginFinancingLendingAdapter,
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
    fetch_margin_detail_sse=None,
    fetch_margin_detail_szse=None,
    now_fn=None,
) -> AkshareAShareMarginFinancingLendingAdapter:
    return AkshareAShareMarginFinancingLendingAdapter(
        fetch_margin_detail_sse=fetch_margin_detail_sse,
        fetch_margin_detail_szse=fetch_margin_detail_szse,
        now_fn=now_fn,
    )


class AkshareAShareMarginFinancingLendingAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = _build_adapter(
            fetch_margin_detail_sse=lambda **kwargs: [],
            fetch_margin_detail_szse=lambda **kwargs: [],
        )
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_validates_contract_and_offline_only(self) -> None:
        sse_calls: list[dict[str, str]] = []
        now = datetime(2026, 6, 1, 8, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        def fake_fetch_sse(*, date: str):
            sse_calls.append({"date": date})
            if date == "20260529":
                row = {
                    "信用交易日期": "20260529",
                    "标的证券代码": "600000",
                    "融资余额": "1,200",
                    "融资买入额": "120",
                    "融资偿还额": "100",
                    "融券余量": "50",
                    "融券卖出量": "6",
                    "融券偿还量": "5",
                    "source_ts": "2026-05-29T15:30:00",
                }
                return [row, dict(row)]
            if date == "20260528":
                return [
                    {
                        "信用交易日期": "20260528",
                        "标的证券代码": "600000",
                        "融资余额": "1,100",
                        "融资买入额": "110",
                        "融资偿还额": "90",
                        "融券余量": "45",
                        "融券卖出量": "5",
                        "融券偿还量": "4",
                    }
                ]
            return []

        adapter = _build_adapter(
            fetch_margin_detail_sse=fake_fetch_sse,
            fetch_margin_detail_szse=lambda **kwargs: [],
            now_fn=lambda: now,
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MARGIN_FINANCING_LENDING,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 28),
                    end_date=date(2026, 5, 29),
                ),
            )

        self.assertEqual(sse_calls, [{"date": "20260529"}, {"date": "20260528"}])
        self.assertEqual(result.record_count, 2)
        records = list(result.normalized_records)
        self.assertEqual(
            [record["trade_date"] for record in records],
            ["2026-05-28", "2026-05-29"],
        )

        for record in records:
            self.assertEqual(record["symbol"], "600000.SH")
            self.assertEqual(record["market"], "A_SHARE")
            self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
            self.assertEqual(record["ingested_at"], now.isoformat())
            self.assertEqual(record["schema_version"], "v1")
            self.assertEqual(
                registry.validate_record(DatasetName.MARGIN_FINANCING_LENDING, record),
                (),
            )

    def test_adapter_supports_dataframe_like_and_list_payloads(self) -> None:
        szse_calls: list[dict[str, str]] = []

        def fake_fetch_szse(*, date: str):
            szse_calls.append({"date": date})
            return _FakeDataFrame(
                [
                    {
                        "证券代码": "000001",
                        "融资买入额": "220",
                        "融资余额": "2,000",
                        "融券卖出量": "10",
                        "融券余量": "100",
                        "融券余额": "600",
                        "融资融券余额": "2600",
                    }
                ]
            )

        adapter = _build_adapter(
            fetch_margin_detail_sse=lambda **kwargs: [],
            fetch_margin_detail_szse=fake_fetch_szse,
            now_fn=lambda: datetime(2026, 6, 1, 8, 0, 0, tzinfo=timezone.utc),
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.MARGIN_FINANCING_LENDING,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000001.SZ",),
                start_date=date(2026, 5, 29),
                end_date=date(2026, 5, 29),
            ),
        )

        self.assertEqual(szse_calls, [{"date": "20260529"}])
        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["symbol"], "000001.SZ")
        self.assertEqual(record["trade_date"], "2026-05-29")
        self.assertEqual(record["financing_balance"], 2000.0)
        self.assertEqual(record["financing_buy_amount"], 220.0)
        self.assertEqual(record["securities_lending_balance"], 600.0)
        self.assertEqual(record["securities_lending_sell_volume"], 10.0)
        self.assertEqual(record["margin_balance_total"], 2600.0)
        self.assertNotIn("financing_repay_amount", record)

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = _build_adapter(
            fetch_margin_detail_sse=lambda **kwargs: [],
            fetch_margin_detail_szse=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_requires_exactly_one_symbol(self) -> None:
        adapter = _build_adapter(
            fetch_margin_detail_sse=lambda **kwargs: [],
            fetch_margin_detail_szse=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "requires exactly one symbol, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MARGIN_FINANCING_LENDING,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

        with self.assertRaisesRegex(ValueError, "exactly one symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MARGIN_FINANCING_LENDING,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH", "000001.SZ"),
                ),
            )

    def test_adapter_accepts_canonical_prefixed_and_bare_symbols(self) -> None:
        adapter = _build_adapter(
            fetch_margin_detail_sse=lambda **kwargs: [
                {
                    "信用交易日期": "20260529",
                    "标的证券代码": "600000",
                    "融资余额": "1200",
                }
            ],
            fetch_margin_detail_szse=lambda **kwargs: [
                {
                    "证券代码": "000001",
                    "融资余额": "2000",
                }
            ],
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
                    dataset=DatasetName.MARGIN_FINANCING_LENDING,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=(raw_symbol,),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )
            if result.record_count == 0 and canonical.endswith(".BJ"):
                continue
            self.assertEqual(result.normalized_records[0]["symbol"], canonical)

    def test_adapter_rejects_invalid_hk_etf_index_and_malformed_symbols(self) -> None:
        adapter = _build_adapter(
            fetch_margin_detail_sse=lambda **kwargs: [],
            fetch_margin_detail_szse=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "Unsupported symbol market suffix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MARGIN_FINANCING_LENDING,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "ETF or fund symbol is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MARGIN_FINANCING_LENDING,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.SH",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Index symbol is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MARGIN_FINANCING_LENDING,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("399001.SZ",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "market-code combination"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MARGIN_FINANCING_LENDING,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000001.SH",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Unsupported symbol format"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MARGIN_FINANCING_LENDING,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("BAD_SYMBOL",),
                ),
            )

    def test_adapter_rejects_invalid_trade_date(self) -> None:
        adapter = _build_adapter(
            fetch_margin_detail_sse=lambda **kwargs: [
                {
                    "信用交易日期": "2026-13-29",
                    "标的证券代码": "600000",
                    "融资余额": "1000",
                }
            ],
            fetch_margin_detail_szse=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "Invalid trade_date value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MARGIN_FINANCING_LENDING,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_adapter_rejects_invalid_numeric_values(self) -> None:
        adapter = _build_adapter(
            fetch_margin_detail_sse=lambda **kwargs: [
                {
                    "信用交易日期": "20260529",
                    "标的证券代码": "600000",
                    "融资余额": "bad-number",
                }
            ],
            fetch_margin_detail_szse=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "Invalid financing_balance value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MARGIN_FINANCING_LENDING,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_adapter_rejects_conflicting_duplicate_rows(self) -> None:
        adapter = _build_adapter(
            fetch_margin_detail_sse=lambda **kwargs: [
                {
                    "信用交易日期": "20260529",
                    "标的证券代码": "600000",
                    "融资余额": "1000",
                },
                {
                    "信用交易日期": "20260529",
                    "标的证券代码": "600000",
                    "融资余额": "1001",
                },
            ],
            fetch_margin_detail_szse=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "Conflicting duplicate A-share margin financing/lending row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MARGIN_FINANCING_LENDING,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape_and_non_mapping_rows(self) -> None:
        bad_shape_adapter = _build_adapter(
            fetch_margin_detail_sse=lambda **kwargs: {"bad": "shape"},
            fetch_margin_detail_szse=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                bad_shape_adapter,
                SourceRequest(
                    dataset=DatasetName.MARGIN_FINANCING_LENDING,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

        bad_row_adapter = _build_adapter(
            fetch_margin_detail_sse=lambda **kwargs: ["bad-row"],
            fetch_margin_detail_szse=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                bad_row_adapter,
                SourceRequest(
                    dataset=DatasetName.MARGIN_FINANCING_LENDING,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_adapter_rejects_missing_required_source_fields(self) -> None:
        adapter = _build_adapter(
            fetch_margin_detail_sse=lambda **kwargs: [
                {
                    "信用交易日期": "20260529",
                    "融资余额": "1000",
                }
            ],
            fetch_margin_detail_szse=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MARGIN_FINANCING_LENDING,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_date_filtering_returns_empty_when_no_match(self) -> None:
        adapter = _build_adapter(
            fetch_margin_detail_sse=lambda **kwargs: [
                {
                    "信用交易日期": "20260528",
                    "标的证券代码": "600000",
                    "融资余额": "1000",
                }
            ],
            fetch_margin_detail_szse=lambda **kwargs: [],
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.MARGIN_FINANCING_LENDING,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
                start_date=date(2026, 5, 29),
                end_date=date(2026, 5, 29),
            ),
        )
        self.assertEqual(result.record_count, 0)


if __name__ == "__main__":
    unittest.main()
