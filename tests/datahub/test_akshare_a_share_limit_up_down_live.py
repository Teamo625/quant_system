import os
import re
import socket
import unittest
from datetime import date, timedelta
from typing import Iterable

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareLimitUpDownAdapter,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceRequest, fetch_source_result


LIVE_TESTS_ENABLED = os.getenv("QUANT_SYSTEM_LIVE_TESTS") == "1"
_OPTIONAL_LIMIT_UP_DOWN_UPSTREAM_ROUTE_TOKENS = (
    "gettopicpreviouspool",
    "gettopicqspool",
    "gettopiccxpooll",
    "gettopiczbgcpool",
)
_OPTIONAL_LIMIT_UP_DOWN_UNAVAILABLE_TOKENS = (
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
        "push2ex.eastmoney.com",
        "gettopicztpool",
        "gettopicdtpool",
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
        if _is_optional_limit_up_down_route_unavailable_message(message):
            return True
        if any(token in message for token in network_message_tokens):
            return True
        if isinstance(cause, (socket.timeout, TimeoutError, ConnectionError)):
            return True
        if isinstance(cause, OSError):
            if cause.errno in {101, 104, 110, 111, 113}:
                return True
            if _is_optional_limit_up_down_route_unavailable_message(message):
                return True
            if any(token in message for token in network_message_tokens):
                return True

    return False


def _is_optional_limit_up_down_route_unavailable_message(message: str) -> bool:
    return any(
        route_token in message for route_token in _OPTIONAL_LIMIT_UP_DOWN_UPSTREAM_ROUTE_TOKENS
    ) and any(
        unavailable_token in message
        for unavailable_token in _OPTIONAL_LIMIT_UP_DOWN_UNAVAILABLE_TOKENS
    )


class AkshareAShareLimitUpDownLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        self.assertTrue(
            _is_live_environment_unavailable(
                RuntimeError("AKShare limit-up/down route unavailable: ProxyError: proxy down")
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(ValueError("Invalid latest_price value"))
        )

    def test_classifier_keeps_route_signature_compatibility_errors_as_failures(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(
                RuntimeError(
                    "AKShare A-share limit-up/down route does not accept required argument: "
                    "route=stock_zt_pool_em, field=date"
                )
            )
        )

    def test_classifier_keeps_optional_route_payload_errors_as_failures(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(
                ValueError("gettopicpreviouspool payload missing latest_price")
            )
        )
        self.assertFalse(
            _is_live_environment_unavailable(
                ValueError(
                    "gettopiczbgcpool row missing required source field: latest_price"
                )
            )
        )

    def test_classifier_keeps_optional_route_normalization_errors_as_failures(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(
                ValueError("gettopicpreviouspool invalid latest_price value: 'bad-number'")
            )
        )

    def test_classifier_marks_optional_route_upstream_unavailable_as_environment_issue(self) -> None:
        self.assertTrue(
            _is_live_environment_unavailable(
                RuntimeError("gettopicpreviouspool source unavailable: HTTP 502 bad gateway")
            )
        )


class AkshareAShareLimitUpDownLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_a_share_limit_up_down_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareAShareLimitUpDownAdapter()
        registry = DatasetRegistry()

        successful_result = None
        for days_back in range(1, 21):
            target_date = date.today() - timedelta(days=days_back)
            request = SourceRequest(
                dataset=DatasetName.LIMIT_UP_DOWN_EVENTS,
                source_name=AKSHARE_SOURCE_ID,
                start_date=target_date,
                end_date=target_date,
            )
            try:
                result = fetch_source_result(adapter, request)
            except Exception as exc:
                if _is_live_environment_unavailable(exc) or adapter._is_limit_up_down_route_unavailable(  # pylint: disable=protected-access
                    exc
                ):
                    self.skipTest(
                        "live AKShare A-share limit-up/down source unavailable in current environment: "
                        f"{type(exc).__name__}: {exc}"
                    )
                raise

            if result.record_count > 0:
                successful_result = result
                break

        if successful_result is None:
            self.skipTest(
                "live AKShare A-share limit-up/down source returned no usable bounded sample records"
            )

        first_record = successful_result.normalized_records[0]
        self.assertEqual(
            registry.validate_record(DatasetName.LIMIT_UP_DOWN_EVENTS, first_record),
            (),
        )
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertIn(
            first_record.get("source_route"),
            {
                "stock_zt_pool_em",
                "stock_zt_pool_dtgc_em",
                "stock_zt_pool_previous_em",
                "stock_zt_pool_strong_em",
                "stock_zt_pool_sub_new_em",
                "stock_zt_pool_zbgc_em",
            },
        )
        self.assertEqual(first_record["market"], "A_SHARE")
        self.assertRegex(first_record["symbol"], r"^\d{6}\.(SH|SZ|BJ)$")
        self.assertIn(first_record["limit_type"], {"limit_up", "limit_down"})
        self.assertIsInstance(first_record["hit_limit_up"], bool)
        self.assertIsInstance(first_record["hit_limit_down"], bool)
        self.assertIn(
            first_record["event_category"],
            {
                "limit_up_pool",
                "limit_down_pool",
                "previous_day_limit_up_pool",
                "strong_pool",
                "sub_new_pool",
                "broken_board_pool",
            },
        )
        self.assertIsNotNone(re.match(r"^\d{4}-\d{2}-\d{2}$", first_record["trade_date"]))


if __name__ == "__main__":
    unittest.main()
