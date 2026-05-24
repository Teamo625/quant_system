import os
import socket
import unittest
from datetime import date
from typing import Iterable

from quant.datahub.adapters.akshare import (
    MACRO_POLICY_SOURCE_ID,
    AkshareChinaMacroAdapter,
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
        "macro_china_cpi_yearly",
        "macro_china_ppi_yearly",
        "macro_china_gdp_yearly",
        "jin10",
        "eastmoney",
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


class AkshareChinaMacroLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        self.assertTrue(
            _is_live_environment_unavailable(
                OSError(111, "connection refused to macro_china_cpi_yearly endpoint")
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        self.assertFalse(_is_live_environment_unavailable(ValueError("Invalid numeric value")))


class AkshareChinaMacroLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_china_macro_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareChinaMacroAdapter()
        registry = DatasetRegistry()

        master_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.MACRO_INDICATOR_MASTER,
                source_name=MACRO_POLICY_SOURCE_ID,
            ),
        )
        self.assertGreaterEqual(master_result.record_count, 1)
        master_first = master_result.normalized_records[0]
        self.assertEqual(
            registry.validate_record(DatasetName.MACRO_INDICATOR_MASTER, master_first),
            (),
        )
        self.assertEqual(master_first["source"], MACRO_POLICY_SOURCE_ID)

        request = SourceRequest(
            dataset=DatasetName.MACRO_OBSERVATIONS,
            source_name=MACRO_POLICY_SOURCE_ID,
            start_date=date(2018, 1, 1),
            end_date=date.today(),
        )

        try:
            observations_result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc):
                self.skipTest(
                    "live AKShare China macro source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if observations_result.record_count < 1:
            self.skipTest(
                "live AKShare China macro source returned no usable bounded sample records"
            )

        observation_first = observations_result.normalized_records[0]
        self.assertEqual(
            registry.validate_record(DatasetName.MACRO_OBSERVATIONS, observation_first),
            (),
        )
        self.assertEqual(observation_first["source"], MACRO_POLICY_SOURCE_ID)
        self.assertIn(observation_first["indicator_id"], {"CPI_CN_YOY", "PPI_CN_YOY", "GDP_CN_YOY"})


if __name__ == "__main__":
    unittest.main()
