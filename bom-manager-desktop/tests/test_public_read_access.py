"""Security regression tests for the public-viewer, per-user-editor design.

No real credential, external network, or GitHub login is used.
"""
import io
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import bom_qt


class PublicReadAccessTests(unittest.TestCase):
    def test_public_read_works_without_token(self):
        with patch.object(bom_qt, "urlopen", return_value=io.BytesIO(b'{"sha":"abc"}')) as fake:
            result = bom_qt.github_api("GET", token=None)
        self.assertEqual(result["sha"], "abc")
        request = fake.call_args.args[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertIsNone(request.get_header("Authorization"))

    def test_shared_pat_is_never_needed_to_read_public_bom(self):
        url = bom_qt.BOM_URL
        revoked = HTTPError(url, 401, "Unauthorized", {}, None)
        with patch.object(bom_qt, "urlopen", side_effect=[
            revoked, io.BytesIO(b'{"sha":"public"}')
        ]) as fake:
            result = bom_qt.github_api("GET", token="TEST_REVOKED_TOKEN")
        self.assertEqual(result["sha"], "public")
        self.assertEqual(fake.call_count, 2)
        first = fake.call_args_list[0].args[0]
        second = fake.call_args_list[1].args[0]
        self.assertEqual(first.get_header("Authorization"), "Bearer TEST_REVOKED_TOKEN")
        self.assertIsNone(second.get_header("Authorization"))

    def test_public_users_cannot_write_without_own_credential(self):
        with patch.object(bom_qt, "urlopen") as fake:
            with self.assertRaises(PermissionError):
                bom_qt.github_api("PUT", payload={"content": "test"}, token=None)
        fake.assert_not_called()

    def test_write_with_authorized_user_has_token_only_in_request_header(self):
        with patch.object(bom_qt, "urlopen", return_value=io.BytesIO(b'{"ok":true}')) as fake:
            result = bom_qt.github_api("PUT", payload={"test": 1}, token="TEST_EDITOR_CREDENTIAL")
        self.assertTrue(result["ok"])
        request = fake.call_args.args[0]
        self.assertEqual(request.get_method(), "PUT")
        self.assertEqual(request.get_header("Authorization"), "Bearer TEST_EDITOR_CREDENTIAL")
        self.assertNotIn(b"TEST_EDITOR_CREDENTIAL", request.data)


if __name__ == "__main__":
    unittest.main()
