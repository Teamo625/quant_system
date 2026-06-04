import unittest

from quant.scanner import (
    UniverseDefinition,
    build_universe_membership_snapshot,
    normalize_universe_symbols,
    validate_universe_definition,
    validate_universe_membership_snapshot,
)
from quant.scanner.contracts import UniverseMembershipInput


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


if __name__ == "__main__":
    unittest.main()
