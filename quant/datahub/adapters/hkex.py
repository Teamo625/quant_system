"""HKEX-backed DataHub source adapters."""

from __future__ import annotations

import hashlib
import html
import re
from datetime import date, datetime, timezone
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from ..datasets import DatasetName, DatasetRegistry

HKEX_SOURCE_ID = "hkex_disclosure_and_calendar_family"
HKEX_SOURCE_NAME = "HKEX Disclosure and Calendar Family"


class HkexCompanyAnnouncementsAdapter:
    """Narrow HKEX adapter for listed company announcements only."""

    source_name = HKEX_SOURCE_ID
    source_display_name = HKEX_SOURCE_NAME

    _DEFAULT_MARKET = "HK"
    _DEFAULT_ANNOUNCEMENT_TYPE = "general"
    _DEFAULT_ANNOUNCEMENTS_URL = "https://www1.hkexnews.hk/search/predefineddoc.xhtml?lang=en"
    _HK_SYMBOL_PATTERN = re.compile(r"^\d{1,5}$")
    _SOURCE_SYMBOL_LABEL_PATTERN = re.compile(
        r"(?:STOCK\s*CODE|股份代號|股份代号|证券代码|證券代號)\s*[:：]\s*(\d{1,5})(?:\.HK)?\b",
        flags=re.IGNORECASE,
    )

    def __init__(
        self,
        *,
        fetch_company_announcements: Callable[..., Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
        max_records_without_symbols: int = 200,
        announcements_url: str = _DEFAULT_ANNOUNCEMENTS_URL,
        default_announcement_type: str = _DEFAULT_ANNOUNCEMENT_TYPE,
    ) -> None:
        if max_records_without_symbols <= 0:
            raise ValueError("max_records_without_symbols must be positive.")
        if not isinstance(announcements_url, str) or announcements_url.strip() == "":
            raise ValueError("announcements_url must be a non-empty string.")
        if (
            not isinstance(default_announcement_type, str)
            or default_announcement_type.strip() == ""
        ):
            raise ValueError("default_announcement_type must be a non-empty string.")

        self._fetch_company_announcements = fetch_company_announcements
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._max_records_without_symbols = max_records_without_symbols
        self._announcements_url = announcements_url.strip()
        self._default_announcement_type = default_announcement_type.strip().lower()
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if dataset != DatasetName.COMPANY_ANNOUNCEMENTS:
            raise ValueError(
                "Unsupported dataset for HkexCompanyAnnouncementsAdapter: "
                f"{dataset.value}"
            )

        requested_symbols = self._normalize_requested_symbols(symbols)
        requested_symbol_set = (
            set(requested_symbols) if requested_symbols is not None else None
        )

        rows = self._fetch_announcement_rows()
        records = self._normalize_announcement_rows(
            rows=rows,
            dataset=dataset,
            requested_symbol_set=requested_symbol_set,
        )
        records = self._filter_records_by_date(
            records=records,
            start_date=start_date,
            end_date=end_date,
        )
        if requested_symbols is None:
            records = self._bounded_default_subset(records)
        return records

    def _resolve_fetch_company_announcements(self) -> Callable[..., Any]:
        if self._fetch_company_announcements is not None:
            return self._fetch_company_announcements
        return self._fetch_live_announcement_page

    def _fetch_live_announcement_page(self) -> str:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        # Prefer requests because certifi-backed trust roots are often more robust
        # than platform defaults in containerized CI/local environments.
        try:
            import requests  # type: ignore[import-not-found]

            response = requests.get(
                self._announcements_url,
                headers=headers,
                timeout=20,
            )
            response.raise_for_status()
            return response.text
        except Exception:
            pass

        request = Request(self._announcements_url, headers=headers)
        with urlopen(request, timeout=20) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")

    def _fetch_announcement_rows(self) -> list[Mapping[str, Any]]:
        fetch_fn = self._resolve_fetch_company_announcements()
        raw_payload = fetch_fn()
        return self._payload_to_rows(raw_payload)

    def _payload_to_rows(self, payload: Any) -> list[Mapping[str, Any]]:
        if isinstance(payload, str):
            return self._parse_predefineddoc_html_rows(payload)

        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
        else:
            candidate = payload

        if not isinstance(candidate, list):
            raise ValueError(
                "HKEX company announcements payload must be HTML str, DataFrame-like, "
                f"or list[Mapping], got {type(payload).__name__}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "HKEX company announcements payload row must be mapping. "
                    f"idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _parse_predefineddoc_html_rows(self, html_text: str) -> list[Mapping[str, Any]]:
        tbody_match = re.search(
            r"<tbody[^>]*>(.*?)</tbody>",
            html_text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if tbody_match is None:
            raise ValueError("HKEX announcements HTML payload missing <tbody> segment.")

        row_blocks = re.findall(
            r"<tr[^>]*>(.*?)</tr>",
            tbody_match.group(1),
            flags=re.IGNORECASE | re.DOTALL,
        )
        rows: list[Mapping[str, Any]] = []
        for row_idx, row_block in enumerate(row_blocks):
            release_time = self._extract_row_value(
                row_block=row_block,
                class_name="release-time",
                field_name="release_time",
                row_idx=row_idx,
            )
            stock_code = self._extract_row_value(
                row_block=row_block,
                class_name="stock-short-code",
                field_name="stock_code",
                row_idx=row_idx,
            )
            headline = self._extract_row_value(
                row_block=row_block,
                class_name="headline",
                field_name="headline",
                row_idx=row_idx,
            )

            link_match = re.search(
                r"<a[^>]*href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>",
                row_block,
                flags=re.IGNORECASE | re.DOTALL,
            )
            if link_match is None:
                raise ValueError(
                    "HKEX announcements HTML row missing document link: "
                    f"row_idx={row_idx}."
                )
            url_value = self._normalize_text(link_match.group(1), field_name="url")
            title_value = self._normalize_text(link_match.group(2), field_name="title")

            rows.append(
                {
                    "release_time": release_time,
                    "stock_code": stock_code,
                    "headline": headline,
                    "title": title_value,
                    "url": urljoin("https://www1.hkexnews.hk", url_value),
                }
            )
        return rows

    def _extract_row_value(
        self,
        *,
        row_block: str,
        class_name: str,
        field_name: str,
        row_idx: int,
    ) -> str:
        match = re.search(
            rf"<(?:td|div)[^>]*class=['\"][^'\"]*{re.escape(class_name)}[^'\"]*['\"][^>]*>(.*?)</(?:td|div)>",
            row_block,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if match is None:
            raise ValueError(
                "HKEX announcements HTML row missing expected field: "
                f"field={field_name!r}, row_idx={row_idx}."
            )
        return self._normalize_text(match.group(1), field_name=field_name)

    def _normalize_announcement_rows(
        self,
        *,
        rows: Sequence[Mapping[str, Any]],
        dataset: DatasetName,
        requested_symbol_set: set[str] | None,
    ) -> list[dict[str, Any]]:
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version
        normalized_by_key: dict[str, dict[str, Any]] = {}

        for idx, row in enumerate(rows):
            raw_symbol = self._pick_optional(
                row,
                "symbol",
                "stock_code",
                "code",
                "证券代码",
                "股份代号",
            )
            if raw_symbol is None:
                continue
            try:
                symbol = self._normalize_source_hk_symbol(raw_symbol)
            except ValueError:
                # HKEX predefined document feeds may include non-company rows
                # where stock-code cells are blank/label-only; skip those rows.
                continue

            if requested_symbol_set is not None and symbol not in requested_symbol_set:
                continue

            publish_time = self._normalize_publish_time(
                self._pick(
                    row,
                    idx,
                    "publish_time",
                    "release_time",
                    "time",
                    "date",
                    "日期",
                    "发布时间",
                )
            )

            title = self._normalize_text(
                self._pick(
                    row,
                    idx,
                    "title",
                    "announcement_title",
                    "document_title",
                    "doc_title",
                    "标题",
                ),
                field_name="title",
            )

            announcement_type = self._normalize_announcement_type(
                self._pick_optional(
                    row,
                    "announcement_type",
                    "type",
                    "category",
                    "headline",
                    "公告类别",
                )
            )

            url_value = self._pick_optional(
                row,
                "url",
                "link",
                "href",
            )
            url = (
                self._normalize_text(url_value, field_name="url")
                if url_value is not None
                else None
            )

            source_ts_value = self._pick_optional(
                row,
                "source_ts",
                "update_time",
                "更新时间",
            )

            source_announcement_id = self._pick_optional(
                row,
                "announcement_id",
                "announcementId",
                "id",
            )
            if source_announcement_id is not None:
                announcement_id = self._normalize_text(
                    source_announcement_id,
                    field_name="announcement_id",
                )
            else:
                announcement_id = self._build_deterministic_announcement_id(
                    symbol=symbol,
                    publish_time=publish_time,
                    title=title,
                    announcement_type=announcement_type,
                    url=url,
                )

            record: dict[str, Any] = {
                "announcement_id": announcement_id,
                "symbol": symbol,
                "market": self._DEFAULT_MARKET,
                "publish_time": publish_time,
                "announcement_type": announcement_type,
                "title": title,
                "source": HKEX_SOURCE_ID,
                "ingested_at": ingested_at,
                "schema_version": schema_version,
            }
            if url is not None:
                record["url"] = url
            if source_ts_value is not None:
                record["source_ts"] = self._normalize_source_ts(source_ts_value)

            existing = normalized_by_key.get(announcement_id)
            if existing is None:
                normalized_by_key[announcement_id] = record
                continue
            if self._is_conflicting_duplicate(existing=existing, candidate=record):
                raise ValueError(
                    "Conflicting duplicate company announcement row detected: "
                    f"announcement_id={announcement_id!r}."
                )
            normalized_by_key[announcement_id] = self._select_preferred_duplicate_record(
                existing=existing,
                candidate=record,
            )

        return list(normalized_by_key.values())

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

    def _bounded_default_subset(
        self,
        records: Sequence[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        bounded = sorted(
            (dict(record) for record in records),
            key=lambda record: (
                str(record.get("publish_time", "")),
                str(record.get("announcement_id", "")),
            ),
            reverse=True,
        )
        return bounded[: self._max_records_without_symbols]

    def _normalize_requested_symbols(self, symbols: list[str] | None) -> list[str] | None:
        if symbols is None or len(symbols) == 0:
            return None
        normalized: list[str] = []
        seen: set[str] = set()
        for symbol in symbols:
            canonical = self._normalize_requested_hk_symbol(symbol)
            if canonical in seen:
                continue
            seen.add(canonical)
            normalized.append(canonical)
        return normalized

    def _normalize_requested_hk_symbol(self, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError(
                "Invalid HK symbol value type: "
                f"{type(value).__name__}"
            )
        normalized = value.strip().upper()
        if normalized == "":
            raise ValueError("Invalid HK symbol value: empty string.")

        code = normalized
        if "." in normalized:
            head, market = normalized.split(".", 1)
            if market != "HK":
                raise ValueError(
                    f"Unsupported HK symbol market suffix: {market!r}. Expected '.HK'."
                )
            code = head

        if not self._HK_SYMBOL_PATTERN.fullmatch(code):
            raise ValueError(
                f"Unsupported HK symbol format: {value!r}. "
                "Expected forms like '700', '00700', or '00700.HK'."
            )
        return f"{code.zfill(5)}.HK"

    def _normalize_source_hk_symbol(self, value: Any) -> str:
        try:
            return self._normalize_requested_hk_symbol(value)
        except ValueError:
            if not isinstance(value, str):
                raise
            normalized = value.strip().upper()
            label_match = self._SOURCE_SYMBOL_LABEL_PATTERN.search(normalized)
            if label_match is None:
                raise
            return f"{label_match.group(1).zfill(5)}.HK"

    def _normalize_publish_time(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time()).isoformat()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                raise ValueError("Invalid publish_time value: empty string.")

            label_match = re.search(
                r"(\d{1,2}/\d{1,2}/\d{4}(?:\s+\d{2}:\d{2}(?::\d{2})?)?)",
                stripped,
            )
            if label_match is not None:
                stripped = label_match.group(1).strip()

            if len(stripped) == 8 and stripped.isdigit():
                parsed_date = date.fromisoformat(
                    f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                )
                return datetime.combine(parsed_date, datetime.min.time()).isoformat()

            for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
                try:
                    parsed = datetime.strptime(stripped, fmt)
                    if fmt == "%d/%m/%Y":
                        return datetime.combine(parsed.date(), datetime.min.time()).isoformat()
                    return parsed.isoformat()
                except ValueError:
                    continue

            try:
                return datetime.fromisoformat(stripped).isoformat()
            except ValueError:
                try:
                    parsed_date = date.fromisoformat(stripped)
                    return datetime.combine(parsed_date, datetime.min.time()).isoformat()
                except ValueError as exc:
                    raise ValueError(f"Invalid publish_time value: {value!r}") from exc

        raise ValueError(f"Invalid publish_time value type: {type(value).__name__}")

    def _normalize_source_ts(self, value: Any) -> str:
        try:
            return self._normalize_publish_time(value)
        except ValueError as exc:
            raise ValueError(f"Invalid source_ts value: {value!r}") from exc

    def _normalize_announcement_type(self, value: Any | None) -> str:
        if value is None:
            return self._default_announcement_type
        normalized = self._normalize_text(value, field_name="announcement_type")
        if " - [" in normalized:
            normalized = normalized.split(" - [", 1)[0].strip()
        if normalized == "":
            return self._default_announcement_type
        return normalized.lower()

    def _build_deterministic_announcement_id(
        self,
        *,
        symbol: str,
        publish_time: str,
        title: str,
        announcement_type: str,
        url: str | None,
    ) -> str:
        stable_fields = (
            symbol,
            publish_time,
            title,
            announcement_type,
            url or "",
        )
        digest = hashlib.sha1("|".join(stable_fields).encode("utf-8")).hexdigest()
        return f"HKEXANN-{digest[:24]}"

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
            "Missing required source field in company announcement row "
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

    def _normalize_text(self, value: Any, *, field_name: str) -> str:
        if not isinstance(value, str):
            raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")
        decoded = html.unescape(value)
        compact = re.sub(r"<[^>]+>", " ", decoded)
        compact = " ".join(compact.replace("\xa0", " ").split())
        if compact == "":
            raise ValueError(f"Invalid {field_name} value: empty string")
        return compact

    def _is_conflicting_duplicate(
        self,
        *,
        existing: Mapping[str, Any],
        candidate: Mapping[str, Any],
    ) -> bool:
        comparable_fields = (
            "symbol",
            "market",
            "publish_time",
            "announcement_type",
            "title",
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
