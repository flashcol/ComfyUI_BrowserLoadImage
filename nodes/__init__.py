"""
Custom nodes for Browser Load Image plugin
"""

from .browser_load_image import BrowserLoadImage

try:
    from .browser_load_video import BrowserLoadVideoToImage
except ImportError:
    BrowserLoadVideoToImage = None

try:
    from .browser_load_video_standard import BrowserLoadVideoStandard
except ImportError:
    BrowserLoadVideoStandard = None

NODE_CLASS_MAPPINGS = {
    "BrowserLoadImage": BrowserLoadImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BrowserLoadImage": "Browser Load Image",
}

if BrowserLoadVideoToImage is not None:
    NODE_CLASS_MAPPINGS["BrowserLoadVideoToImage"] = BrowserLoadVideoToImage
    NODE_DISPLAY_NAME_MAPPINGS["BrowserLoadVideoToImage"] = "Browser Load Video to Image"

if BrowserLoadVideoStandard is not None:
    NODE_CLASS_MAPPINGS["BrowserLoadVideoStandard"] = BrowserLoadVideoStandard
    NODE_DISPLAY_NAME_MAPPINGS["BrowserLoadVideoStandard"] = "Browser Load Video"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']