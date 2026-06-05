import os
import unittest
from datetime import date

from quant.datahub.adapters.akshare import (
    MACRO_POLICY_SOURCE_ID,
    AkshareChinaMacroAdapter,
    is_akshare_macro_live_environment_unavailable,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceRequest, fetch_source_result


LIVE_TESTS_ENABLED = os.getenv("QUANT_SYSTEM_LIVE_TESTS") == "1"
class AkshareChinaMacroLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        self.assertTrue(
            is_akshare_macro_live_environment_unavailable(
                OSError(111, "connection refused to eastmoney upstream")
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        self.assertFalse(
            is_akshare_macro_live_environment_unavailable(
                ValueError("Invalid numeric value")
            )
        )


class AkshareChinaMacroLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_china_macro_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareChinaMacroAdapter()
        registry = DatasetRegistry()

        master_result = fetch_source_result(
            adapter,
            SourceRequest(
                dataset=DatasetName.MACRO_INDICATOR_MASTER,
                source_name=MACRO_POLICY_SOURCE_ID,
                symbols=("CPI_CN_YOY", "PPI_CN_YOY"),
            ),
        )
        self.assertEqual(master_result.record_count, 2)
        master_first = master_result.normalized_records[0]
        self.assertEqual(
            registry.validate_record(DatasetName.MACRO_INDICATOR_MASTER, master_first),
            (),
        )
        self.assertEqual(master_first["source"], MACRO_POLICY_SOURCE_ID)

        request = SourceRequest(
            dataset=DatasetName.MACRO_OBSERVATIONS,
            source_name=MACRO_POLICY_SOURCE_ID,
            start_date=date(2018, 1, 1),
            end_date=date.today(),
            symbols=("CPI_CN_YOY", "PPI_CN_YOY"),
        )

        try:
            observations_result = fetch_source_result(adapter, request)
        except Exception as exc:
            if is_akshare_macro_live_environment_unavailable(exc):
                self.skipTest(
                    "live AKShare China macro source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if observations_result.record_count < 1:
            self.skipTest(
                "live AKShare China macro source returned no usable bounded sample records"
            )

        observation_first = observations_result.normalized_records[0]
        self.assertEqual(
            registry.validate_record(DatasetName.MACRO_OBSERVATIONS, observation_first),
            (),
        )
        self.assertEqual(observation_first["source"], MACRO_POLICY_SOURCE_ID)
        self.assertIn(observation_first["indicator_id"], {"CPI_CN_YOY", "PPI_CN_YOY"})


if __name__ == "__main__":
    unittest.main()
