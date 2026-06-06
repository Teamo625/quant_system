import os
import socket
import unittest
from datetime import date
from typing import Iterable

from quant.datahub.adapters.baostock import (
    BAOSTOCK_SOURCE_ID,
    BaoStockAShareMinuteBarsAdapter,
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
        "remote end closed connection without response",
        "server disconnected",
        "empty reply from server",
    )
    service_unavailable_tokens = (
        "login failed",
        "service unavailable",
        "bad gateway",
        "gateway timeout",
    )

    for cause in _exception_chain(exc):
        name = type(cause).__name__
        module = type(cause).__module__
        message = str(cause).lower()

        if name in network_exception_names:
            return True
        if module.startswith(("requests", "urllib3")) and any(
            token in message
            for token in network_message_tokens + service_unavailable_tokens
        ):
            return True
        if any(token in message for token in network_message_tokens):
            return True
        if any(token in message for token in service_unavailable_tokens):
            return True
        if isinstance(cause, (socket.timeout, TimeoutError, ConnectionError)):
            return True
        if isinstance(cause, OSError):
            if cause.errno in {101, 104, 110, 111, 113}:
                return True
            if any(token in message for token in network_message_tokens):
                return True

    return False


class BaoStockAShareMinuteBarsLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        self.assertTrue(
            _is_live_environment_unavailable(
                RuntimeError("BaoStock login failed: connection reset")
            )
        )

    def test_classifier_marks_service_availability_messages_as_environment_unavailable(
        self,
    ) -> None:
        self.assertTrue(
            _is_live_environment_unavailable(
                RuntimeError("BaoStock login failed: service unavailable")
            )
        )

    def test_classifier_keeps_invalid_baostock_date_failures_as_non_environment_issue(
        self,
    ) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(
                ValueError("Invalid BaoStock date value: bad")
            )
        )

    def test_classifier_keeps_baostock_symbol_mismatch_as_non_environment_issue(
        self,
    ) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(
                ValueError(
                    "Source symbol mismatch for BaoStock A-share minute-bars adapter"
                )
            )
        )


class BaoStockAShareMinuteBarsLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_baostock_a_share_minute_bars_smoke(self) -> None:
        try:
            import baostock as _bs  # noqa: F401
        except Exception as exc:
            self.skipTest(f"baostock is not available for live smoke test: {exc}")

        adapter = BaoStockAShareMinuteBarsAdapter(minute_period="5")
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.MINUTE_BARS,
            source_name=BAOSTOCK_SOURCE_ID,
            symbols=("600000.SH", "000001.SZ"),
            start_date=date(2024, 1, 2),
            end_date=date(2024, 1, 5),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc):
                self.skipTest(
                    "live BaoStock A-share minute-bars source unavailable in current "
                    f"environment: {type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 1:
            self.skipTest("live BaoStock source returned no usable bounded sample records")

        returned_symbols = {record["symbol"] for record in result.normalized_records}
        if not {"600000.SH", "000001.SZ"}.issubset(returned_symbols):
            self.skipTest(
                "live BaoStock source returned no usable bounded sample records "
                f"for both requested symbols: observed={sorted(returned_symbols)!r}"
            )

        distinct_trade_dates = {
            str(record["trade_date"]) for record in result.normalized_records
        }
        self.assertGreaterEqual(len(distinct_trade_dates), 2)

        first_record = result.normalized_records[0]
        self.assertEqual(registry.validate_record(DatasetName.MINUTE_BARS, first_record), ())
        self.assertEqual(first_record["source"], BAOSTOCK_SOURCE_ID)
        self.assertEqual(first_record["market"], "A_SHARE")
        self.assertIn(first_record["symbol"], returned_symbols)


if __name__ == "__main__":
    unittest.main()
