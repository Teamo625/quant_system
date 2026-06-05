import unittest
from unittest.mock import patch

from quant.datahub.datasets import DatasetName
from quant.datahub.personal_readiness import (
    OperationalReadinessEvidence,
    ReadinessStatus,
    build_default_personal_trading_readiness_report,
    build_personal_trading_readiness_report,
)
from quant.datahub.source_capabilities import (
    CapabilityDomain,
    CapabilityRequirement,
    CapabilityStatus,
    ResearchHorizon,
    SourceCapability,
    SourceCapabilityAudit,
)
from quant.datahub.source_catalog import build_default_source_catalog


class PersonalTradingReadinessTests(unittest.TestCase):
    def test_default_report_covers_expected_domains_and_is_not_closure_ready(self) -> None:
        report = build_default_personal_trading_readiness_report()

        self.assertEqual(
            {domain.domain_id for domain in report.domains},
            {
                "a_share",
                "hong_kong",
                "etf_fund",
                "index",
                "sector_concept",
                "macro_policy",
                "local_storage",
                "refresh_metadata",
                "quality_reports",
                "source_health_diagnostics",
            },
        )
        self.assertEqual(report.overall_status, ReadinessStatus.BLOCKED)
        self.assertFalse(report.phase_closure_ready)

        counts = report.status_counts()
        self.assertEqual(counts[ReadinessStatus.PASS], 3)
        self.assertEqual(counts[ReadinessStatus.WARN], 6)
        self.assertEqual(counts[ReadinessStatus.BLOCKED], 1)
        self.assertEqual(counts[ReadinessStatus.FAIL], 0)

    def test_index_domain_keeps_index_weight_history_blocked(self) -> None:
        report = build_default_personal_trading_readiness_report()
        index_domain = report.domain_by_id("index")
        readiness_check = next(
            check
            for check in index_domain.checks
            if check.check_id == "index_capability_readiness"
        )

        self.assertEqual(index_domain.status, ReadinessStatus.BLOCKED)
        self.assertEqual(readiness_check.status, ReadinessStatus.BLOCKED)
        self.assertTrue(
            any("index_weight_history" in item for item in readiness_check.evidence)
        )
        self.assertTrue(
            any("live smoke" in item.lower() for item in readiness_check.follow_ups)
        )
        self.assertTrue(
            any("promote only after" in item.lower() for item in readiness_check.follow_ups)
        )

    def test_operational_domains_use_offline_smoke_evidence(self) -> None:
        report = build_default_personal_trading_readiness_report()

        self.assertTrue(report.operational_evidence.success)
        self.assertEqual(report.operational_evidence.dataset, DatasetName.DAILY_BARS)
        self.assertTrue(report.operational_evidence.raw_written)
        self.assertTrue(report.operational_evidence.curated_written)
        self.assertTrue(report.operational_evidence.metadata_written)
        self.assertTrue(report.operational_evidence.quality_written)
        self.assertIn(
            "source_availability_health",
            set(report.operational_evidence.quality_check_names),
        )
        self.assertEqual(report.operational_evidence.source_health_status, "pass")

        storage_domain = report.domain_by_id("local_storage")
        refresh_domain = report.domain_by_id("refresh_metadata")
        quality_domain = report.domain_by_id("quality_reports")
        source_health_domain = report.domain_by_id("source_health_diagnostics")

        self.assertEqual(storage_domain.status, ReadinessStatus.PASS)
        self.assertEqual(refresh_domain.status, ReadinessStatus.PASS)
        self.assertEqual(quality_domain.status, ReadinessStatus.WARN)
        self.assertEqual(source_health_domain.status, ReadinessStatus.PASS)

    def test_default_report_is_offline_only(self) -> None:
        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            report = build_default_personal_trading_readiness_report()
            self.assertEqual(report.operational_evidence.source_health_status, "pass")

    def test_required_capability_without_dataset_contract_fails_integrity(self) -> None:
        broken_capability = SourceCapability(
            capability_id="broken_required_contract",
            capability_name="Broken required contract",
            horizons=(ResearchHorizon.SHORT_TERM,),
            domain=CapabilityDomain.A_SHARE,
            granularity="synthetic",
            requirement=CapabilityRequirement.REQUIRED,
            dataset_mappings=(),
            source_family_ids=("akshare_cn_hk_public_family",),
            status=CapabilityStatus.COVERED,
            gap_reason="",
            recommended_handoff_theme="restore contract mapping",
        )
        report = build_personal_trading_readiness_report(
            capability_audit=SourceCapabilityAudit(
                capabilities=(broken_capability,),
                source_catalog=build_default_source_catalog(),
            ),
            source_catalog=build_default_source_catalog(),
            operational_evidence=_passing_operational_evidence(),
        )

        a_share_domain = report.domain_by_id("a_share")
        integrity_check = next(
            check
            for check in a_share_domain.checks
            if check.check_id == "a_share_integrity"
        )

        self.assertEqual(a_share_domain.status, ReadinessStatus.FAIL)
        self.assertEqual(integrity_check.status, ReadinessStatus.FAIL)
        self.assertTrue(
            any("required capabilities without dataset contracts" in item for item in integrity_check.evidence)
        )

    def test_missing_source_catalog_mapping_fails_integrity(self) -> None:
        broken_capability = SourceCapability(
            capability_id="broken_required_source_mapping",
            capability_name="Broken required source mapping",
            horizons=(ResearchHorizon.SHORT_TERM,),
            domain=CapabilityDomain.A_SHARE,
            granularity="synthetic",
            requirement=CapabilityRequirement.REQUIRED,
            dataset_mappings=(DatasetName.DAILY_BARS,),
            source_family_ids=("missing_source_family",),
            status=CapabilityStatus.COVERED,
            gap_reason="",
            recommended_handoff_theme="restore source mapping",
        )
        report = build_personal_trading_readiness_report(
            capability_audit=SourceCapabilityAudit(
                capabilities=(broken_capability,),
                source_catalog=build_default_source_catalog(),
            ),
            source_catalog=build_default_source_catalog(),
            operational_evidence=_passing_operational_evidence(),
        )

        a_share_domain = report.domain_by_id("a_share")
        integrity_check = next(
            check
            for check in a_share_domain.checks
            if check.check_id == "a_share_integrity"
        )

        self.assertEqual(a_share_domain.status, ReadinessStatus.FAIL)
        self.assertEqual(integrity_check.status, ReadinessStatus.FAIL)
        self.assertTrue(
            any("missing_source_family" in item for item in integrity_check.evidence)
        )


def _passing_operational_evidence() -> OperationalReadinessEvidence:
    return OperationalReadinessEvidence(
        success=True,
        dataset=DatasetName.DAILY_BARS,
        raw_written=True,
        curated_written=True,
        metadata_written=True,
        quality_written=True,
        quality_check_names=(
            "record_count",
            "schema_validation",
            "metadata_written",
            "source_availability_health",
        ),
        source_health_status="pass",
        refresh_status="success",
    )


if __name__ == "__main__":
    unittest.main()
