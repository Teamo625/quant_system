import os
import re
import socket
import unittest
from datetime import date
from typing import Iterable

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareHKFinancialDataAdapter,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceRequest, fetch_source_result


LIVE_TESTS_ENABLED = os.getenv("QUANT_SYSTEM_LIVE_TESTS") == "1"
_HK_FINANCIAL_UPSTREAM_HOST_TOKENS = (
    "eastmoney",
    "datacenter.eastmoney.com",
)
_HK_FINANCIAL_ROUTE_TOKENS = (
    "stock_financial_hk_report_em",
    "stock_financial_hk_analysis_indicator_em",
)
_HK_FINANCIAL_UNAVAILABLE_MESSAGE_TOKENS = (
    "route unavailable",
    "source unavailable",
    "function is unavailable",
    "temporarily unavailable",
    "service unavailable",
    "bad gateway",
    "gateway timeout",
    "gateway time-out",
    "too many requests",
    "forbidden",
    "not found",
    "http 404",
    "http 429",
    "http 500",
    "http 502",
    "http 503",
    "http 504",
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
        "SSLCertVerificationError",
        "RemoteDisconnected",
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
        "remote end closed connection",
        "dns",
        "certificate verify failed",
        "ssl",
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
        if any(token in message for token in _HK_FINANCIAL_UNAVAILABLE_MESSAGE_TOKENS) and (
            any(token in message for token in _HK_FINANCIAL_UPSTREAM_HOST_TOKENS)
            or any(token in message for token in _HK_FINANCIAL_ROUTE_TOKENS)
        ):
            return True
        if isinstance(cause, (socket.timeout, TimeoutError, ConnectionError)):
            return True
        if isinstance(cause, OSError):
            if cause.errno in {101, 104, 110, 111, 113}:
                return True
            if any(token in message for token in network_message_tokens):
                return True
            if any(token in message for token in _HK_FINANCIAL_UNAVAILABLE_MESSAGE_TOKENS) and (
                any(token in message for token in _HK_FINANCIAL_UPSTREAM_HOST_TOKENS)
                or any(token in message for token in _HK_FINANCIAL_ROUTE_TOKENS)
            ):
                return True

    return False


class AkshareHKFinancialDataLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        self.assertTrue(
            _is_live_environment_unavailable(
                RuntimeError(
                    "stock_financial_hk_report_em route unavailable: ProxyError: proxy down"
                )
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        self.assertFalse(_is_live_environment_unavailable(ValueError("Invalid total_assets value")))

    def test_classifier_keeps_route_name_signature_failures_as_non_environment_issue(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(
                RuntimeError(
                    "stock_financial_hk_report_em signature mismatch: unexpected keyword argument 'symbol'"
                )
            )
        )

    def test_classifier_keeps_route_name_payload_failures_as_non_environment_issue(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(
                ValueError(
                    "stock_financial_hk_analysis_indicator_em missing expected column REPORT_DATE"
                )
            )
        )

    def test_classifier_keeps_route_name_normalization_failures_as_non_environment_issue(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(
                RuntimeError(
                    "stock_financial_hk_report_em normalization failed: invalid report_period_end value"
                )
            )
        )

    def test_classifier_marks_route_name_http_unavailability_as_environment_unavailable(self) -> None:
        self.assertTrue(
            _is_live_environment_unavailable(
                RuntimeError(
                    "stock_financial_hk_analysis_indicator_em temporarily unavailable: HTTP 503 Service Unavailable"
                )
            )
        )


class AkshareHKFinancialDataLiveTests(unittest.TestCase):
    _LIVE_SYMBOLS = ("00700.HK", "00005.HK")

    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_hk_financial_statements_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareHKFinancialDataAdapter()
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.FINANCIAL_STATEMENTS,
            source_name=AKSHARE_SOURCE_ID,
            symbols=self._LIVE_SYMBOLS,
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc) or adapter._is_hk_financial_route_unavailable(  # pylint: disable=protected-access
                exc
            ):
                self.skipTest(
                    "live AKShare HK financial statements source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 1:
            self.skipTest(
                "live AKShare HK financial statements source returned no usable bounded sample records"
            )

        seen_symbols = {record["symbol"] for record in result.normalized_records}
        self.assertEqual(seen_symbols, set(self._LIVE_SYMBOLS))

        first_record = result.normalized_records[0]
        self.assertEqual(
            registry.validate_record(DatasetName.FINANCIAL_STATEMENTS, first_record),
            (),
        )
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(first_record["market"], "HK")
        self.assertEqual(first_record["source_route"], "stock_financial_hk_report_em")
        self.assertRegex(first_record["symbol"], r"^\d{5}\.HK$")
        self.assertIn(first_record["statement_type"], {"balance_sheet", "income_statement", "cash_flow_statement"})
        self.assertIn(first_record["period_type"], {"annual", "semiannual", "quarterly", "report_period"})
        self.assertIsNotNone(re.match(r"^\d{4}-\d{2}-\d{2}$", first_record["report_period_end"]))

        periods_by_symbol = {
            symbol: {
                record["report_period_end"]
                for record in result.normalized_records
                if record["symbol"] == symbol
            }
            for symbol in self._LIVE_SYMBOLS
        }
        self.assertTrue(all(len(periods) >= 2 for periods in periods_by_symbol.values()))

        latest_income_by_symbol = {}
        for record in result.normalized_records:
            if record["statement_type"] != "income_statement":
                continue
            symbol = record["symbol"]
            current = latest_income_by_symbol.get(symbol)
            if current is None or record["report_period_end"] > current["report_period_end"]:
                latest_income_by_symbol[symbol] = record
        self.assertEqual(set(latest_income_by_symbol), set(self._LIVE_SYMBOLS))
        for record in latest_income_by_symbol.values():
            self.assertIn("revenue", record)
            self.assertIn("net_profit", record)

        bounded_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FINANCIAL_STATEMENTS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=self._LIVE_SYMBOLS,
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
            ),
        )
        self.assertTrue(bounded_result.normalized_records)
        self.assertTrue(
            all(
                "2025-01-01" <= record["report_period_end"] <= "2025-12-31"
                for record in bounded_result.normalized_records
            )
        )

    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_hk_financial_indicators_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareHKFinancialDataAdapter()
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.FINANCIAL_INDICATORS,
            source_name=AKSHARE_SOURCE_ID,
            symbols=self._LIVE_SYMBOLS,
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc) or adapter._is_hk_financial_route_unavailable(  # pylint: disable=protected-access
                exc
            ):
                self.skipTest(
                    "live AKShare HK financial indicators source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 1:
            self.skipTest(
                "live AKShare HK financial indicators source returned no usable bounded sample records"
            )

        seen_symbols = {record["symbol"] for record in result.normalized_records}
        self.assertEqual(seen_symbols, set(self._LIVE_SYMBOLS))

        first_record = result.normalized_records[0]
        self.assertEqual(
            registry.validate_record(DatasetName.FINANCIAL_INDICATORS, first_record),
            (),
        )
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(first_record["market"], "HK")
        self.assertEqual(first_record["source_route"], "stock_financial_hk_analysis_indicator_em")
        self.assertRegex(first_record["symbol"], r"^\d{5}\.HK$")
        self.assertIsNotNone(re.match(r"^\d{4}-\d{2}-\d{2}$", first_record["report_period_end"]))
        self.assertIsInstance(first_record["metric_code"], str)
        self.assertIsInstance(first_record["metric_value"], (int, float))
        self.assertIn(first_record["metric_family"], {"per_share", "income_scale", "growth", "profitability", "cash_flow", "leverage_liquidity"})

        periods_by_symbol = {
            symbol: {
                record["report_period_end"]
                for record in result.normalized_records
                if record["symbol"] == symbol
            }
            for symbol in self._LIVE_SYMBOLS
        }
        self.assertTrue(all(len(periods) >= 2 for periods in periods_by_symbol.values()))

        metric_families = {record.get("metric_family") for record in result.normalized_records}
        self.assertIn("per_share", metric_families)
        self.assertIn("income_scale", metric_families)
        self.assertIn("leverage_liquidity", metric_families)

        bounded_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.FINANCIAL_INDICATORS,
                source_name=AKSHARE_SOURCE_ID,
                symbols=self._LIVE_SYMBOLS,
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
            ),
        )
        self.assertTrue(bounded_result.normalized_records)
        self.assertEqual(
            {record["symbol"] for record in bounded_result.normalized_records},
            set(self._LIVE_SYMBOLS),
        )
        self.assertTrue(
            all(
                "2025-01-01" <= record["report_period_end"] <= "2025-12-31"
                for record in bounded_result.normalized_records
            )
        )


if __name__ == "__main__":
    unittest.main()
