"""AKShare-backed DataHub source adapters."""

from __future__ import annotations

import hashlib
import inspect
import json
import math
import re
import socket
import ssl
from datetime import date, datetime, timezone
from typing import Any, Callable, Mapping, Sequence

from ..datasets import DatasetName, DatasetRegistry

AKSHARE_SOURCE_ID = "akshare_cn_hk_public_family"
AKSHARE_SOURCE_NAME = "AKShare CN/HK Public Family"
MACRO_POLICY_SOURCE_ID = "macro_policy_public_sources"
MACRO_POLICY_SOURCE_NAME = "Macro and Policy Public Sources"

_SUPPORTED_ADJUSTMENTS: dict[str, str] = {
    "raw": "",
    "qfq": "qfq",
    "hfq": "hfq",
}

_CN_INDEX_AKSHARE_SYMBOL_MAP: dict[str, str] = {
    "000300": "sh000300",
    "000001": "sh000001",
    "399001": "sz399001",
    "399006": "sz399006",
}

_CN_INDEX_NAME_MAP: dict[str, str] = {
    "000300": "CSI 300",
    "000001": "SSE Composite",
    "399001": "SZSE Component",
    "399006": "ChiNext Index",
}

_MACRO_INDICATOR_SPECS: tuple[dict[str, str], ...] = (
    {
        "indicator_id": "CPI_CN_YOY",
        "indicator_name": "China CPI YoY",
        "frequency": "monthly",
        "unit": "percent",
        "category": "inflation",
        "route_name": "macro_china_cpi_yearly",
    },
    {
        "indicator_id": "PPI_CN_YOY",
        "indicator_name": "China PPI YoY",
        "frequency": "monthly",
        "unit": "percent",
        "category": "inflation",
        "route_name": "macro_china_ppi_yearly",
    },
    {
        "indicator_id": "GDP_CN_YOY",
        "indicator_name": "China GDP YoY",
        "frequency": "quarterly",
        "unit": "percent",
        "category": "growth",
        "route_name": "macro_china_gdp_yearly",
    },
)


class AkshareAShareDailyBarAdapter:
    """Narrow AKShare adapter for A-share daily bars only."""

    source_name = AKSHARE_SOURCE_ID
    source_display_name = AKSHARE_SOURCE_NAME

    def __init__(
        self,
        *,
        fetch_daily_hist: Callable[..., Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
        price_adjustment: str = "raw",
    ) -> None:
        if price_adjustment not in _SUPPORTED_ADJUSTMENTS:
            supported = ", ".join(sorted(_SUPPORTED_ADJUSTMENTS))
            raise ValueError(
                f"Unsupported price_adjustment={price_adjustment!r}. Supported: {supported}"
            )

        self._fetch_daily_hist = fetch_daily_hist
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._price_adjustment = price_adjustment
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if dataset != DatasetName.DAILY_BARS:
            raise ValueError(
                f"Unsupported dataset for AkshareAShareDailyBarAdapter: {dataset.value}"
            )

        symbol = self._require_single_symbol(symbols)
        akshare_symbol = self._to_akshare_symbol(symbol)
        fetch_fn = self._resolve_fetch_daily_hist()
        raw_payload = fetch_fn(
            symbol=akshare_symbol,
            period="daily",
            start_date=self._to_akshare_date(start_date),
            end_date=self._to_akshare_date(end_date),
            adjust=_SUPPORTED_ADJUSTMENTS[self._price_adjustment],
        )
        rows = self._payload_to_rows(raw_payload)
        return self._normalize_daily_bar_rows(rows=rows, symbol=symbol, dataset=dataset)

    def _resolve_fetch_daily_hist(self) -> Callable[..., Any]:
        if self._fetch_daily_hist is not None:
            return self._fetch_daily_hist

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare adapter fetch."
            ) from exc

        return ak.stock_zh_a_hist

    def _require_single_symbol(self, symbols: list[str] | None) -> str:
        if symbols is None or len(symbols) == 0:
            raise ValueError(
                "AkshareAShareDailyBarAdapter requires exactly one symbol, got none."
            )
        if len(symbols) != 1:
            raise ValueError(
                "AkshareAShareDailyBarAdapter currently supports exactly one symbol."
            )
        symbol = symbols[0]
        if not isinstance(symbol, str) or symbol.strip() == "":
            raise ValueError("Symbol must be a non-empty string.")
        return symbol.strip().upper()

    def _to_akshare_symbol(self, symbol: str) -> str:
        if "." not in symbol:
            if symbol.isdigit() and len(symbol) == 6:
                return symbol
            raise ValueError(
                f"Unsupported symbol format: {symbol!r}. Expected like '600000.SH'."
            )

        code, market = symbol.split(".", 1)
        market = market.upper()
        if not code.isdigit() or len(code) != 6:
            raise ValueError(
                f"Unsupported symbol code format: {symbol!r}. Expected 6-digit code."
            )
        if market not in {"SH", "SZ", "BJ"}:
            raise ValueError(
                f"Unsupported market suffix for A-share adapter: {market!r}."
            )
        return code

    def _to_akshare_date(self, value: date | None) -> str:
        if value is None:
            return ""
        return value.strftime("%Y%m%d")

    def _payload_to_rows(self, payload: Any) -> list[Mapping[str, Any]]:
        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "AKShare payload must be DataFrame-like or list[Mapping], "
                f"got {type(payload).__name__}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "AKShare payload row must be mapping. "
                    f"idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _normalize_daily_bar_rows(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        symbol: str,
        dataset: DatasetName,
    ) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version

        for idx, row in enumerate(rows):
            trade_date = self._normalize_trade_date(self._pick(row, idx, "date", "日期", "trade_date"))
            normalized.append(
                {
                    "symbol": symbol,
                    "market": "CN",
                    "trade_date": trade_date,
                    "open": self._to_float(self._pick(row, idx, "open", "开盘")),
                    "high": self._to_float(self._pick(row, idx, "high", "最高")),
                    "low": self._to_float(self._pick(row, idx, "low", "最低")),
                    "close": self._to_float(self._pick(row, idx, "close", "收盘")),
                    "volume": self._to_float(self._pick(row, idx, "volume", "成交量")),
                    "amount": self._to_float(self._pick(row, idx, "amount", "成交额")),
                    "adj_factor": 1.0,
                    "price_adjustment": self._price_adjustment,
                    "source": AKSHARE_SOURCE_ID,
                    "ingested_at": ingested_at,
                    "schema_version": schema_version,
                }
            )
        return normalized

    def _pick(
        self,
        row: Mapping[str, Any],
        row_idx: int,
        *keys: str,
    ) -> Any:
        for key in keys:
            if key in row:
                return row[key]
        raise ValueError(
            f"Missing required source field in row {row_idx}: one of {keys!r}"
        )

    def _to_float(self, value: Any) -> float:
        if isinstance(value, bool):
            raise ValueError(f"Invalid numeric value type: {value!r}")
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            normalized = value.strip().replace(",", "")
            if normalized == "":
                raise ValueError("Invalid numeric value: empty string")
            try:
                return float(normalized)
            except ValueError as exc:
                raise ValueError(f"Invalid numeric value: {value!r}") from exc
        raise ValueError(f"Invalid numeric value type: {type(value).__name__}")

    def _normalize_trade_date(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if len(stripped) == 8 and stripped.isdigit():
                return date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                ).isoformat()
            try:
                return date.fromisoformat(stripped).isoformat()
            except ValueError as exc:
                raise ValueError(f"Invalid trade date value: {value!r}") from exc
        raise ValueError(f"Invalid trade date value type: {type(value).__name__}")


class AkshareAShareInstrumentMasterAdapter:
    """Narrow AKShare adapter for active A-share instrument master only."""

    source_name = AKSHARE_SOURCE_ID
    source_display_name = AKSHARE_SOURCE_NAME

    _ROUTE_SPECS: tuple[dict[str, Any], ...] = (
        {
            "route_id": "sse_main",
            "route_name": "stock_info_sh_name_code(主板A股)",
            "suffix": "SH",
            "exchange": "SSE",
            "allowed_prefixes": ("6",),
        },
        {
            "route_id": "sse_kcb",
            "route_name": "stock_info_sh_name_code(科创板)",
            "suffix": "SH",
            "exchange": "SSE",
            "allowed_prefixes": ("6",),
        },
        {
            "route_id": "szse_a",
            "route_name": "stock_info_sz_name_code(A股列表)",
            "suffix": "SZ",
            "exchange": "SZSE",
            "allowed_prefixes": ("0", "3"),
        },
        {
            "route_id": "bse_a",
            "route_name": "stock_info_bj_name_code()",
            "suffix": "BJ",
            "exchange": "BSE",
            "allowed_prefixes": ("4", "8", "9"),
        },
    )

    def __init__(
        self,
        *,
        fetch_sh_main: Callable[..., Any] | None = None,
        fetch_sh_kcb: Callable[..., Any] | None = None,
        fetch_sz_a: Callable[..., Any] | None = None,
        fetch_bj_a: Callable[..., Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self._fetch_sh_main = fetch_sh_main
        self._fetch_sh_kcb = fetch_sh_kcb
        self._fetch_sz_a = fetch_sz_a
        self._fetch_bj_a = fetch_bj_a
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        del start_date, end_date
        if dataset != DatasetName.INSTRUMENT_MASTER:
            raise ValueError(
                "Unsupported dataset for AkshareAShareInstrumentMasterAdapter: "
                f"{dataset.value}"
            )

        rows_by_route = self._fetch_rows_by_route()
        records = self._normalize_instrument_rows(
            rows_by_route=rows_by_route,
            dataset=dataset,
        )
        return self._filter_by_symbols(records=records, symbols=symbols)

    def _fetch_rows_by_route(self) -> list[tuple[dict[str, Any], list[Mapping[str, Any]]]]:
        rows_by_route: list[tuple[dict[str, Any], list[Mapping[str, Any]]]] = []
        for route_spec in self._ROUTE_SPECS:
            fetch_fn = self._resolve_route_fetch(route_id=route_spec["route_id"])
            route_name = str(route_spec["route_name"])
            try:
                payload = fetch_fn()
            except Exception as exc:
                if self._is_instrument_master_network_unavailable(exc):
                    raise RuntimeError(
                        "AKShare A-share instrument-master route unavailable: "
                        f"{route_name} -> {type(exc).__name__}: {exc}"
                    ) from exc
                raise
            rows = self._payload_to_rows(payload=payload, route_name=route_name)
            rows_by_route.append((route_spec, rows))
        return rows_by_route

    def _resolve_route_fetch(self, *, route_id: str) -> Callable[..., Any]:
        if route_id == "sse_main" and self._fetch_sh_main is not None:
            return self._fetch_sh_main
        if route_id == "sse_kcb" and self._fetch_sh_kcb is not None:
            return self._fetch_sh_kcb
        if route_id == "szse_a" and self._fetch_sz_a is not None:
            return self._fetch_sz_a
        if route_id == "bse_a" and self._fetch_bj_a is not None:
            return self._fetch_bj_a

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare A-share instrument-master fetch."
            ) from exc

        if route_id == "sse_main":
            if not hasattr(ak, "stock_info_sh_name_code"):
                raise RuntimeError(
                    "AKShare A-share instrument-master function is unavailable: "
                    "stock_info_sh_name_code"
                )
            return lambda: ak.stock_info_sh_name_code(symbol="主板A股")

        if route_id == "sse_kcb":
            if not hasattr(ak, "stock_info_sh_name_code"):
                raise RuntimeError(
                    "AKShare A-share instrument-master function is unavailable: "
                    "stock_info_sh_name_code"
                )
            return lambda: ak.stock_info_sh_name_code(symbol="科创板")

        if route_id == "szse_a":
            if not hasattr(ak, "stock_info_sz_name_code"):
                raise RuntimeError(
                    "AKShare A-share instrument-master function is unavailable: "
                    "stock_info_sz_name_code"
                )
            return lambda: ak.stock_info_sz_name_code(symbol="A股列表")

        if route_id == "bse_a":
            if not hasattr(ak, "stock_info_bj_name_code"):
                raise RuntimeError(
                    "AKShare A-share instrument-master function is unavailable: "
                    "stock_info_bj_name_code"
                )
            return ak.stock_info_bj_name_code

        raise RuntimeError(f"Unsupported instrument-master route_id: {route_id!r}")

    def _payload_to_rows(self, *, payload: Any, route_name: str) -> list[Mapping[str, Any]]:
        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "AKShare A-share instrument-master payload must be DataFrame-like "
                f"or list[Mapping], got {type(payload).__name__}, route={route_name}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "AKShare A-share instrument-master payload row must be mapping. "
                    f"route={route_name}, idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _normalize_instrument_rows(
        self,
        *,
        rows_by_route: Sequence[tuple[dict[str, Any], list[Mapping[str, Any]]]],
        dataset: DatasetName,
    ) -> list[dict[str, Any]]:
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version
        normalized_by_symbol: dict[str, dict[str, Any]] = {}

        for route_spec, rows in rows_by_route:
            suffix = str(route_spec["suffix"])
            exchange = str(route_spec["exchange"])
            allowed_prefixes = tuple(route_spec["allowed_prefixes"])
            route_name = str(route_spec["route_name"])

            for row_idx, row in enumerate(rows):
                raw_code = self._pick(row, row_idx, "证券代码", "A股代码", "code")
                code = self._normalize_code(
                    value=raw_code,
                    route_name=route_name,
                    allowed_prefixes=allowed_prefixes,
                )
                name = self._normalize_required_text(
                    self._pick(
                        row,
                        row_idx,
                        "证券简称",
                        "A股简称",
                        "name",
                        "公司简称",
                    ),
                    field_name="name",
                )
                list_date = self._normalize_date(
                    self._pick(
                        row,
                        row_idx,
                        "上市日期",
                        "A股上市日期",
                        "list_date",
                    ),
                    field_name="list_date",
                )
                symbol = f"{code}.{suffix}"
                record: dict[str, Any] = {
                    "symbol": symbol,
                    "raw_symbol": code,
                    "name": name,
                    "market": "CN",
                    "asset_type": "stock",
                    "currency": "CNY",
                    "exchange": exchange,
                    "list_date": list_date,
                    "delist_date": "9999-12-31",
                    "is_active": True,
                    "source": AKSHARE_SOURCE_ID,
                    "ingested_at": ingested_at,
                    "schema_version": schema_version,
                }

                source_ts = self._pick_optional(
                    row,
                    "source_ts",
                    "更新时间",
                    "update_time",
                    "报告日期",
                )
                if source_ts is not None:
                    record["source_ts"] = self._normalize_source_ts(source_ts)

                existing = normalized_by_symbol.get(symbol)
                if existing is None:
                    normalized_by_symbol[symbol] = record
                    continue

                if self._is_conflicting_duplicate(existing=existing, candidate=record):
                    raise ValueError(
                        "Conflicting duplicate A-share instrument row detected: "
                        f"symbol={symbol!r}."
                    )
                normalized_by_symbol[symbol] = self._select_preferred_duplicate_record(
                    existing=existing,
                    candidate=record,
                )

        return [normalized_by_symbol[key] for key in sorted(normalized_by_symbol)]

    def _filter_by_symbols(
        self,
        *,
        records: Sequence[Mapping[str, Any]],
        symbols: list[str] | None,
    ) -> list[dict[str, Any]]:
        if symbols is None or len(symbols) == 0:
            return [dict(record) for record in records]

        requested: set[str] = set()
        for symbol in symbols:
            requested.add(self._normalize_requested_symbol(symbol))

        filtered: list[dict[str, Any]] = []
        for record in records:
            canonical = str(record["symbol"])
            if canonical in requested:
                filtered.append(dict(record))
        return filtered

    def _normalize_requested_symbol(self, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError(
                "Invalid symbol filter value type for A-share instrument adapter: "
                f"{type(value).__name__}"
            )

        symbol = value.strip().upper()
        if symbol == "":
            raise ValueError("Invalid symbol filter value: empty string")

        if symbol.startswith(("SH", "SZ", "BJ")) and len(symbol) == 8:
            market_prefix = symbol[:2]
            code = symbol[2:]
            if not code.isdigit() or len(code) != 6:
                raise ValueError(f"Invalid symbol filter code: {value!r}")
            inferred_market = self._infer_market_from_code(code)
            if inferred_market != market_prefix:
                raise ValueError(
                    "Invalid symbol filter market-code combination: "
                    f"{value!r}."
                )
            return f"{code}.{market_prefix}"

        if "." in symbol:
            code, market = symbol.split(".", 1)
            if not code.isdigit() or len(code) != 6:
                raise ValueError(
                    f"Invalid symbol filter format: {value!r}. Expected 6-digit code."
                )
            if market not in {"SH", "SZ", "BJ"}:
                raise ValueError(
                    f"Invalid symbol filter market suffix: {market!r}. "
                    "Expected SH/SZ/BJ."
                )
            inferred_market = self._infer_market_from_code(code)
            if inferred_market != market:
                raise ValueError(
                    "Invalid symbol filter market-code combination: "
                    f"{value!r}."
                )
            return f"{code}.{market}"

        if symbol.isdigit() and len(symbol) == 6:
            market = self._infer_market_from_code(symbol)
            return f"{symbol}.{market}"

        raise ValueError(
            f"Invalid symbol filter format: {value!r}. "
            "Expected canonical like '600000.SH' or raw 6-digit A-share code."
        )

    def _normalize_code(
        self,
        *,
        value: Any,
        route_name: str,
        allowed_prefixes: Sequence[str],
    ) -> str:
        if isinstance(value, bool):
            raise ValueError(
                f"Invalid A-share code value for route={route_name}: {value!r}"
            )
        if isinstance(value, int):
            code = f"{value:06d}"
        elif isinstance(value, float):
            if not value.is_integer():
                raise ValueError(
                    f"Invalid A-share code value for route={route_name}: {value!r}"
                )
            code = f"{int(value):06d}"
        elif isinstance(value, str):
            raw = value.strip().upper()
            if raw == "":
                raise ValueError(
                    f"Invalid A-share code value for route={route_name}: empty string"
                )
            if raw.startswith(("SH", "SZ", "BJ")) and len(raw) == 8:
                raw = raw[2:]
            if "." in raw:
                raw = raw.split(".", 1)[0]
            if not raw.isdigit():
                raise ValueError(
                    f"Invalid A-share code value for route={route_name}: {value!r}"
                )
            code = raw.zfill(6)
        else:
            raise ValueError(
                "Invalid A-share code value type for route "
                f"{route_name}: {type(value).__name__}"
            )

        if len(code) != 6:
            raise ValueError(
                f"Invalid A-share code length for route={route_name}: {code!r}"
            )
        if code[0] not in set(allowed_prefixes):
            raise ValueError(
                "Invalid A-share code prefix for route "
                f"{route_name}: code={code!r}, allowed_prefixes={tuple(allowed_prefixes)!r}"
            )
        return code

    def _infer_market_from_code(self, code: str) -> str:
        if code.startswith("6"):
            return "SH"
        if code.startswith(("0", "3")):
            return "SZ"
        if code.startswith(("4", "8", "9")):
            return "BJ"
        raise ValueError(
            f"Invalid symbol filter code prefix for A-share instrument adapter: {code!r}"
        )

    def _pick(
        self,
        row: Mapping[str, Any],
        row_idx: int,
        *keys: str,
    ) -> Any:
        for key in keys:
            if key in row:
                return row[key]
        raise ValueError(
            "Missing required source field in A-share instrument row "
            f"{row_idx}: one of {keys!r}"
        )

    def _pick_optional(
        self,
        row: Mapping[str, Any],
        *keys: str,
    ) -> Any | None:
        for key in keys:
            if key not in row:
                continue
            value = row[key]
            if value is None:
                return None
            if isinstance(value, str) and value.strip() == "":
                return None
            return value
        return None

    def _normalize_required_text(self, value: Any, *, field_name: str) -> str:
        if not isinstance(value, str):
            raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")
        normalized = value.strip()
        if normalized == "":
            raise ValueError(f"Invalid {field_name} value: empty string")
        return normalized

    def _normalize_date(self, value: Any, *, field_name: str) -> str:
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError(f"Invalid {field_name} value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                return date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                ).isoformat()
            try:
                return date.fromisoformat(stripped).isoformat()
            except ValueError as exc:
                raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _normalize_source_ts(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time()).isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError("Invalid source_ts value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                parsed_date = date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
                return datetime.combine(parsed_date, datetime.min.time()).isoformat()
            try:
                return datetime.fromisoformat(stripped).isoformat()
            except ValueError:
                try:
                    parsed_date = date.fromisoformat(stripped)
                    return datetime.combine(parsed_date, datetime.min.time()).isoformat()
                except ValueError as exc:
                    raise ValueError(f"Invalid source_ts value: {value!r}") from exc
        raise ValueError(f"Invalid source_ts value type: {type(value).__name__}")

    def _is_conflicting_duplicate(
        self,
        *,
        existing: Mapping[str, Any],
        candidate: Mapping[str, Any],
    ) -> bool:
        comparable_fields = (
            "symbol",
            "raw_symbol",
            "name",
            "market",
            "asset_type",
            "currency",
            "exchange",
            "list_date",
            "delist_date",
            "is_active",
            "source",
        )
        return any(existing.get(field) != candidate.get(field) for field in comparable_fields)

    def _select_preferred_duplicate_record(
        self,
        *,
        existing: dict[str, Any],
        candidate: dict[str, Any],
    ) -> dict[str, Any]:
        existing_source_ts = existing.get("source_ts")
        candidate_source_ts = candidate.get("source_ts")

        if existing_source_ts is None and candidate_source_ts is not None:
            return candidate
        if existing_source_ts is not None and candidate_source_ts is None:
            return existing
        if existing_source_ts is None and candidate_source_ts is None:
            return existing
        if not isinstance(existing_source_ts, str) or not isinstance(candidate_source_ts, str):
            return existing
        if candidate_source_ts > existing_source_ts:
            return candidate
        return existing

    def _is_instrument_master_network_unavailable(self, exc: BaseException) -> bool:
        network_exception_names = {
            "ProxyError",
            "ConnectionError",
            "ConnectTimeout",
            "ReadTimeout",
            "Timeout",
            "MaxRetryError",
            "NewConnectionError",
            "NameResolutionError",
            "SSLError",
        }
        network_message_tokens = (
            "proxy",
            "timed out",
            "timeout",
            "name resolution",
            "temporary failure in name resolution",
            "failed to establish a new connection",
            "max retries exceeded",
            "network is unreachable",
            "connection refused",
            "no route to host",
            "connection reset",
            "dns",
            "sse.com.cn",
            "szse.cn",
            "bjse.cn",
            "eastmoney",
        )

        seen: set[int] = set()
        current: BaseException | None = exc
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            name = type(current).__name__
            module = type(current).__module__
            message = str(current).lower()

            if name in network_exception_names:
                return True
            if module.startswith(("requests", "urllib3")) and any(
                token in message for token in network_message_tokens
            ):
                return True
            if isinstance(current, (socket.timeout, TimeoutError, ConnectionError)):
                return True
            if isinstance(current, OSError):
                if current.errno in {101, 110, 111, 113}:
                    return True
                if any(token in message for token in network_message_tokens):
                    return True

            if current.__cause__ is not None:
                current = current.__cause__
                continue
            current = current.__context__
        return False


class AkshareAShareCorporateActionsAdapter:
    """Narrow AKShare adapter for one-symbol A-share dividend corporate actions."""

    source_name = AKSHARE_SOURCE_ID
    source_display_name = AKSHARE_SOURCE_NAME

    _PRIMARY_ROUTE_NAME = "stock_dividend_cninfo"
    _FALLBACK_ROUTE_NAME = "stock_history_dividend_detail(indicator=分红)"

    def __init__(
        self,
        *,
        fetch_dividend_cninfo: Callable[..., Any] | None = None,
        fetch_dividend_detail: Callable[..., Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self._fetch_dividend_cninfo = fetch_dividend_cninfo
        self._fetch_dividend_detail = fetch_dividend_detail
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if dataset != DatasetName.CORPORATE_ACTIONS:
            raise ValueError(
                "Unsupported dataset for AkshareAShareCorporateActionsAdapter: "
                f"{dataset.value}"
            )

        symbol, akshare_code = self._require_single_a_share_symbol(symbols)
        rows = self._fetch_rows_for_symbol(akshare_code)
        records = self._normalize_corporate_action_rows(
            rows=rows,
            dataset=dataset,
            symbol=symbol,
        )
        return self._filter_records_by_date(
            records=records,
            start_date=start_date,
            end_date=end_date,
        )

    def _resolve_fetch_dividend_cninfo(self) -> Callable[..., Any]:
        if self._fetch_dividend_cninfo is not None:
            return self._fetch_dividend_cninfo

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare A-share corporate-actions fetch."
            ) from exc

        if hasattr(ak, "stock_dividend_cninfo"):
            return ak.stock_dividend_cninfo
        raise RuntimeError(
            "AKShare A-share corporate-actions primary function is unavailable: "
            "stock_dividend_cninfo"
        )

    def _resolve_fetch_dividend_detail(self) -> Callable[..., Any] | None:
        if self._fetch_dividend_detail is not None:
            return self._fetch_dividend_detail

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception:  # pragma: no cover - exercised by live/dependency env
            return None

        if hasattr(ak, "stock_history_dividend_detail"):
            return ak.stock_history_dividend_detail
        return None

    def _fetch_rows_for_symbol(self, akshare_code: str) -> list[Mapping[str, Any]]:
        primary_fetch = self._resolve_fetch_dividend_cninfo()
        try:
            payload = self._call_primary_route(primary_fetch, akshare_code)
        except Exception as primary_exc:
            if not self._is_corporate_actions_network_unavailable(primary_exc):
                raise

            fallback_fetch = self._resolve_fetch_dividend_detail()
            if fallback_fetch is None:
                raise RuntimeError(
                    "AKShare A-share corporate-actions route unavailable: "
                    f"primary={self._PRIMARY_ROUTE_NAME} -> {type(primary_exc).__name__}: {primary_exc}; "
                    "fallback route is unavailable in current akshare runtime."
                ) from primary_exc

            try:
                fallback_payload = self._call_fallback_route(fallback_fetch, akshare_code)
            except Exception as fallback_exc:
                if self._is_corporate_actions_network_unavailable(fallback_exc):
                    raise RuntimeError(
                        "AKShare A-share corporate-actions routes unavailable: "
                        f"primary={self._PRIMARY_ROUTE_NAME} -> {type(primary_exc).__name__}: {primary_exc}; "
                        f"fallback={self._FALLBACK_ROUTE_NAME} -> {type(fallback_exc).__name__}: {fallback_exc}"
                    ) from fallback_exc
                raise
            return self._payload_to_rows(payload=fallback_payload, route_name=self._FALLBACK_ROUTE_NAME)

        return self._payload_to_rows(payload=payload, route_name=self._PRIMARY_ROUTE_NAME)

    def _inspect_callable(
        self,
        fn: Callable[..., Any],
    ) -> tuple[set[str], bool]:
        try:
            signature = inspect.signature(fn)
        except (TypeError, ValueError):
            return set(), True

        accepted_args: set[str] = set()
        supports_var_kwargs = False
        for parameter in signature.parameters.values():
            if parameter.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ):
                accepted_args.add(parameter.name)
            if parameter.kind == inspect.Parameter.VAR_KEYWORD:
                supports_var_kwargs = True
        return accepted_args, supports_var_kwargs

    def _supports_arg(
        self,
        arg_name: str,
        *,
        accepted_args: set[str],
        supports_var_kwargs: bool,
    ) -> bool:
        return supports_var_kwargs or arg_name in accepted_args

    def _resolve_symbol_arg_name(
        self,
        *,
        accepted_args: set[str],
        supports_var_kwargs: bool,
    ) -> str:
        for candidate in ("symbol", "code", "stock", "ts_code"):
            if self._supports_arg(
                candidate,
                accepted_args=accepted_args,
                supports_var_kwargs=supports_var_kwargs,
            ):
                return candidate
        raise RuntimeError(
            "AKShare A-share corporate-actions route does not accept a symbol/code argument."
        )

    def _call_primary_route(
        self,
        fetch_fn: Callable[..., Any],
        akshare_code: str,
    ) -> Any:
        accepted_args, supports_var_kwargs = self._inspect_callable(fetch_fn)
        symbol_arg = self._resolve_symbol_arg_name(
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        )
        return fetch_fn(**{symbol_arg: akshare_code})

    def _call_fallback_route(
        self,
        fetch_fn: Callable[..., Any],
        akshare_code: str,
    ) -> Any:
        accepted_args, supports_var_kwargs = self._inspect_callable(fetch_fn)
        symbol_arg = self._resolve_symbol_arg_name(
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        )
        kwargs: dict[str, Any] = {symbol_arg: akshare_code}
        if self._supports_arg(
            "indicator",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            kwargs["indicator"] = "分红"
        return fetch_fn(**kwargs)

    def _payload_to_rows(self, *, payload: Any, route_name: str) -> list[Mapping[str, Any]]:
        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "AKShare A-share corporate-actions payload must be DataFrame-like "
                f"or list[Mapping], got {type(payload).__name__}, route={route_name}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "AKShare A-share corporate-actions payload row must be mapping. "
                    f"route={route_name}, idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _require_single_a_share_symbol(
        self,
        symbols: list[str] | None,
    ) -> tuple[str, str]:
        if symbols is None or len(symbols) == 0:
            raise ValueError(
                "AkshareAShareCorporateActionsAdapter requires exactly one symbol, got none."
            )
        if len(symbols) != 1:
            raise ValueError(
                "AkshareAShareCorporateActionsAdapter currently supports exactly one symbol."
            )

        raw_value = symbols[0]
        if not isinstance(raw_value, str) or raw_value.strip() == "":
            raise ValueError("Symbol must be a non-empty string.")
        return self._normalize_requested_a_share_symbol(raw_value)

    def _normalize_requested_a_share_symbol(self, value: str) -> tuple[str, str]:
        normalized = value.strip().upper()

        if normalized.startswith(("SH", "SZ", "BJ")) and len(normalized) == 8:
            market = normalized[:2]
            code = normalized[2:]
            if not code.isdigit() or len(code) != 6:
                raise ValueError(f"Invalid symbol filter code: {value!r}")
            inferred = self._infer_market_from_code(code)
            if inferred != market:
                raise ValueError(
                    "Invalid symbol filter market-code combination: "
                    f"{value!r}."
                )
            return f"{code}.{market}", code

        if "." in normalized:
            code, market = normalized.split(".", 1)
            if not code.isdigit() or len(code) != 6:
                raise ValueError(
                    f"Invalid symbol filter format: {value!r}. Expected 6-digit code."
                )
            if market not in {"SH", "SZ", "BJ"}:
                raise ValueError(
                    f"Invalid symbol filter market suffix: {market!r}. "
                    "Expected SH/SZ/BJ for A-share stock symbols."
                )
            inferred = self._infer_market_from_code(code)
            if inferred != market:
                raise ValueError(
                    "Invalid symbol filter market-code combination: "
                    f"{value!r}."
                )
            return f"{code}.{market}", code

        if normalized.isdigit() and len(normalized) == 6:
            market = self._infer_market_from_code(normalized)
            return f"{normalized}.{market}", normalized

        raise ValueError(
            f"Unsupported symbol format for A-share stock corporate-actions adapter: {value!r}. "
            "Expected canonical like '600000.SH' or raw 6-digit stock code."
        )

    def _infer_market_from_code(self, code: str) -> str:
        if code.startswith("6"):
            return "SH"
        if code.startswith(("0", "3")):
            if code.startswith("399"):
                raise ValueError(
                    "Index symbol is unsupported for A-share stock corporate-actions adapter: "
                    f"{code!r}."
                )
            return "SZ"
        if code.startswith(("4", "8", "9")):
            return "BJ"
        raise ValueError(
            "Invalid A-share stock code prefix for corporate-actions adapter: "
            f"{code!r}."
        )

    def _normalize_corporate_action_rows(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        dataset: DatasetName,
        symbol: str,
    ) -> list[dict[str, Any]]:
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version
        normalized_by_identity: dict[tuple[str, str, str, str], dict[str, Any]] = {}

        for row_idx, row in enumerate(rows):
            event_date = self._resolve_event_date(row=row, row_idx=row_idx)
            value = self._build_value_object(row=row, row_idx=row_idx)
            raw_payload_ref = self._build_raw_payload_ref(
                symbol=symbol,
                event_type="dividend",
                event_date=event_date,
                row=row,
            )

            record: dict[str, Any] = {
                "symbol": symbol,
                "market": "CN",
                "event_date": event_date,
                "event_type": "dividend",
                "value": value,
                "raw_payload_ref": raw_payload_ref,
                "source": AKSHARE_SOURCE_ID,
                "ingested_at": ingested_at,
                "schema_version": schema_version,
            }

            source_ts = self._pick_optional(
                row,
                "source_ts",
                "更新时间",
                "update_time",
                "实施方案公告日期",
                "公告日期",
            )
            if source_ts is not None:
                record["source_ts"] = self._normalize_source_ts(source_ts)

            identity = (
                str(record["symbol"]),
                str(record["event_type"]),
                str(record["event_date"]),
                str(record["raw_payload_ref"]),
            )
            existing = normalized_by_identity.get(identity)
            if existing is None:
                normalized_by_identity[identity] = record
                continue

            if self._is_conflicting_duplicate(existing=existing, candidate=record):
                raise ValueError(
                    "Conflicting duplicate A-share corporate-actions row detected: "
                    f"identity={identity!r}."
                )
            normalized_by_identity[identity] = self._select_preferred_duplicate_record(
                existing=existing,
                candidate=record,
            )

        ordered = list(normalized_by_identity.values())
        ordered.sort(key=lambda record: (str(record["event_date"]), str(record["raw_payload_ref"])))
        return ordered

    def _resolve_event_date(
        self,
        *,
        row: Mapping[str, Any],
        row_idx: int,
    ) -> str:
        candidate_groups: tuple[tuple[str, ...], ...] = (
            ("除权日", "除权除息日", "ex_date", "ex_dividend_date"),
            ("股权登记日", "record_date"),
            ("实施方案公告日期", "公告日期", "announcement_date"),
        )

        for keys in candidate_groups:
            for key in keys:
                if key not in row:
                    continue
                raw_value = row[key]
                if self._is_missing_value(raw_value):
                    continue
                return self._normalize_date(raw_value, field_name="event_date")

        raise ValueError(
            "Missing required source field in A-share corporate-actions row "
            f"{row_idx}: one of ('除权日', '除权除息日', '股权登记日', '实施方案公告日期', '公告日期')."
        )

    def _build_value_object(
        self,
        *,
        row: Mapping[str, Any],
        row_idx: int,
    ) -> dict[str, Any]:
        value: dict[str, Any] = {
            "ratio_base": "per_10_shares",
            "cash_currency": "CNY",
        }

        bonus_share_ratio = self._normalize_optional_float(
            self._pick_optional(row, "送股比例", "送股", "bonus_share_ratio"),
            field_name="bonus_share_ratio",
        )
        transfer_share_ratio = self._normalize_optional_float(
            self._pick_optional(row, "转增比例", "转增", "transfer_share_ratio"),
            field_name="transfer_share_ratio",
        )
        cash_dividend = self._normalize_optional_float(
            self._pick_optional(row, "派息比例", "派息", "cash_dividend"),
            field_name="cash_dividend",
        )
        progress = self._normalize_optional_text(
            self._pick_optional(row, "进度", "status"),
            field_name="progress",
        )
        dividend_type = self._normalize_optional_text(
            self._pick_optional(row, "分红类型", "dividend_type"),
            field_name="dividend_type",
        )
        report_period = self._normalize_optional_text(
            self._pick_optional(row, "报告时间", "报告期", "report_period"),
            field_name="report_period",
        )
        explanation = self._normalize_optional_text(
            self._pick_optional(row, "实施方案分红说明", "方案说明", "说明", "note"),
            field_name="plan_explanation",
        )

        if cash_dividend is not None:
            value["cash_dividend_per_10_shares"] = cash_dividend
        if bonus_share_ratio is not None:
            value["bonus_share_ratio_per_10_shares"] = bonus_share_ratio
        if transfer_share_ratio is not None:
            value["transfer_share_ratio_per_10_shares"] = transfer_share_ratio
        if progress is not None:
            value["progress"] = progress
        if dividend_type is not None:
            value["dividend_type"] = dividend_type
        if report_period is not None:
            value["report_period"] = report_period
        if explanation is not None:
            value["plan_explanation"] = explanation

        if len(value) <= 2:
            raise ValueError(
                "Missing required source field in A-share corporate-actions row "
                f"{row_idx}: no usable dividend detail fields found."
            )

        try:
            json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Non-serializable structured corporate-actions value in row "
                f"{row_idx}."
            ) from exc
        return value

    def _build_raw_payload_ref(
        self,
        *,
        symbol: str,
        event_type: str,
        event_date: str,
        row: Mapping[str, Any],
    ) -> str:
        row_signature = self._stable_row_signature(row)
        digest = hashlib.sha1(row_signature.encode("utf-8")).hexdigest()[:24]
        return f"AKCA|{symbol}|{event_type}|{event_date}|{digest}"

    def _stable_row_signature(self, row: Mapping[str, Any]) -> str:
        sanitized: dict[str, Any] = {}
        for key in sorted(row.keys(), key=lambda item: str(item)):
            key_text = str(key)
            sanitized[key_text] = self._sanitize_for_serialization(
                row[key],
                field_name=f"source_row[{key_text}]",
            )
        try:
            return json.dumps(
                sanitized,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
        except (TypeError, ValueError) as exc:
            raise ValueError("Non-serializable value in corporate-actions source row.") from exc

    def _sanitize_for_serialization(self, value: Any, *, field_name: str) -> Any:
        if self._is_missing_value(value):
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            if not math.isfinite(value):
                raise ValueError(
                    f"Invalid non-finite numeric value for {field_name}: {value!r}"
                )
            return float(value)
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, Mapping):
            nested: dict[str, Any] = {}
            for nested_key in sorted(value.keys(), key=lambda item: str(item)):
                nested_name = str(nested_key)
                nested[nested_name] = self._sanitize_for_serialization(
                    value[nested_key],
                    field_name=f"{field_name}.{nested_name}",
                )
            return nested
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            return [
                self._sanitize_for_serialization(item, field_name=field_name)
                for item in value
            ]
        raise ValueError(
            f"Non-serializable value type for {field_name}: {type(value).__name__}"
        )

    def _filter_records_by_date(
        self,
        *,
        records: Sequence[Mapping[str, Any]],
        start_date: date | None,
        end_date: date | None,
    ) -> list[dict[str, Any]]:
        filtered: list[dict[str, Any]] = []
        for record in records:
            event_dt = date.fromisoformat(str(record["event_date"]))
            if start_date is not None and event_dt < start_date:
                continue
            if end_date is not None and event_dt > end_date:
                continue
            filtered.append(dict(record))
        return filtered

    def _pick_optional(
        self,
        row: Mapping[str, Any],
        *keys: str,
    ) -> Any | None:
        for key in keys:
            if key not in row:
                continue
            value = row[key]
            if self._is_missing_value(value):
                return None
            return value
        return None

    def _normalize_optional_text(
        self,
        value: Any | None,
        *,
        field_name: str,
    ) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")
        normalized = value.strip()
        if normalized == "":
            return None
        return normalized

    def _normalize_optional_float(
        self,
        value: Any | None,
        *,
        field_name: str,
    ) -> float | None:
        if value is None:
            return None
        if isinstance(value, bool):
            raise ValueError(f"Invalid {field_name} value type: bool")
        if isinstance(value, (int, float)):
            numeric = float(value)
            if not math.isfinite(numeric):
                raise ValueError(f"Invalid {field_name} value: {value!r}")
            return numeric
        if isinstance(value, str):
            stripped = value.strip().replace(",", "")
            if stripped == "":
                return None
            try:
                numeric = float(stripped)
            except ValueError as exc:
                raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
            if not math.isfinite(numeric):
                raise ValueError(f"Invalid {field_name} value: {value!r}")
            return numeric
        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _normalize_date(self, value: Any, *, field_name: str) -> str:
        if self._is_missing_value(value):
            raise ValueError(f"Invalid {field_name} value: missing")
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError(f"Invalid {field_name} value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                return date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                ).isoformat()
            cn_match = re.fullmatch(r"(\d{4})年(\d{1,2})月(\d{1,2})日?", stripped)
            if cn_match is not None:
                year, month, day = cn_match.groups()
                return date(int(year), int(month), int(day)).isoformat()
            try:
                return date.fromisoformat(stripped).isoformat()
            except ValueError as exc:
                raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _normalize_source_ts(self, value: Any) -> str:
        if self._is_missing_value(value):
            raise ValueError("Invalid source_ts value: missing")
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time()).isoformat()
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            source_ts = datetime.fromtimestamp(float(value), tz=timezone.utc)
            return source_ts.isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError("Invalid source_ts value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                parsed_date = date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
                return datetime.combine(parsed_date, datetime.min.time()).isoformat()
            try:
                return datetime.fromisoformat(stripped).isoformat()
            except ValueError:
                try:
                    parsed_date = date.fromisoformat(stripped)
                    return datetime.combine(parsed_date, datetime.min.time()).isoformat()
                except ValueError as exc:
                    raise ValueError(f"Invalid source_ts value: {value!r}") from exc
        raise ValueError(f"Invalid source_ts value type: {type(value).__name__}")

    def _is_missing_value(self, value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, str) and value.strip().lower() in {"", "nan", "nat", "none", "null"}:
            return True
        if type(value).__name__ == "NaTType":
            return True
        try:
            if value != value:  # NaN / NaT
                return True
        except Exception:
            pass
        return False

    def _is_conflicting_duplicate(
        self,
        *,
        existing: Mapping[str, Any],
        candidate: Mapping[str, Any],
    ) -> bool:
        comparable_fields = (
            "symbol",
            "market",
            "event_date",
            "event_type",
            "value",
            "raw_payload_ref",
            "source",
        )
        return any(existing.get(field) != candidate.get(field) for field in comparable_fields)

    def _select_preferred_duplicate_record(
        self,
        *,
        existing: dict[str, Any],
        candidate: dict[str, Any],
    ) -> dict[str, Any]:
        existing_source_ts = existing.get("source_ts")
        candidate_source_ts = candidate.get("source_ts")

        if existing_source_ts is None and candidate_source_ts is not None:
            return candidate
        if existing_source_ts is not None and candidate_source_ts is None:
            return existing
        if existing_source_ts is None and candidate_source_ts is None:
            return existing
        if not isinstance(existing_source_ts, str) or not isinstance(candidate_source_ts, str):
            return existing
        if candidate_source_ts > existing_source_ts:
            return candidate
        return existing

    def _is_corporate_actions_network_unavailable(self, exc: BaseException) -> bool:
        network_exception_names = {
            "ProxyError",
            "ConnectionError",
            "ConnectTimeout",
            "ReadTimeout",
            "Timeout",
            "MaxRetryError",
            "NewConnectionError",
            "NameResolutionError",
            "SSLError",
        }
        network_message_tokens = (
            "proxy",
            "timed out",
            "timeout",
            "name resolution",
            "temporary failure in name resolution",
            "failed to establish a new connection",
            "max retries exceeded",
            "network is unreachable",
            "connection refused",
            "no route to host",
            "connection reset",
            "dns",
            "cninfo",
            "eastmoney",
            "stock_dividend_cninfo",
            "stock_history_dividend_detail",
        )

        seen: set[int] = set()
        current: BaseException | None = exc
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            name = type(current).__name__
            module = type(current).__module__
            message = str(current).lower()

            if name in network_exception_names:
                return True
            if module.startswith(("requests", "urllib3")) and any(
                token in message for token in network_message_tokens
            ):
                return True
            if any(token in message for token in network_message_tokens):
                return True
            if isinstance(current, (socket.timeout, TimeoutError, ConnectionError)):
                return True
            if isinstance(current, OSError):
                if current.errno in {101, 110, 111, 113}:
                    return True
                if any(token in message for token in network_message_tokens):
                    return True

            if current.__cause__ is not None:
                current = current.__cause__
                continue
            current = current.__context__
        return False


class AkshareAShareValuationSnapshotAdapter:
    """Narrow AKShare adapter for one-symbol A-share valuation snapshot."""

    source_name = AKSHARE_SOURCE_ID
    source_display_name = AKSHARE_SOURCE_NAME

    _PRIMARY_ROUTE_NAME = "stock_zh_valuation_baidu"
    _MARKET_CAP_ROUTE_NAME = "stock_individual_info_em"
    _OPTIONAL_COMPARISON_ROUTE_NAME = "stock_zh_valuation_comparison_em"
    _PRIMARY_ROUTE_PERIOD = "近一年"

    _REQUIRED_BAIDU_METRICS: tuple[tuple[str, str, float], ...] = (
        ("市盈率(TTM)", "pe_ttm", 1.0),
        ("市净率", "pb", 1.0),
        ("总市值", "market_cap", 100000000.0),
    )

    _OPTIONAL_BAIDU_METRICS: tuple[tuple[str, str, float], ...] = (
        ("市销率(TTM)", "ps_ttm", 1.0),
        ("股息率(TTM)", "dividend_yield", 1.0),
    )

    def __init__(
        self,
        *,
        fetch_valuation_baidu: Callable[..., Any] | None = None,
        fetch_individual_info: Callable[..., Any] | None = None,
        fetch_valuation_comparison: Callable[..., Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self._fetch_valuation_baidu = fetch_valuation_baidu
        self._fetch_individual_info = fetch_individual_info
        self._fetch_valuation_comparison = fetch_valuation_comparison
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if dataset != DatasetName.VALUATION_SNAPSHOT:
            raise ValueError(
                "Unsupported dataset for AkshareAShareValuationSnapshotAdapter: "
                f"{dataset.value}"
            )

        symbol, code, market = self._require_single_a_share_symbol(symbols)

        metrics, trade_date, source_ts = self._collect_metrics(
            code=code,
            market=market,
        )
        record = self._build_snapshot_record(
            dataset=dataset,
            symbol=symbol,
            trade_date=trade_date,
            metrics=metrics,
            source_ts=source_ts,
        )
        return self._filter_records_by_date(
            records=[record],
            start_date=start_date,
            end_date=end_date,
        )

    def _collect_metrics(
        self,
        *,
        code: str,
        market: str,
    ) -> tuple[dict[str, float], str, str | None]:
        baidu_metrics, baidu_trade_date = self._fetch_baidu_metrics(code=code)
        individual_metrics, individual_source_ts = self._fetch_individual_metrics(code=code)
        comparison_metrics = self._fetch_optional_comparison_metrics(code=code, market=market)

        merged_metrics: dict[str, float] = {}
        merged_metrics.update(comparison_metrics)
        merged_metrics.update(individual_metrics)
        merged_metrics.update(baidu_metrics)

        if "market_cap" in individual_metrics:
            merged_metrics["market_cap"] = individual_metrics["market_cap"]

        required_fields = ("pe_ttm", "pb", "market_cap")
        missing_required = [field for field in required_fields if field not in merged_metrics]
        if missing_required:
            raise ValueError(
                "Missing required valuation metric(s) after bounded route merge: "
                f"{missing_required!r}"
            )

        if baidu_trade_date is not None:
            trade_date = baidu_trade_date
        else:
            trade_date = self._now_fn().date().isoformat()
        return merged_metrics, trade_date, individual_source_ts

    def _build_snapshot_record(
        self,
        *,
        dataset: DatasetName,
        symbol: str,
        trade_date: str,
        metrics: Mapping[str, float],
        source_ts: str | None,
    ) -> dict[str, Any]:
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version

        record: dict[str, Any] = {
            "symbol": symbol,
            "market": "CN",
            "trade_date": trade_date,
            "pe_ttm": metrics["pe_ttm"],
            "pb": metrics["pb"],
            "market_cap": metrics["market_cap"],
            "source": AKSHARE_SOURCE_ID,
            "ingested_at": ingested_at,
            "schema_version": schema_version,
        }

        if "float_market_cap" in metrics:
            record["float_market_cap"] = metrics["float_market_cap"]
        if "ps_ttm" in metrics:
            record["ps_ttm"] = metrics["ps_ttm"]
        if "dividend_yield" in metrics:
            record["dividend_yield"] = metrics["dividend_yield"]
        if source_ts is not None:
            record["source_ts"] = source_ts
        return record

    def _resolve_fetch_valuation_baidu(self) -> Callable[..., Any]:
        if self._fetch_valuation_baidu is not None:
            return self._fetch_valuation_baidu

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare valuation snapshot fetch."
            ) from exc

        if hasattr(ak, self._PRIMARY_ROUTE_NAME):
            return getattr(ak, self._PRIMARY_ROUTE_NAME)
        raise RuntimeError(
            "AKShare valuation snapshot primary function is unavailable: "
            f"{self._PRIMARY_ROUTE_NAME}"
        )

    def _resolve_fetch_individual_info(self) -> Callable[..., Any]:
        if self._fetch_individual_info is not None:
            return self._fetch_individual_info

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare valuation snapshot fetch."
            ) from exc

        if hasattr(ak, self._MARKET_CAP_ROUTE_NAME):
            return getattr(ak, self._MARKET_CAP_ROUTE_NAME)
        raise RuntimeError(
            "AKShare valuation snapshot market-cap function is unavailable: "
            f"{self._MARKET_CAP_ROUTE_NAME}"
        )

    def _resolve_fetch_valuation_comparison(self) -> Callable[..., Any] | None:
        if self._fetch_valuation_comparison is not None:
            return self._fetch_valuation_comparison

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception:  # pragma: no cover - exercised by live/dependency env
            return None

        if hasattr(ak, self._OPTIONAL_COMPARISON_ROUTE_NAME):
            return getattr(ak, self._OPTIONAL_COMPARISON_ROUTE_NAME)
        return None

    def _fetch_baidu_metrics(
        self,
        *,
        code: str,
    ) -> tuple[dict[str, float], str | None]:
        fetch_fn = self._resolve_fetch_valuation_baidu()
        metrics: dict[str, float] = {}
        latest_trade_date: date | None = None
        route_failures: list[str] = []

        for indicator, field_name, unit_scale in self._REQUIRED_BAIDU_METRICS:
            try:
                payload = self._call_primary_route(
                    fetch_fn=fetch_fn,
                    code=code,
                    indicator=indicator,
                )
                rows = self._payload_to_rows(
                    payload=payload,
                    route_name=f"{self._PRIMARY_ROUTE_NAME}(indicator={indicator})",
                )
                trade_date, metric_value = self._extract_latest_metric_point(
                    rows=rows,
                    field_name=field_name,
                    metric_name=indicator,
                    unit_scale=unit_scale,
                )
            except Exception as exc:
                if self._is_valuation_route_unavailable(
                    route_name=self._PRIMARY_ROUTE_NAME,
                    exc=exc,
                ):
                    route_failures.append(
                        f"{indicator} -> {type(exc).__name__}: {exc}"
                    )
                    continue
                raise

            metrics[field_name] = metric_value
            if latest_trade_date is None or trade_date > latest_trade_date:
                latest_trade_date = trade_date

        missing_required = [
            spec[1]
            for spec in self._REQUIRED_BAIDU_METRICS
            if spec[1] not in metrics
        ]
        if missing_required:
            if route_failures:
                evidence = " | ".join(route_failures[:3])
                if len(route_failures) > 3:
                    evidence = f"{evidence} | ... total={len(route_failures)} failures"
                raise RuntimeError(
                    "AKShare A-share valuation primary route unavailable for required metrics: "
                    f"{evidence}"
                )
            raise ValueError(
                "Missing required valuation metrics from bounded baidu route: "
                f"{missing_required!r}"
            )

        for indicator, field_name, unit_scale in self._OPTIONAL_BAIDU_METRICS:
            try:
                payload = self._call_primary_route(
                    fetch_fn=fetch_fn,
                    code=code,
                    indicator=indicator,
                )
                rows = self._payload_to_rows(
                    payload=payload,
                    route_name=f"{self._PRIMARY_ROUTE_NAME}(indicator={indicator})",
                )
                _, metric_value = self._extract_latest_metric_point(
                    rows=rows,
                    field_name=field_name,
                    metric_name=indicator,
                    unit_scale=unit_scale,
                )
            except Exception as exc:
                if self._is_valuation_route_unavailable(
                    route_name=self._PRIMARY_ROUTE_NAME,
                    exc=exc,
                ):
                    continue
                raise

            metrics[field_name] = metric_value

        if latest_trade_date is None:
            return metrics, None
        return metrics, latest_trade_date.isoformat()

    def _fetch_individual_metrics(
        self,
        *,
        code: str,
    ) -> tuple[dict[str, float], str | None]:
        fetch_fn = self._resolve_fetch_individual_info()
        try:
            payload = self._call_symbol_only_route(
                fetch_fn=fetch_fn,
                code=code,
                route_name=self._MARKET_CAP_ROUTE_NAME,
            )
        except Exception as exc:
            if self._is_valuation_route_unavailable(
                route_name=self._MARKET_CAP_ROUTE_NAME,
                exc=exc,
            ):
                return {}, None
            raise

        rows = self._payload_to_rows(
            payload=payload,
            route_name=self._MARKET_CAP_ROUTE_NAME,
        )
        item_map = self._extract_item_value_map(
            rows=rows,
            route_name=self._MARKET_CAP_ROUTE_NAME,
        )

        total_market_cap = self._pick_optional_item_value(
            item_map=item_map,
            item_names=("总市值", "总市值(元)", "总市值（元）"),
        )
        float_market_cap = self._pick_optional_item_value(
            item_map=item_map,
            item_names=("流通市值", "流通市值(元)", "流通市值（元）"),
        )

        metrics: dict[str, float] = {}
        if total_market_cap is not None:
            metrics["market_cap"] = self._to_float(
                total_market_cap,
                field_name="market_cap",
                default_unit_scale=1.0,
            )
        if float_market_cap is not None:
            metrics["float_market_cap"] = self._to_float(
                float_market_cap,
                field_name="float_market_cap",
                default_unit_scale=1.0,
            )

        pe_value = self._pick_optional_item_value(
            item_map=item_map,
            item_names=("市盈率(TTM)", "市盈率-动态", "市盈率"),
        )
        if pe_value is not None:
            metrics["pe_ttm"] = self._to_float(
                pe_value,
                field_name="pe_ttm",
                default_unit_scale=1.0,
            )

        pb_value = self._pick_optional_item_value(
            item_map=item_map,
            item_names=("市净率",),
        )
        if pb_value is not None:
            metrics["pb"] = self._to_float(
                pb_value,
                field_name="pb",
                default_unit_scale=1.0,
            )

        ps_value = self._pick_optional_item_value(
            item_map=item_map,
            item_names=("市销率(TTM)", "市销率-TTM", "市销率"),
        )
        if ps_value is not None:
            metrics["ps_ttm"] = self._to_float(
                ps_value,
                field_name="ps_ttm",
                default_unit_scale=1.0,
            )

        dividend_value = self._pick_optional_item_value(
            item_map=item_map,
            item_names=("股息率(TTM)", "股息率", "股息率TTM(%)"),
        )
        if dividend_value is not None:
            metrics["dividend_yield"] = self._to_float(
                dividend_value,
                field_name="dividend_yield",
                default_unit_scale=1.0,
            )

        source_ts_value = self._pick_optional_item_value(
            item_map=item_map,
            item_names=("更新时间", "数据日期", "报告日期", "日期", "time"),
        )
        if source_ts_value is None:
            return metrics, None
        return metrics, self._normalize_source_ts(source_ts_value)

    def _fetch_optional_comparison_metrics(
        self,
        *,
        code: str,
        market: str,
    ) -> dict[str, float]:
        fetch_fn = self._resolve_fetch_valuation_comparison()
        if fetch_fn is None:
            return {}

        route_symbol = f"{market}{code}"
        try:
            payload = self._call_symbol_only_route(
                fetch_fn=fetch_fn,
                code=route_symbol,
                route_name=self._OPTIONAL_COMPARISON_ROUTE_NAME,
            )
        except Exception as exc:
            if self._is_valuation_route_unavailable(
                route_name=self._OPTIONAL_COMPARISON_ROUTE_NAME,
                exc=exc,
            ):
                return {}
            raise

        rows = self._payload_to_rows(
            payload=payload,
            route_name=self._OPTIONAL_COMPARISON_ROUTE_NAME,
        )
        return self._extract_comparison_metrics(
            rows=rows,
            code=code,
        )

    def _extract_comparison_metrics(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        code: str,
    ) -> dict[str, float]:
        matching_rows: list[Mapping[str, Any]] = []
        for row in rows:
            source_code = self._pick_optional(row, "代码", "symbol", "code")
            if source_code is None:
                continue
            normalized_code = self._normalize_code_fragment(source_code)
            if normalized_code != code:
                continue
            matching_rows.append(row)

        if not matching_rows:
            return {}

        best: dict[str, float] = {}
        for row_idx, row in enumerate(matching_rows):
            row_metrics: dict[str, float] = {}

            ps_value = self._pick_optional(row, "市销率-TTM", "市销率(TTM)", "ps_ttm")
            if ps_value is not None:
                row_metrics["ps_ttm"] = self._to_float(
                    ps_value,
                    field_name="ps_ttm",
                    default_unit_scale=1.0,
                )

            dividend_value = self._pick_optional(
                row,
                "股息率-TTM",
                "股息率(TTM)",
                "股息率",
                "dividend_yield",
            )
            if dividend_value is not None:
                row_metrics["dividend_yield"] = self._to_float(
                    dividend_value,
                    field_name="dividend_yield",
                    default_unit_scale=1.0,
                )

            if row_idx == 0:
                best = row_metrics
                continue

            for key, value in row_metrics.items():
                if key in best and best[key] != value:
                    raise ValueError(
                        "Conflicting duplicate A-share valuation comparison row detected: "
                        f"code={code!r}, field={key!r}, existing={best[key]!r}, candidate={value!r}."
                    )
                if key not in best:
                    best[key] = value
        return best

    def _call_primary_route(
        self,
        *,
        fetch_fn: Callable[..., Any],
        code: str,
        indicator: str,
    ) -> Any:
        accepted_args, supports_var_kwargs = self._inspect_callable(fetch_fn)
        kwargs: dict[str, Any] = {}
        symbol_arg = self._resolve_symbol_arg_name(
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
            route_name=self._PRIMARY_ROUTE_NAME,
        )
        kwargs[symbol_arg] = code

        if self._supports_arg(
            "indicator",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            kwargs["indicator"] = indicator
        else:
            raise RuntimeError(
                "AKShare valuation primary route does not accept indicator argument."
            )

        if self._supports_arg(
            "period",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            kwargs["period"] = self._PRIMARY_ROUTE_PERIOD
        return fetch_fn(**kwargs)

    def _call_symbol_only_route(
        self,
        *,
        fetch_fn: Callable[..., Any],
        code: str,
        route_name: str,
    ) -> Any:
        accepted_args, supports_var_kwargs = self._inspect_callable(fetch_fn)
        symbol_arg = self._resolve_symbol_arg_name(
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
            route_name=route_name,
        )
        return fetch_fn(**{symbol_arg: code})

    def _inspect_callable(
        self,
        fn: Callable[..., Any],
    ) -> tuple[set[str], bool]:
        try:
            signature = inspect.signature(fn)
        except (TypeError, ValueError):
            return set(), True

        accepted_args: set[str] = set()
        supports_var_kwargs = False
        for parameter in signature.parameters.values():
            if parameter.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ):
                accepted_args.add(parameter.name)
            if parameter.kind == inspect.Parameter.VAR_KEYWORD:
                supports_var_kwargs = True
        return accepted_args, supports_var_kwargs

    def _supports_arg(
        self,
        arg_name: str,
        *,
        accepted_args: set[str],
        supports_var_kwargs: bool,
    ) -> bool:
        return supports_var_kwargs or arg_name in accepted_args

    def _resolve_symbol_arg_name(
        self,
        *,
        accepted_args: set[str],
        supports_var_kwargs: bool,
        route_name: str,
    ) -> str:
        for candidate in ("symbol", "code", "stock", "ts_code"):
            if self._supports_arg(
                candidate,
                accepted_args=accepted_args,
                supports_var_kwargs=supports_var_kwargs,
            ):
                return candidate
        raise RuntimeError(
            "AKShare valuation route does not accept a symbol/code argument: "
            f"{route_name}"
        )

    def _payload_to_rows(
        self,
        *,
        payload: Any,
        route_name: str,
    ) -> list[Mapping[str, Any]]:
        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "AKShare A-share valuation payload must be DataFrame-like or "
                f"list[Mapping], got {type(payload).__name__}, route={route_name}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "AKShare A-share valuation payload row must be mapping. "
                    f"route={route_name}, idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _extract_latest_metric_point(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        field_name: str,
        metric_name: str,
        unit_scale: float,
    ) -> tuple[date, float]:
        if len(rows) == 0:
            raise ValueError(
                "Missing required source field for valuation metric: "
                f"metric={metric_name!r}, reason=empty_payload"
            )

        values_by_date: dict[date, float] = {}
        for row_idx, row in enumerate(rows):
            trade_date = self._normalize_trade_date(
                self._pick(row, row_idx, "date", "日期", "trade_date"),
                field_name="trade_date",
            )
            metric_value = self._to_float(
                self._pick(row, row_idx, "value", "值", "指标值"),
                field_name=field_name,
                default_unit_scale=unit_scale,
            )

            existing = values_by_date.get(trade_date)
            if existing is not None and existing != metric_value:
                raise ValueError(
                    "Conflicting duplicate A-share valuation source row detected: "
                    f"metric={metric_name!r}, trade_date={trade_date.isoformat()!r}, "
                    f"existing={existing!r}, candidate={metric_value!r}."
                )
            values_by_date[trade_date] = metric_value

        latest_trade_date = max(values_by_date)
        return latest_trade_date, values_by_date[latest_trade_date]

    def _extract_item_value_map(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        route_name: str,
    ) -> dict[str, Any]:
        item_map: dict[str, Any] = {}
        for row_idx, row in enumerate(rows):
            item_name_value = self._pick(row, row_idx, "item", "项目", "指标")
            if not isinstance(item_name_value, str):
                raise ValueError(
                    "Invalid item name in valuation market-cap row: "
                    f"route={route_name}, row={row_idx}, value={item_name_value!r}."
                )
            item_name = item_name_value.strip()
            if item_name == "":
                continue

            item_value = self._pick(row, row_idx, "value", "值", "数据")
            existing = item_map.get(item_name)
            if existing is not None and not self._item_values_equal(existing, item_value):
                raise ValueError(
                    "Conflicting duplicate valuation market-cap item detected: "
                    f"route={route_name}, item={item_name!r}, "
                    f"existing={existing!r}, candidate={item_value!r}."
                )
            item_map[item_name] = item_value
        return item_map

    def _item_values_equal(self, left: Any, right: Any) -> bool:
        if self._is_missing_value(left) and self._is_missing_value(right):
            return True
        return left == right

    def _pick_optional_item_value(
        self,
        *,
        item_map: Mapping[str, Any],
        item_names: Sequence[str],
    ) -> Any | None:
        for item_name in item_names:
            if item_name not in item_map:
                continue
            value = item_map[item_name]
            if self._is_missing_value(value):
                return None
            return value
        return None

    def _normalize_code_fragment(self, value: Any) -> str:
        if not isinstance(value, str):
            return ""
        stripped = value.strip().upper()
        if stripped.isdigit() and len(stripped) == 6:
            return stripped
        if stripped.startswith(("SH", "SZ", "BJ")) and len(stripped) == 8:
            code = stripped[2:]
            if code.isdigit():
                return code
            return ""
        if "." in stripped:
            head, tail = stripped.split(".", 1)
            if head.isdigit() and len(head) == 6:
                return head
            if tail.isdigit() and len(tail) == 6:
                return tail
        return ""

    def _pick(
        self,
        row: Mapping[str, Any],
        row_idx: int,
        *keys: str,
    ) -> Any:
        for key in keys:
            if key in row:
                return row[key]
        raise ValueError(
            "Missing required source field in valuation row "
            f"{row_idx}: one of {keys!r}."
        )

    def _pick_optional(
        self,
        row: Mapping[str, Any],
        *keys: str,
    ) -> Any | None:
        for key in keys:
            if key not in row:
                continue
            value = row[key]
            if self._is_missing_value(value):
                return None
            return value
        return None

    def _to_float(
        self,
        value: Any,
        *,
        field_name: str,
        default_unit_scale: float,
    ) -> float:
        if isinstance(value, bool):
            raise ValueError(f"Invalid {field_name} value type: bool")
        if isinstance(value, (int, float)):
            numeric = float(value) * default_unit_scale
            if not math.isfinite(numeric):
                raise ValueError(f"Invalid {field_name} value: {value!r}")
            return numeric
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError(f"Invalid {field_name} value: empty string")
            if stripped.lower() in {"nan", "nat", "none", "null"}:
                raise ValueError(f"Invalid {field_name} value: {value!r}")

            normalized = stripped.replace(",", "")
            unit_scale = default_unit_scale
            unit_specs = (
                ("亿元", 100000000.0),
                ("亿", 100000000.0),
                ("万元", 10000.0),
                ("万", 10000.0),
                ("元", 1.0),
                ("%", 1.0),
            )
            for unit_suffix, factor in unit_specs:
                if normalized.endswith(unit_suffix):
                    normalized = normalized[: -len(unit_suffix)]
                    unit_scale *= factor
                    break

            normalized = normalized.strip()
            if normalized == "":
                raise ValueError(f"Invalid {field_name} value: {value!r}")
            try:
                numeric = float(normalized) * unit_scale
            except ValueError as exc:
                raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
            if not math.isfinite(numeric):
                raise ValueError(f"Invalid {field_name} value: {value!r}")
            return numeric

        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _normalize_trade_date(self, value: Any, *, field_name: str) -> date:
        if self._is_missing_value(value):
            raise ValueError(f"Invalid {field_name} value: missing")
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError(f"Invalid {field_name} value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                return date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
            try:
                return date.fromisoformat(stripped)
            except ValueError:
                try:
                    return datetime.fromisoformat(stripped).date()
                except ValueError as exc:
                    raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _normalize_source_ts(self, value: Any) -> str:
        if self._is_missing_value(value):
            raise ValueError("Invalid source_ts value: missing")
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time()).isoformat()
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            source_ts = datetime.fromtimestamp(float(value), tz=timezone.utc)
            return source_ts.isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError("Invalid source_ts value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                parsed_date = date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
                return datetime.combine(parsed_date, datetime.min.time()).isoformat()
            try:
                return datetime.fromisoformat(stripped).isoformat()
            except ValueError:
                try:
                    parsed_date = date.fromisoformat(stripped)
                    return datetime.combine(parsed_date, datetime.min.time()).isoformat()
                except ValueError as exc:
                    raise ValueError(f"Invalid source_ts value: {value!r}") from exc
        raise ValueError(f"Invalid source_ts value type: {type(value).__name__}")

    def _require_single_a_share_symbol(
        self,
        symbols: list[str] | None,
    ) -> tuple[str, str, str]:
        if symbols is None or len(symbols) == 0:
            raise ValueError(
                "AkshareAShareValuationSnapshotAdapter requires exactly one symbol, got none."
            )
        if len(symbols) != 1:
            raise ValueError(
                "AkshareAShareValuationSnapshotAdapter currently supports exactly one symbol."
            )

        raw_value = symbols[0]
        if not isinstance(raw_value, str) or raw_value.strip() == "":
            raise ValueError("Symbol must be a non-empty string.")
        return self._normalize_requested_a_share_symbol(raw_value)

    def _normalize_requested_a_share_symbol(self, value: str) -> tuple[str, str, str]:
        normalized = value.strip().upper()

        if normalized.startswith(("SH", "SZ", "BJ")) and len(normalized) == 8:
            market = normalized[:2]
            code = normalized[2:]
            if not code.isdigit() or len(code) != 6:
                raise ValueError(f"Invalid symbol filter code: {value!r}")
            inferred = self._infer_market_from_code(code)
            if inferred != market:
                raise ValueError(
                    "Invalid symbol filter market-code combination: "
                    f"{value!r}."
                )
            return f"{code}.{market}", code, market

        if "." in normalized:
            code, market = normalized.split(".", 1)
            if not code.isdigit() or len(code) != 6:
                raise ValueError(
                    f"Invalid symbol filter format: {value!r}. Expected 6-digit code."
                )
            if market not in {"SH", "SZ", "BJ"}:
                raise ValueError(
                    f"Invalid symbol filter market suffix: {market!r}. "
                    "Expected SH/SZ/BJ for A-share stock symbols."
                )
            inferred = self._infer_market_from_code(code)
            if inferred != market:
                raise ValueError(
                    "Invalid symbol filter market-code combination: "
                    f"{value!r}."
                )
            return f"{code}.{market}", code, market

        if normalized.isdigit() and len(normalized) == 6:
            market = self._infer_market_from_code(normalized)
            return f"{normalized}.{market}", normalized, market

        raise ValueError(
            f"Unsupported symbol format for A-share valuation snapshot adapter: {value!r}. "
            "Expected canonical like '600000.SH' or raw 6-digit stock code."
        )

    def _infer_market_from_code(self, code: str) -> str:
        if code.startswith("6"):
            return "SH"
        if code.startswith(("0", "3")):
            if code.startswith("399"):
                raise ValueError(
                    "Index symbol is unsupported for A-share valuation snapshot adapter: "
                    f"{code!r}."
                )
            return "SZ"
        if code.startswith(("4", "8", "9")):
            return "BJ"
        raise ValueError(
            "Invalid A-share stock code prefix for valuation snapshot adapter: "
            f"{code!r}."
        )

    def _filter_records_by_date(
        self,
        *,
        records: Sequence[Mapping[str, Any]],
        start_date: date | None,
        end_date: date | None,
    ) -> list[dict[str, Any]]:
        filtered: list[dict[str, Any]] = []
        for record in records:
            trade_date = date.fromisoformat(str(record["trade_date"]))
            if start_date is not None and trade_date < start_date:
                continue
            if end_date is not None and trade_date > end_date:
                continue
            filtered.append(dict(record))
        return filtered

    def _is_missing_value(self, value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, str) and value.strip().lower() in {"", "nan", "nat", "none", "null"}:
            return True
        if type(value).__name__ == "NaTType":
            return True
        try:
            if value != value:  # NaN / NaT
                return True
        except Exception:
            pass
        return False

    def _is_valuation_route_unavailable(
        self,
        *,
        route_name: str,
        exc: BaseException,
    ) -> bool:
        if self._is_valuation_network_unavailable(exc):
            return True
        if route_name == self._OPTIONAL_COMPARISON_ROUTE_NAME and self._is_comparison_route_shape_unavailable(
            exc
        ):
            return True
        if route_name == self._PRIMARY_ROUTE_NAME and self._is_baidu_route_shape_unavailable(exc):
            return True
        return False

    def _is_baidu_route_shape_unavailable(self, exc: BaseException) -> bool:
        seen: set[int] = set()
        current: BaseException | None = exc
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            if (
                isinstance(current, ValueError)
                and "reason=empty_payload" in str(current)
            ):
                return True
            if (
                isinstance(current, TypeError)
                and "nonetype" in str(current).lower()
                and "subscriptable" in str(current).lower()
            ):
                return True
            if current.__cause__ is not None:
                current = current.__cause__
                continue
            current = current.__context__
        return False

    def _is_comparison_route_shape_unavailable(self, exc: BaseException) -> bool:
        seen: set[int] = set()
        current: BaseException | None = exc
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            if isinstance(current, KeyError):
                message = str(current)
                if "EV/EBITDA-24A" in message:
                    return True
            if current.__cause__ is not None:
                current = current.__cause__
                continue
            current = current.__context__
        return False

    def _is_valuation_network_unavailable(self, exc: BaseException) -> bool:
        network_exception_names = {
            "ProxyError",
            "ConnectionError",
            "ConnectTimeout",
            "ReadTimeout",
            "Timeout",
            "MaxRetryError",
            "NewConnectionError",
            "NameResolutionError",
            "SSLError",
        }
        network_message_tokens = (
            "proxy",
            "timed out",
            "timeout",
            "name resolution",
            "temporary failure in name resolution",
            "failed to establish a new connection",
            "max retries exceeded",
            "network is unreachable",
            "connection refused",
            "no route to host",
            "connection reset",
            "dns",
            "baidu.com",
            "gushitong.baidu.com",
            "eastmoney",
            "push2.eastmoney.com",
            "stock_zh_valuation_baidu",
            "stock_individual_info_em",
            "stock_zh_valuation_comparison_em",
        )

        seen: set[int] = set()
        current: BaseException | None = exc
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            name = type(current).__name__
            module = type(current).__module__
            message = str(current).lower()

            if name in network_exception_names:
                return True
            if module.startswith(("requests", "urllib3")) and any(
                token in message for token in network_message_tokens
            ):
                return True
            if isinstance(current, (socket.timeout, TimeoutError, ConnectionError)):
                return True
            if isinstance(current, OSError):
                if current.errno in {101, 110, 111, 113}:
                    return True
                if any(token in message for token in network_message_tokens):
                    return True

            if current.__cause__ is not None:
                current = current.__cause__
                continue
            current = current.__context__
        return False


class AkshareAShareCapitalFlowSnapshotAdapter:
    """Narrow AKShare adapter for one-symbol A-share capital-flow snapshots."""

    source_name = AKSHARE_SOURCE_ID
    source_display_name = AKSHARE_SOURCE_NAME

    _PRIMARY_ROUTE_NAME = "stock_individual_fund_flow"
    _PRIMARY_FALLBACK_ROUTE_NAME = "datacenter_securities_fundflow_snapshot"
    _TURNOVER_ROUTE_NAME = "stock_zh_a_hist"
    _NORTHBOUND_ROUTE_NAME = "stock_hsgt_individual_em"
    _PRIMARY_FALLBACK_ENDPOINT = "https://datacenter.eastmoney.com/securities/api/data/get"

    def __init__(
        self,
        *,
        fetch_capital_flow: Callable[..., Any] | None = None,
        fetch_capital_flow_fallback: Callable[..., Any] | None = None,
        fetch_turnover_hist: Callable[..., Any] | None = None,
        fetch_northbound: Callable[..., Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self._fetch_capital_flow = fetch_capital_flow
        self._fetch_capital_flow_fallback = fetch_capital_flow_fallback
        self._fetch_turnover_hist = fetch_turnover_hist
        self._fetch_northbound = fetch_northbound
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if dataset != DatasetName.CAPITAL_FLOW_SNAPSHOT:
            raise ValueError(
                "Unsupported dataset for AkshareAShareCapitalFlowSnapshotAdapter: "
                f"{dataset.value}"
            )

        symbol, code, market = self._require_single_a_share_symbol(symbols)
        primary_records = self._fetch_primary_records(
            dataset=dataset,
            symbol=symbol,
            code=code,
            market=market,
        )
        if len(primary_records) == 0:
            return []

        primary_dates = [date.fromisoformat(str(item["trade_date"])) for item in primary_records]
        bounded_start = start_date or min(primary_dates)
        bounded_end = end_date or max(primary_dates)

        turnover_by_date = self._fetch_turnover_by_date(
            code=code,
            start_date=bounded_start,
            end_date=bounded_end,
        )
        northbound_by_date = self._fetch_northbound_by_date(code=code)

        merged = self._merge_optional_metrics(
            records=primary_records,
            turnover_by_date=turnover_by_date,
            northbound_by_date=northbound_by_date,
        )
        return self._filter_records_by_date(
            records=merged,
            start_date=start_date,
            end_date=end_date,
        )

    def _fetch_primary_records(
        self,
        *,
        dataset: DatasetName,
        symbol: str,
        code: str,
        market: str,
    ) -> list[dict[str, Any]]:
        rows = self._fetch_primary_rows_with_fallback(code=code, market=market)
        if len(rows) == 0:
            raise ValueError(
                "Missing required source field for A-share capital-flow snapshot: "
                "reason=empty_payload"
            )
        return self._normalize_primary_rows_to_records(
            dataset=dataset,
            symbol=symbol,
            rows=rows,
        )

    def _fetch_primary_rows_with_fallback(
        self,
        *,
        code: str,
        market: str,
    ) -> list[Mapping[str, Any]]:
        fetch_fn = self._resolve_fetch_capital_flow()
        try:
            payload = self._call_primary_route(
                fetch_fn=fetch_fn,
                code=code,
                market=market.lower(),
            )
            return self._payload_to_rows(
                payload=payload,
                route_name=self._PRIMARY_ROUTE_NAME,
            )
        except Exception as primary_exc:
            if not self._is_capital_flow_route_unavailable(
                route_name=self._PRIMARY_ROUTE_NAME,
                exc=primary_exc,
            ):
                raise

            try:
                fallback_payload = self._fetch_capital_flow_via_fallback_route(code=code)
            except Exception as fallback_exc:
                if self._is_capital_flow_route_unavailable(
                    route_name=self._PRIMARY_FALLBACK_ROUTE_NAME,
                    exc=fallback_exc,
                ):
                    raise RuntimeError(
                        "AKShare A-share capital-flow primary and bounded fallback routes are unavailable: "
                        f"primary={self._PRIMARY_ROUTE_NAME} -> {type(primary_exc).__name__}: {primary_exc}; "
                        f"fallback={self._PRIMARY_FALLBACK_ROUTE_NAME} -> {type(fallback_exc).__name__}: {fallback_exc}"
                    ) from fallback_exc
                raise

            return self._payload_to_rows(
                payload=fallback_payload,
                route_name=self._PRIMARY_FALLBACK_ROUTE_NAME,
            )

    def _normalize_primary_rows_to_records(
        self,
        *,
        dataset: DatasetName,
        symbol: str,
        rows: Sequence[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version
        records_by_identity: dict[tuple[str, str, str], dict[str, Any]] = {}

        for row_idx, row in enumerate(rows):
            trade_date = self._normalize_trade_date(
                self._pick(row, row_idx, "日期", "trade_date", "date"),
                field_name="trade_date",
            ).isoformat()
            record: dict[str, Any] = {
                "symbol": symbol,
                "market": "CN",
                "trade_date": trade_date,
                "main_net_inflow": self._to_float(
                    self._pick(row, row_idx, "主力净流入-净额", "main_net_inflow"),
                    field_name="main_net_inflow",
                    default_unit_scale=1.0,
                ),
                "source": AKSHARE_SOURCE_ID,
                "ingested_at": ingested_at,
                "schema_version": schema_version,
            }

            net_inflow_value = self._pick_optional(
                row,
                "净流入-净额",
                "净流入净额",
                "净额",
                "net_inflow",
            )
            if net_inflow_value is not None:
                record["net_inflow"] = self._to_float(
                    net_inflow_value,
                    field_name="net_inflow",
                    default_unit_scale=1.0,
                )

            turnover_value = self._pick_optional(row, "换手率", "turnover_rate")
            if turnover_value is not None:
                record["turnover_rate"] = self._to_float(
                    turnover_value,
                    field_name="turnover_rate",
                    default_unit_scale=1.0,
                )

            source_ts_value = self._pick_optional(row, "更新时间", "数据时间", "source_ts")
            if source_ts_value is not None:
                record["source_ts"] = self._normalize_source_ts(source_ts_value)

            identity = (symbol, trade_date, AKSHARE_SOURCE_ID)
            existing = records_by_identity.get(identity)
            if existing is None:
                records_by_identity[identity] = record
                continue
            records_by_identity[identity] = self._merge_duplicate_identity_record(
                existing=existing,
                candidate=record,
                identity=identity,
            )

        deduplicated = list(records_by_identity.values())
        deduplicated.sort(key=lambda item: str(item["trade_date"]))
        return deduplicated

    def _fetch_turnover_by_date(
        self,
        *,
        code: str,
        start_date: date | None,
        end_date: date | None,
    ) -> dict[str, float]:
        fetch_fn = self._resolve_fetch_turnover_hist()
        if fetch_fn is None:
            return {}

        try:
            payload = self._call_turnover_route(
                fetch_fn=fetch_fn,
                code=code,
                start_date=start_date,
                end_date=end_date,
            )
        except Exception as exc:
            if self._is_capital_flow_network_unavailable(exc):
                return {}
            raise

        rows = self._payload_to_rows(
            payload=payload,
            route_name=self._TURNOVER_ROUTE_NAME,
        )
        turnover_by_date: dict[str, float] = {}
        for row_idx, row in enumerate(rows):
            turnover_value = self._pick_optional(row, "换手率", "turnover_rate")
            if turnover_value is None:
                continue
            trade_date = self._normalize_trade_date(
                self._pick(row, row_idx, "日期", "trade_date", "date"),
                field_name="trade_date",
            ).isoformat()
            normalized_turnover = self._to_float(
                turnover_value,
                field_name="turnover_rate",
                default_unit_scale=1.0,
            )
            existing = turnover_by_date.get(trade_date)
            if existing is not None and existing != normalized_turnover:
                raise ValueError(
                    "Conflicting duplicate A-share turnover row detected: "
                    f"code={code!r}, trade_date={trade_date!r}, "
                    f"existing={existing!r}, candidate={normalized_turnover!r}."
                )
            turnover_by_date[trade_date] = normalized_turnover
        return turnover_by_date

    def _fetch_northbound_by_date(self, *, code: str) -> dict[str, float]:
        fetch_fn = self._resolve_fetch_northbound()
        if fetch_fn is None:
            return {}

        try:
            payload = self._call_symbol_only_route(
                fetch_fn=fetch_fn,
                code=code,
                route_name=self._NORTHBOUND_ROUTE_NAME,
            )
        except Exception as exc:
            if self._is_capital_flow_route_unavailable(
                route_name=self._NORTHBOUND_ROUTE_NAME,
                exc=exc,
            ):
                return {}
            raise

        rows = self._payload_to_rows(
            payload=payload,
            route_name=self._NORTHBOUND_ROUTE_NAME,
        )
        northbound_by_date: dict[str, float] = {}
        for row_idx, row in enumerate(rows):
            northbound_value = self._pick_optional(row, "今日增持资金", "northbound_net_buy")
            if northbound_value is None:
                continue
            trade_date = self._normalize_trade_date(
                self._pick(row, row_idx, "持股日期", "trade_date", "date"),
                field_name="trade_date",
            ).isoformat()
            normalized_northbound = self._to_float(
                northbound_value,
                field_name="northbound_net_buy",
                default_unit_scale=1.0,
            )
            existing = northbound_by_date.get(trade_date)
            if existing is not None and existing != normalized_northbound:
                raise ValueError(
                    "Conflicting duplicate A-share northbound row detected: "
                    f"code={code!r}, trade_date={trade_date!r}, "
                    f"existing={existing!r}, candidate={normalized_northbound!r}."
                )
            northbound_by_date[trade_date] = normalized_northbound
        return northbound_by_date

    def _merge_optional_metrics(
        self,
        *,
        records: Sequence[Mapping[str, Any]],
        turnover_by_date: Mapping[str, float],
        northbound_by_date: Mapping[str, float],
    ) -> list[dict[str, Any]]:
        merged: list[dict[str, Any]] = []
        for record in records:
            current = dict(record)
            trade_date = str(record["trade_date"])
            if trade_date in turnover_by_date:
                current["turnover_rate"] = turnover_by_date[trade_date]
            if trade_date in northbound_by_date:
                current["northbound_net_buy"] = northbound_by_date[trade_date]
            merged.append(current)
        return merged

    def _merge_duplicate_identity_record(
        self,
        *,
        existing: Mapping[str, Any],
        candidate: Mapping[str, Any],
        identity: tuple[str, str, str],
    ) -> dict[str, Any]:
        merged = dict(existing)
        for field_name, field_value in candidate.items():
            if field_name not in merged:
                merged[field_name] = field_value
                continue
            if self._item_values_equal(merged[field_name], field_value):
                continue
            raise ValueError(
                "Conflicting duplicate A-share capital-flow row detected: "
                f"symbol={identity[0]!r}, trade_date={identity[1]!r}, "
                f"field={field_name!r}, existing={merged[field_name]!r}, "
                f"candidate={field_value!r}."
            )
        return merged

    def _item_values_equal(self, left: Any, right: Any) -> bool:
        if self._is_missing_value(left) and self._is_missing_value(right):
            return True
        return left == right

    def _resolve_fetch_capital_flow(self) -> Callable[..., Any]:
        if self._fetch_capital_flow is not None:
            return self._fetch_capital_flow

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare capital-flow snapshot fetch."
            ) from exc

        if hasattr(ak, self._PRIMARY_ROUTE_NAME):
            return getattr(ak, self._PRIMARY_ROUTE_NAME)
        raise RuntimeError(
            "AKShare A-share capital-flow primary function is unavailable: "
            f"{self._PRIMARY_ROUTE_NAME}"
        )

    def _fetch_capital_flow_via_fallback_route(
        self,
        *,
        code: str,
    ) -> list[Mapping[str, Any]]:
        fetch_fn = self._resolve_fetch_capital_flow_fallback()
        payload = fetch_fn(code=code)
        rows = self._payload_to_rows(
            payload=payload,
            route_name=self._PRIMARY_FALLBACK_ROUTE_NAME,
        )
        if len(rows) == 0:
            raise ValueError(
                "Missing required source field for A-share capital-flow snapshot fallback route: "
                "reason=empty_payload"
            )
        return rows

    def _resolve_fetch_capital_flow_fallback(self) -> Callable[..., Any]:
        if self._fetch_capital_flow_fallback is not None:
            return self._fetch_capital_flow_fallback
        return self._fetch_capital_flow_via_datacenter

    def _fetch_capital_flow_via_datacenter(
        self,
        *,
        code: str,
    ) -> list[Mapping[str, Any]]:
        try:
            import requests
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "requests dependency is required for A-share capital-flow fallback fetch."
            ) from exc

        params = {
            "type": "RPT_FUNDFLOW_SECUCODE",
            "sty": "ALL",
            "source": "SECURITIES",
            "client": "WAP",
            "p": "1",
            "ps": "20",
            "sr": "-1",
            "st": "MAIN_NETINFLOW",
            "filter": f'(SECURITY_CODE="{code}")',
            "extraCols": (
                'MAIN_NETINFLOW|02|SECURITY_CODE|MAIN_NETINFLOW,'
                'f8|02|SECURITY_CODE|TURNOVER_RATE,'
                'f124|02|SECURITY_CODE|F124_TS'
            ),
        }
        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(
            self._PRIMARY_FALLBACK_ENDPOINT,
            params=params,
            headers=headers,
            timeout=10,
        )
        payload = response.json()
        if not isinstance(payload, Mapping):
            raise ValueError(
                "Invalid datacenter fallback payload type: "
                f"{type(payload).__name__}."
            )
        if payload.get("success") is not True:
            raise RuntimeError(
                "Datacenter capital-flow fallback route returned unsuccessful payload: "
                f"message={payload.get('message')!r}, code={payload.get('code')!r}"
            )

        result = payload.get("result")
        if not isinstance(result, Mapping):
            raise ValueError(
                "Invalid datacenter fallback payload: missing mapping result section."
            )
        source_rows = result.get("data")
        if not isinstance(source_rows, list):
            raise ValueError(
                "Invalid datacenter fallback payload: result.data must be list."
            )

        normalized_rows: list[Mapping[str, Any]] = []
        for row_idx, row in enumerate(source_rows):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "Invalid datacenter fallback row type: "
                    f"idx={row_idx}, type={type(row).__name__}."
                )

            if self._normalize_code_fragment(row.get("SECURITY_CODE")) != code:
                continue

            main_net_inflow = row.get("MAIN_NETINFLOW")
            if self._is_missing_value(main_net_inflow):
                raise ValueError(
                    "Missing required source field in datacenter fallback row "
                    f"{row_idx}: MAIN_NETINFLOW."
                )

            normalized_row: dict[str, Any] = {
                "日期": self._resolve_datacenter_trade_date(row),
                "主力净流入-净额": main_net_inflow,
            }

            turnover_value = row.get("TURNOVER_RATE")
            if not self._is_missing_value(turnover_value):
                normalized_row["换手率"] = turnover_value

            source_ts = self._resolve_datacenter_source_ts(row)
            if source_ts is not None:
                normalized_row["source_ts"] = source_ts

            normalized_rows.append(normalized_row)
        return normalized_rows

    def _resolve_datacenter_trade_date(self, row: Mapping[str, Any]) -> str:
        for key in ("TRADE_DATE", "TRADEDATE", "DATE", "REPORT_DATE"):
            if key not in row:
                continue
            value = row[key]
            if self._is_missing_value(value):
                continue
            return str(value)

        source_ts = self._resolve_datacenter_source_ts(row)
        if source_ts is not None:
            source_dt = datetime.fromisoformat(source_ts)
            return source_dt.date().isoformat()

        return self._now_fn().date().isoformat()

    def _resolve_datacenter_source_ts(self, row: Mapping[str, Any]) -> str | None:
        for key in ("F124_TS", "UPDATE_TS", "UPDATE_TIME", "TIMESTAMP"):
            if key not in row:
                continue
            value = row[key]
            if self._is_missing_value(value):
                continue
            return self._normalize_source_ts(value)
        return None

    def _resolve_fetch_turnover_hist(self) -> Callable[..., Any] | None:
        if self._fetch_turnover_hist is not None:
            return self._fetch_turnover_hist

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception:  # pragma: no cover - exercised by live/dependency env
            return None

        if hasattr(ak, self._TURNOVER_ROUTE_NAME):
            return getattr(ak, self._TURNOVER_ROUTE_NAME)
        return None

    def _resolve_fetch_northbound(self) -> Callable[..., Any] | None:
        if self._fetch_northbound is not None:
            return self._fetch_northbound

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception:  # pragma: no cover - exercised by live/dependency env
            return None

        if hasattr(ak, self._NORTHBOUND_ROUTE_NAME):
            return getattr(ak, self._NORTHBOUND_ROUTE_NAME)
        return None

    def _call_primary_route(
        self,
        *,
        fetch_fn: Callable[..., Any],
        code: str,
        market: str,
    ) -> Any:
        accepted_args, supports_var_kwargs = self._inspect_callable(fetch_fn)
        symbol_arg = self._resolve_symbol_arg_name(
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
            route_name=self._PRIMARY_ROUTE_NAME,
        )

        kwargs: dict[str, Any] = {symbol_arg: code}
        if self._supports_arg(
            "market",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            kwargs["market"] = market
        else:
            raise RuntimeError(
                "AKShare capital-flow primary route does not accept market argument."
            )
        return fetch_fn(**kwargs)

    def _call_turnover_route(
        self,
        *,
        fetch_fn: Callable[..., Any],
        code: str,
        start_date: date | None,
        end_date: date | None,
    ) -> Any:
        accepted_args, supports_var_kwargs = self._inspect_callable(fetch_fn)
        symbol_arg = self._resolve_symbol_arg_name(
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
            route_name=self._TURNOVER_ROUTE_NAME,
        )
        kwargs: dict[str, Any] = {symbol_arg: code}
        if self._supports_arg(
            "period",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            kwargs["period"] = "daily"
        if self._supports_arg(
            "adjust",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            kwargs["adjust"] = ""
        if start_date is not None and self._supports_arg(
            "start_date",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            kwargs["start_date"] = self._to_akshare_date(start_date)
        if end_date is not None and self._supports_arg(
            "end_date",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            kwargs["end_date"] = self._to_akshare_date(end_date)
        return fetch_fn(**kwargs)

    def _call_symbol_only_route(
        self,
        *,
        fetch_fn: Callable[..., Any],
        code: str,
        route_name: str,
    ) -> Any:
        accepted_args, supports_var_kwargs = self._inspect_callable(fetch_fn)
        symbol_arg = self._resolve_symbol_arg_name(
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
            route_name=route_name,
        )
        return fetch_fn(**{symbol_arg: code})

    def _inspect_callable(self, fn: Callable[..., Any]) -> tuple[set[str], bool]:
        try:
            signature = inspect.signature(fn)
        except (TypeError, ValueError):
            return set(), True

        accepted_args: set[str] = set()
        supports_var_kwargs = False
        for parameter in signature.parameters.values():
            if parameter.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ):
                accepted_args.add(parameter.name)
            if parameter.kind == inspect.Parameter.VAR_KEYWORD:
                supports_var_kwargs = True
        return accepted_args, supports_var_kwargs

    def _supports_arg(
        self,
        arg_name: str,
        *,
        accepted_args: set[str],
        supports_var_kwargs: bool,
    ) -> bool:
        return supports_var_kwargs or arg_name in accepted_args

    def _resolve_symbol_arg_name(
        self,
        *,
        accepted_args: set[str],
        supports_var_kwargs: bool,
        route_name: str,
    ) -> str:
        for candidate in ("symbol", "stock", "code", "ts_code"):
            if self._supports_arg(
                candidate,
                accepted_args=accepted_args,
                supports_var_kwargs=supports_var_kwargs,
            ):
                return candidate
        raise RuntimeError(
            "AKShare capital-flow route does not accept a symbol/code argument: "
            f"{route_name}"
        )

    def _payload_to_rows(
        self,
        *,
        payload: Any,
        route_name: str,
    ) -> list[Mapping[str, Any]]:
        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "AKShare A-share capital-flow payload must be DataFrame-like or "
                f"list[Mapping], got {type(payload).__name__}, route={route_name}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "AKShare A-share capital-flow payload row must be mapping. "
                    f"route={route_name}, idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _pick(
        self,
        row: Mapping[str, Any],
        row_idx: int,
        *keys: str,
    ) -> Any:
        for key in keys:
            if key in row:
                return row[key]
        raise ValueError(
            "Missing required source field in capital-flow row "
            f"{row_idx}: one of {keys!r}."
        )

    def _pick_optional(self, row: Mapping[str, Any], *keys: str) -> Any | None:
        for key in keys:
            if key not in row:
                continue
            value = row[key]
            if self._is_missing_value(value):
                return None
            return value
        return None

    def _normalize_code_fragment(self, value: Any) -> str:
        if isinstance(value, str):
            stripped = value.strip().upper()
            if stripped.isdigit() and len(stripped) == 6:
                return stripped
            if "." in stripped:
                head, tail = stripped.split(".", 1)
                if head.isdigit() and len(head) == 6:
                    return head
                if tail.isdigit() and len(tail) == 6:
                    return tail
            if stripped.startswith(("SH", "SZ", "BJ")) and len(stripped) == 8:
                code = stripped[2:]
                if code.isdigit():
                    return code
                return ""
            return ""
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            candidate = str(int(value))
            if len(candidate) == 6 and candidate.isdigit():
                return candidate
        return ""

    def _to_float(
        self,
        value: Any,
        *,
        field_name: str,
        default_unit_scale: float,
    ) -> float:
        if isinstance(value, bool):
            raise ValueError(f"Invalid {field_name} value type: bool")
        if isinstance(value, (int, float)):
            numeric = float(value) * default_unit_scale
            if not math.isfinite(numeric):
                raise ValueError(f"Invalid {field_name} value: {value!r}")
            return numeric
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError(f"Invalid {field_name} value: empty string")
            if stripped.lower() in {"nan", "nat", "none", "null"}:
                raise ValueError(f"Invalid {field_name} value: {value!r}")

            normalized = stripped.replace(",", "")
            unit_scale = default_unit_scale
            unit_specs = (
                ("亿元", 100000000.0),
                ("亿", 100000000.0),
                ("万元", 10000.0),
                ("万", 10000.0),
                ("元", 1.0),
                ("%", 1.0),
            )
            for unit_suffix, factor in unit_specs:
                if normalized.endswith(unit_suffix):
                    normalized = normalized[: -len(unit_suffix)]
                    unit_scale *= factor
                    break

            normalized = normalized.strip()
            if normalized == "":
                raise ValueError(f"Invalid {field_name} value: {value!r}")
            try:
                numeric = float(normalized) * unit_scale
            except ValueError as exc:
                raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
            if not math.isfinite(numeric):
                raise ValueError(f"Invalid {field_name} value: {value!r}")
            return numeric

        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _normalize_trade_date(self, value: Any, *, field_name: str) -> date:
        if self._is_missing_value(value):
            raise ValueError(f"Invalid {field_name} value: missing")
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError(f"Invalid {field_name} value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                return date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
            try:
                return date.fromisoformat(stripped)
            except ValueError:
                try:
                    return datetime.fromisoformat(stripped).date()
                except ValueError as exc:
                    raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _normalize_source_ts(self, value: Any) -> str:
        if self._is_missing_value(value):
            raise ValueError("Invalid source_ts value: missing")
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time()).isoformat()
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return datetime.fromtimestamp(float(value), tz=timezone.utc).isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError("Invalid source_ts value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                parsed_date = date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
                return datetime.combine(parsed_date, datetime.min.time()).isoformat()
            try:
                return datetime.fromisoformat(stripped).isoformat()
            except ValueError:
                try:
                    parsed_date = date.fromisoformat(stripped)
                    return datetime.combine(parsed_date, datetime.min.time()).isoformat()
                except ValueError as exc:
                    raise ValueError(f"Invalid source_ts value: {value!r}") from exc
        raise ValueError(f"Invalid source_ts value type: {type(value).__name__}")

    def _require_single_a_share_symbol(
        self,
        symbols: list[str] | None,
    ) -> tuple[str, str, str]:
        if symbols is None or len(symbols) == 0:
            raise ValueError(
                "AkshareAShareCapitalFlowSnapshotAdapter requires exactly one symbol, got none."
            )
        if len(symbols) != 1:
            raise ValueError(
                "AkshareAShareCapitalFlowSnapshotAdapter currently supports exactly one symbol."
            )

        raw_value = symbols[0]
        if not isinstance(raw_value, str) or raw_value.strip() == "":
            raise ValueError("Symbol must be a non-empty string.")
        return self._normalize_requested_a_share_symbol(raw_value)

    def _normalize_requested_a_share_symbol(self, value: str) -> tuple[str, str, str]:
        normalized = value.strip().upper()

        if normalized.startswith(("SH", "SZ", "BJ")) and len(normalized) == 8:
            market = normalized[:2]
            code = normalized[2:]
            if not code.isdigit() or len(code) != 6:
                raise ValueError(f"Invalid symbol filter code: {value!r}")
            inferred = self._infer_market_from_code(code)
            if inferred != market:
                raise ValueError(
                    "Invalid symbol filter market-code combination: "
                    f"{value!r}."
                )
            return f"{code}.{market}", code, market

        if "." in normalized:
            code, market = normalized.split(".", 1)
            if not code.isdigit() or len(code) != 6:
                raise ValueError(
                    f"Invalid symbol filter format: {value!r}. Expected 6-digit code."
                )
            if market not in {"SH", "SZ", "BJ"}:
                raise ValueError(
                    f"Invalid symbol filter market suffix: {market!r}. "
                    "Expected SH/SZ/BJ for A-share stock symbols."
                )
            inferred = self._infer_market_from_code(code)
            if inferred != market:
                raise ValueError(
                    "Invalid symbol filter market-code combination: "
                    f"{value!r}."
                )
            return f"{code}.{market}", code, market

        if normalized.isdigit() and len(normalized) == 6:
            market = self._infer_market_from_code(normalized)
            return f"{normalized}.{market}", normalized, market

        raise ValueError(
            "Unsupported symbol format for A-share capital-flow snapshot adapter: "
            f"{value!r}. Expected canonical like '600000.SH' or raw 6-digit stock code."
        )

    def _infer_market_from_code(self, code: str) -> str:
        if code.startswith("6"):
            return "SH"
        if code.startswith(("0", "3")):
            if code.startswith("399"):
                raise ValueError(
                    "Index symbol is unsupported for A-share capital-flow snapshot adapter: "
                    f"{code!r}."
                )
            return "SZ"
        if code.startswith(("4", "8", "9")):
            return "BJ"
        if code.startswith("5"):
            raise ValueError(
                "ETF or fund symbol is unsupported for A-share capital-flow snapshot adapter: "
                f"{code!r}."
            )
        raise ValueError(
            "Invalid A-share stock code prefix for capital-flow snapshot adapter: "
            f"{code!r}."
        )

    def _filter_records_by_date(
        self,
        *,
        records: Sequence[Mapping[str, Any]],
        start_date: date | None,
        end_date: date | None,
    ) -> list[dict[str, Any]]:
        filtered: list[dict[str, Any]] = []
        for record in records:
            trade_date = date.fromisoformat(str(record["trade_date"]))
            if start_date is not None and trade_date < start_date:
                continue
            if end_date is not None and trade_date > end_date:
                continue
            filtered.append(dict(record))
        return filtered

    def _to_akshare_date(self, value: date) -> str:
        return value.strftime("%Y%m%d")

    def _is_missing_value(self, value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, str) and value.strip().lower() in {"", "nan", "nat", "none", "null"}:
            return True
        if type(value).__name__ == "NaTType":
            return True
        try:
            if value != value:  # NaN / NaT
                return True
        except Exception:
            pass
        return False

    def _is_capital_flow_route_unavailable(
        self,
        *,
        route_name: str,
        exc: BaseException,
    ) -> bool:
        if self._is_capital_flow_network_unavailable(exc):
            return True
        if (
            route_name == self._NORTHBOUND_ROUTE_NAME
            and self._is_northbound_route_shape_unavailable(exc)
        ):
            return True
        return False

    def _is_northbound_route_shape_unavailable(self, exc: BaseException) -> bool:
        seen: set[int] = set()
        current: BaseException | None = exc
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            if isinstance(current, KeyError):
                message = str(current).lower()
                if any(token in message for token in {"result", "data"}):
                    return True
            if current.__cause__ is not None:
                current = current.__cause__
                continue
            current = current.__context__
        return False

    def _is_capital_flow_network_unavailable(self, exc: BaseException) -> bool:
        network_exception_names = {
            "ProxyError",
            "ConnectionError",
            "ConnectTimeout",
            "ReadTimeout",
            "Timeout",
            "MaxRetryError",
            "NewConnectionError",
            "NameResolutionError",
            "SSLError",
        }
        network_message_tokens = (
            "proxy",
            "timed out",
            "timeout",
            "name resolution",
            "temporary failure in name resolution",
            "failed to establish a new connection",
            "max retries exceeded",
            "network is unreachable",
            "connection refused",
            "no route to host",
            "connection reset",
            "dns",
            "eastmoney",
            "push2his.eastmoney.com",
            "push2.eastmoney.com",
            "datacenter.eastmoney.com",
            "datacenter-web.eastmoney.com",
            "securities/api/data/get",
            "rpt_fundflow_secucode",
            "stock_individual_fund_flow",
            "datacenter_securities_fundflow_snapshot",
            "stock_zh_a_hist",
            "stock_hsgt_individual_em",
        )
        generic_message_tokens = (
            "proxy",
            "timed out",
            "timeout",
            "name resolution",
            "temporary failure in name resolution",
            "failed to establish a new connection",
            "max retries exceeded",
            "network is unreachable",
            "connection refused",
            "no route to host",
            "connection reset",
            "dns",
            "eastmoney",
            "push2his.eastmoney.com",
            "push2.eastmoney.com",
            "datacenter.eastmoney.com",
            "datacenter-web.eastmoney.com",
            "securities/api/data/get",
            "rpt_fundflow_secucode",
        )

        seen: set[int] = set()
        current: BaseException | None = exc
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            name = type(current).__name__
            module = type(current).__module__
            message = str(current).lower()

            if name in network_exception_names:
                return True
            if module.startswith(("requests", "urllib3")) and any(
                token in message for token in network_message_tokens
            ):
                return True
            if any(token in message for token in generic_message_tokens):
                return True
            if isinstance(current, (socket.timeout, TimeoutError, ConnectionError)):
                return True
            if isinstance(current, OSError):
                if current.errno in {101, 110, 111, 113}:
                    return True
                if any(token in message for token in generic_message_tokens):
                    return True

            if current.__cause__ is not None:
                current = current.__cause__
                continue
            current = current.__context__
        return False


class AkshareHKInstrumentMasterAdapter:
    """Narrow AKShare adapter for one-symbol Hong Kong stock instrument master."""

    source_name = AKSHARE_SOURCE_ID
    source_display_name = AKSHARE_SOURCE_NAME
    _ROUTE_NAME = "stock_hk_security_profile_em"

    def __init__(
        self,
        *,
        fetch_hk_security_profile: Callable[..., Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self._fetch_hk_security_profile = fetch_hk_security_profile
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        del start_date, end_date
        if dataset != DatasetName.INSTRUMENT_MASTER:
            raise ValueError(
                "Unsupported dataset for AkshareHKInstrumentMasterAdapter: "
                f"{dataset.value}"
            )

        canonical_symbol, raw_symbol = self._require_single_hk_stock_symbol(symbols)
        rows = self._fetch_rows_for_symbol(raw_symbol)
        return self._normalize_instrument_rows(
            rows=rows,
            dataset=dataset,
            requested_symbol=canonical_symbol,
        )

    def _resolve_fetch_hk_security_profile(self) -> Callable[..., Any]:
        if self._fetch_hk_security_profile is not None:
            return self._fetch_hk_security_profile

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare HK instrument-master fetch."
            ) from exc

        if hasattr(ak, self._ROUTE_NAME):
            return getattr(ak, self._ROUTE_NAME)
        raise RuntimeError(
            "AKShare HK instrument-master function is unavailable: "
            f"{self._ROUTE_NAME}"
        )

    def _fetch_rows_for_symbol(self, symbol: str) -> list[Mapping[str, Any]]:
        fetch_fn = self._resolve_fetch_hk_security_profile()
        try:
            payload = fetch_fn(symbol=symbol)
        except Exception as exc:
            if self._is_hk_instrument_master_network_unavailable(exc):
                raise RuntimeError(
                    "AKShare HK instrument-master route unavailable: "
                    f"{self._ROUTE_NAME} -> {type(exc).__name__}: {exc}"
                ) from exc
            raise
        return self._payload_to_rows(payload=payload)

    def _payload_to_rows(self, *, payload: Any) -> list[Mapping[str, Any]]:
        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "AKShare HK instrument-master payload must be DataFrame-like "
                f"or list[Mapping], got {type(payload).__name__}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "AKShare HK instrument-master payload row must be mapping. "
                    f"idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _normalize_instrument_rows(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        dataset: DatasetName,
        requested_symbol: str,
    ) -> list[dict[str, Any]]:
        profile_rows = self._rows_to_profile_rows(rows=rows)
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version
        normalized_by_symbol: dict[str, dict[str, Any]] = {}

        for row_idx, row in enumerate(profile_rows):
            symbol, raw_symbol = self._normalize_source_symbol(
                self._pick(row, row_idx, "证券代码", "symbol", "代码")
            )
            if symbol != requested_symbol:
                raise ValueError(
                    "AKShare HK instrument-master source returned unexpected symbol: "
                    f"requested={requested_symbol!r}, returned={symbol!r}."
                )

            security_type_value = self._pick_optional(row, "证券类型", "security_type", "类型")
            if security_type_value is not None and not self._is_stock_security_type(security_type_value):
                continue

            name = self._normalize_required_text(
                self._pick(row, row_idx, "证券简称", "name", "简称"),
                field_name="name",
            )
            exchange_value = self._normalize_required_text(
                self._pick(row, row_idx, "交易所", "exchange"),
                field_name="exchange",
            )
            if not self._is_hk_exchange(exchange_value):
                raise ValueError(
                    "Invalid exchange value for HK stock instrument slice: "
                    f"{exchange_value!r}."
                )
            list_date = self._normalize_date(
                self._pick(row, row_idx, "上市日期", "list_date"),
                field_name="list_date",
            )

            record: dict[str, Any] = {
                "symbol": symbol,
                "raw_symbol": raw_symbol,
                "name": name,
                "market": "HK",
                "asset_type": "stock",
                "currency": "HKD",
                "exchange": "HKEX",
                "list_date": list_date,
                "delist_date": "9999-12-31",
                "is_active": True,
                "source": AKSHARE_SOURCE_ID,
                "ingested_at": ingested_at,
                "schema_version": schema_version,
            }

            source_ts = self._pick_optional(row, "source_ts", "更新时间", "update_time")
            if source_ts is not None:
                record["source_ts"] = self._normalize_source_ts(source_ts)

            existing = normalized_by_symbol.get(symbol)
            if existing is None:
                normalized_by_symbol[symbol] = record
                continue
            if self._is_conflicting_duplicate(existing=existing, candidate=record):
                raise ValueError(
                    "Conflicting duplicate HK instrument row detected: "
                    f"symbol={symbol!r}."
                )
            normalized_by_symbol[symbol] = self._select_preferred_duplicate_record(
                existing=existing,
                candidate=record,
            )

        if requested_symbol not in normalized_by_symbol:
            raise ValueError(
                "No stock-like HK instrument profile row found for requested symbol: "
                f"{requested_symbol!r}."
            )
        return [normalized_by_symbol[requested_symbol]]

    def _rows_to_profile_rows(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
    ) -> list[Mapping[str, Any]]:
        if len(rows) == 0:
            raise ValueError("AKShare HK instrument-master payload is empty.")

        if self._looks_like_item_value_rows(rows):
            return [self._collapse_item_value_rows(rows=rows)]
        return list(rows)

    def _looks_like_item_value_rows(self, rows: Sequence[Mapping[str, Any]]) -> bool:
        item_keys = ("项目", "item", "Item", "字段", "key", "名称")
        value_keys = ("值", "value", "Value", "内容", "数据", "field_value")

        for row in rows:
            if self._first_existing_key(row, item_keys) is None:
                return False
            if self._first_existing_key(row, value_keys) is None:
                return False
        return True

    def _collapse_item_value_rows(self, *, rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        item_keys = ("项目", "item", "Item", "字段", "key", "名称")
        value_keys = ("值", "value", "Value", "内容", "数据", "field_value")

        collapsed: dict[str, Any] = {}
        for row_idx, row in enumerate(rows):
            item_key = self._first_existing_key(row, item_keys)
            value_key = self._first_existing_key(row, value_keys)
            if item_key is None or value_key is None:
                raise ValueError(
                    "Malformed HK instrument item/value row: "
                    f"idx={row_idx}, row={row!r}."
                )

            item_name = row[item_key]
            if not isinstance(item_name, str) or item_name.strip() == "":
                raise ValueError(
                    "Invalid HK instrument item key value in item/value payload: "
                    f"idx={row_idx}, value={item_name!r}."
                )
            normalized_key = item_name.strip()
            value = row[value_key]

            if normalized_key not in collapsed:
                collapsed[normalized_key] = value
                continue
            if collapsed[normalized_key] != value:
                raise ValueError(
                    "Conflicting HK instrument item/value rows detected for key: "
                    f"{normalized_key!r}."
                )
        return collapsed

    def _first_existing_key(
        self,
        row: Mapping[str, Any],
        keys: Sequence[str],
    ) -> str | None:
        for key in keys:
            if key in row:
                return key
        return None

    def _require_single_hk_stock_symbol(
        self,
        symbols: list[str] | None,
    ) -> tuple[str, str]:
        if symbols is None or len(symbols) == 0:
            raise ValueError(
                "AkshareHKInstrumentMasterAdapter requires exactly one symbol, got none."
            )
        if len(symbols) != 1:
            raise ValueError(
                "AkshareHKInstrumentMasterAdapter currently supports exactly one symbol."
            )

        value = symbols[0]
        if not isinstance(value, str):
            raise ValueError(
                "Invalid symbol value type for HK instrument adapter: "
                f"{type(value).__name__}"
            )
        normalized = value.strip().upper()
        if normalized == "":
            raise ValueError("Invalid symbol value for HK instrument adapter: empty string.")

        symbol, raw_symbol = self._normalize_source_symbol(normalized)
        return symbol, raw_symbol

    def _normalize_source_symbol(self, value: Any) -> tuple[str, str]:
        if isinstance(value, bool):
            raise ValueError(f"Invalid HK symbol value type: bool ({value!r})")

        text_value: str
        if isinstance(value, int):
            text_value = f"{value:05d}"
        elif isinstance(value, float):
            if not value.is_integer():
                raise ValueError(f"Invalid HK symbol value: {value!r}")
            text_value = f"{int(value):05d}"
        elif isinstance(value, str):
            text_value = value.strip().upper()
        else:
            raise ValueError(f"Invalid HK symbol value type: {type(value).__name__}")

        if text_value == "":
            raise ValueError("Invalid HK symbol value: empty string")

        if "." in text_value:
            code, market = text_value.split(".", 1)
            if market != "HK":
                raise ValueError(
                    "Unsupported symbol market suffix for HK instrument adapter: "
                    f"{market!r}. Expected '.HK'."
                )
        else:
            code = text_value

        if not code.isdigit() or len(code) != 5:
            raise ValueError(
                f"Unsupported HK symbol format: {value!r}. "
                "Expected canonical like '00700.HK' or raw 5-digit code."
            )

        return f"{code}.HK", code

    def _pick(
        self,
        row: Mapping[str, Any],
        row_idx: int,
        *keys: str,
    ) -> Any:
        for key in keys:
            if key in row:
                value = row[key]
                if self._is_missing_value(value):
                    continue
                return value
        raise ValueError(
            "Missing required source field in HK instrument row "
            f"{row_idx}: one of {keys!r}"
        )

    def _pick_optional(
        self,
        row: Mapping[str, Any],
        *keys: str,
    ) -> Any | None:
        for key in keys:
            if key not in row:
                continue
            value = row[key]
            if self._is_missing_value(value):
                return None
            return value
        return None

    def _normalize_required_text(self, value: Any, *, field_name: str) -> str:
        if not isinstance(value, str):
            raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")
        normalized = value.strip()
        if normalized == "":
            raise ValueError(f"Invalid {field_name} value: empty string")
        return normalized

    def _normalize_date(self, value: Any, *, field_name: str) -> str:
        if self._is_missing_value(value):
            raise ValueError(f"Invalid {field_name} value: missing")
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError(f"Invalid {field_name} value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                return date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                ).isoformat()
            try:
                return datetime.fromisoformat(stripped).date().isoformat()
            except ValueError:
                pass
            try:
                return date.fromisoformat(stripped).isoformat()
            except ValueError as exc:
                raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _normalize_source_ts(self, value: Any) -> str:
        if self._is_missing_value(value):
            raise ValueError("Invalid source_ts value: missing")
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time()).isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError("Invalid source_ts value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                parsed_date = date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
                return datetime.combine(parsed_date, datetime.min.time()).isoformat()
            try:
                return datetime.fromisoformat(stripped).isoformat()
            except ValueError:
                try:
                    parsed_date = date.fromisoformat(stripped)
                    return datetime.combine(parsed_date, datetime.min.time()).isoformat()
                except ValueError as exc:
                    raise ValueError(f"Invalid source_ts value: {value!r}") from exc
        raise ValueError(f"Invalid source_ts value type: {type(value).__name__}")

    def _is_missing_value(self, value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, str):
            return value.strip().lower() in {"", "nan", "nat", "none", "null"}
        if type(value).__name__ == "NaTType":
            return True
        try:
            if value != value:
                return True
        except Exception:
            pass
        return False

    def _is_hk_exchange(self, value: str) -> bool:
        normalized = value.strip().lower()
        return normalized in {"hkex", "港交所", "香港交易所", "香港联合交易所"}

    def _is_stock_security_type(self, value: Any) -> bool:
        if not isinstance(value, str):
            raise ValueError(
                "Invalid security_type value type for HK instrument adapter: "
                f"{type(value).__name__}"
            )
        normalized = value.strip().lower().replace(" ", "")
        if normalized == "":
            raise ValueError("Invalid security_type value for HK instrument adapter: empty string")

        stock_tokens = (
            "普通股",
            "股票",
            "stock",
            "equity",
            "h股",
            "非h股",
            "主板",
            "创业板",
            "mainboard",
            "gem",
        )
        non_stock_tokens = (
            "etf",
            "fund",
            "基金",
            "债",
            "bond",
            "warrant",
            "窝轮",
            "权证",
            "牛熊证",
            "reit",
            "trust",
            "指数",
            "index",
            "期权",
            "option",
        )

        if any(token in normalized for token in non_stock_tokens):
            return False
        if any(token in normalized for token in stock_tokens):
            return True
        return False

    def _is_conflicting_duplicate(
        self,
        *,
        existing: Mapping[str, Any],
        candidate: Mapping[str, Any],
    ) -> bool:
        comparable_fields = (
            "symbol",
            "raw_symbol",
            "name",
            "market",
            "asset_type",
            "currency",
            "exchange",
            "list_date",
            "delist_date",
            "is_active",
            "source",
        )
        return any(existing.get(field) != candidate.get(field) for field in comparable_fields)

    def _select_preferred_duplicate_record(
        self,
        *,
        existing: dict[str, Any],
        candidate: dict[str, Any],
    ) -> dict[str, Any]:
        existing_source_ts = existing.get("source_ts")
        candidate_source_ts = candidate.get("source_ts")

        if existing_source_ts is None and candidate_source_ts is not None:
            return candidate
        if existing_source_ts is not None and candidate_source_ts is None:
            return existing
        if existing_source_ts is None and candidate_source_ts is None:
            return existing
        if not isinstance(existing_source_ts, str) or not isinstance(candidate_source_ts, str):
            return existing
        if candidate_source_ts > existing_source_ts:
            return candidate
        return existing

    def _is_hk_instrument_master_network_unavailable(self, exc: BaseException) -> bool:
        network_exception_names = {
            "ProxyError",
            "ConnectionError",
            "ConnectTimeout",
            "ReadTimeout",
            "Timeout",
            "MaxRetryError",
            "NewConnectionError",
            "NameResolutionError",
            "SSLError",
        }
        network_message_tokens = (
            "proxy",
            "timed out",
            "timeout",
            "name resolution",
            "temporary failure in name resolution",
            "failed to establish a new connection",
            "max retries exceeded",
            "network is unreachable",
            "connection refused",
            "no route to host",
            "connection reset",
            "dns",
            "eastmoney",
            "hkf10",
            "emweb.securities.eastmoney.com",
            "stock_hk_security_profile_em",
        )

        seen: set[int] = set()
        current: BaseException | None = exc
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            name = type(current).__name__
            module = type(current).__module__
            message = str(current).lower()

            if name in network_exception_names:
                return True
            if module.startswith(("requests", "urllib3")) and any(
                token in message for token in network_message_tokens
            ):
                return True
            if any(token in message for token in network_message_tokens):
                return True
            if isinstance(current, (socket.timeout, TimeoutError, ConnectionError)):
                return True
            if isinstance(current, OSError):
                if current.errno in {101, 110, 111, 113}:
                    return True
                if any(token in message for token in network_message_tokens):
                    return True

            if current.__cause__ is not None:
                current = current.__cause__
                continue
            current = current.__context__
        return False


class AkshareHKCorporateActionsAdapter:
    """Narrow AKShare adapter for one-symbol HK dividend corporate actions."""

    source_name = AKSHARE_SOURCE_ID
    source_display_name = AKSHARE_SOURCE_NAME
    _PRIMARY_ROUTE_NAME = "stock_hk_dividend_payout_em"
    _FALLBACK_ROUTE_NAME = "stock_hk_fhpx_detail_ths"

    def __init__(
        self,
        *,
        fetch_hk_dividend_payout: Callable[..., Any] | None = None,
        fetch_hk_fhpx_detail: Callable[..., Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self._fetch_hk_dividend_payout = fetch_hk_dividend_payout
        self._fetch_hk_fhpx_detail = fetch_hk_fhpx_detail
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if dataset != DatasetName.CORPORATE_ACTIONS:
            raise ValueError(
                "Unsupported dataset for AkshareHKCorporateActionsAdapter: "
                f"{dataset.value}"
            )

        symbol, raw_symbol = self._require_single_hk_symbol(symbols)
        rows = self._fetch_rows_for_symbol(raw_symbol)
        records = self._normalize_corporate_action_rows(
            rows=rows,
            dataset=dataset,
            symbol=symbol,
        )
        return self._filter_records_by_date(
            records=records,
            start_date=start_date,
            end_date=end_date,
        )

    def _resolve_fetch_hk_dividend_payout(self) -> Callable[..., Any]:
        if self._fetch_hk_dividend_payout is not None:
            return self._fetch_hk_dividend_payout

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare HK corporate-actions fetch."
            ) from exc

        if hasattr(ak, self._PRIMARY_ROUTE_NAME):
            return getattr(ak, self._PRIMARY_ROUTE_NAME)
        raise RuntimeError(
            "AKShare HK corporate-actions primary function is unavailable: "
            f"{self._PRIMARY_ROUTE_NAME}"
        )

    def _resolve_fetch_hk_fhpx_detail(self) -> Callable[..., Any] | None:
        if self._fetch_hk_fhpx_detail is not None:
            return self._fetch_hk_fhpx_detail

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception:  # pragma: no cover - exercised by live/dependency env
            return None

        if hasattr(ak, self._FALLBACK_ROUTE_NAME):
            return getattr(ak, self._FALLBACK_ROUTE_NAME)
        return None

    def _fetch_rows_for_symbol(self, raw_symbol: str) -> list[Mapping[str, Any]]:
        primary_fetch = self._resolve_fetch_hk_dividend_payout()
        try:
            payload = primary_fetch(symbol=raw_symbol)
        except Exception as primary_exc:
            if not self._is_hk_corporate_actions_network_unavailable(primary_exc):
                raise

            fallback_fetch = self._resolve_fetch_hk_fhpx_detail()
            if fallback_fetch is None:
                raise RuntimeError(
                    "AKShare HK corporate-actions route unavailable: "
                    f"primary={self._PRIMARY_ROUTE_NAME} -> {type(primary_exc).__name__}: {primary_exc}; "
                    "fallback route is unavailable in current akshare runtime."
                ) from primary_exc

            fallback_symbol = self._to_fallback_symbol(raw_symbol)
            try:
                fallback_payload = fallback_fetch(symbol=fallback_symbol)
            except Exception as fallback_exc:
                if self._is_hk_corporate_actions_network_unavailable(fallback_exc):
                    raise RuntimeError(
                        "AKShare HK corporate-actions routes unavailable: "
                        f"primary={self._PRIMARY_ROUTE_NAME} -> {type(primary_exc).__name__}: {primary_exc}; "
                        f"fallback={self._FALLBACK_ROUTE_NAME} -> {type(fallback_exc).__name__}: {fallback_exc}"
                    ) from fallback_exc
                raise
            return self._payload_to_rows(payload=fallback_payload, route_name=self._FALLBACK_ROUTE_NAME)
        return self._payload_to_rows(payload=payload, route_name=self._PRIMARY_ROUTE_NAME)

    def _payload_to_rows(self, *, payload: Any, route_name: str) -> list[Mapping[str, Any]]:
        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "AKShare HK corporate-actions payload must be DataFrame-like "
                f"or list[Mapping], got {type(payload).__name__}, route={route_name}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "AKShare HK corporate-actions payload row must be mapping. "
                    f"route={route_name}, idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _require_single_hk_symbol(self, symbols: list[str] | None) -> tuple[str, str]:
        if symbols is None or len(symbols) == 0:
            raise ValueError(
                "AkshareHKCorporateActionsAdapter requires exactly one symbol, got none."
            )
        if len(symbols) != 1:
            raise ValueError(
                "AkshareHKCorporateActionsAdapter currently supports exactly one symbol."
            )

        raw_value = symbols[0]
        if not isinstance(raw_value, str):
            raise ValueError(
                "Invalid symbol value type for HK corporate-actions adapter: "
                f"{type(raw_value).__name__}"
            )

        value = raw_value.strip().upper()
        if value == "":
            raise ValueError("Invalid symbol value for HK corporate-actions adapter: empty string.")
        return self._normalize_source_symbol(value)

    def _normalize_source_symbol(self, value: Any) -> tuple[str, str]:
        if isinstance(value, bool):
            raise ValueError(f"Invalid HK symbol value type: bool ({value!r})")

        text_value: str
        if isinstance(value, int):
            text_value = f"{value:05d}"
        elif isinstance(value, float):
            if not value.is_integer():
                raise ValueError(f"Invalid HK symbol value: {value!r}")
            text_value = f"{int(value):05d}"
        elif isinstance(value, str):
            text_value = value.strip().upper()
        else:
            raise ValueError(f"Invalid HK symbol value type: {type(value).__name__}")

        if text_value == "":
            raise ValueError("Invalid HK symbol value: empty string")

        if "." in text_value:
            code, market = text_value.split(".", 1)
            if market != "HK":
                raise ValueError(
                    "Unsupported symbol market suffix for HK corporate-actions adapter: "
                    f"{market!r}. Expected '.HK'."
                )
        else:
            code = text_value

        if not code.isdigit() or len(code) != 5:
            raise ValueError(
                f"Unsupported HK symbol format: {value!r}. "
                "Expected canonical like '00700.HK' or raw 5-digit stock code."
            )

        return f"{code}.HK", code

    def _to_fallback_symbol(self, raw_symbol: str) -> str:
        fallback = raw_symbol.lstrip("0")
        if fallback == "":
            return "0"
        if len(fallback) >= 4:
            return fallback
        return fallback.zfill(4)

    def _normalize_corporate_action_rows(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        dataset: DatasetName,
        symbol: str,
    ) -> list[dict[str, Any]]:
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version
        normalized_by_identity: dict[tuple[str, str, str, str], dict[str, Any]] = {}

        for row_idx, row in enumerate(rows):
            event_date = self._resolve_event_date(row=row, row_idx=row_idx)
            value = self._build_value_object(row=row, row_idx=row_idx)
            raw_payload_ref = self._build_raw_payload_ref(
                symbol=symbol,
                event_type="dividend",
                event_date=event_date,
                row=row,
            )

            record: dict[str, Any] = {
                "symbol": symbol,
                "market": "HK",
                "event_date": event_date,
                "event_type": "dividend",
                "value": value,
                "raw_payload_ref": raw_payload_ref,
                "source": AKSHARE_SOURCE_ID,
                "ingested_at": ingested_at,
                "schema_version": schema_version,
            }

            source_ts = self._pick_optional(
                row,
                "最新公告日期",
                "公告日期",
                "source_ts",
                "update_time",
            )
            if source_ts is not None:
                record["source_ts"] = self._normalize_source_ts(source_ts)

            identity = (
                str(record["symbol"]),
                str(record["event_type"]),
                str(record["event_date"]),
                str(record["raw_payload_ref"]),
            )
            existing = normalized_by_identity.get(identity)
            if existing is None:
                normalized_by_identity[identity] = record
                continue
            if self._is_conflicting_duplicate(existing=existing, candidate=record):
                raise ValueError(
                    "Conflicting duplicate HK corporate-actions row detected: "
                    f"identity={identity!r}."
                )
            normalized_by_identity[identity] = self._select_preferred_duplicate_record(
                existing=existing,
                candidate=record,
            )

        ordered = list(normalized_by_identity.values())
        ordered.sort(key=lambda record: (str(record["event_date"]), str(record["raw_payload_ref"])))
        return ordered

    def _resolve_event_date(
        self,
        *,
        row: Mapping[str, Any],
        row_idx: int,
    ) -> str:
        candidate_groups: tuple[tuple[str, ...], ...] = (
            ("除净日", "除權日", "除息日", "ex_date", "ex_dividend_date"),
            ("最新公告日期", "公告日期", "announcement_date"),
            ("发放日", "派息日", "payout_date"),
        )

        for keys in candidate_groups:
            for key in keys:
                if key not in row:
                    continue
                raw_value = row[key]
                if self._is_missing_value(raw_value):
                    continue
                return self._normalize_date(raw_value, field_name="event_date")

        raise ValueError(
            "Missing required source field in HK corporate-actions row "
            f"{row_idx}: one of ('除净日', '最新公告日期', '公告日期', '发放日', '派息日')."
        )

    def _build_value_object(
        self,
        *,
        row: Mapping[str, Any],
        row_idx: int,
    ) -> dict[str, Any]:
        announcement_date = self._normalize_optional_date(
            self._pick_optional(row, "最新公告日期", "公告日期"),
            field_name="announcement_date",
        )
        fiscal_year = self._normalize_optional_text(
            self._pick_optional(row, "财政年度", "财年", "report_period"),
            field_name="fiscal_year",
        )
        distribution_type = self._normalize_optional_text(
            self._pick_optional(row, "分配类型", "类型"),
            field_name="distribution_type",
        )
        plan_text = self._normalize_optional_text(
            self._pick_optional(row, "分红方案", "方案", "plan_text"),
            field_name="plan_text",
        )
        register_book_period = self._build_register_book_period(row=row)
        payout_date = self._normalize_optional_date(
            self._pick_optional(row, "发放日", "派息日"),
            field_name="payout_date",
        )
        progress = self._normalize_optional_text(
            self._pick_optional(row, "进度", "status"),
            field_name="progress",
        )
        scrip_dividend = self._normalize_optional_text(
            self._pick_optional(row, "以股代息", "scrip_dividend"),
            field_name="scrip_dividend",
        )

        value: dict[str, Any] = {}
        if announcement_date is not None:
            value["announcement_date"] = announcement_date
        if fiscal_year is not None:
            value["fiscal_year"] = fiscal_year
        if distribution_type is not None:
            value["distribution_type"] = distribution_type
        if plan_text is not None:
            value["raw_plan_text"] = plan_text
            value["cash_distribution_text"] = plan_text
        if register_book_period is not None:
            value["register_book_period"] = register_book_period
        if payout_date is not None:
            value["payout_date"] = payout_date
        if progress is not None:
            value["progress"] = progress
        if scrip_dividend is not None:
            value["scrip_dividend"] = scrip_dividend

        parsed = self._extract_cash_dividend_from_text(plan_text)
        if parsed is not None:
            value["cash_dividend_per_share"] = parsed["amount"]
            value["cash_currency"] = parsed["currency"]
            value["cash_dividend_unit"] = "per_share"

        if len(value) == 0:
            raise ValueError(
                "Missing required source field in HK corporate-actions row "
                f"{row_idx}: no usable dividend detail fields found."
            )

        try:
            json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Non-serializable structured HK corporate-actions value in row "
                f"{row_idx}."
            ) from exc
        return value

    def _build_register_book_period(self, *, row: Mapping[str, Any]) -> str | None:
        period_text = self._normalize_optional_text(
            self._pick_optional(row, "截至过户日", "过户日期起止日"),
            field_name="register_book_period",
        )
        if period_text is not None:
            return period_text

        start_value = self._pick_optional(row, "过户日期起止日-起始")
        end_value = self._pick_optional(row, "过户日期起止日-截止")
        if start_value is None and end_value is None:
            return None

        start_text = (
            self._normalize_date(start_value, field_name="register_book_start")
            if start_value is not None
            else ""
        )
        end_text = (
            self._normalize_date(end_value, field_name="register_book_end")
            if end_value is not None
            else ""
        )
        if start_text != "" and end_text != "":
            return f"{start_text}~{end_text}"
        return start_text or end_text

    def _extract_cash_dividend_from_text(self, plan_text: str | None) -> dict[str, Any] | None:
        if plan_text is None:
            return None
        text = plan_text.strip()
        if text == "":
            return None

        patterns: tuple[tuple[re.Pattern[str], str], ...] = (
            (
                re.compile(
                    r"每股(?:派|分派)?(?:港币|港元|hkd)\s*([0-9]+(?:\.[0-9]+)?)\s*(?:元)?",
                    re.IGNORECASE,
                ),
                "HKD",
            ),
            (
                re.compile(
                    r"每股(?:派|分派)?(?:人民币|rmb|cny)\s*([0-9]+(?:\.[0-9]+)?)\s*(?:元)?",
                    re.IGNORECASE,
                ),
                "CNY",
            ),
            (
                re.compile(
                    r"每股(?:派|分派)?(?:美元|usd)\s*([0-9]+(?:\.[0-9]+)?)\s*(?:元)?",
                    re.IGNORECASE,
                ),
                "USD",
            ),
            (
                re.compile(
                    r"每股(?:派|分派)?([0-9]+(?:\.[0-9]+)?)\s*(港币|港元|hkd|人民币|rmb|cny|美元|usd)",
                    re.IGNORECASE,
                ),
                "",
            ),
        )

        for pattern, fixed_currency in patterns:
            match = pattern.search(text)
            if match is None:
                continue

            amount_text = match.group(1).strip().replace(",", "")
            try:
                amount = float(amount_text)
            except ValueError as exc:
                raise ValueError(
                    "Invalid numeric extraction from HK dividend plan text: "
                    f"{plan_text!r}."
                ) from exc

            if not math.isfinite(amount):
                raise ValueError(
                    "Invalid numeric extraction from HK dividend plan text: "
                    f"{plan_text!r}."
                )

            if fixed_currency != "":
                currency = fixed_currency
            else:
                raw_currency = match.group(2).strip().lower()
                if raw_currency in {"港币", "港元", "hkd"}:
                    currency = "HKD"
                elif raw_currency in {"人民币", "rmb", "cny"}:
                    currency = "CNY"
                elif raw_currency in {"美元", "usd"}:
                    currency = "USD"
                else:
                    return None

            return {"amount": amount, "currency": currency}

        return None

    def _build_raw_payload_ref(
        self,
        *,
        symbol: str,
        event_type: str,
        event_date: str,
        row: Mapping[str, Any],
    ) -> str:
        row_signature = self._stable_row_signature(row)
        digest = hashlib.sha1(row_signature.encode("utf-8")).hexdigest()[:24]
        return f"AKCA|{symbol}|{event_type}|{event_date}|{digest}"

    def _stable_row_signature(self, row: Mapping[str, Any]) -> str:
        sanitized: dict[str, Any] = {}
        for key in sorted(row.keys(), key=lambda item: str(item)):
            key_text = str(key)
            sanitized[key_text] = self._sanitize_for_serialization(
                row[key],
                field_name=f"source_row[{key_text}]",
            )
        try:
            return json.dumps(
                sanitized,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Non-serializable value in HK corporate-actions source row."
            ) from exc

    def _sanitize_for_serialization(self, value: Any, *, field_name: str) -> Any:
        if self._is_missing_value(value):
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            if not math.isfinite(value):
                raise ValueError(
                    f"Invalid non-finite numeric value for {field_name}: {value!r}"
                )
            return float(value)
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, Mapping):
            nested: dict[str, Any] = {}
            for nested_key in sorted(value.keys(), key=lambda item: str(item)):
                nested_name = str(nested_key)
                nested[nested_name] = self._sanitize_for_serialization(
                    value[nested_key],
                    field_name=f"{field_name}.{nested_name}",
                )
            return nested
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            return [
                self._sanitize_for_serialization(item, field_name=field_name)
                for item in value
            ]
        raise ValueError(
            f"Non-serializable value type for {field_name}: {type(value).__name__}"
        )

    def _filter_records_by_date(
        self,
        *,
        records: Sequence[Mapping[str, Any]],
        start_date: date | None,
        end_date: date | None,
    ) -> list[dict[str, Any]]:
        filtered: list[dict[str, Any]] = []
        for record in records:
            event_dt = date.fromisoformat(str(record["event_date"]))
            if start_date is not None and event_dt < start_date:
                continue
            if end_date is not None and event_dt > end_date:
                continue
            filtered.append(dict(record))
        return filtered

    def _pick_optional(self, row: Mapping[str, Any], *keys: str) -> Any | None:
        for key in keys:
            if key not in row:
                continue
            value = row[key]
            if self._is_missing_value(value):
                return None
            return value
        return None

    def _normalize_optional_text(
        self,
        value: Any | None,
        *,
        field_name: str,
    ) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")
        normalized = value.strip()
        if normalized == "":
            return None
        return normalized

    def _normalize_date(self, value: Any, *, field_name: str) -> str:
        if self._is_missing_value(value):
            raise ValueError(f"Invalid {field_name} value: missing")
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError(f"Invalid {field_name} value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                return date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                ).isoformat()
            if "/" in stripped:
                parts = stripped.split("/")
                if len(parts) == 3 and all(part.isdigit() for part in parts):
                    year, month, day = parts
                    try:
                        return date(int(year), int(month), int(day)).isoformat()
                    except ValueError as exc:
                        raise ValueError(
                            f"Invalid {field_name} value: {value!r}"
                        ) from exc
            try:
                return datetime.fromisoformat(stripped).date().isoformat()
            except ValueError:
                pass
            try:
                return date.fromisoformat(stripped).isoformat()
            except ValueError as exc:
                raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _normalize_optional_date(
        self,
        value: Any | None,
        *,
        field_name: str,
    ) -> str | None:
        if value is None:
            return None
        return self._normalize_date(value, field_name=field_name)

    def _normalize_source_ts(self, value: Any) -> str:
        if self._is_missing_value(value):
            raise ValueError("Invalid source_ts value: missing")
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time()).isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError("Invalid source_ts value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                parsed_date = date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
                return datetime.combine(parsed_date, datetime.min.time()).isoformat()
            if "/" in stripped:
                parts = stripped.split("/")
                if len(parts) == 3 and all(part.isdigit() for part in parts):
                    try:
                        parsed_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
                    except ValueError as exc:
                        raise ValueError(f"Invalid source_ts value: {value!r}") from exc
                    return datetime.combine(parsed_date, datetime.min.time()).isoformat()
            try:
                return datetime.fromisoformat(stripped).isoformat()
            except ValueError:
                try:
                    parsed_date = date.fromisoformat(stripped)
                    return datetime.combine(parsed_date, datetime.min.time()).isoformat()
                except ValueError as exc:
                    raise ValueError(f"Invalid source_ts value: {value!r}") from exc
        raise ValueError(f"Invalid source_ts value type: {type(value).__name__}")

    def _is_missing_value(self, value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, str):
            return value.strip().lower() in {"", "nan", "nat", "none", "null", "--"}
        if type(value).__name__ == "NaTType":
            return True
        try:
            if value != value:
                return True
        except Exception:
            pass
        return False

    def _is_conflicting_duplicate(
        self,
        *,
        existing: Mapping[str, Any],
        candidate: Mapping[str, Any],
    ) -> bool:
        comparable_fields = (
            "symbol",
            "market",
            "event_date",
            "event_type",
            "value",
            "raw_payload_ref",
            "source",
        )
        return any(existing.get(field) != candidate.get(field) for field in comparable_fields)

    def _select_preferred_duplicate_record(
        self,
        *,
        existing: dict[str, Any],
        candidate: dict[str, Any],
    ) -> dict[str, Any]:
        existing_source_ts = existing.get("source_ts")
        candidate_source_ts = candidate.get("source_ts")

        if existing_source_ts is None and candidate_source_ts is not None:
            return candidate
        if existing_source_ts is not None and candidate_source_ts is None:
            return existing
        if existing_source_ts is None and candidate_source_ts is None:
            return existing
        if not isinstance(existing_source_ts, str) or not isinstance(candidate_source_ts, str):
            return existing
        if candidate_source_ts > existing_source_ts:
            return candidate
        return existing

    def _is_hk_corporate_actions_network_unavailable(self, exc: BaseException) -> bool:
        network_exception_names = {
            "ProxyError",
            "ConnectionError",
            "ConnectTimeout",
            "ReadTimeout",
            "Timeout",
            "MaxRetryError",
            "NewConnectionError",
            "NameResolutionError",
            "SSLError",
        }
        network_message_tokens = (
            "proxy",
            "timed out",
            "timeout",
            "name resolution",
            "temporary failure in name resolution",
            "failed to establish a new connection",
            "max retries exceeded",
            "network is unreachable",
            "connection refused",
            "no route to host",
            "connection reset",
            "dns",
            "eastmoney",
            "10jqka",
            "stock_hk_dividend_payout_em",
            "stock_hk_fhpx_detail_ths",
            "emweb.securities.eastmoney.com",
            "basic.10jqka.com.cn",
        )

        seen: set[int] = set()
        current: BaseException | None = exc
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            name = type(current).__name__
            module = type(current).__module__
            message = str(current).lower()

            if name in network_exception_names:
                return True
            if module.startswith(("requests", "urllib3")) and any(
                token in message for token in network_message_tokens
            ):
                return True
            if any(token in message for token in network_message_tokens):
                return True
            if isinstance(current, (socket.timeout, TimeoutError, ConnectionError, ssl.SSLError)):
                return True
            if isinstance(current, OSError):
                if current.errno in {101, 104, 110, 111, 113}:
                    return True
                if any(token in message for token in network_message_tokens):
                    return True

            if current.__cause__ is not None:
                current = current.__cause__
                continue
            current = current.__context__
        return False


class AkshareHKValuationSnapshotAdapter:
    """Narrow AKShare adapter for one-symbol HK valuation snapshot."""

    source_name = AKSHARE_SOURCE_ID
    source_display_name = AKSHARE_SOURCE_NAME

    _COMPARISON_ROUTE_NAME = "stock_hk_valuation_comparison_em"
    _ENIU_ROUTE_NAME = "stock_hk_indicator_eniu"
    _OPTIONAL_BAIDU_ROUTE_NAME = "stock_hk_valuation_baidu"
    _BAIDU_ROUTE_PERIOD = "近一年"

    _ENIU_METRIC_SPECS: tuple[tuple[str, str, tuple[str, ...], float], ...] = (
        ("市盈率", "pe_ttm", ("pe", "value"), 1.0),
        ("市净率", "pb", ("pb", "value"), 1.0),
        ("市值", "market_cap", ("market_value", "value"), 100000000.0),
        ("股息率", "dividend_yield", ("dv", "value"), 1.0),
    )

    _BAIDU_REQUIRED_METRIC_SPECS: tuple[tuple[str, str, tuple[str, ...], float], ...] = (
        ("市盈率(TTM)", "pe_ttm", ("value", "指标值"), 1.0),
        ("市净率", "pb", ("value", "指标值"), 1.0),
        ("总市值", "market_cap", ("value", "指标值"), 100000000.0),
    )

    _BAIDU_OPTIONAL_METRIC_SPECS: tuple[tuple[str, str, tuple[str, ...], float], ...] = (
        ("市销率(TTM)", "ps_ttm", ("value", "指标值"), 1.0),
        ("股息率(TTM)", "dividend_yield", ("value", "指标值"), 1.0),
        ("流通市值", "float_market_cap", ("value", "指标值"), 100000000.0),
    )

    def __init__(
        self,
        *,
        fetch_valuation_comparison: Callable[..., Any] | None = None,
        fetch_indicator_eniu: Callable[..., Any] | None = None,
        fetch_valuation_baidu: Callable[..., Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self._fetch_valuation_comparison = fetch_valuation_comparison
        self._fetch_indicator_eniu = fetch_indicator_eniu
        self._fetch_valuation_baidu = fetch_valuation_baidu
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if dataset != DatasetName.VALUATION_SNAPSHOT:
            raise ValueError(
                "Unsupported dataset for AkshareHKValuationSnapshotAdapter: "
                f"{dataset.value}"
            )

        symbol, raw_symbol, eniu_symbol = self._require_single_hk_symbol(symbols)
        metrics, trade_date, source_ts = self._collect_metrics(
            raw_symbol=raw_symbol,
            eniu_symbol=eniu_symbol,
        )
        record = self._build_snapshot_record(
            dataset=dataset,
            symbol=symbol,
            trade_date=trade_date,
            metrics=metrics,
            source_ts=source_ts,
        )
        return self._filter_records_by_date(
            records=[record],
            start_date=start_date,
            end_date=end_date,
        )

    def _collect_metrics(
        self,
        *,
        raw_symbol: str,
        eniu_symbol: str,
    ) -> tuple[dict[str, float], str, str | None]:
        eniu_metrics, eniu_trade_date, eniu_failures = self._fetch_eniu_metrics(
            eniu_symbol=eniu_symbol
        )
        comparison_metrics, comparison_failures = self._fetch_comparison_metrics(
            raw_symbol=raw_symbol
        )
        baidu_metrics, baidu_trade_date, baidu_failures = self._fetch_optional_baidu_metrics(
            raw_symbol=raw_symbol
        )

        route_failures = [*eniu_failures, *comparison_failures, *baidu_failures]
        required_fields = ("pe_ttm", "pb", "market_cap")

        if all(field in eniu_metrics for field in required_fields):
            merged_metrics: dict[str, float] = dict(eniu_metrics)
            if "ps_ttm" not in merged_metrics and "ps_ttm" in comparison_metrics:
                merged_metrics["ps_ttm"] = comparison_metrics["ps_ttm"]
            if "float_market_cap" not in merged_metrics and "float_market_cap" in baidu_metrics:
                merged_metrics["float_market_cap"] = baidu_metrics["float_market_cap"]
            if "dividend_yield" not in merged_metrics and "dividend_yield" in comparison_metrics:
                merged_metrics["dividend_yield"] = comparison_metrics["dividend_yield"]
            if "dividend_yield" not in merged_metrics and "dividend_yield" in baidu_metrics:
                merged_metrics["dividend_yield"] = baidu_metrics["dividend_yield"]
            trade_date = (
                eniu_trade_date
                if eniu_trade_date is not None
                else self._now_fn().date().isoformat()
            )
            return merged_metrics, trade_date, None

        merged_metrics = {}
        merged_metrics.update(comparison_metrics)
        merged_metrics.update(baidu_metrics)
        merged_metrics.update(eniu_metrics)

        missing_required = [
            field for field in required_fields if field not in merged_metrics
        ]
        if missing_required:
            if route_failures:
                evidence = " | ".join(route_failures[:3])
                if len(route_failures) > 3:
                    evidence = f"{evidence} | ... total={len(route_failures)} failures"
                raise RuntimeError(
                    "AKShare HK valuation routes unavailable for required metrics: "
                    f"{evidence}"
                )
            raise ValueError(
                "Missing required valuation metric(s) after bounded HK route merge: "
                f"{missing_required!r}"
            )

        if eniu_trade_date is not None:
            trade_date = eniu_trade_date
        elif baidu_trade_date is not None:
            trade_date = baidu_trade_date
        else:
            trade_date = self._now_fn().date().isoformat()
        return merged_metrics, trade_date, None

    def _build_snapshot_record(
        self,
        *,
        dataset: DatasetName,
        symbol: str,
        trade_date: str,
        metrics: Mapping[str, float],
        source_ts: str | None,
    ) -> dict[str, Any]:
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version

        record: dict[str, Any] = {
            "symbol": symbol,
            "market": "HK",
            "trade_date": trade_date,
            "pe_ttm": metrics["pe_ttm"],
            "pb": metrics["pb"],
            "market_cap": metrics["market_cap"],
            "source": AKSHARE_SOURCE_ID,
            "ingested_at": ingested_at,
            "schema_version": schema_version,
        }

        if "ps_ttm" in metrics:
            record["ps_ttm"] = metrics["ps_ttm"]
        if "dividend_yield" in metrics:
            record["dividend_yield"] = metrics["dividend_yield"]
        if "float_market_cap" in metrics:
            record["float_market_cap"] = metrics["float_market_cap"]
        if source_ts is not None:
            record["source_ts"] = source_ts
        return record

    def _resolve_fetch_valuation_comparison(self) -> Callable[..., Any]:
        if self._fetch_valuation_comparison is not None:
            return self._fetch_valuation_comparison

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare HK valuation snapshot fetch."
            ) from exc

        if hasattr(ak, self._COMPARISON_ROUTE_NAME):
            return getattr(ak, self._COMPARISON_ROUTE_NAME)
        raise RuntimeError(
            "AKShare HK valuation comparison function is unavailable: "
            f"{self._COMPARISON_ROUTE_NAME}"
        )

    def _resolve_fetch_indicator_eniu(self) -> Callable[..., Any]:
        if self._fetch_indicator_eniu is not None:
            return self._fetch_indicator_eniu

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare HK valuation snapshot fetch."
            ) from exc

        if hasattr(ak, self._ENIU_ROUTE_NAME):
            return getattr(ak, self._ENIU_ROUTE_NAME)
        raise RuntimeError(
            "AKShare HK valuation eniu function is unavailable: "
            f"{self._ENIU_ROUTE_NAME}"
        )

    def _resolve_fetch_valuation_baidu(self) -> Callable[..., Any] | None:
        if self._fetch_valuation_baidu is not None:
            return self._fetch_valuation_baidu

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception:  # pragma: no cover - exercised by live/dependency env
            return None

        if hasattr(ak, self._OPTIONAL_BAIDU_ROUTE_NAME):
            return getattr(ak, self._OPTIONAL_BAIDU_ROUTE_NAME)
        return None

    def _fetch_eniu_metrics(
        self,
        *,
        eniu_symbol: str,
    ) -> tuple[dict[str, float], str | None, list[str]]:
        fetch_fn = self._resolve_fetch_indicator_eniu()
        metrics: dict[str, float] = {}
        latest_trade_date: date | None = None
        route_failures: list[str] = []

        for indicator, field_name, value_keys, unit_scale in self._ENIU_METRIC_SPECS:
            try:
                payload = self._call_eniu_route(
                    fetch_fn=fetch_fn,
                    symbol=eniu_symbol,
                    indicator=indicator,
                )
                rows = self._payload_to_rows(
                    payload=payload,
                    route_name=f"{self._ENIU_ROUTE_NAME}(indicator={indicator})",
                )
                trade_date, metric_value = self._extract_latest_metric_point(
                    rows=rows,
                    field_name=field_name,
                    metric_name=indicator,
                    value_keys=value_keys,
                    unit_scale=unit_scale,
                )
            except Exception as exc:
                if self._is_hk_valuation_route_unavailable(
                    route_name=self._ENIU_ROUTE_NAME,
                    exc=exc,
                ):
                    route_failures.append(
                        f"{self._ENIU_ROUTE_NAME}(indicator={indicator}) -> "
                        f"{type(exc).__name__}: {exc}"
                    )
                    continue
                raise

            metrics[field_name] = metric_value
            if latest_trade_date is None or trade_date > latest_trade_date:
                latest_trade_date = trade_date

        if latest_trade_date is None:
            return metrics, None, route_failures
        return metrics, latest_trade_date.isoformat(), route_failures

    def _fetch_comparison_metrics(
        self,
        *,
        raw_symbol: str,
    ) -> tuple[dict[str, float], list[str]]:
        fetch_fn = self._resolve_fetch_valuation_comparison()
        try:
            payload = self._call_symbol_only_route(
                fetch_fn=fetch_fn,
                symbol=raw_symbol,
                route_name=self._COMPARISON_ROUTE_NAME,
            )
        except Exception as exc:
            if self._is_hk_valuation_route_unavailable(
                route_name=self._COMPARISON_ROUTE_NAME,
                exc=exc,
            ):
                return (
                    {},
                    [
                        f"{self._COMPARISON_ROUTE_NAME} -> "
                        f"{type(exc).__name__}: {exc}"
                    ],
                )
            raise

        rows = self._payload_to_rows(
            payload=payload,
            route_name=self._COMPARISON_ROUTE_NAME,
        )
        return self._extract_comparison_metrics(rows=rows, raw_symbol=raw_symbol), []

    def _extract_comparison_metrics(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        raw_symbol: str,
    ) -> dict[str, float]:
        matching_rows: list[Mapping[str, Any]] = []
        for row in rows:
            source_code = self._pick_optional(row, "代码", "symbol", "code")
            if source_code is None:
                continue
            if self._normalize_code_fragment(source_code) != raw_symbol:
                continue
            matching_rows.append(row)

        if len(matching_rows) == 0:
            return {}

        metrics: dict[str, float] = {}
        for row_idx, row in enumerate(matching_rows):
            row_metrics: dict[str, float] = {}

            pe_value = self._pick_optional(row, "市盈率-TTM", "市盈率(TTM)", "pe_ttm")
            if pe_value is not None:
                row_metrics["pe_ttm"] = self._to_float(
                    pe_value,
                    field_name="pe_ttm",
                    default_unit_scale=1.0,
                )

            pb_value = self._pick_optional(row, "市净率-MRQ", "市净率", "pb")
            if pb_value is not None:
                row_metrics["pb"] = self._to_float(
                    pb_value,
                    field_name="pb",
                    default_unit_scale=1.0,
                )

            ps_value = self._pick_optional(row, "市销率-TTM", "市销率(TTM)", "ps_ttm")
            if ps_value is not None:
                row_metrics["ps_ttm"] = self._to_float(
                    ps_value,
                    field_name="ps_ttm",
                    default_unit_scale=1.0,
                )

            dividend_value = self._pick_optional(row, "股息率-TTM", "股息率(TTM)", "dividend_yield")
            if dividend_value is not None:
                row_metrics["dividend_yield"] = self._to_float(
                    dividend_value,
                    field_name="dividend_yield",
                    default_unit_scale=1.0,
                )

            if row_idx == 0:
                metrics = row_metrics
                continue

            for key, value in row_metrics.items():
                if key in metrics and metrics[key] != value:
                    raise ValueError(
                        "Conflicting duplicate HK valuation comparison row detected: "
                        f"symbol={raw_symbol!r}, field={key!r}, "
                        f"existing={metrics[key]!r}, candidate={value!r}."
                    )
                if key not in metrics:
                    metrics[key] = value
        return metrics

    def _fetch_optional_baidu_metrics(
        self,
        *,
        raw_symbol: str,
    ) -> tuple[dict[str, float], str | None, list[str]]:
        fetch_fn = self._resolve_fetch_valuation_baidu()
        if fetch_fn is None:
            return {}, None, []

        metrics: dict[str, float] = {}
        latest_trade_date: date | None = None
        route_failures: list[str] = []

        for indicator, field_name, value_keys, unit_scale in (
            *self._BAIDU_REQUIRED_METRIC_SPECS,
            *self._BAIDU_OPTIONAL_METRIC_SPECS,
        ):
            try:
                payload = self._call_baidu_route(
                    fetch_fn=fetch_fn,
                    symbol=raw_symbol,
                    indicator=indicator,
                )
                rows = self._payload_to_rows(
                    payload=payload,
                    route_name=f"{self._OPTIONAL_BAIDU_ROUTE_NAME}(indicator={indicator})",
                )
                trade_date, metric_value = self._extract_latest_metric_point(
                    rows=rows,
                    field_name=field_name,
                    metric_name=indicator,
                    value_keys=value_keys,
                    unit_scale=unit_scale,
                )
            except Exception as exc:
                if self._is_hk_valuation_route_unavailable(
                    route_name=self._OPTIONAL_BAIDU_ROUTE_NAME,
                    exc=exc,
                ):
                    route_failures.append(
                        f"{self._OPTIONAL_BAIDU_ROUTE_NAME}(indicator={indicator}) -> "
                        f"{type(exc).__name__}: {exc}"
                    )
                    continue
                raise

            metrics[field_name] = metric_value
            if latest_trade_date is None or trade_date > latest_trade_date:
                latest_trade_date = trade_date

        if latest_trade_date is None:
            return metrics, None, route_failures
        return metrics, latest_trade_date.isoformat(), route_failures

    def _call_symbol_only_route(
        self,
        *,
        fetch_fn: Callable[..., Any],
        symbol: str,
        route_name: str,
    ) -> Any:
        accepted_args, supports_var_kwargs = self._inspect_callable(fetch_fn)
        symbol_arg = self._resolve_symbol_arg_name(
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
            route_name=route_name,
        )
        return fetch_fn(**{symbol_arg: symbol})

    def _call_eniu_route(
        self,
        *,
        fetch_fn: Callable[..., Any],
        symbol: str,
        indicator: str,
    ) -> Any:
        accepted_args, supports_var_kwargs = self._inspect_callable(fetch_fn)
        kwargs: dict[str, Any] = {}
        symbol_arg = self._resolve_symbol_arg_name(
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
            route_name=self._ENIU_ROUTE_NAME,
        )
        kwargs[symbol_arg] = symbol
        if self._supports_arg(
            "indicator",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            kwargs["indicator"] = indicator
        else:
            raise RuntimeError(
                "AKShare HK valuation eniu route does not accept indicator argument."
            )
        return fetch_fn(**kwargs)

    def _call_baidu_route(
        self,
        *,
        fetch_fn: Callable[..., Any],
        symbol: str,
        indicator: str,
    ) -> Any:
        accepted_args, supports_var_kwargs = self._inspect_callable(fetch_fn)
        kwargs: dict[str, Any] = {}
        symbol_arg = self._resolve_symbol_arg_name(
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
            route_name=self._OPTIONAL_BAIDU_ROUTE_NAME,
        )
        kwargs[symbol_arg] = symbol
        if self._supports_arg(
            "indicator",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            kwargs["indicator"] = indicator
        else:
            raise RuntimeError(
                "AKShare HK valuation baidu route does not accept indicator argument."
            )
        if self._supports_arg(
            "period",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            kwargs["period"] = self._BAIDU_ROUTE_PERIOD
        return fetch_fn(**kwargs)

    def _inspect_callable(self, fn: Callable[..., Any]) -> tuple[set[str], bool]:
        try:
            signature = inspect.signature(fn)
        except (TypeError, ValueError):
            return set(), True

        accepted_args: set[str] = set()
        supports_var_kwargs = False
        for parameter in signature.parameters.values():
            if parameter.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ):
                accepted_args.add(parameter.name)
            if parameter.kind == inspect.Parameter.VAR_KEYWORD:
                supports_var_kwargs = True
        return accepted_args, supports_var_kwargs

    def _supports_arg(
        self,
        arg_name: str,
        *,
        accepted_args: set[str],
        supports_var_kwargs: bool,
    ) -> bool:
        return supports_var_kwargs or arg_name in accepted_args

    def _resolve_symbol_arg_name(
        self,
        *,
        accepted_args: set[str],
        supports_var_kwargs: bool,
        route_name: str,
    ) -> str:
        for candidate in ("symbol", "code", "stock", "ts_code"):
            if self._supports_arg(
                candidate,
                accepted_args=accepted_args,
                supports_var_kwargs=supports_var_kwargs,
            ):
                return candidate
        raise RuntimeError(
            "AKShare HK valuation route does not accept a symbol/code argument: "
            f"{route_name}"
        )

    def _payload_to_rows(
        self,
        *,
        payload: Any,
        route_name: str,
    ) -> list[Mapping[str, Any]]:
        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "AKShare HK valuation payload must be DataFrame-like or "
                f"list[Mapping], got {type(payload).__name__}, route={route_name}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "AKShare HK valuation payload row must be mapping. "
                    f"route={route_name}, idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _extract_latest_metric_point(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        field_name: str,
        metric_name: str,
        value_keys: Sequence[str],
        unit_scale: float,
    ) -> tuple[date, float]:
        if len(rows) == 0:
            raise ValueError(
                "Missing required source field for HK valuation metric: "
                f"metric={metric_name!r}, reason=empty_payload"
            )

        values_by_date: dict[date, float] = {}
        for row_idx, row in enumerate(rows):
            trade_date = self._normalize_trade_date(
                self._pick(row, row_idx, "date", "日期", "trade_date"),
                field_name="trade_date",
            )
            metric_value = self._to_float(
                self._pick(row, row_idx, *value_keys),
                field_name=field_name,
                default_unit_scale=unit_scale,
            )

            existing = values_by_date.get(trade_date)
            if existing is not None and existing != metric_value:
                raise ValueError(
                    "Conflicting duplicate HK valuation source row detected: "
                    f"metric={metric_name!r}, trade_date={trade_date.isoformat()!r}, "
                    f"existing={existing!r}, candidate={metric_value!r}."
                )
            values_by_date[trade_date] = metric_value

        latest_trade_date = max(values_by_date)
        return latest_trade_date, values_by_date[latest_trade_date]

    def _pick(
        self,
        row: Mapping[str, Any],
        row_idx: int,
        *keys: str,
    ) -> Any:
        for key in keys:
            if key in row:
                return row[key]
        raise ValueError(
            "Missing required source field in HK valuation row "
            f"{row_idx}: one of {keys!r}."
        )

    def _pick_optional(self, row: Mapping[str, Any], *keys: str) -> Any | None:
        for key in keys:
            if key not in row:
                continue
            value = row[key]
            if self._is_missing_value(value):
                return None
            return value
        return None

    def _to_float(
        self,
        value: Any,
        *,
        field_name: str,
        default_unit_scale: float,
    ) -> float:
        if isinstance(value, bool):
            raise ValueError(f"Invalid {field_name} value type: bool")
        if isinstance(value, (int, float)):
            numeric = float(value) * default_unit_scale
            if not math.isfinite(numeric):
                raise ValueError(f"Invalid {field_name} value: {value!r}")
            return numeric
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError(f"Invalid {field_name} value: empty string")
            if stripped.lower() in {"nan", "nat", "none", "null"}:
                raise ValueError(f"Invalid {field_name} value: {value!r}")

            normalized = stripped.replace(",", "")
            unit_scale = default_unit_scale
            unit_specs = (
                ("亿港元", 100000000.0),
                ("億港元", 100000000.0),
                ("港元", 1.0),
                ("hkd", 1.0),
                ("亿元", 100000000.0),
                ("亿", 100000000.0),
                ("萬元", 10000.0),
                ("万元", 10000.0),
                ("万", 10000.0),
                ("元", 1.0),
                ("%", 1.0),
            )
            for unit_suffix, factor in unit_specs:
                if normalized.lower().endswith(unit_suffix.lower()):
                    normalized = normalized[: -len(unit_suffix)]
                    unit_scale *= factor
                    break

            normalized = normalized.strip()
            if normalized == "":
                raise ValueError(f"Invalid {field_name} value: {value!r}")
            try:
                numeric = float(normalized) * unit_scale
            except ValueError as exc:
                raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
            if not math.isfinite(numeric):
                raise ValueError(f"Invalid {field_name} value: {value!r}")
            return numeric

        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _normalize_trade_date(self, value: Any, *, field_name: str) -> date:
        if self._is_missing_value(value):
            raise ValueError(f"Invalid {field_name} value: missing")
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError(f"Invalid {field_name} value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                return date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
            if "/" in stripped:
                parts = stripped.split("/")
                if len(parts) == 3 and all(part.isdigit() for part in parts):
                    try:
                        return date(int(parts[0]), int(parts[1]), int(parts[2]))
                    except ValueError as exc:
                        raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
            try:
                return date.fromisoformat(stripped)
            except ValueError:
                try:
                    return datetime.fromisoformat(stripped).date()
                except ValueError as exc:
                    raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _require_single_hk_symbol(
        self,
        symbols: list[str] | None,
    ) -> tuple[str, str, str]:
        if symbols is None or len(symbols) == 0:
            raise ValueError(
                "AkshareHKValuationSnapshotAdapter requires exactly one symbol, got none."
            )
        if len(symbols) != 1:
            raise ValueError(
                "AkshareHKValuationSnapshotAdapter currently supports exactly one symbol."
            )

        raw_value = symbols[0]
        if not isinstance(raw_value, str):
            raise ValueError(
                "Invalid symbol value type for HK valuation snapshot adapter: "
                f"{type(raw_value).__name__}"
            )
        normalized = raw_value.strip().upper()
        if normalized == "":
            raise ValueError("Invalid symbol value for HK valuation snapshot adapter: empty string.")
        canonical_symbol, raw_symbol = self._normalize_hk_symbol(normalized)
        return canonical_symbol, raw_symbol, f"hk{raw_symbol}"

    def _normalize_hk_symbol(self, value: str) -> tuple[str, str]:
        if "." in value:
            code, market = value.split(".", 1)
            if market != "HK":
                raise ValueError(
                    "Unsupported symbol market suffix for HK valuation snapshot adapter: "
                    f"{market!r}. Expected '.HK'."
                )
        else:
            code = value

        if not code.isdigit() or len(code) != 5:
            raise ValueError(
                f"Unsupported HK symbol format: {value!r}. "
                "Expected canonical like '00700.HK' or raw 5-digit stock code."
            )
        return f"{code}.HK", code

    def _normalize_code_fragment(self, value: Any) -> str:
        if isinstance(value, bool):
            return ""
        if isinstance(value, int):
            return f"{value:05d}"
        if isinstance(value, float):
            if not value.is_integer():
                return ""
            return f"{int(value):05d}"
        if not isinstance(value, str):
            return ""
        stripped = value.strip().upper()
        if stripped.startswith("HK") and len(stripped) >= 7:
            stripped = stripped[2:]
        if "." in stripped:
            head, tail = stripped.split(".", 1)
            if tail == "HK":
                stripped = head
        if stripped.isdigit() and len(stripped) <= 5:
            return stripped.zfill(5)
        return ""

    def _filter_records_by_date(
        self,
        *,
        records: Sequence[Mapping[str, Any]],
        start_date: date | None,
        end_date: date | None,
    ) -> list[dict[str, Any]]:
        filtered: list[dict[str, Any]] = []
        for record in records:
            trade_date = date.fromisoformat(str(record["trade_date"]))
            if start_date is not None and trade_date < start_date:
                continue
            if end_date is not None and trade_date > end_date:
                continue
            filtered.append(dict(record))
        return filtered

    def _is_missing_value(self, value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, str) and value.strip().lower() in {"", "nan", "nat", "none", "null"}:
            return True
        if type(value).__name__ == "NaTType":
            return True
        try:
            if value != value:
                return True
        except Exception:
            pass
        return False

    def _is_hk_valuation_route_unavailable(
        self,
        *,
        route_name: str,
        exc: BaseException,
    ) -> bool:
        if self._is_hk_valuation_network_unavailable(exc):
            return True
        if route_name == self._OPTIONAL_BAIDU_ROUTE_NAME and self._is_baidu_route_shape_unavailable(exc):
            return True
        return False

    def _is_baidu_route_shape_unavailable(self, exc: BaseException) -> bool:
        seen: set[int] = set()
        current: BaseException | None = exc
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            message = str(current).lower()
            if isinstance(current, TypeError) and "nonetype" in message and "subscriptable" in message:
                return True
            if isinstance(current, ValueError) and "empty_payload" in message:
                return True
            if current.__cause__ is not None:
                current = current.__cause__
                continue
            current = current.__context__
        return False

    def _is_hk_valuation_network_unavailable(self, exc: BaseException) -> bool:
        network_exception_names = {
            "ProxyError",
            "ConnectionError",
            "ConnectTimeout",
            "ReadTimeout",
            "Timeout",
            "MaxRetryError",
            "NewConnectionError",
            "NameResolutionError",
            "SSLError",
            "SSLCertVerificationError",
        }
        network_message_tokens = (
            "proxy",
            "timed out",
            "timeout",
            "name resolution",
            "temporary failure in name resolution",
            "failed to establish a new connection",
            "max retries exceeded",
            "network is unreachable",
            "connection refused",
            "no route to host",
            "connection reset",
            "dns",
            "certificate verify failed",
            "ssl",
            "eastmoney",
            "gushitong.baidu.com",
            "hq.eniu.com",
            "eniu.com",
        )

        seen: set[int] = set()
        current: BaseException | None = exc
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            name = type(current).__name__
            module = type(current).__module__
            message = str(current).lower()

            if name in network_exception_names:
                return True
            if module.startswith(("requests", "urllib3")) and any(
                token in message for token in network_message_tokens
            ):
                return True
            if any(token in message for token in network_message_tokens):
                return True
            if isinstance(current, (socket.timeout, TimeoutError, ConnectionError, ssl.SSLError)):
                return True
            if isinstance(current, OSError):
                if current.errno in {101, 104, 110, 111, 113}:
                    return True
                if any(token in message for token in network_message_tokens):
                    return True

            if current.__cause__ is not None:
                current = current.__cause__
                continue
            current = current.__context__
        return False


class AkshareHKDailyBarAdapter:
    """Narrow AKShare adapter for Hong Kong stock daily bars only."""

    source_name = AKSHARE_SOURCE_ID
    source_display_name = AKSHARE_SOURCE_NAME

    def __init__(
        self,
        *,
        fetch_hk_hist: Callable[..., Any] | None = None,
        fetch_hk_daily: Callable[..., Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
        price_adjustment: str = "raw",
    ) -> None:
        if price_adjustment not in _SUPPORTED_ADJUSTMENTS:
            supported = ", ".join(sorted(_SUPPORTED_ADJUSTMENTS))
            raise ValueError(
                f"Unsupported price_adjustment={price_adjustment!r}. Supported: {supported}"
            )

        self._fetch_hk_hist = fetch_hk_hist
        self._fetch_hk_daily = fetch_hk_daily
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._price_adjustment = price_adjustment
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if dataset != DatasetName.DAILY_BARS:
            raise ValueError(
                f"Unsupported dataset for AkshareHKDailyBarAdapter: {dataset.value}"
            )

        symbol = self._require_single_symbol(symbols)
        akshare_symbol = self._to_akshare_symbol(symbol)
        rows = self._fetch_hk_rows_with_fallback(
            symbol=akshare_symbol,
            start_date=start_date,
            end_date=end_date,
        )
        records = self._normalize_hk_daily_bar_rows(
            rows=rows,
            symbol=symbol,
            dataset=dataset,
        )
        return self._filter_hk_records_by_date(
            records=records,
            start_date=start_date,
            end_date=end_date,
        )

    def _resolve_fetch_hk_hist(self) -> Callable[..., Any]:
        if self._fetch_hk_hist is not None:
            return self._fetch_hk_hist

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare HK adapter fetch."
            ) from exc

        if hasattr(ak, "stock_hk_hist"):
            return ak.stock_hk_hist
        raise RuntimeError(
            "AKShare HK daily-bar function is unavailable in this akshare version."
        )

    def _resolve_fetch_hk_daily(self) -> Callable[..., Any]:
        if self._fetch_hk_daily is not None:
            return self._fetch_hk_daily

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare HK adapter fetch."
            ) from exc

        if hasattr(ak, "stock_hk_daily"):
            return ak.stock_hk_daily
        raise RuntimeError(
            "AKShare HK daily fallback function is unavailable in this akshare version."
        )

    def _fetch_hk_rows_with_fallback(
        self,
        *,
        symbol: str,
        start_date: date | None,
        end_date: date | None,
    ) -> list[Mapping[str, Any]]:
        fetch_hist = self._resolve_fetch_hk_hist()
        try:
            raw_payload = fetch_hist(
                symbol=symbol,
                period="daily",
                start_date=self._to_akshare_date(start_date),
                end_date=self._to_akshare_date(end_date),
                adjust=_SUPPORTED_ADJUSTMENTS[self._price_adjustment],
            )
            return self._payload_to_rows(raw_payload)
        except Exception as hist_exc:
            if not self._is_hk_hist_network_unavailable(hist_exc):
                raise

        fetch_daily = self._resolve_fetch_hk_daily()
        raw_fallback_payload = fetch_daily(
            symbol=symbol,
            adjust=_SUPPORTED_ADJUSTMENTS[self._price_adjustment],
        )
        return self._payload_to_rows(raw_fallback_payload)

    def _require_single_symbol(self, symbols: list[str] | None) -> str:
        if symbols is None or len(symbols) == 0:
            raise ValueError(
                "AkshareHKDailyBarAdapter requires exactly one symbol, got none."
            )
        if len(symbols) != 1:
            raise ValueError(
                "AkshareHKDailyBarAdapter currently supports exactly one symbol."
            )
        symbol = symbols[0]
        if not isinstance(symbol, str) or symbol.strip() == "":
            raise ValueError("Symbol must be a non-empty string.")

        normalized = symbol.strip().upper()
        if "." not in normalized:
            raise ValueError(
                f"Unsupported HK symbol format: {normalized!r}. Expected like '00700.HK'."
            )
        code, market = normalized.split(".", 1)
        if market != "HK":
            raise ValueError(
                f"Unsupported HK market suffix: {market!r}. Expected '.HK'."
            )
        if not code.isdigit() or len(code) != 5:
            raise ValueError(
                f"Unsupported HK symbol code format: {normalized!r}. "
                "Expected 5-digit code like '00700.HK'."
            )
        return normalized

    def _to_akshare_symbol(self, symbol: str) -> str:
        return symbol.split(".", 1)[0]

    def _to_akshare_date(self, value: date | None) -> str:
        if value is None:
            return ""
        return value.strftime("%Y%m%d")

    def _payload_to_rows(self, payload: Any) -> list[Mapping[str, Any]]:
        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "AKShare HK payload must be DataFrame-like or list[Mapping], "
                f"got {type(payload).__name__}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "AKShare HK payload row must be mapping. "
                    f"idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _normalize_hk_daily_bar_rows(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        symbol: str,
        dataset: DatasetName,
    ) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version

        for idx, row in enumerate(rows):
            trade_date = self._normalize_trade_date(
                self._pick(row, idx, "date", "日期", "trade_date")
            )
            normalized.append(
                {
                    "symbol": symbol,
                    "market": "HK",
                    "trade_date": trade_date,
                    "open": self._to_float(self._pick(row, idx, "open", "开盘")),
                    "high": self._to_float(self._pick(row, idx, "high", "最高")),
                    "low": self._to_float(self._pick(row, idx, "low", "最低")),
                    "close": self._to_float(self._pick(row, idx, "close", "收盘")),
                    "volume": self._to_float(self._pick(row, idx, "volume", "成交量")),
                    "amount": self._to_float(self._pick(row, idx, "amount", "成交额")),
                    "adj_factor": 1.0,
                    "price_adjustment": self._price_adjustment,
                    "source": AKSHARE_SOURCE_ID,
                    "ingested_at": ingested_at,
                    "schema_version": schema_version,
                }
            )
        return normalized

    def _filter_hk_records_by_date(
        self,
        *,
        records: Sequence[Mapping[str, Any]],
        start_date: date | None,
        end_date: date | None,
    ) -> list[dict[str, Any]]:
        filtered: list[dict[str, Any]] = []
        for record in records:
            trade_date = date.fromisoformat(str(record["trade_date"]))
            if start_date is not None and trade_date < start_date:
                continue
            if end_date is not None and trade_date > end_date:
                continue
            filtered.append(dict(record))
        return filtered

    def _pick(
        self,
        row: Mapping[str, Any],
        row_idx: int,
        *keys: str,
    ) -> Any:
        for key in keys:
            if key in row:
                return row[key]
        raise ValueError(
            f"Missing required source field in HK row {row_idx}: one of {keys!r}"
        )

    def _to_float(self, value: Any) -> float:
        if isinstance(value, bool):
            raise ValueError(f"Invalid numeric value type: {value!r}")
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            normalized = value.strip().replace(",", "")
            if normalized == "":
                raise ValueError("Invalid numeric value: empty string")
            try:
                return float(normalized)
            except ValueError as exc:
                raise ValueError(f"Invalid numeric value: {value!r}") from exc
        raise ValueError(f"Invalid numeric value type: {type(value).__name__}")

    def _normalize_trade_date(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if len(stripped) == 8 and stripped.isdigit():
                return date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                ).isoformat()
            try:
                return date.fromisoformat(stripped).isoformat()
            except ValueError as exc:
                raise ValueError(f"Invalid trade date value: {value!r}") from exc
        raise ValueError(f"Invalid trade date value type: {type(value).__name__}")

    def _is_hk_hist_network_unavailable(self, exc: BaseException) -> bool:
        network_exception_names = {
            "ProxyError",
            "ConnectionError",
            "ConnectTimeout",
            "ReadTimeout",
            "Timeout",
            "MaxRetryError",
            "NewConnectionError",
            "NameResolutionError",
            "SSLError",
        }
        network_message_tokens = (
            "proxy",
            "timed out",
            "timeout",
            "name resolution",
            "temporary failure in name resolution",
            "failed to establish a new connection",
            "max retries exceeded",
            "network is unreachable",
            "connection refused",
            "no route to host",
            "connection reset",
            "dns",
            "push2his.eastmoney.com",
            "33.push2his.eastmoney.com",
        )

        seen: set[int] = set()
        current: BaseException | None = exc
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            name = type(current).__name__
            module = type(current).__module__
            message = str(current).lower()

            if name in network_exception_names:
                return True
            if module.startswith(("requests", "urllib3")) and any(
                token in message for token in network_message_tokens
            ):
                return True
            if isinstance(current, (socket.timeout, TimeoutError, ConnectionError)):
                return True
            if isinstance(current, OSError):
                if current.errno in {101, 110, 111, 113}:
                    return True
                if any(token in message for token in network_message_tokens):
                    return True

            if current.__cause__ is not None:
                current = current.__cause__
                continue
            current = current.__context__

        return False


class AkshareIndexDailyBarAdapter:
    """Narrow AKShare adapter for China index daily bars only."""

    source_name = AKSHARE_SOURCE_ID
    source_display_name = AKSHARE_SOURCE_NAME

    def __init__(
        self,
        *,
        fetch_index_daily: Callable[..., Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
        index_name_resolver: Callable[[str], str] | None = None,
    ) -> None:
        self._fetch_index_daily = fetch_index_daily
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._index_name_resolver = index_name_resolver
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if dataset != DatasetName.INDEX_DAILY_BARS:
            raise ValueError(
                "Unsupported dataset for AkshareIndexDailyBarAdapter: "
                f"{dataset.value}"
            )

        canonical_code, akshare_symbol, code = self._require_single_index_code(symbols)
        index_name = self._resolve_index_name(code=code)
        fetch_fn = self._resolve_fetch_index_daily()
        rows = self._fetch_index_rows_with_fallback(
            fetch_fn=fetch_fn,
            akshare_symbol=akshare_symbol,
            start_date=start_date,
            end_date=end_date,
        )
        records = self._normalize_index_rows(
            rows=rows,
            index_code=canonical_code,
            index_name=index_name,
            dataset=dataset,
        )
        return self._filter_records_by_date(
            records=records,
            start_date=start_date,
            end_date=end_date,
        )

    def _resolve_fetch_index_daily(self) -> Callable[..., Any]:
        if self._fetch_index_daily is not None:
            return self._fetch_index_daily

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare index daily-bar fetch."
            ) from exc

        if hasattr(ak, "stock_zh_index_daily_tx"):
            return ak.stock_zh_index_daily_tx
        if hasattr(ak, "stock_zh_index_daily"):
            return ak.stock_zh_index_daily
        if hasattr(ak, "stock_zh_index_daily_em"):
            return ak.stock_zh_index_daily_em
        if hasattr(ak, "index_zh_a_hist"):
            return ak.index_zh_a_hist
        raise RuntimeError(
            "AKShare index daily-bar function is unavailable in this akshare version."
        )

    def _fetch_index_rows_with_fallback(
        self,
        *,
        fetch_fn: Callable[..., Any],
        akshare_symbol: str,
        start_date: date | None,
        end_date: date | None,
    ) -> list[Mapping[str, Any]]:
        accepted_args, supports_var_kwargs = self._inspect_callable(fetch_fn)
        kwargs: dict[str, Any] = {}
        symbol_arg = self._resolve_symbol_arg_name(
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        )
        kwargs[symbol_arg] = akshare_symbol

        if start_date is not None and self._supports_arg(
            "start_date",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            kwargs["start_date"] = self._to_akshare_date(start_date)
        if end_date is not None and self._supports_arg(
            "end_date",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            kwargs["end_date"] = self._to_akshare_date(end_date)

        raw_payload = fetch_fn(**kwargs)
        return self._payload_to_rows(raw_payload)

    def _inspect_callable(
        self,
        fn: Callable[..., Any],
    ) -> tuple[set[str], bool]:
        try:
            signature = inspect.signature(fn)
        except (TypeError, ValueError):
            return set(), True

        accepted_args: set[str] = set()
        supports_var_kwargs = False
        for parameter in signature.parameters.values():
            if parameter.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ):
                accepted_args.add(parameter.name)
            if parameter.kind == inspect.Parameter.VAR_KEYWORD:
                supports_var_kwargs = True
        return accepted_args, supports_var_kwargs

    def _resolve_symbol_arg_name(
        self,
        *,
        accepted_args: set[str],
        supports_var_kwargs: bool,
    ) -> str:
        for candidate in ("symbol", "index", "code"):
            if self._supports_arg(
                candidate,
                accepted_args=accepted_args,
                supports_var_kwargs=supports_var_kwargs,
            ):
                return candidate
        raise RuntimeError(
            "AKShare index daily-bar function does not accept a symbol/index/code argument."
        )

    def _supports_arg(
        self,
        arg_name: str,
        *,
        accepted_args: set[str],
        supports_var_kwargs: bool,
    ) -> bool:
        return supports_var_kwargs or arg_name in accepted_args

    def _require_single_index_code(
        self,
        symbols: list[str] | None,
    ) -> tuple[str, str, str]:
        if symbols is None or len(symbols) == 0:
            raise ValueError(
                "AkshareIndexDailyBarAdapter requires exactly one index code, got none."
            )
        if len(symbols) != 1:
            raise ValueError(
                "AkshareIndexDailyBarAdapter currently supports exactly one index code."
            )

        symbol = symbols[0]
        if not isinstance(symbol, str) or symbol.strip() == "":
            raise ValueError("Index code must be a non-empty string.")

        normalized = symbol.strip().upper()
        code: str
        if normalized.startswith(("SH", "SZ")) and len(normalized) == 8:
            prefix = normalized[:2].lower()
            code = normalized[2:]
            if not code.isdigit():
                raise ValueError(
                    f"Unsupported source-native index code format: {symbol!r}."
                )
            mapped = _CN_INDEX_AKSHARE_SYMBOL_MAP.get(code)
            expected = f"{prefix}{code}"
            if mapped is None or mapped != expected:
                raise ValueError(
                    f"Unsupported or unmapped source-native index code: {symbol!r}."
                )
            return f"{code}.CN_INDEX", expected, code

        if "." in normalized:
            code, market = normalized.split(".", 1)
            if market != "CN_INDEX":
                raise ValueError(
                    f"Unsupported index market suffix: {market!r}. Expected '.CN_INDEX'."
                )
        else:
            code = normalized

        if not code.isdigit() or len(code) != 6:
            raise ValueError(
                f"Unsupported index code format: {symbol!r}. "
                "Expected like '000300.CN_INDEX', '000300', or 'sh000300'."
            )

        akshare_symbol = _CN_INDEX_AKSHARE_SYMBOL_MAP.get(code)
        if akshare_symbol is None:
            raise ValueError(
                f"Unsupported or unmapped index code: {code!r} for current adapter slice."
            )

        return f"{code}.CN_INDEX", akshare_symbol, code

    def _resolve_index_name(self, *, code: str) -> str:
        if self._index_name_resolver is not None:
            resolved = self._index_name_resolver(code)
            if isinstance(resolved, str) and resolved.strip() != "":
                return resolved.strip()

        if code in _CN_INDEX_NAME_MAP:
            return _CN_INDEX_NAME_MAP[code]
        raise ValueError(f"Index name mapping is unavailable for index code {code!r}.")

    def _to_akshare_date(self, value: date | None) -> str:
        if value is None:
            return ""
        return value.strftime("%Y%m%d")

    def _payload_to_rows(self, payload: Any) -> list[Mapping[str, Any]]:
        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "AKShare index payload must be DataFrame-like or list[Mapping], "
                f"got {type(payload).__name__}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "AKShare index payload row must be mapping. "
                    f"idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _normalize_index_rows(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        index_code: str,
        index_name: str,
        dataset: DatasetName,
    ) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version

        for idx, row in enumerate(rows):
            high = self._to_float(self._pick(row, idx, "high", "最高", "最高价"))
            low = self._to_float(self._pick(row, idx, "low", "最低", "最低价"))
            if high < low:
                raise ValueError(
                    f"Invalid OHLC range in index row {idx}: high={high} < low={low}."
                )

            record: dict[str, Any] = {
                "index_code": index_code,
                "index_name": index_name,
                "market": "CN_INDEX",
                "trade_date": self._normalize_trade_date(
                    self._pick(row, idx, "date", "日期", "trade_date")
                ),
                "open": self._to_float(self._pick(row, idx, "open", "开盘", "开盘价")),
                "high": high,
                "low": low,
                "close": self._to_float(self._pick(row, idx, "close", "收盘", "收盘价")),
                "source": AKSHARE_SOURCE_ID,
                "ingested_at": ingested_at,
                "schema_version": schema_version,
            }

            volume = self._pick_optional(row, "volume", "成交量")
            if volume is not None:
                record["volume"] = self._to_float(volume)

            amount = self._pick_optional(row, "amount", "成交额")
            if amount is not None:
                record["amount"] = self._to_float(amount)

            source_ts = self._pick_optional(row, "source_ts", "更新时间", "update_time")
            if source_ts is not None:
                record["source_ts"] = self._normalize_source_ts(source_ts)

            normalized.append(record)

        return normalized

    def _filter_records_by_date(
        self,
        *,
        records: Sequence[Mapping[str, Any]],
        start_date: date | None,
        end_date: date | None,
    ) -> list[dict[str, Any]]:
        filtered: list[dict[str, Any]] = []
        for record in records:
            trade_date = date.fromisoformat(str(record["trade_date"]))
            if start_date is not None and trade_date < start_date:
                continue
            if end_date is not None and trade_date > end_date:
                continue
            filtered.append(dict(record))
        return filtered

    def _pick(
        self,
        row: Mapping[str, Any],
        row_idx: int,
        *keys: str,
    ) -> Any:
        for key in keys:
            if key in row:
                return row[key]
        raise ValueError(
            f"Missing required source field in index row {row_idx}: one of {keys!r}"
        )

    def _pick_optional(
        self,
        row: Mapping[str, Any],
        *keys: str,
    ) -> Any | None:
        for key in keys:
            if key not in row:
                continue
            value = row[key]
            if value is None:
                return None
            if isinstance(value, str) and value.strip() == "":
                return None
            return value
        return None

    def _to_float(self, value: Any) -> float:
        if isinstance(value, bool):
            raise ValueError(f"Invalid numeric value type: {value!r}")
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            normalized = value.strip().replace(",", "")
            if normalized == "":
                raise ValueError("Invalid numeric value: empty string")
            try:
                return float(normalized)
            except ValueError as exc:
                raise ValueError(f"Invalid numeric value: {value!r}") from exc
        raise ValueError(f"Invalid numeric value type: {type(value).__name__}")

    def _normalize_trade_date(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError("Invalid trade date value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                return date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                ).isoformat()
            try:
                return date.fromisoformat(stripped).isoformat()
            except ValueError as exc:
                raise ValueError(f"Invalid trade date value: {value!r}") from exc
        raise ValueError(f"Invalid trade date value type: {type(value).__name__}")

    def _normalize_source_ts(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time()).isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError("Invalid source_ts value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                parsed_date = date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
                return datetime.combine(parsed_date, datetime.min.time()).isoformat()
            try:
                return datetime.fromisoformat(stripped).isoformat()
            except ValueError as exc:
                raise ValueError(f"Invalid source_ts value: {value!r}") from exc
        raise ValueError(f"Invalid source_ts value type: {type(value).__name__}")


class AkshareIndexConstituentsAdapter:
    """Narrow AKShare adapter for China index constituents snapshot only."""

    source_name = AKSHARE_SOURCE_ID
    source_display_name = AKSHARE_SOURCE_NAME

    _FALLBACK_IN_DATE = date(1900, 1, 1)

    def __init__(
        self,
        *,
        fetch_index_cons_weight_csindex: Callable[..., Any] | None = None,
        fetch_index_cons_csindex: Callable[..., Any] | None = None,
        fetch_index_cons_sina: Callable[..., Any] | None = None,
        fetch_index_cons: Callable[..., Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self._fetch_index_cons_weight_csindex = fetch_index_cons_weight_csindex
        self._fetch_index_cons_csindex = fetch_index_cons_csindex
        self._fetch_index_cons_sina = fetch_index_cons_sina
        self._fetch_index_cons = fetch_index_cons
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        del start_date, end_date
        if dataset != DatasetName.INDEX_CONSTITUENTS:
            raise ValueError(
                "Unsupported dataset for AkshareIndexConstituentsAdapter: "
                f"{dataset.value}"
            )

        index_code, source_symbol = self._require_single_index_code(symbols)
        rows = self._fetch_constituent_rows_with_fallback(source_symbol=source_symbol)
        return self._normalize_constituent_rows(
            rows=rows,
            index_code=index_code,
            dataset=dataset,
        )

    def _resolve_fetch_index_cons_weight_csindex(self) -> Callable[..., Any] | None:
        if self._fetch_index_cons_weight_csindex is not None:
            return self._fetch_index_cons_weight_csindex

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception:
            return None

        if hasattr(ak, "index_stock_cons_weight_csindex"):
            return ak.index_stock_cons_weight_csindex
        return None

    def _resolve_fetch_index_cons_csindex(self) -> Callable[..., Any] | None:
        if self._fetch_index_cons_csindex is not None:
            return self._fetch_index_cons_csindex

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception:
            return None

        if hasattr(ak, "index_stock_cons_csindex"):
            return ak.index_stock_cons_csindex
        return None

    def _resolve_fetch_index_cons_sina(self) -> Callable[..., Any] | None:
        if self._fetch_index_cons_sina is not None:
            return self._fetch_index_cons_sina

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception:
            return None

        if hasattr(ak, "index_stock_cons_sina"):
            return ak.index_stock_cons_sina
        return None

    def _resolve_fetch_index_cons(self) -> Callable[..., Any] | None:
        if self._fetch_index_cons is not None:
            return self._fetch_index_cons

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception:
            return None

        if hasattr(ak, "index_stock_cons"):
            return ak.index_stock_cons
        return None

    def _fetch_constituent_rows_with_fallback(
        self,
        *,
        source_symbol: str,
    ) -> list[Mapping[str, Any]]:
        fetch_plan: list[tuple[str, Callable[..., Any] | None]] = [
            (
                "index_stock_cons_weight_csindex",
                self._resolve_fetch_index_cons_weight_csindex(),
            ),
            ("index_stock_cons_csindex", self._resolve_fetch_index_cons_csindex()),
            ("index_stock_cons_sina", self._resolve_fetch_index_cons_sina()),
            ("index_stock_cons", self._resolve_fetch_index_cons()),
        ]

        available = [name for name, fn in fetch_plan if fn is not None]
        if len(available) == 0:
            raise RuntimeError(
                "AKShare index constituents function is unavailable in this akshare version."
            )

        last_network_exc: BaseException | None = None
        last_non_network_exc: BaseException | None = None

        for _route_name, fetch_fn in fetch_plan:
            if fetch_fn is None:
                continue
            try:
                rows = self._call_constituents_fetch_fn(
                    fetch_fn=fetch_fn,
                    source_symbol=source_symbol,
                )
                if len(rows) == 0:
                    continue
                return rows
            except Exception as exc:
                if self._is_index_constituents_network_unavailable(exc):
                    if last_network_exc is None:
                        last_network_exc = exc
                    continue
                if last_non_network_exc is None:
                    last_non_network_exc = exc

        if last_non_network_exc is not None:
            raise last_non_network_exc
        if last_network_exc is not None:
            raise last_network_exc
        raise RuntimeError(
            "AKShare index constituents route returned no usable rows in current environment."
        )

    def _call_constituents_fetch_fn(
        self,
        *,
        fetch_fn: Callable[..., Any],
        source_symbol: str,
    ) -> list[Mapping[str, Any]]:
        accepted_args, supports_var_kwargs = self._inspect_callable(fetch_fn)
        symbol_arg = self._resolve_symbol_arg_name(
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        )
        payload = fetch_fn(**{symbol_arg: source_symbol})
        return self._payload_to_rows(payload)

    def _inspect_callable(
        self,
        fn: Callable[..., Any],
    ) -> tuple[set[str], bool]:
        try:
            signature = inspect.signature(fn)
        except (TypeError, ValueError):
            return set(), True

        accepted_args: set[str] = set()
        supports_var_kwargs = False
        for parameter in signature.parameters.values():
            if parameter.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ):
                accepted_args.add(parameter.name)
            if parameter.kind == inspect.Parameter.VAR_KEYWORD:
                supports_var_kwargs = True
        return accepted_args, supports_var_kwargs

    def _resolve_symbol_arg_name(
        self,
        *,
        accepted_args: set[str],
        supports_var_kwargs: bool,
    ) -> str:
        for candidate in ("symbol", "index", "code"):
            if supports_var_kwargs or candidate in accepted_args:
                return candidate
        raise RuntimeError(
            "AKShare index constituents function does not accept a symbol/index/code argument."
        )

    def _require_single_index_code(
        self,
        symbols: list[str] | None,
    ) -> tuple[str, str]:
        if symbols is None or len(symbols) == 0:
            raise ValueError(
                "AkshareIndexConstituentsAdapter requires exactly one index identifier, got none."
            )
        if len(symbols) != 1:
            raise ValueError(
                "AkshareIndexConstituentsAdapter currently supports exactly one index identifier."
            )

        symbol = symbols[0]
        if not isinstance(symbol, str) or symbol.strip() == "":
            raise ValueError("Index identifier must be a non-empty string.")

        normalized = symbol.strip().upper()
        code: str
        if normalized.startswith(("SH", "SZ")) and len(normalized) == 8:
            code = normalized[2:]
            if not code.isdigit():
                raise ValueError(
                    f"Unsupported source-native index identifier format: {symbol!r}."
                )
            return f"{code}.CN_INDEX", code

        if "." in normalized:
            code, market = normalized.split(".", 1)
            if market != "CN_INDEX":
                raise ValueError(
                    f"Unsupported index market suffix: {market!r}. Expected '.CN_INDEX'."
                )
        else:
            code = normalized

        if not code.isdigit() or len(code) != 6:
            raise ValueError(
                f"Unsupported index identifier format: {symbol!r}. "
                "Expected like '000300.CN_INDEX', '000300', or 'sh000300'."
            )
        return f"{code}.CN_INDEX", code

    def _payload_to_rows(self, payload: Any) -> list[Mapping[str, Any]]:
        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "AKShare index-constituents payload must be DataFrame-like or list[Mapping], "
                f"got {type(payload).__name__}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "AKShare index-constituents payload row must be mapping. "
                    f"idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _normalize_constituent_rows(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        index_code: str,
        dataset: DatasetName,
    ) -> list[dict[str, Any]]:
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version
        normalized_by_key: dict[tuple[str, str], dict[str, Any]] = {}

        for idx, row in enumerate(rows):
            symbol = self._normalize_symbol(
                self._pick(
                    row,
                    idx,
                    "成分券代码",
                    "品种代码",
                    "证券代码",
                    "代码",
                    "symbol",
                    "code",
                )
            )
            record: dict[str, Any] = {
                "index_code": index_code,
                "symbol": symbol,
                "market": "CN_A",
                "in_date": self._resolve_in_date(row).isoformat(),
                "source": AKSHARE_SOURCE_ID,
                "ingested_at": ingested_at,
                "schema_version": schema_version,
            }

            out_date = self._resolve_out_date(row)
            if out_date is not None:
                record["out_date"] = out_date.isoformat()

            weight = self._resolve_weight(row)
            if weight is not None:
                record["weight"] = weight

            source_ts = self._pick_optional(row, "source_ts", "更新时间", "update_time")
            if source_ts is not None:
                record["source_ts"] = self._normalize_source_ts(source_ts)

            dedupe_key = (index_code, symbol)
            if dedupe_key not in normalized_by_key:
                normalized_by_key[dedupe_key] = record
                continue

            existing = normalized_by_key[dedupe_key]
            if (
                existing["in_date"] != record["in_date"]
                or existing.get("out_date") != record.get("out_date")
            ):
                raise ValueError(
                    "Conflicting duplicate index constituent row detected: "
                    f"index_code={index_code!r}, symbol={symbol!r}, "
                    f"in_date={existing['in_date']!r} vs {record['in_date']!r}, "
                    f"out_date={existing.get('out_date')!r} vs {record.get('out_date')!r}."
                )

            normalized_by_key[dedupe_key] = self._select_preferred_duplicate_record(
                existing=existing,
                candidate=record,
            )

        return list(normalized_by_key.values())

    def _resolve_in_date(self, row: Mapping[str, Any]) -> date:
        value = self._pick_optional(
            row,
            "纳入日期",
            "加入日期",
            "调入日期",
            "in_date",
        )
        if value is None:
            return self._FALLBACK_IN_DATE
        return self._normalize_date(value=value, field_name="in_date")

    def _resolve_out_date(self, row: Mapping[str, Any]) -> date | None:
        value = self._pick_optional(
            row,
            "剔除日期",
            "调出日期",
            "移除日期",
            "out_date",
        )
        if value is None:
            return None
        return self._normalize_date(value=value, field_name="out_date")

    def _resolve_weight(self, row: Mapping[str, Any]) -> float | None:
        value = self._pick_optional(row, "权重", "权重(%)", "weight")
        if value is None:
            return None
        weight = self._to_float(value=value, field_name="weight")
        if not (0.0 <= weight <= 100.0):
            raise ValueError(f"Invalid weight value: {weight!r}. Expected within [0, 100].")
        return weight

    def _pick(
        self,
        row: Mapping[str, Any],
        row_idx: int,
        *keys: str,
    ) -> Any:
        for key in keys:
            if key in row:
                return row[key]
        raise ValueError(
            "Missing required source field in index-constituents row "
            f"{row_idx}: one of {keys!r}"
        )

    def _pick_optional(
        self,
        row: Mapping[str, Any],
        *keys: str,
    ) -> Any | None:
        for key in keys:
            if key not in row:
                continue
            value = row[key]
            if value is None:
                return None
            if isinstance(value, str) and value.strip() == "":
                return None
            return value
        return None

    def _normalize_symbol(self, value: Any) -> str:
        raw = self._normalize_symbol_raw_value(value)
        if raw.startswith(("SH", "SZ", "BJ")) and len(raw) == 8:
            return f"{raw[2:]}.{raw[:2]}"
        if "." in raw:
            code, market = raw.split(".", 1)
            if not code.isdigit() or len(code) != 6:
                raise ValueError(f"Invalid index constituent symbol format: {raw!r}.")
            if market not in {"SH", "SZ", "BJ"}:
                raise ValueError(
                    "Invalid index constituent symbol market suffix: "
                    f"{market!r}. Expected SH/SZ/BJ."
                )
            return f"{code}.{market}"
        if not raw.isdigit() or len(raw) != 6:
            raise ValueError(
                f"Invalid index constituent symbol format: {raw!r}. Expected 6-digit code."
            )
        return f"{raw}.{self._infer_a_share_market(raw)}"

    def _normalize_symbol_raw_value(self, value: Any) -> str:
        if isinstance(value, bool):
            raise ValueError(f"Invalid index constituent symbol type: {value!r}")
        if isinstance(value, int):
            if value < 0 or value > 999999:
                raise ValueError(f"Invalid index constituent symbol value: {value!r}")
            return f"{value:06d}"
        if isinstance(value, float):
            if not value.is_integer():
                raise ValueError(f"Invalid index constituent symbol value: {value!r}")
            integer_value = int(value)
            if integer_value < 0 or integer_value > 999999:
                raise ValueError(f"Invalid index constituent symbol value: {value!r}")
            return f"{integer_value:06d}"
        if not isinstance(value, str):
            raise ValueError(
                "Invalid index constituent symbol type: "
                f"{type(value).__name__}"
            )
        normalized = value.strip().upper()
        if normalized == "":
            raise ValueError("Invalid index constituent symbol value: empty string")
        return normalized

    def _infer_a_share_market(self, code: str) -> str:
        if code.startswith(("60", "68", "90")):
            return "SH"
        if code.startswith(("00", "30", "20")):
            return "SZ"
        if code.startswith(("43", "83", "87", "88", "92")):
            return "BJ"
        if code.startswith("6"):
            return "SH"
        if code.startswith(("0", "2", "3")):
            return "SZ"
        if code.startswith(("4", "8")):
            return "BJ"
        raise ValueError(
            "Unsupported index constituent symbol market inference for code "
            f"{code!r}."
        )

    def _normalize_date(self, *, value: Any, field_name: str) -> date:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError(f"Invalid {field_name} value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                return date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
            try:
                return date.fromisoformat(stripped)
            except ValueError as exc:
                raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _to_float(self, *, value: Any, field_name: str) -> float:
        if isinstance(value, bool):
            raise ValueError(f"Invalid {field_name} value type: {value!r}")
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            normalized = value.strip().replace(",", "").replace("%", "")
            if normalized == "":
                raise ValueError(f"Invalid {field_name} value: empty string")
            try:
                return float(normalized)
            except ValueError as exc:
                raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _select_preferred_duplicate_record(
        self,
        *,
        existing: dict[str, Any],
        candidate: dict[str, Any],
    ) -> dict[str, Any]:
        existing_source_ts = existing.get("source_ts")
        candidate_source_ts = candidate.get("source_ts")

        if existing_source_ts is None and candidate_source_ts is not None:
            return candidate
        if existing_source_ts is not None and candidate_source_ts is None:
            return existing
        if existing_source_ts is None and candidate_source_ts is None:
            return existing

        if not isinstance(existing_source_ts, str) or not isinstance(candidate_source_ts, str):
            return existing
        if candidate_source_ts > existing_source_ts:
            return candidate
        return existing

    def _normalize_source_ts(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time()).isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError("Invalid source_ts value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                parsed_date = date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
                return datetime.combine(parsed_date, datetime.min.time()).isoformat()
            try:
                return datetime.fromisoformat(stripped).isoformat()
            except ValueError as exc:
                raise ValueError(f"Invalid source_ts value: {value!r}") from exc
        raise ValueError(f"Invalid source_ts value type: {type(value).__name__}")

    def _is_index_constituents_network_unavailable(self, exc: BaseException) -> bool:
        network_exception_names = {
            "ProxyError",
            "ConnectionError",
            "ConnectTimeout",
            "ReadTimeout",
            "Timeout",
            "MaxRetryError",
            "NewConnectionError",
            "NameResolutionError",
            "SSLError",
        }
        network_message_tokens = (
            "proxy",
            "timed out",
            "timeout",
            "name resolution",
            "temporary failure in name resolution",
            "failed to establish a new connection",
            "max retries exceeded",
            "network is unreachable",
            "connection refused",
            "no route to host",
            "connection reset",
            "dns",
            "sina.com",
            "csindex.com.cn",
        )

        seen: set[int] = set()
        current: BaseException | None = exc
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            name = type(current).__name__
            module = type(current).__module__
            message = str(current).lower()

            if name in network_exception_names:
                return True
            if module.startswith(("requests", "urllib3")) and any(
                token in message for token in network_message_tokens
            ):
                return True
            if isinstance(current, (socket.timeout, TimeoutError, ConnectionError)):
                return True
            if isinstance(current, OSError):
                if current.errno in {101, 110, 111, 113}:
                    return True
                if any(token in message for token in network_message_tokens):
                    return True

            if current.__cause__ is not None:
                current = current.__cause__
                continue
            current = current.__context__
        return False


class AkshareChinaMacroAdapter:
    """Narrow AKShare adapter for selected China macro indicators only."""

    source_name = MACRO_POLICY_SOURCE_ID
    source_display_name = MACRO_POLICY_SOURCE_NAME

    _DEFAULT_REGION = "CN"

    def __init__(
        self,
        *,
        fetch_cpi_yearly: Callable[..., Any] | None = None,
        fetch_ppi_yearly: Callable[..., Any] | None = None,
        fetch_gdp_yearly: Callable[..., Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self._fetch_cpi_yearly = fetch_cpi_yearly
        self._fetch_ppi_yearly = fetch_ppi_yearly
        self._fetch_gdp_yearly = fetch_gdp_yearly
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if dataset == DatasetName.MACRO_INDICATOR_MASTER:
            self._validate_symbols_filter(symbols)
            return self._build_master_records(dataset=dataset)

        if dataset != DatasetName.MACRO_OBSERVATIONS:
            raise ValueError(
                "Unsupported dataset for AkshareChinaMacroAdapter: "
                f"{dataset.value}"
            )

        self._validate_symbols_filter(symbols)
        records = self._fetch_macro_observations(dataset=dataset)
        return self._filter_records_by_date(
            records=records,
            start_date=start_date,
            end_date=end_date,
        )

    def _validate_symbols_filter(self, symbols: list[str] | None) -> None:
        if symbols is None or len(symbols) == 0:
            return
        raise ValueError(
            "AkshareChinaMacroAdapter does not support symbol filters for "
            "the current macro indicator slice."
        )

    def _build_master_records(self, *, dataset: DatasetName) -> list[dict[str, Any]]:
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version
        records: list[dict[str, Any]] = []

        for spec in _MACRO_INDICATOR_SPECS:
            records.append(
                {
                    "indicator_id": spec["indicator_id"],
                    "indicator_name": spec["indicator_name"],
                    "region": self._DEFAULT_REGION,
                    "frequency": spec["frequency"],
                    "unit": spec["unit"],
                    "category": spec["category"],
                    "source": MACRO_POLICY_SOURCE_ID,
                    "ingested_at": ingested_at,
                    "schema_version": schema_version,
                }
            )
        return records

    def _fetch_macro_observations(self, *, dataset: DatasetName) -> list[dict[str, Any]]:
        normalized_by_key: dict[tuple[str, str], dict[str, Any]] = {}

        for spec in _MACRO_INDICATOR_SPECS:
            indicator_id = spec["indicator_id"]
            route_name = spec["route_name"]
            fetch_fn = self._resolve_fetch_macro_indicator(route_name=route_name)
            rows = self._payload_to_rows(payload=fetch_fn(), route_name=route_name)

            for row_idx, row in enumerate(rows):
                record = self._normalize_observation_row(
                    row=row,
                    row_idx=row_idx,
                    dataset=dataset,
                    indicator_id=indicator_id,
                )
                dedupe_key = (
                    record["indicator_id"],
                    record["observation_date"],
                )

                existing = normalized_by_key.get(dedupe_key)
                if existing is None:
                    normalized_by_key[dedupe_key] = record
                    continue

                if self._is_conflicting_duplicate(existing=existing, candidate=record):
                    raise ValueError(
                        "Conflicting duplicate macro observation row detected: "
                        f"indicator_id={record['indicator_id']!r}, "
                        f"observation_date={record['observation_date']!r}."
                    )
                normalized_by_key[dedupe_key] = self._select_preferred_duplicate_record(
                    existing=existing,
                    candidate=record,
                )

        return list(normalized_by_key.values())

    def _resolve_fetch_macro_indicator(self, *, route_name: str) -> Callable[..., Any]:
        override: Callable[..., Any] | None = None
        if route_name == "macro_china_cpi_yearly":
            override = self._fetch_cpi_yearly
        elif route_name == "macro_china_ppi_yearly":
            override = self._fetch_ppi_yearly
        elif route_name == "macro_china_gdp_yearly":
            override = self._fetch_gdp_yearly

        if override is not None:
            return override

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare China macro fetch."
            ) from exc

        if hasattr(ak, route_name):
            return getattr(ak, route_name)
        raise RuntimeError(
            "AKShare China macro function is unavailable in this akshare version: "
            f"{route_name}"
        )

    def _payload_to_rows(
        self,
        *,
        payload: Any,
        route_name: str,
    ) -> list[Mapping[str, Any]]:
        if hasattr(payload, "to_dict"):
            try:
                candidate = payload.to_dict(orient="records")
            except TypeError:
                candidate = payload.to_dict()
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "AKShare China macro payload must be DataFrame-like or list[Mapping], "
                f"got {type(payload).__name__} for route={route_name}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "AKShare China macro payload row must be mapping. "
                    f"route={route_name}, idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _normalize_observation_row(
        self,
        *,
        row: Mapping[str, Any],
        row_idx: int,
        dataset: DatasetName,
        indicator_id: str,
    ) -> dict[str, Any]:
        observation_date = self._normalize_date(
            self._pick(
                row,
                row_idx,
                "observation_date",
                "日期",
                "date",
            ),
            field_name="observation_date",
        )
        value = self._to_float(
            self._pick(
                row,
                row_idx,
                "今值",
                "value",
                "actual",
            )
        )

        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version
        record: dict[str, Any] = {
            "indicator_id": indicator_id,
            "region": self._DEFAULT_REGION,
            "observation_date": observation_date,
            "value": value,
            "source": MACRO_POLICY_SOURCE_ID,
            "ingested_at": ingested_at,
            "schema_version": schema_version,
        }

        release_date = self._pick_optional(row, "release_date", "发布日期")
        if release_date is not None:
            record["release_date"] = self._normalize_date(
                release_date,
                field_name="release_date",
            )

        source_ts = self._pick_optional(row, "source_ts", "更新时间", "update_time")
        if source_ts is not None:
            record["source_ts"] = self._normalize_datetime(
                source_ts,
                field_name="source_ts",
            )

        # Do not infer preliminary flag from numeric forecast/previous fields
        # such as "预告" / "初值" / "预测值"; only accept explicit boolean-like
        # `is_preliminary` in this protocol slice.
        prelim = self._pick_optional(row, "is_preliminary")
        is_preliminary = self._normalize_optional_bool(prelim, field_name="is_preliminary")
        if is_preliminary is not None:
            record["is_preliminary"] = is_preliminary

        return record

    def _filter_records_by_date(
        self,
        *,
        records: Sequence[Mapping[str, Any]],
        start_date: date | None,
        end_date: date | None,
    ) -> list[dict[str, Any]]:
        filtered: list[dict[str, Any]] = []
        for record in records:
            obs_date = date.fromisoformat(str(record["observation_date"]))
            if start_date is not None and obs_date < start_date:
                continue
            if end_date is not None and obs_date > end_date:
                continue
            filtered.append(dict(record))
        return filtered

    def _pick(
        self,
        row: Mapping[str, Any],
        row_idx: int,
        *keys: str,
    ) -> Any:
        for key in keys:
            if key in row:
                return row[key]
        raise ValueError(
            "Missing required source field in macro row "
            f"{row_idx}: one of {keys!r}"
        )

    def _pick_optional(
        self,
        row: Mapping[str, Any],
        *keys: str,
    ) -> Any | None:
        for key in keys:
            if key not in row:
                continue
            value = row[key]
            if value is None:
                return None
            if isinstance(value, str) and value.strip() == "":
                return None
            return value
        return None

    def _normalize_date(self, value: Any, *, field_name: str) -> str:
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError(f"Invalid {field_name} value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                return date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                ).isoformat()
            try:
                return date.fromisoformat(stripped).isoformat()
            except ValueError as exc:
                raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _normalize_datetime(self, value: Any, *, field_name: str) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time()).isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError(f"Invalid {field_name} value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                parsed_date = date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
                return datetime.combine(parsed_date, datetime.min.time()).isoformat()
            try:
                return datetime.fromisoformat(stripped).isoformat()
            except ValueError:
                try:
                    parsed_date = date.fromisoformat(stripped)
                    return datetime.combine(parsed_date, datetime.min.time()).isoformat()
                except ValueError as exc:
                    raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _normalize_optional_bool(
        self,
        value: Any | None,
        *,
        field_name: str,
    ) -> bool | None:
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if value in (0, 0.0):
                return False
            if value in (1, 1.0):
                return True
            raise ValueError(f"Invalid {field_name} value: {value!r}")
        if isinstance(value, str):
            stripped = value.strip().lower()
            if stripped in ("true", "yes", "y", "1", "是"):
                return True
            if stripped in ("false", "no", "n", "0", "否"):
                return False
            raise ValueError(f"Invalid {field_name} value: {value!r}")
        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _to_float(self, value: Any) -> float:
        if isinstance(value, bool):
            raise ValueError(f"Invalid numeric value type: {value!r}")
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            normalized = value.strip().replace(",", "").replace("%", "")
            if normalized == "":
                raise ValueError("Invalid numeric value: empty string")
            try:
                return float(normalized)
            except ValueError as exc:
                raise ValueError(f"Invalid numeric value: {value!r}") from exc
        raise ValueError(f"Invalid numeric value type: {type(value).__name__}")

    def _is_conflicting_duplicate(
        self,
        *,
        existing: Mapping[str, Any],
        candidate: Mapping[str, Any],
    ) -> bool:
        comparable_fields = (
            "indicator_id",
            "region",
            "observation_date",
            "value",
            "release_date",
            "is_preliminary",
            "source",
        )
        return any(existing.get(field) != candidate.get(field) for field in comparable_fields)

    def _select_preferred_duplicate_record(
        self,
        *,
        existing: dict[str, Any],
        candidate: dict[str, Any],
    ) -> dict[str, Any]:
        existing_source_ts = existing.get("source_ts")
        candidate_source_ts = candidate.get("source_ts")

        if existing_source_ts is None and candidate_source_ts is not None:
            return candidate
        if existing_source_ts is not None and candidate_source_ts is None:
            return existing
        if existing_source_ts is None and candidate_source_ts is None:
            return existing
        if not isinstance(existing_source_ts, str) or not isinstance(candidate_source_ts, str):
            return existing
        if candidate_source_ts > existing_source_ts:
            return candidate
        return existing

    def _normalize_source_ts(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time()).isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError("Invalid source_ts value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                parsed_date = date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
                return datetime.combine(parsed_date, datetime.min.time()).isoformat()
            try:
                return datetime.fromisoformat(stripped).isoformat()
            except ValueError as exc:
                raise ValueError(f"Invalid source_ts value: {value!r}") from exc
        raise ValueError(f"Invalid source_ts value type: {type(value).__name__}")

    def _is_index_constituents_network_unavailable(self, exc: BaseException) -> bool:
        network_exception_names = {
            "ProxyError",
            "ConnectionError",
            "ConnectTimeout",
            "ReadTimeout",
            "Timeout",
            "MaxRetryError",
            "NewConnectionError",
            "NameResolutionError",
            "SSLError",
        }
        network_message_tokens = (
            "proxy",
            "timed out",
            "timeout",
            "name resolution",
            "temporary failure in name resolution",
            "failed to establish a new connection",
            "max retries exceeded",
            "network is unreachable",
            "connection refused",
            "no route to host",
            "connection reset",
            "dns",
            "sina.com",
            "csindex.com.cn",
        )

        seen: set[int] = set()
        current: BaseException | None = exc
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            name = type(current).__name__
            module = type(current).__module__
            message = str(current).lower()

            if name in network_exception_names:
                return True
            if module.startswith(("requests", "urllib3")) and any(
                token in message for token in network_message_tokens
            ):
                return True
            if isinstance(current, (socket.timeout, TimeoutError, ConnectionError)):
                return True
            if isinstance(current, OSError):
                if current.errno in {101, 110, 111, 113}:
                    return True
                if any(token in message for token in network_message_tokens):
                    return True

            if current.__cause__ is not None:
                current = current.__cause__
                continue
            current = current.__context__

        return False


class AkshareSectorMasterAdapter:
    """Narrow AKShare adapter for CN sector master snapshot only."""

    source_name = AKSHARE_SOURCE_ID
    source_display_name = AKSHARE_SOURCE_NAME

    def __init__(
        self,
        *,
        fetch_industry_list: Callable[..., Any] | None = None,
        fetch_concept_list: Callable[..., Any] | None = None,
        fetch_industry_list_ths: Callable[..., Any] | None = None,
        fetch_concept_list_ths: Callable[..., Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self._fetch_industry_list = fetch_industry_list
        self._fetch_concept_list = fetch_concept_list
        self._fetch_industry_list_ths = fetch_industry_list_ths
        self._fetch_concept_list_ths = fetch_concept_list_ths
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        del start_date, end_date
        if dataset != DatasetName.SECTOR_MASTER:
            raise ValueError(
                "Unsupported dataset for AkshareSectorMasterAdapter: "
                f"{dataset.value}"
            )

        sector_types = self._resolve_sector_type_filters(symbols)
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version
        seen_sector_ids: set[str] = set()
        normalized_records: list[dict[str, Any]] = []

        for sector_type in sector_types:
            rows = self._fetch_sector_master_rows_with_fallback(sector_type=sector_type)
            normalized_records.extend(
                self._normalize_sector_master_rows(
                    rows=rows,
                    sector_type=sector_type,
                    ingested_at=ingested_at,
                    schema_version=schema_version,
                    seen_sector_ids=seen_sector_ids,
                )
            )
        return normalized_records

    def _resolve_sector_type_filters(
        self,
        symbols: list[str] | None,
    ) -> tuple[str, ...]:
        if symbols is None or len(symbols) == 0:
            return ("INDUSTRY", "CONCEPT")

        if len(symbols) != 1:
            raise ValueError(
                "AkshareSectorMasterAdapter accepts at most one sector-type filter via "
                "symbols, such as 'INDUSTRY' or 'CONCEPT'."
            )

        symbol = symbols[0]
        if not isinstance(symbol, str) or symbol.strip() == "":
            raise ValueError(
                "AkshareSectorMasterAdapter symbols filter value must be a non-empty string."
            )

        sector_type = symbol.strip().upper()
        if sector_type not in {"INDUSTRY", "CONCEPT"}:
            raise ValueError(
                "Unsupported sector type filter value: "
                f"{symbol!r}. Expected 'INDUSTRY' or 'CONCEPT'."
            )

        return (sector_type,)

    def _resolve_fetch_fn(self, *, sector_type: str) -> Callable[..., Any]:
        if sector_type == "INDUSTRY":
            return self._resolve_fetch_industry_list()
        return self._resolve_fetch_concept_list()

    def _resolve_fallback_fetch_fn(self, *, sector_type: str) -> Callable[..., Any]:
        if sector_type == "INDUSTRY":
            return self._resolve_fetch_industry_list_ths()
        return self._resolve_fetch_concept_list_ths()

    def _fetch_sector_master_rows_with_fallback(
        self,
        *,
        sector_type: str,
    ) -> list[Mapping[str, Any]]:
        primary_fetch_fn = self._resolve_fetch_fn(sector_type=sector_type)
        try:
            primary_payload = primary_fetch_fn()
            return self._payload_to_rows(payload=primary_payload, sector_type=sector_type)
        except Exception as primary_exc:
            if not self._is_sector_master_network_unavailable(primary_exc):
                raise

        fallback_fetch_fn = self._resolve_fallback_fetch_fn(sector_type=sector_type)
        fallback_payload = fallback_fetch_fn()
        return self._payload_to_rows(payload=fallback_payload, sector_type=sector_type)

    def _resolve_fetch_industry_list(self) -> Callable[..., Any]:
        if self._fetch_industry_list is not None:
            return self._fetch_industry_list

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare sector master fetch."
            ) from exc

        if hasattr(ak, "stock_board_industry_name_em"):
            return ak.stock_board_industry_name_em
        raise RuntimeError(
            "AKShare industry sector-master function is unavailable in this akshare version."
        )

    def _resolve_fetch_concept_list(self) -> Callable[..., Any]:
        if self._fetch_concept_list is not None:
            return self._fetch_concept_list

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare sector master fetch."
            ) from exc

        if hasattr(ak, "stock_board_concept_name_em"):
            return ak.stock_board_concept_name_em
        raise RuntimeError(
            "AKShare concept sector-master function is unavailable in this akshare version."
        )

    def _resolve_fetch_industry_list_ths(self) -> Callable[..., Any]:
        if self._fetch_industry_list_ths is not None:
            return self._fetch_industry_list_ths

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare sector master fetch."
            ) from exc

        if hasattr(ak, "stock_board_industry_name_ths"):
            return ak.stock_board_industry_name_ths
        raise RuntimeError(
            "AKShare industry sector-master fallback function is unavailable in this akshare version."
        )

    def _resolve_fetch_concept_list_ths(self) -> Callable[..., Any]:
        if self._fetch_concept_list_ths is not None:
            return self._fetch_concept_list_ths

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare sector master fetch."
            ) from exc

        if hasattr(ak, "stock_board_concept_name_ths"):
            return ak.stock_board_concept_name_ths
        raise RuntimeError(
            "AKShare concept sector-master fallback function is unavailable in this akshare version."
        )

    def _payload_to_rows(
        self,
        *,
        payload: Any,
        sector_type: str,
    ) -> list[Mapping[str, Any]]:
        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "AKShare sector-master payload must be DataFrame-like or list[Mapping], "
                f"got {type(payload).__name__} for sector_type={sector_type}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "AKShare sector-master payload row must be mapping. "
                    f"sector_type={sector_type}, idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _normalize_sector_master_rows(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        sector_type: str,
        ingested_at: str,
        schema_version: str,
        seen_sector_ids: set[str],
    ) -> list[dict[str, Any]]:
        normalized_by_sector_id: dict[str, tuple[dict[str, Any], str | None]] = {}
        for idx, row in enumerate(rows):
            sector_name = self._normalize_sector_name(
                self._pick(
                    row,
                    idx,
                    "板块名称",
                    "sector_name",
                    "name",
                )
            )
            sector_id = f"{sector_type}:{sector_name}"
            sector_code = self._normalize_sector_code(
                self._pick_optional(
                    row,
                    "板块代码",
                    "sector_code",
                    "code",
                )
            )

            record: dict[str, Any] = {
                "sector_id": sector_id,
                "sector_name": sector_name,
                "sector_type": sector_type,
                "market": "CN_SECTOR",
                "is_active": True,
                "source": AKSHARE_SOURCE_ID,
                "ingested_at": ingested_at,
                "schema_version": schema_version,
            }

            source_ts = self._pick_optional(row, "source_ts", "更新时间", "update_time")
            if source_ts is not None:
                record["source_ts"] = self._normalize_source_ts(source_ts)

            if sector_id not in normalized_by_sector_id:
                if sector_id in seen_sector_ids:
                    raise ValueError(
                        f"Duplicate canonical sector_id across sector-type routes: {sector_id!r}"
                    )
                seen_sector_ids.add(sector_id)
                normalized_by_sector_id[sector_id] = (record, sector_code)
                continue

            existing_record, existing_sector_code = normalized_by_sector_id[sector_id]
            if (
                existing_sector_code is not None
                and sector_code is not None
                and existing_sector_code != sector_code
            ):
                raise ValueError(
                    "Conflicting duplicate canonical sector_id detected: "
                    f"{sector_id!r}, codes={existing_sector_code!r} vs {sector_code!r}"
                )

            preferred_record = self._select_preferred_duplicate_record(
                existing=existing_record,
                candidate=record,
            )
            preferred_sector_code = existing_sector_code or sector_code
            normalized_by_sector_id[sector_id] = (
                preferred_record,
                preferred_sector_code,
            )

        return [record for record, _sector_code in normalized_by_sector_id.values()]

    def _pick(
        self,
        row: Mapping[str, Any],
        row_idx: int,
        *keys: str,
    ) -> Any:
        for key in keys:
            if key in row:
                return row[key]
        raise ValueError(
            "Missing required source field in sector-master row "
            f"{row_idx}: one of {keys!r}"
        )

    def _pick_optional(
        self,
        row: Mapping[str, Any],
        *keys: str,
    ) -> Any | None:
        for key in keys:
            if key not in row:
                continue
            value = row[key]
            if value is None:
                return None
            if isinstance(value, str) and value.strip() == "":
                return None
            return value
        return None

    def _normalize_sector_name(self, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError(
                "Invalid sector name value type in sector-master payload: "
                f"{type(value).__name__}"
            )
        normalized = value.strip()
        if normalized == "":
            raise ValueError("Invalid sector name value in sector-master payload: empty string")
        if ":" in normalized:
            raise ValueError(
                "Invalid sector name value in sector-master payload: must not contain ':'."
            )
        return normalized

    def _normalize_sector_code(self, value: Any | None) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            value = str(value)
        normalized = value.strip().upper()
        if normalized == "":
            return None
        return normalized

    def _select_preferred_duplicate_record(
        self,
        *,
        existing: dict[str, Any],
        candidate: dict[str, Any],
    ) -> dict[str, Any]:
        existing_source_ts = existing.get("source_ts")
        candidate_source_ts = candidate.get("source_ts")

        if existing_source_ts is None and candidate_source_ts is not None:
            return candidate
        if existing_source_ts is not None and candidate_source_ts is None:
            return existing
        if existing_source_ts is None and candidate_source_ts is None:
            return existing

        if not isinstance(existing_source_ts, str) or not isinstance(candidate_source_ts, str):
            return existing
        if candidate_source_ts > existing_source_ts:
            return candidate
        return existing

    def _normalize_source_ts(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time()).isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError("Invalid source_ts value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                parsed_date = date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
                return datetime.combine(parsed_date, datetime.min.time()).isoformat()
            try:
                return datetime.fromisoformat(stripped).isoformat()
            except ValueError as exc:
                raise ValueError(f"Invalid source_ts value: {value!r}") from exc
        raise ValueError(f"Invalid source_ts value type: {type(value).__name__}")

    def _is_sector_master_network_unavailable(self, exc: BaseException) -> bool:
        network_exception_names = {
            "ProxyError",
            "ConnectionError",
            "ConnectTimeout",
            "ReadTimeout",
            "Timeout",
            "MaxRetryError",
            "NewConnectionError",
            "NameResolutionError",
            "SSLError",
        }
        network_message_tokens = (
            "proxy",
            "timed out",
            "timeout",
            "name resolution",
            "temporary failure in name resolution",
            "failed to establish a new connection",
            "max retries exceeded",
            "network is unreachable",
            "connection refused",
            "no route to host",
            "connection reset",
            "dns",
            "eastmoney",
            "quote.eastmoney.com",
            "push2.eastmoney.com",
            "push2his.eastmoney.com",
        )

        seen: set[int] = set()
        current: BaseException | None = exc
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            name = type(current).__name__
            module = type(current).__module__
            message = str(current).lower()

            if name in network_exception_names:
                return True
            if module.startswith(("requests", "urllib3")) and any(
                token in message for token in network_message_tokens
            ):
                return True
            if isinstance(current, (socket.timeout, TimeoutError, ConnectionError)):
                return True
            if isinstance(current, OSError):
                if current.errno in {101, 110, 111, 113}:
                    return True
                if any(token in message for token in network_message_tokens):
                    return True

            if current.__cause__ is not None:
                current = current.__cause__
                continue
            current = current.__context__

        return False


class AkshareSectorMembershipAdapter:
    """Narrow AKShare adapter for one sector membership snapshot."""

    source_name = AKSHARE_SOURCE_ID
    source_display_name = AKSHARE_SOURCE_NAME

    _FALLBACK_IN_DATE = date(1900, 1, 1)

    def __init__(
        self,
        *,
        fetch_industry_cons: Callable[..., Any] | None = None,
        fetch_concept_cons: Callable[..., Any] | None = None,
        fetch_industry_list_ths: Callable[..., Any] | None = None,
        fetch_concept_list_ths: Callable[..., Any] | None = None,
        fetch_ths_detail_page: Callable[[str], str] | None = None,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self._fetch_industry_cons = fetch_industry_cons
        self._fetch_concept_cons = fetch_concept_cons
        self._fetch_industry_list_ths = fetch_industry_list_ths
        self._fetch_concept_list_ths = fetch_concept_list_ths
        self._fetch_ths_detail_page_fn = fetch_ths_detail_page
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        del start_date, end_date
        if dataset != DatasetName.SECTOR_MEMBERSHIP:
            raise ValueError(
                "Unsupported dataset for AkshareSectorMembershipAdapter: "
                f"{dataset.value}"
            )

        sector_id, sector_type, sector_name = self._require_single_sector_identifier(symbols)
        rows = self._fetch_membership_rows(
            sector_type=sector_type,
            sector_name=sector_name,
        )
        return self._normalize_membership_rows(
            rows=rows,
            sector_id=sector_id,
            dataset=dataset,
        )

    def _resolve_fetch_membership_fn(self, *, sector_type: str) -> Callable[..., Any]:
        if sector_type == "INDUSTRY":
            return self._resolve_fetch_industry_cons()
        return self._resolve_fetch_concept_cons()

    def _resolve_fetch_industry_cons(self) -> Callable[..., Any]:
        if self._fetch_industry_cons is not None:
            return self._fetch_industry_cons

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare sector membership fetch."
            ) from exc

        if hasattr(ak, "stock_board_industry_cons_em"):
            return ak.stock_board_industry_cons_em
        raise RuntimeError(
            "AKShare industry sector-membership function is unavailable in this akshare version."
        )

    def _resolve_fetch_concept_cons(self) -> Callable[..., Any]:
        if self._fetch_concept_cons is not None:
            return self._fetch_concept_cons

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare sector membership fetch."
            ) from exc

        if hasattr(ak, "stock_board_concept_cons_em"):
            return ak.stock_board_concept_cons_em
        raise RuntimeError(
            "AKShare concept sector-membership function is unavailable in this akshare version."
        )

    def _resolve_fetch_industry_list_ths(self) -> Callable[..., Any]:
        if self._fetch_industry_list_ths is not None:
            return self._fetch_industry_list_ths

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for THS sector-membership fallback."
            ) from exc

        if hasattr(ak, "stock_board_industry_name_ths"):
            return ak.stock_board_industry_name_ths
        raise RuntimeError(
            "AKShare THS industry sector-name function is unavailable in this akshare version."
        )

    def _resolve_fetch_concept_list_ths(self) -> Callable[..., Any]:
        if self._fetch_concept_list_ths is not None:
            return self._fetch_concept_list_ths

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for THS sector-membership fallback."
            ) from exc

        if hasattr(ak, "stock_board_concept_name_ths"):
            return ak.stock_board_concept_name_ths
        raise RuntimeError(
            "AKShare THS concept sector-name function is unavailable in this akshare version."
        )

    def _fetch_membership_rows(
        self,
        *,
        sector_type: str,
        sector_name: str,
    ) -> list[Mapping[str, Any]]:
        fetch_fn = self._resolve_fetch_membership_fn(sector_type=sector_type)
        accepted_args, supports_var_kwargs = self._inspect_callable(fetch_fn)
        kwargs: dict[str, Any] = {}
        symbol_arg = self._resolve_symbol_arg_name(
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        )
        kwargs[symbol_arg] = sector_name
        primary_network_exc: BaseException | None = None
        try:
            raw_payload = fetch_fn(**kwargs)
            return self._payload_to_rows(raw_payload)
        except Exception as primary_exc:
            if not self._is_membership_network_unavailable(primary_exc):
                raise
            primary_network_exc = primary_exc

        try:
            return self._fetch_membership_rows_from_ths(
                sector_type=sector_type,
                sector_name=sector_name,
            )
        except Exception as fallback_exc:
            if (
                primary_network_exc is not None
                and self._is_membership_network_unavailable(fallback_exc)
            ):
                raise primary_network_exc from fallback_exc
            raise

    def _fetch_membership_rows_from_ths(
        self,
        *,
        sector_type: str,
        sector_name: str,
    ) -> list[Mapping[str, Any]]:
        sector_code = self._lookup_ths_sector_code(
            sector_type=sector_type,
            sector_name=sector_name,
        )
        detail_url = self._build_ths_sector_detail_url(
            sector_type=sector_type,
            sector_code=sector_code,
        )
        page_text = self._fetch_ths_detail_page(detail_url)
        rows = self._extract_ths_membership_rows(page_text)
        if len(rows) == 0:
            raise ValueError(
                "THS sector-membership fallback returned no rows for "
                f"sector_type={sector_type}, sector_name={sector_name!r}, "
                f"sector_code={sector_code!r}."
            )
        return rows

    def _lookup_ths_sector_code(
        self,
        *,
        sector_type: str,
        sector_name: str,
    ) -> str:
        fetch_list_fn = self._resolve_fetch_sector_name_list_ths(sector_type=sector_type)
        rows = self._payload_to_rows(fetch_list_fn())
        target_name = self._normalize_sector_name_for_lookup(sector_name)

        for row in rows:
            candidate_name = self._pick_optional(
                row,
                "name",
                "板块名称",
                "概念名称",
                "行业名称",
            )
            candidate_code = self._pick_optional(
                row,
                "code",
                "板块代码",
                "概念代码",
                "行业代码",
            )
            if candidate_name is None or candidate_code is None:
                continue

            if self._normalize_sector_name_for_lookup(candidate_name) != target_name:
                continue

            normalized_code = self._normalize_ths_sector_code(candidate_code)
            if normalized_code is not None:
                return normalized_code

        raise ValueError(
            "THS sector-membership fallback cannot resolve sector code for "
            f"sector_type={sector_type}, sector_name={sector_name!r}."
        )

    def _resolve_fetch_sector_name_list_ths(self, *, sector_type: str) -> Callable[..., Any]:
        if sector_type == "INDUSTRY":
            return self._resolve_fetch_industry_list_ths()
        return self._resolve_fetch_concept_list_ths()

    def _normalize_sector_name_for_lookup(self, value: Any) -> str:
        if not isinstance(value, str):
            value = str(value)
        return value.strip()

    def _normalize_ths_sector_code(self, value: Any) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            value = str(value)
        normalized = value.strip()
        if normalized == "":
            return None
        return normalized

    def _build_ths_sector_detail_url(self, *, sector_type: str, sector_code: str) -> str:
        if sector_type == "INDUSTRY":
            return f"https://q.10jqka.com.cn/thshy/detail/code/{sector_code}/"
        return f"https://q.10jqka.com.cn/gn/detail/code/{sector_code}/"

    def _fetch_ths_detail_page(self, url: str) -> str:
        if self._fetch_ths_detail_page_fn is not None:
            return self._fetch_ths_detail_page_fn(url)

        try:
            import requests  # type: ignore[import-untyped]
        except Exception as exc:  # pragma: no cover - dependency env specific
            raise RuntimeError(
                "requests dependency is required for THS sector-membership fallback page fetch."
            ) from exc

        response = requests.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
            },
            timeout=20,
        )
        response.raise_for_status()
        if response.encoding is None:
            response.encoding = response.apparent_encoding or "utf-8"
        return response.text

    def _extract_ths_membership_rows(self, page_text: str) -> list[Mapping[str, Any]]:
        pattern = re.compile(
            r"<td>\s*<a[^>]+stockpage\.10jqka\.com\.cn/(\d{6})/?[^>]*>\d{6}</a>\s*</td>\s*"
            r"<td>\s*<a[^>]*>([^<]+)</a>",
            re.IGNORECASE,
        )
        rows: list[Mapping[str, Any]] = []
        seen_codes: set[str] = set()

        for code, name in pattern.findall(page_text):
            if code in seen_codes:
                continue
            seen_codes.add(code)
            rows.append({"代码": code, "名称": name.strip()})

        return rows

    def _inspect_callable(
        self,
        fn: Callable[..., Any],
    ) -> tuple[set[str], bool]:
        try:
            signature = inspect.signature(fn)
        except (TypeError, ValueError):
            return set(), True

        accepted_args: set[str] = set()
        supports_var_kwargs = False
        for parameter in signature.parameters.values():
            if parameter.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ):
                accepted_args.add(parameter.name)
            if parameter.kind == inspect.Parameter.VAR_KEYWORD:
                supports_var_kwargs = True
        return accepted_args, supports_var_kwargs

    def _resolve_symbol_arg_name(
        self,
        *,
        accepted_args: set[str],
        supports_var_kwargs: bool,
    ) -> str:
        for candidate in ("symbol", "name", "sector"):
            if self._supports_arg(
                candidate,
                accepted_args=accepted_args,
                supports_var_kwargs=supports_var_kwargs,
            ):
                return candidate
        raise RuntimeError(
            "AKShare sector-membership function does not accept a sector symbol/name argument."
        )

    def _supports_arg(
        self,
        arg_name: str,
        *,
        accepted_args: set[str],
        supports_var_kwargs: bool,
    ) -> bool:
        return supports_var_kwargs or arg_name in accepted_args

    def _require_single_sector_identifier(
        self,
        symbols: list[str] | None,
    ) -> tuple[str, str, str]:
        if symbols is None or len(symbols) == 0:
            raise ValueError(
                "AkshareSectorMembershipAdapter requires exactly one sector identifier, got none."
            )
        if len(symbols) != 1:
            raise ValueError(
                "AkshareSectorMembershipAdapter currently supports exactly one sector identifier."
            )

        symbol = symbols[0]
        if not isinstance(symbol, str) or symbol.strip() == "":
            raise ValueError("Sector identifier must be a non-empty string.")

        normalized = symbol.strip()
        if ":" not in normalized:
            raise ValueError(
                "Unsupported sector identifier format. Expected typed identifier like "
                "'INDUSTRY:小金属' or 'CONCEPT:绿色电力'."
            )

        prefix_raw, sector_name_raw = normalized.split(":", 1)
        prefix = prefix_raw.strip().upper()
        sector_name = sector_name_raw.strip()

        if prefix not in {"INDUSTRY", "CONCEPT"}:
            raise ValueError(
                f"Unsupported sector identifier prefix: {prefix!r}. "
                "Expected 'INDUSTRY' or 'CONCEPT'."
            )
        if sector_name == "":
            raise ValueError(
                "Malformed sector identifier: sector name must be non-empty after prefix."
            )
        if ":" in sector_name:
            raise ValueError(
                "Malformed sector identifier: sector name must not contain ':'."
            )

        return f"{prefix}:{sector_name}", prefix, sector_name

    def _payload_to_rows(self, payload: Any) -> list[Mapping[str, Any]]:
        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "AKShare sector-membership payload must be DataFrame-like or list[Mapping], "
                f"got {type(payload).__name__}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "AKShare sector-membership payload row must be mapping. "
                    f"idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _normalize_membership_rows(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        sector_id: str,
        dataset: DatasetName,
    ) -> list[dict[str, Any]]:
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version
        normalized_by_key: dict[tuple[str, str], dict[str, Any]] = {}

        for idx, row in enumerate(rows):
            symbol = self._normalize_symbol(
                self._pick(row, idx, "代码", "symbol", "证券代码", "成分代码")
            )
            record: dict[str, Any] = {
                "sector_id": sector_id,
                "symbol": symbol,
                "market": "CN_A",
                "in_date": self._resolve_in_date(row).isoformat(),
                "source": AKSHARE_SOURCE_ID,
                "ingested_at": ingested_at,
                "schema_version": schema_version,
            }

            out_date = self._resolve_out_date(row)
            if out_date is not None:
                record["out_date"] = out_date.isoformat()

            source_ts = self._pick_optional(row, "source_ts", "更新时间", "update_time")
            if source_ts is not None:
                record["source_ts"] = self._normalize_source_ts(source_ts)

            dedupe_key = (sector_id, symbol)
            if dedupe_key not in normalized_by_key:
                normalized_by_key[dedupe_key] = record
                continue

            existing = normalized_by_key[dedupe_key]
            if (
                existing["in_date"] != record["in_date"]
                or existing.get("out_date") != record.get("out_date")
            ):
                raise ValueError(
                    "Conflicting duplicate sector membership row detected: "
                    f"sector_id={sector_id!r}, symbol={symbol!r}, "
                    f"in_date={existing['in_date']!r} vs {record['in_date']!r}, "
                    f"out_date={existing.get('out_date')!r} vs {record.get('out_date')!r}."
                )

            normalized_by_key[dedupe_key] = self._select_preferred_duplicate_record(
                existing=existing,
                candidate=record,
            )

        return list(normalized_by_key.values())

    def _resolve_in_date(self, row: Mapping[str, Any]) -> date:
        value = self._pick_optional(
            row,
            "纳入日期",
            "加入日期",
            "调入日期",
            "入选日期",
            "in_date",
        )
        if value is None:
            return self._FALLBACK_IN_DATE
        return self._normalize_date(value=value, field_name="in_date")

    def _resolve_out_date(self, row: Mapping[str, Any]) -> date | None:
        value = self._pick_optional(
            row,
            "剔除日期",
            "调出日期",
            "移除日期",
            "out_date",
        )
        if value is None:
            return None
        return self._normalize_date(value=value, field_name="out_date")

    def _pick(
        self,
        row: Mapping[str, Any],
        row_idx: int,
        *keys: str,
    ) -> Any:
        for key in keys:
            if key in row:
                return row[key]
        raise ValueError(
            "Missing required source field in sector-membership row "
            f"{row_idx}: one of {keys!r}"
        )

    def _pick_optional(
        self,
        row: Mapping[str, Any],
        *keys: str,
    ) -> Any | None:
        for key in keys:
            if key not in row:
                continue
            value = row[key]
            if value is None:
                return None
            if isinstance(value, str) and value.strip() == "":
                return None
            return value
        return None

    def _normalize_symbol(self, value: Any) -> str:
        raw = self._normalize_symbol_raw_value(value)
        if "." in raw:
            code, market = raw.split(".", 1)
            if not code.isdigit() or len(code) != 6:
                raise ValueError(
                    f"Invalid sector-membership symbol format: {raw!r}."
                )
            if market not in {"SH", "SZ", "BJ"}:
                raise ValueError(
                    "Invalid sector-membership symbol market suffix: "
                    f"{market!r}. Expected SH/SZ/BJ."
                )
            return f"{code}.{market}"

        if not raw.isdigit() or len(raw) != 6:
            raise ValueError(
                f"Invalid sector-membership symbol format: {raw!r}. Expected 6-digit code."
            )
        market = self._infer_a_share_market(raw)
        return f"{raw}.{market}"

    def _normalize_symbol_raw_value(self, value: Any) -> str:
        if isinstance(value, bool):
            raise ValueError(f"Invalid sector-membership symbol type: {value!r}")
        if isinstance(value, int):
            if value < 0 or value > 999999:
                raise ValueError(f"Invalid sector-membership symbol value: {value!r}")
            return f"{value:06d}"
        if isinstance(value, float):
            if not value.is_integer():
                raise ValueError(f"Invalid sector-membership symbol value: {value!r}")
            integer_value = int(value)
            if integer_value < 0 or integer_value > 999999:
                raise ValueError(f"Invalid sector-membership symbol value: {value!r}")
            return f"{integer_value:06d}"
        if not isinstance(value, str):
            raise ValueError(
                "Invalid sector-membership symbol type: "
                f"{type(value).__name__}"
            )
        normalized = value.strip().upper()
        if normalized == "":
            raise ValueError("Invalid sector-membership symbol value: empty string")
        return normalized

    def _infer_a_share_market(self, code: str) -> str:
        if code.startswith(("60", "68", "90")):
            return "SH"
        if code.startswith(("00", "30", "20")):
            return "SZ"
        if code.startswith(("43", "83", "87", "88", "92")):
            return "BJ"
        if code.startswith("6"):
            return "SH"
        if code.startswith(("0", "2", "3")):
            return "SZ"
        if code.startswith(("4", "8")):
            return "BJ"
        raise ValueError(
            "Unsupported sector-membership symbol market inference for code "
            f"{code!r}."
        )

    def _normalize_date(self, *, value: Any, field_name: str) -> date:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError(f"Invalid {field_name} value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                return date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
            try:
                return date.fromisoformat(stripped)
            except ValueError as exc:
                raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _select_preferred_duplicate_record(
        self,
        *,
        existing: dict[str, Any],
        candidate: dict[str, Any],
    ) -> dict[str, Any]:
        existing_source_ts = existing.get("source_ts")
        candidate_source_ts = candidate.get("source_ts")

        if existing_source_ts is None and candidate_source_ts is not None:
            return candidate
        if existing_source_ts is not None and candidate_source_ts is None:
            return existing
        if existing_source_ts is None and candidate_source_ts is None:
            return existing

        if not isinstance(existing_source_ts, str) or not isinstance(candidate_source_ts, str):
            return existing
        if candidate_source_ts > existing_source_ts:
            return candidate
        return existing

    def _normalize_source_ts(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time()).isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError("Invalid source_ts value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                parsed_date = date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
                return datetime.combine(parsed_date, datetime.min.time()).isoformat()
            try:
                return datetime.fromisoformat(stripped).isoformat()
            except ValueError as exc:
                raise ValueError(f"Invalid source_ts value: {value!r}") from exc
        raise ValueError(f"Invalid source_ts value type: {type(value).__name__}")

    def _is_membership_network_unavailable(self, exc: BaseException) -> bool:
        network_exception_names = {
            "ProxyError",
            "ConnectionError",
            "ConnectTimeout",
            "ReadTimeout",
            "Timeout",
            "MaxRetryError",
            "NewConnectionError",
            "NameResolutionError",
            "SSLError",
            "URLError",
            "HTTPError",
        }
        network_message_tokens = (
            "proxy",
            "timed out",
            "timeout",
            "name resolution",
            "temporary failure in name resolution",
            "failed to establish a new connection",
            "max retries exceeded",
            "network is unreachable",
            "connection refused",
            "no route to host",
            "connection reset",
            "dns",
            "eastmoney",
            "quote.eastmoney.com",
            "push2.eastmoney.com",
            "push2his.eastmoney.com",
            "10jqka",
        )

        seen: set[int] = set()
        current: BaseException | None = exc
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            name = type(current).__name__
            module = type(current).__module__
            message = str(current).lower()

            if name in network_exception_names:
                return True
            if module.startswith(("requests", "urllib3", "urllib")) and any(
                token in message for token in network_message_tokens
            ):
                return True
            if isinstance(current, (socket.timeout, TimeoutError, ConnectionError)):
                return True
            if isinstance(current, OSError):
                if current.errno in {101, 110, 111, 113}:
                    return True
                if any(token in message for token in network_message_tokens):
                    return True

            if current.__cause__ is not None:
                current = current.__cause__
                continue
            current = current.__context__

        return False


class AkshareSectorDailyBarAdapter:
    """Narrow AKShare adapter for one CN industry or concept sector daily series."""

    source_name = AKSHARE_SOURCE_ID
    source_display_name = AKSHARE_SOURCE_NAME

    def __init__(
        self,
        *,
        fetch_industry_hist: Callable[..., Any] | None = None,
        fetch_concept_hist: Callable[..., Any] | None = None,
        fetch_industry_index_ths: Callable[..., Any] | None = None,
        fetch_concept_index_ths: Callable[..., Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self._fetch_industry_hist = fetch_industry_hist
        self._fetch_concept_hist = fetch_concept_hist
        self._fetch_industry_index_ths = fetch_industry_index_ths
        self._fetch_concept_index_ths = fetch_concept_index_ths
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if dataset != DatasetName.SECTOR_DAILY_BARS:
            raise ValueError(
                "Unsupported dataset for AkshareSectorDailyBarAdapter: "
                f"{dataset.value}"
            )

        sector_id, sector_type, sector_name = self._require_single_sector_identifier(symbols)
        rows = self._fetch_sector_rows_with_fallback(
            sector_type=sector_type,
            sector_name=sector_name,
            start_date=start_date,
            end_date=end_date,
        )
        records = self._normalize_sector_rows(
            rows=rows,
            sector_id=sector_id,
            dataset=dataset,
        )
        return self._filter_records_by_date(
            records=records,
            start_date=start_date,
            end_date=end_date,
        )

    def _resolve_fetch_fn(self, *, sector_type: str) -> Callable[..., Any]:
        if sector_type == "INDUSTRY":
            return self._resolve_fetch_industry_hist()
        return self._resolve_fetch_concept_hist()

    def _resolve_fetch_industry_hist(self) -> Callable[..., Any]:
        if self._fetch_industry_hist is not None:
            return self._fetch_industry_hist

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare sector daily-bar fetch."
            ) from exc

        if hasattr(ak, "stock_board_industry_hist_em"):
            return ak.stock_board_industry_hist_em
        raise RuntimeError(
            "AKShare industry sector daily-bar function is unavailable in this akshare version."
        )

    def _resolve_fetch_concept_hist(self) -> Callable[..., Any]:
        if self._fetch_concept_hist is not None:
            return self._fetch_concept_hist

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare sector daily-bar fetch."
            ) from exc

        if hasattr(ak, "stock_board_concept_hist_em"):
            return ak.stock_board_concept_hist_em
        raise RuntimeError(
            "AKShare concept sector daily-bar function is unavailable in this akshare version."
        )

    def _resolve_fetch_industry_index_ths(self) -> Callable[..., Any]:
        if self._fetch_industry_index_ths is not None:
            return self._fetch_industry_index_ths

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare sector daily-bar fetch."
            ) from exc

        if hasattr(ak, "stock_board_industry_index_ths"):
            return ak.stock_board_industry_index_ths
        raise RuntimeError(
            "AKShare industry sector fallback function is unavailable in this akshare version."
        )

    def _resolve_fetch_concept_index_ths(self) -> Callable[..., Any]:
        if self._fetch_concept_index_ths is not None:
            return self._fetch_concept_index_ths

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare sector daily-bar fetch."
            ) from exc

        if hasattr(ak, "stock_board_concept_index_ths"):
            return ak.stock_board_concept_index_ths
        raise RuntimeError(
            "AKShare concept sector fallback function is unavailable in this akshare version."
        )

    def _resolve_fallback_fetch_fn(self, *, sector_type: str) -> Callable[..., Any]:
        if sector_type == "INDUSTRY":
            return self._resolve_fetch_industry_index_ths()
        return self._resolve_fetch_concept_index_ths()

    def _fetch_sector_rows_with_fallback(
        self,
        *,
        sector_type: str,
        sector_name: str,
        start_date: date | None,
        end_date: date | None,
    ) -> list[Mapping[str, Any]]:
        fetch_fn = self._resolve_fetch_fn(sector_type=sector_type)
        try:
            return self._fetch_sector_rows(
                fetch_fn=fetch_fn,
                sector_type=sector_type,
                sector_name=sector_name,
                start_date=start_date,
                end_date=end_date,
            )
        except Exception as primary_exc:
            if not self._is_sector_hist_network_unavailable(primary_exc):
                raise

        fallback_fetch_fn = self._resolve_fallback_fetch_fn(sector_type=sector_type)
        return self._fetch_sector_rows(
            fetch_fn=fallback_fetch_fn,
            sector_type=sector_type,
            sector_name=sector_name,
            start_date=start_date,
            end_date=end_date,
        )

    def _fetch_sector_rows(
        self,
        *,
        fetch_fn: Callable[..., Any],
        sector_type: str,
        sector_name: str,
        start_date: date | None,
        end_date: date | None,
    ) -> list[Mapping[str, Any]]:
        accepted_args, supports_var_kwargs = self._inspect_callable(fetch_fn)
        kwargs: dict[str, Any] = {}

        symbol_arg = self._resolve_symbol_arg_name(
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        )
        kwargs[symbol_arg] = sector_name

        if start_date is not None and self._supports_arg(
            "start_date",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            kwargs["start_date"] = self._to_akshare_date(start_date)
        if end_date is not None and self._supports_arg(
            "end_date",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            kwargs["end_date"] = self._to_akshare_date(end_date)

        period_value = "日k" if sector_type == "INDUSTRY" else "daily"
        if self._supports_arg(
            "period",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            kwargs["period"] = period_value
        if self._supports_arg(
            "adjust",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            kwargs["adjust"] = ""

        raw_payload = fetch_fn(**kwargs)
        return self._payload_to_rows(raw_payload)

    def _inspect_callable(
        self,
        fn: Callable[..., Any],
    ) -> tuple[set[str], bool]:
        try:
            signature = inspect.signature(fn)
        except (TypeError, ValueError):
            return set(), True

        accepted_args: set[str] = set()
        supports_var_kwargs = False
        for parameter in signature.parameters.values():
            if parameter.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ):
                accepted_args.add(parameter.name)
            if parameter.kind == inspect.Parameter.VAR_KEYWORD:
                supports_var_kwargs = True
        return accepted_args, supports_var_kwargs

    def _resolve_symbol_arg_name(
        self,
        *,
        accepted_args: set[str],
        supports_var_kwargs: bool,
    ) -> str:
        for candidate in ("symbol", "name", "sector"):
            if self._supports_arg(
                candidate,
                accepted_args=accepted_args,
                supports_var_kwargs=supports_var_kwargs,
            ):
                return candidate
        raise RuntimeError(
            "AKShare sector daily-bar function does not accept a sector symbol/name argument."
        )

    def _supports_arg(
        self,
        arg_name: str,
        *,
        accepted_args: set[str],
        supports_var_kwargs: bool,
    ) -> bool:
        return supports_var_kwargs or arg_name in accepted_args

    def _require_single_sector_identifier(
        self,
        symbols: list[str] | None,
    ) -> tuple[str, str, str]:
        if symbols is None or len(symbols) == 0:
            raise ValueError(
                "AkshareSectorDailyBarAdapter requires exactly one sector identifier, got none."
            )
        if len(symbols) != 1:
            raise ValueError(
                "AkshareSectorDailyBarAdapter currently supports exactly one sector identifier."
            )

        symbol = symbols[0]
        if not isinstance(symbol, str) or symbol.strip() == "":
            raise ValueError("Sector identifier must be a non-empty string.")

        normalized = symbol.strip()
        if ":" not in normalized:
            raise ValueError(
                "Unsupported sector identifier format. Expected typed identifier like "
                "'INDUSTRY:小金属' or 'CONCEPT:绿色电力'."
            )

        prefix_raw, sector_name_raw = normalized.split(":", 1)
        prefix = prefix_raw.strip().upper()
        sector_name = sector_name_raw.strip()

        if prefix not in {"INDUSTRY", "CONCEPT"}:
            raise ValueError(
                f"Unsupported sector identifier prefix: {prefix!r}. "
                "Expected 'INDUSTRY' or 'CONCEPT'."
            )
        if sector_name == "":
            raise ValueError(
                "Malformed sector identifier: sector name must be non-empty after prefix."
            )
        if ":" in sector_name:
            raise ValueError(
                "Malformed sector identifier: sector name must not contain ':'."
            )

        return f"{prefix}:{sector_name}", prefix, sector_name

    def _to_akshare_date(self, value: date | None) -> str:
        if value is None:
            return ""
        return value.strftime("%Y%m%d")

    def _payload_to_rows(self, payload: Any) -> list[Mapping[str, Any]]:
        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "AKShare sector payload must be DataFrame-like or list[Mapping], "
                f"got {type(payload).__name__}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "AKShare sector payload row must be mapping. "
                    f"idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _normalize_sector_rows(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        sector_id: str,
        dataset: DatasetName,
    ) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version

        for idx, row in enumerate(rows):
            high = self._to_float(self._pick(row, idx, "high", "最高", "最高价"))
            low = self._to_float(self._pick(row, idx, "low", "最低", "最低价"))
            if high < low:
                raise ValueError(
                    f"Invalid OHLC range in sector row {idx}: high={high} < low={low}."
                )

            record: dict[str, Any] = {
                "sector_id": sector_id,
                "market": "CN_SECTOR",
                "trade_date": self._normalize_trade_date(
                    self._pick(row, idx, "date", "日期", "trade_date")
                ),
                "open": self._to_float(self._pick(row, idx, "open", "开盘", "开盘价")),
                "high": high,
                "low": low,
                "close": self._to_float(self._pick(row, idx, "close", "收盘", "收盘价")),
                "source": AKSHARE_SOURCE_ID,
                "ingested_at": ingested_at,
                "schema_version": schema_version,
            }

            volume = self._pick_optional(row, "volume", "成交量")
            if volume is not None:
                record["volume"] = self._to_float(volume)

            amount = self._pick_optional(row, "amount", "成交额")
            if amount is not None:
                record["amount"] = self._to_float(amount)

            source_ts = self._pick_optional(row, "source_ts", "更新时间", "update_time")
            if source_ts is not None:
                record["source_ts"] = self._normalize_source_ts(source_ts)

            normalized.append(record)

        return normalized

    def _filter_records_by_date(
        self,
        *,
        records: Sequence[Mapping[str, Any]],
        start_date: date | None,
        end_date: date | None,
    ) -> list[dict[str, Any]]:
        filtered: list[dict[str, Any]] = []
        for record in records:
            trade_date = date.fromisoformat(str(record["trade_date"]))
            if start_date is not None and trade_date < start_date:
                continue
            if end_date is not None and trade_date > end_date:
                continue
            filtered.append(dict(record))
        return filtered

    def _pick(
        self,
        row: Mapping[str, Any],
        row_idx: int,
        *keys: str,
    ) -> Any:
        for key in keys:
            if key in row:
                return row[key]
        raise ValueError(
            f"Missing required source field in sector row {row_idx}: one of {keys!r}"
        )

    def _is_sector_hist_network_unavailable(self, exc: BaseException) -> bool:
        network_exception_names = {
            "ProxyError",
            "ConnectionError",
            "ConnectTimeout",
            "ReadTimeout",
            "Timeout",
            "MaxRetryError",
            "NewConnectionError",
            "NameResolutionError",
            "SSLError",
        }
        network_message_tokens = (
            "proxy",
            "timed out",
            "timeout",
            "name resolution",
            "temporary failure in name resolution",
            "failed to establish a new connection",
            "max retries exceeded",
            "network is unreachable",
            "connection refused",
            "no route to host",
            "connection reset",
            "dns",
            "eastmoney",
            "push2.eastmoney.com",
            "push2his.eastmoney.com",
            "quote.eastmoney.com",
        )

        seen: set[int] = set()
        current: BaseException | None = exc
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            name = type(current).__name__
            module = type(current).__module__
            message = str(current).lower()

            if name in network_exception_names:
                return True
            if module.startswith(("requests", "urllib3")) and any(
                token in message for token in network_message_tokens
            ):
                return True
            if isinstance(current, (socket.timeout, TimeoutError, ConnectionError)):
                return True
            if isinstance(current, OSError):
                if current.errno in {101, 110, 111, 113}:
                    return True
                if any(token in message for token in network_message_tokens):
                    return True

            if current.__cause__ is not None:
                current = current.__cause__
                continue
            current = current.__context__

        return False

    def _pick_optional(
        self,
        row: Mapping[str, Any],
        *keys: str,
    ) -> Any | None:
        for key in keys:
            if key not in row:
                continue
            value = row[key]
            if value is None:
                return None
            if isinstance(value, str) and value.strip() == "":
                return None
            return value
        return None

    def _to_float(self, value: Any) -> float:
        if isinstance(value, bool):
            raise ValueError(f"Invalid numeric value type: {value!r}")
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            normalized = value.strip().replace(",", "")
            if normalized == "":
                raise ValueError("Invalid numeric value: empty string")
            try:
                return float(normalized)
            except ValueError as exc:
                raise ValueError(f"Invalid numeric value: {value!r}") from exc
        raise ValueError(f"Invalid numeric value type: {type(value).__name__}")

    def _normalize_trade_date(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError("Invalid trade date value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                return date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                ).isoformat()
            try:
                return date.fromisoformat(stripped).isoformat()
            except ValueError as exc:
                raise ValueError(f"Invalid trade date value: {value!r}") from exc
        raise ValueError(f"Invalid trade date value type: {type(value).__name__}")

    def _normalize_source_ts(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time()).isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError("Invalid source_ts value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                parsed_date = date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
                return datetime.combine(parsed_date, datetime.min.time()).isoformat()
            try:
                return datetime.fromisoformat(stripped).isoformat()
            except ValueError as exc:
                raise ValueError(f"Invalid source_ts value: {value!r}") from exc
        raise ValueError(f"Invalid source_ts value type: {type(value).__name__}")


class AkshareETFFundNavSnapshotAdapter:
    """Narrow AKShare adapter for one ETF/fund NAV history series."""

    source_name = AKSHARE_SOURCE_ID
    source_display_name = AKSHARE_SOURCE_NAME

    def __init__(
        self,
        *,
        fetch_fund_nav: Callable[..., Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self._fetch_fund_nav = fetch_fund_nav
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if dataset != DatasetName.FUND_NAV_SNAPSHOT:
            raise ValueError(
                "Unsupported dataset for AkshareETFFundNavSnapshotAdapter: "
                f"{dataset.value}"
            )

        canonical_fund_code, akshare_fund_code = self._require_single_fund_code(symbols)
        fetch_fn = self._resolve_fetch_fund_nav()
        raw_payload = self._call_fetch_fund_nav(
            fetch_fn=fetch_fn,
            fund_code=akshare_fund_code,
            start_date=start_date,
            end_date=end_date,
        )
        rows = self._payload_to_rows(raw_payload)
        return self._normalize_fund_nav_rows(
            rows=rows,
            fund_code=canonical_fund_code,
            dataset=dataset,
        )

    def _resolve_fetch_fund_nav(self) -> Callable[..., Any]:
        if self._fetch_fund_nav is not None:
            return self._fetch_fund_nav

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare ETF/fund NAV fetch."
            ) from exc

        if hasattr(ak, "fund_etf_fund_info_em"):
            return ak.fund_etf_fund_info_em
        if hasattr(ak, "fund_em_etf_fund_info"):
            return ak.fund_em_etf_fund_info
        raise RuntimeError(
            "AKShare ETF/fund NAV function is unavailable in this akshare version."
        )

    def _call_fetch_fund_nav(
        self,
        *,
        fetch_fn: Callable[..., Any],
        fund_code: str,
        start_date: date | None,
        end_date: date | None,
    ) -> Any:
        accepted_args, supports_var_kwargs = self._inspect_callable(fetch_fn)
        kwargs: dict[str, Any] = {}

        fund_arg = self._resolve_fund_arg_name(
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        )
        kwargs[fund_arg] = fund_code

        if start_date is not None and self._supports_arg(
            "start_date",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            kwargs["start_date"] = self._to_akshare_date(start_date)
        if end_date is not None and self._supports_arg(
            "end_date",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            kwargs["end_date"] = self._to_akshare_date(end_date)

        return fetch_fn(**kwargs)

    def _inspect_callable(
        self,
        fn: Callable[..., Any],
    ) -> tuple[set[str], bool]:
        try:
            signature = inspect.signature(fn)
        except (TypeError, ValueError):
            return set(), True

        accepted_args: set[str] = set()
        supports_var_kwargs = False
        for parameter in signature.parameters.values():
            if parameter.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ):
                accepted_args.add(parameter.name)
            if parameter.kind == inspect.Parameter.VAR_KEYWORD:
                supports_var_kwargs = True
        return accepted_args, supports_var_kwargs

    def _resolve_fund_arg_name(
        self,
        *,
        accepted_args: set[str],
        supports_var_kwargs: bool,
    ) -> str:
        if self._supports_arg(
            "fund",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            return "fund"
        if self._supports_arg(
            "symbol",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            return "symbol"
        raise RuntimeError(
            "AKShare ETF/fund NAV function does not accept 'fund' or 'symbol' argument."
        )

    def _supports_arg(
        self,
        arg_name: str,
        *,
        accepted_args: set[str],
        supports_var_kwargs: bool,
    ) -> bool:
        return supports_var_kwargs or arg_name in accepted_args

    def _require_single_fund_code(
        self,
        symbols: list[str] | None,
    ) -> tuple[str, str]:
        if symbols is None or len(symbols) == 0:
            raise ValueError(
                "AkshareETFFundNavSnapshotAdapter requires exactly one fund code, got none."
            )
        if len(symbols) != 1:
            raise ValueError(
                "AkshareETFFundNavSnapshotAdapter currently supports exactly one fund code."
            )

        symbol = symbols[0]
        if not isinstance(symbol, str) or symbol.strip() == "":
            raise ValueError("Fund code must be a non-empty string.")

        normalized = symbol.strip().upper()
        if "." in normalized:
            code, market = normalized.split(".", 1)
            if market != "ETF_CN":
                raise ValueError(
                    f"Unsupported ETF/fund market suffix: {market!r}. Expected '.ETF_CN'."
                )
        else:
            code = normalized

        if not code.isdigit() or len(code) != 6:
            raise ValueError(
                f"Unsupported ETF/fund code format: {normalized!r}. "
                "Expected 6-digit code like '510300' or '510300.ETF_CN'."
            )

        canonical = f"{code}.ETF_CN"
        return canonical, code

    def _to_akshare_date(self, value: date | None) -> str:
        if value is None:
            return ""
        return value.strftime("%Y%m%d")

    def _payload_to_rows(self, payload: Any) -> list[Mapping[str, Any]]:
        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "AKShare ETF/fund NAV payload must be DataFrame-like or list[Mapping], "
                f"got {type(payload).__name__}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "AKShare ETF/fund NAV payload row must be mapping. "
                    f"idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _normalize_fund_nav_rows(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        fund_code: str,
        dataset: DatasetName,
    ) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version

        for idx, row in enumerate(rows):
            record: dict[str, Any] = {
                "fund_code": fund_code,
                "market": "ETF_CN",
                "trade_date": self._normalize_trade_date(
                    self._pick(row, idx, "净值日期", "trade_date", "date")
                ),
                "nav": self._to_float(self._pick(row, idx, "单位净值", "nav", "unit_nav")),
                "source": AKSHARE_SOURCE_ID,
                "ingested_at": ingested_at,
                "schema_version": schema_version,
            }

            accumulated_nav = self._pick_optional(row, "累计净值", "accumulated_nav")
            if accumulated_nav is not None:
                record["accumulated_nav"] = self._to_float(accumulated_nav)

            shares_outstanding = self._pick_optional(
                row,
                "shares_outstanding",
                "基金份额",
                "份额",
            )
            if shares_outstanding is not None:
                record["shares_outstanding"] = self._to_float(shares_outstanding)

            fund_scale = self._pick_optional(row, "fund_scale", "基金规模", "规模")
            if fund_scale is not None:
                record["fund_scale"] = self._to_float(fund_scale)

            source_ts = self._pick_optional(
                row,
                "source_ts",
                "更新时间",
                "update_time",
            )
            if source_ts is not None:
                record["source_ts"] = self._normalize_source_ts(source_ts)

            normalized.append(record)

        return normalized

    def _pick(
        self,
        row: Mapping[str, Any],
        row_idx: int,
        *keys: str,
    ) -> Any:
        for key in keys:
            if key in row:
                return row[key]
        raise ValueError(
            f"Missing required source field in ETF/fund NAV row {row_idx}: one of {keys!r}"
        )

    def _pick_optional(
        self,
        row: Mapping[str, Any],
        *keys: str,
    ) -> Any | None:
        for key in keys:
            if key not in row:
                continue
            value = row[key]
            if value is None:
                return None
            if isinstance(value, str) and value.strip() == "":
                return None
            return value
        return None

    def _to_float(self, value: Any) -> float:
        if isinstance(value, bool):
            raise ValueError(f"Invalid numeric value type: {value!r}")
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            normalized = value.strip().replace(",", "")
            if normalized == "":
                raise ValueError("Invalid numeric value: empty string")
            try:
                return float(normalized)
            except ValueError as exc:
                raise ValueError(f"Invalid numeric value: {value!r}") from exc
        raise ValueError(f"Invalid numeric value type: {type(value).__name__}")

    def _normalize_trade_date(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError("Invalid trade date value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                return date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                ).isoformat()
            try:
                return date.fromisoformat(stripped).isoformat()
            except ValueError as exc:
                raise ValueError(f"Invalid trade date value: {value!r}") from exc
        raise ValueError(f"Invalid trade date value type: {type(value).__name__}")

    def _normalize_source_ts(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time()).isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError("Invalid source_ts value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                parsed_date = date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
                return datetime.combine(parsed_date, datetime.min.time()).isoformat()
            try:
                return datetime.fromisoformat(stripped).isoformat()
            except ValueError as exc:
                raise ValueError(f"Invalid source_ts value: {value!r}") from exc
        raise ValueError(f"Invalid source_ts value type: {type(value).__name__}")


class AkshareETFFundHoldingsAdapter:
    """Narrow AKShare adapter for one ETF/fund holdings slice."""

    source_name = AKSHARE_SOURCE_ID
    source_display_name = AKSHARE_SOURCE_NAME

    _PRIMARY_ROUTE_NAME = "fund_portfolio_hold_em"

    def __init__(
        self,
        *,
        fetch_fund_holdings: Callable[..., Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
        max_records_per_slice: int = 120,
    ) -> None:
        if max_records_per_slice <= 0:
            raise ValueError("max_records_per_slice must be positive.")

        self._fetch_fund_holdings = fetch_fund_holdings
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._max_records_per_slice = max_records_per_slice
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if dataset != DatasetName.FUND_HOLDINGS:
            raise ValueError(
                "Unsupported dataset for AkshareETFFundHoldingsAdapter: "
                f"{dataset.value}"
            )

        canonical_fund_code, akshare_fund_code = self._require_single_fund_code(symbols)
        fetch_fn = self._resolve_fetch_fund_holdings()
        raw_rows = self._fetch_rows_for_fund_code(
            fetch_fn=fetch_fn,
            fund_code=akshare_fund_code,
            start_date=start_date,
            end_date=end_date,
        )
        records = self._normalize_fund_holdings_rows(
            rows=raw_rows,
            fund_code=canonical_fund_code,
            dataset=dataset,
        )
        records = self._filter_records_by_date(
            records=records,
            start_date=start_date,
            end_date=end_date,
        )
        return self._bounded_single_reporting_period_slice(records=records)

    def _resolve_fetch_fund_holdings(self) -> Callable[..., Any]:
        if self._fetch_fund_holdings is not None:
            return self._fetch_fund_holdings

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare ETF/fund holdings fetch."
            ) from exc

        if hasattr(ak, self._PRIMARY_ROUTE_NAME):
            return getattr(ak, self._PRIMARY_ROUTE_NAME)
        if hasattr(ak, "fund_em_portfolio_hold"):
            return getattr(ak, "fund_em_portfolio_hold")
        raise RuntimeError(
            "AKShare ETF/fund holdings function is unavailable in this akshare version."
        )

    def _fetch_rows_for_fund_code(
        self,
        *,
        fetch_fn: Callable[..., Any],
        fund_code: str,
        start_date: date | None,
        end_date: date | None,
    ) -> list[Mapping[str, Any]]:
        years_to_try = self._years_to_try(start_date=start_date, end_date=end_date)
        route_failures: list[str] = []
        first_network_exc: BaseException | None = None

        for year in years_to_try:
            try:
                payload = self._call_fetch_fund_holdings(
                    fetch_fn=fetch_fn,
                    fund_code=fund_code,
                    year=year,
                )
            except Exception as exc:
                if not self._is_fund_holdings_network_unavailable(exc):
                    raise
                if first_network_exc is None:
                    first_network_exc = exc
                route_failures.append(f"{self._PRIMARY_ROUTE_NAME}[year={year}]={type(exc).__name__}: {exc}")
                continue

            rows = self._payload_to_rows(payload)
            if rows:
                return rows

        if route_failures:
            evidence = " | ".join(route_failures[:2])
            if len(route_failures) > 2:
                evidence = f"{evidence} | ... total={len(route_failures)} failures"
            raise RuntimeError(
                "AKShare ETF/fund holdings routes unavailable for requested fund symbol: "
                f"{evidence}"
            ) from first_network_exc
        return []

    def _years_to_try(
        self,
        *,
        start_date: date | None,
        end_date: date | None,
    ) -> tuple[int, ...]:
        if end_date is not None:
            primary_year = end_date.year
        elif start_date is not None:
            primary_year = start_date.year
        else:
            primary_year = self._now_fn().year

        fallback_year = primary_year - 1
        if fallback_year <= 1990:
            return (primary_year,)
        if fallback_year == primary_year:
            return (primary_year,)
        return (primary_year, fallback_year)

    def _call_fetch_fund_holdings(
        self,
        *,
        fetch_fn: Callable[..., Any],
        fund_code: str,
        year: int,
    ) -> Any:
        accepted_args, supports_var_kwargs = self._inspect_callable(fetch_fn)
        kwargs: dict[str, Any] = {}

        symbol_arg = self._resolve_symbol_arg_name(
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        )
        kwargs[symbol_arg] = fund_code

        if self._supports_arg(
            "date",
            accepted_args=accepted_args,
            supports_var_kwargs=supports_var_kwargs,
        ):
            kwargs["date"] = str(year)
        return fetch_fn(**kwargs)

    def _inspect_callable(
        self,
        fn: Callable[..., Any],
    ) -> tuple[set[str], bool]:
        try:
            signature = inspect.signature(fn)
        except (TypeError, ValueError):
            return set(), True

        accepted_args: set[str] = set()
        supports_var_kwargs = False
        for parameter in signature.parameters.values():
            if parameter.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ):
                accepted_args.add(parameter.name)
            if parameter.kind == inspect.Parameter.VAR_KEYWORD:
                supports_var_kwargs = True
        return accepted_args, supports_var_kwargs

    def _resolve_symbol_arg_name(
        self,
        *,
        accepted_args: set[str],
        supports_var_kwargs: bool,
    ) -> str:
        for candidate in ("symbol", "fund", "code", "fund_code"):
            if self._supports_arg(
                candidate,
                accepted_args=accepted_args,
                supports_var_kwargs=supports_var_kwargs,
            ):
                return candidate
        raise RuntimeError(
            "AKShare ETF/fund holdings function does not accept symbol/fund argument."
        )

    def _supports_arg(
        self,
        arg_name: str,
        *,
        accepted_args: set[str],
        supports_var_kwargs: bool,
    ) -> bool:
        return supports_var_kwargs or arg_name in accepted_args

    def _require_single_fund_code(
        self,
        symbols: list[str] | None,
    ) -> tuple[str, str]:
        if symbols is None or len(symbols) == 0:
            raise ValueError(
                "AkshareETFFundHoldingsAdapter requires exactly one fund code, got none."
            )
        if len(symbols) != 1:
            raise ValueError(
                "AkshareETFFundHoldingsAdapter currently supports exactly one fund code."
            )

        symbol = symbols[0]
        if not isinstance(symbol, str) or symbol.strip() == "":
            raise ValueError("Fund code must be a non-empty string.")

        normalized = symbol.strip().upper()
        if "." in normalized:
            code, market = normalized.split(".", 1)
            if market != "ETF_CN":
                raise ValueError(
                    f"Unsupported ETF/fund market suffix: {market!r}. Expected '.ETF_CN'."
                )
        else:
            code = normalized

        if not code.isdigit() or len(code) != 6:
            raise ValueError(
                f"Unsupported ETF/fund code format: {normalized!r}. "
                "Expected 6-digit code like '510300' or '510300.ETF_CN'."
            )

        canonical = f"{code}.ETF_CN"
        return canonical, code

    def _payload_to_rows(self, payload: Any) -> list[Mapping[str, Any]]:
        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "AKShare ETF/fund holdings payload must be DataFrame-like or list[Mapping], "
                f"got {type(payload).__name__}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "AKShare ETF/fund holdings payload row must be mapping. "
                    f"idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _normalize_fund_holdings_rows(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        fund_code: str,
        dataset: DatasetName,
    ) -> list[dict[str, Any]]:
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version
        normalized_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}

        for idx, row in enumerate(rows):
            report_date = self._normalize_report_date(
                self._pick(row, idx, "report_date", "季度", "报告期"),
                field_name="report_date",
            )
            holding_symbol = self._normalize_a_share_symbol(
                self._pick(row, idx, "symbol", "股票代码", "证券代码"),
            )
            weight = self._normalize_weight(
                self._pick(row, idx, "weight", "占净值比例", "占净值比例(%)"),
            )

            record: dict[str, Any] = {
                "fund_code": fund_code,
                "symbol": holding_symbol,
                "market": "CN",
                "report_date": report_date,
                "weight": weight,
                "source": AKSHARE_SOURCE_ID,
                "ingested_at": ingested_at,
                "schema_version": schema_version,
            }

            shares = self._pick_optional(row, "shares", "持股数", "持仓股数")
            if shares is not None:
                record["shares"] = self._to_nonnegative_float(shares, field_name="shares")

            position_value = self._pick_optional(
                row,
                "position_value",
                "持仓市值",
                "持仓金额",
            )
            if position_value is not None:
                record["position_value"] = self._to_nonnegative_float(
                    position_value,
                    field_name="position_value",
                )

            source_ts = self._pick_optional(row, "source_ts", "更新时间", "update_time")
            if source_ts is not None:
                record["source_ts"] = self._normalize_source_ts(source_ts)

            dedupe_key = (str(record["fund_code"]), str(record["symbol"]), str(record["report_date"]))
            existing = normalized_by_key.get(dedupe_key)
            if existing is None:
                normalized_by_key[dedupe_key] = record
                continue

            if self._is_conflicting_duplicate(existing=existing, candidate=record):
                raise ValueError(
                    "Conflicting duplicate ETF/fund holdings row detected: "
                    f"key={dedupe_key!r}."
                )
            normalized_by_key[dedupe_key] = self._select_preferred_duplicate_record(
                existing=existing,
                candidate=record,
            )

        return list(normalized_by_key.values())

    def _pick(
        self,
        row: Mapping[str, Any],
        row_idx: int,
        *keys: str,
    ) -> Any:
        for key in keys:
            if key in row:
                value = row[key]
                if not self._is_missing_value(value):
                    return value
        raise ValueError(
            "Missing required source field in ETF/fund holdings row "
            f"{row_idx}: one of {keys!r}"
        )

    def _pick_optional(
        self,
        row: Mapping[str, Any],
        *keys: str,
    ) -> Any | None:
        for key in keys:
            if key not in row:
                continue
            value = row[key]
            if self._is_missing_value(value):
                return None
            return value
        return None

    def _normalize_report_date(self, value: Any, *, field_name: str) -> str:
        if self._is_missing_value(value):
            raise ValueError(f"Invalid {field_name} value: missing")
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError(f"Invalid {field_name} value: empty string")

            quarter_match = re.search(r"(\d{4})年\s*([1-4])季度", stripped)
            if quarter_match is not None:
                year = int(quarter_match.group(1))
                quarter = int(quarter_match.group(2))
                month_day = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}[quarter]
                return f"{year}-{month_day}"

            if "年中报" in stripped or "半年报" in stripped:
                year_match = re.search(r"(\d{4})年", stripped)
                if year_match is not None:
                    return f"{year_match.group(1)}-06-30"

            if "年报" in stripped or "年度" in stripped:
                year_match = re.search(r"(\d{4})年", stripped)
                if year_match is not None:
                    return f"{year_match.group(1)}-12-31"

            if "一季报" in stripped:
                year_match = re.search(r"(\d{4})年", stripped)
                if year_match is not None:
                    return f"{year_match.group(1)}-03-31"
            if "三季报" in stripped:
                year_match = re.search(r"(\d{4})年", stripped)
                if year_match is not None:
                    return f"{year_match.group(1)}-09-30"

            if len(stripped) == 8 and stripped.isdigit():
                return date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                ).isoformat()

            try:
                return date.fromisoformat(stripped).isoformat()
            except ValueError as exc:
                raise ValueError(f"Invalid {field_name} value: {value!r}") from exc

        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _normalize_a_share_symbol(self, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError(f"Invalid symbol value type: {type(value).__name__}")
        normalized = value.strip().upper()
        if normalized == "":
            raise ValueError("Invalid symbol value: empty string")

        if "." in normalized:
            code, market = normalized.split(".", 1)
            if not code.isdigit() or len(code) != 6:
                raise ValueError(f"Invalid symbol value: {value!r}")
            if market not in {"SH", "SZ", "BJ"}:
                raise ValueError(f"Unsupported symbol market suffix: {market!r}")
            return f"{code}.{market}"

        if not normalized.isdigit() or len(normalized) != 6:
            raise ValueError(
                f"Unsupported holding symbol format: {value!r}. Expected A-share 6-digit code."
            )

        if normalized.startswith("6"):
            return f"{normalized}.SH"
        if normalized.startswith(("0", "3")):
            if normalized.startswith("399"):
                raise ValueError(f"Index symbol is unsupported for holdings record: {value!r}")
            return f"{normalized}.SZ"
        if normalized.startswith(("4", "8", "9")):
            return f"{normalized}.BJ"
        raise ValueError(f"Unsupported A-share holding code prefix: {value!r}")

    def _normalize_weight(self, value: Any) -> float:
        weight = self._to_float(value, field_name="weight")
        if weight < 0.0 or weight > 100.0:
            raise ValueError(f"Invalid weight value: {value!r}. Expected range [0, 100].")
        return weight

    def _to_nonnegative_float(self, value: Any, *, field_name: str) -> float:
        numeric = self._to_float(value, field_name=field_name)
        if numeric < 0.0:
            raise ValueError(f"Invalid {field_name} value: {value!r}. Expected nonnegative.")
        return numeric

    def _to_float(self, value: Any, *, field_name: str) -> float:
        if isinstance(value, bool):
            raise ValueError(f"Invalid {field_name} value type: bool")
        if isinstance(value, (int, float)):
            numeric = float(value)
        elif isinstance(value, str):
            normalized = (
                value.strip()
                .replace(",", "")
                .replace("%", "")
                .replace("股", "")
                .replace("万", "")
                .replace("亿元", "")
                .replace("元", "")
            )
            if normalized == "":
                raise ValueError(f"Invalid {field_name} value: empty string")
            try:
                numeric = float(normalized)
            except ValueError as exc:
                raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
        else:
            raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

        if not math.isfinite(numeric):
            raise ValueError(f"Invalid {field_name} value: {value!r}")
        return numeric

    def _normalize_source_ts(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time()).isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError("Invalid source_ts value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                parsed_date = date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
                return datetime.combine(parsed_date, datetime.min.time()).isoformat()
            try:
                return datetime.fromisoformat(stripped).isoformat()
            except ValueError as exc:
                raise ValueError(f"Invalid source_ts value: {value!r}") from exc
        raise ValueError(f"Invalid source_ts value type: {type(value).__name__}")

    def _filter_records_by_date(
        self,
        *,
        records: Sequence[Mapping[str, Any]],
        start_date: date | None,
        end_date: date | None,
    ) -> list[dict[str, Any]]:
        filtered: list[dict[str, Any]] = []
        for record in records:
            report_dt = date.fromisoformat(str(record["report_date"]))
            if start_date is not None and report_dt < start_date:
                continue
            if end_date is not None and report_dt > end_date:
                continue
            filtered.append(dict(record))
        return filtered

    def _bounded_single_reporting_period_slice(
        self,
        *,
        records: Sequence[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        if not records:
            return []
        latest_report_date = max(str(record["report_date"]) for record in records)
        latest_records = [
            dict(record)
            for record in records
            if str(record["report_date"]) == latest_report_date
        ]
        latest_records.sort(
            key=lambda item: (
                float(item["weight"]),
                str(item["symbol"]),
            ),
            reverse=True,
        )
        return latest_records[: self._max_records_per_slice]

    def _is_missing_value(self, value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, str) and value.strip().lower() in {"", "nan", "nat", "none", "null"}:
            return True
        if type(value).__name__ == "NaTType":
            return True
        try:
            if value != value:
                return True
        except Exception:
            pass
        return False

    def _is_conflicting_duplicate(
        self,
        *,
        existing: Mapping[str, Any],
        candidate: Mapping[str, Any],
    ) -> bool:
        comparable_fields = (
            "fund_code",
            "symbol",
            "market",
            "report_date",
            "weight",
            "shares",
            "position_value",
            "source",
        )
        return any(existing.get(field) != candidate.get(field) for field in comparable_fields)

    def _select_preferred_duplicate_record(
        self,
        *,
        existing: dict[str, Any],
        candidate: dict[str, Any],
    ) -> dict[str, Any]:
        existing_source_ts = existing.get("source_ts")
        candidate_source_ts = candidate.get("source_ts")
        if existing_source_ts is None and candidate_source_ts is not None:
            return candidate
        if existing_source_ts is not None and candidate_source_ts is None:
            return existing
        if existing_source_ts is None and candidate_source_ts is None:
            return existing
        if not isinstance(existing_source_ts, str) or not isinstance(candidate_source_ts, str):
            return existing
        if candidate_source_ts > existing_source_ts:
            return candidate
        return existing

    def _is_fund_holdings_network_unavailable(self, exc: BaseException) -> bool:
        network_exception_names = {
            "ProxyError",
            "ConnectionError",
            "ConnectTimeout",
            "ReadTimeout",
            "Timeout",
            "MaxRetryError",
            "NewConnectionError",
            "NameResolutionError",
            "SSLError",
        }
        network_message_tokens = (
            "proxy",
            "timed out",
            "timeout",
            "name resolution",
            "temporary failure in name resolution",
            "failed to establish a new connection",
            "max retries exceeded",
            "network is unreachable",
            "connection refused",
            "no route to host",
            "connection reset",
            "dns",
            "eastmoney",
            "fundf10.eastmoney.com",
            "fund_portfolio_hold_em",
        )

        seen: set[int] = set()
        current: BaseException | None = exc
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            name = type(current).__name__
            module = type(current).__module__
            message = str(current).lower()

            if name in network_exception_names:
                return True
            if module.startswith(("requests", "urllib3")) and any(
                token in message for token in network_message_tokens
            ):
                return True
            if isinstance(current, (socket.timeout, TimeoutError, ConnectionError, ssl.SSLError)):
                return True
            if isinstance(current, OSError):
                if current.errno in {101, 104, 110, 111, 113}:
                    return True
                if any(token in message for token in network_message_tokens):
                    return True

            if current.__cause__ is not None:
                current = current.__cause__
                continue
            current = current.__context__
        return False


class AkshareAShareTradingCalendarAdapter:
    """Narrow AKShare adapter for A-share trading calendar only."""

    source_name = AKSHARE_SOURCE_ID
    source_display_name = AKSHARE_SOURCE_NAME

    def __init__(
        self,
        *,
        fetch_trade_dates: Callable[..., Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self._fetch_trade_dates = fetch_trade_dates
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if dataset != DatasetName.TRADING_CALENDAR:
            raise ValueError(
                "Unsupported dataset for AkshareAShareTradingCalendarAdapter: "
                f"{dataset.value}"
            )
        if symbols is not None:
            raise ValueError(
                "AkshareAShareTradingCalendarAdapter does not accept symbols input "
                "for market-level trading calendar fetch."
            )

        fetch_fn = self._resolve_fetch_trade_dates()
        raw_payload = fetch_fn()
        all_dates = self._payload_to_trade_dates(raw_payload)
        filtered_dates = self._filter_dates(
            dates=all_dates,
            start_date=start_date,
            end_date=end_date,
        )
        if not filtered_dates:
            raise ValueError(
                "AKShare trading calendar payload produced no usable trade dates "
                "after date filtering."
            )
        return self._normalize_trading_calendar_records(
            dataset=dataset,
            trade_dates=filtered_dates,
        )

    def _resolve_fetch_trade_dates(self) -> Callable[..., Any]:
        if self._fetch_trade_dates is not None:
            return self._fetch_trade_dates

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare calendar fetch."
            ) from exc

        if hasattr(ak, "tool_trade_date_hist_sina"):
            return ak.tool_trade_date_hist_sina
        raise RuntimeError(
            "AKShare trading calendar function is unavailable in this akshare version."
        )

    def _payload_to_trade_dates(self, payload: Any) -> list[date]:
        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "AKShare calendar payload must be DataFrame-like, list of mappings, "
                f"or list of date-like values; got {type(payload).__name__}."
            )

        parsed_dates: list[date] = []
        for idx, row in enumerate(candidate):
            if isinstance(row, Mapping):
                date_value = self._pick_trade_date_value(row=row, row_idx=idx)
            else:
                date_value = row
            parsed_dates.append(self._to_date(value=date_value))

        if not parsed_dates:
            return []
        unique_sorted = sorted(set(parsed_dates))
        return unique_sorted

    def _pick_trade_date_value(
        self,
        *,
        row: Mapping[str, Any],
        row_idx: int,
    ) -> Any:
        for key in ("trade_date", "date", "日期"):
            if key in row:
                return row[key]
        raise ValueError(
            "Missing required trade-date field in calendar payload row "
            f"{row_idx}: expected one of ('trade_date', 'date', '日期')."
        )

    def _to_date(self, *, value: Any) -> date:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError("Invalid trade date value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                return date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
            try:
                return date.fromisoformat(stripped)
            except ValueError as exc:
                raise ValueError(f"Invalid trade date value: {value!r}") from exc
        raise ValueError(f"Invalid trade date value type: {type(value).__name__}")

    def _filter_dates(
        self,
        *,
        dates: Sequence[date],
        start_date: date | None,
        end_date: date | None,
    ) -> list[date]:
        filtered: list[date] = []
        for trade_date in dates:
            if start_date is not None and trade_date < start_date:
                continue
            if end_date is not None and trade_date > end_date:
                continue
            filtered.append(trade_date)
        return filtered

    def _normalize_trading_calendar_records(
        self,
        *,
        dataset: DatasetName,
        trade_dates: Sequence[date],
    ) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version

        for idx, trade_date in enumerate(trade_dates):
            previous_trade_date = (
                trade_dates[idx - 1] if idx > 0 else trade_date
            )
            next_trade_date = (
                trade_dates[idx + 1] if idx < len(trade_dates) - 1 else trade_date
            )
            records.append(
                {
                    "market": "CN",
                    "trade_date": trade_date.isoformat(),
                    "is_open": True,
                    "session_type": "full",
                    "previous_trade_date": previous_trade_date.isoformat(),
                    "next_trade_date": next_trade_date.isoformat(),
                    "source": AKSHARE_SOURCE_ID,
                    "ingested_at": ingested_at,
                    "schema_version": schema_version,
                }
            )
        return records


class AkshareGlobalEquitySnapshotAdapter:
    """Narrow AKShare adapter for concise global equity snapshot records."""

    source_name = AKSHARE_SOURCE_ID
    source_display_name = AKSHARE_SOURCE_NAME

    _DEFAULT_MARKET = "US"
    _DEFAULT_CURRENCY = "USD"
    _DEFAULT_REGION = "GLOBAL"
    _DEFAULT_EXCHANGE = "US"

    _SOURCE_CODE_EXCHANGE_PREFIX_MAP: dict[str, str] = {
        "105": "NASDAQ",
        "106": "NYSE",
        "107": "AMEX",
    }

    _UNSUPPORTED_MARKET_SUFFIXES = {
        "CN",
        "CN_A",
        "CN_INDEX",
        "ETF_CN",
        "HK",
        "SH",
        "SZ",
        "BJ",
    }

    _TICKER_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9._-]{0,23}$")

    def __init__(
        self,
        *,
        fetch_global_equity_spot: Callable[..., Any] | None = None,
        fetch_global_equity_spot_em: Callable[..., Any] | None = None,
        fetch_global_equity_spot_sina: Callable[..., Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
        max_records_without_symbols: int = 200,
    ) -> None:
        if max_records_without_symbols <= 0:
            raise ValueError("max_records_without_symbols must be positive.")
        if fetch_global_equity_spot is not None and (
            fetch_global_equity_spot_em is not None
            or fetch_global_equity_spot_sina is not None
        ):
            raise ValueError(
                "Provide either fetch_global_equity_spot or explicit route-specific "
                "callables (fetch_global_equity_spot_em/fetch_global_equity_spot_sina), "
                "not both."
            )

        self._fetch_global_equity_spot = fetch_global_equity_spot
        self._fetch_global_equity_spot_em = fetch_global_equity_spot_em
        self._fetch_global_equity_spot_sina = fetch_global_equity_spot_sina
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._max_records_without_symbols = max_records_without_symbols
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if dataset != DatasetName.GLOBAL_EQUITY_SNAPSHOT:
            raise ValueError(
                "Unsupported dataset for AkshareGlobalEquitySnapshotAdapter: "
                f"{dataset.value}"
            )

        requested_symbols = self._normalize_requested_symbols(symbols)
        requested_symbol_set = (
            set(requested_symbols) if requested_symbols is not None else None
        )
        fetch_routes = self._resolve_fetch_global_equity_routes()
        rows = self._fetch_rows_with_fallback(fetch_routes)
        records = self._normalize_global_equity_rows(
            rows=rows,
            requested_symbol_set=requested_symbol_set,
            dataset=dataset,
        )
        records = self._filter_records_by_date(
            records=records,
            start_date=start_date,
            end_date=end_date,
        )
        if requested_symbols is None:
            records = self._bounded_default_subset(records)
        return records

    def _resolve_fetch_global_equity_routes(
        self,
    ) -> list[tuple[str, Callable[..., Any]]]:
        if self._fetch_global_equity_spot is not None:
            return [("custom", self._fetch_global_equity_spot)]
        explicit_routes: list[tuple[str, Callable[..., Any]]] = []
        if self._fetch_global_equity_spot_em is not None:
            explicit_routes.append(("stock_us_spot_em", self._fetch_global_equity_spot_em))
        if self._fetch_global_equity_spot_sina is not None:
            explicit_routes.append(("stock_us_spot", self._fetch_global_equity_spot_sina))
        if explicit_routes:
            return explicit_routes

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare global equity snapshot fetch."
            ) from exc

        routes: list[tuple[str, Callable[..., Any]]] = []
        if hasattr(ak, "stock_us_spot_em"):
            routes.append(("stock_us_spot_em", ak.stock_us_spot_em))
        if hasattr(ak, "stock_us_spot"):
            routes.append(("stock_us_spot", ak.stock_us_spot))
        if routes:
            return routes
        raise RuntimeError(
            "AKShare global equity snapshot function is unavailable in this akshare version."
        )

    def _fetch_rows_with_fallback(
        self,
        routes: Sequence[tuple[str, Callable[..., Any]]],
    ) -> list[Mapping[str, Any]]:
        network_failures: list[str] = []
        first_network_exc: BaseException | None = None

        for route_name, fetch_fn in routes:
            try:
                raw_payload = fetch_fn()
            except Exception as exc:
                if not self._is_global_equity_route_unavailable(
                    route_name=route_name,
                    exc=exc,
                ):
                    raise
                if first_network_exc is None:
                    first_network_exc = exc
                network_failures.append(f"{route_name} -> {type(exc).__name__}: {exc}")
                continue

            rows = self._payload_to_rows(raw_payload)
            if rows:
                return rows

        if network_failures:
            evidence = " | ".join(network_failures[:2])
            if len(network_failures) > 2:
                evidence = f"{evidence} | ... total={len(network_failures)} failures"
            raise RuntimeError(
                "AKShare global-equity fetch routes unavailable: "
                f"{evidence}"
            ) from first_network_exc

        return []

    def _is_global_equity_route_unavailable(
        self,
        *,
        route_name: str,
        exc: BaseException,
    ) -> bool:
        if self._is_global_equity_network_unavailable(exc):
            return True
        if route_name != "stock_us_spot":
            return False
        return self._is_stock_us_spot_upstream_payload_unavailable(exc)

    def _is_stock_us_spot_upstream_payload_unavailable(
        self,
        exc: BaseException,
    ) -> bool:
        seen: set[int] = set()
        current: BaseException | None = exc
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            if (
                isinstance(current, KeyError)
                and len(current.args) == 1
                and current.args[0] == "data"
            ):
                return True
            if current.__cause__ is not None:
                current = current.__cause__
                continue
            current = current.__context__
        return False

    def _payload_to_rows(self, payload: Any) -> list[Mapping[str, Any]]:
        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "AKShare global equity snapshot payload must be DataFrame-like "
                f"or list[Mapping], got {type(payload).__name__}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "AKShare global equity snapshot payload row must be mapping. "
                    f"idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _normalize_global_equity_rows(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        requested_symbol_set: set[str] | None,
        dataset: DatasetName,
    ) -> list[dict[str, Any]]:
        ingested_at = self._now_fn().isoformat()
        fallback_trade_date = self._now_fn().date()
        schema_version = self._registry.get(dataset).schema_version

        normalized_by_key: dict[tuple[str, str], dict[str, Any]] = {}
        for idx, row in enumerate(rows):
            if requested_symbol_set is not None:
                source_symbol = self._pick_optional(
                    row,
                    "symbol",
                    "代码",
                    "code",
                    "ticker",
                    "股票代码",
                )
                if source_symbol is None:
                    continue
                try:
                    candidate_symbol, _ = self._normalize_source_symbol(source_symbol)
                except ValueError:
                    continue
                if candidate_symbol not in requested_symbol_set:
                    continue

            record = self._normalize_global_equity_row(
                row=row,
                row_idx=idx,
                ingested_at=ingested_at,
                fallback_trade_date=fallback_trade_date,
                schema_version=schema_version,
            )
            symbol = record["symbol"]

            dedupe_key = (symbol, record["trade_date"])
            if dedupe_key not in normalized_by_key:
                normalized_by_key[dedupe_key] = record
                continue

            existing = normalized_by_key[dedupe_key]
            if self._is_conflicting_duplicate(existing=existing, candidate=record):
                raise ValueError(
                    "Conflicting duplicate global equity snapshot row detected: "
                    f"symbol={symbol!r}, trade_date={record['trade_date']!r}, "
                    f"existing_close={existing['close']!r}, candidate_close={record['close']!r}, "
                    f"existing_change_pct={existing['change_pct']!r}, candidate_change_pct={record['change_pct']!r}."
                )
            normalized_by_key[dedupe_key] = self._select_preferred_duplicate_record(
                existing=existing,
                candidate=record,
            )

        return list(normalized_by_key.values())

    def _bounded_default_subset(
        self,
        records: Sequence[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        bounded = sorted(
            (dict(record) for record in records),
            key=lambda record: (
                str(record.get("symbol", "")),
                str(record.get("trade_date", "")),
            ),
        )
        return bounded[: self._max_records_without_symbols]

    def _filter_records_by_date(
        self,
        *,
        records: Sequence[Mapping[str, Any]],
        start_date: date | None,
        end_date: date | None,
    ) -> list[dict[str, Any]]:
        filtered: list[dict[str, Any]] = []
        for record in records:
            trade_date = date.fromisoformat(str(record["trade_date"]))
            if start_date is not None and trade_date < start_date:
                continue
            if end_date is not None and trade_date > end_date:
                continue
            filtered.append(dict(record))
        return filtered

    def _normalize_global_equity_row(
        self,
        *,
        row: Mapping[str, Any],
        row_idx: int,
        ingested_at: str,
        fallback_trade_date: date,
        schema_version: str,
    ) -> dict[str, Any]:
        source_symbol = self._pick(
            row,
            row_idx,
            "symbol",
            "代码",
            "code",
            "ticker",
            "股票代码",
        )
        canonical_symbol, source_exchange = self._normalize_source_symbol(source_symbol)

        close = self._to_float(
            value=self._pick(
                row,
                row_idx,
                "最新价",
                "close",
                "last",
                "price",
                "trade",
                "收盘",
            ),
            field_name="close",
        )

        change_pct = self._to_float(
            value=self._pick(
                row,
                row_idx,
                "涨跌幅",
                "chg",
                "change_pct",
                "changepercent",
                "percent",
                "pct_change",
            ),
            field_name="change_pct",
            strip_percent=True,
        )

        trade_date_value = self._pick_optional(
            row,
            "trade_date",
            "date",
            "日期",
            "交易日期",
            "行情日期",
            "latest_date",
            "最新日期",
            "更新时间",
            "最新行情时间",
            "time",
            "latest_time",
        )
        trade_date = self._normalize_trade_date(
            value=trade_date_value,
            fallback=fallback_trade_date,
        )

        currency_value = self._pick_optional(
            row,
            "currency",
            "币种",
            "货币",
        )
        currency = (
            self._normalize_nonempty_string(currency_value, field_name="currency")
            if currency_value is not None
            else self._DEFAULT_CURRENCY
        )

        exchange_value = self._pick_optional(
            row,
            "exchange",
            "交易所",
            "market_name",
            "market",
        )
        if exchange_value is not None:
            exchange = self._normalize_nonempty_string(
                exchange_value,
                field_name="exchange",
            )
        elif source_exchange is not None:
            exchange = source_exchange
        else:
            exchange = self._DEFAULT_EXCHANGE

        region_value = self._pick_optional(
            row,
            "region",
            "地区",
        )
        region = (
            self._normalize_nonempty_string(region_value, field_name="region")
            if region_value is not None
            else self._DEFAULT_REGION
        )

        record: dict[str, Any] = {
            "symbol": canonical_symbol,
            "market": self._DEFAULT_MARKET,
            "trade_date": trade_date.isoformat(),
            "close": close,
            "change_pct": change_pct,
            "currency": currency,
            "exchange": exchange,
            "region": region,
            "source": AKSHARE_SOURCE_ID,
            "ingested_at": ingested_at,
            "schema_version": schema_version,
        }

        source_ts_value = self._pick_optional(
            row,
            "source_ts",
            "更新时间",
            "最新行情时间",
            "latest_time",
            "time",
            "update_time",
        )
        if source_ts_value is not None:
            record["source_ts"] = self._normalize_source_ts(source_ts_value)
        return record

    def _normalize_requested_symbols(self, symbols: list[str] | None) -> list[str] | None:
        if symbols is None:
            return None
        if len(symbols) == 0:
            return None

        normalized: list[str] = []
        seen: set[str] = set()
        for symbol in symbols:
            canonical_symbol = self._normalize_user_symbol(symbol)
            if canonical_symbol in seen:
                continue
            seen.add(canonical_symbol)
            normalized.append(canonical_symbol)
        return normalized

    def _normalize_source_symbol(self, value: Any) -> tuple[str, str | None]:
        if not isinstance(value, str):
            raise ValueError(f"Invalid source symbol value type: {type(value).__name__}")
        stripped = value.strip().upper()
        if stripped == "":
            raise ValueError("Invalid source symbol value: empty string")

        source_exchange: str | None = None
        ticker = stripped
        parts = stripped.split(".")
        if len(parts) >= 2 and parts[0].isdigit():
            source_exchange = self._SOURCE_CODE_EXCHANGE_PREFIX_MAP.get(parts[0])
            ticker = ".".join(parts[1:])
            if ticker.endswith(".US"):
                ticker = ticker[: -len(".US")]
        elif len(parts) >= 2 and parts[-1] == "US":
            ticker = ".".join(parts[:-1])
        elif len(parts) >= 2 and parts[-1] in self._UNSUPPORTED_MARKET_SUFFIXES:
            raise ValueError(
                f"Unsupported source symbol market suffix: {parts[-1]!r}."
            )

        normalized_ticker = self._normalize_ticker(ticker)
        return f"{normalized_ticker}.US", source_exchange

    def _normalize_user_symbol(self, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError("Global equity symbol filter must be a non-empty string.")

        stripped = value.strip().upper()
        if stripped == "":
            raise ValueError("Global equity symbol filter must be a non-empty string.")

        parts = stripped.split(".")
        if len(parts) >= 2 and parts[0].isdigit():
            ticker = ".".join(parts[1:])
            if ticker.endswith(".US"):
                ticker = ticker[: -len(".US")]
            normalized_ticker = self._normalize_ticker(ticker)
            return f"{normalized_ticker}.US"

        if len(parts) >= 2 and parts[-1] == "US":
            ticker = ".".join(parts[:-1])
            normalized_ticker = self._normalize_ticker(ticker)
            return f"{normalized_ticker}.US"

        if len(parts) >= 2 and parts[-1] in self._UNSUPPORTED_MARKET_SUFFIXES:
            raise ValueError(
                f"Unsupported global equity market suffix: {parts[-1]!r}. Expected '.US'."
            )

        normalized_ticker = self._normalize_ticker(stripped)
        return f"{normalized_ticker}.US"

    def _normalize_ticker(self, value: str) -> str:
        stripped = value.strip().upper()
        if stripped == "":
            raise ValueError("Global equity ticker must be a non-empty string.")
        if not self._TICKER_PATTERN.fullmatch(stripped):
            raise ValueError(
                f"Unsupported global equity symbol format: {value!r}. "
                "Expected ticker forms like 'AAPL', 'AAPL.US', or '105.AAPL'."
            )
        return stripped

    def _pick(
        self,
        row: Mapping[str, Any],
        row_idx: int,
        *keys: str,
    ) -> Any:
        for key in keys:
            if key in row:
                return row[key]
        raise ValueError(
            "Missing required source field in global equity row "
            f"{row_idx}: one of {keys!r}"
        )

    def _pick_optional(
        self,
        row: Mapping[str, Any],
        *keys: str,
    ) -> Any | None:
        for key in keys:
            if key not in row:
                continue
            value = row[key]
            if value is None:
                return None
            if isinstance(value, str) and value.strip() == "":
                return None
            return value
        return None

    def _to_float(
        self,
        *,
        value: Any,
        field_name: str,
        strip_percent: bool = False,
    ) -> float:
        if isinstance(value, bool):
            raise ValueError(f"Invalid {field_name} value type: {value!r}")
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            normalized = value.strip().replace(",", "")
            if strip_percent:
                normalized = normalized.replace("%", "")
            if normalized == "":
                raise ValueError(f"Invalid {field_name} value: empty string")
            try:
                return float(normalized)
            except ValueError as exc:
                raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _normalize_nonempty_string(self, value: Any, *, field_name: str) -> str:
        if not isinstance(value, str):
            raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")
        stripped = value.strip()
        if stripped == "":
            raise ValueError(f"Invalid {field_name} value: empty string")
        return stripped.upper()

    def _normalize_trade_date(
        self,
        *,
        value: Any | None,
        fallback: date,
    ) -> date:
        if value is None:
            return fallback
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                return fallback
            if len(stripped) == 8 and stripped.isdigit():
                return date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
            try:
                return date.fromisoformat(stripped)
            except ValueError:
                try:
                    return datetime.fromisoformat(stripped).date()
                except ValueError as exc:
                    raise ValueError(f"Invalid trade date value: {value!r}") from exc
        raise ValueError(f"Invalid trade date value type: {type(value).__name__}")

    def _normalize_source_ts(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time()).isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError("Invalid source_ts value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                parsed_date = date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
                return datetime.combine(parsed_date, datetime.min.time()).isoformat()
            try:
                return datetime.fromisoformat(stripped).isoformat()
            except ValueError as exc:
                raise ValueError(f"Invalid source_ts value: {value!r}") from exc
        raise ValueError(f"Invalid source_ts value type: {type(value).__name__}")

    def _is_conflicting_duplicate(
        self,
        *,
        existing: Mapping[str, Any],
        candidate: Mapping[str, Any],
    ) -> bool:
        comparable_fields = (
            "close",
            "change_pct",
            "currency",
            "exchange",
            "region",
            "market",
            "source",
        )
        return any(existing[field] != candidate[field] for field in comparable_fields)

    def _select_preferred_duplicate_record(
        self,
        *,
        existing: dict[str, Any],
        candidate: dict[str, Any],
    ) -> dict[str, Any]:
        existing_source_ts = existing.get("source_ts")
        candidate_source_ts = candidate.get("source_ts")

        if existing_source_ts is None and candidate_source_ts is not None:
            return candidate
        if existing_source_ts is not None and candidate_source_ts is None:
            return existing
        if existing_source_ts is None and candidate_source_ts is None:
            return existing
        if not isinstance(existing_source_ts, str) or not isinstance(candidate_source_ts, str):
            return existing
        if candidate_source_ts > existing_source_ts:
            return candidate
        return existing

    def _is_global_equity_network_unavailable(self, exc: BaseException) -> bool:
        network_exception_names = {
            "ProxyError",
            "ConnectionError",
            "ConnectTimeout",
            "ReadTimeout",
            "Timeout",
            "MaxRetryError",
            "NewConnectionError",
            "NameResolutionError",
            "SSLError",
        }
        network_message_tokens = (
            "proxy",
            "timed out",
            "timeout",
            "name resolution",
            "temporary failure in name resolution",
            "failed to establish a new connection",
            "max retries exceeded",
            "network is unreachable",
            "connection refused",
            "no route to host",
            "connection reset",
            "dns",
            "eastmoney",
            "push2.eastmoney.com",
            "72.push2.eastmoney.com",
            "sina.com",
            "finance.sina.com.cn",
            "stock.finance.sina.com.cn",
        )

        seen: set[int] = set()
        current: BaseException | None = exc
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            name = type(current).__name__
            module = type(current).__module__
            message = str(current).lower()

            if name in network_exception_names:
                return True
            if module.startswith(("requests", "urllib3")) and any(
                token in message for token in network_message_tokens
            ):
                return True
            if isinstance(current, (socket.timeout, TimeoutError, ConnectionError)):
                return True
            if isinstance(current, OSError):
                if current.errno in {101, 110, 111, 113}:
                    return True
                if any(token in message for token in network_message_tokens):
                    return True

            if current.__cause__ is not None:
                current = current.__cause__
                continue
            current = current.__context__
        return False


class AkshareNewsEventsAdapter:
    """Narrow AKShare adapter for news events only."""

    source_name = AKSHARE_SOURCE_ID
    source_display_name = AKSHARE_SOURCE_NAME

    _DEFAULT_REGION = "GLOBAL"
    _DEFAULT_ROUTE_SOURCE_NAME = "SHMET"

    def __init__(
        self,
        *,
        fetch_news_events: Callable[..., Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
        max_records_without_symbols: int = 200,
        route_source_name: str = _DEFAULT_ROUTE_SOURCE_NAME,
    ) -> None:
        if max_records_without_symbols <= 0:
            raise ValueError("max_records_without_symbols must be positive.")
        if not isinstance(route_source_name, str) or route_source_name.strip() == "":
            raise ValueError("route_source_name must be a non-empty string.")

        self._fetch_news_events = fetch_news_events
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._max_records_without_symbols = max_records_without_symbols
        self._route_source_name = route_source_name.strip()
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if dataset != DatasetName.NEWS_EVENTS:
            raise ValueError(
                f"Unsupported dataset for AkshareNewsEventsAdapter: {dataset.value}"
            )
        self._validate_symbols_filter(symbols)

        rows = self._fetch_news_rows()
        records = self._normalize_news_rows(rows=rows, dataset=dataset)
        records = self._filter_records_by_date(
            records=records,
            start_date=start_date,
            end_date=end_date,
        )
        return self._bounded_default_subset(records)

    def _validate_symbols_filter(self, symbols: list[str] | None) -> None:
        if symbols is None:
            return
        if len(symbols) == 0:
            return
        raise ValueError(
            "AkshareNewsEventsAdapter does not support symbol filters for "
            "the selected AKShare route."
        )

    def _resolve_fetch_news_events(self) -> Callable[..., Any]:
        if self._fetch_news_events is not None:
            return self._fetch_news_events

        try:
            import akshare as ak  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "akshare dependency is required for live AKShare news-events fetch."
            ) from exc

        if hasattr(ak, "futures_news_shmet"):
            return ak.futures_news_shmet
        raise RuntimeError(
            "AKShare public news function is unavailable in this akshare version."
        )

    def _fetch_news_rows(self) -> list[Mapping[str, Any]]:
        fetch_fn = self._resolve_fetch_news_events()
        raw_payload = fetch_fn()
        return self._payload_to_rows(raw_payload)

    def _payload_to_rows(self, payload: Any) -> list[Mapping[str, Any]]:
        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "AKShare news events payload must be DataFrame-like "
                f"or list[Mapping], got {type(payload).__name__}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "AKShare news events payload row must be mapping. "
                    f"idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _normalize_news_rows(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        dataset: DatasetName,
    ) -> list[dict[str, Any]]:
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version

        normalized_by_news_id: dict[str, dict[str, Any]] = {}
        for idx, row in enumerate(rows):
            publish_time = self._normalize_publish_time(
                value=self._pick(
                    row,
                    idx,
                    "publish_time",
                    "发布时间",
                    "time",
                    "datetime",
                    "date",
                    "日期",
                ),
                field_name="publish_time",
            )

            title = self._build_title_from_row(row=row, row_idx=idx)
            summary = self._normalize_optional_text(
                self._pick_optional(
                    row,
                    "summary",
                    "摘要",
                    "内容",
                    "content",
                    "正文",
                ),
                field_name="summary",
            )

            source_name_value = self._pick_optional(
                row,
                "source_name",
                "来源",
                "媒体",
                "source",
            )
            source_name = self._normalize_required_text(
                source_name_value if source_name_value is not None else self._route_source_name,
                field_name="source_name",
            )

            related_symbol = self._normalize_optional_related_symbol(
                self._pick_optional(
                    row,
                    "related_symbol",
                    "symbol",
                    "代码",
                    "ticker",
                    "stock_code",
                )
            )
            sentiment_label = self._normalize_optional_text(
                self._pick_optional(
                    row,
                    "sentiment_label",
                    "sentiment",
                    "情感",
                    "情绪",
                ),
                field_name="sentiment_label",
            )
            url = self._normalize_optional_text(
                self._pick_optional(row, "url", "链接", "link"),
                field_name="url",
            )

            source_ts_value = self._pick_optional(
                row,
                "source_ts",
                "更新时间",
                "update_time",
            )

            source_news_id = self._pick_optional(
                row,
                "news_id",
                "id",
                "资讯ID",
                "新闻ID",
            )
            if source_news_id is not None:
                news_id = self._normalize_required_text(source_news_id, field_name="news_id")
            else:
                news_id = self._build_deterministic_news_id(
                    title=title,
                    publish_time=publish_time,
                    source_name=source_name,
                    url=url,
                    related_symbol=related_symbol,
                )

            record: dict[str, Any] = {
                "news_id": news_id,
                "region": self._DEFAULT_REGION,
                "publish_time": publish_time,
                "title": title,
                "source_name": source_name,
                "source": AKSHARE_SOURCE_ID,
                "ingested_at": ingested_at,
                "schema_version": schema_version,
            }

            if related_symbol is not None:
                record["related_symbol"] = related_symbol
            if sentiment_label is not None:
                record["sentiment_label"] = sentiment_label
            if summary is not None:
                record["summary"] = summary
            if url is not None:
                record["url"] = url
            if source_ts_value is not None:
                record["source_ts"] = self._normalize_source_ts(source_ts_value)

            existing = normalized_by_news_id.get(news_id)
            if existing is None:
                normalized_by_news_id[news_id] = record
                continue
            if self._is_conflicting_duplicate(existing=existing, candidate=record):
                raise ValueError(
                    "Conflicting duplicate news event row detected: "
                    f"news_id={news_id!r}."
                )
            normalized_by_news_id[news_id] = self._select_preferred_duplicate_record(
                existing=existing,
                candidate=record,
            )

        return list(normalized_by_news_id.values())

    def _bounded_default_subset(
        self,
        records: Sequence[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        bounded = sorted(
            (dict(record) for record in records),
            key=lambda record: (
                str(record.get("publish_time", "")),
                str(record.get("news_id", "")),
            ),
            reverse=True,
        )
        return bounded[: self._max_records_without_symbols]

    def _filter_records_by_date(
        self,
        *,
        records: Sequence[Mapping[str, Any]],
        start_date: date | None,
        end_date: date | None,
    ) -> list[dict[str, Any]]:
        filtered: list[dict[str, Any]] = []
        for record in records:
            publish_date = datetime.fromisoformat(str(record["publish_time"])).date()
            if start_date is not None and publish_date < start_date:
                continue
            if end_date is not None and publish_date > end_date:
                continue
            filtered.append(dict(record))
        return filtered

    def _build_title_from_row(
        self,
        *,
        row: Mapping[str, Any],
        row_idx: int,
    ) -> str:
        title_value = self._pick_optional(
            row,
            "title",
            "标题",
            "新闻标题",
            "资讯标题",
        )
        if title_value is not None:
            return self._normalize_required_text(title_value, field_name="title")

        fallback_text = self._pick(
            row,
            row_idx,
            "summary",
            "摘要",
            "内容",
            "content",
            "正文",
        )
        fallback = self._normalize_required_text(fallback_text, field_name="title")
        compact = " ".join(fallback.split())
        if len(compact) <= 80:
            return compact
        return compact[:80].rstrip()

    def _build_deterministic_news_id(
        self,
        *,
        title: str,
        publish_time: str,
        source_name: str,
        url: str | None,
        related_symbol: str | None,
    ) -> str:
        stable_fields = (
            title,
            publish_time,
            source_name,
            url or "",
            related_symbol or "",
        )
        digest = hashlib.sha1("|".join(stable_fields).encode("utf-8")).hexdigest()
        return f"AKNEWS-{digest[:24]}"

    def _pick(
        self,
        row: Mapping[str, Any],
        row_idx: int,
        *keys: str,
    ) -> Any:
        for key in keys:
            if key in row:
                return row[key]
        raise ValueError(
            "Missing required source field in news event row "
            f"{row_idx}: one of {keys!r}"
        )

    def _pick_optional(
        self,
        row: Mapping[str, Any],
        *keys: str,
    ) -> Any | None:
        for key in keys:
            if key not in row:
                continue
            value = row[key]
            if value is None:
                return None
            if isinstance(value, str) and value.strip() == "":
                return None
            return value
        return None

    def _normalize_required_text(self, value: Any, *, field_name: str) -> str:
        if not isinstance(value, str):
            raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")
        stripped = value.strip()
        if stripped == "":
            raise ValueError(f"Invalid {field_name} value: empty string")
        return stripped

    def _normalize_optional_text(self, value: Any | None, *, field_name: str) -> str | None:
        if value is None:
            return None
        return self._normalize_required_text(value, field_name=field_name)

    def _normalize_optional_related_symbol(self, value: Any | None) -> str | None:
        if value is None:
            return None
        normalized = self._normalize_required_text(value, field_name="related_symbol")
        return normalized.upper()

    def _normalize_publish_time(self, *, value: Any, field_name: str) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time()).isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError(f"Invalid {field_name} value: empty string")
            if len(stripped) == 8 and stripped.isdigit():
                parsed_date = date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
                return datetime.combine(parsed_date, datetime.min.time()).isoformat()
            try:
                return datetime.fromisoformat(stripped).isoformat()
            except ValueError:
                try:
                    parsed_date = date.fromisoformat(stripped)
                    return datetime.combine(parsed_date, datetime.min.time()).isoformat()
                except ValueError as exc:
                    raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _normalize_source_ts(self, value: Any) -> str:
        return self._normalize_publish_time(value=value, field_name="source_ts")

    def _is_conflicting_duplicate(
        self,
        *,
        existing: Mapping[str, Any],
        candidate: Mapping[str, Any],
    ) -> bool:
        comparable_fields = (
            "region",
            "publish_time",
            "title",
            "source_name",
            "related_symbol",
            "sentiment_label",
            "summary",
            "url",
            "source",
        )
        return any(existing.get(field) != candidate.get(field) for field in comparable_fields)

    def _select_preferred_duplicate_record(
        self,
        *,
        existing: dict[str, Any],
        candidate: dict[str, Any],
    ) -> dict[str, Any]:
        existing_source_ts = existing.get("source_ts")
        candidate_source_ts = candidate.get("source_ts")

        if existing_source_ts is None and candidate_source_ts is not None:
            return candidate
        if existing_source_ts is not None and candidate_source_ts is None:
            return existing
        if existing_source_ts is None and candidate_source_ts is None:
            return existing
        if not isinstance(existing_source_ts, str) or not isinstance(candidate_source_ts, str):
            return existing
        if candidate_source_ts > existing_source_ts:
            return candidate
        return existing
