"""
ComfyUI Browser Load Image Plugin
Enhanced Load Image node with browser interface for selecting images from input folder
"""

from .nodes.browser_load_image import BrowserLoadImage

# ComfyUI 插件必需的映射
NODE_CLASS_MAPPINGS = {
    "BrowserLoadImage": BrowserLoadImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BrowserLoadImage": "Browser Load Image",
}

# 视频节点依赖 cv2 / comfy_api，导入失败时优雅降级
try:
    from .nodes.browser_load_video import BrowserLoadVideoToImage
    NODE_CLASS_MAPPINGS["BrowserLoadVideoToImage"] = BrowserLoadVideoToImage
    NODE_DISPLAY_NAME_MAPPINGS["BrowserLoadVideoToImage"] = "Browser Load Video to Image"
except ImportError:
    pass

try:
    from .nodes.browser_load_video_standard import BrowserLoadVideoStandard
    NODE_CLASS_MAPPINGS["BrowserLoadVideoStandard"] = BrowserLoadVideoStandard
    NODE_DISPLAY_NAME_MAPPINGS["BrowserLoadVideoStandard"] = "Browser Load Video"
except ImportError:
    pass

# 文件管理 HTTP 接口（删除/移动/重命名/新建文件夹），需要 ComfyUI 的 PromptServer
try:
    from server import PromptServer
    from .api.routes import register_routes
    register_routes(PromptServer.instance.routes)
except Exception as e:
    print(f"[BrowserLoadImage] file management API disabled: {e}")

# Web 目录设置
WEB_DIRECTORY = "web/js"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']