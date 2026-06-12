import os
import socket
import unittest
from datetime import date, timedelta
from typing import Iterable

from quant.datahub.adapters.akshare import AKSHARE_SOURCE_ID, AkshareHKMinuteBarsAdapter
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
        "RemoteDisconnected",
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
        "connection reset",
        "dns",
        "eastmoney",
        "push2his.eastmoney.com",
        "emweb.securities.eastmoney.com",
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


class AkshareHKMinuteBarsLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        self.assertTrue(
            _is_live_environment_unavailable(
                RuntimeError(
                    "AKShare HK minute-bars route unavailable: ProxyError: proxy down"
                )
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(ValueError("Invalid close value"))
        )

    def test_classifier_keeps_route_signature_compatibility_errors_as_failures(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(
                RuntimeError(
                    "AKShare HK minute-bars route does not accept required argument: "
                    "route=stock_hk_hist_min_em, field=start_date"
                )
            )
        )


class AkshareHKMinuteBarsLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_hk_minute_bars_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live HK minute-bar smoke: {exc}")

        adapter = AkshareHKMinuteBarsAdapter(minute_period="5", price_adjustment="raw")
        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=4)
        request = SourceRequest(
            dataset=DatasetName.MINUTE_BARS,
            source_name=AKSHARE_SOURCE_ID,
            start_date=start_date,
            end_date=end_date,
            symbols=("00700.HK", "00005.HK"),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc) or adapter._is_hk_minute_network_unavailable(  # pylint: disable=protected-access
                exc
            ):
                self.skipTest(
                    "live AKShare HK minute-bars source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 1:
            self.skipTest("live AKShare HK minute-bars source returned no usable bounded sample")

        registry = DatasetRegistry()
        returned_symbols = {
            str(record["symbol"]) for record in result.normalized_records
        }
        self.assertEqual(returned_symbols, {"00700.HK", "00005.HK"})
        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.MINUTE_BARS, record),
                (),
            )
            trade_date = date.fromisoformat(str(record["trade_date"]))
            bar_time = str(record["bar_time"])
            self.assertGreaterEqual(trade_date, start_date)
            self.assertLessEqual(trade_date, end_date)
            self.assertEqual(record["market"], "HK")
            self.assertTrue(bar_time.startswith(str(trade_date)))
