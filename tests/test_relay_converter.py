# -*- coding: utf-8 -*-
"""relay-converter 离线测试：不发网络请求"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import relay_converter as rc  # noqa: E402

CTX = {"root": "https://api.example.com", "full": "https://api.example.com/v1",
       "key": "sk-test123456", "model": "gpt-4o-mini"}


class SplitBaseTest(unittest.TestCase):
    def test_strip_v1(self):
        self.assertEqual(rc.split_base("https://a.com/v1"),
                         ("https://a.com", "https://a.com/v1"))

    def test_add_v1(self):
        self.assertEqual(rc.split_base("https://a.com"),
                         ("https://a.com", "https://a.com/v1"))

    def test_trailing_slash(self):
        self.assertEqual(rc.split_base("https://a.com/v1/"),
                         ("https://a.com", "https://a.com/v1"))

    def test_nested_path(self):
        self.assertEqual(rc.split_base("https://a.com/api/v1"),
                         ("https://a.com/api", "https://a.com/api/v1"))


class TargetTest(unittest.TestCase):
    def test_all_targets_render(self):
        for tid, name, cat, kind, fn in rc.TARGETS:
            with self.subTest(target=tid):
                fname, text = fn(CTX)
                self.assertIsInstance(text, str)
                self.assertGreater(len(text), 10)
                self.assertIn("sk-test123456", text)

    def test_cherry_has_no_v1(self):
        _, text = rc.t_cherry(CTX)
        self.assertIn("https://api.example.com ", text)
        self.assertIn("不要带 /v1", text)

    def test_env_uses_full_url(self):
        _, text = rc.t_env(CTX)
        self.assertIn("https://api.example.com/v1", text)

    def test_targets_unique_ids(self):
        ids = [t[0] for t in rc.TARGETS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_cli_list(self):
        self.assertEqual(rc.main(["--list"]), 0)

    def test_cli_rejects_unknown_target(self):
        with self.assertRaises(SystemExit):
            rc.main(["-u", "https://a.com", "-k", "sk-x", "-t", "nope"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
