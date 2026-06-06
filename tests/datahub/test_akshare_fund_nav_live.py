import os
import socket
import unittest
from datetime import date
from typing import Iterable

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareETFFundNavSnapshotAdapter,
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
        "fundf10.eastmoney.com",
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


class AkshareETFFundNavSnapshotLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_fund_nav_snapshot_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareETFFundNavSnapshotAdapter()
        registry = DatasetRegistry()
        recent_request = SourceRequest(
            dataset=DatasetName.FUND_NAV_SNAPSHOT,
            source_name=AKSHARE_SOURCE_ID,
            start_date=date(2024, 1, 2),
            end_date=date(2024, 1, 10),
            symbols=("510300.ETF_CN", "000001.FUND_CN"),
        )
        historical_request = SourceRequest(
            dataset=DatasetName.FUND_NAV_SNAPSHOT,
            source_name=AKSHARE_SOURCE_ID,
            start_date=date(2001, 12, 18),
            end_date=date(2002, 1, 15),
            symbols=("000001.FUND_CN",),
        )

        try:
            recent_result = fetch_source_result(adapter, recent_request)
            historical_result = fetch_source_result(adapter, historical_request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc):
                self.skipTest(
                    "live AKShare ETF/fund NAV source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if recent_result.record_count < 2:
            self.skipTest(
                "live AKShare ETF/fund NAV source returned insufficient bounded "
                "sample records for requested multi-symbol batch"
            )

        returned_symbols = {record["fund_code"] for record in recent_result.normalized_records}
        self.assertEqual(returned_symbols, {"000001.FUND_CN", "510300.ETF_CN"})
        returned_markets = {record["market"] for record in recent_result.normalized_records}
        self.assertEqual(returned_markets, {"ETF_CN", "FUND_CN"})
        first_record = recent_result.normalized_records[0]
        issues = registry.validate_record(DatasetName.FUND_NAV_SNAPSHOT, first_record)
        self.assertEqual(issues, ())
        self.assertGreaterEqual(historical_result.record_count, 1)
        self.assertEqual(
            historical_result.normalized_records[0]["trade_date"],
            "2001-12-18",
        )
        self.assertEqual(
            historical_result.normalized_records[0]["fund_code"],
            "000001.FUND_CN",
        )


if __name__ == "__main__":
    unittest.main()
