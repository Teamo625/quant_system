import unittest
from dataclasses import dataclass
from datetime import date, datetime

from quant.datahub.datasets import DatasetName
from quant.features.contracts import FeatureName, validate_feature_value_record
from quant.features.capital_flow import (
    CapitalFlowSnapshotInput,
    build_latest_main_net_inflow_feature,
    calculate_latest_main_net_inflow,
    calculate_latest_northbound_net_buy,
    calculate_trailing_main_net_inflow_sum,
    calculate_turnover_adjusted_main_net_inflow,
    normalize_capital_flow_snapshots,
)


@dataclass(frozen=True)
class ExternalCapitalFlowSnapshot:
    symbol: str
    market: str
    trade_date: date | datetime
    main_net_inflow: float | None = None
    northbound_net_buy: float | None = None
    turnover_rate: float | None = None


class CapitalFlowPrimitivesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.created_at = datetime(2026, 6, 4, 9, 30, 0)
        self.unsorted_rows = [
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 3),
                "main_net_inflow": 15.0,
                "northbound_net_buy": 4.0,
                "turnover_rate": 2.5,
            },
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": datetime(2026, 6, 1, 15, 0, 0),
                "main_net_inflow": -5.0,
                "northbound_net_buy": 1.0,
                "turnover_rate": 1.2,
            },
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 2),
                "main_net_inflow": 10.0,
                "northbound_net_buy": 2.0,
                "turnover_rate": 2.0,
            },
        ]

    def test_normalize_capital_flow_snapshots_sorts_and_coerces_trade_date(self) -> None:
        snapshots = normalize_capital_flow_snapshots(self.unsorted_rows)

        self.assertEqual(
            snapshots,
            (
                CapitalFlowSnapshotInput(
                    symbol="600000.SH",
                    market="CN",
                    trade_date=date(2026, 6, 1),
                    main_net_inflow=-5.0,
                    northbound_net_buy=1.0,
                    turnover_rate=1.2,
                ),
                CapitalFlowSnapshotInput(
                    symbol="600000.SH",
                    market="CN",
                    trade_date=date(2026, 6, 2),
                    main_net_inflow=10.0,
                    northbound_net_buy=2.0,
                    turnover_rate=2.0,
                ),
                CapitalFlowSnapshotInput(
                    symbol="600000.SH",
                    market="CN",
                    trade_date=date(2026, 6, 3),
                    main_net_inflow=15.0,
                    northbound_net_buy=4.0,
                    turnover_rate=2.5,
                ),
            ),
        )

    def test_calculations_use_latest_sorted_snapshot(self) -> None:
        self.assertAlmostEqual(calculate_latest_main_net_inflow(self.unsorted_rows), 15.0)
        self.assertAlmostEqual(
            calculate_trailing_main_net_inflow_sum(self.unsorted_rows, window=2),
            25.0,
        )
        self.assertAlmostEqual(
            calculate_latest_northbound_net_buy(self.unsorted_rows),
            4.0,
        )
        self.assertAlmostEqual(
            calculate_turnover_adjusted_main_net_inflow(self.unsorted_rows),
            6.0,
        )

    def test_optional_metrics_return_none_when_latest_value_missing(self) -> None:
        rows = [
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 1),
                "main_net_inflow": 5.0,
                "northbound_net_buy": 3.0,
                "turnover_rate": 1.0,
            },
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 2),
                "main_net_inflow": 0.0,
            },
        ]

        self.assertIsNone(calculate_latest_northbound_net_buy(rows))
        self.assertIsNone(calculate_turnover_adjusted_main_net_inflow(rows))
        self.assertEqual(calculate_latest_main_net_inflow(rows), 0.0)

    def test_build_latest_main_net_inflow_feature_passes_contract_validation(
        self,
    ) -> None:
        record = build_latest_main_net_inflow_feature(
            self.unsorted_rows,
            created_at=self.created_at,
        )

        self.assertEqual(record.feature_name, FeatureName.CAPITAL_FLOW)
        self.assertEqual(record.source_dataset, DatasetName.CAPITAL_FLOW_SNAPSHOT)
        self.assertEqual(record.trade_date, date(2026, 6, 3))
        self.assertEqual(record.created_at, self.created_at)
        self.assertEqual(record.value, 15.0)
        self.assertEqual(validate_feature_value_record(record), ())

    def test_dataclass_rows_are_supported(self) -> None:
        rows = [
            ExternalCapitalFlowSnapshot(
                "600000.SH",
                "CN",
                date(2026, 6, 1),
                main_net_inflow=12.0,
                northbound_net_buy=1.0,
                turnover_rate=1.5,
            ),
            ExternalCapitalFlowSnapshot(
                "600000.SH",
                "CN",
                date(2026, 6, 2),
                main_net_inflow=18.0,
                northbound_net_buy=2.0,
                turnover_rate=3.0,
            ),
        ]

        self.assertAlmostEqual(calculate_latest_main_net_inflow(rows), 18.0)

    def test_missing_required_main_net_inflow_raises_value_error(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "main_net_inflow is required for main-net-inflow calculation",
        ):
            calculate_latest_main_net_inflow(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 3),
                    }
                ]
            )

        with self.assertRaisesRegex(
            ValueError,
            "main_net_inflow is required for main-net-inflow calculation",
        ):
            calculate_trailing_main_net_inflow_sum(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 1),
                        "main_net_inflow": 10.0,
                    },
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 2),
                    },
                ],
                window=2,
            )

    def test_invalid_window_and_insufficient_rows_raise_value_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "window must be a positive integer"):
            calculate_trailing_main_net_inflow_sum(self.unsorted_rows, window=0)

        with self.assertRaisesRegex(
            ValueError,
            "window must be a positive integer",
        ):
            calculate_trailing_main_net_inflow_sum(
                self.unsorted_rows,
                window=1.5,  # type: ignore[arg-type]
            )

        with self.assertRaisesRegex(
            ValueError,
            "insufficient rows for requested main-net-inflow window",
        ):
            calculate_trailing_main_net_inflow_sum(self.unsorted_rows[:2], window=3)

    def test_invalid_numeric_inputs_raise_value_error(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "main_net_inflow must be a finite number when provided",
        ):
            normalize_capital_flow_snapshots(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 3),
                        "main_net_inflow": True,
                    }
                ]
            )

        with self.assertRaisesRegex(
            ValueError,
            "northbound_net_buy must be a finite number when provided",
        ):
            normalize_capital_flow_snapshots(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 3),
                        "northbound_net_buy": "4.0",
                    }
                ]
            )

        with self.assertRaisesRegex(
            ValueError,
            "turnover_rate must be a finite number when provided",
        ):
            normalize_capital_flow_snapshots(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 3),
                        "turnover_rate": float("inf"),
                    }
                ]
            )

    def test_non_positive_turnover_rate_raises_when_adjusted_flow_requested(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "turnover_rate must be a positive finite number for adjusted flow",
        ):
            calculate_turnover_adjusted_main_net_inflow(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 3),
                        "main_net_inflow": 10.0,
                        "turnover_rate": 0.0,
                    }
                ]
            )

    def test_duplicate_trade_dates_raise_value_error(self) -> None:
        rows = [
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": datetime(2026, 6, 3, 9, 30, 0),
                "main_net_inflow": 10.0,
            },
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": datetime(2026, 6, 3, 15, 0, 0),
                "main_net_inflow": 11.0,
            },
        ]

        with self.assertRaisesRegex(
            ValueError,
            "capital flow snapshot rows must have unique trade_date values",
        ):
            normalize_capital_flow_snapshots(rows)

    def test_mixed_symbol_market_and_invalid_created_at_raise_value_error(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "all capital flow snapshot rows must share the same symbol",
        ):
            normalize_capital_flow_snapshots(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 1),
                        "main_net_inflow": 10.0,
                    },
                    {
                        "symbol": "600001.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 2),
                        "main_net_inflow": 11.0,
                    },
                ]
            )

        with self.assertRaisesRegex(
            ValueError,
            "all capital flow snapshot rows must share the same market",
        ):
            normalize_capital_flow_snapshots(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 1),
                        "main_net_inflow": 10.0,
                    },
                    {
                        "symbol": "600000.SH",
                        "market": "HK",
                        "trade_date": date(2026, 6, 2),
                        "main_net_inflow": 11.0,
                    },
                ]
            )

        with self.assertRaisesRegex(
            ValueError,
            "created_at must be a datetime instance",
        ):
            build_latest_main_net_inflow_feature(
                self.unsorted_rows,
                created_at=date(2026, 6, 4),
            )


if __name__ == "__main__":
    unittest.main()
