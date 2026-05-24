from datetime import date, datetime
import unittest
from unittest.mock import patch

from quant.datahub.datasets import DatasetName, DatasetRegistry
from quant.datahub.source import (
    SourceAdapter,
    SourceAdapterContractError,
    SourcePayloadNormalizationError,
    SourceRequest,
    SourceResult,
    fetch_source_result,
    normalize_source_payload,
)


class DummyListPayloadSource:
    source_name = "fixture_list_payload"

    def fetch(self, dataset, *, start_date=None, end_date=None, symbols=None):
        if dataset != DatasetName.DAILY_BARS:
            raise ValueError("Unsupported dataset for fixture source")
        return [
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": "2024-01-02",
                "open": 10.0,
                "high": 10.2,
                "low": 9.8,
                "close": 10.1,
                "volume": 1000.0,
                "amount": 10000.0,
                "adj_factor": 1.0,
                "price_adjustment": "raw",
                "source": "fixture",
                "ingested_at": "2024-01-02T10:00:00",
                "schema_version": "v1",
            }
        ]


class DummyCanonicalResultSource:
    source_name = "fixture_canonical_payload"

    def fetch(self, dataset, *, start_date=None, end_date=None, symbols=None):
        request = SourceRequest(
            dataset=dataset,
            source_name=self.source_name,
            start_date=start_date,
            end_date=end_date,
            symbols=tuple(symbols) if symbols else None,
        )
        return SourceResult(
            request=request,
            source_name=self.source_name,
            normalized_records=(
                {
                    "indicator_id": "CPI_CN_YOY",
                    "region": "CN",
                    "observation_date": "2024-01-01",
                    "value": 0.2,
                    "release_date": "2024-01-10",
                    "source": "fixture",
                    "ingested_at": "2024-01-10T10:00:00",
                    "schema_version": "v1",
                },
            ),
            record_count=1,
            produced_at=datetime(2024, 1, 10, 9, 0, 0),
            fetched_at=datetime(2024, 1, 10, 9, 5, 0),
        )


class MissingFetchSource:
    source_name = "missing_fetch"


class UnsupportedPayloadSource:
    source_name = "unsupported_payload"

    def fetch(self, dataset, *, start_date=None, end_date=None, symbols=None):
        return {"records": []}


class NonMappingRecordSource:
    source_name = "non_mapping_record"

    def fetch(self, dataset, *, start_date=None, end_date=None, symbols=None):
        return [{"ok": True}, "not_a_mapping"]


class InvalidSchemaRecordSource:
    source_name = "invalid_schema_record"

    def fetch(self, dataset, *, start_date=None, end_date=None, symbols=None):
        return [
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": "2024-01-02",
                "open": 10.0,
                "high": 10.2,
                "low": 9.8,
                "volume": 1000.0,
                "amount": 10000.0,
                "adj_factor": 1.0,
                "price_adjustment": "raw",
                "source": "fixture",
                "ingested_at": "2024-01-02T10:00:00",
                "schema_version": "v1",
            }
        ]


class InvalidSemanticRecordSource:
    source_name = "invalid_semantic_record"

    def fetch(self, dataset, *, start_date=None, end_date=None, symbols=None):
        return [
            {
                "symbol": "600000.SH",
                "market": "CN",
                "trade_date": "2024-01-02",
                "open": 10.0,
                "high": 9.7,
                "low": 9.8,
                "close": 10.1,
                "volume": 1000.0,
                "amount": 10000.0,
                "adj_factor": 1.0,
                "price_adjustment": "raw",
                "source": "fixture",
                "ingested_at": "2024-01-02T10:00:00",
                "schema_version": "v1",
            }
        ]


class MismatchedStartDateCanonicalSource:
    source_name = "mismatched_start_date"

    def fetch(self, dataset, *, start_date=None, end_date=None, symbols=None):
        mismatched_start_date = date(2024, 1, 1) if start_date != date(2024, 1, 1) else date(2024, 1, 2)
        return SourceResult(
            request=SourceRequest(
                dataset=dataset,
                source_name=self.source_name,
                start_date=mismatched_start_date,
                end_date=end_date,
                symbols=tuple(symbols) if symbols else None,
            ),
            source_name=self.source_name,
            normalized_records=(
                {
                    "symbol": "600000.SH",
                    "market": "CN",
                    "trade_date": "2024-01-02",
                    "open": 10.0,
                    "high": 10.2,
                    "low": 9.8,
                    "close": 10.1,
                    "volume": 1000.0,
                    "amount": 10000.0,
                    "adj_factor": 1.0,
                    "price_adjustment": "raw",
                    "source": "fixture",
                    "ingested_at": "2024-01-02T10:00:00",
                    "schema_version": "v1",
                },
            ),
            record_count=1,
            produced_at=datetime(2024, 1, 2, 9, 0, 0),
            fetched_at=datetime(2024, 1, 2, 9, 5, 0),
        )


class MismatchedEndDateCanonicalSource:
    source_name = "mismatched_end_date"

    def fetch(self, dataset, *, start_date=None, end_date=None, symbols=None):
        mismatched_end_date = date(2024, 1, 3) if end_date != date(2024, 1, 3) else date(2024, 1, 4)
        return SourceResult(
            request=SourceRequest(
                dataset=dataset,
                source_name=self.source_name,
                start_date=start_date,
                end_date=mismatched_end_date,
                symbols=tuple(symbols) if symbols else None,
            ),
            source_name=self.source_name,
            normalized_records=(
                {
                    "symbol": "600000.SH",
                    "market": "CN",
                    "trade_date": "2024-01-02",
                    "open": 10.0,
                    "high": 10.2,
                    "low": 9.8,
                    "close": 10.1,
                    "volume": 1000.0,
                    "amount": 10000.0,
                    "adj_factor": 1.0,
                    "price_adjustment": "raw",
                    "source": "fixture",
                    "ingested_at": "2024-01-02T10:00:00",
                    "schema_version": "v1",
                },
            ),
            record_count=1,
            produced_at=datetime(2024, 1, 2, 9, 0, 0),
            fetched_at=datetime(2024, 1, 2, 9, 5, 0),
        )


class MismatchedSymbolsCanonicalSource:
    source_name = "mismatched_symbols"

    def fetch(self, dataset, *, start_date=None, end_date=None, symbols=None):
        return SourceResult(
            request=SourceRequest(
                dataset=dataset,
                source_name=self.source_name,
                start_date=start_date,
                end_date=end_date,
                symbols=("000001.SZ",),
            ),
            source_name=self.source_name,
            normalized_records=(
                {
                    "symbol": "600000.SH",
                    "market": "CN",
                    "trade_date": "2024-01-02",
                    "open": 10.0,
                    "high": 10.2,
                    "low": 9.8,
                    "close": 10.1,
                    "volume": 1000.0,
                    "amount": 10000.0,
                    "adj_factor": 1.0,
                    "price_adjustment": "raw",
                    "source": "fixture",
                    "ingested_at": "2024-01-02T10:00:00",
                    "schema_version": "v1",
                },
            ),
            record_count=1,
            produced_at=datetime(2024, 1, 2, 9, 0, 0),
            fetched_at=datetime(2024, 1, 2, 9, 5, 0),
        )


def _use_source(source: SourceAdapter) -> dict:
    return fetch_source_result(
        source,
        SourceRequest(
            dataset=DatasetName.DAILY_BARS,
            source_name=getattr(source, "source_name", None),
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 2),
            symbols=("000001.SZ",),
        ),
        fetched_at=datetime(2024, 1, 2, 10, 0, 0),
    ).normalized_records[0]


class SourceRequestTests(unittest.TestCase):
    def test_request_rejects_inverted_date_range(self) -> None:
        with self.assertRaisesRegex(ValueError, "Invalid SourceRequest date range"):
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                start_date=date(2024, 1, 3),
                end_date=date(2024, 1, 2),
            )

    def test_request_fetch_symbols_returns_list_copy(self) -> None:
        request = SourceRequest(
            dataset=DatasetName.DAILY_BARS,
            symbols=("000001.SZ", "600000.SH"),
        )

        self.assertEqual(request.fetch_symbols(), ["000001.SZ", "600000.SH"])

    def test_request_rejects_bare_string_symbols(self) -> None:
        with self.assertRaisesRegex(ValueError, "not bare str/bytes"):
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                symbols="000001.SZ",
            )

    def test_request_rejects_bare_bytes_symbols(self) -> None:
        with self.assertRaisesRegex(ValueError, "not bare str/bytes"):
            SourceRequest(
                dataset=DatasetName.DAILY_BARS,
                symbols=b"000001.SZ",
            )


class SourcePayloadNormalizationTests(unittest.TestCase):
    def test_normalize_accepts_list_of_mappings(self) -> None:
        normalized = normalize_source_payload([{"a": 1}, {"b": 2}])
        self.assertEqual(normalized, [{"a": 1}, {"b": 2}])

    def test_normalize_accepts_canonical_source_result(self) -> None:
        payload = SourceResult(
            request=SourceRequest(dataset=DatasetName.DAILY_BARS),
            source_name="fixture",
            normalized_records=({"symbol": "600000.SH"},),
            record_count=1,
            produced_at=datetime(2024, 1, 2, 9, 30, 0),
            fetched_at=datetime(2024, 1, 2, 10, 0, 0),
        )

        normalized = normalize_source_payload(payload)

        self.assertEqual(normalized, [{"symbol": "600000.SH"}])

    def test_normalize_rejects_unsupported_payload_shape(self) -> None:
        with self.assertRaisesRegex(SourcePayloadNormalizationError, "Unsupported source payload shape"):
            normalize_source_payload({"records": []})

    def test_normalize_rejects_non_mapping_record(self) -> None:
        with self.assertRaisesRegex(SourcePayloadNormalizationError, "not a mapping"):
            normalize_source_payload([{"ok": True}, "bad"])


class SourceAdapterTests(unittest.TestCase):
    def test_source_protocol_contract_is_usable(self) -> None:
        payload = _use_source(DummyListPayloadSource())

        self.assertEqual(payload["symbol"], "600000.SH")
        self.assertEqual(payload["source"], "fixture")

    def test_source_protocol_runtime_checkable(self) -> None:
        self.assertIsInstance(DummyListPayloadSource(), SourceAdapter)
        self.assertNotIsInstance(MissingFetchSource(), SourceAdapter)

    def test_fetch_source_result_with_legacy_daily_bars_fixture(self) -> None:
        request = SourceRequest(
            dataset=DatasetName.DAILY_BARS,
            source_name="fixture_list_payload",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 2),
            symbols=("600000.SH",),
            source_catalog_entry_id="fixture_daily_bars",
        )
        registry = DatasetRegistry()

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                DummyListPayloadSource(),
                request,
                fetched_at=datetime(2024, 1, 2, 10, 0, 0),
            )

        self.assertEqual(result.request.dataset, DatasetName.DAILY_BARS)
        self.assertEqual(result.request.source_catalog_entry_id, "fixture_daily_bars")
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.request.symbols, ("600000.SH",))
        self.assertEqual(result.normalized_records[0]["symbol"], "600000.SH")
        self.assertEqual(registry.validate_record(DatasetName.DAILY_BARS, result.normalized_records[0]), ())

    def test_fetch_source_result_with_expanded_macro_fixture(self) -> None:
        request = SourceRequest(
            dataset=DatasetName.MACRO_OBSERVATIONS,
            source_name="fixture_canonical_payload",
            source_id="fixture_macro",
            source_catalog_entry_id="fixture_macro_observations",
        )
        registry = DatasetRegistry()

        with patch(
            "socket.create_connection",
            side_effect=AssertionError("Network access should not be used"),
        ):
            result = fetch_source_result(
                DummyCanonicalResultSource(),
                request,
                fetched_at=datetime(2024, 1, 10, 10, 0, 0),
            )

        self.assertEqual(result.request.dataset, DatasetName.MACRO_OBSERVATIONS)
        self.assertEqual(result.request.source_id, "fixture_macro")
        self.assertEqual(result.source_name, "fixture_canonical_payload")
        self.assertEqual(result.record_count, 1)
        self.assertIsNotNone(result.produced_at)
        self.assertEqual(
            registry.validate_record(
                DatasetName.MACRO_OBSERVATIONS,
                result.normalized_records[0],
            ),
            (),
        )

    def test_fetch_source_result_rejects_non_protocol_adapter(self) -> None:
        with self.assertRaisesRegex(SourceAdapterContractError, "does not satisfy SourceAdapter protocol"):
            fetch_source_result(
                MissingFetchSource(),  # type: ignore[arg-type]
                SourceRequest(dataset=DatasetName.DAILY_BARS),
            )

    def test_fetch_source_result_rejects_unsupported_payload_shape(self) -> None:
        with self.assertRaisesRegex(SourcePayloadNormalizationError, "Unsupported source payload shape"):
            fetch_source_result(
                UnsupportedPayloadSource(),
                SourceRequest(dataset=DatasetName.DAILY_BARS),
            )

    def test_fetch_source_result_rejects_non_mapping_payload_record(self) -> None:
        with self.assertRaisesRegex(SourcePayloadNormalizationError, "not a mapping"):
            fetch_source_result(
                NonMappingRecordSource(),
                SourceRequest(dataset=DatasetName.DAILY_BARS),
            )

    def test_schema_invalid_record_surfaces_through_contract_validation(self) -> None:
        registry = DatasetRegistry()
        result = fetch_source_result(
            InvalidSchemaRecordSource(),
            SourceRequest(dataset=DatasetName.DAILY_BARS),
            fetched_at=datetime(2024, 1, 2, 10, 0, 0),
        )
        issues = registry.validate_record(DatasetName.DAILY_BARS, result.normalized_records[0])

        self.assertTrue(any(issue.code == "missing_required_field" for issue in issues))

    def test_semantic_invalid_record_surfaces_through_contract_validation(self) -> None:
        registry = DatasetRegistry()
        result = fetch_source_result(
            InvalidSemanticRecordSource(),
            SourceRequest(dataset=DatasetName.DAILY_BARS),
            fetched_at=datetime(2024, 1, 2, 10, 0, 0),
        )
        issues = registry.validate_record(DatasetName.DAILY_BARS, result.normalized_records[0])

        self.assertTrue(any(issue.code == "invalid_price_range" for issue in issues))

    def test_canonical_source_result_rejects_start_date_mismatch(self) -> None:
        with self.assertRaisesRegex(SourceAdapterContractError, "start_date does not match"):
            fetch_source_result(
                MismatchedStartDateCanonicalSource(),
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name="mismatched_start_date",
                    start_date=date(2024, 1, 3),
                    end_date=date(2024, 1, 4),
                    symbols=("600000.SH",),
                ),
            )

    def test_canonical_source_result_rejects_end_date_mismatch(self) -> None:
        with self.assertRaisesRegex(SourceAdapterContractError, "end_date does not match"):
            fetch_source_result(
                MismatchedEndDateCanonicalSource(),
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name="mismatched_end_date",
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 2),
                    symbols=("600000.SH",),
                ),
            )

    def test_canonical_source_result_rejects_symbols_mismatch(self) -> None:
        with self.assertRaisesRegex(SourceAdapterContractError, "symbols do not match"):
            fetch_source_result(
                MismatchedSymbolsCanonicalSource(),
                SourceRequest(
                    dataset=DatasetName.DAILY_BARS,
                    source_name="mismatched_symbols",
                    start_date=date(2024, 1, 2),
                    end_date=date(2024, 1, 2),
                    symbols=("600000.SH",),
                ),
            )
