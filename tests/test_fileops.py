"""Tests for nodes/fileops.py"""

import os
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path

plugin_dir = Path(__file__).parent.parent
sys.path.insert(0, str(plugin_dir))

# 复用 test_nodes 中的 folder_paths mock，避免两个测试模块各自 mock 导致 nodes.utils 绑定错误对象
sys.path.insert(0, str(Path(__file__).parent))
from test_nodes import mock_folder_paths  # noqa: E402

from nodes import fileops
from nodes.fileops import FileOpError


def touch(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(b"x")


class TestFileOps(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        mock_folder_paths._input_dir = self.root

    def tearDown(self):
        shutil.rmtree(self.root)
        mock_folder_paths._input_dir = None

    def p(self, *parts):
        return os.path.join(self.root, *parts)

    # ----- safe_resolve -----
    def test_safe_resolve_rejects_escape(self):
        for bad in ["../x.png", "a/../../x.png", "/etc/x.png", "C:/x.png",
                    "C:\\x.png", "a/b/c.png", ".trash/a.png", "", "a//b.png"]:
            with self.assertRaises(FileOpError, msg=bad):
                fileops.safe_resolve(bad, "file")

    def test_safe_resolve_folder_one_level_only(self):
        with self.assertRaises(FileOpError):
            fileops.safe_resolve("a/b", "folder")
        self.assertEqual(fileops.safe_resolve("a", "folder")[1], "a")

    def test_safe_resolve_backslash_normalized(self):
        self.assertEqual(fileops.safe_resolve("a\\b.png", "file")[1], "a/b.png")

    # ----- delete -----
    def test_delete_file_goes_to_trash(self):
        touch(self.p("a.png"))
        r = fileops.delete_items(["a.png"])
        self.assertEqual(r["deleted"], ["a.png"])
        self.assertFalse(os.path.exists(self.p("a.png")))
        self.assertEqual(len(os.listdir(self.p(".trash"))), 1)

    def test_delete_same_name_twice_no_overwrite(self):
        for _ in range(2):
            touch(self.p("a.png"))
            fileops.delete_items(["a.png"])
        self.assertEqual(len(os.listdir(self.p(".trash"))), 2)

    def test_delete_folder_with_contents(self):
        touch(self.p("g", "a.png"))
        touch(self.p("g", "note.txt"))
        r = fileops.delete_items(["g"])
        self.assertEqual(r["deleted"], ["g"])
        self.assertFalse(os.path.exists(self.p("g")))

    def test_delete_rejects_non_media_and_escape(self):
        touch(self.p("a.txt"))
        r = fileops.delete_items(["a.txt", "../evil.png"])
        self.assertEqual(r["deleted"], [])
        self.assertEqual(len(r["failed"]), 2)
        self.assertTrue(os.path.exists(self.p("a.txt")))

    def test_delete_missing_is_ok(self):
        self.assertEqual(fileops.delete_items(["nope.png"])["deleted"], ["nope.png"])

    # ----- mkdir / move -----
    def test_make_folder(self):
        self.assertEqual(fileops.make_folder("g"), "g")
        self.assertTrue(os.path.isdir(self.p("g")))
        with self.assertRaises(FileOpError):
            fileops.make_folder("g")
        with self.assertRaises(FileOpError):
            fileops.make_folder("a/b")
        with self.assertRaises(FileOpError):
            fileops.make_folder("..")

    def test_move_and_conflict_suffix(self):
        touch(self.p("a.png"))
        touch(self.p("g", "a.png"))
        r = fileops.move_files(["a.png"], "g")
        self.assertEqual(r["moved"], [{"from": "a.png", "to": "g/a (1).png"}])
        self.assertTrue(os.path.exists(self.p("g", "a (1).png")))
        self.assertTrue(os.path.exists(self.p("g", "a.png")))

    def test_move_back_to_root(self):
        touch(self.p("g", "a.png"))
        r = fileops.move_files(["g/a.png"], "")
        self.assertEqual(r["moved"], [{"from": "g/a.png", "to": "a.png"}])

    def test_move_to_missing_folder(self):
        touch(self.p("a.png"))
        with self.assertRaises(FileOpError):
            fileops.move_files(["a.png"], "nope")

    # ----- rename -----
    def test_rename_file(self):
        touch(self.p("g", "a.png"))
        self.assertEqual(fileops.rename_item("g/a.png", "b.png"), "g/b.png")
        self.assertTrue(os.path.exists(self.p("g", "b.png")))

    def test_rename_file_extension_locked(self):
        touch(self.p("a.png"))
        with self.assertRaises(FileOpError):
            fileops.rename_item("a.png", "a.jpg")

    def test_rename_target_exists(self):
        touch(self.p("a.png"))
        touch(self.p("b.png"))
        with self.assertRaises(FileOpError):
            fileops.rename_item("a.png", "b.png")

    def test_rename_case_only(self):
        touch(self.p("a.png"))
        self.assertEqual(fileops.rename_item("a.png", "A.png"), "A.png")
        self.assertIn("A.png", os.listdir(self.root))

    def test_rename_folder(self):
        touch(self.p("g", "a.png"))
        self.assertEqual(fileops.rename_item("g", "h"), "h")
        self.assertTrue(os.path.exists(self.p("h", "a.png")))

    def test_rename_illegal_names(self):
        touch(self.p("a.png"))
        for bad in ["b/c.png", "b\\c.png", "con.png", "b?.png", " b.png",
                    "b.png.", ".b.png", "", "..png"]:
            with self.assertRaises(FileOpError, msg=bad):
                fileops.rename_item("a.png", bad)

    def test_list_folders_skips_hidden(self):
        os.makedirs(self.p("g"))
        os.makedirs(self.p(".trash"))
        touch(self.p("a.png"))
        self.assertEqual(fileops.list_folders(), ["g"])


if __name__ == "__main__":
    unittest.main()
