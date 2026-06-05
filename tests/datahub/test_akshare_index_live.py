import os
import socket
import unittest
from datetime import date
from typing import Iterable

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareIndexDailyBarAdapter,
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
        "route unavailable",
        "eastmoney",
        "qt.gtimg.cn",
        "sina.com",
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


class AkshareIndexDailyBarLiveTests(unittest.TestCase):
    def test_live_unavailable_classifier_accepts_route_unavailable_errors(self) -> None:
        exc = RuntimeError(
            "AKShare index daily-bar route unavailable: "
            "route=stock_zh_index_daily_tx, symbol='sh000300', "
            "cause=ProxyError: proxy down"
        )
        self.assertTrue(_is_live_environment_unavailable(exc))

    def test_live_unavailable_classifier_does_not_mask_signature_failures(self) -> None:
        exc = RuntimeError(
            "AKShare index daily-bar function does not accept required argument: "
            "route=stock_zh_index_daily_tx, field=symbol"
        )
        self.assertFalse(_is_live_environment_unavailable(exc))

    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_index_daily_bars_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareIndexDailyBarAdapter()
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.INDEX_DAILY_BARS,
            source_name=AKSHARE_SOURCE_ID,
            start_date=date(2024, 1, 2),
            end_date=date(2024, 1, 5),
            symbols=("000300.CN_INDEX", "399001.CN_INDEX"),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc):
                self.skipTest(
                    "live AKShare index source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 1:
            self.skipTest("live AKShare index source returned no usable bounded sample records")

        seen_codes = {record["index_code"] for record in result.normalized_records}
        self.assertEqual(seen_codes, {"000300.CN_INDEX", "399001.CN_INDEX"})

        for record in result.normalized_records:
            issues = registry.validate_record(DatasetName.INDEX_DAILY_BARS, record)
            self.assertEqual(issues, ())


if __name__ == "__main__":
    unittest.main()
