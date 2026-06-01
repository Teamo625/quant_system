import os
import re
import socket
import unittest
from datetime import date, timedelta
from typing import Iterable

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareMarginFinancingLendingAdapter,
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
        "sse.com.cn",
        "szse.cn",
        "querymargin.do",
        "showreport",
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


class AkshareAShareMarginFinancingLendingLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        self.assertTrue(
            _is_live_environment_unavailable(
                RuntimeError("AKShare margin route unavailable: ProxyError: proxy down")
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(ValueError("Invalid financing_balance value"))
        )

    def test_classifier_keeps_route_signature_compatibility_errors_as_failures(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(
                RuntimeError(
                    "AKShare A-share margin-detail route does not accept required argument: "
                    "route=stock_margin_detail_sse, field=date"
                )
            )
        )


class AkshareAShareMarginFinancingLendingLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_a_share_margin_financing_lending_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareAShareMarginFinancingLendingAdapter()
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.MARGIN_FINANCING_LENDING,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("600000.SH",),
            start_date=date.today() - timedelta(days=45),
            end_date=date.today(),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc) or adapter._is_margin_route_unavailable(  # pylint: disable=protected-access
                exc
            ):
                self.skipTest(
                    "live AKShare A-share margin financing/lending source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 1:
            self.skipTest(
                "live AKShare A-share margin financing/lending source returned no usable bounded sample records"
            )

        first_record = result.normalized_records[0]
        self.assertEqual(
            registry.validate_record(DatasetName.MARGIN_FINANCING_LENDING, first_record),
            (),
        )
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(first_record["market"], "A_SHARE")
        self.assertRegex(first_record["symbol"], r"^\d{6}\.(SH|SZ|BJ)$")
        self.assertIsInstance(first_record["financing_balance"], (int, float))
        self.assertIsNotNone(re.match(r"^\d{4}-\d{2}-\d{2}$", first_record["trade_date"]))


if __name__ == "__main__":
    unittest.main()
