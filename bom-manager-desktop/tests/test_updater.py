"""Offline updater safety/logic tests (no network required)."""
import hashlib
import io
import json
import shutil
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import updater


class UpdaterTests(unittest.TestCase):
    def test_version_order(self):
        self.assertLess(updater.version_tuple("1.9.9"), updater.version_tuple("1.10.0"))
        with self.assertRaises(ValueError):
            updater.version_tuple("1.2")

    def test_only_bom_releases_are_selected(self):
        tag = "bom-v1.2.0"
        base = ("https://github.com/tronza449-dot/"
                "crane-vehicle-engineering-tool-updates/releases/download/" + tag + "/")
        release = {"tag_name": tag, "draft": False, "prerelease": False,
                   "html_url": "https://github.com/example/release",
                   "assets": [
                       {"name": updater.ASSET_NAME, "state": "uploaded",
                        "size": 3, "browser_download_url": base + updater.ASSET_NAME},
                       {"name": updater.CHECKSUM_NAME, "state": "uploaded",
                        "size": 80, "browser_download_url": base + updater.CHECKSUM_NAME}
                   ]}
        irrelevant = dict(release, tag_name="v53.8.50")
        with patch.object(updater, "_read_url",
                          return_value=json.dumps([irrelevant, release]).encode()):
            found = updater.find_update("1.1.0")
            self.assertEqual(found["version"], "1.2.0")
        with patch.object(updater, "_read_url",
                          return_value=json.dumps([irrelevant, release]).encode()):
            self.assertIsNone(updater.find_update("1.2.0"))

    def test_reject_non_repo_asset_urls(self):
        self.assertFalse(updater._trusted_asset_url(
            "https://example.com/malware.exe", "bom-v1.2.0", updater.ASSET_NAME))

    def test_valid_checksum_allows_download(self):
        content = b"abc"
        sha = hashlib.sha256(content).hexdigest()
        item = self._item(len(content))
        with patch.object(updater, "_read_url",
                          return_value=f"{sha}  {updater.ASSET_NAME}".encode()), \
             patch.object(updater, "urlopen", return_value=io.BytesIO(content)):
            installer = updater.download_update(item)
        try:
            self.assertEqual(installer.read_bytes(), content)
        finally:
            shutil.rmtree(installer.parent, ignore_errors=True)

    def test_rejects_checksum_mismatch(self):
        item = self._item(3)
        with patch.object(updater, "_read_url",
                          return_value=(("0" * 64) + "  " + updater.ASSET_NAME).encode()), \
             patch.object(updater, "urlopen", return_value=io.BytesIO(b"abc")):
            with self.assertRaises(updater.UpdateError):
                updater.download_update(item)

    @staticmethod
    def _item(size):
        tag = "bom-v1.2.0"
        url = ("https://github.com/tronza449-dot/crane-vehicle-engineering-tool-updates/"
               "releases/download/" + tag + "/")
        return {"tag": tag, "url": url + updater.ASSET_NAME,
                "sha_url": url + updater.CHECKSUM_NAME, "size": size}


if __name__ == "__main__":
    unittest.main()
