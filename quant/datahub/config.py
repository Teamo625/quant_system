"""Configuration primitives for local DataHub storage."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class DataHubConfig:
    """Local filesystem configuration used by DataHub components."""

    root_dir: Path
    raw_subdir: str = "raw"
    curated_subdir: str = "curated"
    meta_subdir: str = "meta"

    @classmethod
    def from_env(cls, env_var: str = "QUANT_DATAHUB_ROOT") -> "DataHubConfig":
        """Build config from environment or use a local default path."""
        configured = os.getenv(env_var)
        root = Path(configured) if configured else Path(".quant_datahub")
        return cls(root_dir=root)

    @property
    def raw_dir(self) -> Path:
        return self.root_dir / self.raw_subdir

    @property
    def curated_dir(self) -> Path:
        return self.root_dir / self.curated_subdir

    @property
    def meta_dir(self) -> Path:
        return self.root_dir / self.meta_subdir

