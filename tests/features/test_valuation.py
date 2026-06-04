import unittest
from dataclasses import dataclass
from datetime import date, datetime

from quant.datahub.datasets import DatasetName
from quant.features.contracts import FeatureName, validate_feature_value_record
from quant.features.valuation import (
    ValuationSnapshotInput,
    build_book_to_price_feature,
    build_earnings_yield_feature,
    build_float_market_cap_ratio_feature,
    calculate_book_to_price,
    calculate_earnings_yield,
    calculate_float_market_cap_ratio,
    normalize_valuation_snapshots,
)


@dataclass(frozen=True)
class ExternalValuationSnapshot:
    symbol: str
    market: str
    trade_date: date | datetime
    pe_ttm: float | None = None
    pb: float | None = None
    market_cap: float | None = None
    float_market_cap: float | None = None


class ValuationPrimitivesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.created_at = datetime(2026, 6, 4, 9, 30, 0)
        self.unsorted_rows = [
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 3),
                "pe_ttm": 10.0,
                "pb": 2.0,
                "market_cap": 120.0,
                "float_market_cap": 84.0,
            },
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": datetime(2026, 6, 1, 15, 0, 0),
                "pe_ttm": 12.0,
                "pb": 2.4,
                "market_cap": 100.0,
                "float_market_cap": 70.0,
            },
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 2),
                "pe_ttm": 11.0,
                "pb": 2.2,
                "market_cap": 110.0,
                "float_market_cap": 77.0,
            },
        ]

    def test_normalize_valuation_snapshots_sorts_rows_and_coerces_datetime_dates(
        self,
    ) -> None:
        snapshots = normalize_valuation_snapshots(self.unsorted_rows)

        self.assertEqual(
            snapshots,
            (
                ValuationSnapshotInput(
                    symbol="600000.SH",
                    market="CN",
                    trade_date=date(2026, 6, 1),
                    pe_ttm=12.0,
                    pb=2.4,
                    market_cap=100.0,
                    float_market_cap=70.0,
                ),
                ValuationSnapshotInput(
                    symbol="600000.SH",
                    market="CN",
                    trade_date=date(2026, 6, 2),
                    pe_ttm=11.0,
                    pb=2.2,
                    market_cap=110.0,
                    float_market_cap=77.0,
                ),
                ValuationSnapshotInput(
                    symbol="600000.SH",
                    market="CN",
                    trade_date=date(2026, 6, 3),
                    pe_ttm=10.0,
                    pb=2.0,
                    market_cap=120.0,
                    float_market_cap=84.0,
                ),
            ),
        )

    def test_calculations_use_latest_sorted_snapshot(self) -> None:
        self.assertAlmostEqual(calculate_earnings_yield(self.unsorted_rows), 0.1)
        self.assertAlmostEqual(calculate_book_to_price(self.unsorted_rows), 0.5)
        self.assertAlmostEqual(
            calculate_float_market_cap_ratio(self.unsorted_rows),
            84.0 / 120.0,
        )

    def test_build_feature_records_pass_contract_validation(self) -> None:
        earnings_yield_record = build_earnings_yield_feature(
            self.unsorted_rows,
            created_at=self.created_at,
        )
        book_to_price_record = build_book_to_price_feature(
            self.unsorted_rows,
            created_at=self.created_at,
        )
        float_market_cap_ratio_record = build_float_market_cap_ratio_feature(
            self.unsorted_rows,
            created_at=self.created_at,
        )

        for record in (
            earnings_yield_record,
            book_to_price_record,
            float_market_cap_ratio_record,
        ):
            self.assertEqual(record.feature_name, FeatureName.VALUATION)
            self.assertEqual(record.source_dataset, DatasetName.VALUATION_SNAPSHOT)
            self.assertEqual(record.trade_date, date(2026, 6, 3))
            self.assertEqual(record.created_at, self.created_at)
            self.assertEqual(validate_feature_value_record(record), ())

        self.assertAlmostEqual(earnings_yield_record.value, 0.1)
        self.assertAlmostEqual(book_to_price_record.value, 0.5)
        self.assertAlmostEqual(float_market_cap_ratio_record.value, 84.0 / 120.0)

    def test_dataclass_rows_are_supported(self) -> None:
        rows = [
            ExternalValuationSnapshot(
                "600000.SH",
                "CN",
                date(2026, 6, 1),
                pe_ttm=10.0,
                pb=2.5,
                market_cap=100.0,
                float_market_cap=60.0,
            ),
            ExternalValuationSnapshot(
                "600000.SH",
                "CN",
                date(2026, 6, 2),
                pe_ttm=8.0,
                pb=2.0,
                market_cap=120.0,
                float_market_cap=72.0,
            ),
        ]

        self.assertAlmostEqual(calculate_earnings_yield(rows), 0.125)

    def test_missing_required_fields_raise_value_error(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "pe_ttm is required for valuation ratio calculation",
        ):
            calculate_earnings_yield(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 3),
                        "pb": 2.0,
                    }
                ]
            )

        with self.assertRaisesRegex(
            ValueError,
            "pb is required for valuation ratio calculation",
        ):
            calculate_book_to_price(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 3),
                        "pe_ttm": 10.0,
                    }
                ]
            )

        with self.assertRaisesRegex(
            ValueError,
            "float_market_cap is required for float-market-cap ratio calculation",
        ):
            calculate_float_market_cap_ratio(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 3),
                        "market_cap": 120.0,
                    }
                ]
            )

    def test_invalid_ratio_inputs_raise_value_error(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "pe_ttm must be a finite number when provided",
        ):
            normalize_valuation_snapshots(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 3),
                        "pe_ttm": True,
                    }
                ]
            )

        with self.assertRaisesRegex(
            ValueError,
            "pb must be a finite number when provided",
        ):
            normalize_valuation_snapshots(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 3),
                        "pb": "2.0",
                    }
                ]
            )

        with self.assertRaisesRegex(
            ValueError,
            "pe_ttm must be a non-zero finite number",
        ):
            calculate_earnings_yield(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 3),
                        "pe_ttm": 0.0,
                    }
                ]
            )

    def test_invalid_market_cap_inputs_raise_value_error(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "market_cap must be a positive finite number",
        ):
            calculate_float_market_cap_ratio(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 3),
                        "market_cap": 0.0,
                        "float_market_cap": 70.0,
                    }
                ]
            )

        with self.assertRaisesRegex(
            ValueError,
            "float_market_cap must be a non-negative finite number",
        ):
            calculate_float_market_cap_ratio(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 3),
                        "market_cap": 100.0,
                        "float_market_cap": -1.0,
                    }
                ]
            )

    def test_duplicate_trade_dates_raise_value_error(self) -> None:
        rows = [
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": datetime(2026, 6, 3, 9, 30, 0),
                "pe_ttm": 10.0,
            },
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": datetime(2026, 6, 3, 15, 0, 0),
                "pe_ttm": 11.0,
            },
        ]

        with self.assertRaisesRegex(
            ValueError,
            "valuation snapshot rows must have unique trade_date values",
        ):
            normalize_valuation_snapshots(rows)

    def test_mixed_symbols_and_invalid_created_at_raise_value_error(self) -> None:
        rows = [
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 1),
                "pe_ttm": 10.0,
            },
            {
                "symbol": "600001.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 2),
                "pe_ttm": 11.0,
            },
        ]

        with self.assertRaisesRegex(
            ValueError,
            "all valuation snapshot rows must share the same symbol",
        ):
            normalize_valuation_snapshots(rows)

        with self.assertRaisesRegex(
            ValueError,
            "created_at must be a datetime instance",
        ):
            build_earnings_yield_feature(self.unsorted_rows, created_at=date(2026, 6, 4))


if __name__ == "__main__":
    unittest.main()
