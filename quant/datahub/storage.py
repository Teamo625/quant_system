"""Local storage helpers for DataHub datasets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from .config import DataHubConfig
from .datasets import DatasetName, DatasetRegistry


class LocalStorage:
    """Resolves deterministic local paths and local IO for datasets."""

    def __init__(self, config: DataHubConfig) -> None:
        self._config = config

    def ensure_base_dirs(self) -> None:
        """Create base DataHub directories on local disk."""
        self._config.raw_dir.mkdir(parents=True, exist_ok=True)
        self._config.curated_dir.mkdir(parents=True, exist_ok=True)
        self._config.meta_dir.mkdir(parents=True, exist_ok=True)

    def dataset_dir(
        self,
        dataset: DatasetName,
        *,
        layer: str = "curated",
        ensure_exists: bool = False,
    ) -> Path:
        """Resolve local directory path for a dataset in a storage layer."""
        base = self._resolve_layer_dir(layer=layer)
        target = base / dataset.value
        if ensure_exists:
            target.mkdir(parents=True, exist_ok=True)
        return target

    def dataset_file(
        self,
        dataset: DatasetName,
        *,
        layer: str = "curated",
        ext: str = "parquet",
    ) -> Path:
        """Resolve a conventional dataset file path without reading or writing."""
        return self.dataset_dir(dataset, layer=layer) / f"{dataset.value}.{ext}"

    def write_records(
        self,
        dataset: DatasetName,
        records: Iterable[Mapping[str, Any]],
        *,
        layer: str = "curated",
        ext: str = "jsonl",
        validate_schema: bool = False,
        registry: DatasetRegistry | None = None,
    ) -> Path:
        """Write in-memory records to a deterministic local JSONL dataset file."""
        output_path = self.dataset_file(dataset, layer=layer, ext=ext)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if validate_schema:
            registry = registry or DatasetRegistry()

        with output_path.open("w", encoding="utf-8") as handle:
            for index, record in enumerate(records):
                if validate_schema:
                    issues = registry.validate_record(dataset, record)
                    if issues:
                        issue_text = "; ".join(
                            f"{issue.code}:{issue.field}" for issue in issues
                        )
                        raise ValueError(
                            f"Record {index} failed schema validation: {issue_text}"
                        )
                handle.write(json.dumps(dict(record), ensure_ascii=True, sort_keys=True))
                handle.write("\n")

        return output_path

    def read_records(
        self,
        dataset: DatasetName,
        *,
        layer: str = "curated",
        ext: str = "jsonl",
        on_missing: str = "empty",
    ) -> list[dict[str, Any]]:
        """Read records from a deterministic local JSONL dataset file."""
        input_path = self.dataset_file(dataset, layer=layer, ext=ext)

        if not input_path.exists():
            if on_missing == "empty":
                return []
            if on_missing == "raise":
                raise FileNotFoundError(f"Dataset file not found: {input_path}")
            raise ValueError(f"Unsupported on_missing strategy: {on_missing}")

        records: list[dict[str, Any]] = []
        with input_path.open("r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                parsed = json.loads(stripped)
                if not isinstance(parsed, dict):
                    raise ValueError(
                        f"Expected object JSON at line {line_no} in {input_path}"
                    )
                records.append(parsed)
        return records

    def write_metadata(
        self,
        dataset: DatasetName,
        metadata: Mapping[str, Any],
        *,
        layer: str = "meta",
        ext: str = "json",
    ) -> Path:
        """Write dataset metadata as a local JSON file."""
        output_path = self.dataset_file(dataset, layer=layer, ext=ext)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(dict(metadata), handle, ensure_ascii=True, sort_keys=True)
            handle.write("\n")
        return output_path

    def read_metadata(
        self,
        dataset: DatasetName,
        *,
        layer: str = "meta",
        ext: str = "json",
        on_missing: str = "empty",
    ) -> dict[str, Any]:
        """Read dataset metadata from a local JSON file."""
        input_path = self.dataset_file(dataset, layer=layer, ext=ext)

        if not input_path.exists():
            if on_missing == "empty":
                return {}
            if on_missing == "raise":
                raise FileNotFoundError(f"Metadata file not found: {input_path}")
            raise ValueError(f"Unsupported on_missing strategy: {on_missing}")

        with input_path.open("r", encoding="utf-8") as handle:
            parsed = json.load(handle)
        if not isinstance(parsed, dict):
            raise ValueError(f"Expected object JSON in {input_path}")
        return parsed

    def _resolve_layer_dir(self, *, layer: str) -> Path:
        if layer == "raw":
            return self._config.raw_dir
        if layer == "curated":
            return self._config.curated_dir
        if layer == "meta":
            return self._config.meta_dir
        raise ValueError(f"Unsupported layer: {layer}")
