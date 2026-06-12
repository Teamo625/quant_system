import importlib
import unittest
from datetime import datetime

from quant.features.contracts import FeatureName
from quant.scanner import (
    FeatureReference,
    InvalidRankingFeatureValueError,
    InvalidScanRankingConfigError,
    FeatureValueSnapshot,
    FilterOperator,
    FilterSpec,
    InvalidFilterSpecError,
    InvalidScanOutputError,
    InvalidScanRunnerInputError,
    MissingEligibilityStateError,
    MissingFeaturePolicy,
    MissingSymbolFeatureValuesError,
    ScanCandidateList,
    ScanConstraintPolicies,
    ScanRankingConfig,
    ScanRunMetadata,
    RankingCriterion,
    RankingDirection,
    StaleFeaturePolicy,
    StaleFeatureValueError,
    SymbolDecisionAction,
    SymbolMarketState,
    UniverseDefinition,
    UniverseExclusionInput,
    UniverseFamily,
    UniverseMembershipInput,
    run_scan,
    run_scan_with_diagnostics,
)
from quant.scanner.contracts import validate_scan_candidate_list


class ScannerRunnerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = ScanRunMetadata(
            run_id="scan-2026-06-04-cn-core",
            scanner_id="foundation_scan",
            trade_date="2026-06-04",
            universe_id="cn-core",
            generated_at=datetime(2026, 6, 4, 9, 30, 0),
        )
        self.universe = UniverseMembershipInput(
            universe_id="cn-core",
            universe_name="CN Core",
            market="CN",
            as_of_date="2026-06-04",
            symbols=("600000.SH", "000001.SZ", "300750.SZ"),
        )
        self.universe_definition = UniverseDefinition(
            universe_id="cn-core",
            universe_name="CN Core",
            market="CN",
            source="manual_fixture",
            family=UniverseFamily.A_SHARE,
        )
        self.filters = (
            FilterSpec(
                filter_id="above_ma20",
                feature_ref=FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0),
                operator=FilterOperator.GT,
                threshold=0.0,
            ),
            FilterSpec(
                filter_id="valuation_floor",
                feature_ref=FeatureReference(FeatureName.VALUATION, lag_days=1),
                operator=FilterOperator.GTE,
                threshold=0.08,
            ),
            FilterSpec(
                filter_id="flow_label",
                feature_ref=FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0),
                operator=FilterOperator.EQ,
                threshold="positive",
            ),
        )
        self.symbol_feature_values = {
            "600000.SH": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.02,
                FeatureReference(FeatureName.VALUATION, lag_days=1): 0.10,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
            },
            "000001.SZ": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.03,
                FeatureReference(FeatureName.VALUATION, lag_days=1): 0.09,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
            },
            "300750.SZ": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.05,
                FeatureReference(FeatureName.VALUATION, lag_days=1): 0.06,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
            },
        }

    def test_runner_helpers_are_exported(self) -> None:
        package = importlib.import_module("quant.scanner")
        module = importlib.import_module("quant.scanner.runner")

        self.assertTrue(hasattr(package, "run_scan"))
        self.assertTrue(hasattr(package, "run_scan_with_diagnostics"))
        self.assertTrue(hasattr(package, "ScanConstraintPolicies"))
        self.assertTrue(hasattr(package, "ScanRankingConfig"))
        self.assertTrue(hasattr(module, "MissingEligibilityStateError"))

    def test_run_scan_builds_valid_candidate_list_with_stable_order(self) -> None:
        candidate_list = run_scan(
            metadata=self.metadata,
            universe=self.universe,
            filters=self.filters,
            symbol_feature_values=self.symbol_feature_values,
        )

        self.assertIsInstance(candidate_list, ScanCandidateList)
        self.assertEqual(validate_scan_candidate_list(candidate_list), ())
        self.assertEqual(
            tuple(candidate.symbol for candidate in candidate_list.candidates),
            ("000001.SZ", "600000.SH"),
        )
        self.assertEqual(
            candidate_list.feature_refs,
            (
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0),
                FeatureReference(FeatureName.VALUATION, lag_days=1),
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0),
            ),
        )
        self.assertEqual(
            candidate_list.candidates[0].matched_filter_ids,
            ("above_ma20", "valuation_floor", "flow_label"),
        )
        self.assertIsNone(candidate_list.candidates[0].score)
        self.assertIsNone(candidate_list.candidates[0].rank)
        self.assertIsNotNone(candidate_list.metadata.artifact_context)
        self.assertEqual(
            candidate_list.metadata.artifact_context.universe_snapshot.universe_id,
            "cn-core",
        )
        self.assertEqual(
            candidate_list.metadata.artifact_context.universe_snapshot.symbols,
            ("600000.SH", "000001.SZ", "300750.SZ"),
        )
        self.assertIsNone(candidate_list.metadata.artifact_context.ranking)
        self.assertEqual(
            candidate_list.metadata.artifact_context.handoff.intended_consumers,
            ("strategy_lab", "signal_engine"),
        )

    def test_run_scan_applies_explicit_ranking_and_stable_tie_breaks(self) -> None:
        ranked_symbol_feature_values = {
            "600000.SH": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.05,
                FeatureReference(FeatureName.VALUATION, lag_days=1): 0.10,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
                FeatureReference(FeatureName.RELATIVE, lag_days=0): 0.04,
            },
            "000001.SZ": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.05,
                FeatureReference(FeatureName.VALUATION, lag_days=1): 0.10,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
                FeatureReference(FeatureName.RELATIVE, lag_days=0): 0.04,
            },
            "300750.SZ": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.06,
                FeatureReference(FeatureName.VALUATION, lag_days=1): 0.11,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
                FeatureReference(FeatureName.RELATIVE, lag_days=0): 0.02,
            },
        }

        candidate_list = run_scan(
            metadata=self.metadata,
            universe=self.universe,
            filters=self.filters,
            symbol_feature_values=ranked_symbol_feature_values,
            ranking=ScanRankingConfig(
                criteria=(
                    RankingCriterion(
                        feature_ref=FeatureReference(FeatureName.RELATIVE, lag_days=0),
                        direction=RankingDirection.DESC,
                        weight=2.0,
                    ),
                    RankingCriterion(
                        feature_ref=FeatureReference(FeatureName.VALUATION, lag_days=1),
                        direction=RankingDirection.ASC,
                        weight=1.0,
                    ),
                )
            ),
        )

        self.assertEqual(
            tuple(candidate.symbol for candidate in candidate_list.candidates),
            ("000001.SZ", "600000.SH", "300750.SZ"),
        )
        self.assertEqual(
            tuple(candidate.rank for candidate in candidate_list.candidates),
            (1, 2, 3),
        )
        self.assertAlmostEqual(candidate_list.candidates[0].score, -0.02)
        self.assertAlmostEqual(candidate_list.candidates[1].score, -0.02)
        self.assertAlmostEqual(candidate_list.candidates[2].score, -0.07)
        self.assertEqual(
            candidate_list.feature_refs,
            (
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0),
                FeatureReference(FeatureName.VALUATION, lag_days=1),
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0),
                FeatureReference(FeatureName.RELATIVE, lag_days=0),
            ),
        )
        self.assertIsNotNone(candidate_list.metadata.artifact_context.ranking)
        self.assertEqual(
            tuple(
                criterion.feature_ref.feature_name
                for criterion in candidate_list.metadata.artifact_context.ranking.criteria
            ),
            (FeatureName.RELATIVE, FeatureName.VALUATION),
        )

    def test_run_scan_supports_ascending_ranking_direction(self) -> None:
        ranked_symbol_feature_values = {
            "600000.SH": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.02,
                FeatureReference(FeatureName.VALUATION, lag_days=1): 0.10,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
            },
            "000001.SZ": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.03,
                FeatureReference(FeatureName.VALUATION, lag_days=1): 0.08,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
            },
            "300750.SZ": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.04,
                FeatureReference(FeatureName.VALUATION, lag_days=1): 0.09,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
            },
        }

        candidate_list = run_scan(
            metadata=self.metadata,
            universe=self.universe,
            filters=self.filters,
            symbol_feature_values=ranked_symbol_feature_values,
            ranking={
                "criteria": (
                    {
                        "feature_ref": {
                            "feature_name": FeatureName.VALUATION,
                            "lag_days": 1,
                        },
                        "direction": "asc",
                        "weight": 1.0,
                    },
                )
            },
        )

        self.assertEqual(
            tuple(candidate.symbol for candidate in candidate_list.candidates),
            ("000001.SZ", "300750.SZ", "600000.SH"),
        )

    def test_run_scan_accepts_dataclass_criteria_inside_mapping_ranking_payload(self) -> None:
        ranked_symbol_feature_values = {
            "600000.SH": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.02,
                FeatureReference(FeatureName.VALUATION, lag_days=1): 0.10,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
                FeatureReference(FeatureName.RELATIVE, lag_days=0): 0.02,
            },
            "000001.SZ": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.03,
                FeatureReference(FeatureName.VALUATION, lag_days=1): 0.09,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
                FeatureReference(FeatureName.RELATIVE, lag_days=0): 0.04,
            },
            "300750.SZ": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.04,
                FeatureReference(FeatureName.VALUATION, lag_days=1): 0.11,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
                FeatureReference(FeatureName.RELATIVE, lag_days=0): 0.01,
            },
        }

        candidate_list = run_scan(
            metadata=self.metadata,
            universe=self.universe,
            filters=self.filters,
            symbol_feature_values=ranked_symbol_feature_values,
            ranking={
                "criteria": (
                    RankingCriterion(
                        feature_ref=FeatureReference(FeatureName.RELATIVE, lag_days=0),
                        direction=RankingDirection.DESC,
                        weight=1.0,
                    ),
                )
            },
        )

        self.assertEqual(
            tuple(candidate.symbol for candidate in candidate_list.candidates),
            ("000001.SZ", "600000.SH", "300750.SZ"),
        )
        self.assertEqual(
            tuple(candidate.rank for candidate in candidate_list.candidates),
            (1, 2, 3),
        )

    def test_run_scan_with_diagnostics_tracks_exclusions_and_ineligible_symbols(self) -> None:
        result = run_scan_with_diagnostics(
            metadata=self.metadata,
            universe=self.universe,
            universe_definition=self.universe_definition,
            exclusions=(
                UniverseExclusionInput(
                    exclusion_list_id="manual_blacklist",
                    market="CN",
                    symbols=("600000.SH",),
                    reason="owner_review",
                ),
            ),
            filters=self.filters,
            symbol_feature_values=self.symbol_feature_values,
            constraint_policies=ScanConstraintPolicies(
                exclude_suspended=True,
                blocked_constraint_flags_by_market={"CN": ("st",)},
            ),
            symbol_market_states={
                "000001.SZ": SymbolMarketState(
                    symbol="000001.SZ",
                    market="CN",
                    trade_date="2026-06-04",
                    constraint_flags=("st",),
                ),
                "300750.SZ": SymbolMarketState(
                    symbol="300750.SZ",
                    market="CN",
                    trade_date="2026-06-04",
                    is_suspended=True,
                ),
            },
        )

        self.assertEqual(result.candidate_list.candidates, ())
        self.assertEqual(
            result.candidate_list.metadata.artifact_context.universe_snapshot.source,
            "manual_fixture",
        )
        self.assertEqual(
            result.candidate_list.metadata.artifact_context.universe_snapshot.family,
            UniverseFamily.A_SHARE,
        )
        self.assertEqual(
            tuple(
                (decision.symbol, decision.action, decision.reason_code, decision.detail)
                for decision in result.symbol_decisions
            ),
            (
                (
                    "600000.SH",
                    SymbolDecisionAction.EXCLUDED,
                    "universe_exclusion",
                    "manual_blacklist:owner_review",
                ),
                (
                    "000001.SZ",
                    SymbolDecisionAction.INELIGIBLE,
                    "market_constraint",
                    "st",
                ),
                (
                    "300750.SZ",
                    SymbolDecisionAction.INELIGIBLE,
                    "suspended",
                    "caller_provided_market_state",
                ),
            ),
        )

    def test_run_scan_rejects_universe_definition_snapshot_mismatch(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            r"invalid universe definition/snapshot pair: snapshot\.market: definition_mismatch",
        ):
            run_scan_with_diagnostics(
                metadata=self.metadata,
                universe=self.universe,
                universe_definition=UniverseDefinition(
                    universe_id="cn-core",
                    universe_name="CN Core",
                    market="HK",
                    source="manual_fixture",
                    family=UniverseFamily.HONG_KONG_STOCK,
                ),
                filters=self.filters,
                symbol_feature_values=self.symbol_feature_values,
            )

    def test_missing_feature_policy_can_exclude_instead_of_fail(self) -> None:
        symbol_feature_values = {
            "600000.SH": self.symbol_feature_values["600000.SH"],
            "000001.SZ": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.03,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
            },
            "300750.SZ": self.symbol_feature_values["300750.SZ"],
        }

        result = run_scan_with_diagnostics(
            metadata=self.metadata,
            universe=self.universe,
            filters=self.filters,
            symbol_feature_values=symbol_feature_values,
            constraint_policies=ScanConstraintPolicies(
                missing_feature_policy=MissingFeaturePolicy.EXCLUDE
            ),
        )

        self.assertEqual(
            tuple(candidate.symbol for candidate in result.candidate_list.candidates),
            ("600000.SH",),
        )
        self.assertEqual(
            tuple(
                (decision.symbol, decision.reason_code, decision.detail)
                for decision in result.symbol_decisions
            ),
            (("000001.SZ", "missing_feature", "valuation[lag_days=1]"),),
        )

    def test_missing_ranking_feature_can_exclude_without_promoting_symbol(self) -> None:
        symbol_feature_values = {
            "600000.SH": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.02,
                FeatureReference(FeatureName.VALUATION, lag_days=1): 0.10,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
            },
            "000001.SZ": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.03,
                FeatureReference(FeatureName.VALUATION, lag_days=1): 0.09,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
                FeatureReference(FeatureName.RELATIVE, lag_days=0): 0.02,
            },
            "300750.SZ": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.05,
                FeatureReference(FeatureName.VALUATION, lag_days=1): 0.12,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
                FeatureReference(FeatureName.RELATIVE, lag_days=0): 0.01,
            },
        }

        result = run_scan_with_diagnostics(
            metadata=self.metadata,
            universe=self.universe,
            filters=self.filters,
            symbol_feature_values=symbol_feature_values,
            constraint_policies=ScanConstraintPolicies(
                missing_feature_policy=MissingFeaturePolicy.EXCLUDE
            ),
            ranking=ScanRankingConfig(
                criteria=(
                    RankingCriterion(
                        feature_ref=FeatureReference(FeatureName.RELATIVE, lag_days=0),
                        direction=RankingDirection.DESC,
                    ),
                )
            ),
        )

        self.assertEqual(
            tuple(candidate.symbol for candidate in result.candidate_list.candidates),
            ("000001.SZ", "300750.SZ"),
        )
        self.assertEqual(
            tuple(
                (decision.symbol, decision.reason_code, decision.detail)
                for decision in result.symbol_decisions
            ),
            (("600000.SH", "missing_feature", "relative[lag_days=0]"),),
        )

    def test_stale_feature_policy_can_fail_or_exclude_deterministically(self) -> None:
        symbol_feature_values = {
            "600000.SH": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): FeatureValueSnapshot(
                    value=0.02,
                    as_of_date="2026-06-04",
                ),
                FeatureReference(FeatureName.VALUATION, lag_days=1): FeatureValueSnapshot(
                    value=0.10,
                    as_of_date="2026-06-03",
                ),
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
            },
            "000001.SZ": self.symbol_feature_values["000001.SZ"],
            "300750.SZ": self.symbol_feature_values["300750.SZ"],
        }

        with self.assertRaisesRegex(
            StaleFeatureValueError,
            r"symbol '600000\.SH': stale feature value for valuation\[lag_days=1\]@2026-06-03",
        ):
            run_scan(
                metadata=self.metadata,
                universe=self.universe,
                filters=self.filters,
                symbol_feature_values=symbol_feature_values,
                constraint_policies=ScanConstraintPolicies(
                    stale_feature_policy=StaleFeaturePolicy.FAIL
                ),
            )

        result = run_scan_with_diagnostics(
            metadata=self.metadata,
            universe=self.universe,
            filters=self.filters,
            symbol_feature_values=symbol_feature_values,
            constraint_policies=ScanConstraintPolicies(
                stale_feature_policy=StaleFeaturePolicy.EXCLUDE
            ),
        )
        self.assertEqual(
            tuple(candidate.symbol for candidate in result.candidate_list.candidates),
            ("000001.SZ",),
        )
        self.assertEqual(
            tuple(
                (decision.symbol, decision.reason_code, decision.detail)
                for decision in result.symbol_decisions
            ),
            (("600000.SH", "stale_feature", "valuation[lag_days=1]@2026-06-03"),),
        )

    def test_run_scan_rejects_invalid_ranking_config(self) -> None:
        with self.assertRaisesRegex(
            InvalidScanRankingConfigError,
            r"invalid ranking config: criteria\[0\]\.direction: unsupported_direction",
        ):
            run_scan(
                metadata=self.metadata,
                universe=self.universe,
                filters=self.filters,
                symbol_feature_values=self.symbol_feature_values,
                ranking={
                    "criteria": (
                        {
                            "feature_ref": {
                                "feature_name": FeatureName.PRICE_TECHNICAL,
                                "lag_days": 0,
                            },
                            "direction": "sideways",
                        },
                    )
                },
            )

    def test_run_scan_rejects_invalid_ranking_feature_value(self) -> None:
        symbol_feature_values = {
            "600000.SH": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.02,
                FeatureReference(FeatureName.VALUATION, lag_days=1): 0.10,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
                FeatureReference(FeatureName.RELATIVE, lag_days=0): "top",
            },
            "000001.SZ": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.03,
                FeatureReference(FeatureName.VALUATION, lag_days=1): 0.09,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
                FeatureReference(FeatureName.RELATIVE, lag_days=0): 0.02,
            },
            "300750.SZ": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.05,
                FeatureReference(FeatureName.VALUATION, lag_days=1): 0.12,
                FeatureReference(FeatureName.CAPITAL_FLOW, lag_days=0): "positive",
                FeatureReference(FeatureName.RELATIVE, lag_days=0): 0.01,
            },
        }

        with self.assertRaisesRegex(
            InvalidRankingFeatureValueError,
            r"invalid ranking feature value for symbol '600000\.SH' and relative\[lag_days=0\]",
        ):
            run_scan(
                metadata=self.metadata,
                universe=self.universe,
                filters=self.filters,
                symbol_feature_values=symbol_feature_values,
                ranking=ScanRankingConfig(
                    criteria=(
                        RankingCriterion(
                            feature_ref=FeatureReference(FeatureName.RELATIVE, lag_days=0),
                            direction=RankingDirection.DESC,
                        ),
                    )
                ),
            )

    def test_market_constraints_require_symbol_market_state_when_enabled(self) -> None:
        with self.assertRaisesRegex(
            MissingEligibilityStateError,
            r"missing symbol market states for symbols: \['000001\.SZ', '300750\.SZ', '600000\.SH'\]",
        ):
            run_scan_with_diagnostics(
                metadata=self.metadata,
                universe=self.universe,
                filters=self.filters,
                symbol_feature_values=self.symbol_feature_values,
                constraint_policies=ScanConstraintPolicies(exclude_limit_up=True),
            )

    def test_run_scan_requires_feature_values_for_every_universe_symbol(self) -> None:
        symbol_feature_values = dict(self.symbol_feature_values)
        del symbol_feature_values["300750.SZ"]

        with self.assertRaisesRegex(
            MissingSymbolFeatureValuesError,
            r"missing symbol feature values for symbols: \['300750\.SZ'\]",
        ):
            run_scan(
                metadata=self.metadata,
                universe=self.universe,
                filters=self.filters,
                symbol_feature_values=symbol_feature_values,
            )

    def test_run_scan_rejects_malformed_symbol_feature_mapping(self) -> None:
        symbol_feature_values = dict(self.symbol_feature_values)
        symbol_feature_values["000001.SZ"] = {"price_technical": 0.03}

        with self.assertRaisesRegex(
            InvalidScanRunnerInputError,
            r"symbol_feature_values\['000001\.SZ'\] keys must be FeatureReference instances",
        ):
            run_scan(
                metadata=self.metadata,
                universe=self.universe,
                filters=self.filters,
                symbol_feature_values=symbol_feature_values,
            )

    def test_run_scan_rejects_malformed_metadata_payload(self) -> None:
        with self.assertRaisesRegex(
            InvalidScanRunnerInputError,
            r"invalid scan metadata: payload must be a dataclass instance or mapping",
        ):
            run_scan(
                metadata="scan-2026-06-04-cn-core",
                universe=self.universe,
                filters=self.filters,
                symbol_feature_values=self.symbol_feature_values,
            )

    def test_run_scan_rejects_duplicate_universe_symbols(self) -> None:
        duplicate_universe = UniverseMembershipInput(
            universe_id="cn-core",
            universe_name="CN Core",
            market="CN",
            as_of_date="2026-06-04",
            symbols=("000001.SZ", "000001.SZ"),
        )
        symbol_feature_values = {
            "000001.SZ": self.symbol_feature_values["000001.SZ"],
        }

        with self.assertRaisesRegex(
            InvalidScanRunnerInputError,
            r"invalid universe input: symbols: duplicate_symbol",
        ):
            run_scan(
                metadata=self.metadata,
                universe=duplicate_universe,
                filters=self.filters,
                symbol_feature_values=symbol_feature_values,
            )

    def test_run_scan_surfaces_invalid_filter_specs(self) -> None:
        filters = (
            {
                "filter_id": "broken",
                "feature_ref": {
                    "feature_name": FeatureName.PRICE_TECHNICAL,
                    "lag_days": 0,
                },
                "operator": "contains",
                "threshold": 1.0,
            },
        )
        symbol_feature_values = {
            "600000.SH": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.02,
            },
            "000001.SZ": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.03,
            },
            "300750.SZ": {
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0): 0.05,
            },
        }

        with self.assertRaisesRegex(
            InvalidFilterSpecError,
            r"invalid filter spec: operator: unsupported_operator",
        ):
            run_scan(
                metadata=self.metadata,
                universe=self.universe,
                filters=filters,
                symbol_feature_values=symbol_feature_values,
            )

    def test_run_scan_rejects_invalid_generated_candidate_list(self) -> None:
        mismatched_metadata = ScanRunMetadata(
            run_id="scan-2026-06-04-cn-core",
            scanner_id="foundation_scan",
            trade_date="2026-06-04",
            universe_id="wrong-universe",
            generated_at=datetime(2026, 6, 4, 9, 30, 0),
        )
        symbol_feature_values = {
            "000001.SZ": self.symbol_feature_values["000001.SZ"],
            "300750.SZ": self.symbol_feature_values["300750.SZ"],
            "600000.SH": self.symbol_feature_values["600000.SH"],
        }

        with self.assertRaisesRegex(
            InvalidScanOutputError,
            r"generated candidate list failed validation: candidates\[0\]\.universe_id: metadata_mismatch",
        ):
            run_scan(
                metadata=mismatched_metadata,
                universe=self.universe,
                filters=self.filters,
                symbol_feature_values=symbol_feature_values,
            )


if __name__ == "__main__":
    unittest.main()
