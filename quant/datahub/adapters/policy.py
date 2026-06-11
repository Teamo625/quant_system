"""Public policy-document source adapter implementations."""

from __future__ import annotations

import hashlib
import inspect
import json
import re
import socket
import ssl
from datetime import date, datetime, timezone
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import urlencode
from urllib.request import urlopen

from ..datasets import DatasetName, DatasetRegistry
from .akshare import MACRO_POLICY_SOURCE_ID, MACRO_POLICY_SOURCE_NAME


class MacroPolicyDocumentsAdapter:
    """Narrow public-source adapter for policy document metadata."""

    source_name = MACRO_POLICY_SOURCE_ID
    source_display_name = MACRO_POLICY_SOURCE_NAME

    _DEFAULT_REGION = "CN"
    _SEARCH_BASE_URL = "https://sousuo.www.gov.cn/search-gov/data"
    _ROUTE_ORDER: tuple[tuple[str, str], ...] = (
        ("zhengcelibrary_gw", "国务院文件"),
        ("zhengcelibrary_bm", "国务院部门文件"),
    )
    _ROUTE_BY_NORMALIZED_SELECTOR: dict[str, tuple[str, str]] = {
        route_t.upper(): (route_t, route_document_type)
        for route_t, route_document_type in _ROUTE_ORDER
    }

    def __init__(
        self,
        *,
        fetch_policy_documents: Callable[..., Any] | None = None,
        now_fn: Callable[[], datetime] | None = None,
        max_records_per_route: int = 20,
        request_timeout_seconds: int = 20,
        allow_insecure_tls_fallback: bool = True,
        source_type: str = "gwyzcwjk",
    ) -> None:
        if max_records_per_route <= 0:
            raise ValueError("max_records_per_route must be positive.")
        if request_timeout_seconds <= 0:
            raise ValueError("request_timeout_seconds must be positive.")
        if not isinstance(source_type, str) or source_type.strip() == "":
            raise ValueError("source_type must be a non-empty string.")

        self._fetch_policy_documents = fetch_policy_documents
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._max_records_per_route = max_records_per_route
        self._request_timeout_seconds = request_timeout_seconds
        self._allow_insecure_tls_fallback = allow_insecure_tls_fallback
        self._source_type = source_type.strip()
        self._registry = DatasetRegistry()

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if dataset != DatasetName.POLICY_DOCUMENTS:
            raise ValueError(
                "Unsupported dataset for MacroPolicyDocumentsAdapter: "
                f"{dataset.value}"
            )
        if start_date is not None and end_date is not None and end_date < start_date:
            raise ValueError(
                "Invalid date range for MacroPolicyDocumentsAdapter: "
                f"start_date={start_date.isoformat()} > end_date={end_date.isoformat()}."
            )

        selected_routes = self._resolve_route_filters(symbols)
        records = self._fetch_policy_documents_records(
            dataset=dataset,
            selected_routes=selected_routes,
            start_date=start_date,
            end_date=end_date,
        )
        return self._filter_records_by_date(
            records=records,
            start_date=start_date,
            end_date=end_date,
        )

    def _resolve_route_filters(
        self,
        symbols: list[str] | None,
    ) -> tuple[tuple[str, str], ...]:
        if symbols is None or len(symbols) == 0:
            return self._ROUTE_ORDER

        resolved_routes: list[tuple[str, str]] = []
        seen: set[str] = set()
        supported = ", ".join(sorted(route for route in self._ROUTE_BY_NORMALIZED_SELECTOR))
        for idx, symbol in enumerate(symbols):
            if not isinstance(symbol, str) or symbol.strip() == "":
                raise ValueError(
                    f"Policy document route selector at index {idx} must be a non-empty string."
                )

            normalized = symbol.strip().upper()
            if normalized in seen:
                raise ValueError(
                    "Duplicate policy document route selector after normalization: "
                    f"{symbol!r}."
                )
            seen.add(normalized)

            route_definition = self._ROUTE_BY_NORMALIZED_SELECTOR.get(normalized)
            if route_definition is None:
                raise ValueError(
                    "Unsupported policy document route selector "
                    f"{symbol!r}. Supported selectors: {supported}."
                )
            resolved_routes.append(route_definition)
        return tuple(resolved_routes)

    def _fetch_policy_documents_records(
        self,
        *,
        dataset: DatasetName,
        selected_routes: Sequence[tuple[str, str]],
        start_date: date | None,
        end_date: date | None,
    ) -> list[dict[str, Any]]:
        normalized_by_policy_id: dict[str, dict[str, Any]] = {}
        ingested_at = self._now_fn().isoformat()
        schema_version = self._registry.get(dataset).schema_version

        for route_t, route_document_type in selected_routes:
            payload = self._fetch_route_payload(
                route_t=route_t,
                start_date=start_date,
                end_date=end_date,
            )
            rows = self._payload_to_rows(payload=payload, route_t=route_t)
            for row_idx, row in enumerate(rows):
                record = self._normalize_policy_row(
                    row=row,
                    row_idx=row_idx,
                    route_t=route_t,
                    route_document_type=route_document_type,
                    ingested_at=ingested_at,
                    schema_version=schema_version,
                )
                self._validate_record(dataset=dataset, record=record)

                policy_id = str(record["policy_id"])
                existing = normalized_by_policy_id.get(policy_id)
                if existing is None:
                    normalized_by_policy_id[policy_id] = record
                    continue

                if self._is_conflicting_duplicate(existing=existing, candidate=record):
                    raise ValueError(
                        "Conflicting duplicate policy document row detected: "
                        f"policy_id={policy_id!r}."
                    )
                normalized_by_policy_id[policy_id] = self._select_preferred_duplicate_record(
                    existing=existing,
                    candidate=record,
                )

        ordered = list(normalized_by_policy_id.values())
        ordered.sort(key=lambda item: (str(item["publish_date"]), str(item["policy_id"])))
        return ordered

    def _fetch_route_payload(
        self,
        *,
        route_t: str,
        start_date: date | None,
        end_date: date | None,
    ) -> Any:
        fetch_fn = self._resolve_fetch_policy_documents()
        accepted_args, supports_var_kwargs = self._inspect_callable(fetch_fn)
        kwargs: dict[str, Any] = {"route_t": route_t}
        optional_args = {
            "page": 1,
            "page_size": self._max_records_per_route,
            "source_type": self._source_type,
            "timeout_seconds": self._request_timeout_seconds,
            "allow_insecure_tls_fallback": self._allow_insecure_tls_fallback,
            "min_time": None if start_date is None else start_date.isoformat(),
            "max_time": None if end_date is None else end_date.isoformat(),
        }
        for arg_name, arg_value in optional_args.items():
            if arg_value is None:
                continue
            if supports_var_kwargs or arg_name in accepted_args:
                kwargs[arg_name] = arg_value
        return fetch_fn(**kwargs)

    def _resolve_fetch_policy_documents(self) -> Callable[..., Any]:
        if self._fetch_policy_documents is not None:
            return self._fetch_policy_documents
        return self._fetch_policy_documents_from_gov_search

    def _fetch_policy_documents_from_gov_search(
        self,
        *,
        route_t: str,
        page: int,
        page_size: int,
        source_type: str,
        timeout_seconds: int,
        allow_insecure_tls_fallback: bool,
        min_time: str | None = None,
        max_time: str | None = None,
    ) -> Mapping[str, Any]:
        query_params = {
            "t": route_t,
            "q": "",
            "timetype": "",
            "mintime": min_time or "",
            "maxtime": max_time or "",
            "sort": "score",
            "sortType": "1",
            "searchfield": "title:content:summary",
            "pcodeJiguan": "",
            "childtype": "",
            "subchildtype": "",
            "tsbq": "",
            "pubtimeyear": "",
            "puborg": "",
            "pcodeYear": "",
            "pcodeNum": "",
            "filetype": "",
            "p": str(page),
            "n": str(page_size),
            "inpro": "",
            "bmfl": "",
            "dup": "",
            "orpro": "",
            "bmpubyear": "",
            "type": source_type,
        }

        url = f"{self._SEARCH_BASE_URL}?{urlencode(query_params)}"
        try:
            return self._request_json(url=url, timeout_seconds=timeout_seconds, insecure_tls=False)
        except Exception as exc:
            if not allow_insecure_tls_fallback or not self._is_tls_verification_failure(exc):
                raise
        return self._request_json(url=url, timeout_seconds=timeout_seconds, insecure_tls=True)

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

    def _request_json(
        self,
        *,
        url: str,
        timeout_seconds: int,
        insecure_tls: bool,
    ) -> Mapping[str, Any]:
        context = None
        if insecure_tls:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        with urlopen(url, timeout=timeout_seconds, context=context) as response:
            raw = response.read().decode("utf-8", errors="ignore")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("Policy search route returned non-JSON payload.") from exc
        if not isinstance(parsed, Mapping):
            raise ValueError(
                "Policy search route must return mapping JSON payload, "
                f"got {type(parsed).__name__}."
            )
        return parsed

    def _payload_to_rows(
        self,
        *,
        payload: Any,
        route_t: str,
    ) -> list[Mapping[str, Any]]:
        if hasattr(payload, "to_dict"):
            candidate = payload.to_dict(orient="records")
            return self._normalize_candidate_rows(candidate=candidate, route_t=route_t)

        if isinstance(payload, list):
            return self._normalize_candidate_rows(candidate=payload, route_t=route_t)

        if isinstance(payload, Mapping):
            search_obj = payload.get("searchVO")
            if isinstance(search_obj, Mapping):
                list_rows = search_obj.get("listVO")
                if isinstance(list_rows, list):
                    return self._normalize_candidate_rows(candidate=list_rows, route_t=route_t)

            list_rows = payload.get("listVO")
            if isinstance(list_rows, list):
                return self._normalize_candidate_rows(candidate=list_rows, route_t=route_t)

        raise ValueError(
            "Policy documents payload must be DataFrame-like, list[Mapping], "
            f"or search response mapping, got {type(payload).__name__}."
        )

    def _normalize_candidate_rows(
        self,
        *,
        candidate: Any,
        route_t: str,
    ) -> list[Mapping[str, Any]]:
        if not isinstance(candidate, list):
            raise ValueError(
                "Policy documents payload rows must be a list after conversion, "
                f"route={route_t}, got {type(candidate).__name__}."
            )

        rows: list[Mapping[str, Any]] = []
        for idx, row in enumerate(candidate):
            if not isinstance(row, Mapping):
                raise ValueError(
                    "Policy documents payload row must be mapping. "
                    f"route={route_t}, idx={idx}, got={type(row).__name__}."
                )
            rows.append(row)
        return rows

    def _normalize_policy_row(
        self,
        *,
        row: Mapping[str, Any],
        row_idx: int,
        route_t: str,
        route_document_type: str,
        ingested_at: str,
        schema_version: str,
    ) -> dict[str, Any]:
        publish_date = self._normalize_date(
            self._pick(row, row_idx, "publish_date", "pubtime", "pubtimeStr"),
            field_name="publish_date",
        )
        title = self._normalize_required_text(
            self._pick(row, row_idx, "title"),
            field_name="title",
        )
        authority_value = self._pick_optional(row, "authority", "puborg", "fwdw")
        authority = self._normalize_required_text(authority_value, field_name="authority")
        document_type_value = self._pick_optional(row, "document_type", "wjlx", "dateType")
        if document_type_value is None:
            document_type_value = route_document_type
        document_type = self._normalize_required_text(
            document_type_value,
            field_name="document_type",
        )

        url = self._normalize_optional_text(
            self._pick_optional(row, "url", "link"),
            field_name="url",
        )
        summary = self._normalize_optional_text(
            self._pick_optional(row, "summary", "content"),
            field_name="summary",
        )
        source_ts = self._pick_optional(row, "source_ts", "ptime", "update_time")
        source_policy_id = self._pick_optional(row, "policy_id", "id")
        policy_id = self._build_policy_id(
            source_policy_id=source_policy_id,
            title=title,
            publish_date=publish_date,
            authority=authority,
            document_type=document_type,
            url=url,
        )

        record: dict[str, Any] = {
            "policy_id": policy_id,
            "region": self._DEFAULT_REGION,
            "publish_date": publish_date,
            "title": title,
            "authority": authority,
            "document_type": document_type,
            "source": MACRO_POLICY_SOURCE_ID,
            "ingested_at": ingested_at,
            "schema_version": schema_version,
        }
        if summary is not None:
            record["summary"] = summary
        if url is not None:
            record["url"] = url
        if source_ts is not None:
            record["source_ts"] = self._normalize_datetime(source_ts, field_name="source_ts")
        return record

    def _validate_record(
        self,
        *,
        dataset: DatasetName,
        record: Mapping[str, Any],
    ) -> None:
        issues = self._registry.validate_record(dataset, dict(record))
        if issues:
            raise ValueError(
                f"Normalized {dataset.value} record failed DatasetRegistry validation: {issues!r}"
            )

    def _build_policy_id(
        self,
        *,
        source_policy_id: Any | None,
        title: str,
        publish_date: str,
        authority: str,
        document_type: str,
        url: str | None,
    ) -> str:
        if source_policy_id is not None:
            stable_source_id = self._normalize_required_text(
                source_policy_id,
                field_name="policy_id",
            )
            return f"GOVCN-{stable_source_id}"

        stable_fields = (
            title,
            publish_date,
            authority,
            document_type,
            url or "",
        )
        digest = hashlib.sha1("|".join(stable_fields).encode("utf-8")).hexdigest()
        return f"GOVPOL-{digest[:24]}"

    def _filter_records_by_date(
        self,
        *,
        records: Sequence[Mapping[str, Any]],
        start_date: date | None,
        end_date: date | None,
    ) -> list[dict[str, Any]]:
        filtered: list[dict[str, Any]] = []
        for record in records:
            publish_dt = date.fromisoformat(str(record["publish_date"]))
            if start_date is not None and publish_dt < start_date:
                continue
            if end_date is not None and publish_dt > end_date:
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
                value = row[key]
                if not self._is_missing_value(value):
                    return value
        raise ValueError(
            "Missing required source field in policy documents row "
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
        if value is None or self._is_missing_value(value):
            raise ValueError(f"Invalid {field_name} value: empty string")
        if isinstance(value, bool):
            raise ValueError(f"Invalid {field_name} value type: bool")
        text = str(value)
        stripped = self._strip_html(text).strip()
        if stripped == "":
            raise ValueError(f"Invalid {field_name} value: empty string")
        return stripped

    def _normalize_optional_text(self, value: Any | None, *, field_name: str) -> str | None:
        if value is None:
            return None
        return self._normalize_required_text(value, field_name=field_name)

    def _normalize_date(self, value: Any, *, field_name: str) -> str:
        if self._is_missing_value(value):
            raise ValueError(f"Invalid {field_name} value: missing")
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return self._epoch_to_datetime(value).date().isoformat()
        if isinstance(value, str):
            stripped = self._strip_html(value).strip()
            if stripped == "":
                raise ValueError(f"Invalid {field_name} value: empty string")
            if stripped.isdigit():
                return self._normalize_digit_date_or_epoch(
                    stripped,
                    field_name=field_name,
                )
            try:
                return datetime.fromisoformat(stripped).date().isoformat()
            except ValueError:
                try:
                    return date.fromisoformat(stripped).isoformat()
                except ValueError as exc:
                    raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _normalize_datetime(self, value: Any, *, field_name: str) -> str:
        if self._is_missing_value(value):
            raise ValueError(f"Invalid {field_name} value: missing")
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time()).isoformat()
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return self._epoch_to_datetime(value).isoformat()
        if isinstance(value, str):
            stripped = self._strip_html(value).strip()
            if stripped == "":
                raise ValueError(f"Invalid {field_name} value: empty string")
            if stripped.isdigit():
                if len(stripped) == 8:
                    parsed_date = date.fromisoformat(
                        f"{stripped[0:4]}-{stripped[4:6]}-{stripped[6:8]}"
                    )
                    return datetime.combine(parsed_date, datetime.min.time()).isoformat()
                return self._epoch_to_datetime(float(stripped)).isoformat()
            try:
                return datetime.fromisoformat(stripped).isoformat()
            except ValueError:
                try:
                    parsed_date = date.fromisoformat(stripped)
                    return datetime.combine(parsed_date, datetime.min.time()).isoformat()
                except ValueError as exc:
                    raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
        raise ValueError(f"Invalid {field_name} value type: {type(value).__name__}")

    def _normalize_digit_date_or_epoch(self, value: str, *, field_name: str) -> str:
        if len(value) == 8:
            return date.fromisoformat(
                f"{value[0:4]}-{value[4:6]}-{value[6:8]}"
            ).isoformat()
        try:
            epoch_value = float(value)
        except ValueError as exc:
            raise ValueError(f"Invalid {field_name} value: {value!r}") from exc
        return self._epoch_to_datetime(epoch_value).date().isoformat()

    def _epoch_to_datetime(self, value: float) -> datetime:
        epoch_seconds = value
        if abs(epoch_seconds) >= 1_000_000_000_000:
            epoch_seconds = epoch_seconds / 1000.0
        return datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).replace(tzinfo=None)

    def _strip_html(self, text: str) -> str:
        compact = re.sub(r"<[^>]+>", " ", text)
        return " ".join(compact.split())

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
            "region",
            "publish_date",
            "title",
            "authority",
            "document_type",
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

    def _is_tls_verification_failure(self, exc: BaseException) -> bool:
        for cause in self._exception_chain(exc):
            message = str(cause).lower()
            if "certificate verify failed" in message:
                return True
            if isinstance(cause, ssl.SSLCertVerificationError):
                return True
        return False

    def _exception_chain(self, exc: BaseException) -> Sequence[BaseException]:
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
        return chain

    def is_live_environment_unavailable(self, exc: BaseException) -> bool:
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
            "ssl",
            "certificate verify failed",
            "sousuo.www.gov.cn",
            "search-gov/data",
            "gov.cn",
        )

        for cause in self._exception_chain(exc):
            name = type(cause).__name__
            module = type(cause).__module__
            message = str(cause).lower()

            if name in network_exception_names:
                return True
            if module.startswith(("requests", "urllib3")) and any(
                token in message for token in network_message_tokens
            ):
                return True
            if isinstance(cause, (socket.timeout, TimeoutError, ConnectionError, ssl.SSLError)):
                return True
            if isinstance(cause, OSError):
                if cause.errno in {101, 104, 110, 111, 113}:
                    return True
                if any(token in message for token in network_message_tokens):
                    return True
        return False
