"""
Tests for Browser Load Image nodes
对齐当前真实 API
"""

import unittest
import tempfile
import os
import shutil
from pathlib import Path
import sys
import types

# 将插件目录加入 Python 路径
plugin_dir = Path(__file__).parent.parent
sys.path.insert(0, str(plugin_dir))

# 在导入节点之前 mock folder_paths
mock_folder_paths = types.ModuleType("folder_paths")
mock_folder_paths._input_dir = None


def _get_input_directory():
    return mock_folder_paths._input_dir


def _get_annotated_filepath(filename):
    input_dir = mock_folder_paths._input_dir
    if input_dir:
        return os.path.join(input_dir, filename)
    raise ValueError("No input directory set")


mock_folder_paths.get_input_directory = _get_input_directory
mock_folder_paths.get_annotated_filepath = _get_annotated_filepath
sys.modules["folder_paths"] = mock_folder_paths

from nodes.utils import (
    list_media_files,
    resolve_media_path,
    is_changed,
    validate_input,
    SUPPORTED_IMAGE_FORMATS,
    SUPPORTED_VIDEO_FORMATS,
)
from nodes.browser_load_image import BrowserLoadImage


# ===== 测试常量 =====

class TestConstants(unittest.TestCase):
    """测试格式常量定义"""

    def test_image_formats_is_set(self):
        self.assertIsInstance(SUPPORTED_IMAGE_FORMATS, set)

    def test_video_formats_is_set(self):
        self.assertIsInstance(SUPPORTED_VIDEO_FORMATS, set)

    def test_image_formats_contains_common(self):
        for fmt in [".jpg", ".jpeg", ".png", ".webp"]:
            self.assertIn(fmt, SUPPORTED_IMAGE_FORMATS)

    def test_video_formats_contains_common(self):
        for fmt in [".mp4", ".avi", ".mov", ".mkv"]:
            self.assertIn(fmt, SUPPORTED_VIDEO_FORMATS)


# ===== 测试工具函数 =====

class TestUtils(unittest.TestCase):
    """测试 nodes/utils.py 中的公共工具函数"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        mock_folder_paths._input_dir = self.temp_dir

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        mock_folder_paths._input_dir = None

    def test_list_media_files_empty_dir(self):
        result = list_media_files(SUPPORTED_IMAGE_FORMATS)
        self.assertEqual(result, [])

    def test_list_media_files_filters_correctly(self):
        from PIL import Image

        img = Image.new("RGB", (10, 10), "red")
        img.save(os.path.join(self.temp_dir, "test.png"))
        # 非图片文件应被过滤
        with open(os.path.join(self.temp_dir, "readme.txt"), "w") as f:
            f.write("hello")

        result = list_media_files(SUPPORTED_IMAGE_FORMATS)
        self.assertEqual(result, ["test.png"])

    def test_list_media_files_sorted(self):
        from PIL import Image

        img = Image.new("RGB", (10, 10), "red")
        img.save(os.path.join(self.temp_dir, "b.png"))
        img.save(os.path.join(self.temp_dir, "a.png"))

        result = list_media_files(SUPPORTED_IMAGE_FORMATS)
        self.assertEqual(result, ["a.png", "b.png"])

    def test_list_media_files_ignores_subdirs(self):
        from PIL import Image

        img = Image.new("RGB", (10, 10), "red")
        img.save(os.path.join(self.temp_dir, "top.png"))
        sub = os.path.join(self.temp_dir, "subdir")
        os.makedirs(sub)
        img.save(os.path.join(sub, "nested.png"))

        result = list_media_files(SUPPORTED_IMAGE_FORMATS)
        self.assertEqual(result, ["top.png"])

    def test_resolve_media_path(self):
        path = resolve_media_path("test.png")
        self.assertEqual(path, os.path.join(self.temp_dir, "test.png"))

    def test_resolve_media_path_empty_raises(self):
        with self.assertRaises(ValueError):
            resolve_media_path("")

    def test_resolve_media_path_none_raises(self):
        with self.assertRaises(ValueError):
            resolve_media_path(None)

    def test_validate_input_empty_is_ok(self):
        self.assertTrue(validate_input(""))

    def test_validate_input_none_is_ok(self):
        self.assertTrue(validate_input(None))

    def test_validate_input_existing_file(self):
        from PIL import Image

        img = Image.new("RGB", (10, 10), "red")
        img.save(os.path.join(self.temp_dir, "test.png"))
        self.assertTrue(validate_input("test.png"))

    def test_validate_input_nonexistent(self):
        self.assertFalse(validate_input("nonexistent.png"))

    def test_is_changed_existing_file(self):
        from PIL import Image

        img = Image.new("RGB", (10, 10), "red")
        img.save(os.path.join(self.temp_dir, "test.png"))
        result = is_changed("test.png")
        self.assertIsInstance(result, float)

    def test_is_changed_nonexistent(self):
        self.assertFalse(is_changed("nonexistent.png"))

    def test_is_changed_empty(self):
        self.assertFalse(is_changed(""))


# ===== 测试 BrowserLoadImage 节点 =====

class TestBrowserLoadImage(unittest.TestCase):
    """测试 BrowserLoadImage 节点"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        mock_folder_paths._input_dir = self.temp_dir
        self.node = BrowserLoadImage()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        mock_folder_paths._input_dir = None

    def test_return_types(self):
        self.assertEqual(BrowserLoadImage.RETURN_TYPES, ("IMAGE", "MASK"))
        self.assertEqual(BrowserLoadImage.RETURN_NAMES, ("image", "mask"))

    def test_category(self):
        self.assertEqual(BrowserLoadImage.CATEGORY, "image")

    def test_function_name(self):
        self.assertEqual(BrowserLoadImage.FUNCTION, "load_image")

    def test_input_types_has_required_image(self):
        input_types = BrowserLoadImage.INPUT_TYPES()
        self.assertIn("required", input_types)
        self.assertIn("image", input_types["required"])

    def test_input_types_with_images(self):
        from PIL import Image

        img = Image.new("RGB", (10, 10), "red")
        img.save(os.path.join(self.temp_dir, "photo.jpg"))

        input_types = BrowserLoadImage.INPUT_TYPES()
        image_config = input_types["required"]["image"]
        # 第一个元素是文件名列表
        self.assertIn("photo.jpg", image_config[0])

    def test_load_image_empty_returns_default(self):
        import torch

        image, mask = self.node.load_image("")
        self.assertEqual(image.shape, (1, 64, 64, 3))
        self.assertEqual(mask.shape, (1, 64, 64))
        self.assertEqual(image.dtype, torch.float32)

    def test_load_image_valid_rgb(self):
        from PIL import Image as PILImage
        import torch

        img = PILImage.new("RGB", (100, 80), "blue")
        img.save(os.path.join(self.temp_dir, "valid.png"))

        image, mask = self.node.load_image("valid.png")

        self.assertIsInstance(image, torch.Tensor)
        self.assertIsInstance(mask, torch.Tensor)
        self.assertEqual(image.shape, (1, 80, 100, 3))
        self.assertEqual(mask.shape, (1, 80, 100))
        # RGB 值范围 [0, 1]
        self.assertTrue((image >= 0).all() and (image <= 1).all())

    def test_load_image_with_alpha(self):
        from PIL import Image as PILImage

        img = PILImage.new("RGBA", (50, 50), (255, 0, 0, 128))
        img.save(os.path.join(self.temp_dir, "alpha.png"))

        image, mask = self.node.load_image("alpha.png")
        self.assertEqual(image.shape, (1, 50, 50, 3))
        self.assertEqual(mask.shape, (1, 50, 50))

    def test_load_image_not_found_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.node.load_image("nonexistent.png")

    def test_is_changed_delegates(self):
        from PIL import Image as PILImage

        img = PILImage.new("RGB", (10, 10), "red")
        img.save(os.path.join(self.temp_dir, "test.png"))

        result = BrowserLoadImage.IS_CHANGED("test.png")
        self.assertIsInstance(result, float)

    def test_validate_inputs_delegates(self):
        self.assertTrue(BrowserLoadImage.VALIDATE_INPUTS(""))
        self.assertFalse(BrowserLoadImage.VALIDATE_INPUTS("no_such_file.png"))


if __name__ == "__main__":
    unittest.main()