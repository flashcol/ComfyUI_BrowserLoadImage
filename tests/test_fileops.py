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
        self.assertEqual(len([x for x in os.listdir(self.p(".trash")) if not x.startswith(".")]), 1)

    def test_delete_same_name_twice_no_overwrite(self):
        for _ in range(2):
            touch(self.p("a.png"))
            fileops.delete_items(["a.png"])
        self.assertEqual(len([x for x in os.listdir(self.p(".trash")) if not x.startswith(".")]), 2)

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


class TestTrash(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        mock_folder_paths._input_dir = self.root

    def tearDown(self):
        shutil.rmtree(self.root)
        mock_folder_paths._input_dir = None

    def p(self, *parts):
        return os.path.join(self.root, *parts)

    def names(self):
        return [e["name"] for e in fileops.trash_list(fileops.ALL_MEDIA_FORMATS)["entries"]]

    def test_delete_writes_index_and_restore_to_original(self):
        touch(self.p("g", "a.png"))
        fileops.delete_items(["g/a.png"])
        (entry,) = fileops.trash_list(fileops.ALL_MEDIA_FORMATS)["entries"]
        self.assertEqual(entry["orig"], "g/a.png")
        self.assertEqual(entry["kind"], "file")
        shutil.rmtree(self.p("g"))  # 原文件夹被删，还原时应重建
        r = fileops.trash_restore([entry["name"]])
        self.assertEqual(r["restored"][0]["to"], "g/a.png")
        self.assertTrue(os.path.exists(self.p("g", "a.png")))
        self.assertEqual(self.names(), [])

    def test_restore_conflict_gets_suffix(self):
        touch(self.p("a.png"))
        fileops.delete_items(["a.png"])
        touch(self.p("a.png"))
        r = fileops.trash_restore(self.names())
        self.assertEqual(r["restored"][0]["to"], "a (1).png")
        self.assertTrue(os.path.exists(self.p("a.png")))
        self.assertTrue(os.path.exists(self.p("a (1).png")))

    def test_restore_folder(self):
        touch(self.p("g", "a.png"))
        fileops.delete_items(["g"])
        (entry,) = fileops.trash_list(fileops.ALL_MEDIA_FORMATS)["entries"]
        self.assertEqual((entry["kind"], entry["orig"], entry["count"]), ("folder", "g", 1))
        fileops.trash_restore([entry["name"]])
        self.assertTrue(os.path.exists(self.p("g", "a.png")))

    def test_restore_without_index_goes_to_root(self):
        os.makedirs(self.p(".trash"))
        touch(self.p(".trash", "20260101-000000_old.png"))
        r = fileops.trash_restore(["20260101-000000_old.png"])
        self.assertEqual(r["restored"][0]["to"], "old.png")

    def test_corrupt_index_is_tolerated(self):
        touch(self.p("a.png"))
        fileops.delete_items(["a.png"])
        with open(self.p(".trash", ".index.json"), "w") as f:
            f.write("{not json")
        r = fileops.trash_restore(self.names())
        self.assertEqual(len(r["restored"]), 1)
        self.assertEqual(len(os.listdir(self.root)) - 1, 1)  # a.png + .trash

    def test_tampered_index_cannot_escape(self):
        touch(self.p("a.png"))
        fileops.delete_items(["a.png"])
        idx = self.p(".trash", ".index.json")
        name = self.names()[0]
        import json
        with open(idx, "w") as f:
            json.dump({name: {"orig": "../../evil.png", "kind": "file", "at": 1}}, f)
        r = fileops.trash_restore([name])
        self.assertEqual(len(r["restored"]), 1)
        self.assertFalse(os.path.exists(os.path.join(self.root, "..", "..", "evil.png")))
        self.assertTrue(os.path.exists(self.p("a.png")))

    def test_trash_names_reject_traversal(self):
        touch(self.p("secret.png"))
        for bad in ["../secret.png", "..", ".index.json", "a/b", "a\\b", "", "C:x"]:
            r = fileops.trash_restore([bad])
            self.assertEqual(r["restored"], [], msg=bad)
            r = fileops.trash_purge([bad])
            self.assertEqual(r["purged"], [], msg=bad)
        self.assertTrue(os.path.exists(self.p("secret.png")))

    def test_purge_selected_and_all(self):
        for n in ("a.png", "b.png", "c.png"):
            touch(self.p(n))
        fileops.delete_items(["a.png", "b.png", "c.png"])
        first = self.names()[0]
        self.assertEqual(fileops.trash_purge([first])["purged"], [first])
        self.assertEqual(len(self.names()), 2)
        fileops.trash_purge(None)
        self.assertEqual(self.names(), [])
        self.assertTrue(os.path.exists(self.p(".trash")))

    def test_list_filters_by_type_and_totals(self):
        touch(self.p("a.png"))
        touch(self.p("v.mp4"))
        fileops.delete_items(["a.png", "v.mp4"])
        r = fileops.trash_list(fileops.SUPPORTED_IMAGE_FORMATS)
        self.assertEqual(len(r["entries"]), 1)
        self.assertEqual(r["total_count"], 2)
        self.assertEqual(r["total_size"], 2)

    def test_list_empty_when_no_trash(self):
        r = fileops.trash_list(fileops.ALL_MEDIA_FORMATS)
        self.assertEqual(r["entries"], [])


if __name__ == "__main__":
    unittest.main()
