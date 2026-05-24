from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.hkex import (
    HKEX_SOURCE_ID,
    HkexCompanyAnnouncementsAdapter,
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


class HkexCompanyAnnouncementsAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = HkexCompanyAnnouncementsAdapter(fetch_company_announcements=lambda: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_records(self) -> None:
        now = datetime(2024, 1, 12, 10, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        adapter = HkexCompanyAnnouncementsAdapter(
            fetch_company_announcements=lambda: [
                {
                    "stock_code": "700",
                    "release_time": "22/05/2026 22:57",
                    "headline": "Financial Statements/ESG Information - [Interim/Half-Year Report]",
                    "title": "INTERIM REPORT 2026",
                    "url": "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0522/2026052202350.pdf",
                },
                {
                    "announcement_id": "ANN-001",
                    "symbol": "00005.HK",
                    "publish_time": "2024-01-11",
                    "announcement_type": "general",
                    "title": "Monthly Return",
                    "url": "https://example.com/ann.pdf",
                    "source_ts": "2024-01-11 12:30:00",
                },
            ],
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
                    source_name=HKEX_SOURCE_ID,
                ),
            )

        self.assertEqual(result.record_count, 2)
        by_symbol = {record["symbol"]: record for record in result.normalized_records}

        first = by_symbol["00700.HK"]
        self.assertEqual(first["market"], "HK")
        self.assertEqual(first["source"], HKEX_SOURCE_ID)
        self.assertEqual(first["publish_time"], "2026-05-22T22:57:00")
        self.assertEqual(first["announcement_type"], "financial statements/esg information")
        self.assertEqual(first["title"], "INTERIM REPORT 2026")
        self.assertTrue(first["announcement_id"].startswith("HKEXANN-"))
        self.assertEqual(first["ingested_at"], now.isoformat())
        self.assertEqual(first["schema_version"], "v1")

        second = by_symbol["00005.HK"]
        self.assertEqual(second["announcement_id"], "ANN-001")
        self.assertEqual(second["publish_time"], "2024-01-11T00:00:00")
        self.assertEqual(second["source_ts"], "2024-01-11T12:30:00")

        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.COMPANY_ANNOUNCEMENTS, record),
                (),
            )

    def test_adapter_supports_dataframe_like_payload(self) -> None:
        payload = _FakeDataFrame(
            [
                {
                    "stock_code": "2382",
                    "release_time": "22/05/2026 22:57",
                    "headline": "Results",
                    "title": "Annual Report 2025",
                    "url": "/listedco/listconews/sehk/2026/0522/2026052202316.pdf",
                }
            ]
        )
        adapter = HkexCompanyAnnouncementsAdapter(
            fetch_company_announcements=lambda: payload,
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                source_name=HKEX_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["symbol"], "02382.HK")
        self.assertEqual(record["publish_time"], "2026-05-22T22:57:00")

    def test_adapter_parses_html_payload_rows(self) -> None:
        html_payload = """
        <html><body><table><tbody>
        <tr>
            <td class="release-time"><span>Release Time: </span>22/05/2026 22:57</td>
            <td class="stock-short-code"><span>Stock Code: </span>02175</td>
            <td><div class="headline">Financial Statements/ESG Information - [Interim/Half-Year Report]</div>
                <div class="doc-link"><a href="/listedco/listconews/sehk/2026/0522/2026052202350.pdf">INTERIM REPORT 2026</a></div>
            </td>
        </tr>
        </tbody></table></body></html>
        """
        adapter = HkexCompanyAnnouncementsAdapter(
            fetch_company_announcements=lambda: html_payload,
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                source_name=HKEX_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["symbol"], "02175.HK")
        self.assertEqual(
            record["url"],
            "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0522/2026052202350.pdf",
        )

    def test_adapter_builds_deterministic_announcement_id_when_source_id_missing(
        self,
    ) -> None:
        payload = [
            {
                "stock_code": "700",
                "release_time": "22/05/2026 22:57",
                "headline": "Results",
                "title": "INTERIM REPORT 2026",
                "url": "https://www1.hkexnews.hk/x.pdf",
            }
        ]
        adapter = HkexCompanyAnnouncementsAdapter(
            fetch_company_announcements=lambda: payload,
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        result_one = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                source_name=HKEX_SOURCE_ID,
            ),
        )
        result_two = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                source_name=HKEX_SOURCE_ID,
            ),
        )
        self.assertEqual(
            result_one.normalized_records[0]["announcement_id"],
            result_two.normalized_records[0]["announcement_id"],
        )

    def test_adapter_normalizes_and_filters_symbols(self) -> None:
        adapter = HkexCompanyAnnouncementsAdapter(
            fetch_company_announcements=lambda: [
                {
                    "stock_code": "700",
                    "release_time": "22/05/2026 22:57",
                    "headline": "Results",
                    "title": "INTERIM REPORT 2026",
                    "url": "https://www1.hkexnews.hk/x.pdf",
                },
                {
                    "stock_code": "5",
                    "release_time": "22/05/2026 22:50",
                    "headline": "General",
                    "title": "Monthly Return",
                    "url": "https://www1.hkexnews.hk/y.pdf",
                },
            ],
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        for user_symbol in ("700", "00700", "00700.HK"):
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=HKEX_SOURCE_ID,
                    symbols=(user_symbol,),
                ),
            )
            with self.subTest(symbol=user_symbol):
                self.assertEqual(result.record_count, 1)
                self.assertEqual(result.normalized_records[0]["symbol"], "00700.HK")

    def test_adapter_rejects_prefix_polluted_symbol_filters(self) -> None:
        adapter = HkexCompanyAnnouncementsAdapter(fetch_company_announcements=lambda: [])
        for invalid_symbol in ("foo700", "A700.HK", "00700HK"):
            with self.subTest(symbol=invalid_symbol):
                with self.assertRaisesRegex(ValueError, "Unsupported HK symbol"):
                    fetch_source_result(
                        adapter,
                        SourceRequest(
                            dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                            source_name=HKEX_SOURCE_ID,
                            symbols=(invalid_symbol,),
                        ),
                    )

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = HkexCompanyAnnouncementsAdapter(fetch_company_announcements=lambda: [])
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.NEWS_EVENTS,
                    source_name=HKEX_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_invalid_symbol_filter(self) -> None:
        adapter = HkexCompanyAnnouncementsAdapter(fetch_company_announcements=lambda: [])
        with self.assertRaisesRegex(ValueError, "Unsupported HK symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=HKEX_SOURCE_ID,
                    symbols=("AAPL.US",),
                ),
            )

    def test_adapter_rejects_empty_or_non_string_symbol_filter(self) -> None:
        adapter = HkexCompanyAnnouncementsAdapter(fetch_company_announcements=lambda: [])
        with self.assertRaisesRegex(ValueError, "Invalid HK symbol value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=HKEX_SOURCE_ID,
                    symbols=("",),
                ),
            )
        with self.assertRaisesRegex(ValueError, "Invalid HK symbol value type"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=HKEX_SOURCE_ID,
                    symbols=(700,),  # type: ignore[arg-type]
                ),
            )

    def test_adapter_rejects_malformed_payload_shape(self) -> None:
        adapter = HkexCompanyAnnouncementsAdapter(
            fetch_company_announcements=lambda: {"stock_code": "00700"}
        )
        with self.assertRaisesRegex(ValueError, "payload must be HTML str, DataFrame-like"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=HKEX_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_non_mapping_payload_row(self) -> None:
        adapter = HkexCompanyAnnouncementsAdapter(fetch_company_announcements=lambda: [1])
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=HKEX_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_invalid_publish_time(self) -> None:
        adapter = HkexCompanyAnnouncementsAdapter(
            fetch_company_announcements=lambda: [
                {
                    "stock_code": "00700",
                    "release_time": "2024-13-01",
                    "headline": "General",
                    "title": "Monthly Return",
                    "url": "https://www1.hkexnews.hk/y.pdf",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid publish_time value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=HKEX_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_missing_required_fields(self) -> None:
        adapter = HkexCompanyAnnouncementsAdapter(
            fetch_company_announcements=lambda: [{"stock_code": "00700"}]
        )
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=HKEX_SOURCE_ID,
                ),
            )

    def test_adapter_filters_records_by_date_range(self) -> None:
        adapter = HkexCompanyAnnouncementsAdapter(
            fetch_company_announcements=lambda: [
                {
                    "stock_code": "00700",
                    "release_time": "21/05/2026 22:57",
                    "headline": "General",
                    "title": "Doc A",
                    "url": "https://www1.hkexnews.hk/a.pdf",
                },
                {
                    "stock_code": "00700",
                    "release_time": "22/05/2026 22:57",
                    "headline": "General",
                    "title": "Doc B",
                    "url": "https://www1.hkexnews.hk/b.pdf",
                },
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                source_name=HKEX_SOURCE_ID,
                start_date=date(2026, 5, 22),
                end_date=date(2026, 5, 22),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["title"], "Doc B")

    def test_adapter_skips_rows_without_usable_hk_symbol(self) -> None:
        adapter = HkexCompanyAnnouncementsAdapter(
            fetch_company_announcements=lambda: [
                {
                    "stock_code": "Stock Code:",
                    "release_time": "22/05/2026 22:57",
                    "headline": "General",
                    "title": "Invalid row",
                    "url": "https://www1.hkexnews.hk/invalid.pdf",
                },
                {
                    "stock_code": "00700",
                    "release_time": "22/05/2026 22:58",
                    "headline": "General",
                    "title": "Valid row",
                    "url": "https://www1.hkexnews.hk/valid.pdf",
                },
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                source_name=HKEX_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "00700.HK")

    def test_adapter_accepts_label_prefixed_stock_code_in_source_row(self) -> None:
        adapter = HkexCompanyAnnouncementsAdapter(
            fetch_company_announcements=lambda: [
                {
                    "stock_code": "Stock Code: 00700",
                    "release_time": "22/05/2026 22:57",
                    "headline": "General",
                    "title": "Label-prefixed row",
                    "url": "https://www1.hkexnews.hk/label.pdf",
                }
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                source_name=HKEX_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["symbol"], "00700.HK")

    def test_adapter_dedupes_benign_duplicates(self) -> None:
        adapter = HkexCompanyAnnouncementsAdapter(
            fetch_company_announcements=lambda: [
                {
                    "announcement_id": "ANN-XYZ",
                    "stock_code": "00700",
                    "release_time": "22/05/2026 22:57",
                    "headline": "General",
                    "title": "Doc",
                    "url": "https://www1.hkexnews.hk/a.pdf",
                    "source_ts": "2026-05-22 23:01:00",
                },
                {
                    "announcement_id": "ANN-XYZ",
                    "stock_code": "00700",
                    "release_time": "22/05/2026 22:57",
                    "headline": "General",
                    "title": "Doc",
                    "url": "https://www1.hkexnews.hk/a.pdf",
                    "source_ts": "2026-05-22 23:02:00",
                },
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                source_name=HKEX_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(
            result.normalized_records[0]["source_ts"],
            "2026-05-22T23:02:00",
        )

    def test_adapter_rejects_conflicting_duplicates(self) -> None:
        adapter = HkexCompanyAnnouncementsAdapter(
            fetch_company_announcements=lambda: [
                {
                    "announcement_id": "ANN-XYZ",
                    "stock_code": "00700",
                    "release_time": "22/05/2026 22:57",
                    "headline": "General",
                    "title": "Doc A",
                    "url": "https://www1.hkexnews.hk/a.pdf",
                },
                {
                    "announcement_id": "ANN-XYZ",
                    "stock_code": "00700",
                    "release_time": "22/05/2026 22:57",
                    "headline": "General",
                    "title": "Doc B",
                    "url": "https://www1.hkexnews.hk/a.pdf",
                },
            ]
        )
        with self.assertRaisesRegex(
            ValueError,
            "Conflicting duplicate company announcement row",
        ):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
                    source_name=HKEX_SOURCE_ID,
                ),
            )


if __name__ == "__main__":
    unittest.main()
