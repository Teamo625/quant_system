import unittest
from dataclasses import dataclass
from datetime import date, datetime

from quant.features.relative import (
    EntityReturnInput,
    MemberReturnInput,
    RelativePriceInput,
    calculate_above_threshold_return_ratio,
    calculate_index_relative_performance,
    calculate_positive_return_ratio,
    calculate_relative_sector_momentum,
    calculate_sector_return_rankings,
    calculate_sector_strength,
    calculate_sector_strength_from_returns,
    calculate_stock_vs_sector_return_spread,
    calculate_top_bottom_sector_spread,
    normalize_entity_return_series,
    normalize_member_return_rows,
    normalize_relative_price_series,
)


@dataclass(frozen=True)
class ExternalRelativePriceRow:
    entity_id: str
    market: str
    trade_date: date | datetime
    close: float


class RelativeFeaturePrimitivesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.stock_rows = [
            {
                "entity_id": "600000.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 4),
                "close": 13.0,
            },
            {
                "entity_id": "600000.SH",
                "market": "CN",
                "trade_date": datetime(2026, 6, 1, 15, 0, 0),
                "close": 10.0,
            },
            {
                "entity_id": "600000.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 2),
                "close": 12.0,
            },
        ]
        self.sector_rows = [
            {
                "entity_id": "BK0420",
                "market": "CN",
                "trade_date": date(2026, 6, 4),
                "close": 103.0,
            },
            {
                "entity_id": "BK0420",
                "market": "CN",
                "trade_date": date(2026, 6, 2),
                "close": 98.0,
            },
            {
                "entity_id": "BK0420",
                "market": "CN",
                "trade_date": date(2026, 6, 1),
                "close": 100.0,
            },
        ]

    def test_normalize_relative_price_series_sorts_rows_and_coerces_dates(self) -> None:
        series = normalize_relative_price_series(self.stock_rows)

        self.assertEqual(
            series,
            (
                RelativePriceInput(
                    entity_id="600000.SH",
                    market="CN",
                    trade_date=date(2026, 6, 1),
                    close=10.0,
                ),
                RelativePriceInput(
                    entity_id="600000.SH",
                    market="CN",
                    trade_date=date(2026, 6, 2),
                    close=12.0,
                ),
                RelativePriceInput(
                    entity_id="600000.SH",
                    market="CN",
                    trade_date=date(2026, 6, 4),
                    close=13.0,
                ),
            ),
        )

    def test_relative_return_spread_and_index_relative_performance_align_common_dates(
        self,
    ) -> None:
        stock_vs_sector = calculate_stock_vs_sector_return_spread(
            self.stock_rows,
            self.sector_rows,
            window=3,
        )
        index_relative = calculate_index_relative_performance(
            self.stock_rows,
            [
                {
                    "entity_id": "000300.SH",
                    "market": "CN",
                    "trade_date": date(2026, 6, 1),
                    "close": 200.0,
                },
                {
                    "entity_id": "000300.SH",
                    "market": "CN",
                    "trade_date": date(2026, 6, 2),
                    "close": 210.0,
                },
                {
                    "entity_id": "000300.SH",
                    "market": "CN",
                    "trade_date": date(2026, 6, 4),
                    "close": 214.0,
                },
            ],
            window=3,
        )

        self.assertAlmostEqual(stock_vs_sector, (13.0 / 10.0 - 1.0) - (103.0 / 100.0 - 1.0))
        self.assertAlmostEqual(index_relative, (13.0 / 10.0 - 1.0) - (214.0 / 200.0 - 1.0))

    def test_sector_strength_supports_price_rows_and_return_rows(self) -> None:
        price_strength = calculate_sector_strength(self.sector_rows, window=3)
        return_strength = calculate_sector_strength_from_returns(
            [
                {
                    "entity_id": "BK0420",
                    "market": "CN",
                    "trade_date": date(2026, 6, 1),
                    "return_value": 0.01,
                },
                {
                    "entity_id": "BK0420",
                    "market": "CN",
                    "trade_date": date(2026, 6, 2),
                    "return_value": 0.02,
                },
                {
                    "entity_id": "BK0420",
                    "market": "CN",
                    "trade_date": date(2026, 6, 3),
                    "return_value": -0.01,
                },
            ],
            window=3,
        )

        self.assertAlmostEqual(price_strength, 103.0 / 100.0 - 1.0)
        self.assertAlmostEqual(return_strength, (1.01 * 1.02 * 0.99) - 1.0)

    def test_breadth_primitives_use_one_date_constituent_returns(self) -> None:
        rows = [
            {
                "universe_id": "CSI300",
                "market": "CN",
                "trade_date": date(2026, 6, 4),
                "member_id": "600000.SH",
                "return_value": 0.02,
            },
            {
                "universe_id": "CSI300",
                "market": "CN",
                "trade_date": date(2026, 6, 4),
                "member_id": "600001.SH",
                "return_value": -0.01,
            },
            {
                "universe_id": "CSI300",
                "market": "CN",
                "trade_date": date(2026, 6, 4),
                "member_id": "600002.SH",
                "return_value": 0.03,
            },
        ]

        self.assertAlmostEqual(calculate_positive_return_ratio(rows), 2.0 / 3.0)
        self.assertAlmostEqual(
            calculate_above_threshold_return_ratio(rows, threshold=0.015),
            2.0 / 3.0,
        )

    def test_sector_rotation_primitives_are_deterministic(self) -> None:
        rows = [
            {"entity_id": "BK1001", "market": "CN", "trade_date": date(2026, 6, 1), "close": 100.0},
            {"entity_id": "BK1001", "market": "CN", "trade_date": date(2026, 6, 2), "close": 110.0},
            {"entity_id": "BK1001", "market": "CN", "trade_date": date(2026, 6, 3), "close": 120.0},
            {"entity_id": "BK1002", "market": "CN", "trade_date": date(2026, 6, 1), "close": 100.0},
            {"entity_id": "BK1002", "market": "CN", "trade_date": date(2026, 6, 2), "close": 110.0},
            {"entity_id": "BK1002", "market": "CN", "trade_date": date(2026, 6, 3), "close": 120.0},
            {"entity_id": "BK1003", "market": "CN", "trade_date": date(2026, 6, 1), "close": 100.0},
            {"entity_id": "BK1003", "market": "CN", "trade_date": date(2026, 6, 2), "close": 100.0},
            {"entity_id": "BK1003", "market": "CN", "trade_date": date(2026, 6, 3), "close": 105.0},
        ]

        rankings = calculate_sector_return_rankings(rows, window=3)

        self.assertEqual(tuple(ranking.sector_id for ranking in rankings), ("BK1001", "BK1002", "BK1003"))
        self.assertEqual(tuple(ranking.rank for ranking in rankings), (1, 2, 3))
        self.assertTrue(all(ranking.market == "CN" for ranking in rankings))
        self.assertTrue(all(ranking.trade_date == date(2026, 6, 3) for ranking in rankings))
        self.assertAlmostEqual(rankings[0].trailing_return, 0.2)
        self.assertAlmostEqual(rankings[1].trailing_return, 0.2)
        self.assertAlmostEqual(rankings[2].trailing_return, 0.05)
        self.assertAlmostEqual(
            calculate_relative_sector_momentum(
                rows,
                target_sector_id="BK1003",
                window=3,
            ),
            0.05 - ((0.2 + 0.2 + 0.05) / 3.0),
        )
        self.assertAlmostEqual(calculate_top_bottom_sector_spread(rows, window=3), 0.15)

    def test_dataclass_inputs_are_supported(self) -> None:
        rows = [
            ExternalRelativePriceRow("BK0420", "CN", date(2026, 6, 1), 100.0),
            ExternalRelativePriceRow("BK0420", "CN", date(2026, 6, 2), 101.0),
        ]

        series = normalize_relative_price_series(rows)

        self.assertEqual(series[-1].trade_date, date(2026, 6, 2))
        self.assertAlmostEqual(series[-1].close, 101.0)

    def test_normalize_entity_return_series_and_member_rows(self) -> None:
        entity_series = normalize_entity_return_series(
            [
                {
                    "entity_id": "BK0420",
                    "market": "CN",
                    "trade_date": datetime(2026, 6, 2, 15, 0, 0),
                    "return_value": 0.01,
                },
                {
                    "entity_id": "BK0420",
                    "market": "CN",
                    "trade_date": date(2026, 6, 1),
                    "return_value": -0.02,
                },
            ]
        )
        member_rows = normalize_member_return_rows(
            [
                {
                    "universe_id": "CSI300",
                    "market": "CN",
                    "trade_date": date(2026, 6, 4),
                    "member_id": "600001.SH",
                    "return_value": 0.02,
                },
                {
                    "universe_id": "CSI300",
                    "market": "CN",
                    "trade_date": date(2026, 6, 4),
                    "member_id": "600000.SH",
                    "return_value": -0.01,
                },
            ]
        )

        self.assertEqual(entity_series[0], EntityReturnInput("BK0420", "CN", date(2026, 6, 1), -0.02))
        self.assertEqual(member_rows[0], MemberReturnInput("CSI300", "CN", date(2026, 6, 4), "600000.SH", -0.01))

    def test_alignment_and_window_validation_errors_are_explicit(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "insufficient aligned rows for requested stock-vs-sector window",
        ):
            calculate_stock_vs_sector_return_spread(
                self.stock_rows,
                self.sector_rows[:2],
                window=3,
            )

        with self.assertRaisesRegex(
            ValueError,
            "no common trade dates are available for aligned relative calculation",
        ):
            calculate_index_relative_performance(
                self.stock_rows,
                [
                    {
                        "entity_id": "000300.SH",
                        "market": "CN",
                        "trade_date": date(2026, 5, 20),
                        "close": 200.0,
                    },
                    {
                        "entity_id": "000300.SH",
                        "market": "CN",
                        "trade_date": date(2026, 5, 21),
                        "close": 201.0,
                    },
                ],
                window=2,
            )

        with self.assertRaisesRegex(
            ValueError,
            "relative comparison rows must share the same market",
        ):
            calculate_stock_vs_sector_return_spread(
                self.stock_rows,
                [
                    {
                        "entity_id": "BK0420",
                        "market": "HK",
                        "trade_date": date(2026, 6, 1),
                        "close": 100.0,
                    },
                    {
                        "entity_id": "BK0420",
                        "market": "HK",
                        "trade_date": date(2026, 6, 2),
                        "close": 101.0,
                    },
                    {
                        "entity_id": "BK0420",
                        "market": "HK",
                        "trade_date": date(2026, 6, 4),
                        "close": 102.0,
                    },
                ],
                window=3,
            )

        with self.assertRaisesRegex(
            ValueError,
            "window must be an integer greater than or equal to 2",
        ):
            calculate_sector_strength(self.sector_rows, window=1)

    def test_invalid_identifier_and_duplicate_errors_are_explicit(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "all relative price rows must share the same entity_id",
        ):
            normalize_relative_price_series(
                [
                    {
                        "entity_id": "BK0420",
                        "market": "CN",
                        "trade_date": date(2026, 6, 1),
                        "close": 100.0,
                    },
                    {
                        "entity_id": "BK0421",
                        "market": "CN",
                        "trade_date": date(2026, 6, 2),
                        "close": 101.0,
                    },
                ]
            )

        with self.assertRaisesRegex(
            ValueError,
            "member return rows must have unique member_id values",
        ):
            normalize_member_return_rows(
                [
                    {
                        "universe_id": "CSI300",
                        "market": "CN",
                        "trade_date": date(2026, 6, 4),
                        "member_id": "600000.SH",
                        "return_value": 0.01,
                    },
                    {
                        "universe_id": "CSI300",
                        "market": "CN",
                        "trade_date": date(2026, 6, 4),
                        "member_id": "600000.SH",
                        "return_value": 0.02,
                    },
                ]
            )

        with self.assertRaisesRegex(
            ValueError,
            "all sector rotation rows must share the same market",
        ):
            calculate_sector_return_rankings(
                [
                    {
                        "entity_id": "BK1001",
                        "market": "CN",
                        "trade_date": date(2026, 6, 1),
                        "close": 100.0,
                    },
                    {
                        "entity_id": "BK1001",
                        "market": "CN",
                        "trade_date": date(2026, 6, 2),
                        "close": 101.0,
                    },
                    {
                        "entity_id": "BK1002",
                        "market": "HK",
                        "trade_date": date(2026, 6, 1),
                        "close": 100.0,
                    },
                    {
                        "entity_id": "BK1002",
                        "market": "HK",
                        "trade_date": date(2026, 6, 2),
                        "close": 102.0,
                    },
                ],
                window=2,
            )


if __name__ == "__main__":
    unittest.main()
