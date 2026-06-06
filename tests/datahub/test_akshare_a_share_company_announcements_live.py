import os
import re
import socket
import unittest
from datetime import date, timedelta
from typing import Iterable

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareCompanyAnnouncementsAdapter,
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
    )
    source_route_tokens = ("eastmoney", "data.eastmoney.com", "notices/detail")

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


class AkshareAShareCompanyAnnouncementsLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        self.assertTrue(
            _is_live_environment_unavailable(
                RuntimeError("AKShare company announcements route unavailable: ProxyError: proxy down")
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        self.assertFalse(_is_live_environment_unavailable(ValueError("Invalid publish_time value")))

    def test_classifier_keeps_route_signature_compatibility_errors_as_failures(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(
                RuntimeError(
                    "AKShare A-share company announcements route does not accept required argument: "
                    "route=stock_individual_notice_report, field=security/code"
                )
            )
        )

    def test_classifier_keeps_provider_tokens_without_network_context_as_failures(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(
                RuntimeError("Eastmoney payload schema changed for data.eastmoney.com route")
            )
        )


class AkshareAShareCompanyAnnouncementsLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_a_share_company_announcements_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareAShareCompanyAnnouncementsAdapter(max_route_days=180)
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.COMPANY_ANNOUNCEMENTS,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("600000.SH",),
            start_date=date.today() - timedelta(days=179),
            end_date=date.today(),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc) or adapter._is_company_announcements_route_unavailable(  # pylint: disable=protected-access
                exc
            ):
                self.skipTest(
                    "live AKShare A-share company announcements source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 1:
            self.skipTest(
                "live AKShare A-share company announcements source returned no usable bounded sample records"
            )

        publish_dates = [
            date.fromisoformat(record["publish_time"][:10])
            for record in result.normalized_records
        ]
        self.assertGreaterEqual(len(publish_dates), 1)
        self.assertTrue(
            all(request.start_date <= publish_date <= request.end_date for publish_date in publish_dates)
        )

        first_record = result.normalized_records[0]
        self.assertEqual(
            registry.validate_record(DatasetName.COMPANY_ANNOUNCEMENTS, first_record),
            (),
        )
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(first_record["market"], "A_SHARE")
        self.assertIn(
            first_record.get("source_route"),
            {"stock_individual_notice_report", "stock_notice_report"},
        )
        self.assertIsNotNone(re.match(r"^\d{6}\.(SH|SZ|BJ)$", first_record["symbol"]))
        self.assertIsNotNone(re.match(r"^\d{4}-\d{2}-\d{2}T", first_record["publish_time"]))
        self.assertGreaterEqual(
            sum(
                1
                for publish_date in publish_dates
                if request.start_date <= publish_date <= request.end_date
            ),
            1,
        )


if __name__ == "__main__":
    unittest.main()
