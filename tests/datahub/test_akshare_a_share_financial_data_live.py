from datetime import date
import os
import re
import socket
import unittest
from typing import Iterable

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareFinancialDataAdapter,
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
        "bad gateway",
        "service unavailable",
        "gateway timeout",
        "temporarily unavailable",
    )
    source_route_tokens = (
        "money.finance.sina.com.cn",
        "datacenter.eastmoney.com",
        "stock_financial_report_sina",
        "stock_financial_analysis_indicator_em",
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
        if any(token in message for token in source_route_tokens) and any(
            token in message for token in network_message_tokens
        ):
            return True
        if isinstance(cause, (socket.timeout, TimeoutError, ConnectionError)):
            return True
        if isinstance(cause, OSError):
            if cause.errno in {101, 104, 110, 111, 113}:
                return True
            if any(token in message for token in network_message_tokens):
                return True

    return False


class AkshareAShareFinancialDataLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        self.assertTrue(
            _is_live_environment_unavailable(
                RuntimeError(
                    "stock_financial_report_sina route unavailable: ProxyError: proxy down"
                )
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        self.assertFalse(_is_live_environment_unavailable(ValueError("Invalid total_assets value")))

    def test_classifier_keeps_route_named_signature_or_payload_failures_as_non_environment_issue(
        self,
    ) -> None:
        adapter = AkshareAShareFinancialDataAdapter()
        signature_exc = TypeError(
            "stock_financial_report_sina() got an unexpected keyword argument 'stock'"
        )
        payload_exc = ValueError(
            "AKShare A-share financial-data payload must be DataFrame-like or "
            "list[Mapping], got dict, route=stock_financial_report_sina."
        )

        self.assertFalse(_is_live_environment_unavailable(signature_exc))
        self.assertFalse(_is_live_environment_unavailable(payload_exc))
        self.assertFalse(adapter._is_a_share_financial_route_unavailable(signature_exc))  # pylint: disable=protected-access
        self.assertFalse(adapter._is_a_share_financial_route_unavailable(payload_exc))  # pylint: disable=protected-access


class AkshareAShareFinancialDataLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_a_share_financial_statements_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareAShareFinancialDataAdapter()
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.FINANCIAL_STATEMENTS,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("600000.SH", "000001.SZ"),
            start_date=date(2022, 1, 1),
            end_date=date.today(),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc) or adapter._is_a_share_financial_route_unavailable(  # pylint: disable=protected-access
                exc
            ):
                self.skipTest(
                    "live AKShare A-share financial statements source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 2:
            self.skipTest(
                "live AKShare A-share financial statements source returned no usable bounded batch records"
            )

        symbols = {record["symbol"] for record in result.normalized_records}
        if len(symbols) < 2:
            self.skipTest(
                "live AKShare A-share financial statements source did not return usable records for at least two symbols"
            )

        self.assertEqual(
            [record["symbol"] for record in result.normalized_records],
            sorted(record["symbol"] for record in result.normalized_records),
        )

        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.FINANCIAL_STATEMENTS, record),
                (),
            )
            self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
            self.assertEqual(record["source_route"], "stock_financial_report_sina")
            self.assertEqual(record["market"], "A_SHARE")
            self.assertRegex(record["symbol"], r"^\d{6}\.(SH|SZ|BJ)$")
            self.assertIn(
                record["statement_type"],
                {"balance_sheet", "income_statement", "cash_flow_statement"},
            )
            self.assertIn(
                record["period_type"],
                {"annual", "semiannual", "quarterly", "report_period"},
            )
            self.assertIsNotNone(re.match(r"^\d{4}-\d{2}-\d{2}$", record["report_period_end"]))
            report_period_end = date.fromisoformat(record["report_period_end"])
            self.assertGreaterEqual(report_period_end, request.start_date)
            self.assertLessEqual(report_period_end, request.end_date)

    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_a_share_financial_indicators_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareAShareFinancialDataAdapter()
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.FINANCIAL_INDICATORS,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("600000.SH", "000001.SZ"),
            start_date=date(2022, 1, 1),
            end_date=date.today(),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc) or adapter._is_a_share_financial_route_unavailable(  # pylint: disable=protected-access
                exc
            ):
                self.skipTest(
                    "live AKShare A-share financial indicators source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 2:
            self.skipTest(
                "live AKShare A-share financial indicators source returned no usable bounded batch records"
            )

        symbols = {record["symbol"] for record in result.normalized_records}
        if len(symbols) < 2:
            self.skipTest(
                "live AKShare A-share financial indicators source did not return usable records for at least two symbols"
            )

        self.assertEqual(
            [record["symbol"] for record in result.normalized_records],
            sorted(record["symbol"] for record in result.normalized_records),
        )

        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.FINANCIAL_INDICATORS, record),
                (),
            )
            self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
            self.assertEqual(record["market"], "A_SHARE")
            self.assertRegex(record["symbol"], r"^\d{6}\.(SH|SZ|BJ)$")
            self.assertIsNotNone(re.match(r"^\d{4}-\d{2}-\d{2}$", record["report_period_end"]))
            self.assertIsInstance(record["metric_code"], str)
            self.assertIsInstance(record["metric_value"], (int, float))
            report_period_end = date.fromisoformat(record["report_period_end"])
            self.assertGreaterEqual(report_period_end, request.start_date)
            self.assertLessEqual(report_period_end, request.end_date)


if __name__ == "__main__":
    unittest.main()
