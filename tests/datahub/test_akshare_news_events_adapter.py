from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import AKSHARE_SOURCE_ID, AkshareNewsEventsAdapter
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceAdapter, SourceRequest, fetch_source_result


class _FakeDataFrame:
    def __init__(self, records):
        self._records = list(records)

    def to_dict(self, orient="records"):
        if orient != "records":
            raise ValueError("Only orient='records' is supported in test fixture.")
        return list(self._records)


class AkshareNewsEventsAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = AkshareNewsEventsAdapter(fetch_news_events=lambda: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_records(self) -> None:
        now = datetime(2024, 1, 12, 10, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        adapter = AkshareNewsEventsAdapter(
            fetch_news_events=lambda: [
                {
                    "发布时间": "2024-01-11 09:31:00",
                    "内容": "苹果发布新品，市场反应积极，相关供应链受关注。",
                    "source_name": "新华网",
                    "related_symbol": "aapl.us",
                    "url": "https://example.com/news/1",
                    "source_ts": "2024-01-11 09:35:00",
                },
                {
                    "publish_time": "2024-01-11",
                    "title": "港股科技板块走强",
                    "summary": "市场风险偏好回升。",
                    "source_name": "财联社",
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
                    dataset=DatasetName.NEWS_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

        self.assertEqual(result.record_count, 2)

        by_source_name = {
            record["source_name"]: record for record in result.normalized_records
        }

        cl_record = by_source_name["财联社"]
        self.assertEqual(cl_record["region"], "GLOBAL")
        self.assertEqual(cl_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(cl_record["publish_time"], "2024-01-11T00:00:00")
        self.assertEqual(cl_record["title"], "港股科技板块走强")
        self.assertEqual(cl_record["summary"], "市场风险偏好回升。")
        self.assertEqual(cl_record["ingested_at"], now.isoformat())
        self.assertEqual(cl_record["schema_version"], "v1")

        xh_record = by_source_name["新华网"]
        self.assertEqual(xh_record["related_symbol"], "AAPL.US")
        self.assertEqual(xh_record["source_ts"], "2024-01-11T09:35:00")
        self.assertEqual(xh_record["publish_time"], "2024-01-11T09:31:00")

        for record in result.normalized_records:
            self.assertEqual(registry.validate_record(DatasetName.NEWS_EVENTS, record), ())

    def test_adapter_builds_deterministic_news_id_when_source_id_missing(self) -> None:
        payload = [
            {
                "发布时间": "2024-01-11 09:31:00",
                "内容": "全球风险资产走强，市场关注后续政策动向。",
                "source_name": "路透",
                "url": "https://example.com/news/2",
            }
        ]
        adapter = AkshareNewsEventsAdapter(
            fetch_news_events=lambda: payload,
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        result_one = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.NEWS_EVENTS,
                source_name=AKSHARE_SOURCE_ID,
            ),
        )
        result_two = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.NEWS_EVENTS,
                source_name=AKSHARE_SOURCE_ID,
            ),
        )

        self.assertEqual(result_one.record_count, 1)
        self.assertEqual(result_two.record_count, 1)
        self.assertEqual(
            result_one.normalized_records[0]["news_id"],
            result_two.normalized_records[0]["news_id"],
        )
        self.assertTrue(result_one.normalized_records[0]["news_id"].startswith("AKNEWS-"))

    def test_adapter_supports_dataframe_like_payload(self) -> None:
        payload = _FakeDataFrame(
            [
                {
                    "发布时间": "2024-01-11 09:31:00",
                    "内容": "市场波动加剧，资金分歧明显。",
                }
            ]
        )
        adapter = AkshareNewsEventsAdapter(
            fetch_news_events=lambda: payload,
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.NEWS_EVENTS,
                source_name=AKSHARE_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(
            result.normalized_records[0]["publish_time"],
            "2024-01-11T09:31:00",
        )

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = AkshareNewsEventsAdapter(fetch_news_events=lambda: [])
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_symbol_filter_for_selected_route(self) -> None:
        adapter = AkshareNewsEventsAdapter(fetch_news_events=lambda: [])
        with self.assertRaisesRegex(ValueError, "does not support symbol filters"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.NEWS_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("AAPL.US",),
                ),
            )

    def test_adapter_parses_date_only_publish_time_to_midnight(self) -> None:
        adapter = AkshareNewsEventsAdapter(
            fetch_news_events=lambda: [
                {"date": "20240111", "title": "测试新闻", "source_name": "测试源"}
            ],
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.NEWS_EVENTS,
                source_name=AKSHARE_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["publish_time"], "2024-01-11T00:00:00")

    def test_adapter_filters_by_date_range(self) -> None:
        adapter = AkshareNewsEventsAdapter(
            fetch_news_events=lambda: [
                {"date": "2024-01-10", "title": "旧新闻", "source_name": "测试源"},
                {"date": "2024-01-11", "title": "新新闻", "source_name": "测试源"},
            ],
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.NEWS_EVENTS,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 11),
                end_date=date(2024, 1, 11),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["title"], "新新闻")

    def test_adapter_rejects_malformed_payload_shape(self) -> None:
        adapter = AkshareNewsEventsAdapter(
            fetch_news_events=lambda: {"发布时间": "2024-01-11 09:31:00", "内容": "x"}
        )
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.NEWS_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_non_mapping_payload_row(self) -> None:
        adapter = AkshareNewsEventsAdapter(fetch_news_events=lambda: [1])
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.NEWS_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_invalid_publish_time(self) -> None:
        adapter = AkshareNewsEventsAdapter(
            fetch_news_events=lambda: [
                {"发布时间": "2024-13-11", "title": "测试新闻", "source_name": "测试源"}
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid publish_time value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.NEWS_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_missing_title_and_summary(self) -> None:
        adapter = AkshareNewsEventsAdapter(
            fetch_news_events=lambda: [{"发布时间": "2024-01-11 09:31:00"}]
        )
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.NEWS_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_dedupes_benign_duplicates_using_latest_source_ts(self) -> None:
        adapter = AkshareNewsEventsAdapter(
            fetch_news_events=lambda: [
                {
                    "news_id": "N-001",
                    "发布时间": "2024-01-11 09:31:00",
                    "title": "重复新闻",
                    "source_name": "测试源",
                    "source_ts": "2024-01-11 09:33:00",
                },
                {
                    "news_id": "N-001",
                    "发布时间": "2024-01-11 09:31:00",
                    "title": "重复新闻",
                    "source_name": "测试源",
                    "source_ts": "2024-01-11 09:35:00",
                },
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.NEWS_EVENTS,
                source_name=AKSHARE_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["source_ts"], "2024-01-11T09:35:00")

    def test_adapter_rejects_conflicting_duplicate_rows(self) -> None:
        adapter = AkshareNewsEventsAdapter(
            fetch_news_events=lambda: [
                {
                    "news_id": "N-002",
                    "发布时间": "2024-01-11 09:31:00",
                    "title": "新闻A",
                    "source_name": "测试源",
                },
                {
                    "news_id": "N-002",
                    "发布时间": "2024-01-11 09:31:00",
                    "title": "新闻B",
                    "source_name": "测试源",
                },
            ]
        )
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate news event row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.NEWS_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_invalid_optional_field_type(self) -> None:
        adapter = AkshareNewsEventsAdapter(
            fetch_news_events=lambda: [
                {
                    "发布时间": "2024-01-11 09:31:00",
                    "title": "测试新闻",
                    "source_name": "测试源",
                    "summary": 1,
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid summary value type"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.NEWS_EVENTS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )


if __name__ == "__main__":
    unittest.main()
