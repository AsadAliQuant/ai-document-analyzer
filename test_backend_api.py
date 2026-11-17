import json
import tempfile
import unittest
from pathlib import Path

from backend_api import DEFAULT_API_BASE_URL, resolve_api_base_url


class BackendApiBaseUrlTests(unittest.TestCase):
    @staticmethod
    def _write(root, relative, value):
        path = Path(root, *relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"API_BASE_URL": value}), encoding="utf-8")

    def test_precedence_and_trailing_slash_normalization(self):
        with tempfile.TemporaryDirectory() as appdata, tempfile.TemporaryDirectory() as bundle, tempfile.TemporaryDirectory() as development:
            self._write(development, ["config.json"], "https://development.test/")
            self._write(bundle, ["config.json"], "https://bundle.test///")
            self._write(appdata, ["AI Document Analyzer", "config.json"], "https://appdata.test/")

            self.assertEqual(resolve_api_base_url(appdata_dir=appdata, bundled_dir=bundle, development_dir=development), "https://appdata.test")
            Path(appdata, "AI Document Analyzer", "config.json").unlink()
            self.assertEqual(resolve_api_base_url(appdata_dir=appdata, bundled_dir=bundle, development_dir=development), "https://bundle.test")
            Path(bundle, "config.json").unlink()
            self.assertEqual(resolve_api_base_url(appdata_dir=appdata, bundled_dir=bundle, development_dir=development), "https://development.test")
            Path(development, "config.json").unlink()
            self.assertEqual(resolve_api_base_url(appdata_dir=appdata, bundled_dir=bundle, development_dir=development), DEFAULT_API_BASE_URL)

    def test_invalid_config_falls_through(self):
        with tempfile.TemporaryDirectory() as appdata, tempfile.TemporaryDirectory() as bundle, tempfile.TemporaryDirectory() as development:
            self._write(appdata, ["AI Document Analyzer", "config.json"], "")
            Path(bundle, "config.json").write_text("not-json", encoding="utf-8")
            self._write(development, ["config.json"], "https://valid.test/")
            self.assertEqual(resolve_api_base_url(appdata_dir=appdata, bundled_dir=bundle, development_dir=development), "https://valid.test")


if __name__ == "__main__":
    unittest.main()
