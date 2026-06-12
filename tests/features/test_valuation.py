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
    calculate_latest_pb,
    calculate_latest_pe_ttm,
    calculate_latest_ps_ttm,
    calculate_relative_valuation_to_history_mean,
    calculate_valuation_percentile,
    normalize_valuation_snapshots,
)


@dataclass(frozen=True)
class ExternalValuationSnapshot:
    symbol: str
    market: str
    trade_date: date | datetime
    pe_ttm: float | None = None
    pb: float | None = None
    ps_ttm: float | None = None
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
                "ps_ttm": 2.0,
                "market_cap": 120.0,
                "float_market_cap": 84.0,
            },
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": datetime(2026, 6, 1, 15, 0, 0),
                "pe_ttm": 12.0,
                "pb": 2.4,
                "ps_ttm": 3.0,
                "market_cap": 100.0,
                "float_market_cap": 70.0,
            },
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 2),
                "pe_ttm": 11.0,
                "pb": 2.2,
                "ps_ttm": 2.5,
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
                    ps_ttm=3.0,
                    market_cap=100.0,
                    float_market_cap=70.0,
                ),
                ValuationSnapshotInput(
                    symbol="600000.SH",
                    market="CN",
                    trade_date=date(2026, 6, 2),
                    pe_ttm=11.0,
                    pb=2.2,
                    ps_ttm=2.5,
                    market_cap=110.0,
                    float_market_cap=77.0,
                ),
                ValuationSnapshotInput(
                    symbol="600000.SH",
                    market="CN",
                    trade_date=date(2026, 6, 3),
                    pe_ttm=10.0,
                    pb=2.0,
                    ps_ttm=2.0,
                    market_cap=120.0,
                    float_market_cap=84.0,
                ),
            ),
        )

    def test_latest_ratio_calculations_use_latest_sorted_snapshot(self) -> None:
        self.assertAlmostEqual(calculate_latest_pe_ttm(self.unsorted_rows), 10.0)
        self.assertAlmostEqual(calculate_latest_pb(self.unsorted_rows), 2.0)
        self.assertAlmostEqual(calculate_latest_ps_ttm(self.unsorted_rows), 2.0)
        self.assertAlmostEqual(calculate_earnings_yield(self.unsorted_rows), 0.1)
        self.assertAlmostEqual(calculate_book_to_price(self.unsorted_rows), 0.5)
        self.assertAlmostEqual(
            calculate_float_market_cap_ratio(self.unsorted_rows),
            84.0 / 120.0,
        )

    def test_history_aware_valuation_metrics_use_bounded_window(self) -> None:
        self.assertAlmostEqual(
            calculate_valuation_percentile(
                self.unsorted_rows,
                metric_name="pe_ttm",
                window=3,
            ),
            1.0 / 3.0,
        )
        self.assertAlmostEqual(
            calculate_relative_valuation_to_history_mean(
                self.unsorted_rows,
                metric_name="ps_ttm",
                window=3,
            ),
            2.0 / 2.5,
        )
        self.assertAlmostEqual(
            calculate_valuation_percentile(
                self.unsorted_rows,
                metric_name="pb",
                window=2,
            ),
            0.5,
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

        self.assertEqual(earnings_yield_record.metric_name, "earnings_yield")
        self.assertEqual(earnings_yield_record.metric_params, {})
        self.assertEqual(book_to_price_record.metric_name, "book_to_price")
        self.assertEqual(book_to_price_record.metric_params, {})
        self.assertEqual(
            float_market_cap_ratio_record.metric_name,
            "float_market_cap_ratio",
        )
        self.assertEqual(float_market_cap_ratio_record.metric_params, {})
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
                ps_ttm=1.8,
                market_cap=100.0,
                float_market_cap=60.0,
            ),
            ExternalValuationSnapshot(
                "600000.SH",
                "CN",
                date(2026, 6, 2),
                pe_ttm=8.0,
                pb=2.0,
                ps_ttm=1.5,
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

    def test_history_aware_metrics_validate_window_and_metric_inputs(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "window must be a positive integer",
        ):
            calculate_valuation_percentile(
                self.unsorted_rows,
                metric_name="pe_ttm",
                window=0,
            )

        with self.assertRaisesRegex(
            ValueError,
            "metric_name must be one of: pe_ttm, pb, ps_ttm",
        ):
            calculate_valuation_percentile(
                self.unsorted_rows,
                metric_name="ev_ebitda",
                window=2,
            )

        with self.assertRaisesRegex(
            ValueError,
            "insufficient rows for requested valuation window",
        ):
            calculate_relative_valuation_to_history_mean(
                self.unsorted_rows[:2],
                metric_name="pb",
                window=3,
            )

        with self.assertRaisesRegex(
            ValueError,
            "ps_ttm is required for valuation percentile calculation",
        ):
            calculate_valuation_percentile(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 1),
                        "ps_ttm": 2.0,
                    },
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 2),
                    },
                ],
                metric_name="ps_ttm",
                window=2,
            )

        with self.assertRaisesRegex(
            ValueError,
            "pb history mean must be non-zero for relative valuation calculation",
        ):
            calculate_relative_valuation_to_history_mean(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 1),
                        "pb": 1.0,
                    },
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 2),
                        "pb": -1.0,
                    },
                ],
                metric_name="pb",
                window=2,
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
                        "pb": float("inf"),
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

        with self.assertRaisesRegex(
            ValueError,
            "market_cap must be a finite number when provided",
        ):
            normalize_valuation_snapshots(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 3),
                        "market_cap": float("nan"),
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
            "all valuation snapshot rows must share the same market",
        ):
            normalize_valuation_snapshots(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 1),
                        "pe_ttm": 10.0,
                    },
                    {
                        "symbol": "600000.SH",
                        "market": "HK",
                        "trade_date": date(2026, 6, 2),
                        "pe_ttm": 11.0,
                    },
                ]
            )

        with self.assertRaisesRegex(
            ValueError,
            "created_at must be a datetime instance",
        ):
            build_earnings_yield_feature(self.unsorted_rows, created_at=date(2026, 6, 4))


if __name__ == "__main__":
    unittest.main()
