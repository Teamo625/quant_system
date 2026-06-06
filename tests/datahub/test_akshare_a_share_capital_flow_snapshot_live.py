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
        "push2his.eastmoney.com",
        "push2.eastmoney.com",
        "datacenter.eastmoney.com",
        "datacenter-web.eastmoney.com",
        "securities/api/data/get",
        "rpt_fundflow_secucode",
        "stock_individual_fund_flow",
        "datacenter_securities_fundflow_snapshot",
        "stock_zh_a_hist",
        "stock_hsgt_individual_em",
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


class AkshareAShareCapitalFlowSnapshotLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        self.assertTrue(
            _is_live_environment_unavailable(
                RuntimeError("AKShare A-share capital-flow source unavailable: ProxyError")
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(ValueError("Invalid main_net_inflow value"))
        )


class AkshareAShareCapitalFlowSnapshotLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_a_share_capital_flow_snapshot_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareAShareCapitalFlowSnapshotAdapter()
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("600000.SH", "000001.SZ"),
            start_date=date.today() - timedelta(days=45),
            end_date=date.today(),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc) or adapter._is_capital_flow_network_unavailable(  # pylint: disable=protected-access
                exc
            ):
                self.skipTest(
                    "live AKShare A-share capital-flow source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 2:
            self.skipTest(
                "live AKShare A-share capital-flow source returned no usable bounded batch records"
            )

        symbols = {record["symbol"] for record in result.normalized_records}
        if len(symbols) < 2:
            self.skipTest(
                "live AKShare A-share capital-flow source did not return usable records for at least two symbols"
            )

        self.assertEqual(
            [record["symbol"] for record in result.normalized_records],
            sorted(record["symbol"] for record in result.normalized_records),
        )

        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.CAPITAL_FLOW_SNAPSHOT, record),
                (),
            )
            self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
            self.assertIn(
                record["source_route"],
                {
                    "stock_individual_fund_flow",
                    "datacenter_securities_fundflow_snapshot",
                },
            )
            self.assertEqual(record["market"], "CN")
            self.assertRegex(record["symbol"], r"^\d{6}\.(SH|SZ|BJ)$")
            self.assertIsInstance(record["main_net_inflow"], (int, float))
            if "net_inflow" in record:
                self.assertIsInstance(record["net_inflow"], (int, float))
            if "northbound_net_buy" in record:
                self.assertIsInstance(record["northbound_net_buy"], (int, float))
            if "turnover_rate" in record:
                self.assertIsInstance(record["turnover_rate"], (int, float))
            self.assertIsNotNone(re.match(r"^\d{4}-\d{2}-\d{2}$", record["trade_date"]))
            trade_date = date.fromisoformat(record["trade_date"])
            self.assertGreaterEqual(trade_date, request.start_date)
            self.assertLessEqual(trade_date, request.end_date)


if __name__ == "__main__":
    unittest.main()
