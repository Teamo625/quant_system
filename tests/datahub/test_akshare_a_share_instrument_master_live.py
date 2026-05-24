import os
import re
import unittest

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareInstrumentMasterAdapter,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceRequest, fetch_source_result


LIVE_TESTS_ENABLED = os.getenv("QUANT_SYSTEM_LIVE_TESTS") == "1"


class AkshareAShareInstrumentMasterLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        adapter = AkshareAShareInstrumentMasterAdapter(
            fetch_sh_main=lambda: [],
            fetch_sh_kcb=lambda: [],
            fetch_sz_a=lambda: [],
            fetch_bj_a=lambda: [],
        )
        self.assertTrue(
            adapter._is_instrument_master_network_unavailable(  # pylint: disable=protected-access
                OSError(111, "connection refused to sse.com.cn endpoint")
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        adapter = AkshareAShareInstrumentMasterAdapter(
            fetch_sh_main=lambda: [],
            fetch_sh_kcb=lambda: [],
            fetch_sz_a=lambda: [],
            fetch_bj_a=lambda: [],
        )
        self.assertFalse(
            adapter._is_instrument_master_network_unavailable(  # pylint: disable=protected-access
                ValueError("Invalid list_date value")
            )
        )


class AkshareAShareInstrumentMasterLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_a_share_instrument_master_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareAShareInstrumentMasterAdapter()
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.INSTRUMENT_MASTER,
            source_name=AKSHARE_SOURCE_ID,
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if adapter._is_instrument_master_network_unavailable(exc):  # pylint: disable=protected-access
                self.skipTest(
                    "live AKShare A-share instrument-master source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 1:
            self.skipTest(
                "live AKShare A-share instrument-master source returned no usable sample records"
            )

        first_record = result.normalized_records[0]
        self.assertEqual(
            registry.validate_record(DatasetName.INSTRUMENT_MASTER, first_record),
            (),
        )
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertRegex(first_record["symbol"], r"^\d{6}\.(SH|SZ|BJ)$")
        self.assertIn(first_record["exchange"], {"SSE", "SZSE", "BSE"})
        self.assertEqual(first_record["delist_date"], "9999-12-31")
        self.assertTrue(first_record["is_active"])
        self.assertIsNotNone(re.match(r"^\d{4}-\d{2}-\d{2}$", first_record["list_date"]))


if __name__ == "__main__":
    unittest.main()
