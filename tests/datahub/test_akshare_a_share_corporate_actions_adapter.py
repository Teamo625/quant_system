from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareCorporateActionsAdapter,
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
    fetch_dividend_cninfo=None,
    fetch_dividend_detail=None,
    fetch_rights_issue_cninfo=None,
    fetch_rights_issue_detail=None,
    now_fn=None,
) -> AkshareAShareCorporateActionsAdapter:
    if fetch_rights_issue_cninfo is None:
        if fetch_rights_issue_detail is None:
            fetch_rights_issue_cninfo = lambda **kwargs: []
        else:
            fetch_rights_issue_cninfo = (
                lambda **kwargs: (_ for _ in ()).throw(OSError(111, "connection refused"))
            )
    return AkshareAShareCorporateActionsAdapter(
        fetch_dividend_cninfo=fetch_dividend_cninfo or (lambda **kwargs: []),
        fetch_dividend_detail=fetch_dividend_detail or (lambda **kwargs: []),
        fetch_rights_issue_cninfo=fetch_rights_issue_cninfo,
        fetch_rights_issue_detail=fetch_rights_issue_detail or (lambda **kwargs: []),
        now_fn=now_fn,
    )


class AkshareAShareCorporateActionsAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = _build_adapter()
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_corporate_actions(self) -> None:
        calls: list[dict[str, str]] = []
        now = datetime(2024, 7, 1, 10, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        def fake_fetch_dividend_cninfo(**kwargs):
            calls.append(kwargs)
            return _FakeDataFrame(
                [
                    {
                        "实施方案公告日期": "2024-05-01",
                        "分红类型": "年度分红",
                        "送股比例": 1.5,
                        "转增比例": 0,
                        "派息比例": "2.3",
                        "股权登记日": "2024-05-10",
                        "除权日": "2024-05-11",
                        "实施方案分红说明": "10派2.3元(含税)",
                        "报告时间": "2023年报",
                    }
                ]
            )

        adapter = _build_adapter(
            fetch_dividend_cninfo=fake_fetch_dividend_cninfo,
            now_fn=lambda: now,
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
                fetched_at=datetime(2024, 7, 1, 10, 5, 0, tzinfo=timezone.utc),
            )

        self.assertEqual(calls, [{"symbol": "600000"}])
        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]

        self.assertEqual(record["symbol"], "600000.SH")
        self.assertEqual(record["market"], "CN")
        self.assertEqual(record["event_date"], "2024-05-11")
        self.assertEqual(record["event_type"], "dividend")
        self.assertEqual(record["action_family"], "dividend_distribution")
        self.assertEqual(record["source_route"], "stock_dividend_cninfo")
        self.assertEqual(record["announcement_date"], "2024-05-01")
        self.assertEqual(record["record_date"], "2024-05-10")
        self.assertEqual(record["ex_date"], "2024-05-11")
        self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(record["schema_version"], "v1")
        self.assertEqual(record["ingested_at"], now.isoformat())
        self.assertEqual(record["source_ts"], "2024-05-01T00:00:00")
        self.assertTrue(str(record["raw_payload_ref"]).startswith("AKCA|600000.SH|dividend|2024-05-11|"))

        value = record["value"]
        self.assertEqual(value["action_family"], "dividend_distribution")
        self.assertEqual(value["source_route"], "stock_dividend_cninfo")
        self.assertEqual(value["ratio_base"], "per_10_shares")
        self.assertEqual(value["cash_currency"], "CNY")
        self.assertEqual(value["cash_dividend_per_10_shares"], 2.3)
        self.assertEqual(value["bonus_share_ratio_per_10_shares"], 1.5)
        self.assertEqual(value["transfer_share_ratio_per_10_shares"], 0.0)
        self.assertEqual(value["distribution_components"], ["cash_dividend", "bonus_share"])
        self.assertEqual(value["dividend_type"], "年度分红")
        self.assertEqual(value["report_period"], "2023年报")
        self.assertEqual(value["plan_explanation"], "10派2.3元(含税)")
        self.assertEqual(value["record_date"], "2024-05-10")
        self.assertEqual(value["ex_date"], "2024-05-11")

        self.assertEqual(
            registry.validate_record(DatasetName.CORPORATE_ACTIONS, record),
            (),
        )

    def test_fetch_source_result_combines_dividend_and_rights_issue_taxonomy(self) -> None:
        now = datetime(2024, 7, 1, 10, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        adapter = _build_adapter(
            fetch_dividend_cninfo=lambda **kwargs: [
                {
                    "实施方案公告日期": "2024-05-01",
                    "分红类型": "年度分红",
                    "送股比例": 1.5,
                    "转增比例": 0,
                    "派息比例": "2.3",
                    "股权登记日": "2024-05-10",
                    "除权日": "2024-05-11",
                    "实施方案分红说明": "10派2.3元(含税)",
                    "报告时间": "2023年报",
                }
            ],
            fetch_rights_issue_cninfo=lambda **kwargs: [
                {
                    "公告日期": "2010-10-11",
                    "配股比例": 1.5,
                    "配股价格": 5.69,
                    "配股前总股本": 74518.4,
                    "除权基准日": "2010-10-22",
                    "股权登记日": "2010-10-13",
                    "配股缴款起始日": "2010-10-14",
                    "配股缴款截止日": "2010-10-20",
                    "配股上市日": "2010-10-29",
                    "实际募资总额": 61423.3281,
                }
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
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600584.SH",),
                ),
            )

        self.assertEqual(result.record_count, 2)
        self.assertEqual(
            [record["event_type"] for record in result.normalized_records],
            ["rights_issue", "dividend"],
        )

        rights_record = result.normalized_records[0]
        self.assertEqual(rights_record["event_date"], "2010-10-22")
        self.assertEqual(rights_record["source_ts"], "2010-10-11T00:00:00")
        self.assertEqual(rights_record["action_family"], "rights_issue")
        self.assertEqual(rights_record["source_route"], "stock_allotment_cninfo")
        self.assertEqual(rights_record["announcement_date"], "2010-10-11")
        self.assertEqual(rights_record["record_date"], "2010-10-13")
        self.assertEqual(rights_record["ex_date"], "2010-10-22")
        self.assertTrue(
            str(rights_record["raw_payload_ref"]).startswith(
                "AKCA|600584.SH|rights_issue|2010-10-22|cninfo_rights_issue|"
            )
        )
        self.assertEqual(
            rights_record["value"],
            {
                "action_family": "rights_issue",
                "source_route": "stock_allotment_cninfo",
                "ratio_base": "per_10_shares",
                "pricing_currency": "CNY",
                "rights_issue_ratio_per_10_shares": 1.5,
                "rights_issue_price_per_share": 5.69,
                "base_share_capital": 74518.4,
                "funds_raised_total": 61423.3281,
                "announcement_date": "2010-10-11",
                "record_date": "2010-10-13",
                "ex_date": "2010-10-22",
                "payment_start_date": "2010-10-14",
                "payment_end_date": "2010-10-20",
                "listing_date": "2010-10-29",
            },
        )
        self.assertEqual(
            registry.validate_record(DatasetName.CORPORATE_ACTIONS, rights_record),
            (),
        )

    def test_rights_issue_cninfo_route_receives_bounded_dates(self) -> None:
        calls: list[dict[str, str]] = []

        def fake_fetch_rights_issue_cninfo(**kwargs):
            calls.append(kwargs)
            return [
                {
                    "公告日期": "2022-01-14",
                    "配股比例": 1.5,
                    "配股价格": 14.43,
                    "除权基准日": "2022-01-27",
                }
            ]

        adapter = _build_adapter(fetch_rights_issue_cninfo=fake_fetch_rights_issue_cninfo)
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CORPORATE_ACTIONS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600030.SH",),
                start_date=date(2022, 1, 1),
                end_date=date(2022, 1, 31),
            ),
        )

        self.assertEqual(calls, [{"symbol": "600030", "start_date": "20220101", "end_date": "20220131"}])
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["source_route"], "stock_allotment_cninfo")

    def test_rights_issue_cninfo_falls_back_to_sina_detail_on_network_error(self) -> None:
        class ProxyError(Exception):
            pass

        adapter = _build_adapter(
            fetch_rights_issue_cninfo=lambda **kwargs: (_ for _ in ()).throw(ProxyError("cninfo proxy down")),
            fetch_rights_issue_detail=lambda **kwargs: [
                {
                    "公告日期": "2010-10-11",
                    "配股方案": 1.5,
                    "配股价格": 5.69,
                    "基准股本": 745184000,
                    "除权日": "2010-10-22",
                    "股权登记日": "2010-10-13",
                }
            ],
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CORPORATE_ACTIONS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600584.SH",),
            ),
        )

        rights_record = result.normalized_records[0]
        self.assertEqual(rights_record["event_type"], "rights_issue")
        self.assertEqual(
            rights_record["source_route"],
            "stock_history_dividend_detail(indicator=配股)",
        )
        self.assertTrue(
            str(rights_record["raw_payload_ref"]).startswith(
                "AKCA|600584.SH|rights_issue|2010-10-22|sina_rights_issue|"
            )
        )

    def test_symbol_normalization_accepts_canonical_and_raw_6_digit(self) -> None:
        adapter = _build_adapter(
            fetch_dividend_cninfo=lambda **kwargs: [
                {
                    "实施方案公告日期": "2024-05-01",
                    "派息比例": 1.0,
                    "股权登记日": "2024-05-10",
                }
            ]
        )

        result_canonical = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CORPORATE_ACTIONS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
            ),
        )
        self.assertEqual(result_canonical.record_count, 1)
        self.assertEqual(result_canonical.normalized_records[0]["symbol"], "600000.SH")

        result_raw = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CORPORATE_ACTIONS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000",),
            ),
        )
        self.assertEqual(result_raw.record_count, 1)
        self.assertEqual(result_raw.normalized_records[0]["symbol"], "600000.SH")

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = _build_adapter()
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
        adapter = _build_adapter()
        with self.assertRaisesRegex(ValueError, "requires exactly one symbol, got none"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )
        with self.assertRaisesRegex(ValueError, "exactly one symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH", "000001.SZ"),
                ),
            )

    def test_adapter_rejects_invalid_hk_etf_and_index_like_symbols(self) -> None:
        adapter = _build_adapter()

        with self.assertRaisesRegex(ValueError, "Invalid symbol filter format"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "code prefix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.SH",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Index symbol is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("399001.SZ",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "market-code combination"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SZ",),
                ),
            )

    def test_event_date_fallback_order_is_deterministic(self) -> None:
        adapter = _build_adapter(
            fetch_dividend_cninfo=lambda **kwargs: [
                {
                    "除权日": "2024-06-11",
                    "股权登记日": "2024-06-10",
                    "实施方案公告日期": "2024-06-01",
                    "派息比例": 1,
                },
                {
                    "股权登记日": "2024-06-12",
                    "实施方案公告日期": "2024-06-02",
                    "派息比例": 1,
                },
                {
                    "实施方案公告日期": "2024-06-13",
                    "派息比例": 1,
                },
            ],
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CORPORATE_ACTIONS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
            ),
        )
        self.assertEqual(
            [record["event_date"] for record in result.normalized_records],
            ["2024-06-11", "2024-06-12", "2024-06-13"],
        )

    def test_start_end_date_filtering_uses_normalized_event_date(self) -> None:
        adapter = _build_adapter(
            fetch_dividend_cninfo=lambda **kwargs: [
                {"除权日": "2024-06-10", "派息比例": 1},
                {"除权日": "2024-06-11", "派息比例": 1},
                {"除权日": "2024-06-12", "派息比例": 1},
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CORPORATE_ACTIONS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
                start_date=date(2024, 6, 11),
                end_date=date(2024, 6, 11),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["event_date"], "2024-06-11")

    def test_raw_payload_ref_is_deterministic_for_equivalent_rows(self) -> None:
        row_a = {
            "除权日": "2024-06-11",
            "派息比例": 1.2,
            "实施方案公告日期": "2024-06-01",
            "分红类型": "年度分红",
        }
        row_b = {
            "分红类型": "年度分红",
            "实施方案公告日期": "2024-06-01",
            "派息比例": 1.2,
            "除权日": "2024-06-11",
        }

        adapter_a = _build_adapter(fetch_dividend_cninfo=lambda **kwargs: [row_a])
        adapter_b = _build_adapter(fetch_dividend_cninfo=lambda **kwargs: [row_b])

        result_a = fetch_source_result(
            adapter_a,
            SourceRequest(
                dataset=DatasetName.CORPORATE_ACTIONS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
            ),
        )
        result_b = fetch_source_result(
            adapter_b,
            SourceRequest(
                dataset=DatasetName.CORPORATE_ACTIONS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
            ),
        )
        self.assertEqual(
            result_a.normalized_records[0]["raw_payload_ref"],
            result_b.normalized_records[0]["raw_payload_ref"],
        )

    def test_adapter_deduplicates_benign_exact_duplicate_rows(self) -> None:
        row = {
            "除权日": "2024-06-11",
            "派息比例": 1.2,
            "实施方案公告日期": "2024-06-01",
        }
        adapter = _build_adapter(fetch_dividend_cninfo=lambda **kwargs: [row, dict(row)])
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CORPORATE_ACTIONS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600000.SH",),
            ),
        )
        self.assertEqual(result.record_count, 1)

    def test_adapter_rejects_conflicting_duplicate_same_identity(self) -> None:
        class _ConflictRawRefAdapter(AkshareAShareCorporateActionsAdapter):
            def _build_raw_payload_ref(self, **kwargs):  # type: ignore[override]
                return "AKCA|CONFLICT"

        adapter = _ConflictRawRefAdapter(
            fetch_dividend_cninfo=lambda **kwargs: [
                {"除权日": "2024-06-11", "派息比例": 1.0, "实施方案公告日期": "2024-06-01"},
                {"除权日": "2024-06-11", "派息比例": 2.0, "实施方案公告日期": "2024-06-01"},
            ]
        )
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate A-share corporate-actions row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape(self) -> None:
        adapter = _build_adapter(fetch_dividend_cninfo=lambda **kwargs: {"除权日": "2024-06-11"})
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_non_mapping_payload_row(self) -> None:
        adapter = _build_adapter(fetch_dividend_cninfo=lambda **kwargs: [1])
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_missing_required_event_date_fields(self) -> None:
        adapter = _build_adapter(fetch_dividend_cninfo=lambda **kwargs: [{"派息比例": 1.0}])
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_invalid_event_date(self) -> None:
        adapter = _build_adapter(
            fetch_dividend_cninfo=lambda **kwargs: [{"除权日": "2024/06/11", "派息比例": 1.0}]
        )
        with self.assertRaisesRegex(ValueError, "Invalid event_date value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_invalid_dividend_numeric_value(self) -> None:
        adapter = _build_adapter(
            fetch_dividend_cninfo=lambda **kwargs: [{"除权日": "2024-06-11", "派息比例": "bad"}]
        )
        with self.assertRaisesRegex(ValueError, "Invalid cash_dividend value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_rejects_negative_rights_issue_price(self) -> None:
        adapter = _build_adapter(
            fetch_rights_issue_detail=lambda **kwargs: [
                {
                    "公告日期": "2010-10-11",
                    "配股方案": 1.5,
                    "配股价格": -5.69,
                    "除权日": "2010-10-22",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid rights_issue_price value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600584.SH",),
                ),
            )

    def test_adapter_rejects_non_serializable_source_row_values(self) -> None:
        adapter = _build_adapter(
            fetch_dividend_cninfo=lambda **kwargs: [
                {"除权日": "2024-06-11", "派息比例": 1.0, "weird": object()}
            ]
        )
        with self.assertRaisesRegex(ValueError, "Non-serializable"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_wraps_network_related_failures_for_live_diagnostics(self) -> None:
        class ProxyError(Exception):
            pass

        adapter = _build_adapter(
            fetch_dividend_cninfo=lambda **kwargs: (_ for _ in ()).throw(ProxyError("proxy down")),
            fetch_dividend_detail=lambda **kwargs: (_ for _ in ()).throw(ProxyError("proxy down fallback")),
        )
        with self.assertRaisesRegex(RuntimeError, "routes unavailable"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

    def test_adapter_does_not_mask_non_network_primary_errors(self) -> None:
        adapter = _build_adapter(
            fetch_dividend_cninfo=lambda **kwargs: (_ for _ in ()).throw(ValueError("bad payload"))
        )
        with self.assertRaisesRegex(ValueError, "bad payload"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )


if __name__ == "__main__":
    unittest.main()
