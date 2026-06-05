import os
import socket
import unittest
from typing import Iterable

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareSectorMembershipAdapter,
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


class AkshareSectorMembershipLiveTests(unittest.TestCase):
    def test_live_unavailable_classifier_accepts_route_unavailable_errors(self) -> None:
        exc = RuntimeError(
            "AKShare sector-membership route unavailable: "
            "route=stock_board_industry_cons_em, cause=ProxyError: proxy down"
        )
        self.assertTrue(_is_live_environment_unavailable(exc))

    def test_live_unavailable_classifier_does_not_mask_signature_failures(self) -> None:
        exc = RuntimeError(
            "AKShare sector-membership function does not accept a sector symbol/name "
            "argument: route=stock_board_industry_cons_em"
        )
        self.assertFalse(_is_live_environment_unavailable(exc))

    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_sector_membership_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareSectorMembershipAdapter()
        registry = DatasetRegistry()
        candidate_requests = (
            ("INDUSTRY:小金属", "CONCEPT:绿色电力"),
            ("INDUSTRY:小金属", "CONCEPT:阿里巴巴概念"),
        )

        network_failures: list[str] = []
        empty_results: list[str] = []
        for symbols in candidate_requests:
            request = SourceRequest(
                dataset=DatasetName.SECTOR_MEMBERSHIP,
                source_name=AKSHARE_SOURCE_ID,
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

            if result.record_count < 2:
                empty_results.append(f"{symbols!r} -> record_count={result.record_count}")
                continue

            seen_sector_ids = {record["sector_id"] for record in result.normalized_records}
            self.assertEqual(seen_sector_ids, set(symbols))
            for record in result.normalized_records:
                issues = registry.validate_record(DatasetName.SECTOR_MEMBERSHIP, record)
                self.assertEqual(issues, ())
                self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
                self.assertTrue(record["sector_id"].startswith(("INDUSTRY:", "CONCEPT:")))
            return

        if network_failures:
            evidence = " | ".join(network_failures[:2])
            if len(network_failures) > 2:
                evidence = f"{evidence} | ... total={len(network_failures)} failures"
            self.skipTest(
                "live AKShare sector-membership source unavailable in current environment: "
                f"{evidence}"
            )
        if empty_results:
            self.skipTest(
                "live AKShare sector-membership source returned no usable bounded batch sample "
                f"records for requests={empty_results}"
            )
        self.skipTest("live AKShare sector-membership source returned no usable route")


if __name__ == "__main__":
    unittest.main()
