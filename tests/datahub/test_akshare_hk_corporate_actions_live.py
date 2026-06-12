import os
import re
import unittest
from datetime import date

from quant.datahub.adapters.akshare import (
    AKSHARE_SOURCE_ID,
    AkshareHKCorporateActionsAdapter,
)
from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import SourceRequest, fetch_source_result


LIVE_TESTS_ENABLED = os.getenv("QUANT_SYSTEM_LIVE_TESTS") == "1"


class AkshareHKCorporateActionsLiveClassifierTests(unittest.TestCase):
    def test_classifier_marks_network_related_errors_as_environment_unavailable(self) -> None:
        adapter = AkshareHKCorporateActionsAdapter(
            fetch_hk_dividend_payout=lambda **kwargs: [],
            fetch_hk_fhpx_detail=lambda **kwargs: [],
        )
        self.assertTrue(
            adapter._is_hk_corporate_actions_network_unavailable(  # pylint: disable=protected-access
                OSError(111, "connection refused to emweb.securities.eastmoney.com")
            )
        )

    def test_classifier_keeps_contract_failures_as_non_environment_issue(self) -> None:
        adapter = AkshareHKCorporateActionsAdapter(
            fetch_hk_dividend_payout=lambda **kwargs: [],
            fetch_hk_fhpx_detail=lambda **kwargs: [],
        )
        self.assertFalse(
            adapter._is_hk_corporate_actions_network_unavailable(  # pylint: disable=protected-access
                ValueError("Invalid event_date value")
            )
        )

    def test_classifier_keeps_route_name_contract_failures_as_non_environment_issue(self) -> None:
        adapter = AkshareHKCorporateActionsAdapter(
            fetch_hk_dividend_payout=lambda **kwargs: [],
            fetch_hk_fhpx_detail=lambda **kwargs: [],
        )
        self.assertFalse(
            adapter._is_hk_corporate_actions_network_unavailable(  # pylint: disable=protected-access
                ValueError("stock_hk_dividend_payout_em missing required field")
            )
        )
        self.assertFalse(
            adapter._is_hk_corporate_actions_network_unavailable(  # pylint: disable=protected-access
                ValueError("stock_hk_fhpx_detail_ths bad payload schema")
            )
        )


class AkshareHKCorporateActionsLiveTests(unittest.TestCase):
    @unittest.skipUnless(
        LIVE_TESTS_ENABLED,
        "Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.",
    )
    def test_live_akshare_hk_corporate_actions_smoke(self) -> None:
        try:
            import akshare as _ak  # noqa: F401
        except Exception as exc:
            self.skipTest(f"akshare is not available for live smoke test: {exc}")

        adapter = AkshareHKCorporateActionsAdapter()
        registry = DatasetRegistry()
        request = SourceRequest(
            dataset=DatasetName.CORPORATE_ACTIONS,
            source_name=AKSHARE_SOURCE_ID,
            symbols=("00700.HK", "00005.HK"),
            start_date=date(2000, 1, 1),
            end_date=date.today(),
        )

        try:
            result = fetch_source_result(adapter, request)
        except Exception as exc:
            if adapter._is_hk_corporate_actions_network_unavailable(exc):  # pylint: disable=protected-access
                self.skipTest(
                    "live AKShare HK corporate-actions source unavailable in current environment: "
                    f"{type(exc).__name__}: {exc}"
                )
            raise

        if result.record_count < 1:
            self.skipTest(
                "live AKShare HK corporate-actions source returned no usable bounded sample records"
            )

        observed_symbols = {str(record["symbol"]) for record in result.normalized_records}
        if observed_symbols != {"00005.HK", "00700.HK"}:
            self.fail(
                "live AKShare HK corporate-actions batch did not preserve the requested "
                f"two-symbol coverage: observed={sorted(observed_symbols)!r}"
            )

        for record in result.normalized_records:
            self.assertEqual(
                registry.validate_record(DatasetName.CORPORATE_ACTIONS, record),
                (),
            )

        first_record = result.normalized_records[0]
        self.assertEqual(first_record["source"], AKSHARE_SOURCE_ID)
        self.assertEqual(first_record["market"], "HK")
        self.assertEqual(first_record["event_type"], "dividend")
        self.assertIn(
            first_record["action_family"],
            {"dividend_distribution", "dividend_no_distribution"},
        )
        self.assertEqual(first_record["action_family"], first_record["value"]["action_family"])
        self.assertEqual(first_record["source_route"], first_record["value"]["source_route"])
        self.assertIn(
            first_record["source_route"],
            {
                AkshareHKCorporateActionsAdapter._PRIMARY_ROUTE_NAME,
                AkshareHKCorporateActionsAdapter._FALLBACK_ROUTE_NAME,
            },
        )
        self.assertRegex(first_record["symbol"], r"^\d{5}\.HK$")
        self.assertIsInstance(first_record["value"], dict)
        self.assertTrue(str(first_record["raw_payload_ref"]).startswith("AKCA|"))
        self.assertIsNotNone(re.match(r"^\d{4}-\d{2}-\d{2}$", first_record["event_date"]))
        self.assertIn(
            "dividend_distribution",
            {str(record["action_family"]) for record in result.normalized_records},
        )

        route_names = {
            str(record["source_route"])
            for record in result.normalized_records
        }
        if AkshareHKCorporateActionsAdapter._PRIMARY_ROUTE_NAME not in route_names:
            try:
                import akshare as ak  # type: ignore[import-not-found]

                ak.stock_hk_dividend_payout_em(symbol="00700")
            except Exception as exc:
                if adapter._is_hk_corporate_actions_network_unavailable(exc):  # pylint: disable=protected-access
                    self.skipTest(
                        "live AKShare HK primary corporate-actions route unavailable while "
                        f"attempting combined-route proof: {type(exc).__name__}: {exc}"
                    )
                raise
            self.fail("adapter did not surface primary HK corporate-actions route records")

        if AkshareHKCorporateActionsAdapter._FALLBACK_ROUTE_NAME not in route_names:
            try:
                import akshare as ak  # type: ignore[import-not-found]

                ak.stock_hk_fhpx_detail_ths(symbol="0700")
            except Exception as exc:
                if adapter._is_hk_corporate_actions_network_unavailable(exc):  # pylint: disable=protected-access
                    self.skipTest(
                        "live AKShare HK fallback corporate-actions route unavailable while "
                        f"attempting combined-route proof: {type(exc).__name__}: {exc}"
                    )
                raise
            self.fail("adapter did not surface fallback HK corporate-actions route records")

        self.assertIn(
            "dividend_no_distribution",
            {str(record["action_family"]) for record in result.normalized_records},
        )
        self.assertLessEqual(
            min(str(record["event_date"]) for record in result.normalized_records),
            "2004-08-19",
        )


if __name__ == "__main__":
    unittest.main()
