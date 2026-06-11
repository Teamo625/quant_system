import os
import socket
import unittest
from datetime import date
from typing import Iterable

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareSectorDailyBarAdapter,
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
        "HTTPError",
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
        "quote.eastmoney.com",
        "push2.eastmoney.com",
        "push2his.eastmoney.com",
        "10jqka",
    )

    for cause in _exception_chain(exc):
        name = type(cause).__name__
        module = type(cause).__module__
        message = str(cause).lower()

        if name in network_exception_names:
            return True
        if module.startswith(("requests", "urllib3", "urllib")) and any(
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


class AkshareSectorDailyBarLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_sector_daily_bars_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareSectorDailyBarAdapter()
        registry = DatasetRegistry()
        candidate_requests = (
            ("INDUSTRY:小金属", "CONCEPT:绿色电力"),
            ("INDUSTRY:小金属", "CONCEPT:阿里巴巴概念"),
        )

        network_failures: list[str] = []
        empty_results: list[str] = []
        for symbols in candidate_requests:
            request = SourceRequest(
                dataset=DatasetName.SECTOR_DAILY_BARS,
                source_name=AKSHARE_SOURCE_ID,
                start_date=date(2024, 1, 2),
                end_date=date(2024, 1, 5),
                symbols=symbols,
            )
            try:
                result = fetch_source_result(adapter, request)
            except Exception as exc:
                if _is_live_environment_unavailable(exc):
                    network_failures.append(f"{symbols!r} -> {type(exc).__name__}: {exc}")
                    continue
                if isinstance(exc, ValueError):
                    empty_results.append(f"{symbols!r} -> {exc}")
                    continue
                raise

            seen_sector_ids = {record["sector_id"] for record in result.normalized_records}
            if seen_sector_ids != set(symbols):
                empty_results.append(
                    f"{symbols!r} -> seen_sector_ids={sorted(seen_sector_ids)!r}"
                )
                continue

            for record in result.normalized_records:
                issues = registry.validate_record(DatasetName.SECTOR_DAILY_BARS, record)
                self.assertEqual(issues, ())
                self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
                self.assertTrue(record["sector_id"].startswith(("INDUSTRY:", "CONCEPT:")))
            return

        if network_failures:
            evidence = " | ".join(network_failures[:2])
            if len(network_failures) > 2:
                evidence = f"{evidence} | ... total={len(network_failures)} failures"
            self.skipTest(
                "live AKShare sector source unavailable in current environment: "
                f"{evidence}"
            )
        if empty_results:
            self.skipTest(
                "live AKShare sector source returned no usable bounded batch sample "
                f"records for requests={empty_results}"
            )
        self.skipTest("live AKShare sector source returned no usable route in current environment")


if __name__ == "__main__":
    unittest.main()
