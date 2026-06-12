import math
import unittest
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from quant.datahub.datasets import DatasetName
from quant.features.contracts import FeatureName, validate_feature_value_record
from quant.features.technical import (
    BollingerBandsValue,
    DailyBarInput,
    MacdValue,
    StochasticOscillatorValue,
    build_average_true_range_feature,
    build_close_to_close_return_feature,
    build_exponential_moving_average_feature,
    build_realized_volatility_feature,
    build_relative_strength_index_feature,
    build_simple_moving_average_feature,
    calculate_amihud_illiquidity,
    calculate_average_true_range,
    calculate_average_turnover,
    calculate_average_volume,
    calculate_bollinger_bands,
    calculate_breakout_ratio,
    calculate_close_to_close_return,
    calculate_exponential_moving_average,
    calculate_gap_return,
    calculate_macd,
    calculate_realized_volatility,
    calculate_relative_strength_index,
    calculate_simple_moving_average,
    calculate_stochastic_oscillator,
    normalize_daily_bars,
)


@dataclass(frozen=True)
class ExternalDailyBar:
    symbol: str
    market: str
    trade_date: date | datetime
    close: float
    open: float | None = None
    high: float | None = None
    low: float | None = None
    volume: float | None = None
    turnover: float | None = None


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
            calculate_realized_volatility(
                self.unsorted_rows,
                window=1.5,  # type: ignore[arg-type]
            )

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
            build_close_to_close_return_feature(
                self.unsorted_rows,
                created_at=date(2026, 6, 4),
            )


class ExpandedTechnicalIndicatorsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.created_at = datetime(2026, 6, 20, 9, 30, 0)

    def test_normalize_daily_bars_preserves_optional_ohlcv_fields(self) -> None:
        bars = normalize_daily_bars(
            [
                {
                    "symbol": "600000.SH",
                    "market": "CN",
                    "trade_date": date(2026, 6, 2),
                    "open": 10.3,
                    "high": 10.8,
                    "low": 10.1,
                    "close": 10.5,
                    "volume": 1200,
                    "turnover": 12600,
                },
                {
                    "symbol": "600000.SH",
                    "market": "CN",
                    "trade_date": date(2026, 6, 1),
                    "open": 10.0,
                    "high": 10.4,
                    "low": 9.9,
                    "close": 10.2,
                    "volume": 1000,
                    "turnover": 10200,
                },
            ]
        )

        self.assertEqual(bars[0].open, 10.0)
        self.assertEqual(bars[1].high, 10.8)
        self.assertEqual(bars[1].low, 10.1)
        self.assertEqual(bars[1].volume, 1200.0)
        self.assertEqual(bars[1].turnover, 12600.0)

    def test_invalid_optional_price_fields_raise_value_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "daily bar low must not exceed high"):
            normalize_daily_bars(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 1),
                        "close": 10.0,
                        "high": 9.8,
                        "low": 9.9,
                    }
                ]
            )

        with self.assertRaisesRegex(
            ValueError,
            "daily bar volume must be a non-negative finite number",
        ):
            normalize_daily_bars(
                [
                    {
                        "symbol": "600000.SH",
                        "market": "CN",
                        "trade_date": date(2026, 6, 1),
                        "close": 10.0,
                        "volume": -1.0,
                    }
                ]
            )

    def test_calculate_exponential_moving_average_uses_sma_seed(self) -> None:
        rows = self._build_close_only_rows([10.0, 10.0, 10.0, 20.0], start_day=1)

        value = calculate_exponential_moving_average(rows, window=3)

        self.assertAlmostEqual(value, 15.0)

    def test_calculate_exponential_moving_average_rejects_invalid_window_and_history(self) -> None:
        rows = self._build_close_only_rows([10.0, 10.5], start_day=1)

        with self.assertRaisesRegex(ValueError, "window must be a positive integer"):
            calculate_exponential_moving_average(rows, window=0)

        with self.assertRaisesRegex(
            ValueError,
            "insufficient values for requested EMA window",
        ):
            calculate_exponential_moving_average(rows, window=3)

    def test_calculate_macd_returns_latest_line_signal_and_histogram(self) -> None:
        closes = [10.0, 11.0, 12.0, 11.5, 12.5, 13.0, 12.8, 13.4]
        rows = self._build_close_only_rows(closes, start_day=1)

        macd = calculate_macd(rows, short_window=3, long_window=5, signal_window=3)

        expected_macd, expected_signal, expected_histogram = self._manual_macd(
            closes,
            short_window=3,
            long_window=5,
            signal_window=3,
        )
        self.assertEqual(macd, MacdValue(expected_macd, expected_signal, expected_histogram))

    def test_calculate_macd_rejects_invalid_window_ordering(self) -> None:
        rows = self._build_close_only_rows([10.0, 10.2, 10.4, 10.6, 10.8], start_day=1)

        with self.assertRaisesRegex(
            ValueError,
            "short_window must be smaller than long_window for MACD",
        ):
            calculate_macd(rows, short_window=5, long_window=5, signal_window=3)

    def test_calculate_macd_rejects_invalid_window_values(self) -> None:
        rows = self._build_close_only_rows([10.0, 10.2, 10.4, 10.6, 10.8], start_day=1)

        with self.assertRaisesRegex(ValueError, "window must be a positive integer"):
            calculate_macd(rows, short_window=0, long_window=5, signal_window=3)

        with self.assertRaisesRegex(ValueError, "window must be a positive integer"):
            calculate_macd(rows, short_window=3, long_window=0, signal_window=3)

        with self.assertRaisesRegex(ValueError, "window must be a positive integer"):
            calculate_macd(rows, short_window=3, long_window=5, signal_window=0)

    def test_calculate_macd_rejects_insufficient_long_and_signal_history(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "insufficient values for requested EMA window",
        ):
            calculate_macd(
                self._build_close_only_rows([10.0, 10.2, 10.4, 10.6], start_day=1),
                short_window=3,
                long_window=5,
                signal_window=3,
            )

        with self.assertRaisesRegex(
            ValueError,
            "insufficient rows for requested MACD signal window",
        ):
            calculate_macd(
                self._build_close_only_rows(
                    [10.0, 10.2, 10.4, 10.6, 10.8, 11.0],
                    start_day=1,
                ),
                short_window=3,
                long_window=5,
                signal_window=3,
            )

    def test_calculate_relative_strength_index_handles_normal_and_edge_cases(self) -> None:
        mixed_rows = self._build_close_only_rows([10.0, 11.0, 10.0, 12.0], start_day=1)
        self.assertAlmostEqual(
            calculate_relative_strength_index(mixed_rows, window=3),
            75.0,
        )

        flat_rows = self._build_close_only_rows([10.0, 10.0, 10.0, 10.0], start_day=1)
        self.assertEqual(calculate_relative_strength_index(flat_rows, window=3), 50.0)

        rising_rows = self._build_close_only_rows([10.0, 11.0, 12.0, 13.0], start_day=1)
        self.assertEqual(calculate_relative_strength_index(rising_rows, window=3), 100.0)

        falling_rows = self._build_close_only_rows([13.0, 12.0, 11.0, 10.0], start_day=1)
        self.assertEqual(calculate_relative_strength_index(falling_rows, window=3), 0.0)

    def test_calculate_relative_strength_index_rejects_invalid_window_and_history(self) -> None:
        rows = self._build_close_only_rows([10.0, 10.5, 10.8], start_day=1)

        with self.assertRaisesRegex(ValueError, "window must be a positive integer"):
            calculate_relative_strength_index(rows, window=0)

        with self.assertRaisesRegex(
            ValueError,
            "insufficient rows for requested RSI window",
        ):
            calculate_relative_strength_index(rows, window=3)

    def test_calculate_stochastic_oscillator_returns_k_d_j(self) -> None:
        rows = [
            self._make_bar(1, close=10.0, high=11.0, low=9.0),
            self._make_bar(2, close=12.0, high=13.0, low=10.0),
            self._make_bar(3, close=9.0, high=12.0, low=8.0),
            self._make_bar(4, close=14.0, high=15.0, low=11.0),
        ]

        value = calculate_stochastic_oscillator(rows, k_window=3, d_window=2)

        percent_k_1 = ((9.0 - 8.0) / (13.0 - 8.0)) * 100.0
        percent_k_2 = ((14.0 - 8.0) / (15.0 - 8.0)) * 100.0
        percent_d = (percent_k_1 + percent_k_2) / 2.0
        percent_j = (3.0 * percent_k_2) - (2.0 * percent_d)
        self.assertEqual(
            value,
            StochasticOscillatorValue(percent_k_2, percent_d, percent_j),
        )

    def test_calculate_stochastic_oscillator_handles_flat_range(self) -> None:
        rows = [
            self._make_bar(1, close=10.0, high=10.0, low=10.0),
            self._make_bar(2, close=10.0, high=10.0, low=10.0),
            self._make_bar(3, close=10.0, high=10.0, low=10.0),
        ]

        value = calculate_stochastic_oscillator(rows, k_window=2, d_window=2)

        self.assertEqual(value, StochasticOscillatorValue(50.0, 50.0, 50.0))

    def test_calculate_stochastic_oscillator_rejects_invalid_windows_and_history(self) -> None:
        rows = [
            self._make_bar(1, close=10.0, high=11.0, low=9.0),
            self._make_bar(2, close=10.5, high=11.5, low=9.5),
            self._make_bar(3, close=11.0, high=12.0, low=10.0),
        ]

        with self.assertRaisesRegex(ValueError, "window must be a positive integer"):
            calculate_stochastic_oscillator(rows, k_window=0, d_window=2)

        with self.assertRaisesRegex(ValueError, "window must be a positive integer"):
            calculate_stochastic_oscillator(rows, k_window=2, d_window=0)

        with self.assertRaisesRegex(
            ValueError,
            "insufficient rows for requested stochastic windows",
        ):
            calculate_stochastic_oscillator(rows, k_window=3, d_window=2)

    def test_calculate_bollinger_bands_returns_expected_levels(self) -> None:
        rows = self._build_close_only_rows([10.0, 12.0, 14.0], start_day=1)

        value = calculate_bollinger_bands(rows, window=3, num_std_dev=2.0)

        deviation = math.sqrt((4.0 + 0.0 + 4.0) / 3.0)
        upper = 12.0 + (2.0 * deviation)
        lower = 12.0 - (2.0 * deviation)
        self.assertEqual(
            value,
            BollingerBandsValue(
                middle_band=12.0,
                upper_band=upper,
                lower_band=lower,
                bandwidth=(upper - lower) / 12.0,
            ),
        )

    def test_calculate_average_true_range_uses_true_range_mean(self) -> None:
        rows = [
            self._make_bar(1, close=10.5, high=11.0, low=10.0),
            self._make_bar(2, close=11.5, high=12.0, low=10.0),
            self._make_bar(3, close=12.5, high=13.0, low=11.0),
        ]

        value = calculate_average_true_range(rows, window=2)

        self.assertAlmostEqual(value, 2.0)

    def test_volume_turnover_liquidity_features_use_trailing_rows(self) -> None:
        rows = [
            self._make_bar(1, close=10.0, volume=100.0, turnover=1000.0),
            self._make_bar(2, close=10.5, volume=200.0, turnover=2100.0),
            self._make_bar(3, close=10.0, volume=300.0, turnover=3300.0),
            self._make_bar(4, close=11.0, volume=400.0, turnover=4400.0),
        ]

        self.assertAlmostEqual(calculate_average_volume(rows, window=2), 350.0)
        self.assertAlmostEqual(
            calculate_average_turnover(rows, window=3),
            (2100.0 + 3300.0 + 4400.0) / 3.0,
        )

        illiquidity = calculate_amihud_illiquidity(rows, window=3)
        expected = (
            abs((10.5 / 10.0) - 1.0) / 2100.0
            + abs((10.0 / 10.5) - 1.0) / 3300.0
            + abs((11.0 / 10.0) - 1.0) / 4400.0
        ) / 3.0
        self.assertAlmostEqual(illiquidity, expected)

    def test_gap_and_breakout_primitives_return_expected_values(self) -> None:
        rows = [
            self._make_bar(1, close=10.0, open_price=9.8, high=10.2, low=9.7),
            self._make_bar(2, close=10.3, open_price=10.1, high=10.4, low=9.9),
            self._make_bar(3, close=10.6, open_price=10.5, high=10.7, low=10.2),
            self._make_bar(4, close=11.0, open_price=10.9, high=11.1, low=10.8),
        ]

        self.assertAlmostEqual(calculate_gap_return(rows), (10.9 / 10.6) - 1.0)
        self.assertAlmostEqual(calculate_breakout_ratio(rows, window=3), (11.0 / 10.7) - 1.0)

    def test_new_feature_builders_pass_contract_validation(self) -> None:
        ema_rows = self._build_close_only_rows([10.0, 10.0, 10.0, 20.0], start_day=1)
        rsi_rows = self._build_close_only_rows([10.0, 11.0, 10.0, 12.0], start_day=1)
        atr_rows = [
            self._make_bar(1, close=10.5, high=11.0, low=10.0),
            self._make_bar(2, close=11.5, high=12.0, low=10.0),
            self._make_bar(3, close=12.5, high=13.0, low=11.0),
        ]

        records = (
            build_exponential_moving_average_feature(
                ema_rows,
                window=3,
                created_at=self.created_at,
            ),
            build_relative_strength_index_feature(
                rsi_rows,
                window=3,
                created_at=self.created_at,
            ),
            build_average_true_range_feature(
                atr_rows,
                window=2,
                created_at=self.created_at,
            ),
        )

        for record in records:
            self.assertEqual(record.feature_name, FeatureName.PRICE_TECHNICAL)
            self.assertEqual(record.source_dataset, DatasetName.DAILY_BARS)
            self.assertEqual(record.created_at, self.created_at)
            self.assertEqual(validate_feature_value_record(record), ())

        self.assertAlmostEqual(records[0].value, 15.0)
        self.assertAlmostEqual(records[1].value, 75.0)
        self.assertAlmostEqual(records[2].value, 2.0)

    def test_missing_required_indicator_fields_raise_value_error(self) -> None:
        missing_high_rows = [
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
                "close": 10.5,
                "low": 9.9,
            },
        ]
        with self.assertRaisesRegex(
            ValueError,
            "daily bar high is required for this calculation",
        ):
            calculate_average_true_range(missing_high_rows, window=1)

        missing_turnover_rows = [
            self._make_bar(1, close=10.0, turnover=1000.0),
            self._make_bar(2, close=10.5),
        ]
        with self.assertRaisesRegex(
            ValueError,
            "daily bar turnover is required for this calculation",
        ):
            calculate_amihud_illiquidity(missing_turnover_rows, window=1)

        with self.assertRaisesRegex(
            ValueError,
            "daily bar open is required for this calculation",
        ):
            calculate_gap_return(
                [
                    self._make_bar(1, close=10.0),
                    self._make_bar(2, close=10.5),
                ]
            )

    def _build_close_only_rows(
        self,
        closes: list[float],
        *,
        start_day: int,
    ) -> list[dict[str, object]]:
        return [
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": date(2026, 6, start_day + index),
                "close": close,
            }
            for index, close in enumerate(closes)
        ]

    def _make_bar(
        self,
        day_offset: int,
        *,
        close: float,
        open_price: float | None = None,
        high: float | None = None,
        low: float | None = None,
        volume: float | None = None,
        turnover: float | None = None,
    ) -> dict[str, object]:
        base_date = date(2026, 6, 1)
        return {
            "symbol": "600000.SH",
            "market": "CN",
            "trade_date": base_date + timedelta(days=day_offset - 1),
            "close": close,
            "open": open_price,
            "high": high,
            "low": low,
            "volume": volume,
            "turnover": turnover,
        }

    def _manual_macd(
        self,
        closes: list[float],
        *,
        short_window: int,
        long_window: int,
        signal_window: int,
    ) -> tuple[float, float, float]:
        short_series = self._manual_ema_series(closes, short_window)
        long_series = self._manual_ema_series(closes, long_window)
        macd_series = [
            short_series[index - (short_window - 1)] - long_series[index - (long_window - 1)]
            for index in range(long_window - 1, len(closes))
        ]
        signal_series = self._manual_ema_series(macd_series, signal_window)
        macd_line = macd_series[-1]
        signal_line = signal_series[-1]
        return macd_line, signal_line, macd_line - signal_line

    def _manual_ema_series(self, values: list[float], window: int) -> list[float]:
        smoothing_factor = 2.0 / (window + 1.0)
        ema_values = [sum(values[:window]) / window]
        for value in values[window:]:
            ema_values.append((value * smoothing_factor) + (ema_values[-1] * (1.0 - smoothing_factor)))
        return ema_values


if __name__ == "__main__":
    unittest.main()
