"""
Browser Load Video Standard Node - 标准视频加载节点，输出 VIDEO 类型
"""

import os

from .utils import resolve_media_path, is_changed, validate_input, SUPPORTED_VIDEO_FORMATS

try:
    import folder_paths
except ImportError:
    folder_paths = None

# 导入 ComfyUI 标准类型
try:
    from comfy_api.latest import InputImpl
except ImportError:
    try:
        from comfy import InputImpl
    except ImportError:
        InputImpl = None


class BrowserLoadVideoStandard:
    """标准视频加载节点，输出 VIDEO 类型"""

    @classmethod
    def INPUT_TYPES(cls):
        videos = []
        if folder_paths:
            input_dir = folder_paths.get_input_directory()
            if input_dir and os.path.exists(input_dir):
                files = [
                    f for f in os.listdir(input_dir)
                    if os.path.isfile(os.path.join(input_dir, f))
                ]
                # 优先使用 ComfyUI 原生 MIME 类型过滤
                if hasattr(folder_paths, 'filter_files_content_types'):
                    videos = sorted(folder_paths.filter_files_content_types(files, ["video"]))
                else:
                    videos = sorted(
                        f for f in files
                        if os.path.splitext(f)[1].lower() in SUPPORTED_VIDEO_FORMATS
                    )

        return {
            "required": {
                "video": (videos, {"video_upload": True}),
            },
        }

    CATEGORY = "video"
    RETURN_TYPES = ("VIDEO",)
    RETURN_NAMES = ("video",)
    FUNCTION = "load_video"

    def load_video(self, video):
        if not video:
            raise ValueError("No video file selected")

        video_path = resolve_media_path(video)

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video}")

        if InputImpl is not None:
            return (InputImpl.VideoFromFile(video_path),)

        return ({"video_path": video_path, "type": "VIDEO"},)

    @classmethod
    def IS_CHANGED(cls, video):
        return is_changed(video)

    @classmethod
    def VALIDATE_INPUTS(cls, video):
        return validate_input(video)