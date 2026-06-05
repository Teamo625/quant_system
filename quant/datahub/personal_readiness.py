"""Deterministic personal trading readiness gate for DataHub re-review."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from enum import Enum
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable, Mapping, Sequence

from .config import DataHubConfig
from .datasets import DatasetName, DatasetRegistry
from .quality import LocalRefreshQualityHelper
from .refresh import run_local_warehouse_refresh
from .source import SOURCE_AVAILABILITY_HEALTH_CHECK_NAME, SourceRequest
from .source_capabilities import (
    CapabilityDomain,
    CapabilityRequirement,
    CapabilityStatus,
    SourceCapability,
    SourceCapabilityAudit,
    build_default_source_capability_audit,
)
from .source_catalog import InformationDomain, SourceCatalog, build_default_source_catalog
from .storage import LocalStorage


class ReadinessStatus(str, Enum):
    """Stable personal-readiness gate statuses."""

    PASS = "pass"
    WARN = "warn"
    BLOCKED = "blocked"
    FAIL = "fail"


@dataclass(frozen=True)
class ReadinessCheck:
    """One deterministic readiness check in the re-review matrix."""

    check_id: str
    title: str
    status: ReadinessStatus
    summary: str
    evidence: tuple[str, ...] = ()
    follow_ups: tuple[str, ...] = ()


@dataclass(frozen=True)
class DomainReadiness:
    """All readiness checks for one DataHub domain."""

    domain_id: str
    domain_name: str
    status: ReadinessStatus
    summary: str
    checks: tuple[ReadinessCheck, ...]

    def status_counts(self) -> dict[ReadinessStatus, int]:
        counts = {status: 0 for status in ReadinessStatus}
        for check in self.checks:
            counts[check.status] += 1
        return counts

    def follow_ups(self) -> tuple[str, ...]:
        items: list[str] = []
        for check in self.checks:
            for follow_up in check.follow_ups:
                if follow_up not in items:
                    items.append(follow_up)
        return tuple(items)


@dataclass(frozen=True)
class OperationalReadinessEvidence:
    """Deterministic offline operational evidence for local DataHub plumbing."""

    success: bool
    dataset: DatasetName
    raw_written: bool
    curated_written: bool
    metadata_written: bool
    quality_written: bool
    quality_check_names: tuple[str, ...]
    source_health_status: str | None
    refresh_status: str | None
    error_message: str | None = None


@dataclass(frozen=True)
class PersonalTradingReadinessReport:
    """Top-level result of the DataHub personal trading re-review gate."""

    domains: tuple[DomainReadiness, ...]
    operational_evidence: OperationalReadinessEvidence

    @property
    def overall_status(self) -> ReadinessStatus:
        return _aggregate_status(domain.status for domain in self.domains)

    @property
    def phase_closure_ready(self) -> bool:
        return all(domain.status == ReadinessStatus.PASS for domain in self.domains)

    def status_counts(self) -> dict[ReadinessStatus, int]:
        counts = {status: 0 for status in ReadinessStatus}
        for domain in self.domains:
            counts[domain.status] += 1
        return counts

    def follow_ups(self) -> tuple[str, ...]:
        items: list[str] = []
        for domain in self.domains:
            for follow_up in domain.follow_ups():
                if follow_up not in items:
                    items.append(follow_up)
        return tuple(items)

    def domain_by_id(self, domain_id: str) -> DomainReadiness:
        return next(domain for domain in self.domains if domain.domain_id == domain_id)


@dataclass(frozen=True)
class _DomainSpec:
    domain_id: str
    domain_name: str
    capability_domains: tuple[CapabilityDomain, ...]
    information_domains: tuple[InformationDomain, ...]


_DOMAIN_SPECS: tuple[_DomainSpec, ...] = (
    _DomainSpec(
        domain_id="a_share",
        domain_name="A-share",
        capability_domains=(CapabilityDomain.A_SHARE,),
        information_domains=(
            InformationDomain.A_SHARE_FULL_DATA,
            InformationDomain.EXCHANGE_CALENDAR,
        ),
    ),
    _DomainSpec(
        domain_id="hong_kong",
        domain_name="Hong Kong stock",
        capability_domains=(CapabilityDomain.HONG_KONG,),
        information_domains=(
            InformationDomain.HK_STOCK_FULL_DATA,
            InformationDomain.EXCHANGE_CALENDAR,
            InformationDomain.ANNOUNCEMENT,
        ),
    ),
    _DomainSpec(
        domain_id="etf_fund",
        domain_name="ETF/fund",
        capability_domains=(CapabilityDomain.ETF_FUND,),
        information_domains=(InformationDomain.ETF_FUND_FULL_DATA,),
    ),
    _DomainSpec(
        domain_id="index",
        domain_name="Index",
        capability_domains=(CapabilityDomain.INDEX,),
        information_domains=(InformationDomain.INDEX_DATA,),
    ),
    _DomainSpec(
        domain_id="sector_concept",
        domain_name="Sector/concept",
        capability_domains=(CapabilityDomain.SECTOR_CONCEPT,),
        information_domains=(InformationDomain.INDUSTRY_CONCEPT_SECTOR,),
    ),
    _DomainSpec(
        domain_id="macro_policy",
        domain_name="Macro/policy",
        capability_domains=(
            CapabilityDomain.MACRO,
            CapabilityDomain.POLICY_NEWS_ANNOUNCEMENT,
        ),
        information_domains=(
            InformationDomain.GLOBAL_MACRO,
            InformationDomain.CHINA_MACRO,
            InformationDomain.POLICY,
            InformationDomain.NEWS,
            InformationDomain.ANNOUNCEMENT,
        ),
    ),
)

_STATUS_PRIORITY: Mapping[ReadinessStatus, int] = {
    ReadinessStatus.PASS: 0,
    ReadinessStatus.WARN: 1,
    ReadinessStatus.BLOCKED: 2,
    ReadinessStatus.FAIL: 3,
}


def build_personal_trading_readiness_report(
    *,
    capability_audit: SourceCapabilityAudit | None = None,
    source_catalog: SourceCatalog | None = None,
    dataset_registry: DatasetRegistry | None = None,
    operational_evidence: OperationalReadinessEvidence | None = None,
) -> PersonalTradingReadinessReport:
    """Build the deterministic offline DataHub personal-readiness report."""

    resolved_catalog = source_catalog or build_default_source_catalog()
    resolved_audit = capability_audit or build_default_source_capability_audit()
    resolved_registry = dataset_registry or DatasetRegistry()
    resolved_operational_evidence = (
        operational_evidence
        if operational_evidence is not None
        else _run_offline_operational_smoke(dataset_registry=resolved_registry)
    )

    domains = [
        _build_market_domain_readiness(
            spec=spec,
            capability_audit=resolved_audit,
            source_catalog=resolved_catalog,
            dataset_registry=resolved_registry,
        )
        for spec in _DOMAIN_SPECS
    ]
    domains.extend(
        _build_operational_domains(
            capability_audit=resolved_audit,
            operational_evidence=resolved_operational_evidence,
        )
    )
    return PersonalTradingReadinessReport(
        domains=tuple(domains),
        operational_evidence=resolved_operational_evidence,
    )


def build_default_personal_trading_readiness_report() -> PersonalTradingReadinessReport:
    """Convenience wrapper for the repository-default personal-readiness gate."""

    return build_personal_trading_readiness_report()


def _build_market_domain_readiness(
    *,
    spec: _DomainSpec,
    capability_audit: SourceCapabilityAudit,
    source_catalog: SourceCatalog,
    dataset_registry: DatasetRegistry,
) -> DomainReadiness:
    capabilities = _capabilities_for_domains(capability_audit, spec.capability_domains)
    integrity_check = _build_integrity_check(
        domain_id=spec.domain_id,
        capabilities=capabilities,
        information_domains=spec.information_domains,
        source_catalog=source_catalog,
        dataset_registry=dataset_registry,
    )
    readiness_check = _build_capability_readiness_check(
        domain_id=spec.domain_id,
        domain_name=spec.domain_name,
        capabilities=capabilities,
    )
    checks = (integrity_check, readiness_check)
    status = _aggregate_status(check.status for check in checks)
    summary = _build_domain_summary(
        domain_name=spec.domain_name,
        status=status,
        capabilities=capabilities,
    )
    return DomainReadiness(
        domain_id=spec.domain_id,
        domain_name=spec.domain_name,
        status=status,
        summary=summary,
        checks=checks,
    )


def _build_integrity_check(
    *,
    domain_id: str,
    capabilities: Sequence[SourceCapability],
    information_domains: Sequence[InformationDomain],
    source_catalog: SourceCatalog,
    dataset_registry: DatasetRegistry,
) -> ReadinessCheck:
    capability_ids_missing_contracts = [
        capability.capability_id
        for capability in capabilities
        if capability.requirement == CapabilityRequirement.REQUIRED
        and not capability.dataset_mappings
    ]
    missing_catalog_datasets: list[str] = []
    missing_registry_datasets: list[str] = []
    for capability in capabilities:
        for dataset in capability.dataset_mappings:
            if not source_catalog.sources_for_dataset(dataset) and dataset.value not in missing_catalog_datasets:
                missing_catalog_datasets.append(dataset.value)
            try:
                dataset_registry.get(dataset)
            except KeyError:
                if dataset.value not in missing_registry_datasets:
                    missing_registry_datasets.append(dataset.value)

    unresolved_source_ids = [
        source_id
        for source_id in _unique_strings(
            source_id
            for capability in capabilities
            for source_id in capability.source_family_ids
        )
        if source_id not in {entry.source_id for entry in source_catalog.all_sources()}
    ]
    missing_information_sources = [
        domain.value
        for domain in information_domains
        if not source_catalog.sources_for_information_domain(domain)
    ]
    missing_information_contracts = [
        domain.value
        for domain in information_domains
        if (
            source_catalog.sources_for_information_domain(domain)
            and not source_catalog.stable_datasets_for_information_domain(domain)
        )
    ]

    failures: list[str] = []
    evidence: list[str] = []
    if capability_ids_missing_contracts:
        failures.append(
            "required capabilities without dataset contracts: "
            + ", ".join(sorted(capability_ids_missing_contracts))
        )
    if missing_catalog_datasets:
        failures.append(
            "datasets missing source-catalog coverage: "
            + ", ".join(sorted(missing_catalog_datasets))
        )
    if missing_registry_datasets:
        failures.append(
            "datasets missing registry contracts: "
            + ", ".join(sorted(missing_registry_datasets))
        )
    if unresolved_source_ids:
        failures.append(
            "source families missing from source catalog: "
            + ", ".join(sorted(unresolved_source_ids))
        )
    if missing_information_sources:
        failures.append(
            "information domains without source coverage: "
            + ", ".join(sorted(missing_information_sources))
        )
    if missing_information_contracts:
        failures.append(
            "information domains without stable datasets: "
            + ", ".join(sorted(missing_information_contracts))
        )

    evidence.append(
        "required capabilities checked: "
        f"{sum(1 for item in capabilities if item.requirement == CapabilityRequirement.REQUIRED)}"
    )
    evidence.append(
        "stable information domains checked: "
        + ", ".join(domain.value for domain in information_domains)
    )

    if failures:
        return ReadinessCheck(
            check_id=f"{domain_id}_integrity",
            title="Contract and source mapping integrity",
            status=ReadinessStatus.FAIL,
            summary="Local contract/source truth is inconsistent with readiness requirements.",
            evidence=tuple(evidence + failures),
            follow_ups=tuple(failures),
        )

    return ReadinessCheck(
        check_id=f"{domain_id}_integrity",
        title="Contract and source mapping integrity",
        status=ReadinessStatus.PASS,
        summary="Required contracts, stable information domains, and source mappings are locally linked.",
        evidence=tuple(evidence),
    )


def _build_capability_readiness_check(
    *,
    domain_id: str,
    domain_name: str,
    capabilities: Sequence[SourceCapability],
) -> ReadinessCheck:
    required_capabilities = [
        capability
        for capability in capabilities
        if capability.requirement == CapabilityRequirement.REQUIRED
    ]
    optional_warn_capabilities = [
        capability
        for capability in capabilities
        if capability.requirement == CapabilityRequirement.OPTIONAL
        and capability.status == CapabilityStatus.MISSING
    ]

    pass_ids: list[str] = []
    warn_ids: list[str] = []
    blocked_ids: list[str] = []
    fail_ids: list[str] = []
    follow_ups: list[str] = []

    for capability in required_capabilities:
        status = _readiness_status_for_capability(capability)
        if status == ReadinessStatus.PASS:
            pass_ids.append(capability.capability_id)
        elif status == ReadinessStatus.WARN:
            warn_ids.append(capability.capability_id)
        elif status == ReadinessStatus.BLOCKED:
            blocked_ids.append(capability.capability_id)
        else:
            fail_ids.append(capability.capability_id)
        if status != ReadinessStatus.PASS:
            _append_follow_up(follow_ups, capability.recommended_handoff_theme)

    for capability in optional_warn_capabilities:
        warn_ids.append(capability.capability_id)
        _append_follow_up(follow_ups, capability.recommended_handoff_theme)

    status = _aggregate_status(
        [_readiness_status_for_capability(item) for item in required_capabilities]
        + [ReadinessStatus.WARN for _ in optional_warn_capabilities]
    )
    evidence = [
        f"required covered={len(pass_ids)}",
        f"required warn={len(warn_ids) - len(optional_warn_capabilities)}",
        f"required blocked={len(blocked_ids)}",
        f"required fail={len(fail_ids)}",
    ]
    if warn_ids:
        evidence.append("warn capabilities: " + ", ".join(sorted(warn_ids)))
    if blocked_ids:
        evidence.append("blocked capabilities: " + ", ".join(sorted(blocked_ids)))
    if fail_ids:
        evidence.append("fail capabilities: " + ", ".join(sorted(fail_ids)))

    if status == ReadinessStatus.PASS:
        summary = (
            f"{domain_name} historical DataHub work is locally marked covered for "
            "all required readiness capabilities."
        )
    elif status == ReadinessStatus.BLOCKED:
        summary = (
            f"{domain_name} remains non-final-ready under the personal standard "
            "because at least one required capability is blocked."
        )
    elif status == ReadinessStatus.FAIL:
        summary = (
            f"{domain_name} fails the personal readiness gate because at least one "
            "required capability is missing."
        )
    else:
        summary = (
            f"{domain_name} remains non-final-ready under the personal standard "
            "because required capability limits are still only partial."
        )

    return ReadinessCheck(
        check_id=f"{domain_id}_capability_readiness",
        title="Historical capability readiness",
        status=status,
        summary=summary,
        evidence=tuple(evidence),
        follow_ups=tuple(follow_ups),
    )


def _build_operational_domains(
    *,
    capability_audit: SourceCapabilityAudit,
    operational_evidence: OperationalReadinessEvidence,
) -> tuple[DomainReadiness, ...]:
    source_quality_by_id = {
        capability.capability_id: capability
        for capability in build_default_source_capability_audit().capabilities_by_domain(
            CapabilityDomain.SOURCE_QUALITY,
            required_only=True,
        )
    }
    source_quality_by_id.update(
        {
            capability.capability_id: capability
            for capability in capability_audit.capabilities_by_domain(
                CapabilityDomain.SOURCE_QUALITY,
                required_only=True,
            )
        }
    )

    storage_check = _build_storage_check(operational_evidence)
    storage_domain = DomainReadiness(
        domain_id="local_storage",
        domain_name="Local storage",
        status=storage_check.status,
        summary=_simple_summary("Local storage", storage_check.status),
        checks=(storage_check,),
    )

    refresh_checks = (
        _build_capability_specific_check(
            capability=source_quality_by_id["source_freshness"],
            domain_id="refresh_metadata",
            title="Source freshness metadata",
        ),
        _build_capability_specific_check(
            capability=source_quality_by_id["source_refresh_metadata"],
            domain_id="refresh_metadata",
            title="Refresh metadata and observability",
            extra_evidence=(
                f"offline refresh status={operational_evidence.refresh_status}",
                f"metadata_written={operational_evidence.metadata_written}",
            ),
        ),
    )
    refresh_domain = DomainReadiness(
        domain_id="refresh_metadata",
        domain_name="Refresh metadata",
        status=_aggregate_status(check.status for check in refresh_checks),
        summary=_simple_summary(
            "Refresh metadata",
            _aggregate_status(check.status for check in refresh_checks),
        ),
        checks=refresh_checks,
    )

    quality_checks = (
        _build_capability_specific_check(
            capability=source_quality_by_id["source_schema_validation"],
            domain_id="quality_reports",
            title="Schema validation coverage",
            extra_evidence=(
                "offline quality checks: "
                + ", ".join(operational_evidence.quality_check_names),
            ),
        ),
        _build_capability_specific_check(
            capability=source_quality_by_id["source_coverage_metadata"],
            domain_id="quality_reports",
            title="Coverage metadata richness",
        ),
    )
    quality_domain = DomainReadiness(
        domain_id="quality_reports",
        domain_name="Quality reports",
        status=_aggregate_status(check.status for check in quality_checks),
        summary=_simple_summary(
            "Quality reports",
            _aggregate_status(check.status for check in quality_checks),
        ),
        checks=quality_checks,
    )

    source_health_checks = (
        _build_capability_specific_check(
            capability=source_quality_by_id["source_availability_health"],
            domain_id="source_health_diagnostics",
            title="Source availability health diagnostics",
            extra_evidence=(
                f"offline source_health_status={operational_evidence.source_health_status}",
            ),
        ),
    )
    source_health_domain = DomainReadiness(
        domain_id="source_health_diagnostics",
        domain_name="Source-health diagnostics",
        status=_aggregate_status(check.status for check in source_health_checks),
        summary=_simple_summary(
            "Source-health diagnostics",
            _aggregate_status(check.status for check in source_health_checks),
        ),
        checks=source_health_checks,
    )

    return (
        storage_domain,
        refresh_domain,
        quality_domain,
        source_health_domain,
    )


def _build_storage_check(
    operational_evidence: OperationalReadinessEvidence,
) -> ReadinessCheck:
    if not operational_evidence.success:
        return ReadinessCheck(
            check_id="local_storage_offline_smoke",
            title="Offline storage smoke",
            status=ReadinessStatus.FAIL,
            summary="Deterministic offline storage/refresh smoke failed.",
            evidence=(
                f"error={operational_evidence.error_message}",
                f"raw_written={operational_evidence.raw_written}",
                f"curated_written={operational_evidence.curated_written}",
                f"metadata_written={operational_evidence.metadata_written}",
                f"quality_written={operational_evidence.quality_written}",
            ),
            follow_ups=(
                "repair deterministic offline storage/refresh smoke before treating local DataHub plumbing as ready",
            ),
        )

    return ReadinessCheck(
        check_id="local_storage_offline_smoke",
        title="Offline storage smoke",
        status=ReadinessStatus.PASS,
        summary="Deterministic offline storage, curated persistence, metadata, and quality writes succeeded.",
        evidence=(
            f"dataset={operational_evidence.dataset.value}",
            f"raw_written={operational_evidence.raw_written}",
            f"curated_written={operational_evidence.curated_written}",
            f"metadata_written={operational_evidence.metadata_written}",
            f"quality_written={operational_evidence.quality_written}",
        ),
    )


def _build_capability_specific_check(
    *,
    capability: SourceCapability,
    domain_id: str,
    title: str,
    extra_evidence: tuple[str, ...] = (),
) -> ReadinessCheck:
    status = _readiness_status_for_capability(capability)
    evidence = [
        "dataset mappings: "
        + ", ".join(dataset.value for dataset in capability.dataset_mappings),
        "source families: " + ", ".join(capability.source_family_ids),
    ]
    evidence.extend(extra_evidence)
    follow_ups = ()
    if status != ReadinessStatus.PASS:
        follow_ups = (capability.recommended_handoff_theme,)
    return ReadinessCheck(
        check_id=f"{domain_id}_{capability.capability_id}",
        title=title,
        status=status,
        summary=capability.gap_reason or f"{title} is locally marked covered.",
        evidence=tuple(evidence),
        follow_ups=tuple(item for item in follow_ups if item),
    )


def _run_offline_operational_smoke(
    *,
    dataset_registry: DatasetRegistry,
) -> OperationalReadinessEvidence:
    class _OfflineSmokeAdapter:
        source_name = "offline_personal_readiness_smoke"

        def fetch(
            self,
            dataset: DatasetName,
            *,
            start_date: date | None = None,
            end_date: date | None = None,
            symbols: list[str] | None = None,
        ) -> list[dict[str, object]]:
            _ = dataset, start_date, end_date, symbols
            return [
                {
                    "symbol": "000001.SZ",
                    "market": "a_share",
                    "trade_date": "2024-01-02",
                    "open": 10.0,
                    "high": 10.5,
                    "low": 9.8,
                    "close": 10.2,
                    "volume": 12345.0,
                    "amount": 67890.0,
                    "adj_factor": 1.0,
                    "price_adjustment": "forward",
                    "source": self.source_name,
                    "source_ts": "2024-01-02T15:00:00+00:00",
                    "ingested_at": "2024-01-02T15:01:00+00:00",
                    "schema_version": dataset_registry.get(DatasetName.DAILY_BARS).schema_version,
                }
            ]

    try:
        with TemporaryDirectory(prefix="datahub_personal_readiness_") as tempdir:
            storage = LocalStorage(config=DataHubConfig(root_dir=Path(tempdir)))
            storage.ensure_base_dirs()
            now = datetime(2024, 1, 2, 15, 2, tzinfo=timezone.utc)
            quality_helper = LocalRefreshQualityHelper(
                registry=dataset_registry,
                now_fn=lambda: now,
            )
            result = run_local_warehouse_refresh(
                _OfflineSmokeAdapter(),
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name="offline_personal_readiness_smoke",
                    source_id="offline_personal_readiness_smoke",
                    source_catalog_entry_id="local_offline_smoke",
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 2),
                    symbols=("000001.SZ",),
                ),
                storage,
                registry=dataset_registry,
                quality_helper=quality_helper,
                now_fn=lambda: now,
            )
            quality_records = storage.read_records(DatasetName.DATA_QUALITY_REPORT)
            quality_check_names = tuple(
                record["check_name"]
                for record in quality_records
                if isinstance(record.get("check_name"), str)
            )
            source_health_record = next(
                (
                    record
                    for record in quality_records
                    if record.get("check_name") == SOURCE_AVAILABILITY_HEALTH_CHECK_NAME
                ),
                None,
            )
            return OperationalReadinessEvidence(
                success=result.success
                and result.raw_path.exists()
                and result.curated_path is not None
                and result.curated_path.exists()
                and result.metadata_path is not None
                and result.metadata_path.exists()
                and result.quality_path.exists(),
                dataset=result.dataset,
                raw_written=result.raw_path.exists(),
                curated_written=result.curated_path is not None and result.curated_path.exists(),
                metadata_written=result.metadata_path is not None
                and result.metadata_path.exists(),
                quality_written=result.quality_path.exists(),
                quality_check_names=quality_check_names,
                source_health_status=(
                    str(source_health_record.get("status"))
                    if isinstance(source_health_record, dict)
                    else None
                ),
                refresh_status=result.refresh_status,
            )
    except Exception as error:  # pragma: no cover - failure path exercised by injection tests
        return OperationalReadinessEvidence(
            success=False,
            dataset=DatasetName.DAILY_BARS,
            raw_written=False,
            curated_written=False,
            metadata_written=False,
            quality_written=False,
            quality_check_names=(),
            source_health_status=None,
            refresh_status=None,
            error_message=str(error),
        )


def _capabilities_for_domains(
    capability_audit: SourceCapabilityAudit,
    capability_domains: Sequence[CapabilityDomain],
) -> tuple[SourceCapability, ...]:
    capabilities: list[SourceCapability] = []
    for domain in capability_domains:
        capabilities.extend(
            capability_audit.capabilities_by_domain(domain, required_only=False)
        )
    return tuple(capabilities)


def _readiness_status_for_capability(capability: SourceCapability) -> ReadinessStatus:
    if capability.status == CapabilityStatus.COVERED:
        return ReadinessStatus.PASS
    if capability.status == CapabilityStatus.PARTIAL:
        return ReadinessStatus.WARN
    if capability.status == CapabilityStatus.PLANNED:
        return ReadinessStatus.BLOCKED
    if capability.status == CapabilityStatus.MISSING:
        if capability.requirement == CapabilityRequirement.REQUIRED:
            return ReadinessStatus.FAIL
        return ReadinessStatus.WARN
    raise ValueError(f"Unsupported capability status: {capability.status!r}")


def _build_domain_summary(
    *,
    domain_name: str,
    status: ReadinessStatus,
    capabilities: Sequence[SourceCapability],
) -> str:
    required_total = sum(
        1 for capability in capabilities if capability.requirement == CapabilityRequirement.REQUIRED
    )
    if status == ReadinessStatus.PASS:
        return f"{domain_name} passes all local required readiness checks ({required_total} required capabilities)."
    if status == ReadinessStatus.BLOCKED:
        return f"{domain_name} is not closure-ready because at least one required capability remains blocked."
    if status == ReadinessStatus.FAIL:
        return f"{domain_name} fails local readiness integrity or required capability coverage."
    return f"{domain_name} remains warning-grade only and cannot be treated as final under the personal standard."


def _simple_summary(domain_name: str, status: ReadinessStatus) -> str:
    if status == ReadinessStatus.PASS:
        return f"{domain_name} passes deterministic offline readiness checks."
    if status == ReadinessStatus.BLOCKED:
        return f"{domain_name} remains blocked under deterministic offline readiness checks."
    if status == ReadinessStatus.FAIL:
        return f"{domain_name} fails deterministic offline readiness checks."
    return f"{domain_name} is only warning-grade under deterministic offline readiness checks."


def _aggregate_status(statuses: Iterable[ReadinessStatus]) -> ReadinessStatus:
    items = tuple(statuses)
    if not items:
        return ReadinessStatus.PASS
    return max(items, key=lambda item: _STATUS_PRIORITY[item])


def _append_follow_up(target: list[str], text: str) -> None:
    if text and text not in target:
        target.append(text)


def _unique_strings(items: Iterable[str]) -> tuple[str, ...]:
    seen: list[str] = []
    for item in items:
        if item not in seen:
            seen.append(item)
    return tuple(seen)


__all__ = [
    "DomainReadiness",
    "OperationalReadinessEvidence",
    "PersonalTradingReadinessReport",
    "ReadinessCheck",
    "ReadinessStatus",
    "build_default_personal_trading_readiness_report",
    "build_personal_trading_readiness_report",
]
