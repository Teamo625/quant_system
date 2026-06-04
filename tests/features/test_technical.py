import math
import unittest
from dataclasses import dataclass
from datetime import date, datetime

from quant.datahub.datasets import DatasetName
from quant.features.contracts import FeatureName, validate_feature_value_record
from quant.features.technical import (
    DailyBarInput,
    build_close_to_close_return_feature,
    build_realized_volatility_feature,
    build_simple_moving_average_feature,
    calculate_close_to_close_return,
    calculate_realized_volatility,
    calculate_simple_moving_average,
    normalize_daily_bars,
)


@dataclass(frozen=True)
class ExternalDailyBar:
    symbol: str
    market: str
    trade_date: date | datetime
    close: float


class PriceTechnicalPrimitivesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.created_at = datetime(2026, 6, 4, 9, 30, 0)
        self.unsorted_rows = [
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 3),
                "close": 11.0,
            },
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": datetime(2026, 6, 1, 15, 0, 0),
                "close": 10.0,
            },
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 2),
                "close": 10.5,
            },
        ]

    def test_normalize_daily_bars_sorts_rows_and_coerces_datetime_dates(self) -> None:
        bars = normalize_daily_bars(self.unsorted_rows)

        self.assertEqual(
            bars,
            (
                DailyBarInput(
                    symbol="600000.SH",
                    market="CN",
                    trade_date=date(2026, 6, 1),
                    close=10.0,
                ),
                DailyBarInput(
                    symbol="600000.SH",
                    market="CN",
                    trade_date=date(2026, 6, 2),
                    close=10.5,
                ),
                DailyBarInput(
                    symbol="600000.SH",
                    market="CN",
                    trade_date=date(2026, 6, 3),
                    close=11.0,
                ),
            ),
        )

    def test_calculate_close_to_close_return_uses_latest_two_closes(self) -> None:
        value = calculate_close_to_close_return(self.unsorted_rows)

        self.assertAlmostEqual(value, (11.0 / 10.5) - 1.0)

    def test_calculate_simple_moving_average_uses_trailing_window(self) -> None:
        value = calculate_simple_moving_average(self.unsorted_rows, window=2)

        self.assertAlmostEqual(value, 10.75)

    def test_calculate_realized_volatility_uses_rms_of_trailing_returns(self) -> None:
        rows = self.unsorted_rows + [
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 4),
                "close": 10.78,
            }
        ]

        value = calculate_realized_volatility(
            rows,
            window=3,
            annualization_factor=1.0,
        )

        returns = ((10.5 / 10.0) - 1.0, (11.0 / 10.5) - 1.0, (10.78 / 11.0) - 1.0)
        expected = math.sqrt(sum(item * item for item in returns) / len(returns))
        self.assertAlmostEqual(value, expected)

    def test_build_feature_records_pass_contract_validation(self) -> None:
        close_return_record = build_close_to_close_return_feature(
            self.unsorted_rows,
            created_at=self.created_at,
        )
        sma_record = build_simple_moving_average_feature(
            self.unsorted_rows,
            window=3,
            created_at=self.created_at,
        )
        volatility_record = build_realized_volatility_feature(
            self.unsorted_rows,
            window=2,
            created_at=self.created_at,
            annualization_factor=1.0,
        )

        for record in (close_return_record, sma_record, volatility_record):
            self.assertEqual(record.feature_name, FeatureName.PRICE_TECHNICAL)
            self.assertEqual(record.source_dataset, DatasetName.DAILY_BARS)
            self.assertEqual(record.trade_date, date(2026, 6, 3))
            self.assertEqual(record.created_at, self.created_at)
            self.assertEqual(validate_feature_value_record(record), ())

        self.assertAlmostEqual(close_return_record.value, (11.0 / 10.5) - 1.0)
        self.assertAlmostEqual(sma_record.value, 10.5)

    def test_dataclass_rows_are_supported(self) -> None:
        rows = [
            ExternalDailyBar("600000.SH", "CN", date(2026, 6, 1), 10.0),
            ExternalDailyBar("600000.SH", "CN", date(2026, 6, 2), 10.5),
        ]

        value = calculate_close_to_close_return(rows)

        self.assertAlmostEqual(value, 0.05)

    def test_insufficient_rows_raise_value_error(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "at least two rows are required for close-to-close return",
        ):
            calculate_close_to_close_return(self.unsorted_rows[:1])

        with self.assertRaisesRegex(
            ValueError,
            "insufficient rows for requested moving-average window",
        ):
            calculate_simple_moving_average(self.unsorted_rows[:2], window=3)

        with self.assertRaisesRegex(
            ValueError,
            "insufficient rows for requested realized-volatility window",
        ):
            calculate_realized_volatility(self.unsorted_rows[:3], window=3)

    def test_invalid_window_raises_value_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "window must be a positive integer"):
            calculate_simple_moving_average(self.unsorted_rows, window=0)

        with self.assertRaisesRegex(ValueError, "window must be a positive integer"):
            calculate_realized_volatility(self.unsorted_rows, window=1.5)  # type: ignore[arg-type]

    def test_invalid_close_values_raise_value_error(self) -> None:
        rows = [
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 1),
                "close": 10.0,
            },
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 2),
                "close": 0.0,
            },
        ]

        with self.assertRaisesRegex(
            ValueError,
            "daily bar close must be a positive finite number",
        ):
            normalize_daily_bars(rows)

    def test_duplicate_trade_dates_raise_value_error(self) -> None:
        rows = [
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": datetime(2026, 6, 1, 9, 30, 0),
                "close": 10.0,
            },
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": datetime(2026, 6, 1, 15, 0, 0),
                "close": 10.2,
            },
        ]

        with self.assertRaisesRegex(
            ValueError,
            "daily bar rows must have unique trade_date values",
        ):
            normalize_daily_bars(rows)

    def test_mixed_symbols_and_invalid_created_at_raise_value_error(self) -> None:
        rows = [
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 1),
                "close": 10.0,
            },
            {
                "symbol": "600001.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 2),
                "close": 10.5,
            },
        ]

        with self.assertRaisesRegex(
            ValueError,
            "all daily bar rows must share the same symbol",
        ):
            normalize_daily_bars(rows)

        with self.assertRaisesRegex(
            ValueError,
            "created_at must be a datetime instance",
        ):
            build_close_to_close_return_feature(self.unsorted_rows, created_at=date(2026, 6, 4))


if __name__ == "__main__":
    unittest.main()
