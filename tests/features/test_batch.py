import unittest
from datetime import date, datetime, timedelta

from quant.datahub.datasets import DatasetName
from quant.features.batch import (
    FeatureBatchContextInput,
    FeatureBatchJob,
    calculate_feature_batch,
)
from quant.features.contracts import FeatureName, build_feature_metric_identity


class FeatureBatchTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.created_at = datetime(2026, 6, 12, 9, 30, 0)
        self.daily_bars = (
            {"symbol": "600000.SH", "market": "CN", "trade_date": date(2026, 6, 1), "close": 10.0},
            {"symbol": "600000.SH", "market": "CN", "trade_date": date(2026, 6, 2), "close": 10.5},
            {"symbol": "600000.SH", "market": "CN", "trade_date": date(2026, 6, 3), "close": 11.0},
        )
        self.valuation_rows = (
            {
                "symbol": "600001.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 1),
                "pe_ttm": 12.0,
                "pb": 1.6,
                "ps_ttm": 2.2,
                "market_cap": 100.0,
                "float_market_cap": 60.0,
            },
            {
                "symbol": "600001.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 2),
                "pe_ttm": 10.0,
                "pb": 1.5,
                "ps_ttm": 2.0,
                "market_cap": 110.0,
                "float_market_cap": 66.0,
            },
        )
        self.capital_flow_rows = (
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 2),
                "main_net_inflow": 8.0,
                "northbound_net_buy": 1.5,
                "turnover_rate": 1.0,
            },
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": date(2026, 6, 3),
                "main_net_inflow": 12.0,
                "northbound_net_buy": 2.5,
                "turnover_rate": 1.2,
            },
        )
        self.index_rows = (
            {"entity_id": "000300.SH", "market": "CN", "trade_date": date(2026, 6, 1), "close": 200.0},
            {"entity_id": "000300.SH", "market": "CN", "trade_date": date(2026, 6, 2), "close": 206.0},
            {"entity_id": "000300.SH", "market": "CN", "trade_date": date(2026, 6, 3), "close": 214.0},
        )

    def test_calculate_feature_batch_returns_deterministic_cross_family_outputs(self) -> None:
        result = calculate_feature_batch(
            [
                FeatureBatchJob(
                    job_id="valuation-1",
                    symbol="600001.SH",
                    market="CN",
                    feature_name=FeatureName.VALUATION,
                    metric_name="earnings_yield",
                    source_dataset=DatasetName.VALUATION_SNAPSHOT,
                    input_rows=self.valuation_rows,
                ),
                FeatureBatchJob(
                    job_id="relative-1",
                    symbol="600000.SH",
                    market="CN",
                    feature_name=FeatureName.RELATIVE,
                    metric_name="index_relative_performance",
                    source_dataset=DatasetName.DAILY_BARS,
                    input_rows=(
                        {"entity_id": "600000.SH", "market": "CN", "trade_date": date(2026, 6, 1), "close": 10.0},
                        {"entity_id": "600000.SH", "market": "CN", "trade_date": date(2026, 6, 2), "close": 10.5},
                        {"entity_id": "600000.SH", "market": "CN", "trade_date": date(2026, 6, 3), "close": 11.0},
                    ),
                    parameters={"window": 3},
                    context_inputs=(
                        FeatureBatchContextInput(
                            role="index_rows",
                            source_dataset=DatasetName.INDEX_DAILY_BARS,
                            rows=self.index_rows,
                        ),
                    ),
                ),
                FeatureBatchJob(
                    job_id="technical-1",
                    symbol="600000.SH",
                    market="CN",
                    feature_name=FeatureName.PRICE_TECHNICAL,
                    metric_name="simple_moving_average",
                    source_dataset=DatasetName.DAILY_BARS,
                    input_rows=self.daily_bars,
                    parameters={"window": 3},
                ),
                FeatureBatchJob(
                    job_id="flow-1",
                    symbol="600000.SH",
                    market="CN",
                    feature_name=FeatureName.CAPITAL_FLOW,
                    metric_name="latest_main_net_inflow",
                    source_dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
                    input_rows=self.capital_flow_rows,
                ),
            ],
            created_at=self.created_at,
        )

        self.assertEqual(
            [(record.symbol, record.feature_name.value, record.metric_name) for record in result.records],
            [
                ("600000.SH", "capital_flow", "latest_main_net_inflow"),
                ("600000.SH", "price_technical", "simple_moving_average"),
                ("600000.SH", "relative", "index_relative_performance"),
                ("600001.SH", "valuation", "earnings_yield"),
            ],
        )
        self.assertEqual(result.records[0].metric_params, {})
        self.assertEqual(result.records[1].metric_params, {"window": 3})
        self.assertEqual(result.records[2].metric_params, {"window": 3})
        self.assertAlmostEqual(result.records[0].value, 12.0)
        self.assertAlmostEqual(result.records[1].value, 10.5)
        self.assertAlmostEqual(
            result.records[2].value,
            (11.0 / 10.0 - 1.0) - (214.0 / 200.0 - 1.0),
        )
        self.assertAlmostEqual(result.records[3].value, 0.1)
        self.assertEqual(
            result.manifest.metric_identities,
            (
                "capital_flow:latest_main_net_inflow:{}",
                'price_technical:simple_moving_average:{"window":3}',
                'relative:index_relative_performance:{"window":3}',
                "valuation:earnings_yield:{}",
            ),
        )

    def test_batch_rejects_duplicate_output_identity(self) -> None:
        jobs = [
            FeatureBatchJob(
                job_id="technical-1",
                symbol="600000.SH",
                market="CN",
                feature_name=FeatureName.PRICE_TECHNICAL,
                metric_name="simple_moving_average",
                source_dataset=DatasetName.DAILY_BARS,
                input_rows=self.daily_bars,
                parameters={"window": 3},
            ),
            FeatureBatchJob(
                job_id="technical-2",
                symbol="600000.SH",
                market="CN",
                feature_name=FeatureName.PRICE_TECHNICAL,
                metric_name="simple_moving_average",
                source_dataset=DatasetName.DAILY_BARS,
                input_rows=self.daily_bars,
                parameters={"window": 3},
            ),
        ]

        with self.assertRaisesRegex(ValueError, "duplicate output identity produced"):
            calculate_feature_batch(jobs, created_at=self.created_at)

    def test_batch_rejects_missing_required_parameter(self) -> None:
        job = FeatureBatchJob(
            job_id="technical-1",
            symbol="600000.SH",
            market="CN",
            feature_name=FeatureName.PRICE_TECHNICAL,
            metric_name="simple_moving_average",
            source_dataset=DatasetName.DAILY_BARS,
            input_rows=self.daily_bars,
        )

        with self.assertRaisesRegex(ValueError, "missing required calculation parameter: window"):
            calculate_feature_batch([job], created_at=self.created_at)

    def test_batch_rejects_missing_required_context_input(self) -> None:
        job = FeatureBatchJob(
            job_id="relative-1",
            symbol="600000.SH",
            market="CN",
            feature_name=FeatureName.RELATIVE,
            metric_name="index_relative_performance",
            source_dataset=DatasetName.DAILY_BARS,
            input_rows=(
                {"entity_id": "600000.SH", "market": "CN", "trade_date": date(2026, 6, 1), "close": 10.0},
                {"entity_id": "600000.SH", "market": "CN", "trade_date": date(2026, 6, 2), "close": 10.5},
                {"entity_id": "600000.SH", "market": "CN", "trade_date": date(2026, 6, 3), "close": 11.0},
            ),
            parameters={"window": 3},
        )

        with self.assertRaisesRegex(ValueError, "missing required context inputs: index_rows"):
            calculate_feature_batch([job], created_at=self.created_at)

    def test_batch_keeps_missing_optional_source_behavior_explicit(self) -> None:
        job = FeatureBatchJob(
            job_id="flow-1",
            symbol="600000.SH",
            market="CN",
            feature_name=FeatureName.CAPITAL_FLOW,
            metric_name="latest_northbound_net_buy",
            source_dataset=DatasetName.NORTHBOUND_FLOW_SNAPSHOT,
            input_rows=(
                {
                    "symbol": "600000.SH",
                    "market": "CN",
                    "trade_date": date(2026, 6, 2),
                    "main_net_inflow": 8.0,
                    "northbound_net_buy": 1.5,
                },
                {
                    "symbol": "600000.SH",
                    "market": "CN",
                    "trade_date": date(2026, 6, 3),
                    "main_net_inflow": 12.0,
                },
            ),
        )

        with self.assertRaisesRegex(
            ValueError,
            "latest_northbound_net_buy cannot be emitted because required input values are missing",
        ):
            calculate_feature_batch([job], created_at=self.created_at)

    def test_batch_rejects_symbol_mismatch_between_job_and_input_rows(self) -> None:
        job = FeatureBatchJob(
            job_id="valuation-1",
            symbol="600999.SH",
            market="CN",
            feature_name=FeatureName.VALUATION,
            metric_name="earnings_yield",
            source_dataset=DatasetName.VALUATION_SNAPSHOT,
            input_rows=self.valuation_rows,
        )

        with self.assertRaisesRegex(ValueError, "valuation batch job symbol does not match normalized input rows"):
            calculate_feature_batch([job], created_at=self.created_at)

    def test_batch_rejects_unsupported_feature_family(self) -> None:
        job = FeatureBatchJob(
            job_id="macro-1",
            symbol="CN_CPI",
            market="CN",
            feature_name=FeatureName.MACRO,
            metric_name="latest_value",
            source_dataset=DatasetName.MACRO_OBSERVATIONS,
            input_rows=({"symbol": "CN_CPI"},),
        )

        with self.assertRaisesRegex(ValueError, "unsupported batch feature family: macro"):
            calculate_feature_batch([job], created_at=self.created_at)

    def test_defaulted_parameters_produce_explicit_metric_identity(self) -> None:
        result = calculate_feature_batch(
            [
                FeatureBatchJob(
                    job_id="technical-1",
                    symbol="600000.SH",
                    market="CN",
                    feature_name=FeatureName.PRICE_TECHNICAL,
                    metric_name="macd_histogram",
                    source_dataset=DatasetName.DAILY_BARS,
                    input_rows=tuple(
                        {
                            "symbol": "600000.SH",
                            "market": "CN",
                            "trade_date": date(2026, 5, 1) + timedelta(days=day - 1),
                            "close": 10.0 + day,
                        }
                        for day in range(1, 40)
                    ),
                )
            ],
            created_at=self.created_at,
        )

        self.assertEqual(
            result.records[0].metric_params,
            {"long_window": 26, "short_window": 12, "signal_window": 9},
        )
        self.assertEqual(
            build_feature_metric_identity(result.records[0]),
            'price_technical:macd_histogram:{"long_window":26,"short_window":12,"signal_window":9}',
        )


if __name__ == "__main__":
    unittest.main()
