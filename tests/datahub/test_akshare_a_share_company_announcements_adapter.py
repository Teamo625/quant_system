from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareCompanyAnnouncementsAdapter,
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
    fetch_individual_notice_report=None,
    fetch_notice_report=None,
    now_fn=None,
    max_route_days=120,
) -> AkshareAShareCompanyAnnouncementsAdapter:
    return AkshareAShareCompanyAnnouncementsAdapter(
        fetch_individual_notice_report=fetch_individual_notice_report,
        fetch_notice_report=fetch_notice_report,
        now_fn=now_fn,
        max_route_days=max_route_days,
    )


class AkshareAShareCompanyAnnouncementsAdapterTests(unittest.TestCase):
    def test_unavailable_classifier_does_not_treat_route_signature_errors_as_unavailable(
        self,
    ) -> None:
        adapter = _build_adapter(fetch_individual_notice_report=lambda **kwargs: [])
        self.assertFalse(
            adapter._is_company_announcements_route_unavailable(  # pylint: disable=protected-access
                RuntimeError(
                    "AKShare A-share company announcements route does not accept required argument: "
                    "route=stock_individual_notice_report, field=security/code"
                )
            )
        )

    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = _build_adapter(fetch_individual_notice_report=lambda **kwargs: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_records_offline_only(self) -> None:
        calls: list[dict[str, str]] = []
        now = datetime(2026, 6, 1, 8, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        def fake_fetch_individual_notice_report(**kwargs):
            calls.append(kwargs)
            return [
                {
                    "代码": "600000",
                    "公告标题": "浦发银行:董事任职资格获核准",
                    "公告类型": "高管人员任职变动",
                    "公告日期": "2026-05-20",
                    "网址": "https://data.eastmoney.com/notices/detail/600000/AN1.html",
                    "source_ts": "2026-05-20 18:00:00",
                },
                {
                    "代码": "600000",
                    "公告标题": "浦发银行:董事任职资格获核准",
                    "公告类型": "高管人员任职变动",
                    "公告日期": "2026-05-20",
                    "网址": "https://data.eastmoney.com/notices/detail/600000/AN1.html",
                    "source_ts": "2026-05-20 18:01:00",
                },
                {
                    "代码": "600000",
                    "公告标题": "浦发银行:董事会决议公告",
                    "公告类型": "董事会决议",
                    "公告日期": date(2026, 5, 21),
                    "网址": "https://data.eastmoney.com/notices/detail/600000/AN2.html",
                    "announcement_id": "AN-600000-20260521",
                },
                {
                    "代码": "000001",
                    "公告标题": "平安银行:无关记录",
                    "公告类型": "一般事项",
                    "公告日期": "2026-05-21",
                },
            ]

        adapter = _build_adapter(
            fetch_individual_notice_report=fake_fetch_individual_notice_report,
            now_fn=lambda: now,
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 20),
                    end_date=date(2026, 5, 21),
                ),
            )

        self.assertEqual(
            calls,
            [
                {
                    "security": "600000",
                    "symbol": "全部",
                    "begin_date": "2026-05-20",
                    "end_date": "2026-05-21",
                }
            ],
        )

        self.assertEqual(result.record_count, 2)
        records = list(result.normalized_records)
        self.assertEqual(
            [(r["publish_time"], r["symbol"], r["announcement_id"]) for r in records],
            sorted(
                [(r["publish_time"], r["symbol"], r["announcement_id"]) for r in records]
            ),
        )

        first = records[0]
        self.assertEqual(first["symbol"], "600000.SH")
        self.assertEqual(first["market"], "A_SHARE")
        self.assertEqual(first["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(first["ingested_at"], now.isoformat())
        self.assertEqual(first["schema_version"], "v1")
        self.assertIn("announcement_type", first)
        self.assertIn("title", first)

        deduped_record = next(
            r for r in records if r["publish_time"] == "2026-05-20T00:00:00"
        )
        self.assertEqual(deduped_record["source_ts"], "2026-05-20T18:01:00")

        explicit_id_record = next(
            r for r in records if r["announcement_id"] == "AN-600000-20260521"
        )
        self.assertEqual(explicit_id_record["publish_time"], "2026-05-21T00:00:00")

        for record in records:
            self.assertEqual(
                registry.validate_record(DatasetName.COMPANY_ANNOUNCEMENTS, record),
                (),
            )

    def test_adapter_supports_dataframe_like_payload(self) -> None:
        adapter = _build_adapter(
            fetch_individual_notice_report=lambda **kwargs: _FakeDataFrame(
                [
                    {
                        "代码": "000001",
                        "公告标题": "平安银行:董事会决议",
                        "公告类型": "董事会决议",
                        "公告日期": "2026-05-30",
                        "网址": "https://data.eastmoney.com/notices/detail/000001/AN3.html",
                    }
                ]
            )
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("000001.SZ",),
                start_date=date(2026, 5, 30),
                end_date=date(2026, 5, 30),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "000001.SZ")

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = _build_adapter(fetch_individual_notice_report=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.NEWS_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_requires_exactly_one_symbol(self) -> None:
        adapter = _build_adapter(fetch_individual_notice_report=lambda **kwargs: [])

        with self.assertRaisesRegex(ValueError, "requires exactly one symbol, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

        with self.assertRaisesRegex(ValueError, "exactly one symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH", "000001.SZ"),
                ),
            )

    def test_adapter_accepts_canonical_prefixed_and_bare_symbols(self) -> None:
        adapter = _build_adapter(
            fetch_individual_notice_report=lambda **kwargs: [
                {
                    "代码": kwargs["security"],
                    "公告标题": "公告A",
                    "公告类型": "一般事项",
                    "公告日期": "2026-05-31",
                }
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
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=(raw_symbol,),
                    start_date=date(2026, 5, 31),
                    end_date=date(2026, 5, 31),
                ),
            )
            self.assertEqual(result.record_count, 1)
            self.assertEqual(result.normalized_records[0]["symbol"], canonical)

    def test_adapter_rejects_invalid_hk_etf_index_and_malformed_symbols(self) -> None:
        adapter = _build_adapter(fetch_individual_notice_report=lambda **kwargs: [])

        with self.assertRaisesRegex(ValueError, "Unsupported symbol market suffix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "ETF or fund symbol is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.SH",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Index symbol is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("399001.SZ",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "market-code combination"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000001.SH",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Unsupported symbol format"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("BAD_SYMBOL",),
                ),
            )

    def test_adapter_rejects_invalid_publish_time(self) -> None:
        adapter = _build_adapter(
            fetch_individual_notice_report=lambda **kwargs: [
                {
                    "代码": "600000",
                    "公告标题": "公告A",
                    "公告类型": "一般事项",
                    "公告日期": "2026-13-01",
                }
            ]
        )

        with self.assertRaisesRegex(ValueError, "Invalid publish_time value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 31),
                    end_date=date(2026, 5, 31),
                ),
            )

    def test_adapter_rejects_conflicting_duplicate_rows(self) -> None:
        adapter = _build_adapter(
            fetch_individual_notice_report=lambda **kwargs: [
                {
                    "announcement_id": "ANN-1",
                    "代码": "600000",
                    "公告标题": "公告A",
                    "公告类型": "一般事项",
                    "公告日期": "2026-05-31",
                    "网址": "https://data.eastmoney.com/notices/detail/600000/1.html",
                },
                {
                    "announcement_id": "ANN-1",
                    "代码": "600000",
                    "公告标题": "公告B",
                    "公告类型": "一般事项",
                    "公告日期": "2026-05-31",
                    "网址": "https://data.eastmoney.com/notices/detail/600000/1.html",
                },
            ]
        )

        with self.assertRaisesRegex(
            ValueError,
            "Conflicting duplicate A-share company announcement row",
        ):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 31),
                    end_date=date(2026, 5, 31),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape_and_non_mapping_rows(self) -> None:
        bad_shape_adapter = _build_adapter(
            fetch_individual_notice_report=lambda **kwargs: {"bad": "shape"}
        )
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                bad_shape_adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 31),
                    end_date=date(2026, 5, 31),
                ),
            )

        bad_row_adapter = _build_adapter(
            fetch_individual_notice_report=lambda **kwargs: ["bad-row"]
        )
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                bad_row_adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 31),
                    end_date=date(2026, 5, 31),
                ),
            )

    def test_adapter_rejects_missing_required_source_fields(self) -> None:
        adapter = _build_adapter(fetch_individual_notice_report=lambda **kwargs: [{"代码": "600000"}])

        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 31),
                    end_date=date(2026, 5, 31),
                ),
            )

    def test_route_signature_compatibility_errors_are_hard_failures(self) -> None:
        def incompatible_fetch(*, code: str):
            return []

        adapter = _build_adapter(fetch_individual_notice_report=incompatible_fetch)

        with self.assertRaisesRegex(
            RuntimeError,
            "does not accept required argument",
        ):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 31),
                    end_date=date(2026, 5, 31),
                ),
            )

    def test_adapter_rejects_too_wide_date_range(self) -> None:
        adapter = _build_adapter(fetch_individual_notice_report=lambda **kwargs: [], max_route_days=5)
        with self.assertRaisesRegex(ValueError, "date range exceeds bounded limit"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2026, 5, 1),
                    end_date=date(2026, 5, 10),
                ),
            )


if __name__ == "__main__":
    unittest.main()
