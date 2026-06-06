from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareHKCorporateActionsAdapter,
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
    fetch_hk_dividend_payout=None,
    fetch_hk_fhpx_detail=None,
    now_fn=None,
) -> AkshareHKCorporateActionsAdapter:
    return AkshareHKCorporateActionsAdapter(
        fetch_hk_dividend_payout=fetch_hk_dividend_payout or (lambda **kwargs: []),
        fetch_hk_fhpx_detail=fetch_hk_fhpx_detail,
        now_fn=now_fn,
    )


class AkshareHKCorporateActionsAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = _build_adapter()
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_and_validates_corporate_actions(self) -> None:
        calls: list[dict[str, str]] = []
        now = datetime(2026, 5, 28, 9, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        def fake_fetch_hk_dividend_payout(**kwargs):
            calls.append(kwargs)
            return _FakeDataFrame(
                [
                    {
                        "最新公告日期": "2026-05-13",
                        "财政年度": "2025",
                        "分红方案": "每股派港币5.3元",
                        "分配类型": "年度分配",
                        "除净日": "2026-05-15",
                        "截至过户日": "2026/05/19-2026/05/20",
                        "发放日": "2026-06-01",
                    }
                ]
            )

        adapter = _build_adapter(
            fetch_hk_dividend_payout=fake_fetch_hk_dividend_payout,
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
                    symbols=("00700.HK",),
                ),
                fetched_at=datetime(2026, 5, 28, 9, 5, 0, tzinfo=timezone.utc),
            )

        self.assertEqual(calls, [{"symbol": "00700"}])
        self.assertEqual(result.record_count, 1)
        record = result.normalized_records[0]

        self.assertEqual(record["symbol"], "00700.HK")
        self.assertEqual(record["market"], "HK")
        self.assertEqual(record["event_date"], "2026-05-15")
        self.assertEqual(record["event_type"], "dividend")
        self.assertEqual(record["action_family"], "dividend_distribution")
        self.assertEqual(
            record["source_route"],
            AkshareHKCorporateActionsAdapter._PRIMARY_ROUTE_NAME,
        )
        self.assertEqual(record["announcement_date"], "2026-05-13")
        self.assertEqual(record["ex_date"], "2026-05-15")
        self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(record["schema_version"], "v1")
        self.assertEqual(record["ingested_at"], now.isoformat())
        self.assertEqual(record["source_ts"], "2026-05-13T00:00:00")
        self.assertTrue(str(record["raw_payload_ref"]).startswith("AKCA|00700.HK|dividend|2026-05-15|"))

        value = record["value"]
        self.assertEqual(value["action_family"], "dividend_distribution")
        self.assertEqual(
            value["source_route"],
            AkshareHKCorporateActionsAdapter._PRIMARY_ROUTE_NAME,
        )
        self.assertEqual(value["fiscal_year"], "2025")
        self.assertEqual(value["distribution_type"], "年度分配")
        self.assertEqual(value["announcement_date"], "2026-05-13")
        self.assertEqual(value["raw_plan_text"], "每股派港币5.3元")
        self.assertEqual(value["cash_distribution_text"], "每股派港币5.3元")
        self.assertEqual(value["cash_dividend_per_share"], 5.3)
        self.assertEqual(value["cash_currency"], "HKD")
        self.assertEqual(value["cash_dividend_unit"], "per_share")
        self.assertEqual(value["register_book_period"], "2026/05/19-2026/05/20")
        self.assertEqual(value["payout_date"], "2026-06-01")

        self.assertEqual(
            registry.validate_record(DatasetName.CORPORATE_ACTIONS, record),
            (),
        )

    def test_symbol_normalization_accepts_canonical_and_raw_hk_code(self) -> None:
        adapter = _build_adapter(
            fetch_hk_dividend_payout=lambda **kwargs: [
                {"除净日": "2026-05-15", "分红方案": "每股派港币1.0元"}
            ]
        )
        result_canonical = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CORPORATE_ACTIONS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
            ),
        )
        self.assertEqual(result_canonical.normalized_records[0]["symbol"], "00700.HK")

        result_raw = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CORPORATE_ACTIONS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700",),
            ),
        )
        self.assertEqual(result_raw.normalized_records[0]["symbol"], "00700.HK")

    def test_adapter_rejects_unsupported_dataset(self) -> None:
        adapter = _build_adapter()
        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
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
                    symbols=("00700.HK", "00005.HK"),
                ),
            )

    def test_adapter_rejects_invalid_a_share_etf_and_index_like_symbols(self) -> None:
        adapter = _build_adapter()
        with self.assertRaisesRegex(ValueError, "Unsupported symbol market suffix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )
        with self.assertRaisesRegex(ValueError, "Unsupported HK symbol format"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("510300.HK",),
                ),
            )
        with self.assertRaisesRegex(ValueError, "Unsupported HK symbol format"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("HSI.HK",),
                ),
            )

    def test_event_date_fallback_order_is_deterministic(self) -> None:
        adapter = _build_adapter(
            fetch_hk_dividend_payout=lambda **kwargs: [
                {"除净日": "2026-05-15", "最新公告日期": "2026-05-13", "发放日": "2026-06-01"},
                {"最新公告日期": "2026-05-14", "发放日": "2026-06-02"},
                {"发放日": "2026-06-03"},
            ],
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CORPORATE_ACTIONS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
            ),
        )
        self.assertEqual(
            [record["event_date"] for record in result.normalized_records],
            ["2026-05-14", "2026-05-15", "2026-06-03"],
        )

    def test_start_end_date_filtering_uses_normalized_event_date(self) -> None:
        adapter = _build_adapter(
            fetch_hk_dividend_payout=lambda **kwargs: [
                {"除净日": "2026-05-14", "分红方案": "每股派港币0.1元"},
                {"除净日": "2026-05-15", "分红方案": "每股派港币0.1元"},
                {"除净日": "2026-05-16", "分红方案": "每股派港币0.1元"},
            ]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CORPORATE_ACTIONS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
                start_date=date(2026, 5, 15),
                end_date=date(2026, 5, 15),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.normalized_records[0]["event_date"], "2026-05-15")

    def test_raw_payload_ref_is_deterministic_for_equivalent_rows(self) -> None:
        row_a = {
            "除净日": "2026-05-15",
            "最新公告日期": "2026-05-13",
            "分红方案": "每股派港币5.3元",
        }
        row_b = {
            "分红方案": "每股派港币5.3元",
            "最新公告日期": "2026-05-13",
            "除净日": "2026-05-15",
        }
        adapter_a = _build_adapter(fetch_hk_dividend_payout=lambda **kwargs: [row_a])
        adapter_b = _build_adapter(fetch_hk_dividend_payout=lambda **kwargs: [row_b])
        result_a = fetch_source_result(
            adapter_a,
            SourceRequest(
                dataset=DatasetName.CORPORATE_ACTIONS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
            ),
        )
        result_b = fetch_source_result(
            adapter_b,
            SourceRequest(
                dataset=DatasetName.CORPORATE_ACTIONS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
            ),
        )
        self.assertEqual(
            result_a.normalized_records[0]["raw_payload_ref"],
            result_b.normalized_records[0]["raw_payload_ref"],
        )

    def test_adapter_deduplicates_benign_exact_duplicate_rows(self) -> None:
        row = {"除净日": "2026-05-15", "分红方案": "每股派港币5.3元"}
        adapter = _build_adapter(fetch_hk_dividend_payout=lambda **kwargs: [row, dict(row)])
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CORPORATE_ACTIONS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
            ),
        )
        self.assertEqual(result.record_count, 1)

    def test_adapter_rejects_conflicting_duplicate_same_identity(self) -> None:
        class _ConflictRawRefAdapter(AkshareHKCorporateActionsAdapter):
            def _build_raw_payload_ref(self, **kwargs):  # type: ignore[override]
                return "AKCA|HK|CONFLICT"

        adapter = _ConflictRawRefAdapter(
            fetch_hk_dividend_payout=lambda **kwargs: [
                {"除净日": "2026-05-15", "分红方案": "每股派港币1.0元"},
                {"除净日": "2026-05-15", "分红方案": "每股派港币2.0元"},
            ]
        )
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate HK corporate-actions row"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_malformed_payload_shape_and_non_mapping_row(self) -> None:
        adapter = _build_adapter(fetch_hk_dividend_payout=lambda **kwargs: {"除净日": "2026-05-15"})
        with self.assertRaisesRegex(ValueError, "must be DataFrame-like or list"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

        adapter = _build_adapter(fetch_hk_dividend_payout=lambda **kwargs: [1])
        with self.assertRaisesRegex(ValueError, "payload row must be mapping"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_missing_required_event_date_fields(self) -> None:
        adapter = _build_adapter(fetch_hk_dividend_payout=lambda **kwargs: [{"分红方案": "每股派港币1.0元"}])
        with self.assertRaisesRegex(ValueError, "Missing required source field"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_invalid_event_date(self) -> None:
        adapter = _build_adapter(
            fetch_hk_dividend_payout=lambda **kwargs: [{"除净日": "2026/13/40", "分红方案": "每股派港币1.0元"}]
        )
        with self.assertRaisesRegex(ValueError, "Invalid event_date value"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_rejects_invalid_numeric_extraction_when_pattern_is_malformed(self) -> None:
        adapter = _build_adapter(
            fetch_hk_dividend_payout=lambda **kwargs: [{"除净日": "2026-05-15", "分红方案": "每股派港币.元"}]
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CORPORATE_ACTIONS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
            ),
        )
        self.assertEqual(result.record_count, 1)
        self.assertNotIn("cash_dividend_per_share", result.normalized_records[0]["value"])

    def test_adapter_rejects_non_serializable_source_row_values(self) -> None:
        adapter = _build_adapter(
            fetch_hk_dividend_payout=lambda **kwargs: [
                {"除净日": "2026-05-15", "分红方案": "每股派港币1.0元", "weird": object()}
            ]
        )
        with self.assertRaisesRegex(ValueError, "Non-serializable"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_uses_fallback_route_when_primary_network_unavailable(self) -> None:
        class ProxyError(Exception):
            pass

        calls: list[tuple[str, str]] = []

        def failing_primary(**kwargs):
            calls.append(("primary", kwargs["symbol"]))
            raise ProxyError("proxy unavailable")

        def good_fallback(**kwargs):
            calls.append(("fallback", kwargs["symbol"]))
            return [
                {
                    "公告日期": "2024-08-19",
                    "方案": "每股派港币0.1元",
                    "除净日": "2024-09-02",
                    "派息日": "2024-09-14",
                    "过户日期起止日-起始": "2024-09-04",
                    "过户日期起止日-截止": "2024-09-05",
                    "类型": "中报",
                    "进度": "实施完成",
                }
            ]

        adapter = _build_adapter(
            fetch_hk_dividend_payout=failing_primary,
            fetch_hk_fhpx_detail=good_fallback,
        )
        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.CORPORATE_ACTIONS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("00700.HK",),
            ),
        )
        self.assertEqual(calls, [("primary", "00700"), ("fallback", "0700")])
        self.assertEqual(result.record_count, 1)
        self.assertEqual(
            result.normalized_records[0]["source_route"],
            AkshareHKCorporateActionsAdapter._FALLBACK_ROUTE_NAME,
        )
        self.assertEqual(
            result.normalized_records[0]["action_family"],
            "dividend_distribution",
        )
        self.assertEqual(result.normalized_records[0]["value"]["register_book_period"], "2024-09-04~2024-09-05")

    def test_adapter_wraps_network_related_failures_for_live_diagnostics(self) -> None:
        class ProxyError(Exception):
            pass

        adapter = _build_adapter(
            fetch_hk_dividend_payout=lambda **kwargs: (_ for _ in ()).throw(ProxyError("proxy down")),
            fetch_hk_fhpx_detail=lambda **kwargs: (_ for _ in ()).throw(ProxyError("proxy down fallback")),
        )
        with self.assertRaisesRegex(RuntimeError, "routes unavailable"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )

    def test_adapter_does_not_mask_non_network_primary_errors(self) -> None:
        adapter = _build_adapter(
            fetch_hk_dividend_payout=lambda **kwargs: (_ for _ in ()).throw(ValueError("bad payload"))
        )
        with self.assertRaisesRegex(ValueError, "bad payload"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.CORPORATE_ACTIONS,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("00700.HK",),
                ),
            )


if __name__ == "__main__":
    unittest.main()
