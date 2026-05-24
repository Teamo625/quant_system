import os
import re
import socket
import unittest
from typing import Iterable

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareValuationSnapshotAdapter,
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
        "baidu.com",
        "gushitong.baidu.com",
        "eastmoney",
        "push2.eastmoney.com",
        "market-cap route unavailable",
        "primary route unavailable",
        "stock_zh_valuation_baidu",
        "stock_individual_info_em",
        "stock_zh_valuation_comparison_em",
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
            if cause.errno in {101, 110, 111, 113}:
                return True
            if any(token in message for token in network_message_tokens):
                return True

    return False


class AkshareAShareValuationSnapshotLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        self.assertTrue(
            _is_live_environment_unavailable(
                RuntimeError(
                    "AKShare A-share valuation market-cap route unavailable: "
                    "ProxyError: proxy down"
                )
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        self.assertFalse(_is_live_environment_unavailable(ValueError("Invalid pe_ttm value")))


class AkshareAShareValuationSnapshotLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_a_share_valuation_snapshot_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareAShareValuationSnapshotAdapter()
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.VALUATION_SNAPSHOT,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("600000.SH",),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc) or adapter._is_valuation_network_unavailable(  # pylint: disable=protected-access
                exc
            ):
                self.skipTest(
                    "live AKShare A-share valuation source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 1:
            self.skipTest(
                "live AKShare A-share valuation source returned no usable bounded sample records"
            )

        first_record = result.normalized_records[0]
        self.assertEqual(
            registry.validate_record(DatasetName.VALUATION_SNAPSHOT, first_record),
            (),
        )
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(first_record["market"], "CN")
        self.assertRegex(first_record["symbol"], r"^\d{6}\.(SH|SZ|BJ)$")
        self.assertIsInstance(first_record["pe_ttm"], (int, float))
        self.assertIsInstance(first_record["pb"], (int, float))
        self.assertIsInstance(first_record["market_cap"], (int, float))
        if "float_market_cap" in first_record:
            self.assertIsInstance(first_record["float_market_cap"], (int, float))
        self.assertIsNotNone(re.match(r"^\d{4}-\d{2}-\d{2}$", first_record["trade_date"]))


if __name__ == "__main__":
    unittest.main()
