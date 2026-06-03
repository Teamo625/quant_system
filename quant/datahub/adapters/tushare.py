"""Tushare-backed DataHub adapters."""

from __future__ import annotations

import inspect
import os
import socket
from datetime import date, datetime, timezone
from typing import Any, Callable, Mapping, Sequence

from ..datasets import DatasetName, DatasetRegistry, ValidationIssue


TUSHARE_SOURCE_ID = "tushare_pro_cn_core"
TUSHARE_SOURCE_NAME = "Tushare Pro CN Core"


def _exception_chain(exc: BaseException) -> Sequence[BaseException]:
    seen: set[int] = set()
    chain: list[BaseException] = []
    current: BaseException | None = exc
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        chain.append(current)
        if current.__cause__ is not None:
            current = current.__cause__
            continue
        current = current.__context__
    return tuple(chain)


def is_tushare_live_environment_unavailable(exc: BaseException) -> bool:
    """Return True only for environment or upstream availability failures."""
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
        "api.waditu.com",
        "tushare.pro",
        "service unavailable",
        "temporarily unavailable",
        "bad gateway",
        "gateway timeout",
    )

    for cause in _exception_chain(exc):
        name = type(cause).__name__
        module = type(cause).__module__
        message = str(cause).lower()

        if name in network_exception_names:
            return True
        if module.startswith(("requests", "urllib3")) and any(
            token in message for token in network_message_tokens
        ):
            return True
        if any(token in message for token in network_message_tokens):
            return True
        if isinstance(cause, (socket.timeout, TimeoutError, ConnectionError)):
            return True
        if isinstance(cause, OSError):
            if cause.errno in {101, 104, 110, 111, 113}:
                return True
            if any(token in message for token in network_message_tokens):
                return True

    return False


class TushareIndexWeightHistoryAdapter:
    """Narrow Tushare Pro adapter for one bounded index weight-history slice."""

    source_name = TUSHARE_SOURCE_ID
    source_display_name = TUSHARE_SOURCE_NAME

    _ROUTE_NAME = "index_weight"
    _TOKEN_ENV_VAR = "TUSHARE_TOKEN"
    _SUPPORTED_INDEX_ALIASES = {
        "000300.CN_INDEX": "000300.CN_INDEX",
        "000300.SH": "000300.CN_INDEX",
        "399300.SZ": "000300.CN_INDEX",
        "000300": "000300.CN_INDEX",
    }
    _CANONICAL_TO_ROUTE_CODE = {
        "000300.CN_INDEX": "399300.SZ",
    }

    def __init__(
        self,
        *,
        index_weight_fetcher: Callable[..., Any] | None = None,
        tushare_pro_client_factory: Callable[[str], Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
        token_env_var: str = _TOKEN_ENV_VAR,
    ) -> None:
        self._index_weight_fetcher = index_weight_fetcher
        self._tushare_pro_client_factory = tushare_pro_client_factory
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._token_env_var = token_env_var
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if dataset != DatasetName.INDEX_WEIGHT_HISTORY:
            raise ValueError(
                "Unsupported dataset for TushareIndexWeightHistoryAdapter: "
                f"{dataset.value}"
            )

        index_code, route_index_code = self._require_single_index_code(symbols)
        route_kwargs = self._resolve_bounded_request_kwargs(
            start_date=start_date,
            end_date=end_date,
        )
        rows = self._fetch_index_weight_rows(
            route_index_code=route_index_code,
            route_kwargs=route_kwargs,
        )
        return self._normalize_weight_history_rows(
            rows=rows,
            requested_index_code=index_code,
            dataset=dataset,
        )

    def _require_single_index_code(
        self,
        symbols: list[str] | None,
    ) -> tuple[str, str]:
        if symbols is None or len(symbols) == 0:
            raise ValueError(
                "TushareIndexWeightHistoryAdapter requires exactly one China index identifier, "
                "got none."
            )
        if len(symbols) != 1:
            raise ValueError(
                "TushareIndexWeightHistoryAdapter currently supports exactly one China index "
                "identifier."
            )

        raw_symbol = symbols[0]
        if not isinstance(raw_symbol, str) or raw_symbol.strip() == "":
            raise ValueError("Index identifier must be a non-empty string.")

        normalized = raw_symbol.strip().upper()
        if normalized in self._SUPPORTED_INDEX_ALIASES:
            canonical = self._SUPPORTED_INDEX_ALIASES[normalized]
            return canonical, self._CANONICAL_TO_ROUTE_CODE[canonical]

        if normalized.endswith((".HK", ".HK_INDEX", ".HK_STOCK")):
            raise ValueError(
                f"Unsupported Hong Kong index identifier: {raw_symbol!r}. "
                "Expected a supported mainland China index identifier."
            )

        if normalized.endswith((".ETF", ".ETF_CN", ".FUND")) or normalized.startswith(
            ("15", "16", "50", "51", "56", "58", "159")
        ):
            raise ValueError(
                f"Unsupported ETF/fund identifier for index weight history: {raw_symbol!r}."
            )

        if "." in normalized:
            code, market = normalized.split(".", 1)
            if market not in {"SH", "SZ", "CN_INDEX"}:
                raise ValueError(
                    f"Unsupported index identifier market suffix: {market!r}. "
                    "Expected .CN_INDEX, .SH, or .SZ for the current bounded slice."
                )
            if code.isdigit() and len(code) == 6:
                raise ValueError(
                    f"Unsupported China index identifier for current bounded slice: "
                    f"{raw_symbol!r}. Only CSI 300 aliases are supported right now."
                )

        raise ValueError(
            f"Unsupported index identifier format: {raw_symbol!r}. Expected one of "
            "'000300.CN_INDEX', '000300.SH', '399300.SZ', or '000300'."
        )

    def _resolve_bounded_request_kwargs(
        self,
        *,
        start_date: date | None,
        end_date: date | None,
    ) -> dict[str, str]:
        if start_date is None and end_date is None:
            raise ValueError(
                "TushareIndexWeightHistoryAdapter requires a bounded request. Provide start_date "
                "for a single trade-date request, or provide both start_date and end_date."
            )
        if start_date is None and end_date is not None:
            raise ValueError(
                "end_date without start_date is unsupported. Provide start_date for a single "
                "trade-date request, or both start_date and end_date for a range."
            )
        if start_date is not None and end_date is None:
            return {"trade_date": start_date.strftime("%Y%m%d")}
        if start_date == end_date:
            return {"trade_date": start_date.strftime("%Y%m%d")}
        return {
            "start_date": start_date.strftime("%Y%m%d"),
            "end_date": end_date.strftime("%Y%m%d"),
        }

    def _fetch_index_weight_rows(
        self,
        *,
        route_index_code: str,
        route_kwargs: Mapping[str, str],
    ) -> list[Mapping[str, Any]]:
        fetcher = self._resolve_index_weight_fetcher()
        payload = self._call_index_weight_fetcher(
            fetcher=fetcher,
            route_index_code=route_index_code,
            route_kwargs=route_kwargs,
        )
        return self._payload_to_rows(payload)

    def _resolve_index_weight_fetcher(self) -> Callable[..., Any]:
        if self._index_weight_fetcher is not None:
            return self._index_weight_fetcher

        token = os.getenv(self._token_env_var)
        if token is None or token.strip() == "":
            raise RuntimeError(
                f"{self._token_env_var} is required for live Tushare index weight history "
                "fetches."
            )

        if self._tushare_pro_client_factory is not None:
            pro_client = self._tushare_pro_client_factory(token)
        else:
            try:
                import tushare as ts  # type: ignore[import-not-found]
            except Exception as exc:  # pragma: no cover - exercised by live/dependency env
                raise RuntimeError(
                    "tushare dependency is required for live Tushare index weight history fetch."
                ) from exc
            pro_client = ts.pro_api(token)

        fetcher = getattr(pro_client, self._ROUTE_NAME, None)
        if fetcher is None:
            raise RuntimeError(
                f"Tushare Pro client does not expose the {self._ROUTE_NAME!r} route."
            )
        return fetcher

    def _call_index_weight_fetcher(
        self,
        *,
        fetcher: Callable[..., Any],
        route_index_code: str,
        route_kwargs: Mapping[str, str],
    ) -> Any:
        accepted_args, supports_var_kwargs = self._inspect_callable(fetcher)
        call_kwargs = {"index_code": route_index_code, **dict(route_kwargs)}
        unsupported_args = sorted(
            name
            for name in call_kwargs
            if not supports_var_kwargs and name not in accepted_args
        )
        if unsupported_args:
            raise RuntimeError(
                "Tushare index_weight function does not accept required argument(s): "
                f"{unsupported_args!r}."
            )

        try:
            return fetcher(**call_kwargs)
        except TypeError as exc:
            if self._is_route_signature_incompatibility(exc):
                raise RuntimeError(
                    "Tushare index_weight route signature incompatibility: "
                    f"{type(exc).__name__}: {exc}"
                ) from exc
            raise

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

    def _payload_to_rows(self, payload: Any) -> list[Mapping[str, Any]]:
        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "Tushare index weight-history payload must be DataFrame-like or list[Mapping], "
                f"got {type(payload).__name__}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "Tushare index weight-history payload row must be mapping. "
                    f"idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _normalize_weight_history_rows(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        requested_index_code: str,
        dataset: DatasetName,
    ) -> list[dict[str, Any]]:
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version
        normalized_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}

        for row_idx, row in enumerate(rows):
            row_index_code = self._normalize_payload_index_code(
                self._pick(
                    row,
                    row_idx,
                    "index_code",
                    "ts_code",
                )
            )
            if row_index_code != requested_index_code:
                raise ValueError(
                    "Tushare index weight-history row index_code does not match request: "
                    f"row={row_index_code!r}, request={requested_index_code!r}."
                )

            weight, weight_unit = self._resolve_weight(row=row, row_idx=row_idx)
            record: dict[str, Any] = {
                "index_code": requested_index_code,
                "symbol": self._normalize_symbol(
                    self._pick(row, row_idx, "con_code", "symbol", "constituent_code")
                ),
                "market": "CN_A",
                "effective_date": self._normalize_date(
                    self._pick(row, row_idx, "trade_date", "effective_date"),
                    field_name="effective_date",
                ).isoformat(),
                "weight": weight,
                "weight_unit": weight_unit,
                "source_route": self._ROUTE_NAME,
                "source": TUSHARE_SOURCE_ID,
                "ingested_at": ingested_at,
                "schema_version": schema_version,
            }

            rebalance_date = self._pick_optional(
                row,
                "rebalance_date",
                "adjust_date",
                "ann_date",
            )
            if rebalance_date is not None:
                record["rebalance_date"] = self._normalize_date(
                    rebalance_date,
                    field_name="rebalance_date",
                ).isoformat()

            out_date = self._pick_optional(row, "out_date", "remove_date")
            if out_date is not None:
                record["out_date"] = self._normalize_date(
                    out_date,
                    field_name="out_date",
                ).isoformat()

            source_ts = self._pick_optional(row, "source_ts", "update_time", "更新时间")
            if source_ts is not None:
                record["source_ts"] = self._normalize_source_ts(source_ts)

            self._validate_record(dataset=dataset, record=record, row_idx=row_idx)

            dedupe_key = (
                record["index_code"],
                record["effective_date"],
                record["symbol"],
            )
            existing = normalized_by_key.get(dedupe_key)
            if existing is None:
                normalized_by_key[dedupe_key] = record
                continue

            if self._is_conflicting_duplicate(existing=existing, candidate=record):
                raise ValueError(
                    "Conflicting duplicate index weight-history row detected: "
                    f"index_code={record['index_code']!r}, "
                    f"effective_date={record['effective_date']!r}, "
                    f"symbol={record['symbol']!r}."
                )
            normalized_by_key[dedupe_key] = self._select_preferred_duplicate_record(
                existing=existing,
                candidate=record,
            )

        return sorted(
            normalized_by_key.values(),
            key=lambda item: (
                item["index_code"],
                item["effective_date"],
                item["symbol"],
            ),
        )

    def _normalize_payload_index_code(self, value: Any) -> str:
        normalized = self._normalize_identifier_value(value, field_name="index_code")
        if normalized in self._SUPPORTED_INDEX_ALIASES:
            return self._SUPPORTED_INDEX_ALIASES[normalized]
        raise ValueError(
            f"Unsupported source index_code value: {value!r}. "
            "Expected a supported CSI 300 alias."
        )

    def _resolve_weight(
        self,
        *,
        row: Mapping[str, Any],
        row_idx: int,
    ) -> tuple[float, str]:
        key, value = self._pick_with_key(
            row,
            row_idx,
            "weight",
            "weight_pct",
            "weight_percent",
            "weight_ratio",
            "weight_decimal",
        )
        explicit_unit = self._pick_optional(row, "weight_unit", "unit", "权重单位")
        unit = self._normalize_weight_unit(
            key=key,
            explicit_unit=explicit_unit,
            raw_value=value,
        )
        raw_weight = self._to_float(value=value, field_name="weight")
        if unit == "fraction":
            if not (0.0 <= raw_weight <= 1.0):
                raise ValueError(
                    "Invalid fractional weight value: "
                    f"{raw_weight!r}. Expected within [0, 1]."
                )
            return raw_weight * 100.0, "percent"
        if not (0.0 <= raw_weight <= 100.0):
            raise ValueError(
                f"Invalid weight value: {raw_weight!r}. Expected within [0, 100]."
            )
        return raw_weight, "percent"

    def _normalize_weight_unit(
        self,
        *,
        key: str,
        explicit_unit: Any | None,
        raw_value: Any,
    ) -> str:
        if key in {"weight_ratio", "weight_decimal"}:
            return "fraction"

        if isinstance(raw_value, str) and raw_value.strip().endswith("%"):
            return "percent"

        if explicit_unit is None:
            return "percent"

        if not isinstance(explicit_unit, str):
            raise ValueError(
                "Invalid weight_unit value type: "
                f"{type(explicit_unit).__name__}"
            )

        normalized = explicit_unit.strip().lower()
        if normalized in {"percent", "percentage", "pct", "%"}:
            return "percent"
        if normalized in {"fraction", "ratio", "decimal"}:
            return "fraction"
        raise ValueError(f"Unsupported weight_unit value: {explicit_unit!r}.")

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
            "Missing required source field in Tushare index weight-history row "
            f"{row_idx}: one of {keys!r}"
        )

    def _pick_with_key(
        self,
        row: Mapping[str, Any],
        row_idx: int,
        *keys: str,
    ) -> tuple[str, Any]:
        for key in keys:
            if key in row:
                return key, row[key]
        raise ValueError(
            "Missing required source field in Tushare index weight-history row "
            f"{row_idx}: one of {keys!r}"
        )

    def _pick_optional(self, row: Mapping[str, Any], *keys: str) -> Any | None:
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
        raw = self._normalize_identifier_value(value, field_name="symbol")
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

    def _normalize_identifier_value(self, value: Any, *, field_name: str) -> str:
        if isinstance(value, bool):
            raise ValueError(f"Invalid {field_name} value type: {value!r}")
        if isinstance(value, int):
            if value < 0 or value > 999999:
                raise ValueError(f"Invalid {field_name} value: {value!r}")
            return f"{value:06d}"
        if isinstance(value, float):
            if not value.is_integer():
                raise ValueError(f"Invalid {field_name} value: {value!r}")
            integer_value = int(value)
            if integer_value < 0 or integer_value > 999999:
                raise ValueError(f"Invalid {field_name} value: {value!r}")
            return f"{integer_value:06d}"
        if not isinstance(value, str):
            raise ValueError(
                f"Invalid {field_name} value type: {type(value).__name__}"
            )
        normalized = value.strip().upper()
        if normalized == "":
            raise ValueError(f"Invalid {field_name} value: empty string")
        return normalized

    def _infer_a_share_market(self, code: str) -> str:
        if code.startswith(("60", "68", "90")):
            return "SH"
        if code.startswith(("00", "20", "30")):
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

    def _normalize_date(self, value: Any, *, field_name: str) -> date:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, bool):
            raise ValueError(f"Invalid {field_name} value type: {value!r}")
        if isinstance(value, int):
            value = f"{value:08d}"
        if isinstance(value, float):
            if not value.is_integer():
                raise ValueError(f"Invalid {field_name} value: {value!r}")
            value = f"{int(value):08d}"
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

    def _normalize_source_ts(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time()).isoformat()
        if isinstance(value, bool):
            raise ValueError(f"Invalid source_ts value type: {value!r}")
        if isinstance(value, int):
            value = f"{value:08d}"
        if isinstance(value, float):
            if not value.is_integer():
                raise ValueError(f"Invalid source_ts value: {value!r}")
            value = f"{int(value):08d}"
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

    def _validate_record(
        self,
        *,
        dataset: DatasetName,
        record: Mapping[str, Any],
        row_idx: int,
    ) -> None:
        issues = self._registry.validate_record(dataset, record)
        if not issues:
            return
        rendered = ", ".join(self._format_issue(issue) for issue in issues)
        raise ValueError(
            "Invalid normalized Tushare index weight-history record at row "
            f"{row_idx}: {rendered}"
        )

    def _format_issue(self, issue: ValidationIssue) -> str:
        return f"{issue.field}:{issue.code}"

    def _is_conflicting_duplicate(
        self,
        *,
        existing: Mapping[str, Any],
        candidate: Mapping[str, Any],
    ) -> bool:
        for key in (
            "index_code",
            "symbol",
            "market",
            "effective_date",
            "weight",
            "weight_unit",
            "rebalance_date",
            "out_date",
            "source_route",
            "source",
            "schema_version",
        ):
            if existing.get(key) != candidate.get(key):
                return True
        return False

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

    def _is_route_signature_incompatibility(self, exc: BaseException) -> bool:
        message = str(exc).lower()
        return any(
            token in message
            for token in (
                "unexpected keyword argument",
                "required positional argument",
                "positional arguments but",
                "got an unexpected keyword argument",
            )
        )

    def _is_tushare_index_weight_route_unavailable(self, exc: BaseException) -> bool:
        if is_tushare_live_environment_unavailable(exc):
            return True

        availability_tokens = (
            "temporarily unavailable",
            "service unavailable",
            "502",
            "503",
            "504",
        )
        for cause in _exception_chain(exc):
            message = str(cause).lower()
            if any(token in message for token in availability_tokens):
                return True
        return False

