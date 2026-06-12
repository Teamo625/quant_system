import importlib
import unittest
from datetime import datetime

from quant.features.contracts import FeatureName
from quant.scanner.contracts import (
    RANKING_CRITERION_FIELDS,
    SCANNER_CONTRACT_SCHEMA_VERSION,
    SCANNER_RANKING_SCORE_FORMULA,
    SCANNER_RANKING_TIE_BREAK_ORDER,
    FeatureReference,
    FilterOperator,
    FilterSpec,
    RankingCriterion,
    RankingDirection,
    ScanArtifactContext,
    ScanArtifactHandoffMetadata,
    ScanArtifactRankingMetadata,
    ScanArtifactUniverseSnapshot,
    ScanRankingConfig,
    ScanCandidateList,
    ScanCandidateRecord,
    ScanRunMetadata,
    UniverseMembershipInput,
    UniverseFamily,
    UniversePreset,
    validate_feature_reference,
    validate_filter_spec,
    validate_scan_artifact_context,
    validate_scan_ranking_config,
    validate_scan_candidate_list,
    validate_universe_membership_input,
)


class ScannerContractsTestCase(unittest.TestCase):
    def test_scanner_package_imports_cleanly(self) -> None:
        package = importlib.import_module("quant.scanner")
        module = importlib.import_module("quant.scanner.contracts")

        self.assertTrue(hasattr(package, "UniverseMembershipInput"))
        self.assertTrue(hasattr(package, "FeatureReference"))
        self.assertTrue(hasattr(package, "FilterSpec"))
        self.assertTrue(hasattr(package, "ScanCandidateList"))
        self.assertTrue(hasattr(package, "ScanRankingConfig"))
        self.assertTrue(hasattr(package, "ScanArtifactContext"))
        self.assertTrue(hasattr(package, "UniverseFamily"))
        self.assertTrue(hasattr(package, "UniversePreset"))
        self.assertTrue(hasattr(module, "FilterOperator"))
        self.assertTrue(hasattr(module, "RankingDirection"))

    def test_universe_family_and_preset_enums_are_stable(self) -> None:
        self.assertEqual(UniverseFamily.A_SHARE.value, "a_share")
        self.assertEqual(UniversePreset.INDEX_CONSTITUENTS.value, "index_constituents")
        self.assertEqual(RankingDirection.DESC.value, "desc")
        self.assertEqual(RANKING_CRITERION_FIELDS, ("feature_ref", "direction", "weight"))

    def test_valid_scan_candidate_list_passes_validation(self) -> None:
        payload = ScanCandidateList(
            metadata=ScanRunMetadata(
                run_id="scan-2026-06-04-cn-core",
                scanner_id="value_breakout_watchlist",
                trade_date="2026-06-04",
                universe_id="cn-core",
                generated_at=datetime(2026, 6, 4, 9, 30, 0),
            ),
            feature_refs=(
                FeatureReference(
                    feature_name=FeatureName.PRICE_TECHNICAL,
                    lag_days=0,
                ),
                FeatureReference(
                    feature_name=FeatureName.VALUATION,
                    lag_days=1,
                ),
            ),
            filters=(
                FilterSpec(
                    filter_id="close_above_ma20",
                    feature_ref=FeatureReference(
                        feature_name=FeatureName.PRICE_TECHNICAL,
                    ),
                    operator=FilterOperator.GT,
                    threshold=0.0,
                ),
                FilterSpec(
                    filter_id="earnings_yield_floor",
                    feature_ref=FeatureReference(
                        feature_name=FeatureName.VALUATION,
                        lag_days=1,
                    ),
                    operator=FilterOperator.GTE,
                    threshold=0.08,
                ),
            ),
            candidates=(
                ScanCandidateRecord(
                    run_id="scan-2026-06-04-cn-core",
                    trade_date="2026-06-04",
                    symbol="000001.SZ",
                    market="CN",
                    universe_id="cn-core",
                    matched_filter_ids=(
                        "close_above_ma20",
                        "earnings_yield_floor",
                    ),
                ),
                ScanCandidateRecord(
                    run_id="scan-2026-06-04-cn-core",
                    trade_date="2026-06-04",
                    symbol="600000.SH",
                    market="CN",
                    universe_id="cn-core",
                    matched_filter_ids=("close_above_ma20",),
                ),
            ),
        )

        self.assertEqual(validate_scan_candidate_list(payload), ())

    def test_universe_membership_requires_iso_trade_date_and_unique_symbols(self) -> None:
        issues = validate_universe_membership_input(
            UniverseMembershipInput(
                universe_id="cn-core",
                universe_name="CN Core",
                market="CN",
                as_of_date="2026/06/04",
                symbols=("600000.SH", "600000.SH"),
            )
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                ("as_of_date", "invalid_date_string"),
                ("symbols", "duplicate_symbol"),
            },
        )

    def test_feature_reference_rejects_non_declarative_extra_fields(self) -> None:
        issues = validate_feature_reference(
            {
                "feature_name": FeatureName.CAPITAL_FLOW,
                "lag_days": 0,
                "loader": "read_feature_records_jsonl",
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {("loader", "unexpected_field")},
        )

    def test_filter_spec_rejects_unsupported_operators_and_bad_thresholds(self) -> None:
        unsupported_operator_issues = validate_filter_spec(
            {
                "filter_id": "mystery",
                "feature_ref": {
                    "feature_name": FeatureName.PRICE_TECHNICAL,
                    "lag_days": 0,
                },
                "operator": "contains",
                "threshold": 1.0,
            }
        )
        malformed_threshold_issues = validate_filter_spec(
            {
                "filter_id": "band",
                "feature_ref": {
                    "feature_name": FeatureName.VALUATION,
                    "lag_days": 0,
                },
                "operator": FilterOperator.BETWEEN,
                "threshold": (2.0, 1.0),
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in unsupported_operator_issues},
            {("operator", "unsupported_operator")},
        )
        self.assertEqual(
            {(issue.field, issue.code) for issue in malformed_threshold_issues},
            {("threshold", "invalid_threshold")},
        )

    def test_ranking_config_rejects_duplicate_features_and_bad_direction(self) -> None:
        issues = validate_scan_ranking_config(
            {
                "criteria": (
                    {
                        "feature_ref": {
                            "feature_name": FeatureName.PRICE_TECHNICAL,
                            "lag_days": 0,
                        },
                        "direction": RankingDirection.DESC,
                        "weight": 1.5,
                    },
                    {
                        "feature_ref": {
                            "feature_name": FeatureName.PRICE_TECHNICAL,
                            "lag_days": 0,
                        },
                        "direction": "sideways",
                        "weight": 0.0,
                    },
                )
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                ("criteria", "duplicate_ranking_feature"),
                ("criteria[1].direction", "unsupported_direction"),
                ("criteria[1].weight", "invalid_weight"),
            },
        )

    def test_ranked_candidate_list_passes_validation(self) -> None:
        payload = ScanCandidateList(
            metadata=ScanRunMetadata(
                run_id="scan-2026-06-05-cn-ranked",
                scanner_id="ranked_value_breakout_watchlist",
                trade_date="2026-06-05",
                universe_id="cn-ranked",
                generated_at=datetime(2026, 6, 5, 9, 30, 0),
                artifact_context=ScanArtifactContext(
                    universe_snapshot=ScanArtifactUniverseSnapshot(
                        universe_id="cn-ranked",
                        universe_name="CN Ranked",
                        market="CN",
                        as_of_date="2026-06-05",
                        symbols=("000001.SZ", "600000.SH"),
                        source="manual_fixture",
                        family=UniverseFamily.A_SHARE,
                        preset=UniversePreset.A_SHARE_ALL,
                    ),
                    ranking=ScanArtifactRankingMetadata(
                        criteria=(
                            RankingCriterion(
                                feature_ref=FeatureReference(
                                    FeatureName.RELATIVE,
                                    lag_days=0,
                                ),
                                direction=RankingDirection.DESC,
                                weight=2.0,
                            ),
                        ),
                    ),
                    handoff=ScanArtifactHandoffMetadata(),
                ),
            ),
            feature_refs=(
                FeatureReference(FeatureName.PRICE_TECHNICAL, lag_days=0),
                FeatureReference(FeatureName.RELATIVE, lag_days=0),
            ),
            filters=(
                FilterSpec(
                    filter_id="above_zero",
                    feature_ref=FeatureReference(FeatureName.PRICE_TECHNICAL),
                    operator=FilterOperator.GT,
                    threshold=0.0,
                ),
            ),
            candidates=(
                ScanCandidateRecord(
                    run_id="scan-2026-06-05-cn-ranked",
                    trade_date="2026-06-05",
                    symbol="000001.SZ",
                    market="CN",
                    universe_id="cn-ranked",
                    matched_filter_ids=("above_zero",),
                    score=1.4,
                    rank=1,
                ),
                ScanCandidateRecord(
                    run_id="scan-2026-06-05-cn-ranked",
                    trade_date="2026-06-05",
                    symbol="600000.SH",
                    market="CN",
                    universe_id="cn-ranked",
                    matched_filter_ids=("above_zero",),
                    score=1.2,
                    rank=2,
                ),
            ),
        )

        self.assertEqual(validate_scan_candidate_list(payload), ())

    def test_artifact_context_validation_accepts_ranked_reproducibility_metadata(self) -> None:
        issues = validate_scan_artifact_context(
            ScanArtifactContext(
                universe_snapshot=ScanArtifactUniverseSnapshot(
                    universe_id="cn-core",
                    universe_name="CN Core",
                    market="CN",
                    as_of_date="2026-06-04",
                    symbols=("000001.SZ", "600000.SH"),
                    source="manual_fixture",
                    family=UniverseFamily.A_SHARE,
                    preset=UniversePreset.A_SHARE_ALL,
                ),
                ranking=ScanArtifactRankingMetadata(
                    criteria=(
                        RankingCriterion(
                            feature_ref=FeatureReference(
                                FeatureName.RELATIVE,
                                lag_days=0,
                            ),
                            direction=RankingDirection.DESC,
                            weight=1.5,
                        ),
                    ),
                    score_formula=SCANNER_RANKING_SCORE_FORMULA,
                    tie_break_order=SCANNER_RANKING_TIE_BREAK_ORDER,
                ),
                handoff=ScanArtifactHandoffMetadata(),
            )
        )

        self.assertEqual(issues, ())

    def test_candidate_list_enforces_metadata_alignment_and_deterministic_order(self) -> None:
        issues = validate_scan_candidate_list(
            {
                "metadata": {
                    "run_id": "scan-2026-06-04-cn-core",
                    "scanner_id": "value_breakout_watchlist",
                    "trade_date": "2026-06-04",
                    "universe_id": "cn-core",
                    "generated_at": datetime(2026, 6, 4, 9, 30, 0),
                    "schema_version": SCANNER_CONTRACT_SCHEMA_VERSION,
                },
                "feature_refs": [
                    {"feature_name": FeatureName.PRICE_TECHNICAL, "lag_days": 0},
                ],
                "filters": [
                    {
                        "filter_id": "close_above_ma20",
                        "feature_ref": {
                            "feature_name": FeatureName.PRICE_TECHNICAL,
                            "lag_days": 0,
                        },
                        "operator": FilterOperator.GT,
                        "threshold": 0.0,
                    }
                ],
                "candidates": [
                    {
                        "run_id": "wrong-run",
                        "trade_date": "2026-06-04",
                        "symbol": "600000.SH",
                        "market": "CN",
                        "universe_id": "cn-core",
                        "matched_filter_ids": ("close_above_ma20",),
                    },
                    {
                        "run_id": "scan-2026-06-04-cn-core",
                        "trade_date": "2026-06-04",
                        "symbol": "000001.SZ",
                        "market": "CN",
                        "universe_id": "cn-core",
                        "matched_filter_ids": ("unknown_filter",),
                    },
                ],
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                ("candidates", "non_deterministic_order"),
                ("candidates[0].run_id", "metadata_mismatch"),
                ("candidates[1].matched_filter_ids", "unknown_filter_id"),
            },
        )

    def test_ranked_candidate_list_rejects_non_contiguous_mixed_ordering(self) -> None:
        issues = validate_scan_candidate_list(
            {
                "metadata": {
                    "run_id": "scan-2026-06-05-cn-ranked",
                    "scanner_id": "ranked_value_breakout_watchlist",
                    "trade_date": "2026-06-05",
                    "universe_id": "cn-ranked",
                    "generated_at": datetime(2026, 6, 5, 9, 30, 0),
                    "schema_version": SCANNER_CONTRACT_SCHEMA_VERSION,
                },
                "feature_refs": [
                    {"feature_name": FeatureName.PRICE_TECHNICAL, "lag_days": 0},
                ],
                "filters": [
                    {
                        "filter_id": "above_zero",
                        "feature_ref": {
                            "feature_name": FeatureName.PRICE_TECHNICAL,
                            "lag_days": 0,
                        },
                        "operator": FilterOperator.GT,
                        "threshold": 0.0,
                    }
                ],
                "candidates": [
                    {
                        "run_id": "scan-2026-06-05-cn-ranked",
                        "trade_date": "2026-06-05",
                        "symbol": "600000.SH",
                        "market": "CN",
                        "universe_id": "cn-ranked",
                        "matched_filter_ids": ("above_zero",),
                        "score": 1.2,
                        "rank": 2,
                    },
                    {
                        "run_id": "scan-2026-06-05-cn-ranked",
                        "trade_date": "2026-06-05",
                        "symbol": "000001.SZ",
                        "market": "CN",
                        "universe_id": "cn-ranked",
                        "matched_filter_ids": ("above_zero",),
                        "score": 1.0,
                    },
                ],
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                ("candidates", "mixed_ranking_fields"),
                ("candidates", "non_contiguous_rank"),
                ("candidates[1].rank", "ranking_field_pair_required"),
            },
        )

    def test_ranked_candidate_list_requires_ranking_artifact_metadata_when_context_present(self) -> None:
        issues = validate_scan_candidate_list(
            {
                "metadata": {
                    "run_id": "scan-2026-06-05-cn-ranked",
                    "scanner_id": "ranked_value_breakout_watchlist",
                    "trade_date": "2026-06-05",
                    "universe_id": "cn-ranked",
                    "generated_at": datetime(2026, 6, 5, 9, 30, 0),
                    "schema_version": SCANNER_CONTRACT_SCHEMA_VERSION,
                    "artifact_context": {
                        "universe_snapshot": {
                            "universe_id": "cn-ranked",
                            "universe_name": "CN Ranked",
                            "market": "CN",
                            "as_of_date": "2026-06-05",
                            "symbols": ("000001.SZ", "600000.SH"),
                        },
                        "handoff": {
                            "artifact_type": "scanner_candidate_list",
                            "artifact_purpose": "research_candidate_handoff",
                            "producer_name": "scanner",
                            "intended_consumers": ("strategy_lab", "signal_engine"),
                        },
                    },
                },
                "feature_refs": [
                    {"feature_name": FeatureName.PRICE_TECHNICAL, "lag_days": 0},
                    {"feature_name": FeatureName.RELATIVE, "lag_days": 0},
                ],
                "filters": [
                    {
                        "filter_id": "above_zero",
                        "feature_ref": {
                            "feature_name": FeatureName.PRICE_TECHNICAL,
                            "lag_days": 0,
                        },
                        "operator": FilterOperator.GT,
                        "threshold": 0.0,
                    }
                ],
                "candidates": [
                    {
                        "run_id": "scan-2026-06-05-cn-ranked",
                        "trade_date": "2026-06-05",
                        "symbol": "000001.SZ",
                        "market": "CN",
                        "universe_id": "cn-ranked",
                        "matched_filter_ids": ("above_zero",),
                        "score": 1.4,
                        "rank": 1,
                    },
                    {
                        "run_id": "scan-2026-06-05-cn-ranked",
                        "trade_date": "2026-06-05",
                        "symbol": "600000.SH",
                        "market": "CN",
                        "universe_id": "cn-ranked",
                        "matched_filter_ids": ("above_zero",),
                        "score": 1.2,
                        "rank": 2,
                    },
                ],
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                (
                    "metadata.artifact_context.ranking",
                    "missing_required_for_ranked_candidates",
                ),
            },
        )

    def test_empty_ranked_candidate_list_allows_ranking_artifact_metadata(self) -> None:
        issues = validate_scan_candidate_list(
            {
                "metadata": {
                    "run_id": "scan-2026-06-05-cn-ranked-empty",
                    "scanner_id": "ranked_empty_scan",
                    "trade_date": "2026-06-05",
                    "universe_id": "cn-ranked",
                    "generated_at": datetime(2026, 6, 5, 9, 30, 0),
                    "schema_version": SCANNER_CONTRACT_SCHEMA_VERSION,
                    "artifact_context": {
                        "universe_snapshot": {
                            "universe_id": "cn-ranked",
                            "universe_name": "CN Ranked",
                            "market": "CN",
                            "as_of_date": "2026-06-05",
                            "symbols": ("000001.SZ", "600000.SH"),
                        },
                        "ranking": {
                            "criteria": (
                                {
                                    "feature_ref": {
                                        "feature_name": FeatureName.RELATIVE,
                                        "lag_days": 0,
                                    },
                                    "direction": RankingDirection.DESC,
                                    "weight": 1.0,
                                },
                            ),
                            "score_formula": SCANNER_RANKING_SCORE_FORMULA,
                            "tie_break_order": SCANNER_RANKING_TIE_BREAK_ORDER,
                        },
                        "handoff": {
                            "artifact_type": "scanner_candidate_list",
                            "artifact_purpose": "research_candidate_handoff",
                            "producer_name": "scanner",
                            "intended_consumers": ("strategy_lab", "signal_engine"),
                        },
                    },
                },
                "feature_refs": [
                    {"feature_name": FeatureName.PRICE_TECHNICAL, "lag_days": 0},
                    {"feature_name": FeatureName.RELATIVE, "lag_days": 0},
                ],
                "filters": [
                    {
                        "filter_id": "above_zero",
                        "feature_ref": {
                            "feature_name": FeatureName.PRICE_TECHNICAL,
                            "lag_days": 0,
                        },
                        "operator": FilterOperator.GT,
                        "threshold": 0.0,
                    },
                ],
                "candidates": [],
            },
        )

        self.assertEqual(issues, ())


if __name__ == "__main__":
    unittest.main()
