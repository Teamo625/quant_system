import os
import socket
import unittest
from typing import Iterable

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareInstrumentStatusHistoryAdapter,
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
        "sse.com.cn",
        "szse.cn",
        "bjse.cn",
        "sina.com.cn",
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
        if any(token in message for token in network_message_tokens):
            return True
        if isinstance(cause, (socket.timeout, TimeoutError, ConnectionError)):
            return True
        if isinstance(cause, OSError):
            if cause.errno in {101, 104, 110, 111, 113}:
                return True
            if any(token in message for token in network_message_tokens):
                return True

    return False


class AkshareAShareInstrumentStatusHistoryLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        self.assertTrue(
            _is_live_environment_unavailable(
                RuntimeError(
                    "AKShare instrument-status-history route unavailable: ProxyError: proxy down"
                )
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(ValueError("Invalid effective_start_date value"))
        )

    def test_classifier_keeps_route_signature_compatibility_errors_as_failures(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(
                RuntimeError(
                    "AKShare A-share instrument-status-history route does not accept "
                    "required argument: route=stock_info_sz_change_name(简称变更), field=symbol"
                )
            )
        )


class AkshareAShareInstrumentStatusHistoryLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_a_share_instrument_status_history_smoke(self) -> None:
        try:
            import akshare as ak
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        normal_symbol = "000001.SZ"
        special_symbol = None
        special_mode = None

        try:
            sh_delist = ak.stock_info_sh_delist()
            if not sh_delist.empty:
                code = str(sh_delist.iloc[0]["公司代码"]).strip().zfill(6)
                if code.startswith("6"):
                    special_symbol = f"{code}.SH"
                    special_mode = "sh_lifecycle"
        except Exception as exc:
            if _is_live_environment_unavailable(exc):
                sh_delist = None
            else:
                raise

        if special_symbol is None:
            try:
                sz_delist = ak.stock_info_sz_delist()
                if not sz_delist.empty:
                    code = str(sz_delist.iloc[0]["证券代码"]).strip().zfill(6)
                    if code.startswith(("0", "3")):
                        special_symbol = f"{code}.SZ"
                        special_mode = "delisted"
            except Exception as exc:
                if not _is_live_environment_unavailable(exc):
                    raise

        if special_symbol is None:
            try:
                for payload in (
                    ak.stock_info_sh_name_code(symbol="主板A股"),
                    ak.stock_info_sz_name_code(symbol="A股列表"),
                ):
                    code_column = "证券代码" if "证券代码" in payload.columns else "A股代码"
                    name_column = "证券简称" if "证券简称" in payload.columns else "A股简称"
                    for _, row in payload.iterrows():
                        name = str(row[name_column]).replace(" ", "").upper()
                        if not (name.startswith("*ST") or name.startswith("ST")):
                            continue
                        code = str(row[code_column]).strip().zfill(6)
                        market = "SH" if code.startswith("6") else "SZ"
                        special_symbol = f"{code}.{market}"
                        special_mode = "risk_warning"
                        break
                    if special_symbol is not None:
                        break
            except Exception as exc:
                if not _is_live_environment_unavailable(exc):
                    raise

        symbols = [normal_symbol]
        if special_symbol is not None:
            symbols.append(special_symbol)

        adapter = AkshareAShareInstrumentStatusHistoryAdapter()
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.INSTRUMENT_STATUS_HISTORY,
            source_name=AKSHARE_SOURCE_ID,
            symbols=tuple(symbols),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc) or adapter._is_instrument_status_history_route_unavailable(  # pylint: disable=protected-access
                exc
            ):
                self.skipTest(
                    "live AKShare A-share instrument-status-history source unavailable "
                    f"in current environment: {type(exc).__name__}: {exc}"
                )
            raise

        self.assertGreater(result.record_count, 0)

        records = list(result.normalized_records)
        normal_records = [record for record in records if record["symbol"] == normal_symbol]
        self.assertTrue(normal_records)
        self.assertTrue(
            any(
                record["status_type"] == "listing_status" and record["status"] == "listed"
                for record in normal_records
            )
        )
        normal_risk_snapshot = next(
            record
            for record in normal_records
            if record["status_type"] == "risk_warning"
        )
        self.assertEqual(normal_risk_snapshot["status"], "normal")
        self.assertEqual(normal_risk_snapshot["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(
            registry.validate_record(DatasetName.INSTRUMENT_STATUS_HISTORY, normal_risk_snapshot),
            (),
        )

        if special_symbol is not None:
            special_records = [record for record in records if record["symbol"] == special_symbol]
            self.assertTrue(special_records)
            if special_mode == "sh_lifecycle":
                self.assertTrue(
                    any(
                        record["status_type"] == "listing_status"
                        and record["status"] == "listing_suspended"
                        for record in special_records
                    )
                )
                self.assertTrue(
                    any(
                        record["status_type"] == "listing_status"
                        and record["status"] == "delisted"
                        for record in special_records
                    )
                )
            elif special_mode == "delisted":
                self.assertTrue(
                    any(
                        record["status_type"] == "listing_status"
                        and record["status"] == "delisted"
                        for record in special_records
                    )
                )
            elif special_mode == "risk_warning":
                self.assertTrue(
                    any(
                        record["status_type"] == "risk_warning"
                        and record["status"] in {"st", "star_st"}
                        for record in special_records
                    )
                )


if __name__ == "__main__":
    unittest.main()
