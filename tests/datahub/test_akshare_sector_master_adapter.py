from datetime import datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareSectorMasterAdapter,
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


class AkshareSectorMasterAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = AkshareSectorMasterAdapter(
            fetch_industry_list=lambda: [],
            fetch_concept_list=lambda: [],
        )
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_sector_master_records(self) -> None:
        industry_calls: list[dict] = []
        concept_calls: list[dict] = []
        registry = DatasetRegistry()
        now = datetime(2024, 1, 12, 10, 0, 0, tzinfo=timezone.utc)

        def fake_fetch_industry_list():
            industry_calls.append({"route": "industry"})
            return [
                {
                    "板块名称": "小金属",
                    "更新时间": "2024-01-12 09:30:00",
                }
            ]

        def fake_fetch_concept_list():
            concept_calls.append({"route": "concept"})
            return _FakeDataFrame(
                [
                    {
                        "name": "绿色电力",
                        "source_ts": "2024-01-12T09:31:00",
                    }
                ]
            )

        adapter = AkshareSectorMasterAdapter(
            fetch_industry_list=fake_fetch_industry_list,
            fetch_concept_list=fake_fetch_concept_list,
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.SECTOR_MASTER,
            source_name=AKSHARE_SOURCE_ID,
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

        self.assertEqual(industry_calls, [{"route": "industry"}])
        self.assertEqual(concept_calls, [{"route": "concept"}])
        self.assertEqual(result.record_count, 2)

        industry_record = result.normalized_records[0]
        self.assertEqual(industry_record["sector_id"], "INDUSTRY:小金属")
        self.assertEqual(industry_record["sector_name"], "小金属")
        self.assertEqual(industry_record["sector_type"], "INDUSTRY")
        self.assertEqual(industry_record["market"], "CN_SECTOR")
        self.assertTrue(industry_record["is_active"])
        self.assertEqual(industry_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(industry_record["schema_version"], "v1")
        self.assertEqual(industry_record["ingested_at"], now.isoformat())
        self.assertEqual(industry_record["source_ts"], "2024-01-12T09:30:00")

        concept_record = result.normalized_records[1]
        self.assertEqual(concept_record["sector_id"], "CONCEPT:绿色电力")
        self.assertEqual(concept_record["sector_type"], "CONCEPT")
        self.assertEqual(concept_record["source_ts"], "2024-01-12T09:31:00")

        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.SECTOR_MASTER, record),
                (),
            )

    def test_adapter_routes_industry_filter_only(self) -> None:
        industry_calls: list[dict] = []
        concept_calls: list[dict] = []

        def fake_fetch_industry_list():
            industry_calls.append({"route": "industry"})
            return [{"板块名称": "小金属"}]

        def fake_fetch_concept_list():
            concept_calls.append({"route": "concept"})
            return [{"板块名称": "绿色电力"}]

        adapter = AkshareSectorMasterAdapter(
            fetch_industry_list=fake_fetch_industry_list,
            fetch_concept_list=fake_fetch_concept_list,
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_MASTER,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("industry",),
            ),
        )

        self.assertEqual(industry_calls, [{"route": "industry"}])
        self.assertEqual(concept_calls, [])
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["sector_id"], "INDUSTRY:小金属")

    def test_adapter_routes_concept_filter_only(self) -> None:
        industry_calls: list[dict] = []
        concept_calls: list[dict] = []

        def fake_fetch_industry_list():
            industry_calls.append({"route": "industry"})
            return [{"板块名称": "小金属"}]

        def fake_fetch_concept_list():
            concept_calls.append({"route": "concept"})
            return [{"板块名称": "绿色电力"}]

        adapter = AkshareSectorMasterAdapter(
            fetch_industry_list=fake_fetch_industry_list,
            fetch_concept_list=fake_fetch_concept_list,
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_MASTER,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("CONCEPT",),
            ),
        )

        self.assertEqual(industry_calls, [])
        self.assertEqual(concept_calls, [{"route": "concept"}])
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["sector_id"], "CONCEPT:绿色电力")

    def test_adapter_falls_back_to_ths_when_em_network_unavailable(self) -> None:
        industry_em_calls: list[dict] = []
        industry_ths_calls: list[dict] = []

        class ProxyError(Exception):
            pass

        def fake_fetch_industry_list():
            industry_em_calls.append({"route": "industry_em"})
            raise ProxyError("Unable to connect to proxy")

        def fake_fetch_industry_list_ths():
            industry_ths_calls.append({"route": "industry_ths"})
            return [{"name": "半导体"}]

        adapter = AkshareSectorMasterAdapter(
            fetch_industry_list=fake_fetch_industry_list,
            fetch_concept_list=lambda: [],
            fetch_industry_list_ths=fake_fetch_industry_list_ths,
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_MASTER,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("INDUSTRY",),
            ),
        )

        self.assertEqual(industry_em_calls, [{"route": "industry_em"}])
        self.assertEqual(industry_ths_calls, [{"route": "industry_ths"}])
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["sector_id"], "INDUSTRY:半导体")

    def test_adapter_does_not_mask_non_network_em_errors(self) -> None:
        industry_ths_calls: list[dict] = []

        def fake_fetch_industry_list():
            raise ValueError("bad sector source payload")

        def fake_fetch_industry_list_ths():
            industry_ths_calls.append({"route": "industry_ths"})
            return [{"name": "半导体"}]

        adapter = AkshareSectorMasterAdapter(
            fetch_industry_list=fake_fetch_industry_list,
            fetch_concept_list=lambda: [],
            fetch_industry_list_ths=fake_fetch_industry_list_ths,
        )

        with self.assertRaisesRegex(ValueError, "bad sector source payload"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY",),
                ),
            )

        self.assertEqual(industry_ths_calls, [])

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = AkshareSectorMasterAdapter(
            fetch_industry_list=lambda: [],
            fetch_concept_list=lambda: [],
        )
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_invalid_symbols_filter_value(self) -> None:
        adapter = AkshareSectorMasterAdapter(
            fetch_industry_list=lambda: [],
            fetch_concept_list=lambda: [],
        )
        with self.assertRaisesRegex(ValueError, "Unsupported sector type filter value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("THEME",),
                ),
            )

    def test_adapter_rejects_multiple_symbols_filter_values(self) -> None:
        adapter = AkshareSectorMasterAdapter(
            fetch_industry_list=lambda: [],
            fetch_concept_list=lambda: [],
        )
        with self.assertRaisesRegex(ValueError, "accepts at most one sector-type filter"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY", "CONCEPT"),
                ),
            )

    def test_adapter_rejects_non_string_symbols_filter_value(self) -> None:
        adapter = AkshareSectorMasterAdapter(
            fetch_industry_list=lambda: [],
            fetch_concept_list=lambda: [],
        )
        with self.assertRaisesRegex(ValueError, "must be a non-empty string"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=(123,),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape(self) -> None:
        adapter = AkshareSectorMasterAdapter(
            fetch_industry_list=lambda: {"板块名称": "小金属"},
            fetch_concept_list=lambda: [],
        )
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY",),
                ),
            )

    def test_adapter_rejects_non_mapping_payload_row(self) -> None:
        adapter = AkshareSectorMasterAdapter(
            fetch_industry_list=lambda: [1],
            fetch_concept_list=lambda: [],
        )
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY",),
                ),
            )

    def test_adapter_rejects_missing_required_source_field(self) -> None:
        adapter = AkshareSectorMasterAdapter(
            fetch_industry_list=lambda: [{"foo": "小金属"}],
            fetch_concept_list=lambda: [],
        )
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY",),
                ),
            )

    def test_adapter_rejects_empty_sector_name(self) -> None:
        adapter = AkshareSectorMasterAdapter(
            fetch_industry_list=lambda: [{"板块名称": "   "}],
            fetch_concept_list=lambda: [],
        )
        with self.assertRaisesRegex(ValueError, "empty string"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY",),
                ),
            )

    def test_adapter_deduplicates_benign_canonical_sector_id_duplicates(self) -> None:
        adapter = AkshareSectorMasterAdapter(
            fetch_industry_list=lambda: [
                {
                    "板块名称": "小金属",
                    "板块代码": "BK1027",
                    "更新时间": "2024-01-12 09:30:00",
                },
                {
                    "板块名称": " 小金属 ",
                    "板块代码": "BK1027",
                    "更新时间": "2024-01-12 09:31:00",
                },
            ],
            fetch_concept_list=lambda: [],
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_MASTER,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("INDUSTRY",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["sector_id"], "INDUSTRY:小金属")
        self.assertEqual(result.normalized_records[0]["source_ts"], "2024-01-12T09:31:00")

    def test_adapter_rejects_conflicting_duplicate_canonical_sector_id(self) -> None:
        adapter = AkshareSectorMasterAdapter(
            fetch_industry_list=lambda: [
                {"板块名称": "小金属", "板块代码": "BK1027"},
                {"板块名称": " 小金属 ", "板块代码": "BK9999"},
            ],
            fetch_concept_list=lambda: [],
        )
        with self.assertRaisesRegex(
            ValueError,
            "Conflicting duplicate canonical sector_id",
        ):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY",),
                ),
            )

    def test_adapter_rejects_invalid_optional_source_ts_value(self) -> None:
        adapter = AkshareSectorMasterAdapter(
            fetch_industry_list=lambda: [
                {
                    "板块名称": "小金属",
                    "更新时间": "not-a-datetime",
                }
            ],
            fetch_concept_list=lambda: [],
        )
        with self.assertRaisesRegex(ValueError, "Invalid source_ts value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY",),
                ),
            )

    def test_adapter_omits_optional_source_ts_when_empty(self) -> None:
        adapter = AkshareSectorMasterAdapter(
            fetch_industry_list=lambda: [{"板块名称": "小金属", "更新时间": " "}],
            fetch_concept_list=lambda: [],
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_MASTER,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("INDUSTRY",),
            ),
        )
        self.assertNotIn("source_ts", result.normalized_records[0])


if __name__ == "__main__":
    unittest.main()
