import os
import unittest
from datetime import date

from quant.datahub.adapters.akshare import MACRO_POLICY_SOURCE_ID
from quant.datahub.adapters.policy import MacroPolicyDocumentsAdapter
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceRequest, fetch_source_result


LIVE_TESTS_ENABLED = os.getenv("QUANT_SYSTEM_LIVE_TESTS") == "1"


def _is_live_environment_unavailable(exc: BaseException) -> bool:
    adapter = MacroPolicyDocumentsAdapter(fetch_policy_documents=lambda **kwargs: [])
    return adapter.is_live_environment_unavailable(exc)


class MacroPolicyDocumentsLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        self.assertTrue(
            _is_live_environment_unavailable(
                OSError(111, "connection refused to sousuo.www.gov.cn search-gov/data")
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        self.assertFalse(
            _is_live_environment_unavailable(ValueError("Invalid publish_date value"))
        )


class MacroPolicyDocumentsLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_macro_policy_documents_smoke(self) -> None:
        adapter = MacroPolicyDocumentsAdapter(max_records_per_route=10)
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.POLICY_DOCUMENTS,
            source_name=MACRO_POLICY_SOURCE_ID,
            start_date=date(2010, 1, 1),
            end_date=date.today(),
            symbols=("zhengcelibrary_gw",),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if _is_live_environment_unavailable(exc):
                self.skipTest(
                    "live policy documents source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 1:
            self.skipTest("live policy documents source returned no usable bounded sample records")

        first_record = result.normalized_records[0]
        issues = registry.validate_record(DatasetName.POLICY_DOCUMENTS, first_record)
        self.assertEqual(issues, ())
        self.assertEqual(first_record["source"], MACRO_POLICY_SOURCE_ID)
        self.assertIn("policy_id", first_record)
        self.assertIn("title", first_record)
        self.assertIn("publish_date", first_record)


if __name__ == "__main__":
    unittest.main()
