from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    MACRO_POLICY_SOURCE_ID,
    AkshareChinaMacroAdapter,
    is_akshare_macro_live_environment_unavailable,
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


class AkshareChinaMacroAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = AkshareChinaMacroAdapter(
            fetch_cpi_yearly=lambda: [],
            fetch_ppi_yearly=lambda: [],
            fetch_gdp_yearly=lambda: [],
        )
        self.assertIsInstance(adapter, SourceAdapter)

    def test_macro_indicator_master_records_are_stable_and_contract_valid(self) -> None:
        now = datetime(2024, 1, 12, 10, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()
        adapter = AkshareChinaMacroAdapter(now_fn=lambda: now)

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MACRO_INDICATOR_MASTER,
                    source_name=MACRO_POLICY_SOURCE_ID,
                ),
            )

        self.assertEqual(result.record_count, 11)
        by_id = {record["indicator_id"]: record for record in result.normalized_records}
        self.assertEqual(
            set(by_id),
            {
                "CPI_CN_YOY",
                "PPI_CN_YOY",
                "GDP_CN_YOY",
                "M2_CN_YOY",
                "PMI_CN",
                "EXPORTS_CN_YOY",
                "IMPORTS_CN_YOY",
                "CPI_US_YOY",
                "PPI_US_YOY",
                "CPI_EU_YOY",
                "GDP_EU_YOY",
            },
        )

        self.assertEqual(by_id["CPI_CN_YOY"]["indicator_name"], "China CPI YoY")
        self.assertEqual(by_id["CPI_CN_YOY"]["frequency"], "monthly")
        self.assertEqual(by_id["CPI_CN_YOY"]["category"], "inflation")

        self.assertEqual(by_id["PPI_CN_YOY"]["indicator_name"], "China PPI YoY")
        self.assertEqual(by_id["PPI_CN_YOY"]["frequency"], "monthly")
        self.assertEqual(by_id["PPI_CN_YOY"]["category"], "inflation")

        self.assertEqual(by_id["GDP_CN_YOY"]["indicator_name"], "China GDP YoY")
        self.assertEqual(by_id["GDP_CN_YOY"]["frequency"], "quarterly")
        self.assertEqual(by_id["GDP_CN_YOY"]["category"], "growth")
        self.assertEqual(by_id["CPI_US_YOY"]["region"], "US")
        self.assertEqual(by_id["CPI_EU_YOY"]["region"], "EU")
        self.assertEqual(by_id["PMI_CN"]["unit"], "index")

        for record in result.normalized_records:
            self.assertEqual(record["source"], MACRO_POLICY_SOURCE_ID)
            self.assertEqual(record["schema_version"], "v1")
            self.assertEqual(record["ingested_at"], now.isoformat())
            self.assertEqual(
                registry.validate_record(DatasetName.MACRO_INDICATOR_MASTER, record),
                (),
            )

    def test_macro_indicator_master_supports_requested_indicator_subset(self) -> None:
        adapter = AkshareChinaMacroAdapter()
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.MACRO_INDICATOR_MASTER,
                source_name=MACRO_POLICY_SOURCE_ID,
                symbols=("ppi_cn_yoy", "GDP_CN_YOY"),
            ),
        )
        self.assertEqual(result.record_count, 2)
        self.assertEqual(
            [record["indicator_id"] for record in result.normalized_records],
            ["PPI_CN_YOY", "GDP_CN_YOY"],
        )

    def test_macro_observations_normalize_and_validate_from_list_and_dataframe(self) -> None:
        now = datetime(2024, 1, 12, 10, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        adapter = AkshareChinaMacroAdapter(
            fetch_cpi_yearly=lambda: [
                {
                    "日期": "2024-01-10",
                    "今值": "0.2%",
                    "release_date": "2024-01-12",
                    "source_ts": "2024-01-12 09:30:00",
                    "is_preliminary": "true",
                }
            ],
            fetch_ppi_yearly=lambda: _FakeDataFrame(
                [
                    {
                        "date": "20240210",
                        "value": 0.1,
                        "is_preliminary": 0,
                    }
                ]
            ),
            fetch_gdp_yearly=lambda: [],
            now_fn=lambda: now,
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.MACRO_OBSERVATIONS,
                source_name=MACRO_POLICY_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 2)
        by_indicator_id = {
            record["indicator_id"]: record for record in result.normalized_records
        }

        cpi_record = by_indicator_id["CPI_CN_YOY"]
        self.assertEqual(cpi_record["observation_date"], "2024-01-10")
        self.assertEqual(cpi_record["value"], 0.2)
        self.assertEqual(cpi_record["release_date"], "2024-01-12")
        self.assertEqual(cpi_record["is_preliminary"], True)
        self.assertEqual(cpi_record["source_ts"], "2024-01-12T09:30:00")

        ppi_record = by_indicator_id["PPI_CN_YOY"]
        self.assertEqual(ppi_record["observation_date"], "2024-02-10")
        self.assertEqual(ppi_record["value"], 0.1)
        self.assertEqual(ppi_record["is_preliminary"], False)

        for record in result.normalized_records:
            self.assertEqual(record["region"], "CN")
            self.assertEqual(record["source"], MACRO_POLICY_SOURCE_ID)
            self.assertEqual(record["schema_version"], "v1")
            self.assertEqual(record["ingested_at"], now.isoformat())
            self.assertEqual(
                registry.validate_record(DatasetName.MACRO_OBSERVATIONS, record),
                (),
            )

    def test_macro_observations_filter_by_date_range(self) -> None:
        adapter = AkshareChinaMacroAdapter(
            fetch_cpi_yearly=lambda: [
                {"日期": "2024-01-10", "今值": "0.2"},
                {"日期": "2024-02-10", "今值": "0.3"},
            ],
            fetch_ppi_yearly=lambda: [{"日期": "2024-03-10", "今值": "0.4"}],
            fetch_gdp_yearly=lambda: [],
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.MACRO_OBSERVATIONS,
                source_name=MACRO_POLICY_SOURCE_ID,
                start_date=date(2024, 2, 1),
                end_date=date(2024, 2, 29),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["indicator_id"], "CPI_CN_YOY")
        self.assertEqual(result.normalized_records[0]["observation_date"], "2024-02-10")

    def test_macro_observations_support_requested_indicator_subset(self) -> None:
        adapter = AkshareChinaMacroAdapter(
            fetch_cpi_yearly=lambda: [{"日期": "2024-01-10", "今值": "0.2"}],
            fetch_ppi_yearly=lambda: [{"日期": "2024-02-10", "今值": "0.3"}],
            fetch_gdp_yearly=lambda: [{"日期": "2024-03-31", "今值": "5.1"}],
            now_fn=lambda: datetime(2024, 1, 12, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.MACRO_OBSERVATIONS,
                source_name=MACRO_POLICY_SOURCE_ID,
                symbols=("gdp_cn_yoy", "CPI_CN_YOY"),
            ),
        )
        self.assertEqual(result.record_count, 2)
        self.assertEqual(
            [record["indicator_id"] for record in result.normalized_records],
            ["CPI_CN_YOY", "GDP_CN_YOY"],
        )

    def test_macro_observations_support_global_release_date_aliases(self) -> None:
        adapter = AkshareChinaMacroAdapter(
            fetch_cpi_yearly=lambda: [],
            fetch_ppi_yearly=lambda: [],
            fetch_gdp_yearly=lambda: [],
            fetch_usa_cpi_yoy=lambda: [
                {
                    "时间": "2024-04-01",
                    "发布日期": "2024-04-10",
                    "现值": "3.5",
                }
            ],
            now_fn=lambda: datetime(2024, 4, 11, 10, 0, 0),
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.MACRO_OBSERVATIONS,
                source_name=MACRO_POLICY_SOURCE_ID,
                symbols=("CPI_US_YOY",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["indicator_id"], "CPI_US_YOY")
        self.assertEqual(record["region"], "US")
        self.assertEqual(record["observation_date"], "2024-04-01")
        self.assertEqual(record["release_date"], "2024-04-10")
        self.assertEqual(record["value"], 3.5)

    def test_adapter_ignores_numeric_chuzhi_field_for_is_preliminary(self) -> None:
        adapter = AkshareChinaMacroAdapter(
            fetch_cpi_yearly=lambda: [{"日期": "2024-01-10", "今值": "0.2", "初值": "0.1"}],
            fetch_ppi_yearly=lambda: [],
            fetch_gdp_yearly=lambda: [],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.MACRO_OBSERVATIONS,
                source_name=MACRO_POLICY_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]
        self.assertEqual(record["indicator_id"], "CPI_CN_YOY")
        self.assertEqual(record["value"], 0.2)
        self.assertNotIn("is_preliminary", record)

    def test_adapter_ignores_numeric_yucezhi_or_yugao_fields_for_is_preliminary(self) -> None:
        adapter = AkshareChinaMacroAdapter(
            fetch_cpi_yearly=lambda: [{"日期": "2024-01-10", "今值": "0.2", "预测值": "0.3"}],
            fetch_ppi_yearly=lambda: [{"日期": "2024-01-11", "今值": "0.4", "预告": 0.6}],
            fetch_gdp_yearly=lambda: [],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.MACRO_OBSERVATIONS,
                source_name=MACRO_POLICY_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 2)
        for record in result.normalized_records:
            self.assertNotIn("is_preliminary", record)

    def test_adapter_keeps_explicit_is_preliminary_behavior(self) -> None:
        adapter = AkshareChinaMacroAdapter(
            fetch_cpi_yearly=lambda: [{"日期": "2024-01-10", "今值": "0.2", "is_preliminary": 1}],
            fetch_ppi_yearly=lambda: [],
            fetch_gdp_yearly=lambda: [],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.MACRO_OBSERVATIONS,
                source_name=MACRO_POLICY_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["is_preliminary"], True)

    def test_adapter_rejects_duplicate_normalized_macro_symbol(self) -> None:
        adapter = AkshareChinaMacroAdapter(
            fetch_cpi_yearly=lambda: [],
            fetch_ppi_yearly=lambda: [],
            fetch_gdp_yearly=lambda: [],
        )
        with self.assertRaisesRegex(ValueError, "Duplicate macro indicator symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MACRO_OBSERVATIONS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                    symbols=("cpi_cn_yoy", "CPI_CN_YOY"),
                ),
            )

    def test_adapter_rejects_blank_macro_symbol(self) -> None:
        adapter = AkshareChinaMacroAdapter()
        with self.assertRaisesRegex(ValueError, "must be a non-empty string"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MACRO_OBSERVATIONS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                    symbols=(" ",),
                ),
            )

    def test_adapter_rejects_stock_like_macro_symbol(self) -> None:
        adapter = AkshareChinaMacroAdapter()
        with self.assertRaisesRegex(ValueError, "stock/ETF/fund market symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MACRO_OBSERVATIONS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_hk_stock_like_macro_symbol(self) -> None:
        adapter = AkshareChinaMacroAdapter()
        with self.assertRaisesRegex(ValueError, "Hong Kong stock symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MACRO_OBSERVATIONS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_policy_route_like_macro_symbol(self) -> None:
        adapter = AkshareChinaMacroAdapter()
        with self.assertRaisesRegex(ValueError, "policy-document route selector"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MACRO_OBSERVATIONS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                    symbols=("zhengcelibrary_gw",),
                ),
            )

    def test_adapter_rejects_unsupported_macro_symbol(self) -> None:
        adapter = AkshareChinaMacroAdapter()
        with self.assertRaisesRegex(ValueError, "Unsupported macro indicator symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MACRO_OBSERVATIONS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                    symbols=("M3_CN_YOY",),
                ),
            )

    def test_adapter_rejects_invalid_date_window(self) -> None:
        adapter = AkshareChinaMacroAdapter(
            fetch_cpi_yearly=lambda: [],
            fetch_ppi_yearly=lambda: [],
            fetch_gdp_yearly=lambda: [],
        )
        with self.assertRaisesRegex(ValueError, "Invalid SourceRequest date range"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MACRO_OBSERVATIONS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                    start_date=date(2024, 2, 1),
                    end_date=date(2024, 1, 1),
                ),
            )

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = AkshareChinaMacroAdapter(
            fetch_cpi_yearly=lambda: [],
            fetch_ppi_yearly=lambda: [],
            fetch_gdp_yearly=lambda: [],
        )
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_missing_required_fields(self) -> None:
        adapter = AkshareChinaMacroAdapter(
            fetch_cpi_yearly=lambda: [{"今值": "0.2"}],
            fetch_ppi_yearly=lambda: [],
            fetch_gdp_yearly=lambda: [],
        )
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MACRO_OBSERVATIONS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_invalid_observation_date(self) -> None:
        adapter = AkshareChinaMacroAdapter(
            fetch_cpi_yearly=lambda: [{"日期": "2024-13-10", "今值": "0.2"}],
            fetch_ppi_yearly=lambda: [],
            fetch_gdp_yearly=lambda: [],
        )
        with self.assertRaisesRegex(ValueError, "Invalid observation_date value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MACRO_OBSERVATIONS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_invalid_numeric_value(self) -> None:
        adapter = AkshareChinaMacroAdapter(
            fetch_cpi_yearly=lambda: [{"日期": "2024-01-10", "今值": "bad-value"}],
            fetch_ppi_yearly=lambda: [],
            fetch_gdp_yearly=lambda: [],
        )
        with self.assertRaisesRegex(ValueError, "Invalid numeric value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MACRO_OBSERVATIONS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_invalid_optional_bool_value(self) -> None:
        adapter = AkshareChinaMacroAdapter(
            fetch_cpi_yearly=lambda: [
                {"日期": "2024-01-10", "今值": "0.2", "is_preliminary": "maybe"}
            ],
            fetch_ppi_yearly=lambda: [],
            fetch_gdp_yearly=lambda: [],
        )
        with self.assertRaisesRegex(ValueError, "Invalid is_preliminary value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MACRO_OBSERVATIONS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                ),
            )

    def test_adapter_dedupes_exact_duplicates_and_prefers_latest_source_ts(self) -> None:
        adapter = AkshareChinaMacroAdapter(
            fetch_cpi_yearly=lambda: [
                {
                    "日期": "2024-01-10",
                    "今值": "0.2",
                    "source_ts": "2024-01-10 09:30:00",
                },
                {
                    "日期": "2024-01-10",
                    "今值": "0.2",
                    "source_ts": "2024-01-10 09:35:00",
                },
            ],
            fetch_ppi_yearly=lambda: [],
            fetch_gdp_yearly=lambda: [],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.MACRO_OBSERVATIONS,
                source_name=MACRO_POLICY_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(
            result.normalized_records[0]["source_ts"],
            "2024-01-10T09:35:00",
        )

    def test_adapter_rejects_conflicting_duplicate_rows(self) -> None:
        adapter = AkshareChinaMacroAdapter(
            fetch_cpi_yearly=lambda: [
                {"日期": "2024-01-10", "今值": "0.2"},
                {"日期": "2024-01-10", "今值": "0.3"},
            ],
            fetch_ppi_yearly=lambda: [],
            fetch_gdp_yearly=lambda: [],
        )
        with self.assertRaisesRegex(
            ValueError,
            "Conflicting duplicate macro observation row detected",
        ):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MACRO_OBSERVATIONS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_malformed_payload_shape(self) -> None:
        adapter = AkshareChinaMacroAdapter(
            fetch_cpi_yearly=lambda: {"日期": "2024-01-10", "今值": "0.2"},
            fetch_ppi_yearly=lambda: [],
            fetch_gdp_yearly=lambda: [],
        )
        with self.assertRaisesRegex(ValueError, "payload must be DataFrame-like or list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MACRO_OBSERVATIONS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_non_mapping_payload_row(self) -> None:
        adapter = AkshareChinaMacroAdapter(
            fetch_cpi_yearly=lambda: [1],
            fetch_ppi_yearly=lambda: [],
            fetch_gdp_yearly=lambda: [],
        )
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MACRO_OBSERVATIONS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                ),
            )

    def test_adapter_returns_empty_result_for_exactly_empty_upstream_payload(self) -> None:
        adapter = AkshareChinaMacroAdapter(
            fetch_cpi_yearly=lambda: [],
            fetch_ppi_yearly=lambda: _FakeDataFrame([]),
            fetch_gdp_yearly=lambda: [],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.MACRO_OBSERVATIONS,
                source_name=MACRO_POLICY_SOURCE_ID,
            ),
        )
        self.assertEqual(result.record_count, 0)
        self.assertEqual(tuple(result.normalized_records), ())

    def test_adapter_fails_requested_batch_when_one_indicator_has_no_usable_rows(self) -> None:
        adapter = AkshareChinaMacroAdapter(
            fetch_cpi_yearly=lambda: [{"日期": "2024-01-10", "今值": "0.2"}],
            fetch_ppi_yearly=lambda: [],
            fetch_gdp_yearly=lambda: [],
        )
        with self.assertRaisesRegex(ValueError, "yielded no usable rows"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MACRO_OBSERVATIONS,
                    source_name=MACRO_POLICY_SOURCE_ID,
                    symbols=("CPI_CN_YOY", "PPI_CN_YOY"),
                ),
            )


class AkshareChinaMacroLiveEnvironmentTests(unittest.TestCase):
    def test_live_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        self.assertTrue(
            is_akshare_macro_live_environment_unavailable(
                OSError(111, "connection refused to eastmoney upstream")
            )
        )

    def test_live_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        self.assertFalse(
            is_akshare_macro_live_environment_unavailable(
                ValueError("Unsupported macro indicator symbol 'BAD'")
            )
        )


if __name__ == "__main__":
    unittest.main()
