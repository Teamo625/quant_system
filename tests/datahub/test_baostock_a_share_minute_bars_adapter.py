from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from quant.datahub.adapters.baostock import (
    BAOSTOCK_SOURCE_ID,
    BaoStockAShareMinuteBarsAdapter,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceAdapter, SourceRequest, fetch_source_result


class _FakeBaoStockResult:
    def __init__(
        self,
        rows,
        *,
        fields=None,
        error_code="0",
        error_msg="success",
        iteration_error_code=None,
        iteration_error_msg=None,
    ):
        self.fields = fields or [
            "date",
            "time",
            "code",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "amount",
            "adjustflag",
        ]
        self.error_code = error_code
        self.error_msg = error_msg
        self._rows = list(rows)
        self._idx = -1
        self._iteration_error_code = iteration_error_code
        self._iteration_error_msg = iteration_error_msg

    def next(self):
        self._idx += 1
        has_row = self._idx < len(self._rows)
        if not has_row and self._iteration_error_code is not None:
            self.error_code = self._iteration_error_code
            self.error_msg = self._iteration_error_msg or "iteration failed"
        return has_row

    def get_row_data(self):
        return self._rows[self._idx]


def _ok_login():
    return type("LoginResult", (), {"error_code": "0", "error_msg": "success"})()


def _build_adapter(
    *,
    login_fn=None,
    query_history_fn=None,
    logout_fn=None,
    now_fn=None,
    minute_period="5",
) -> BaoStockAShareMinuteBarsAdapter:
    return BaoStockAShareMinuteBarsAdapter(
        login_fn=login_fn or _ok_login,
        query_history_fn=query_history_fn or (lambda *args, **kwargs: _FakeBaoStockResult([])),
        logout_fn=logout_fn or (lambda: None),
        now_fn=now_fn,
        minute_period=minute_period,
    )


class BaoStockAShareMinuteBarsAdapterTests(unittest.TestCase):
    def test_adapter_is_source_protocol_compatible(self) -> None:
        self.assertIsInstance(_build_adapter(), SourceAdapter)

    def test_fetch_source_result_validates_contract_sorts_dedupes_and_logs_out(self) -> None:
        calls: list[tuple[str, object]] = []
        now = datetime(2026, 6, 1, 8, 0, 0, tzinfo=timezone.utc)
        registry = DatasetRegistry()

        def fake_login():
            calls.append(("login", None))
            return _ok_login()

        def fake_query(code, fields, **kwargs):
            calls.append(("query", (code, fields, kwargs)))
            if code == "sh.600000":
                return _FakeBaoStockResult(
                    [
                        [
                            "2024-01-03",
                            "20240103100000000",
                            "sh.600000",
                            "6.60",
                            "6.70",
                            "6.50",
                            "6.65",
                            "1000",
                            "6650",
                            "3",
                        ],
                        [
                            "2024-01-02",
                            "20240102093500000",
                            "sh.600000",
                            "6.30",
                            "6.40",
                            "6.20",
                            "6.35",
                            "900",
                            "5715",
                            "3",
                        ],
                        [
                            "2024-01-02",
                            "20240102093500000",
                            "sh.600000",
                            "6.30",
                            "6.40",
                            "6.20",
                            "6.35",
                            "900",
                            "5715",
                            "3",
                        ],
                    ]
                )
            return _FakeBaoStockResult(
                [
                    [
                        "2024-01-02",
                        "20240102093500000",
                        "sz.000001",
                        "9.30",
                        "9.40",
                        "9.20",
                        "9.35",
                        "2000",
                        "18700",
                        "3",
                    ]
                ]
            )

        def fake_logout():
            calls.append(("logout", None))

        adapter = _build_adapter(
            login_fn=fake_login,
            query_history_fn=fake_query,
            logout_fn=fake_logout,
            now_fn=lambda: now,
        )

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=BAOSTOCK_SOURCE_ID,
                    symbols=("600000.SH", "000001.SZ", "600000.SH"),
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                ),
            )

        self.assertEqual(calls[0], ("login", None))
        self.assertEqual(calls[-1], ("logout", None))
        query_calls = [call for call in calls if call[0] == "query"]
        self.assertEqual(len(query_calls), 2)
        self.assertEqual(query_calls[0][1][0], "sh.600000")
        self.assertEqual(query_calls[0][1][1], adapter._FIELDS)  # pylint: disable=protected-access
        self.assertEqual(
            query_calls[0][1][2],
            {
                "start_date": "2024-01-02",
                "end_date": "2024-01-05",
                "frequency": "5",
                "adjustflag": "3",
            },
        )
        self.assertEqual(query_calls[1][1][0], "sz.000001")

        self.assertEqual(result.record_count, 3)
        self.assertEqual(
            [(record["symbol"], record["bar_time"]) for record in result.normalized_records],
            [
                ("000001.SZ", "2024-01-02T09:35:00"),
                ("600000.SH", "2024-01-02T09:35:00"),
                ("600000.SH", "2024-01-03T10:00:00"),
            ],
        )
        for record in result.normalized_records:
            self.assertEqual(record["source"], BAOSTOCK_SOURCE_ID)
            self.assertEqual(record["market"], "A_SHARE")
            self.assertEqual(record["ingested_at"], now.isoformat())
            self.assertEqual(record["schema_version"], "v1")
            self.assertEqual(registry.validate_record(DatasetName.MINUTE_BARS, record), ())

    def test_adapter_supports_5_15_30_60_and_rejects_1_minute(self) -> None:
        for minute_period in ("5", "15", "30", "60"):
            adapter = _build_adapter(minute_period=minute_period)
            self.assertEqual(adapter._minute_period, minute_period)  # pylint: disable=protected-access

        with self.assertRaisesRegex(ValueError, "Unsupported minute_period"):
            _build_adapter(minute_period="1")

    def test_adapter_rejects_unsupported_dataset_and_unbounded_requests(self) -> None:
        adapter = _build_adapter()

        with self.assertRaisesRegex(ValueError, "Unsupported dataset"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name=BAOSTOCK_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                ),
            )

        with self.assertRaisesRegex(ValueError, "requires bounded date window"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=BAOSTOCK_SOURCE_ID,
                    symbols=("600000.SH",),
                ),
            )

        with self.assertRaisesRegex(ValueError, "requires both start_date and end_date"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=BAOSTOCK_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2024, 1, 2),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Invalid SourceRequest date range"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=BAOSTOCK_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2024, 1, 5),
                    end_date=date(2024, 1, 2),
                ),
            )

    def test_adapter_accepts_canonical_prefixed_and_bare_symbols(self) -> None:
        seen_codes: list[str] = []

        def fake_query(code, fields, **kwargs):
            del fields, kwargs
            seen_codes.append(code)
            return _FakeBaoStockResult(
                [
                    [
                        "2024-01-02",
                        "20240102093500000",
                        code,
                        "1",
                        "1",
                        "1",
                        "1",
                        "1",
                        "1",
                        "3",
                    ]
                ]
            )

        accepted = {
            "600000.SH": "600000.SH",
            "SH600000": "600000.SH",
            "600000": "600000.SH",
            "000001.SZ": "000001.SZ",
            "SZ000001": "000001.SZ",
            "000001": "000001.SZ",
        }
        for raw_symbol, canonical in accepted.items():
            adapter = _build_adapter(query_history_fn=fake_query)
            result = fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=BAOSTOCK_SOURCE_ID,
                    symbols=(raw_symbol,),
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 2),
                ),
            )
            self.assertEqual(result.record_count, 1)
            self.assertEqual(result.normalized_records[0]["symbol"], canonical)

        self.assertIn("sh.600000", seen_codes)
        self.assertIn("sz.000001", seen_codes)

    def test_adapter_rejects_invalid_hk_etf_index_and_malformed_symbols(self) -> None:
        adapter = _build_adapter()

        with self.assertRaisesRegex(ValueError, "Unsupported symbol market suffix"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=BAOSTOCK_SOURCE_ID,
                    symbols=("00700.HK",),
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                ),
            )

        with self.assertRaisesRegex(ValueError, "ETF or fund symbol is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=BAOSTOCK_SOURCE_ID,
                    symbols=("510300.SH",),
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Index symbol is unsupported"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=BAOSTOCK_SOURCE_ID,
                    symbols=("399001.SZ",),
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Unsupported symbol format"):
            fetch_source_result(
                adapter,
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=BAOSTOCK_SOURCE_ID,
                    symbols=("BAD_SYMBOL",),
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                ),
            )

    def test_adapter_reports_baostock_login_query_and_iteration_errors(self) -> None:
        bad_login = lambda: type("LoginResult", (), {"error_code": "1", "error_msg": "down"})()
        with self.assertRaisesRegex(RuntimeError, "BaoStock login failed"):
            fetch_source_result(
                _build_adapter(login_fn=bad_login),
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=BAOSTOCK_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                ),
            )

        with self.assertRaisesRegex(RuntimeError, "BaoStock minute-bars query failed"):
            fetch_source_result(
                _build_adapter(
                    query_history_fn=lambda *args, **kwargs: _FakeBaoStockResult(
                        [], error_code="100", error_msg="query failed"
                    )
                ),
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=BAOSTOCK_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                ),
            )

        with self.assertRaisesRegex(RuntimeError, "BaoStock minute-bars iteration failed"):
            fetch_source_result(
                _build_adapter(
                    query_history_fn=lambda *args, **kwargs: _FakeBaoStockResult(
                        [],
                        iteration_error_code="200",
                        iteration_error_msg="iteration failed",
                    )
                ),
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=BAOSTOCK_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                ),
            )

    def test_adapter_rejects_malformed_payload_missing_fields_and_invalid_values(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing structured fields"):
            fetch_source_result(
                _build_adapter(
                    query_history_fn=lambda *args, **kwargs: _FakeBaoStockResult(
                        [], fields="bad"
                    )
                ),
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=BAOSTOCK_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                ),
            )

        with self.assertRaisesRegex(ValueError, "row field count mismatch"):
            fetch_source_result(
                _build_adapter(
                    query_history_fn=lambda *args, **kwargs: _FakeBaoStockResult([["short"]])
                ),
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=BAOSTOCK_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                ),
            )

        bad_timestamp = _FakeBaoStockResult(
            [["2024-13-02", "20240102093500000", "sh.600000", "1", "1", "1", "1", "1", "1", "3"]]
        )
        with self.assertRaisesRegex(ValueError, "Invalid BaoStock date value"):
            fetch_source_result(
                _build_adapter(query_history_fn=lambda *args, **kwargs: bad_timestamp),
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=BAOSTOCK_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                ),
            )

        bad_numeric = _FakeBaoStockResult(
            [["2024-01-02", "20240102093500000", "sh.600000", "bad", "1", "1", "1", "1", "1", "3"]]
        )
        with self.assertRaisesRegex(ValueError, "Invalid open value"):
            fetch_source_result(
                _build_adapter(query_history_fn=lambda *args, **kwargs: bad_numeric),
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=BAOSTOCK_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                ),
            )

    def test_adapter_rejects_source_symbol_mismatch_and_conflicting_duplicates(self) -> None:
        mismatch = _FakeBaoStockResult(
            [["2024-01-02", "20240102093500000", "sz.000001", "1", "1", "1", "1", "1", "1", "3"]]
        )
        with self.assertRaisesRegex(ValueError, "Source symbol mismatch"):
            fetch_source_result(
                _build_adapter(query_history_fn=lambda *args, **kwargs: mismatch),
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=BAOSTOCK_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                ),
            )

        conflict = _FakeBaoStockResult(
            [
                ["2024-01-02", "20240102093500000", "sh.600000", "1", "1", "1", "1", "1", "1", "3"],
                ["2024-01-02", "20240102093500000", "sh.600000", "2", "1", "1", "1", "1", "1", "3"],
            ]
        )
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate BaoStock"):
            fetch_source_result(
                _build_adapter(query_history_fn=lambda *args, **kwargs: conflict),
                SourceRequest(
                    dataset=DatasetName.MINUTE_BARS,
                    source_name=BAOSTOCK_SOURCE_ID,
                    symbols=("600000.SH",),
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 5),
                ),
            )


if __name__ == "__main__":
    unittest.main()
