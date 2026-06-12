import unittest

from quant.scanner import (
    SymbolDecisionAction,
    UniverseDefinition,
    UniverseExclusionInput,
    UniverseFamily,
    UniverseMembershipInput,
    UniversePreset,
    build_universe_membership_snapshot,
    compose_universe_membership,
    normalize_universe_symbols,
    validate_supported_scan_universe_definition,
    validate_universe_definition,
    validate_universe_membership_snapshot,
)


class ScannerUniverseTestCase(unittest.TestCase):
    def test_build_membership_snapshot_normalizes_symbols_deterministically(self) -> None:
        snapshot = build_universe_membership_snapshot(
            definition=UniverseDefinition(
                universe_id="cn-core",
                universe_name="CN Core",
                market="CN",
                source="manual_fixture",
            ),
            as_of_date="2026-06-04",
            symbols=(" 600000.sh ", "000001.sz"),
        )

        self.assertEqual(snapshot.universe_id, "cn-core")
        self.assertEqual(snapshot.symbols, ("000001.SZ", "600000.SH"))
        self.assertEqual(
            validate_universe_membership_snapshot(
                definition=UniverseDefinition(
                    universe_id="cn-core",
                    universe_name="CN Core",
                    market="CN",
                    source="manual_fixture",
                ),
                snapshot=snapshot,
            ),
            (),
        )

    def test_universe_definition_requires_identity_fields(self) -> None:
        issues = validate_universe_definition(
            {
                "universe_id": "",
                "universe_name": "CN Core",
                "market": "CN",
                "description": 123,
                "loader": "read_datahub_storage",
            }
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                ("universe_id", "invalid_text"),
                ("source", "missing_required"),
                ("description", "invalid_type"),
                ("loader", "unexpected_field"),
            },
        )

    def test_supported_scan_universe_requires_family_or_preset(self) -> None:
        issues = validate_supported_scan_universe_definition(
            UniverseDefinition(
                universe_id="cn-core",
                universe_name="CN Core",
                market="CN",
                source="manual_fixture",
            )
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {("family", "missing_required")},
        )

    def test_supported_scan_universe_rejects_inconsistent_family_market_combo(self) -> None:
        issues = validate_supported_scan_universe_definition(
            UniverseDefinition(
                universe_id="hk-invalid",
                universe_name="HK Invalid",
                market="CN",
                source="manual_fixture",
                family=UniverseFamily.HONG_KONG_STOCK,
                preset=UniversePreset.HONG_KONG_STOCK_ALL,
            )
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                ("market", "unsupported_family_market_combo"),
                ("market", "unsupported_preset_market_combo"),
            },
        )

    def test_normalize_symbols_rejects_duplicates_after_normalization(self) -> None:
        with self.assertRaisesRegex(ValueError, "unique after normalization"):
            normalize_universe_symbols(("600000.sh", " 600000.SH "))

    def test_snapshot_validation_rejects_mismatch_and_unsorted_symbols(self) -> None:
        issues = validate_universe_membership_snapshot(
            definition=UniverseDefinition(
                universe_id="cn-core",
                universe_name="CN Core",
                market="CN",
                source="manual_fixture",
            ),
            snapshot=UniverseMembershipInput(
                universe_id="cn-core",
                universe_name="CN Core",
                market="HK",
                as_of_date="2026-06-04",
                symbols=("600000.SH", "000001.SZ"),
            ),
        )

        self.assertEqual(
            {(issue.field, issue.code) for issue in issues},
            {
                ("snapshot.market", "definition_mismatch"),
                ("snapshot.symbols", "non_deterministic_order"),
            },
        )

    def test_build_membership_snapshot_rejects_bad_dates_without_network(self) -> None:
        with self.assertRaisesRegex(ValueError, "as_of_date: invalid_date_string"):
            build_universe_membership_snapshot(
                definition={
                    "universe_id": "cn-core",
                    "universe_name": "CN Core",
                    "market": "CN",
                    "source": "manual_fixture",
                },
                as_of_date="2026/06/04",
                symbols=("000001.SZ",),
            )

    def test_compose_universe_membership_applies_exclusions_without_mutating_snapshot(self) -> None:
        snapshot = UniverseMembershipInput(
            universe_id="cn-all",
            universe_name="CN All",
            market="CN",
            as_of_date="2026-06-04",
            symbols=("000001.SZ", "300750.SZ", "600000.SH"),
        )
        result = compose_universe_membership(
            definition=UniverseDefinition(
                universe_id="cn-all",
                universe_name="CN All",
                market="CN",
                source="manual_fixture",
                family=UniverseFamily.A_SHARE,
                preset=UniversePreset.A_SHARE_ALL,
            ),
            snapshot=snapshot,
            exclusions=(
                UniverseExclusionInput(
                    exclusion_list_id="risk-blacklist",
                    market="CN",
                    symbols=("300750.sz", "600000.sh"),
                    reason="manual_block",
                ),
            ),
        )

        self.assertEqual(result.snapshot.symbols, snapshot.symbols)
        self.assertEqual(result.effective_symbols, ("000001.SZ",))
        self.assertEqual(
            tuple(
                (decision.symbol, decision.action, decision.reason_code, decision.detail)
                for decision in result.symbol_decisions
            ),
            (
                (
                    "300750.SZ",
                    SymbolDecisionAction.EXCLUDED,
                    "universe_exclusion",
                    "risk-blacklist:manual_block",
                ),
                (
                    "600000.SH",
                    SymbolDecisionAction.EXCLUDED,
                    "universe_exclusion",
                    "risk-blacklist:manual_block",
                ),
            ),
        )

    def test_exclusion_market_must_match_snapshot_market(self) -> None:
        with self.assertRaisesRegex(ValueError, "market must match snapshot market"):
            compose_universe_membership(
                definition=UniverseDefinition(
                    universe_id="cn-all",
                    universe_name="CN All",
                    market="CN",
                    source="manual_fixture",
                    family=UniverseFamily.A_SHARE,
                ),
                snapshot=UniverseMembershipInput(
                    universe_id="cn-all",
                    universe_name="CN All",
                    market="CN",
                    as_of_date="2026-06-04",
                    symbols=("000001.SZ",),
                ),
                exclusions=(
                    UniverseExclusionInput(
                        exclusion_list_id="wrong-market",
                        market="HK",
                        symbols=("000001.SZ",),
                    ),
                ),
            )


if __name__ == "__main__":
    unittest.main()
