"""Deterministic synthetic fixtures for offline DataHub contract tests."""

from __future__ import annotations

from quant.datahub.datasets import DatasetName


OFFLINE_FIXTURE_RECORDS: dict[DatasetName, list[dict[str, object]]] = {
    DatasetName.INSTRUMENT_MASTER: [
        {
            "symbol": "600000.SH",
            "raw_symbol": "600000",
            "name": "SYNTH_BANK",
            "market": "CN",
            "asset_type": "stock",
            "currency": "CNY",
            "exchange": "SSE",
            "list_date": "1999-11-10",
            "delist_date": "9999-12-31",
            "is_active": True,
            "source": "fixture",
            "ingested_at": "2024-01-02T10:00:00",
            "schema_version": "v1",
        }
    ],
    DatasetName.TRADING_CALENDAR: [
        {
            "market": "CN",
            "trade_date": "2024-01-02",
            "is_open": True,
            "session_type": "full",
            "previous_trade_date": "2024-01-01",
            "next_trade_date": "2024-01-03",
            "source": "fixture",
            "ingested_at": "2024-01-02T10:00:00",
            "schema_version": "v1",
        }
    ],
    DatasetName.DAILY_BARS: [
        {
            "symbol": "600000.SH",
            "market": "CN",
            "trade_date": "2024-01-02",
            "open": 10.0,
            "high": 10.2,
            "low": 9.8,
            "close": 10.1,
            "volume": 1000,
            "amount": 10000,
            "adj_factor": 1.0,
            "price_adjustment": "raw",
            "source": "fixture",
            "ingested_at": "2024-01-02T10:00:00",
            "schema_version": "v1",
        }
    ],
    DatasetName.DATA_QUALITY_REPORT: [
        {
            "dataset": "daily_bars",
            "market": "CN",
            "trade_date": "2024-01-02",
            "check_name": "completeness",
            "status": "pass",
            "severity": "low",
            "details": "synthetic fixture",
            "created_at": "2024-01-02T10:00:00",
            "source": "fixture",
            "ingested_at": "2024-01-02T10:00:01",
            "schema_version": "v1",
        }
    ],
}


INVALID_REQUIRED_FIXTURE_RECORDS: dict[DatasetName, dict[str, object]] = {
    DatasetName.INSTRUMENT_MASTER: {
        "raw_symbol": "600000",
        "name": "SYNTH_BANK",
        "market": "CN",
        "asset_type": "stock",
        "currency": "CNY",
        "exchange": "SSE",
        "list_date": "1999-11-10",
        "delist_date": "9999-12-31",
        "is_active": True,
        "source": "fixture",
        "ingested_at": "2024-01-02T10:00:00",
        "schema_version": "v1",
    },
    DatasetName.TRADING_CALENDAR: {
        "market": "CN",
        "trade_date": "2024-01-02",
        "session_type": "full",
        "previous_trade_date": "2024-01-01",
        "next_trade_date": "2024-01-03",
        "source": "fixture",
        "ingested_at": "2024-01-02T10:00:00",
        "schema_version": "v1",
    },
    DatasetName.DAILY_BARS: {
        "symbol": "600000.SH",
        "market": "CN",
        "trade_date": "2024-01-02",
        "open": 10.0,
        "high": 10.2,
        "low": 9.8,
        "volume": 1000,
        "amount": 10000,
        "adj_factor": 1.0,
        "price_adjustment": "raw",
        "source": "fixture",
        "ingested_at": "2024-01-02T10:00:00",
        "schema_version": "v1",
    },
    DatasetName.DATA_QUALITY_REPORT: {
        "dataset": "daily_bars",
        "market": "CN",
        "trade_date": "2024-01-02",
        "check_name": "completeness",
        "status": "pass",
        "details": "synthetic fixture",
        "created_at": "2024-01-02T10:00:00",
        "source": "fixture",
        "ingested_at": "2024-01-02T10:00:01",
        "schema_version": "v1",
    },
}


INVALID_TYPED_FIXTURE_RECORDS: dict[DatasetName, dict[str, object]] = {
    DatasetName.INSTRUMENT_MASTER: {
        **OFFLINE_FIXTURE_RECORDS[DatasetName.INSTRUMENT_MASTER][0],
        "is_active": "yes",
    },
    DatasetName.TRADING_CALENDAR: {
        **OFFLINE_FIXTURE_RECORDS[DatasetName.TRADING_CALENDAR][0],
        "trade_date": 20240102,
    },
    DatasetName.DAILY_BARS: {
        **OFFLINE_FIXTURE_RECORDS[DatasetName.DAILY_BARS][0],
        "open": "10.0",
    },
    DatasetName.DATA_QUALITY_REPORT: {
        **OFFLINE_FIXTURE_RECORDS[DatasetName.DATA_QUALITY_REPORT][0],
        "created_at": 1704160800,
    },
}
