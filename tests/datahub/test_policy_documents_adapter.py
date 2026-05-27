from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.policy import MacroPolicyDocumentsAdapter
from quant.datahub.adapters.akshare import MACRO_POLICY_SOURCE_ID
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceAdapter, SourceRequest, fetch_source_result


class _FakeDataFrame:
    def __init__(self, records):
        self._records = list(records)

    def to_dict(self, orient="records"):
        if orient != "records":
            raise ValueError("Only orient='records' is supported in test fixture.")
        return list(self._records)


class MacroPolicyDocumentsAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = MacroPolicyDocumentsAdapter(fetch_policy_documents=lambda **kwargs: [])
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_records(self) -> None:
        now = datetime(2026, 5, 27, 12, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        def fake_fetch_policy_documents(**kwargs):
            route_t = kwargs["route_t"]
            if route_t == "zhengcelibrary_gw":
                return {
                    "searchVO": {
                        "listVO": [
                            {
                                "id": "GW-001",
                                "title": "国务院关于测试事项的通知",
                                "puborg": "国务院",
                                "pubtime": 1779267600000,
                                "ptime": 1779267700000,
                                "summary": "用于离线适配器测试。",
                                "url": "https://www.gov.cn/example-1",
                            }
                        ]
                    }
                }
            return {
                "searchVO": {
                    "listVO": [
                        {
                            "id": "BM-001",
                            "title": "国家发展改革委关于测试事项的通知",
                            "puborg": "国家发展改革委",
                            "pubtime": "2026-05-20",
                            "summary": "用于离线适配器测试。",
                            "url": "https://www.gov.cn/example-2",
                        }
                    ]
                }
            }

        adapter = MacroPolicyDocumentsAdapter(
            fetch_policy_documents=fake_fetch_policy_documents,
            now_fn=lambda: now,
            max_records_per_route=5,
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.POLICY_DOCUMENTS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                ),
            )

        self.assertEqual(result.record_count, 2)
        by_id = {record["policy_id"]: record for record in result.normalized_records}
        self.assertIn("GOVCN-GW-001", by_id)
        self.assertIn("GOVCN-BM-001", by_id)

        gw_record = by_id["GOVCN-GW-001"]
        self.assertEqual(gw_record["region"], "CN")
        self.assertEqual(gw_record["publish_date"], "2026-05-20")
        self.assertEqual(gw_record["authority"], "国务院")
        self.assertEqual(gw_record["document_type"], "国务院文件")
        self.assertEqual(gw_record["source"], MACRO_POLICY_SOURCE_ID)
        self.assertEqual(gw_record["schema_version"], "v1")
        self.assertEqual(gw_record["ingested_at"], now.isoformat())
        self.assertEqual(gw_record["source_ts"], "2026-05-20T09:01:40")

        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.POLICY_DOCUMENTS, record),
                (),
            )

    def test_adapter_supports_dataframe_like_payload(self) -> None:
        def fake_fetch_policy_documents(**kwargs):
            route_t = kwargs["route_t"]
            if route_t == "zhengcelibrary_gw":
                return _FakeDataFrame(
                    [
                        {
                            "id": "GW-DF-1",
                            "title": "国务院办公厅关于测试A的通知",
                            "puborg": "国务院办公厅",
                            "pubtime": "20260518",
                            "url": "https://www.gov.cn/example-a",
                        }
                    ]
                )
            return []

        adapter = MacroPolicyDocumentsAdapter(
            fetch_policy_documents=fake_fetch_policy_documents,
            now_fn=lambda: datetime(2026, 5, 27, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.POLICY_DOCUMENTS,
                source_name=MACRO_POLICY_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["publish_date"], "2026-05-18")

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = MacroPolicyDocumentsAdapter(fetch_policy_documents=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_symbol_filters(self) -> None:
        adapter = MacroPolicyDocumentsAdapter(fetch_policy_documents=lambda **kwargs: [])
        with self.assertRaisesRegex(ValueError, "does not support symbol filters"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.POLICY_DOCUMENTS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                    symbols=("POLICY-001",),
                ),
            )

    def test_adapter_filters_by_date_range(self) -> None:
        def fake_fetch_policy_documents(**kwargs):
            route_t = kwargs["route_t"]
            if route_t == "zhengcelibrary_gw":
                return [
                    {
                        "id": "GW-OLD",
                        "title": "旧文件",
                        "puborg": "国务院",
                        "pubtime": "2026-05-18",
                    },
                    {
                        "id": "GW-NEW",
                        "title": "新文件",
                        "puborg": "国务院",
                        "pubtime": "2026-05-20",
                    },
                ]
            return []

        adapter = MacroPolicyDocumentsAdapter(
            fetch_policy_documents=fake_fetch_policy_documents,
            now_fn=lambda: datetime(2026, 5, 27, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.POLICY_DOCUMENTS,
                source_name=MACRO_POLICY_SOURCE_ID,
                start_date=date(2026, 5, 19),
                end_date=date(2026, 5, 20),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["policy_id"], "GOVCN-GW-NEW")

    def test_adapter_builds_deterministic_policy_id_when_source_id_missing(self) -> None:
        payload = [
            {
                "title": "国家发展改革委关于测试事项B的通知",
                "puborg": "国家发展改革委",
                "pubtime": "2026-05-20",
                "url": "https://www.gov.cn/example-b",
            }
        ]

        def fake_fetch_policy_documents(**kwargs):
            route_t = kwargs["route_t"]
            if route_t == "zhengcelibrary_bm":
                return payload
            return []

        adapter = MacroPolicyDocumentsAdapter(
            fetch_policy_documents=fake_fetch_policy_documents,
            now_fn=lambda: datetime(2026, 5, 27, 10, 0, 0),
        )
        result_one = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.POLICY_DOCUMENTS,
                source_name=MACRO_POLICY_SOURCE_ID,
            ),
        )
        result_two = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.POLICY_DOCUMENTS,
                source_name=MACRO_POLICY_SOURCE_ID,
            ),
        )
        self.assertEqual(result_one.record_count, 1)
        self.assertEqual(result_two.record_count, 1)
        self.assertEqual(
            result_one.normalized_records[0]["policy_id"],
            result_two.normalized_records[0]["policy_id"],
        )
        self.assertTrue(
            result_one.normalized_records[0]["policy_id"].startswith("GOVPOL-")
        )

    def test_adapter_omits_empty_optional_fields(self) -> None:
        def fake_fetch_policy_documents(**kwargs):
            route_t = kwargs["route_t"]
            if route_t == "zhengcelibrary_gw":
                return [
                    {
                        "id": "GW-OPT-1",
                        "title": "国务院关于测试可选字段的通知",
                        "puborg": "国务院",
                        "pubtime": "2026-05-20",
                        "summary": "   ",
                        "url": "",
                    }
                ]
            return []

        adapter = MacroPolicyDocumentsAdapter(
            fetch_policy_documents=fake_fetch_policy_documents,
            now_fn=lambda: datetime(2026, 5, 27, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.POLICY_DOCUMENTS,
                source_name=MACRO_POLICY_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertNotIn("summary", record)
        self.assertNotIn("url", record)

    def test_adapter_rejects_missing_required_field(self) -> None:
        def fake_fetch_policy_documents(**kwargs):
            route_t = kwargs["route_t"]
            if route_t == "zhengcelibrary_gw":
                return [{"id": "GW-MISS", "puborg": "国务院", "pubtime": "2026-05-20"}]
            return []

        adapter = MacroPolicyDocumentsAdapter(fetch_policy_documents=fake_fetch_policy_documents)
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.POLICY_DOCUMENTS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_invalid_publish_date(self) -> None:
        def fake_fetch_policy_documents(**kwargs):
            route_t = kwargs["route_t"]
            if route_t == "zhengcelibrary_gw":
                return [
                    {
                        "id": "GW-BAD-DATE",
                        "title": "国务院关于测试日期的通知",
                        "puborg": "国务院",
                        "pubtime": "2026-13-20",
                    }
                ]
            return []

        adapter = MacroPolicyDocumentsAdapter(fetch_policy_documents=fake_fetch_policy_documents)
        with self.assertRaisesRegex(ValueError, "Invalid publish_date value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.POLICY_DOCUMENTS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_invalid_required_string(self) -> None:
        def fake_fetch_policy_documents(**kwargs):
            route_t = kwargs["route_t"]
            if route_t == "zhengcelibrary_bm":
                return [
                    {
                        "id": "BM-BLANK-AUTH",
                        "title": "国家发展改革委关于测试事项的通知",
                        "puborg": "   ",
                        "pubtime": "2026-05-20",
                    }
                ]
            return []

        adapter = MacroPolicyDocumentsAdapter(fetch_policy_documents=fake_fetch_policy_documents)
        with self.assertRaisesRegex(ValueError, "Invalid authority value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.POLICY_DOCUMENTS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_malformed_payload_shape(self) -> None:
        adapter = MacroPolicyDocumentsAdapter(
            fetch_policy_documents=lambda **kwargs: "invalid-payload"
        )
        with self.assertRaisesRegex(ValueError, "payload must be DataFrame-like"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.POLICY_DOCUMENTS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_non_mapping_payload_row(self) -> None:
        def fake_fetch_policy_documents(**kwargs):
            route_t = kwargs["route_t"]
            if route_t == "zhengcelibrary_gw":
                return [1]
            return []

        adapter = MacroPolicyDocumentsAdapter(fetch_policy_documents=fake_fetch_policy_documents)
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.POLICY_DOCUMENTS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                ),
            )

    def test_adapter_dedupes_benign_duplicates_using_latest_source_ts(self) -> None:
        def fake_fetch_policy_documents(**kwargs):
            route_t = kwargs["route_t"]
            if route_t == "zhengcelibrary_gw":
                return [
                    {
                        "id": "GW-DUP",
                        "title": "国务院关于重复文件的通知",
                        "puborg": "国务院",
                        "pubtime": "2026-05-20",
                        "ptime": "2026-05-20T09:00:00",
                    },
                    {
                        "id": "GW-DUP",
                        "title": "国务院关于重复文件的通知",
                        "puborg": "国务院",
                        "pubtime": "2026-05-20",
                        "ptime": "2026-05-20T10:00:00",
                    },
                ]
            return []

        adapter = MacroPolicyDocumentsAdapter(fetch_policy_documents=fake_fetch_policy_documents)
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.POLICY_DOCUMENTS,
                source_name=MACRO_POLICY_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["source_ts"], "2026-05-20T10:00:00")

    def test_adapter_rejects_conflicting_duplicate_rows(self) -> None:
        def fake_fetch_policy_documents(**kwargs):
            route_t = kwargs["route_t"]
            if route_t == "zhengcelibrary_gw":
                return [
                    {
                        "id": "GW-CONFLICT",
                        "title": "国务院关于文件A的通知",
                        "puborg": "国务院",
                        "pubtime": "2026-05-20",
                    },
                    {
                        "id": "GW-CONFLICT",
                        "title": "国务院关于文件B的通知",
                        "puborg": "国务院",
                        "pubtime": "2026-05-20",
                    },
                ]
            return []

        adapter = MacroPolicyDocumentsAdapter(fetch_policy_documents=fake_fetch_policy_documents)
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate policy document row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.POLICY_DOCUMENTS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                ),
            )


if __name__ == "__main__":
    unittest.main()
