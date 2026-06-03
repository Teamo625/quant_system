from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareSuspensionResumptionAdapter,
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
    fetch_suspension_resumption=None,
    now_fn=None,
) -> AkshareAShareSuspensionResumptionAdapter:
    return AkshareAShareSuspensionResumptionAdapter(
        fetch_suspension_resumption=fetch_suspension_resumption,
        now_fn=now_fn,
    )


class AkshareAShareSuspensionResumptionAdapterTests(unittest.TestCase):
    def test_unavailable_classifier_does_not_treat_route_signature_errors_as_unavailable(
        self,
    ) -> None:
        adapter = _build_adapter(fetch_suspension_resumption=lambda **kwargs: [])
        self.assertFalse(
            adapter._is_suspension_resumption_route_unavailable(  # pylint: disable=protected-access
                RuntimeError(
                    "AKShare A-share suspension/resumption route does not accept required "
                    "argument: route=stock_tfp_em, field=date"
                )
            )
        )

    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = _build_adapter(fetch_suspension_resumption=lambda **kwargs: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_sorts_deduplicates_and_validates_offline_only(
        self,
    ) -> None:
        calls: list[dict[str, str]] = []
        now = datetime(2026, 6, 1, 8, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        def fake_fetch_suspension_resumption(**kwargs):
            calls.append(dict(kwargs))
            return [
                {
                    "代码": "000001",
                    "名称": "平安银行",
                    "停牌时间": "2026-05-29",
                    "停牌截止时间": "2026-05-29",
                    "停牌期限": "停牌一天",
                    "停牌原因": "刊登重要公告",
                    "所属市场": "深交所主板",
                    "预计复牌时间": date(2026, 5, 30),
                    "source_ts": "2026-05-29 09:00:00",
                },
                {
                    "代码": "000001",
                    "名称": "平安银行",
                    "停牌时间": "2026-05-29",
                    "停牌截止时间": "2026-05-29",
                    "停牌期限": "停牌一天",
                    "停牌原因": "刊登重要公告",
                    "所属市场": "深交所主板",
                    "预计复牌时间": date(2026, 5, 30),
                    "source_ts": "2026-05-29 09:30:00",
                },
                {
                    "代码": "600000",
                    "停牌时间": date(2026, 5, 28),
                    "停牌截止时间": date(2026, 6, 2),
                    "停牌期限": "继续停牌",
                    "停牌原因": "重大资产重组",
                    "所属市场": "上交所主板",
                },
                {
                    "代码": "200706",
                    "停牌时间": "2026-05-29",
                    "停牌期限": "停牌一天",
                    "停牌原因": "B股样本",
                    "所属市场": "深交所主板",
                },
            ]

        adapter = _build_adapter(
            fetch_suspension_resumption=fake_fetch_suspension_resumption,
            now_fn=lambda: now,
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SUSPENSION_RESUMPTION_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000001.SZ", "600000.SH"),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

        self.assertEqual(calls, [{"date": "20260529"}])
        self.assertEqual(result.record_count, 2)

        records = list(result.normalized_records)
        self.assertEqual(
            [(r["event_date"], r["symbol"], r["event_type"]) for r in records],
            sorted((r["event_date"], r["symbol"], r["event_type"]) for r in records),
        )

        continued = next(r for r in records if r["symbol"] == "600000.SH")
        temporary = next(r for r in records if r["symbol"] == "000001.SZ")

        self.assertEqual(temporary["market"], "A_SHARE")
        self.assertEqual(temporary["event_type"], "temporary_suspension")
        self.assertEqual(temporary["start_date"], "2026-05-29")
        self.assertEqual(temporary["end_date"], "2026-05-29")
        self.assertEqual(temporary["reason"], "刊登重要公告")
        self.assertEqual(temporary["raw_status"], "停牌一天")
        self.assertEqual(temporary["exchange"], "SZSE")
        self.assertEqual(temporary["board"], "main_board")
        self.assertEqual(temporary["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(temporary["ingested_at"], now.isoformat())
        self.assertEqual(temporary["schema_version"], "v1")
        self.assertEqual(temporary["source_ts"], "2026-05-29T09:30:00")

        self.assertEqual(continued["market"], "A_SHARE")
        self.assertEqual(continued["event_type"], "continued_suspension")
        self.assertEqual(continued["start_date"], "2026-05-28")
        self.assertEqual(continued["end_date"], "2026-06-02")
        self.assertEqual(continued["exchange"], "SSE")
        self.assertEqual(continued["board"], "main_board")
        self.assertNotIn("source_ts", continued)

        for record in records:
            self.assertEqual(
                registry.validate_record(DatasetName.SUSPENSION_RESUMPTION_EVENTS, record),
                (),
            )

    def test_adapter_supports_dataframe_like_and_list_payloads(self) -> None:
        adapter = _build_adapter(
            fetch_suspension_resumption=lambda **kwargs: _FakeDataFrame(
                [
                    {
                        "代码": "000001",
                        "停牌时间": "2026-05-29",
                        "停牌期限": "停牌一天",
                    }
                ]
            ),
            now_fn=lambda: datetime(2026, 6, 1, 8, 0, 0, tzinfo=timezone.utc),
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SUSPENSION_RESUMPTION_EVENTS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000001.SZ",),
                start_date=date(2026, 5, 29),
                end_date=date(2026, 5, 29),
            ),
        )
        self.assertEqual(result.record_count, 1)

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = _build_adapter(fetch_suspension_resumption=lambda **kwargs: [])

        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_adapter_requires_one_bounded_trade_date(self) -> None:
        adapter = _build_adapter(fetch_suspension_resumption=lambda **kwargs: [])

        with self.assertRaisesRegex(ValueError, "requires bounded trade_date"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SUSPENSION_RESUMPTION_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

        with self.assertRaisesRegex(ValueError, "requires both start_date and end_date"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SUSPENSION_RESUMPTION_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 29),
                ),
            )

        with self.assertRaisesRegex(ValueError, "supports exactly one trade_date"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SUSPENSION_RESUMPTION_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 28),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_adapter_accepts_canonical_prefixed_and_bare_symbols(self) -> None:
        adapter = _build_adapter(
            fetch_suspension_resumption=lambda **kwargs: [
                {"代码": "600000", "停牌时间": "2026-05-29", "停牌期限": "停牌一天"},
                {"代码": "000001", "停牌时间": "2026-05-29", "停牌期限": "停牌一天"},
                {"代码": "430047", "停牌时间": "2026-05-29", "停牌期限": "停牌一天"},
            ]
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
                    dataset=DatasetName.SUSPENSION_RESUMPTION_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=(raw_symbol,),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )
            self.assertEqual(result.record_count, 1)
            self.assertEqual(result.normalized_records[0]["symbol"], canonical)

    def test_adapter_rejects_invalid_hk_etf_index_and_malformed_symbols(self) -> None:
        adapter = _build_adapter(fetch_suspension_resumption=lambda **kwargs: [])

        with self.assertRaisesRegex(ValueError, "Unsupported symbol market suffix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SUSPENSION_RESUMPTION_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

        with self.assertRaisesRegex(ValueError, "ETF or fund symbol is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SUSPENSION_RESUMPTION_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.SH",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Index symbol is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SUSPENSION_RESUMPTION_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("399001.SZ",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Unsupported symbol format"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SUSPENSION_RESUMPTION_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("ABC",),
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_status_mapping_is_conservative_and_ambiguous_text_is_preserved(self) -> None:
        adapter = _build_adapter(
            fetch_suspension_resumption=lambda **kwargs: [
                {
                    "代码": "600000",
                    "停牌时间": "2026-05-28",
                    "停牌截止时间": "2026-05-30",
                    "停牌期限": "复牌",
                    "预计复牌时间": "2026-05-30",
                },
                {
                    "代码": "000001",
                    "停牌时间": "2026-05-29",
                    "停牌期限": "待定",
                },
            ]
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SUSPENSION_RESUMPTION_EVENTS,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2026, 5, 29),
                end_date=date(2026, 5, 29),
            ),
        )

        records = list(result.normalized_records)
        resumption = next(r for r in records if r["symbol"] == "600000.SH")
        ambiguous = next(r for r in records if r["symbol"] == "000001.SZ")

        self.assertEqual(resumption["event_type"], "resumption")
        self.assertEqual(resumption["event_date"], "2026-05-30")
        self.assertEqual(ambiguous["event_type"], "suspension")
        self.assertEqual(ambiguous["raw_status"], "待定")

    def test_optional_fields_remain_source_truth_based(self) -> None:
        adapter = _build_adapter(
            fetch_suspension_resumption=lambda **kwargs: [
                {
                    "代码": "600000",
                    "停牌时间": "2026-05-29",
                }
            ]
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SUSPENSION_RESUMPTION_EVENTS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
                start_date=date(2026, 5, 29),
                end_date=date(2026, 5, 29),
            ),
        )

        record = result.normalized_records[0]
        self.assertNotIn("end_date", record)
        self.assertNotIn("reason", record)
        self.assertNotIn("raw_status", record)
        self.assertNotIn("exchange", record)
        self.assertNotIn("board", record)
        self.assertNotIn("source_ts", record)

    def test_invalid_dates_and_missing_required_fields_fail_clearly(self) -> None:
        adapter = _build_adapter(
            fetch_suspension_resumption=lambda **kwargs: [
                {"代码": "600000", "停牌时间": "2026/05/29", "停牌期限": "停牌一天"}
            ]
        )

        with self.assertRaisesRegex(ValueError, "Invalid start_date value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SUSPENSION_RESUMPTION_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

        missing_field_adapter = _build_adapter(
            fetch_suspension_resumption=lambda **kwargs: [{"代码": "600000", "停牌期限": "停牌一天"}]
        )
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                missing_field_adapter,
                SourceRequest(
                    dataset=DatasetName.SUSPENSION_RESUMPTION_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_malformed_payloads_fail_clearly(self) -> None:
        adapter = _build_adapter(fetch_suspension_resumption=lambda **kwargs: {"代码": "600000"})

        with self.assertRaisesRegex(ValueError, "payload must be DataFrame-like or list\\[Mapping\\]"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SUSPENSION_RESUMPTION_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )

    def test_route_signature_compatibility_errors_are_hard_failures(self) -> None:
        def incompatible_fetch(*, trade_day: str):
            return []

        adapter = _build_adapter(fetch_suspension_resumption=incompatible_fetch)

        with self.assertRaisesRegex(RuntimeError, "does not accept required argument"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SUSPENSION_RESUMPTION_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    start_date=date(2026, 5, 29),
                    end_date=date(2026, 5, 29),
                ),
            )


if __name__ == "__main__":
    unittest.main()
