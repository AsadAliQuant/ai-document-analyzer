import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import main
import main_window


class ResourcePathTests(unittest.TestCase):
    def test_main_resolves_source_resources_from_module_directory(self):
        with patch.object(sys, "frozen", False, create=True):
            path = main._asset_path("styles.qss")

        self.assertEqual(path, str(Path(main.__file__).resolve().parent / "styles.qss"))

    def test_main_resolves_frozen_resources_from_meipass(self):
        bundle_dir = os.path.join("C:\\", "synthetic-bundle")
        with patch.object(sys, "frozen", True, create=True), patch.object(
            sys,
            "_MEIPASS",
            bundle_dir,
            create=True,
        ):
            path = main._asset_path("assets", "app-icon-logo.jpeg")

        self.assertEqual(path, os.path.join(bundle_dir, "assets", "app-icon-logo.jpeg"))

    def test_main_window_resolves_source_resources_from_module_directory(self):
        with patch.object(sys, "frozen", False, create=True):
            path = main_window._asset_path("assets", "logo.png")

        self.assertEqual(path, str(Path(main_window.__file__).resolve().parent / "assets" / "logo.png"))

    def test_main_window_resolves_frozen_resources_from_meipass(self):
        bundle_dir = os.path.join("C:\\", "synthetic-bundle")
        with patch.object(sys, "frozen", True, create=True), patch.object(
            sys,
            "_MEIPASS",
            bundle_dir,
            create=True,
        ):
            path = main_window._asset_path("assets", "logo.png")

        self.assertEqual(path, os.path.join(bundle_dir, "assets", "logo.png"))


if __name__ == "__main__":
    unittest.main()
