from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareSectorMembershipAdapter,
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


class AkshareSectorMembershipAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [],
            fetch_concept_cons=lambda **kwargs: [],
        )
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_membership_records(self) -> None:
        industry_calls: list[dict] = []
        registry = DatasetRegistry()
        now = datetime(2024, 1, 12, 10, 0, 0, tzinfo=timezone.utc)

        def fake_fetch_industry_cons(**kwargs):
            industry_calls.append(kwargs)
            return [
                {
                    "代码": "600000",
                    "名称": "浦发银行",
                    "纳入日期": "20200102",
                    "剔除日期": "",
                    "更新时间": "2024-01-12 09:31:00",
                }
            ]

        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=fake_fetch_industry_cons,
            fetch_concept_cons=lambda **kwargs: [],
            now_fn=lambda: now,
        )
        request = SourceRequest(
            dataset=DatasetName.SECTOR_MEMBERSHIP,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("INDUSTRY:小金属",),
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

        self.assertEqual(industry_calls, [{"symbol": "小金属"}])
        self.assertEqual(result.record_count, 1)

        record = result.normalized_records[0]
        self.assertEqual(record["sector_id"], "INDUSTRY:小金属")
        self.assertEqual(record["symbol"], "600000.SH")
        self.assertEqual(record["market"], "CN_A")
        self.assertEqual(record["in_date"], "2020-01-02")
        self.assertNotIn("out_date", record)
        self.assertEqual(record["source_ts"], "2024-01-12T09:31:00")
        self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(record["schema_version"], "v1")
        self.assertEqual(record["ingested_at"], now.isoformat())
        self.assertEqual(
            registry.validate_record(DatasetName.SECTOR_MEMBERSHIP, record),
            (),
        )

    def test_adapter_routes_concept_membership(self) -> None:
        concept_calls: list[dict] = []

        def fake_fetch_concept_cons(**kwargs):
            concept_calls.append(kwargs)
            return [{"代码": "000001"}]

        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [],
            fetch_concept_cons=fake_fetch_concept_cons,
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_MEMBERSHIP,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("concept:绿色电力",),
            ),
        )

        self.assertEqual(concept_calls, [{"symbol": "绿色电力"}])
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["sector_id"], "CONCEPT:绿色电力")
        self.assertEqual(result.normalized_records[0]["symbol"], "000001.SZ")

    def test_adapter_supports_multi_sector_batch_requests(self) -> None:
        industry_calls: list[dict] = []
        concept_calls: list[dict] = []
        registry = DatasetRegistry()

        def fake_fetch_industry_cons(**kwargs):
            industry_calls.append(kwargs)
            return [
                {
                    "代码": "600000",
                    "纳入日期": "20210103",
                    "更新时间": "2024-01-12 09:31:00",
                }
            ]

        def fake_fetch_concept_cons(**kwargs):
            concept_calls.append(kwargs)
            return [
                {
                    "代码": "000001",
                    "纳入日期": "20200102",
                }
            ]

        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=fake_fetch_industry_cons,
            fetch_concept_cons=fake_fetch_concept_cons,
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_MEMBERSHIP,
                source_name=AKSHARE_SOURCE_ID,
                symbols=(" industry : 小金属 ", "concept:绿色电力"),
            ),
        )

        self.assertEqual(industry_calls, [{"symbol": "小金属"}])
        self.assertEqual(concept_calls, [{"symbol": "绿色电力"}])
        self.assertEqual(result.record_count, 2)
        self.assertEqual(
            [record["sector_id"] for record in result.normalized_records],
            ["CONCEPT:绿色电力", "INDUSTRY:小金属"],
        )
        self.assertEqual(
            [record["symbol"] for record in result.normalized_records],
            ["000001.SZ", "600000.SH"],
        )
        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.SECTOR_MEMBERSHIP, record),
                (),
            )

    def test_adapter_falls_back_to_ths_membership_when_primary_network_unavailable(self) -> None:
        def fake_fetch_industry_cons(**kwargs):
            raise OSError("proxy connect failed for push2.eastmoney.com")

        ths_page = """
        <table class="m-table m-pager-table">
            <tbody>
                <tr>
                    <td>1</td>
                    <td><a href="http://stockpage.10jqka.com.cn/000001/" target="_blank">000001</a></td>
                    <td><a href="http://stockpage.10jqka.com.cn/000001" target="_blank">平安银行</a></td>
                </tr>
                <tr>
                    <td>2</td>
                    <td><a href="https://stockpage.10jqka.com.cn/600000/" target="_blank">600000</a></td>
                    <td><a href="https://stockpage.10jqka.com.cn/600000" target="_blank">浦发银行</a></td>
                </tr>
            </tbody>
        </table>
        """

        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=fake_fetch_industry_cons,
            fetch_concept_cons=lambda **kwargs: [],
            fetch_industry_list_ths=lambda: [{"name": "小金属", "code": "881170"}],
            fetch_concept_list_ths=lambda: [],
            fetch_ths_detail_page=lambda url: ths_page,
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_MEMBERSHIP,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("INDUSTRY:小金属",),
            ),
        )

        self.assertEqual(result.record_count, 2)
        self.assertEqual(
            [item["symbol"] for item in result.normalized_records],
            ["000001.SZ", "600000.SH"],
        )
        self.assertEqual(result.normalized_records[0]["sector_id"], "INDUSTRY:小金属")
        self.assertEqual(result.normalized_records[0]["in_date"], "1900-01-01")

    def test_extract_ths_membership_rows_dedupes_by_code(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [],
            fetch_concept_cons=lambda **kwargs: [],
        )
        ths_page = """
        <tr>
            <td><a href="http://stockpage.10jqka.com.cn/000001/" target="_blank">000001</a></td>
            <td><a href="http://stockpage.10jqka.com.cn/000001" target="_blank">平安银行</a></td>
        </tr>
        <tr>
            <td><a href="http://stockpage.10jqka.com.cn/000001/" target="_blank">000001</a></td>
            <td><a href="http://stockpage.10jqka.com.cn/000001" target="_blank">平安银行</a></td>
        </tr>
        <tr>
            <td><a href="http://stockpage.10jqka.com.cn/600000/" target="_blank">600000</a></td>
            <td><a href="http://stockpage.10jqka.com.cn/600000" target="_blank">浦发银行</a></td>
        </tr>
        """
        rows = adapter._extract_ths_membership_rows(ths_page)
        self.assertEqual(rows, [{"代码": "000001", "名称": "平安银行"}, {"代码": "600000", "名称": "浦发银行"}])

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [],
            fetch_concept_cons=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MASTER,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY:小金属",),
                ),
            )

    def test_adapter_rejects_missing_symbols(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [],
            fetch_concept_cons=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "requires at least one sector identifier, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MEMBERSHIP,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

    def test_adapter_rejects_duplicate_sector_identifier_after_normalization(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [],
            fetch_concept_cons=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "Duplicate sector identifier after normalization"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MEMBERSHIP,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY:小金属", " industry : 小金属 "),
                ),
            )

    def test_adapter_rejects_untyped_identifier(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [],
            fetch_concept_cons=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "Expected typed identifier"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MEMBERSHIP,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("小金属",),
                ),
            )

    def test_adapter_rejects_untyped_stock_like_identifier(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [],
            fetch_concept_cons=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "looks like a stock/ETF instrument code"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MEMBERSHIP,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_untyped_fund_like_identifier(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [],
            fetch_concept_cons=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "looks like an ETF/fund instrument code"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MEMBERSHIP,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.OF",),
                ),
            )

    def test_adapter_rejects_untyped_hk_like_identifier(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [],
            fetch_concept_cons=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "looks like a Hong Kong stock code"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MEMBERSHIP,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_unsupported_identifier_prefix(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [],
            fetch_concept_cons=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "Unsupported sector identifier prefix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MEMBERSHIP,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("THEME:绿色电力",),
                ),
            )

    def test_adapter_rejects_malformed_identifier_without_name(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [],
            fetch_concept_cons=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "must be non-empty"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MEMBERSHIP,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY:",),
                ),
            )

    def test_adapter_rejects_malformed_identifier_with_extra_colon(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [],
            fetch_concept_cons=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "must not contain ':'"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MEMBERSHIP,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("CONCEPT:绿色:电力",),
                ),
            )

    def test_adapter_rejects_typed_stock_like_sector_name(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [],
            fetch_concept_cons=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "sector name looks like a stock/ETF instrument code"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MEMBERSHIP,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY:600000.SH",),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: {"代码": "000001"},
            fetch_concept_cons=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MEMBERSHIP,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY:小金属",),
                ),
            )

    def test_adapter_rejects_non_mapping_payload_row(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [1],
            fetch_concept_cons=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MEMBERSHIP,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY:小金属",),
                ),
            )

    def test_adapter_rejects_missing_required_symbol_field(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [{"名称": "浦发银行"}],
            fetch_concept_cons=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MEMBERSHIP,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY:小金属",),
                ),
            )

    def test_adapter_symbol_normalization_is_stable(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [
                {"代码": "600000"},
                {"代码": "000001"},
                {"代码": "830799"},
            ],
            fetch_concept_cons=lambda **kwargs: [],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_MEMBERSHIP,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("INDUSTRY:小金属",),
            ),
        )
        symbols = {item["symbol"] for item in result.normalized_records}
        self.assertEqual(symbols, {"600000.SH", "000001.SZ", "830799.BJ"})

    def test_adapter_accepts_symbol_with_market_suffix(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [{"代码": "000001.sz"}],
            fetch_concept_cons=lambda **kwargs: [],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_MEMBERSHIP,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("INDUSTRY:小金属",),
            ),
        )
        self.assertEqual(result.normalized_records[0]["symbol"], "000001.SZ")

    def test_adapter_rejects_invalid_symbol_value(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [{"代码": "BAD"}],
            fetch_concept_cons=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "Invalid sector-membership symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MEMBERSHIP,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY:小金属",),
                ),
            )

    def test_adapter_in_date_falls_back_when_missing(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [{"代码": "000001"}],
            fetch_concept_cons=lambda **kwargs: [],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_MEMBERSHIP,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("INDUSTRY:小金属",),
            ),
        )
        self.assertEqual(result.normalized_records[0]["in_date"], "1900-01-01")

    def test_adapter_in_date_and_out_date_parsing(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [
                {
                    "代码": "000001",
                    "纳入日期": "2024-01-02",
                    "剔除日期": "20250103",
                }
            ],
            fetch_concept_cons=lambda **kwargs: [],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_MEMBERSHIP,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("INDUSTRY:小金属",),
            ),
        )
        self.assertEqual(result.normalized_records[0]["in_date"], "2024-01-02")
        self.assertEqual(result.normalized_records[0]["out_date"], "2025-01-03")

    def test_adapter_rejects_invalid_out_date_value(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [{"代码": "000001", "剔除日期": "not-a-date"}],
            fetch_concept_cons=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "Invalid out_date value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MEMBERSHIP,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY:小金属",),
                ),
            )

    def test_adapter_rejects_invalid_optional_source_ts_value(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [{"代码": "000001", "更新时间": "not-a-datetime"}],
            fetch_concept_cons=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(ValueError, "Invalid source_ts value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MEMBERSHIP,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY:小金属",),
                ),
            )

    def test_adapter_omits_optional_fields_when_empty(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [
                {
                    "代码": "000001",
                    "剔除日期": " ",
                    "更新时间": " ",
                }
            ],
            fetch_concept_cons=lambda **kwargs: [],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_MEMBERSHIP,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("INDUSTRY:小金属",),
            ),
        )
        record = result.normalized_records[0]
        self.assertNotIn("out_date", record)
        self.assertNotIn("source_ts", record)

    def test_adapter_dedupes_benign_duplicates_deterministically(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [
                {
                    "代码": "000001",
                    "纳入日期": "2020-01-02",
                    "更新时间": "2024-01-12 09:30:00",
                },
                {
                    "代码": "000001",
                    "纳入日期": "2020-01-02",
                    "更新时间": "2024-01-12 09:31:00",
                },
            ],
            fetch_concept_cons=lambda **kwargs: [],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_MEMBERSHIP,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("INDUSTRY:小金属",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["source_ts"], "2024-01-12T09:31:00")

    def test_adapter_keeps_distinct_historical_membership_windows(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [
                {"代码": "000001", "纳入日期": "2020-01-02", "剔除日期": "2020-06-01"},
                {"代码": "000001", "纳入日期": "2020-06-01", "剔除日期": "2020-12-31"},
            ],
            fetch_concept_cons=lambda **kwargs: [],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_MEMBERSHIP,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("INDUSTRY:小金属",),
            ),
        )
        self.assertEqual(result.record_count, 2)
        self.assertEqual(
            [(record["in_date"], record["out_date"]) for record in result.normalized_records],
            [("2020-01-02", "2020-06-01"), ("2020-06-01", "2020-12-31")],
        )

    def test_adapter_rejects_conflicting_duplicate_rows(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: [
                {"代码": "000001", "纳入日期": "2020-01-02"},
                {"代码": "000001", "纳入日期": "2020-01-03"},
            ],
            fetch_concept_cons=lambda **kwargs: [],
        )
        with self.assertRaisesRegex(
            ValueError,
            "Conflicting duplicate sector membership history window",
        ):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MEMBERSHIP,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY:小金属",),
                ),
            )

    def test_adapter_handles_dataframe_like_payload(self) -> None:
        payload = _FakeDataFrame(
            [
                {
                    "代码": "000001",
                    "纳入日期": "20240102",
                }
            ]
        )
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: payload,
            fetch_concept_cons=lambda **kwargs: [],
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.SECTOR_MEMBERSHIP,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("INDUSTRY:小金属",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["in_date"], "2024-01-02")

    def test_adapter_fails_batch_when_one_sector_returns_no_rows(self) -> None:
        industry_calls: list[dict] = []
        concept_calls: list[dict] = []

        def fake_fetch_industry_cons(**kwargs):
            industry_calls.append(kwargs)
            return [{"代码": "600000"}]

        def fake_fetch_concept_cons(**kwargs):
            concept_calls.append(kwargs)
            return []

        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=fake_fetch_industry_cons,
            fetch_concept_cons=fake_fetch_concept_cons,
        )

        with self.assertRaisesRegex(ValueError, "partial batch results are not allowed"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MEMBERSHIP,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY:小金属", "CONCEPT:绿色电力"),
                ),
            )

        self.assertEqual(industry_calls, [{"symbol": "小金属"}])
        self.assertEqual(concept_calls, [{"symbol": "绿色电力"}])

    def test_adapter_validates_all_identifiers_before_fetching(self) -> None:
        industry_calls: list[dict] = []
        concept_calls: list[dict] = []

        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda **kwargs: industry_calls.append(kwargs) or [],
            fetch_concept_cons=lambda **kwargs: concept_calls.append(kwargs) or [],
        )

        with self.assertRaisesRegex(ValueError, "Unsupported sector identifier prefix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MEMBERSHIP,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY:小金属", "THEME:绿色电力"),
                ),
            )

        self.assertEqual(industry_calls, [])
        self.assertEqual(concept_calls, [])

    def test_adapter_route_signature_incompatibility_is_hard_failure(self) -> None:
        adapter = AkshareSectorMembershipAdapter(
            fetch_industry_cons=lambda code: [],
            fetch_concept_cons=lambda **kwargs: [],
        )

        with self.assertRaisesRegex(
            RuntimeError,
            "route=stock_board_industry_cons_em",
        ):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.SECTOR_MEMBERSHIP,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("INDUSTRY:小金属",),
                ),
            )


if __name__ == "__main__":
    unittest.main()
