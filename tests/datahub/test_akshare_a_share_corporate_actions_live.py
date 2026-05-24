import os
import re
import unittest
from datetime import date

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareAShareCorporateActionsAdapter,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceRequest, fetch_source_result


LIVE_TESTS_ENABLED = os.getenv("QUANT_SYSTEM_LIVE_TESTS") == "1"


class AkshareAShareCorporateActionsLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        adapter = AkshareAShareCorporateActionsAdapter(
            fetch_dividend_cninfo=lambda **kwargs: [],
            fetch_dividend_detail=lambda **kwargs: [],
        )
        self.assertTrue(
            adapter._is_corporate_actions_network_unavailable(  # pylint: disable=protected-access
                OSError(111, "connection refused to cninfo endpoint")
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        adapter = AkshareAShareCorporateActionsAdapter(
            fetch_dividend_cninfo=lambda **kwargs: [],
            fetch_dividend_detail=lambda **kwargs: [],
        )
        self.assertFalse(
            adapter._is_corporate_actions_network_unavailable(  # pylint: disable=protected-access
                ValueError("Invalid event_date value")
            )
        )


class AkshareAShareCorporateActionsLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_a_share_corporate_actions_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareAShareCorporateActionsAdapter()
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.CORPORATE_ACTIONS,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("600000.SH",),
            start_date=date(2000, 1, 1),
            end_date=date.today(),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if adapter._is_corporate_actions_network_unavailable(exc):  # pylint: disable=protected-access
                self.skipTest(
                    "live AKShare A-share corporate-actions source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 1:
            self.skipTest(
                "live AKShare A-share corporate-actions source returned no usable bounded sample records"
            )

        first_record = result.normalized_records[0]
        self.assertEqual(
            registry.validate_record(DatasetName.CORPORATE_ACTIONS, first_record),
            (),
        )
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(first_record["market"], "CN")
        self.assertEqual(first_record["event_type"], "dividend")
        self.assertRegex(first_record["symbol"], r"^\d{6}\.(SH|SZ|BJ)$")
        self.assertIsInstance(first_record["value"], dict)
        self.assertTrue(str(first_record["raw_payload_ref"]).startswith("AKCA|"))
        self.assertIsNotNone(re.match(r"^\d{4}-\d{2}-\d{2}$", first_record["event_date"]))


if __name__ == "__main__":
    unittest.main()
