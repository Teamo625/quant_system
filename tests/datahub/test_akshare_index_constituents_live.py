import os
import socket
import unittest
from typing import Iterable

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareIndexConstituentsAdapter,
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
        "route unavailable",
        "sina.com",
        "csindex.com.cn",
        "sse.com.cn",
        "szse.cn",
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


class AkshareIndexConstituentsLiveTests(unittest.TestCase):
    def test_live_unavailable_classifier_accepts_route_unavailable_errors(self) -> None:
        exc = RuntimeError(
            "AKShare index constituents route unavailable: "
            "route=index_stock_cons_weight_csindex, symbol='000300', "
            "cause=ProxyError: proxy down"
        )
        self.assertTrue(_is_live_environment_unavailable(exc))

    def test_live_unavailable_classifier_does_not_mask_signature_failures(self) -> None:
        exc = RuntimeError(
            "AKShare index constituents function does not accept required argument: "
            "route=index_stock_cons_weight_csindex, field=symbol"
        )
        self.assertFalse(_is_live_environment_unavailable(exc))

    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_index_constituents_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareIndexConstituentsAdapter()
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.INDEX_CONSTITUENTS,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("000300.CN_INDEX", "399001.CN_INDEX"),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc):
                self.skipTest(
                    "live AKShare index-constituents source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 2:
            self.skipTest(
                "live AKShare index-constituents source returned insufficient bounded sample records"
            )

        seen_codes = {record["index_code"] for record in result.normalized_records}
        self.assertEqual(seen_codes, {"000300.CN_INDEX", "399001.CN_INDEX"})

        seen_with_effective_dates: set[str] = set()
        for record in result.normalized_records:
            issues = registry.validate_record(DatasetName.INDEX_CONSTITUENTS, record)
            self.assertEqual(issues, ())
            self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
            self.assertEqual(record["market"], "CN_A")
            if record["in_date"] != "1900-01-01":
                seen_with_effective_dates.add(record["index_code"])

        self.assertIn("000300.CN_INDEX", seen_with_effective_dates)

    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_index_constituents_star50_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareIndexConstituentsAdapter()
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.INDEX_CONSTITUENTS,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("000688.CN_INDEX",),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc):
                self.skipTest(
                    "live AKShare STAR 50 constituents source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 1:
            self.skipTest("live AKShare STAR 50 constituents source returned no usable records")

        self.assertEqual(
            {record["index_code"] for record in result.normalized_records},
            {"000688.CN_INDEX"},
        )
        self.assertTrue(
            any(record["in_date"] != "1900-01-01" for record in result.normalized_records)
        )
        self.assertTrue(any("weight" in record for record in result.normalized_records))

        for record in result.normalized_records:
            issues = registry.validate_record(DatasetName.INDEX_CONSTITUENTS, record)
            self.assertEqual(issues, ())
            self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
            self.assertEqual(record["market"], "CN_A")


if __name__ == "__main__":
    unittest.main()
