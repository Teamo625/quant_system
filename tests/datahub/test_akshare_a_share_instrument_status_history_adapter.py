from datetime import datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareInstrumentStatusHistoryAdapter,
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
    fetch_sh_main=None,
    fetch_sh_kcb=None,
    fetch_sz_a=None,
    fetch_bj_a=None,
    fetch_sh_delist=None,
    fetch_sz_delist=None,
    fetch_sz_change_name=None,
    now_fn=None,
) -> AkshareAShareInstrumentStatusHistoryAdapter:
    return AkshareAShareInstrumentStatusHistoryAdapter(
        fetch_sh_main=fetch_sh_main or (lambda: []),
        fetch_sh_kcb=fetch_sh_kcb or (lambda: []),
        fetch_sz_a=fetch_sz_a or (lambda: []),
        fetch_bj_a=fetch_bj_a or (lambda: []),
        fetch_sh_delist=fetch_sh_delist or (lambda symbol=None: []),
        fetch_sz_delist=fetch_sz_delist or (lambda symbol=None: []),
        fetch_sz_change_name=fetch_sz_change_name or (lambda symbol=None: []),
        now_fn=now_fn,
    )


class AkshareAShareInstrumentStatusHistoryAdapterTests(unittest.TestCase):
    def test_unavailable_classifier_does_not_treat_route_signature_errors_as_unavailable(
        self,
    ) -> None:
        adapter = _build_adapter(fetch_sz_change_name=lambda: [])
        self.assertFalse(
            adapter._is_instrument_status_history_route_unavailable(  # pylint: disable=protected-access
                RuntimeError(
                    "AKShare A-share instrument-status-history route does not accept "
                    "required argument: route=stock_info_sz_change_name(简称变更), field=symbol"
                )
            )
        )

    def test_adapter_is_source_protocol_compatible(self) -> None:
        adapter = _build_adapter()
        self.assertIsInstance(adapter, SourceAdapter)

    def test_fetch_source_result_normalizes_sorts_deduplicates_and_validates_offline_only(
        self,
    ) -> None:
        now = datetime(2026, 6, 5, 8, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()
        calls: list[tuple[str, object]] = []

        adapter = _build_adapter(
            fetch_sh_main=lambda: _FakeDataFrame(
                [
                    {
                        "证券代码": "600000",
                        "证券简称": "浦发银行",
                        "上市日期": "19991110",
                    },
                    {
                        "证券代码": "600053",
                        "证券简称": "*ST九鼎",
                        "上市日期": "19970418",
                    },
                ]
            ),
            fetch_sh_kcb=lambda: calls.append(("sh_kcb", None)) or [],
            fetch_sz_a=lambda: calls.append(("sz_a", None))
            or [
                {
                    "A股代码": "000001",
                    "A股简称": "平安银行",
                    "A股上市日期": "1991-04-03",
                    "板块": "主板",
                }
            ],
            fetch_bj_a=lambda: calls.append(("bj_a", None))
            or [
                {
                    "证券代码": "920001",
                    "证券简称": "纬达光电",
                    "上市日期": "2022-12-27",
                    "报告日期": "2026-06-05",
                }
            ],
            fetch_sh_delist=lambda symbol=None: calls.append(("sh_delist", symbol))
            or [
                {
                    "公司代码": "600002",
                    "公司简称": "齐鲁退市",
                    "上市日期": "1998-04-08",
                    "暂停上市日期": "2006-04-24",
                }
            ],
            fetch_sz_delist=lambda symbol=None: calls.append(("sz_delist", symbol))
            or _FakeDataFrame(
                [
                    {
                        "证券代码": "000005",
                        "证券简称": "ST星源",
                        "上市日期": "1990-12-10",
                        "终止上市日期": "2024-04-26",
                    }
                ]
            ),
            fetch_sz_change_name=lambda symbol=None: calls.append(("sz_change_name", symbol))
            or [
                {
                    "变更日期": "2024-01-10",
                    "证券代码": "000005",
                    "证券简称": "ST星源",
                    "变更前简称": "星源环境",
                    "变更后简称": "ST星源",
                },
                {
                    "变更日期": "2024-03-15",
                    "证券代码": "000005",
                    "证券简称": "*ST星源",
                    "变更前简称": "ST星源",
                    "变更后简称": "*ST星源",
                },
                {
                    "变更日期": "2024-03-15",
                    "证券代码": "000005",
                    "证券简称": "*ST星源",
                    "变更前简称": "ST星源",
                    "变更后简称": "*ST星源",
                },
                {
                    "变更日期": "2024-04-02",
                    "证券代码": "000001",
                    "证券简称": "平安银行",
                    "变更前简称": "平银股份",
                    "变更后简称": "平安银行",
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
                    dataset=DatasetName.INSTRUMENT_STATUS_HISTORY,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SH", "600053", "000001.SZ", "000005.SZ", "920001.BJ"),
                ),
            )

        self.assertEqual(
            calls,
            [
                ("sh_kcb", None),
                ("sz_a", None),
                ("bj_a", None),
                ("sh_delist", "全部"),
                ("sz_delist", "终止上市公司"),
                ("sz_change_name", "简称变更"),
            ],
        )
        self.assertEqual(result.record_count, 12)

        records = list(result.normalized_records)
        self.assertEqual(
            [(r["symbol"], r["effective_start_date"], r["status_type"], r["status"]) for r in records],
            sorted(
                (r["symbol"], r["effective_start_date"], r["status_type"], r["status"])
                for r in records
            ),
        )

        self.assertEqual(
            len(
                [
                    r
                    for r in records
                    if r["symbol"] == "000005.SZ"
                    and r["effective_start_date"] == "2024-03-15"
                    and r["status_type"] == "risk_warning"
                ]
            ),
            1,
        )

        active_normal = next(
            r
            for r in records
            if r["symbol"] == "000001.SZ"
            and r["status_type"] == "risk_warning"
        )
        self.assertEqual(active_normal["status"], "normal")
        self.assertEqual(active_normal["effective_start_date"], "2026-06-05")
        self.assertEqual(active_normal["exchange"], "SZSE")
        self.assertEqual(active_normal["board"], "main_board")

        active_st = next(
            r
            for r in records
            if r["symbol"] == "600053.SH"
            and r["status_type"] == "risk_warning"
        )
        self.assertEqual(active_st["status"], "star_st")
        self.assertEqual(active_st["raw_status"], "*ST")
        self.assertEqual(active_st["effective_start_date"], "2026-06-05")
        self.assertNotIn("effective_end_date", active_st)

        listed_sh = next(
            r
            for r in records
            if r["symbol"] == "600000.SH"
            and r["status_type"] == "listing_status"
            and r["status"] == "listed"
        )
        self.assertEqual(listed_sh["effective_start_date"], "1999-11-10")
        self.assertEqual(listed_sh["exchange"], "SSE")
        self.assertEqual(listed_sh["board"], "main_board")

        delisted_sz = next(
            r
            for r in records
            if r["symbol"] == "000005.SZ"
            and r["status_type"] == "listing_status"
            and r["status"] == "delisted"
        )
        self.assertEqual(delisted_sz["effective_start_date"], "2024-04-26")

        st_transition = next(
            r
            for r in records
            if r["symbol"] == "000005.SZ"
            and r["effective_start_date"] == "2024-03-15"
        )
        self.assertEqual(st_transition["status"], "star_st")
        self.assertEqual(st_transition["raw_status"], "*ST")
        self.assertEqual(
            st_transition["status_reason"],
            "简称变更: ST星源 -> *ST星源",
        )

        bj_normal = next(
            r
            for r in records
            if r["symbol"] == "920001.BJ"
            and r["status_type"] == "risk_warning"
        )
        self.assertEqual(bj_normal["status"], "normal")
        self.assertEqual(bj_normal["board"], "beijing_board")
        self.assertEqual(bj_normal["source_ts"], "2026-06-05T00:00:00")

        for record in records:
            self.assertEqual(
                registry.validate_record(DatasetName.INSTRUMENT_STATUS_HISTORY, record),
                (),
            )

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

    def test_adapter_requires_non_empty_symbol_list(self) -> None:
        adapter = _build_adapter()

        with self.assertRaisesRegex(ValueError, "requires at least one symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_STATUS_HISTORY,
                    source_name=AKSHARE_SOURCE_ID,
                ),
            )

        with self.assertRaisesRegex(ValueError, "requires at least one symbol"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_STATUS_HISTORY,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=(),
                ),
            )

    def test_adapter_accepts_canonical_prefixed_and_bare_symbols(self) -> None:
        adapter = _build_adapter(
            fetch_sh_main=lambda: [{"证券代码": "600000", "证券简称": "浦发银行", "上市日期": "19991110"}],
            fetch_sz_a=lambda: [{"A股代码": "000001", "A股简称": "平安银行", "A股上市日期": "1991-04-03"}],
            fetch_bj_a=lambda: [{"证券代码": "920001", "证券简称": "纬达光电", "上市日期": "2022-12-27"}],
        )

        accepted = {
            "600000.SH": "600000.SH",
            "SH600000": "600000.SH",
            "600000": "600000.SH",
            "000001.SZ": "000001.SZ",
            "SZ000001": "000001.SZ",
            "000001": "000001.SZ",
            "920001.BJ": "920001.BJ",
            "920001": "920001.BJ",
        }

        for raw_symbol, canonical in accepted.items():
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_STATUS_HISTORY,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=(raw_symbol,),
                ),
            )
            self.assertTrue(result.record_count >= 2)
            self.assertEqual(result.normalized_records[0]["symbol"], canonical)

    def test_adapter_rejects_invalid_symbol_inputs(self) -> None:
        adapter = _build_adapter()

        with self.assertRaisesRegex(ValueError, "empty string"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_STATUS_HISTORY,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=(" ",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "market-code combination"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_STATUS_HISTORY,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("600000.SZ",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "value type"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_STATUS_HISTORY,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=(123,),
                ),
            )

    def test_adapter_returns_empty_result_when_symbol_has_no_public_source_evidence(self) -> None:
        adapter = _build_adapter(
            fetch_sh_main=lambda: [],
            fetch_sh_kcb=lambda: [],
            fetch_sh_delist=lambda symbol=None: [],
        )

        result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.INSTRUMENT_STATUS_HISTORY,
                source_name=AKSHARE_SOURCE_ID,
                symbols=("600999.SH",),
            ),
        )
        self.assertEqual(result.record_count, 0)

    def test_route_signature_compatibility_errors_remain_hard_failures(self) -> None:
        adapter = _build_adapter(fetch_sz_change_name=lambda: [])

        with self.assertRaisesRegex(RuntimeError, "does not accept required argument"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.INSTRUMENT_STATUS_HISTORY,
                    source_name=AKSHARE_SOURCE_ID,
                    symbols=("000001.SZ",),
                ),
            )


if __name__ == "__main__":
    unittest.main()
