import os
import socket
import unittest
from datetime import date
from typing import Iterable

from quant.datahub.adapters.akshare import AKSHARE_SOURCE_ID, AkshareHKDailyBarAdapter
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
        "push2his.eastmoney.com",
        "33.push2his.eastmoney.com",
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
        if isinstance(cause, (socket.timeout, TimeoutError, ConnectionError)):
            return True
        if isinstance(cause, OSError):
            if cause.errno in {101, 110, 111, 113}:
                return True
            if any(token in message for token in network_message_tokens):
                return True

    return False


class AkshareHKDailyBarLiveTests(unittest.TestCase):
    def _assert_bounded_live_records(
        self,
        *,
        result,
        expected_symbols: set[str],
        start_date: date,
        end_date: date,
    ) -> None:
        registry = DatasetRegistry()
        self.assertGreaterEqual(result.record_count, len(expected_symbols))
        returned_symbols = {
            str(record["symbol"]) for record in result.normalized_records
        }
        self.assertEqual(returned_symbols, expected_symbols)
        for record in result.normalized_records:
            issues = registry.validate_record(DatasetName.DAILY_BARS, record)
            self.assertEqual(issues, ())
            trade_date = date.fromisoformat(str(record["trade_date"]))
            self.assertGreaterEqual(trade_date, start_date)
            self.assertLessEqual(trade_date, end_date)

    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_hk_daily_bars_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareHKDailyBarAdapter(price_adjustment="raw")
        start_date = date(2019, 1, 2)
        end_date = date(2019, 1, 15)
        request = SourceRequest(
            dataset=DatasetName.DAILY_BARS,
            source_name=AKSHARE_SOURCE_ID,
            start_date=start_date,
            end_date=end_date,
            symbols=("00700.HK", "00005.HK"),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc):
                self.skipTest(
                    "live AKShare HK source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 1:
            self.skipTest("live AKShare HK source returned no usable bounded sample records")

        self._assert_bounded_live_records(
            result=result,
            expected_symbols={"00700.HK", "00005.HK"},
            start_date=start_date,
            end_date=end_date,
        )

    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_hk_daily_bars_real_fallback_route_smoke(self) -> None:
        try:
            import akshare as ak
        except Exception as exc:
            self.skipTest(f"akshare is not available for live fallback smoke test: {exc}")

        def force_hist_unavailable(**kwargs):
            raise ConnectionError("synthetic stock_hk_hist outage for fallback smoke")

        adapter = AkshareHKDailyBarAdapter(
            fetch_hk_hist=force_hist_unavailable,
            fetch_hk_daily=ak.stock_hk_daily,
            price_adjustment="raw",
        )
        start_date = date(2019, 1, 2)
        end_date = date(2019, 1, 15)
        request = SourceRequest(
            dataset=DatasetName.DAILY_BARS,
            source_name=AKSHARE_SOURCE_ID,
            start_date=start_date,
            end_date=end_date,
            symbols=("00700.HK", "00005.HK"),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc):
                self.skipTest(
                    "live AKShare HK fallback route unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 1:
            self.skipTest("live AKShare HK fallback route returned no usable bounded sample records")

        self._assert_bounded_live_records(
            result=result,
            expected_symbols={"00700.HK", "00005.HK"},
            start_date=start_date,
            end_date=end_date,
        )
