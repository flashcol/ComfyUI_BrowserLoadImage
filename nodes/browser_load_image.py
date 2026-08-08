"""
Browser Load Image Node - 带浏览器界面的增强型图片加载节点
"""

import os
import torch
from PIL import Image, ImageOps
import numpy as np

from .utils import (
    list_media_files, resolve_media_path, is_changed, validate_input,
    SUPPORTED_IMAGE_FORMATS,
)


class BrowserLoadImage:
    """完全兼容 ComfyUI 原生 Load Image 节点标准的增强型图片加载节点"""

    @classmethod
    def INPUT_TYPES(cls):
        images = list_media_files(SUPPORTED_IMAGE_FORMATS)
        if images:
            return {
                "required": {
                    "image": (images, {"default": images[0], "image_upload": True}),
                }
            }
        return {
            "required": {
                "image": ([],),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "load_image"
    CATEGORY = "image"
    OUTPUT_NODE = False

    @classmethod
    def IS_CHANGED(cls, image):
        return is_changed(image)

    @classmethod
    def VALIDATE_INPUTS(cls, image):
        return validate_input(image)

    def load_image(self, image):
        """加载图片并返回 IMAGE + MASK 张量"""
        if not image:
            return (torch.zeros((1, 64, 64, 3), dtype=torch.float32),
                    torch.zeros((1, 64, 64), dtype=torch.float32))

        image_path = resolve_media_path(image)

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image}")

        i = Image.open(image_path)
        i = ImageOps.exif_transpose(i)
        image_data = i.convert("RGB")
        image_data = np.array(image_data).astype(np.float32) / 255.0
        image_tensor = torch.from_numpy(image_data)[None,]

        if 'A' in i.getbands():
            mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
            mask = 1. - torch.from_numpy(mask)[None,]
        else:
            mask = torch.zeros((1, image_tensor.shape[1], image_tensor.shape[2]),
                               dtype=torch.float32)

        return (image_tensor, mask)