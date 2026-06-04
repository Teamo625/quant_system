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
from .technical import (
    DailyBarInput,
    build_close_to_close_return_feature,
    build_realized_volatility_feature,
    build_simple_moving_average_feature,
    calculate_close_to_close_return,
    calculate_realized_volatility,
    calculate_simple_moving_average,
    normalize_daily_bars,
)

__all__ = [
    "APPROVED_SOURCE_DATASETS",
    "DailyBarInput",
    "FEATURE_VALUE_SCHEMA",
    "FEATURE_VALUE_SCHEMA_VERSION",
    "FeatureContractIssue",
    "FeatureName",
    "FeatureSchemaMetadata",
    "FeatureValueRecord",
    "build_close_to_close_return_feature",
    "build_realized_volatility_feature",
    "build_simple_moving_average_feature",
    "calculate_close_to_close_return",
    "calculate_realized_volatility",
    "calculate_simple_moving_average",
    "normalize_daily_bars",
    "validate_feature_value_record",
]
