"""BaoStock-backed DataHub adapters."""

from __future__ import annotations

from datetime import date, datetime, timezone
import math
import re
from typing import Any, Callable, Mapping, Sequence

from ..datasets import DatasetName, DatasetRegistry


BAOSTOCK_SOURCE_ID = "baostock_public_cn"
BAOSTOCK_SOURCE_NAME = "BaoStock Public CN"


class BaoStockAShareMinuteBarsAdapter:
    """BaoStock adapter for bounded A-share historical minute-bar windows."""

    source_name = BAOSTOCK_SOURCE_ID
    source_display_name = BAOSTOCK_SOURCE_NAME

    _SUPPORTED_PERIODS = {"5", "15", "30", "60"}
    _FIELDS = "date,time,code,open,high,low,close,volume,amount,adjustflag"
    _ADJUST_FLAG_RAW = "3"

    def __init__(
        self,
        *,
        login_fn: Callable[[], Any] | None = None,
        query_history_fn: Callable[..., Any] | None = None,
        logout_fn: Callable[[], Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
        minute_period: str = "5",
    ) -> None:
        if minute_period not in self._SUPPORTED_PERIODS:
            raise ValueError(
                "Unsupported minute_period for BaoStock A-share minute-bars adapter: "
                f"{minute_period!r}. Supported: {sorted(self._SUPPORTED_PERIODS)!r}"
            )
        self._login_fn = login_fn
        self._query_history_fn = query_history_fn
        self._logout_fn = logout_fn
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._minute_period = minute_period
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if dataset != DatasetName.MINUTE_BARS:
            raise ValueError(
                "Unsupported dataset for BaoStockAShareMinuteBarsAdapter: "
                f"{dataset.value}"
            )

        requested_symbols = self._require_symbols(symbols)
        bounded_start, bounded_end = self._resolve_bounded_date_window(
            start_date=start_date,
            end_date=end_date,
        )
        login_fn, query_fn, logout_fn = self._resolve_baostock_functions()

        login_result = login_fn()
        self._ensure_success(login_result, context="BaoStock login")
        try:
            normalized_records: list[dict[str, Any]] = []
            for symbol, code, market in requested_symbols:
                rows = self._query_rows(
                    query_fn=query_fn,
                    code=self._to_baostock_code(code=code, market=market),
                    start_date=bounded_start,
                    end_date=bounded_end,
                )
                normalized_records.extend(
                    self._normalize_rows(
                        rows=rows,
                        symbol=symbol,
                        start_date=bounded_start,
                        end_date=bounded_end,
                        dataset=dataset,
                    )
                )
            return self._dedupe_and_sort_records(normalized_records)
        finally:
            logout_fn()

    def _resolve_baostock_functions(
        self,
    ) -> tuple[Callable[[], Any], Callable[..., Any], Callable[[], Any]]:
        if (
            self._login_fn is not None
            and self._query_history_fn is not None
            and self._logout_fn is not None
        ):
            return self._login_fn, self._query_history_fn, self._logout_fn

        try:
            import baostock as bs  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - exercised by live/dependency env
            raise RuntimeError(
                "baostock dependency is required for live BaoStock adapter fetch."
            ) from exc

        return (
            self._login_fn or bs.login,
            self._query_history_fn or bs.query_history_k_data_plus,
            self._logout_fn or bs.logout,
        )

    def _query_rows(
        self,
        *,
        query_fn: Callable[..., Any],
        code: str,
        start_date: date,
        end_date: date,
    ) -> list[Mapping[str, Any]]:
        result = query_fn(
            code,
            self._FIELDS,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            frequency=self._minute_period,
            adjustflag=self._ADJUST_FLAG_RAW,
        )
        self._ensure_success(result, context="BaoStock minute-bars query")
        return self._query_result_to_rows(result)

    def _query_result_to_rows(self, result: Any) -> list[Mapping[str, Any]]:
        fields = getattr(result, "fields", None)
        if not isinstance(fields, Sequence) or isinstance(fields, (str, bytes)):
            raise ValueError("BaoStock minute-bars result is missing structured fields.")

        rows: list[Mapping[str, Any]] = []
        while result.next():
            row_data = result.get_row_data()
            if not isinstance(row_data, Sequence) or isinstance(row_data, (str, bytes)):
                raise ValueError(
                    "BaoStock minute-bars row data must be a sequence, "
                    f"got {type(row_data).__name__}."
                )
            if len(row_data) != len(fields):
                raise ValueError(
                    "BaoStock minute-bars row field count mismatch: "
                    f"fields={len(fields)}, values={len(row_data)}."
                )
            rows.append({str(field): value for field, value in zip(fields, row_data)})

        self._ensure_success(result, context="BaoStock minute-bars iteration")
        return rows

    def _ensure_success(self, result: Any, *, context: str) -> None:
        error_code = getattr(result, "error_code", "0")
        if str(error_code) != "0":
            error_msg = getattr(result, "error_msg", "")
            raise RuntimeError(f"{context} failed: {error_code}: {error_msg}")

    def _normalize_rows(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        symbol: str,
        start_date: date,
        end_date: date,
        dataset: DatasetName,
    ) -> list[dict[str, Any]]:
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version
        normalized_records: list[dict[str, Any]] = []

        for row_idx, row in enumerate(rows):
            source_code = self._pick(row, row_idx, "code")
            resolved_symbol = self._normalize_baostock_source_symbol(source_code)
            if resolved_symbol != symbol:
                raise ValueError(
                    "Source symbol mismatch for BaoStock A-share minute-bars adapter: "
                    f"requested={symbol!r}, row_symbol={resolved_symbol!r}."
                )

            bar_time = self._normalize_bar_time(
                trade_date=self._pick(row, row_idx, "date"),
                trade_time=self._pick(row, row_idx, "time"),
            )
            bar_date = bar_time.date()
            if bar_date < start_date or bar_date > end_date:
                continue

            normalized_records.append(
                {
                    "symbol": symbol,
                    "market": "A_SHARE",
                    "trade_date": bar_date.isoformat(),
                    "bar_time": bar_time.isoformat(sep="T"),
                    "open": self._to_nonnegative_float(
                        self._pick(row, row_idx, "open"),
                        field_name="open",
                    ),
                    "high": self._to_nonnegative_float(
                        self._pick(row, row_idx, "high"),
                        field_name="high",
                    ),
                    "low": self._to_nonnegative_float(
                        self._pick(row, row_idx, "low"),
                        field_name="low",
                    ),
                    "close": self._to_nonnegative_float(
                        self._pick(row, row_idx, "close"),
                        field_name="close",
                    ),
                    "volume": self._to_nonnegative_float(
                        self._pick(row, row_idx, "volume"),
                        field_name="volume",
                    ),
                    "amount": self._to_nonnegative_float(
                        self._pick(row, row_idx, "amount"),
                        field_name="amount",
                    ),
                    "source": BAOSTOCK_SOURCE_ID,
                    "ingested_at": ingested_at,
                    "schema_version": schema_version,
                }
            )

        return normalized_records

    def _dedupe_and_sort_records(
        self,
        records: Sequence[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        deduped: dict[tuple[str, str, str, str], dict[str, Any]] = {}
        for record in records:
            normalized = dict(record)
            identity = (
                str(normalized["symbol"]),
                str(normalized["bar_time"]),
                self._minute_period,
                str(normalized["source"]),
            )
            existing = deduped.get(identity)
            if existing is None:
                deduped[identity] = normalized
                continue
            deduped[identity] = self._merge_duplicate_record(
                existing=existing,
                candidate=normalized,
            )
        return sorted(
            deduped.values(),
            key=lambda item: (
                str(item["symbol"]),
                str(item["bar_time"]),
                str(item["source"]),
            ),
        )

    def _merge_duplicate_record(
        self,
        *,
        existing: dict[str, Any],
        candidate: dict[str, Any],
    ) -> dict[str, Any]:
        comparable_fields = (
            "symbol",
            "market",
            "trade_date",
            "bar_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "amount",
            "source",
        )
        for field in comparable_fields:
            left = existing.get(field)
            right = candidate.get(field)
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                if float(left) == float(right):
                    continue
            elif left == right:
                continue
            raise ValueError(
                "Conflicting duplicate BaoStock A-share minute-bars row detected: "
                f"field={field!r}, existing={left!r}, candidate={right!r}."
            )
        return dict(existing)

    def _resolve_bounded_date_window(
        self,
        *,
        start_date: date | None,
        end_date: date | None,
    ) -> tuple[date, date]:
        if start_date is None and end_date is None:
            raise ValueError(
                "BaoStock A-share minute-bars adapter requires bounded date window "
                "via start_date and end_date."
            )
        if start_date is None or end_date is None:
            raise ValueError(
                "BaoStock A-share minute-bars adapter requires both start_date and end_date "
                "for a bounded date-window request."
            )
        if start_date > end_date:
            raise ValueError(
                "Invalid date range for BaoStock A-share minute-bars adapter: "
                f"start_date={start_date.isoformat()} > end_date={end_date.isoformat()}"
            )
        return start_date, end_date

    def _require_symbols(self, symbols: list[str] | None) -> tuple[tuple[str, str, str], ...]:
        if symbols is None or len(symbols) == 0:
            raise ValueError(
                "BaoStockAShareMinuteBarsAdapter requires at least one symbol, got none."
            )
        normalized: list[tuple[str, str, str]] = []
        seen: set[str] = set()
        for idx, raw_value in enumerate(symbols):
            if not isinstance(raw_value, str):
                raise ValueError(
                    "Invalid symbol value type for BaoStock A-share minute-bars adapter: "
                    f"index={idx}, type={type(raw_value).__name__}"
                )
            value = raw_value.strip().upper()
            if value == "":
                raise ValueError(
                    "Invalid symbol value for BaoStock A-share minute-bars adapter: empty string."
                )
            canonical, code, market = self._normalize_a_share_symbol(value)
            if canonical in seen:
                continue
            seen.add(canonical)
            normalized.append((canonical, code, market))
        return tuple(normalized)

    def _normalize_a_share_symbol(self, value: str) -> tuple[str, str, str]:
        prefixed_match = re.match(r"^(SH|SZ|BJ)(\d{6})$", value)
        if prefixed_match is not None:
            market = prefixed_match.group(1)
            code = prefixed_match.group(2)
            inferred = self._infer_market_from_code(code)
            if inferred != market:
                raise ValueError(
                    "Invalid symbol filter market-code combination: "
                    f"{value!r}."
                )
            return f"{code}.{market}", code, market

        if "." in value:
            code, market = value.split(".", 1)
            if market not in {"SH", "SZ", "BJ"}:
                raise ValueError(
                    "Unsupported symbol market suffix for BaoStock A-share minute-bars adapter: "
                    f"{market!r}. Expected SH/SZ/BJ."
                )
            if not code.isdigit() or len(code) != 6:
                raise ValueError(
                    f"Invalid symbol filter format: {value!r}. Expected 6-digit code."
                )
            inferred = self._infer_market_from_code(code)
            if inferred != market:
                raise ValueError(
                    "Invalid symbol filter market-code combination: "
                    f"{value!r}."
                )
            return f"{code}.{market}", code, market

        if value.isdigit() and len(value) == 6:
            market = self._infer_market_from_code(value)
            return f"{value}.{market}", value, market

        raise ValueError(
            "Unsupported symbol format for BaoStock A-share minute-bars adapter: "
            f"{value!r}. Expected canonical like '600000.SH' or raw 6-digit stock code."
        )

    def _infer_market_from_code(self, code: str) -> str:
        if code.startswith("6"):
            return "SH"
        if code.startswith(("0", "3")):
            if code.startswith("399"):
                raise ValueError(
                    "Index symbol is unsupported for BaoStock A-share minute-bars adapter: "
                    f"{code!r}."
                )
            return "SZ"
        if code.startswith(("4", "8", "9")):
            return "BJ"
        if code.startswith(("1", "2", "5")):
            raise ValueError(
                "ETF or fund symbol is unsupported for BaoStock A-share minute-bars adapter: "
                f"{code!r}."
            )
        raise ValueError(
            "Invalid A-share stock code prefix for BaoStock minute-bars adapter: "
            f"{code!r}."
        )

    def _to_baostock_code(self, *, code: str, market: str) -> str:
        return f"{market.lower()}.{code}"

    def _normalize_baostock_source_symbol(self, value: Any) -> str:
        if not isinstance(value, str) or value.strip() == "":
            raise ValueError(f"Invalid BaoStock code value: {value!r}")
        normalized = value.strip().lower()
        if not re.match(r"^(sh|sz|bj)\.\d{6}$", normalized):
            raise ValueError(f"Invalid BaoStock code value: {value!r}")
        market, code = normalized.split(".", 1)
        canonical_market = market.upper()
        inferred = self._infer_market_from_code(code)
        if inferred != canonical_market:
            raise ValueError(
                "Invalid BaoStock source market-code combination: "
                f"{value!r}."
            )
        return f"{code}.{canonical_market}"

    def _normalize_bar_time(self, *, trade_date: Any, trade_time: Any) -> datetime:
        normalized_date = self._normalize_trade_date(trade_date)
        normalized_time = self._normalize_trade_time(trade_time)
        return datetime.combine(normalized_date, normalized_time.time())

    def _normalize_trade_date(self, value: Any) -> date:
        if not isinstance(value, str) or value.strip() == "":
            raise ValueError(f"Invalid BaoStock date value: {value!r}")
        try:
            return date.fromisoformat(value.strip())
        except ValueError as exc:
            raise ValueError(f"Invalid BaoStock date value: {value!r}") from exc

    def _normalize_trade_time(self, value: Any) -> datetime:
        if not isinstance(value, str) or value.strip() == "":
            raise ValueError(f"Invalid BaoStock time value: {value!r}")
        normalized = value.strip()
        for fmt in ("%Y%m%d%H%M%S%f", "%Y%m%d%H%M%S"):
            try:
                return datetime.strptime(normalized, fmt)
            except ValueError:
                continue
        raise ValueError(f"Invalid BaoStock time value: {value!r}")

    def _pick(self, row: Mapping[str, Any], row_idx: int, field_name: str) -> Any:
        value = row.get(field_name)
        if self._is_missing_value(value):
            raise ValueError(
                "Missing required source field in BaoStock A-share minute-bars row "
                f"idx={row_idx}, field={field_name!r}."
            )
        return value

    def _to_nonnegative_float(self, value: Any, *, field_name: str) -> float:
        if self._is_missing_value(value):
            raise ValueError(f"Invalid {field_name} value: missing")
        if isinstance(value, bool):
            raise ValueError(f"Invalid {field_name} value type: bool")
        if isinstance(value, (int, float)):
            numeric_value = float(value)
        elif isinstance(value, str):
            normalized = value.strip().replace(",", "")
            if normalized == "":
                raise ValueError(f"Invalid {field_name} value: empty string")
            try:
                numeric_value = float(normalized)
            except ValueError as exc:
                raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
        else:
            raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")
        if not math.isfinite(numeric_value) or numeric_value < 0:
            raise ValueError(f"Invalid {field_name} value: {value!r}")
        return numeric_value

    def _is_missing_value(self, value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, float) and math.isnan(value):
            return True
        if isinstance(value, str) and value.strip() == "":
            return True
        return False


__all__ = [
    "BAOSTOCK_SOURCE_ID",
    "BAOSTOCK_SOURCE_NAME",
    "BaoStockAShareMinuteBarsAdapter",
]
