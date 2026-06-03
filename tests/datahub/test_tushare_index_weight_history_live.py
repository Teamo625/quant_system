from datetime import date, timedelta
import os
import unittest

from quant.datahub.adapters.tushare import (
    TUSHARE_SOURCE_ID,
    TushareIndexWeightHistoryAdapter,
    is_tushare_live_environment_unavailable,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceRequest, fetch_source_result


LIVE_TESTS_ENABLED = os.getenv("QUANT_SYSTEM_LIVE_TESTS") == "1"


class TushareIndexWeightHistoryLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        self.assertTrue(
            is_tushare_live_environment_unavailable(
                RuntimeError("ProxyError: unable to reach api.waditu.com")
            )
        )

    def test_classifier_keeps_route_signature_errors_as_non_environment_issue(self) -> None:
        self.assertFalse(
            is_tushare_live_environment_unavailable(
                RuntimeError("Tushare index_weight route signature incompatibility")
            )
        )


class TushareIndexWeightHistoryLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_tushare_index_weight_history_smoke(self) -> None:
        token = os.getenv("TUSHARE_TOKEN")
        if token is None or token.strip() == "":
            self.skipTest(
                "TUSHARE_TOKEN is not set. Operator action required: export TUSHARE_TOKEN and "
                "rerun the live smoke test."
            )

        try:
            import tushare as _ts  # noqa: F401
        except Exception as exc:
            self.skipTest(
                "tushare is not available for live smoke test. Operator action required: "
                f"install tushare locally. Details: {exc}"
            )

        today = date.today()
        current_month_start = today.replace(day=1)
        end_date = current_month_start - timedelta(days=1)
        start_date = end_date.replace(day=1)

        adapter = TushareIndexWeightHistoryAdapter()
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.INDEX_WEIGHT_HISTORY,
            source_name=TUSHARE_SOURCE_ID,
            start_date=start_date,
            end_date=end_date,
            symbols=("000300.CN_INDEX",),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if is_tushare_live_environment_unavailable(exc) or adapter._is_tushare_index_weight_route_unavailable(  # pylint: disable=protected-access
                exc
            ):
                self.skipTest(
                    "live Tushare index weight-history source unavailable in current "
                    f"environment: {type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 1:
            self.skipTest(
                "live Tushare index weight-history source returned no usable bounded sample "
                f"records for {start_date.isoformat()}..{end_date.isoformat()}"
            )

        first_record = result.normalized_records[0]
        self.assertEqual(
            registry.validate_record(DatasetName.INDEX_WEIGHT_HISTORY, first_record),
            (),
        )
        self.assertEqual(first_record["source"], TUSHARE_SOURCE_ID)
        self.assertEqual(first_record["market"], "CN_A")
        self.assertEqual(first_record["index_code"], "000300.CN_INDEX")
        self.assertRegex(first_record["symbol"], r"^\d{6}\.(SH|SZ|BJ)$")
        self.assertRegex(first_record["effective_date"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertGreaterEqual(first_record["weight"], 0.0)
        self.assertLessEqual(first_record["weight"], 100.0)
        self.assertEqual(first_record["weight_unit"], "percent")


if __name__ == "__main__":
    unittest.main()
