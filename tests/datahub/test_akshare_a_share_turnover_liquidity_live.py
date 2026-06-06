import os
import re
import socket
import unittest
from datetime import date, timedelta
from typing import Iterable

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareCapitalFlowSnapshotAdapter,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceRequest, fetch_source_result


LIVE_TESTS_ENABLED = os.getenv("QUANT_SYSTEM_LIVE_TESTS") == "1"
_NON_ENVIRONMENT_FAILURE_MESSAGE_TOKENS = (
    "unexpected keyword argument",
    "got an unexpected keyword argument",
    "missing required positional argument",
    "missing 1 required positional argument",
    "required positional argument",
    "missing required keyword-only argument",
    "missing 1 required keyword-only argument",
    "got multiple values for argument",
    "takes 0 positional arguments but",
    "takes 1 positional argument but",
    "takes 2 positional arguments but",
    "takes 3 positional arguments but",
)
_ENVIRONMENT_MESSAGE_TOKENS = (
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
    "ssl",
    "tls",
    "certificate verify failed",
    "remote disconnected",
    "remote end closed connection without response",
    "service unavailable",
    "temporarily unavailable",
    "bad gateway",
    "gateway timeout",
    "source unavailable",
    "upstream unavailable",
    "eastmoney",
    "push2his.eastmoney.com",
)


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

    for cause in _exception_chain(exc):
        message = str(cause).lower()
        if isinstance(cause, TypeError):
            return False
        if any(token in message for token in _NON_ENVIRONMENT_FAILURE_MESSAGE_TOKENS):
            return False

    for cause in _exception_chain(exc):
        name = type(cause).__name__
        module = type(cause).__module__
        message = str(cause).lower()

        if name in network_exception_names:
            return True
        if module.startswith(("requests", "urllib3")) and any(
            token in message for token in _ENVIRONMENT_MESSAGE_TOKENS
        ):
            return True
        if any(token in message for token in _ENVIRONMENT_MESSAGE_TOKENS):
            return True
        if isinstance(cause, (socket.timeout, TimeoutError, ConnectionError)):
            return True
        if isinstance(cause, OSError):
            if cause.errno in {101, 104, 110, 111, 113}:
                return True
            if any(token in message for token in _ENVIRONMENT_MESSAGE_TOKENS):
                return True
    return False


class AkshareAShareTurnoverLiquidityLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        self.assertTrue(
            _is_live_environment_unavailable(
                RuntimeError("AKShare turnover/liquidity source unavailable: ProxyError")
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(ValueError("Invalid turnover_rate value"))
        )

    def test_classifier_keeps_route_signature_failures_as_non_environment_issue(self) -> None:
        try:
            try:
                raise TypeError(
                    "stock_zh_a_hist() got an unexpected keyword argument 'market'"
                )
            except TypeError as exc:
                raise RuntimeError("AKShare turnover/liquidity source unavailable") from exc
        except RuntimeError as exc:
            self.assertFalse(_is_live_environment_unavailable(exc))

    def test_classifier_keeps_route_name_only_message_as_non_environment_issue(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(
                RuntimeError("stock_zh_a_hist returned malformed payload")
            )
        )

    def test_classifier_marks_upstream_service_unavailable_as_environment_issue(self) -> None:
        self.assertTrue(
            _is_live_environment_unavailable(
                RuntimeError(
                    "AKShare turnover/liquidity source unavailable: "
                    "503 Service Unavailable from Eastmoney upstream"
                )
            )
        )


class AkshareAShareTurnoverLiquidityLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_a_share_turnover_liquidity_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareAShareCapitalFlowSnapshotAdapter()
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("600000.SH", "000001.SZ"),
            start_date=date.today() - timedelta(days=45),
            end_date=date.today(),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc):
                self.skipTest(
                    "live AKShare A-share turnover/liquidity source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 2:
            self.skipTest(
                "live AKShare A-share turnover/liquidity source returned no usable bounded batch records"
            )

        symbols = {record["symbol"] for record in result.normalized_records}
        if len(symbols) < 2:
            self.skipTest(
                "live AKShare A-share turnover/liquidity source did not return usable records for at least two symbols"
            )

        self.assertEqual(
            [record["symbol"] for record in result.normalized_records],
            sorted(record["symbol"] for record in result.normalized_records),
        )

        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT, record),
                (),
            )
            self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
            self.assertEqual(record["source_route"], "stock_zh_a_hist")
            self.assertEqual(record["market"], "CN")
            self.assertEqual(record["metric_granularity"], "daily")
            self.assertRegex(record["symbol"], r"^\d{6}\.(SH|SZ|BJ)$")
            self.assertIsInstance(record["volume"], (int, float))
            self.assertIsInstance(record["amount"], (int, float))
            self.assertIsInstance(record["turnover_rate"], (int, float))
            self.assertIsNotNone(re.match(r"^\d{4}-\d{2}-\d{2}$", record["trade_date"]))
            trade_date = date.fromisoformat(record["trade_date"])
            self.assertGreaterEqual(trade_date, request.start_date)
            self.assertLessEqual(trade_date, request.end_date)


if __name__ == "__main__":
    unittest.main()
