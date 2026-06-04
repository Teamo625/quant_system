"""FeatureHub foundation contracts for offline-safe feature primitives."""

from .contracts import (
    APPROVED_SOURCE_DATASETS,
    FEATURE_VALUE_SCHEMA,
    FEATURE_VALUE_SCHEMA_VERSION,
    FeatureContractIssue,
    FeatureName,
    FeatureSchemaMetadata,
    FeatureValueRecord,
    validate_feature_value_record,
)

__all__ = [
    "APPROVED_SOURCE_DATASETS",
    "FEATURE_VALUE_SCHEMA",
    "FEATURE_VALUE_SCHEMA_VERSION",
    "FeatureContractIssue",
    "FeatureName",
    "FeatureSchemaMetadata",
    "FeatureValueRecord",
    "validate_feature_value_record",
]
