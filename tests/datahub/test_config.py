import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from quant.datahub.config import DataHubConfig


class DataHubConfigTests(unittest.TestCase):
    def test_config_uses_default_root_when_env_missing(self) -> None:
        original = os.environ.pop("QUANT_DATAHUB_ROOT", None)
        try:
            config = DataHubConfig.from_env()
        finally:
            if original is not None:
                os.environ["QUANT_DATAHUB_ROOT"] = original

        self.assertEqual(config.root_dir, Path(".quant_datahub"))
        self.assertEqual(config.raw_dir, Path(".quant_datahub/raw"))
        self.assertEqual(config.curated_dir, Path(".quant_datahub/curated"))
        self.assertEqual(config.meta_dir, Path(".quant_datahub/meta"))

    def test_config_reads_root_from_env(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "warehouse"
            original = os.environ.get("QUANT_DATAHUB_ROOT")
            os.environ["QUANT_DATAHUB_ROOT"] = str(root)
            try:
                config = DataHubConfig.from_env()
            finally:
                if original is None:
                    os.environ.pop("QUANT_DATAHUB_ROOT", None)
                else:
                    os.environ["QUANT_DATAHUB_ROOT"] = original

        self.assertEqual(config.root_dir, root)
