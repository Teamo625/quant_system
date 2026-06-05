import os
import re
import unittest

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareHKInstrumentMasterAdapter,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceRequest, fetch_source_result


LIVE_TESTS_ENABLED = os.getenv("QUANT_SYSTEM_LIVE_TESTS") == "1"


class AkshareHKInstrumentMasterLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        adapter = AkshareHKInstrumentMasterAdapter(
            fetch_hk_security_profile=lambda **kwargs: []
        )
        self.assertTrue(
            adapter._is_hk_instrument_master_network_unavailable(  # pylint: disable=protected-access
                OSError(111, "connection refused to emweb.securities.eastmoney.com")
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        adapter = AkshareHKInstrumentMasterAdapter(
            fetch_hk_security_profile=lambda **kwargs: []
        )
        self.assertFalse(
            adapter._is_hk_instrument_master_network_unavailable(  # pylint: disable=protected-access
                ValueError("Invalid list_date value")
            )
        )


class AkshareHKInstrumentMasterLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_hk_instrument_master_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareHKInstrumentMasterAdapter()
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.INSTRUMENT_MASTER,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("00005.HK", "00700.HK"),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if adapter._is_hk_instrument_master_network_unavailable(exc):  # pylint: disable=protected-access
                self.skipTest(
                    "live AKShare HK instrument-master source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 2:
            self.skipTest(
                "live AKShare HK instrument-master source returned insufficient bounded sample records"
            )

        self.assertEqual(
            [record["symbol"] for record in result.normalized_records],
            ["00005.HK", "00700.HK"],
        )
        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.INSTRUMENT_MASTER, record),
                (),
            )
            self.assertEqual(record["source"], AKSHARE_SOURCE_ID)
            self.assertEqual(record["market"], "HK")
            self.assertEqual(record["exchange"], "HKEX")
            self.assertEqual(record["asset_type"], "stock")
            self.assertEqual(record["currency"], "HKD")
            self.assertEqual(record["delist_date"], "9999-12-31")
            self.assertTrue(record["is_active"])
            self.assertRegex(record["symbol"], r"^\d{5}\.HK$")
            self.assertIsNotNone(re.match(r"^\d{4}-\d{2}-\d{2}$", record["list_date"]))


if __name__ == "__main__":
    unittest.main()
