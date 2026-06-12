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
    "remote disconnected",
    "service unavailable",
    "temporarily unavailable",
    "bad gateway",
    "gateway timeout",
    "source unavailable",
    "upstream unavailable",
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
            if cause.errno in {101, 110, 111, 113}:
                return True
            if any(token in message for token in _ENVIRONMENT_MESSAGE_TOKENS):
                return True
    return False


class AkshareAShareNorthboundFlowLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        self.assertTrue(
            _is_live_environment_unavailable(
                RuntimeError("AKShare northbound source unavailable: ProxyError")
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(ValueError("Invalid northbound_shares_held value"))
        )

    def test_classifier_keeps_route_signature_failures_as_non_environment_issue(self) -> None:
        try:
            try:
                raise TypeError(
                    "stock_hsgt_individual_em() got an unexpected keyword argument 'market'"
                )
            except TypeError as exc:
                raise RuntimeError("AKShare northbound source unavailable") from exc
        except RuntimeError as exc:
            self.assertFalse(_is_live_environment_unavailable(exc))

    def test_classifier_keeps_route_name_only_messages_as_non_environment_issue(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(
                RuntimeError("stock_hsgt_individual_em returned malformed payload")
            )
        )

    def test_classifier_marks_upstream_service_unavailable_as_environment_issue(self) -> None:
        self.assertTrue(
            _is_live_environment_unavailable(
                RuntimeError("503 Service Unavailable from Eastmoney upstream")
            )
        )


class AkshareAShareNorthboundFlowLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_a_share_northbound_flow_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareAShareCapitalFlowSnapshotAdapter()
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.NORTHBOUND_FLOW_SNAPSHOT,
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
                    "live AKShare A-share northbound source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 2:
            self.skipTest(
                "live AKShare A-share northbound source returned no usable historical records"
            )

        symbols = {record["symbol"] for record in result.normalized_records}
        if len(symbols) < 2:
            self.skipTest(
                "live AKShare A-share northbound source did not return usable records for at least two symbols"
            )

        self.assertEqual(
            [record["symbol"] for record in result.normalized_records],
            sorted(record["symbol"] for record in result.normalized_records),
        )
        latest_trade_date_by_symbol: dict[str, date] = {}
        source_routes = {record["source_route"] for record in result.normalized_records}
        self.assertTrue(
            source_routes.issubset(
                {
                    "stock_hsgt_individual_em",
                    "stock_hsgt_individual_detail_em",
                }
            )
        )

        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.NORTHBOUND_FLOW_SNAPSHOT, record),
                (),
            )
            self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
            self.assertIn(
                record["source_route"],
                {"stock_hsgt_individual_em", "stock_hsgt_individual_detail_em"},
            )
            self.assertEqual(record["market"], "CN")
            self.assertRegex(record["symbol"], r"^\d{6}\.(SH|SZ|BJ)$")
            self.assertIsInstance(record["northbound_shares_held"], (int, float))
            self.assertIsInstance(record["northbound_holding_market_value"], (int, float))
            self.assertIsInstance(record["northbound_holding_ratio_a_share_pct"], (int, float))
            if "northbound_share_change" in record:
                self.assertIsInstance(record["northbound_share_change"], (int, float))
            if "northbound_net_buy" in record:
                self.assertIsInstance(record["northbound_net_buy"], (int, float))
            if "northbound_holding_market_value_change" in record:
                self.assertIsInstance(
                    record["northbound_holding_market_value_change"],
                    (int, float),
                )
            self.assertIsNotNone(re.match(r"^\d{4}-\d{2}-\d{2}$", record["trade_date"]))
            trade_date = date.fromisoformat(record["trade_date"])
            self.assertLessEqual(trade_date, date.today())
            previous = latest_trade_date_by_symbol.get(record["symbol"])
            latest_trade_date_by_symbol[record["symbol"]] = (
                trade_date if previous is None else max(previous, trade_date)
            )

        self.assertEqual(set(latest_trade_date_by_symbol), symbols)
        self.assertTrue(all(latest_trade_date_by_symbol.values()))


if __name__ == "__main__":
    unittest.main()
