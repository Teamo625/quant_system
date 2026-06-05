import os
import re
import socket
import unittest
from datetime import date, timedelta
from typing import Iterable, Sequence
from unittest.mock import patch

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareMinuteBarsAdapter,
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
        "sina",
        "finance.sina.com.cn",
        "quote.eastmoney.com",
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


def _unwrap_live_environment_exc(exc: BaseException) -> BaseException:
    causes = list(_exception_chain(exc))
    for cause in causes[1:]:
        if _is_live_environment_unavailable(cause):
            return cause
    if _is_live_environment_unavailable(exc):
        return exc
    return exc


def _fetch_recent_live_sample(
    *,
    adapter: AkshareAShareMinuteBarsAdapter,
    symbols: Sequence[str] = ("600000.SH", "000001.SZ"),
    max_days_back: int = 10,
) -> tuple[object | None, BaseException | None]:
    last_unavailable_exc: BaseException | None = None
    requested_symbols = tuple(symbols)

    for days_back in range(1, max_days_back + 1):
        target_date = date.today() - timedelta(days=days_back)
        request = SourceRequest(
            dataset=DatasetName.MINUTE_BARS,
            source_name=AKSHARE_SOURCE_ID,
            symbols=requested_symbols,
            start_date=target_date,
            end_date=target_date,
        )
        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc) or adapter._is_minute_bars_route_unavailable(  # pylint: disable=protected-access
                exc
            ):
                last_unavailable_exc = _unwrap_live_environment_exc(exc)
                continue
            raise

        if result.record_count <= 0:
            continue

        returned_symbols = {
            str(record["symbol"]) for record in getattr(result, "normalized_records", ())
        }
        if all(symbol in returned_symbols for symbol in requested_symbols):
            return result, None

    return None, last_unavailable_exc


def _fetch_historical_live_sample(
    *,
    adapter: AkshareAShareMinuteBarsAdapter,
    symbols: Sequence[str] = ("600000.SH",),
    end_days_back_candidates: Sequence[int] = (1, 2, 3, 4, 5, 6, 7, 10, 15),
    window_days: int = 30,
    min_trade_dates: int = 2,
) -> tuple[object | None, BaseException | None]:
    last_unavailable_exc: BaseException | None = None
    requested_symbols = tuple(symbols)

    for end_days_back in end_days_back_candidates:
        end_date = date.today() - timedelta(days=end_days_back)
        start_date = end_date - timedelta(days=window_days)
        request = SourceRequest(
            dataset=DatasetName.MINUTE_BARS,
            source_name=AKSHARE_SOURCE_ID,
            symbols=requested_symbols,
            start_date=start_date,
            end_date=end_date,
        )
        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc) or adapter._is_minute_bars_route_unavailable(  # pylint: disable=protected-access
                exc
            ):
                last_unavailable_exc = _unwrap_live_environment_exc(exc)
                continue
            raise

        if result.record_count <= 0:
            continue

        returned_symbols = {
            str(record["symbol"]) for record in getattr(result, "normalized_records", ())
        }
        if not all(symbol in returned_symbols for symbol in requested_symbols):
            continue

        distinct_trade_dates = {
            str(record["trade_date"]) for record in getattr(result, "normalized_records", ())
        }
        if len(distinct_trade_dates) < min_trade_dates:
            continue

        return result, None

    return None, last_unavailable_exc


class AkshareAShareMinuteBarsLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        self.assertTrue(
            _is_live_environment_unavailable(
                RuntimeError("AKShare minute-bars route unavailable: ProxyError: proxy down")
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        self.assertFalse(_is_live_environment_unavailable(ValueError("Invalid open value")))

    def test_classifier_keeps_route_signature_compatibility_errors_as_failures(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(
                RuntimeError(
                    "AKShare A-share minute-bars route does not accept required argument: "
                    "route=stock_zh_a_hist_min_em, field=start_date"
                )
            )
        )

    def test_recent_live_sample_probe_continues_after_unavailable_date(self) -> None:
        class _Adapter:
            def _is_minute_bars_route_unavailable(self, exc: BaseException) -> bool:
                return isinstance(exc, RuntimeError) and "route unavailable" in str(exc)

        class _Result:
            def __init__(self, count: int, symbols: Sequence[str]) -> None:
                self.record_count = count
                self.normalized_records = [{"symbol": symbol} for symbol in symbols]

        adapter = _Adapter()
        attempts: list[tuple[date | None, date | None]] = []

        def fake_fetch(_adapter: object, request: SourceRequest) -> _Result:
            attempts.append((request.start_date, request.end_date))
            if len(attempts) == 1:
                raise RuntimeError("route unavailable for this date")
            return _Result(2, ("600000.SH", "000001.SZ"))

        with patch(f"{__name__}.fetch_source_result", side_effect=fake_fetch):
            result, last_exc = _fetch_recent_live_sample(adapter=adapter, max_days_back=2)  # type: ignore[arg-type]

        self.assertIsNotNone(result)
        self.assertEqual(result.record_count, 2)  # type: ignore[union-attr]
        self.assertIsNone(last_exc)
        self.assertEqual(len(attempts), 2)


class AkshareAShareMinuteBarsLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_a_share_minute_bars_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareAShareMinuteBarsAdapter(minute_period="5")
        registry = DatasetRegistry()
        successful_result, last_unavailable_exc = _fetch_historical_live_sample(
            adapter=adapter,
            symbols=("600000.SH",),
            end_days_back_candidates=(1, 2, 3, 4, 5, 6, 7, 10, 15),
            window_days=30,
            min_trade_dates=2,
        )
        if successful_result is None:
            if last_unavailable_exc is not None:
                self.skipTest(
                    "live AKShare A-share minute-bars source unavailable in current environment "
                    "for bounded historical 5-minute trade-date windows: "
                    f"{type(last_unavailable_exc).__name__}: {last_unavailable_exc}"
                )
            self.skipTest(
                "live AKShare A-share minute-bars source returned no usable bounded historical "
                "5-minute sample with at least two distinct trade dates"
            )

        returned_symbols = {
            str(record["symbol"]) for record in successful_result.normalized_records
        }
        self.assertEqual(returned_symbols, {"600000.SH"})
        distinct_trade_dates = {
            str(record["trade_date"]) for record in successful_result.normalized_records
        }
        self.assertGreaterEqual(len(distinct_trade_dates), 2)
        first_record = successful_result.normalized_records[0]
        self.assertEqual(
            registry.validate_record(DatasetName.MINUTE_BARS, first_record),
            (),
        )
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(first_record["market"], "A_SHARE")
        self.assertIn(first_record["symbol"], returned_symbols)
        self.assertIsNotNone(re.match(r"^\d{4}-\d{2}-\d{2}T", first_record["bar_time"]))


if __name__ == "__main__":
    unittest.main()
