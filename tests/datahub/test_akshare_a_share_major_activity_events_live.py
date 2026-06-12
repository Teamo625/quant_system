import os
import re
import socket
import unittest
from datetime import date, timedelta
from typing import Iterable
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareMajorActivityEventsAdapter,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceRequest, fetch_source_result


LIVE_TESTS_ENABLED = os.getenv("QUANT_SYSTEM_LIVE_TESTS") == "1"


def _exception_chain(exc: BaseException) -> Iterable[BaseException]:
    seen: set[int] = set()
    current: BaseException | None = exc
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        yield current
        if current.__cause__ is not None:
            current = current.__cause__
            continue
        current = current.__context__


def _is_live_environment_unavailable(exc: BaseException) -> bool:
    network_exception_names = {
        "ProxyError",
        "ConnectionError",
        "ConnectTimeout",
        "ReadTimeout",
        "Timeout",
        "MaxRetryError",
        "NewConnectionError",
        "NameResolutionError",
        "SSLError",
        "SSLCertVerificationError",
    }
    network_message_tokens = (
        "proxy",
        "timed out",
        "timeout",
        "name resolution",
        "temporary failure in name resolution",
        "failed to establish a new connection",
        "max retries exceeded",
        "network is unreachable",
        "connection refused",
        "no route to host",
        "connection reset",
        "dns",
        "certificate verify failed",
        "ssl",
        "eastmoney",
        "datacenter-web.eastmoney.com",
        "getdata",
        "query.sse.com.cn",
        "szse.cn",
        "bse.cn",
        "getdjgcgbdlist.do",
    )

    for cause in _exception_chain(exc):
        name = type(cause).__name__
        module = type(cause).__module__
        message = str(cause).lower()

        if name in network_exception_names:
            return True
        if module.startswith(("requests", "urllib3")) and any(
            token in message for token in network_message_tokens
        ):
            return True
        if any(token in message for token in network_message_tokens):
            return True
        if isinstance(cause, (socket.timeout, TimeoutError, ConnectionError)):
            return True
        if isinstance(cause, OSError):
            if cause.errno in {101, 104, 110, 111, 113}:
                return True
            if any(token in message for token in network_message_tokens):
                return True

    return False


def _fetch_recent_live_sample(
    *,
    adapter: AkshareAShareMajorActivityEventsAdapter,
    window_days: int = 3,
    max_days_back: int = 30,
) -> tuple[object | None, BaseException | None, tuple[date, date] | None]:
    last_unavailable_exc: BaseException | None = None

    for days_back in range(1, max_days_back + 1):
        target_date = date.today() - timedelta(days=days_back)
        start_date = target_date - timedelta(days=window_days - 1)
        request = SourceRequest(
            dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
            source_name=AKSHARE_SOURCE_ID,
            start_date=start_date,
            end_date=target_date,
        )
        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc) or adapter._is_major_activity_route_unavailable(  # pylint: disable=protected-access
                exc
            ):
                last_unavailable_exc = exc
                continue
            raise

        if result.record_count > 0:
            return result, None, (start_date, target_date)

    return None, last_unavailable_exc, None


def _fetch_curated_insider_live_sample(
    *,
    adapter: AkshareAShareMajorActivityEventsAdapter,
) -> tuple[object | None, BaseException | None, tuple[tuple[str, ...], date, date] | None]:
    last_unavailable_exc: BaseException | None = None
    probe_cases: tuple[tuple[tuple[str, ...], date, date], ...] = (
        (("001308.SZ",), date(2024, 9, 1), date(2024, 9, 30)),
        (("430489.BJ",), date(2023, 7, 1), date(2023, 7, 31)),
        (("600000.SH",), date(2021, 7, 1), date(2021, 7, 31)),
    )

    for symbols, start_date, end_date in probe_cases:
        request = SourceRequest(
            dataset=DatasetName.MAJOR_ACTIVITY_EVENTS,
            source_name=AKSHARE_SOURCE_ID,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
        )
        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc) or adapter._is_major_activity_route_unavailable(  # pylint: disable=protected-access
                exc
            ):
                last_unavailable_exc = exc
                continue
            raise

        insider_records = [
            record
            for record in result.normalized_records
            if record.get("event_type") == "insider_holding_change"
        ]
        if insider_records:
            return result, None, (symbols, start_date, end_date)

    return None, last_unavailable_exc, None


class AkshareAShareMajorActivityEventsLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        self.assertTrue(
            _is_live_environment_unavailable(
                RuntimeError("AKShare major-activity route unavailable: ProxyError: proxy down")
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(ValueError("Invalid event_volume value"))
        )

    def test_classifier_keeps_route_signature_compatibility_errors_as_failures(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(
                RuntimeError(
                    "AKShare A-share major-activity route does not accept required argument: "
                    "route=stock_dzjy_mrmx, field=start_date"
                )
            )
        )

    def test_recent_live_sample_probe_continues_after_unavailable_date(self) -> None:
        class _Adapter:
            def _is_major_activity_route_unavailable(self, exc: BaseException) -> bool:
                return isinstance(exc, RuntimeError) and "route unavailable" in str(exc)

        class _Result:
            def __init__(self, count: int) -> None:
                self.record_count = count

        adapter = _Adapter()
        attempts: list[tuple[date | None, date | None]] = []

        def fake_fetch(_adapter: object, request: SourceRequest) -> _Result:
            attempts.append((request.start_date, request.end_date))
            if len(attempts) == 1:
                raise RuntimeError("route unavailable for this date")
            return _Result(1)

        with patch(f"{__name__}.fetch_source_result", side_effect=fake_fetch):
            result, last_exc, window = _fetch_recent_live_sample(  # type: ignore[arg-type]
                adapter=adapter,
                max_days_back=2,
            )

        self.assertIsNotNone(result)
        self.assertEqual(result.record_count, 1)  # type: ignore[union-attr]
        self.assertIsNone(last_exc)
        self.assertIsNotNone(window)
        self.assertEqual(len(attempts), 2)
        self.assertEqual(attempts[0][0], attempts[0][1] - timedelta(days=2))

    def test_recent_live_sample_probe_returns_last_unavailable_error(self) -> None:
        class _Adapter:
            def _is_major_activity_route_unavailable(self, exc: BaseException) -> bool:
                return isinstance(exc, RuntimeError) and "route unavailable" in str(exc)

        adapter = _Adapter()
        last_error = RuntimeError("route unavailable day-2")
        errors = [RuntimeError("route unavailable day-1"), last_error]

        def fake_fetch(_adapter: object, _request: SourceRequest) -> object:
            raise errors.pop(0)

        with patch(f"{__name__}.fetch_source_result", side_effect=fake_fetch):
            result, last_exc, window = _fetch_recent_live_sample(  # type: ignore[arg-type]
                adapter=adapter,
                max_days_back=2,
            )

        self.assertIsNone(result)
        self.assertIs(last_exc, last_error)
        self.assertIsNone(window)

    def test_recent_live_sample_probe_keeps_non_unavailable_errors_as_failures(self) -> None:
        class _Adapter:
            def _is_major_activity_route_unavailable(self, _exc: BaseException) -> bool:
                return False

        adapter = _Adapter()

        def fake_fetch(_adapter: object, _request: SourceRequest) -> object:
            raise ValueError("invalid event_volume value")

        with patch(f"{__name__}.fetch_source_result", side_effect=fake_fetch):
            with self.assertRaisesRegex(ValueError, "invalid event_volume value"):
                _fetch_recent_live_sample(adapter=adapter, max_days_back=2)  # type: ignore[arg-type]

    def test_curated_insider_probe_returns_first_case_with_insider_records(self) -> None:
        class _Result:
            def __init__(self, records: list[dict[str, str]]) -> None:
                self.normalized_records = records

        class _Adapter:
            def _is_major_activity_route_unavailable(self, exc: BaseException) -> bool:
                return isinstance(exc, RuntimeError) and "route unavailable" in str(exc)

        adapter = _Adapter()
        attempts: list[tuple[tuple[str, ...], date, date]] = []

        def fake_fetch(_adapter: object, request: SourceRequest) -> _Result:
            attempts.append((request.symbols or (), request.start_date, request.end_date))
            if len(attempts) == 1:
                raise RuntimeError("route unavailable first probe")
            return _Result(
                [
                    {
                        "symbol": "430489.BJ",
                        "event_type": "insider_holding_change",
                    }
                ]
            )

        with patch(f"{__name__}.fetch_source_result", side_effect=fake_fetch):
            result, last_exc, probe = _fetch_curated_insider_live_sample(  # type: ignore[arg-type]
                adapter=adapter
            )

        self.assertIsNotNone(result)
        self.assertIsNone(last_exc)
        self.assertEqual(
            attempts,
            [
                (("001308.SZ",), date(2024, 9, 1), date(2024, 9, 30)),
                (("430489.BJ",), date(2023, 7, 1), date(2023, 7, 31)),
            ],
        )
        self.assertEqual(probe, (("430489.BJ",), date(2023, 7, 1), date(2023, 7, 31)))


class AkshareAShareMajorActivityEventsLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_a_share_major_activity_events_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareAShareMajorActivityEventsAdapter()
        registry = DatasetRegistry()
        successful_result, last_unavailable_exc, successful_window = _fetch_recent_live_sample(
            adapter=adapter,
            window_days=3,
            max_days_back=30,
        )
        if successful_result is None:
            if last_unavailable_exc is not None:
                self.skipTest(
                    "live AKShare A-share major-activity source unavailable in current environment "
                    "for recent bounded trade dates: "
                    f"{type(last_unavailable_exc).__name__}: {last_unavailable_exc}"
                )
            self.skipTest(
                "live AKShare A-share major-activity source returned no usable bounded sample records "
                "within recent 30 days"
            )

        self.assertIsNotNone(successful_window)
        window_start, window_end = successful_window  # type: ignore[misc]
        first_record = successful_result.normalized_records[0]
        self.assertEqual(
            registry.validate_record(DatasetName.MAJOR_ACTIVITY_EVENTS, first_record),
            (),
        )
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(first_record["market"], "A_SHARE")
        self.assertRegex(first_record["symbol"], r"^\d{6}\.(SH|SZ|BJ)$")
        self.assertIn(first_record["event_type"], {"block_trade", "block_trade_summary"})
        self.assertIn(first_record["source_route"], {"stock_dzjy_mrmx", "stock_dzjy_mrtj"})
        self.assertIsInstance(first_record["event_value"], (int, float))
        self.assertIsInstance(first_record["event_volume"], (int, float))
        self.assertIsNotNone(re.match(r"^\d{4}-\d{2}-\d{2}$", first_record["event_date"]))
        event_dates = {record["event_date"] for record in successful_result.normalized_records}
        self.assertTrue(event_dates)
        self.assertTrue(
            all(window_start.isoformat() <= event_date <= window_end.isoformat() for event_date in event_dates)
        )
        source_routes = {record["source_route"] for record in successful_result.normalized_records}
        self.assertIn("stock_dzjy_mrmx", source_routes)
        self.assertIn("stock_dzjy_mrtj", source_routes)

    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_a_share_insider_holding_change_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareAShareMajorActivityEventsAdapter()
        registry = DatasetRegistry()
        successful_result, last_unavailable_exc, probe = _fetch_curated_insider_live_sample(
            adapter=adapter
        )
        if successful_result is None:
            if last_unavailable_exc is not None:
                self.skipTest(
                    "live AKShare A-share insider-holding-change source unavailable in current "
                    f"environment for curated symbol windows: {type(last_unavailable_exc).__name__}: "
                    f"{last_unavailable_exc}"
                )
            self.skipTest(
                "live AKShare A-share insider-holding-change source returned no usable records "
                "for curated symbol windows"
            )

        self.assertIsNotNone(probe)
        symbols, window_start, window_end = probe  # type: ignore[misc]
        insider_records = [
            record
            for record in successful_result.normalized_records
            if record["event_type"] == "insider_holding_change"
        ]
        self.assertTrue(insider_records)

        for record in insider_records:
            self.assertEqual(
                registry.validate_record(DatasetName.MAJOR_ACTIVITY_EVENTS, record),
                (),
            )
            self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
            self.assertEqual(record["market"], "A_SHARE")
            self.assertIn(record["symbol"], symbols)
            self.assertIn(
                record["source_route"],
                {
                    "stock_share_hold_change_sse",
                    "stock_share_hold_change_szse",
                    "stock_share_hold_change_bse",
                },
            )
            self.assertIn(record["direction"], {"buy", "sell"})
            self.assertGreater(record["event_volume"], 0.0)
            self.assertGreaterEqual(record["event_date"], window_start.isoformat())
            self.assertLessEqual(record["event_date"], window_end.isoformat())


if __name__ == "__main__":
    unittest.main()
