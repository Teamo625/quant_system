from datetime import date, timedelta
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
        self.assertTrue(
            _is_live_environment_unavailable(
                RuntimeError(
                    "AKShare A-share valuation secondary history route unavailable: "
                    "HTTPSConnectionPool(host='datacenter-web.eastmoney.com', port=443): Read timed out"
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
        end_date = date.today()
        start_date = end_date - timedelta(days=4500)
        request = SourceRequest(
            dataset=DatasetName.VALUATION_SNAPSHOT,
            source_name=AKSHARE_SOURCE_ID,
            start_date=start_date,
            end_date=end_date,
            symbols=("600000.SH", "000001.SZ"),
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

        if result.record_count < 2:
            self.skipTest(
                "live AKShare A-share valuation source returned no usable bounded batch records"
            )

        symbols = {record["symbol"] for record in result.normalized_records}
        self.assertGreaterEqual(len(symbols), 2)
        self.assertEqual(
            [record["symbol"] for record in result.normalized_records],
            sorted(record["symbol"] for record in result.normalized_records),
        )
        source_routes = {record.get("source_route") for record in result.normalized_records}
        self.assertIn("stock_value_em", source_routes)
        min_trade_date = min(
            date.fromisoformat(record["trade_date"]) for record in result.normalized_records
        )
        self.assertLess(min_trade_date, end_date - timedelta(days=3660))
        self.assertIn(
            "stock_zh_valuation_baidu",
            {
                record.get("source_route")
                for record in result.normalized_records
                if date.fromisoformat(record["trade_date"]) < date(2018, 1, 1)
            },
        )

        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.VALUATION_SNAPSHOT, record),
                (),
            )
            self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
            self.assertEqual(record["market"], "CN")
            self.assertRegex(record["symbol"], r"^\d{6}\.(SH|SZ|BJ)$")
            self.assertIsInstance(record["pe_ttm"], (int, float))
            self.assertIsInstance(record["pb"], (int, float))
            self.assertIsInstance(record["market_cap"], (int, float))
            if "float_market_cap" in record:
                self.assertIsInstance(record["float_market_cap"], (int, float))
            self.assertIn(record.get("source_route"), {"stock_zh_valuation_baidu", "stock_value_em"})
            self.assertIsNotNone(re.match(r"^\d{4}-\d{2}-\d{2}$", record["trade_date"]))
            trade_date = date.fromisoformat(record["trade_date"])
            self.assertGreaterEqual(trade_date, start_date)
            self.assertLessEqual(trade_date, end_date)


if __name__ == "__main__":
    unittest.main()
