"""
ComfyUI Browser Load Image Plugin
Enhanced Load Image node with browser interface for selecting images from input folder
"""

# 从nodes模块导入所有节点
from .nodes.browser_load_image import BrowserLoadImage
from .nodes.browser_load_video import BrowserLoadVideoToImage
from .nodes.browser_load_video_standard import BrowserLoadVideoStandard

# ComfyUI插件必需的映射
NODE_CLASS_MAPPINGS = {
    "BrowserLoadImage": BrowserLoadImage,
    "BrowserLoadVideoToImage": BrowserLoadVideoToImage,
    "BrowserLoadVideoStandard": BrowserLoadVideoStandard,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BrowserLoadImage": "Browser Load Image",
    "BrowserLoadVideoToImage": "Browser Load Video to Image",
    "BrowserLoadVideoStandard": "Browser Load Video",
}

# Web目录设置 - 直接指向js目录
WEB_DIRECTORY = "web/js"

# 导出所有必要的符号
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']