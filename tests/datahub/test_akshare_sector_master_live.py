import os
import socket
import unittest
from typing import Iterable

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareSectorMasterAdapter,
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
        "eastmoney",
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
        if isinstance(cause, (socket.timeout, TimeoutError, ConnectionError)):
            return True
        if isinstance(cause, OSError):
            if cause.errno in {101, 110, 111, 113}:
                return True
            if any(token in message for token in network_message_tokens):
                return True

    return False


class AkshareSectorMasterLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_sector_master_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareSectorMasterAdapter()
        registry = DatasetRegistry()

        candidate_filters = ("INDUSTRY", "CONCEPT")
        network_failures: list[str] = []
        empty_results: list[str] = []

        for sector_type in candidate_filters:
            request = SourceRequest(
                dataset=DatasetName.SECTOR_MASTER,
                source_name=AKSHARE_SOURCE_ID,
                symbols=(sector_type,),
            )

            try:
                result = fetch_source_result(adapter, request)
            except Exception as exc:
                if _is_live_environment_unavailable(exc):
                    network_failures.append(
                        f"{sector_type} -> {type(exc).__name__}: {exc}"
                    )
                    continue
                raise

            if result.record_count < 1:
                empty_results.append(sector_type)
                continue

            first_record = result.normalized_records[0]
            issues = registry.validate_record(DatasetName.SECTOR_MASTER, first_record)
            self.assertEqual(issues, ())
            self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
            self.assertTrue(
                first_record["sector_id"].startswith(f"{first_record['sector_type']}:"),
            )
            return

        if network_failures:
            evidence = " | ".join(network_failures[:2])
            if len(network_failures) > 2:
                evidence = f"{evidence} | ... total={len(network_failures)} failures"
            self.skipTest(
                "live AKShare sector-master source unavailable in current environment: "
                f"{evidence}"
            )

        if empty_results:
            self.skipTest(
                "live AKShare sector-master source returned no usable bounded sample records "
                f"for filters={empty_results}"
            )

        self.skipTest("live AKShare sector-master source returned no usable route")


if __name__ == "__main__":
    unittest.main()
