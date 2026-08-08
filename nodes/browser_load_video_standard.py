"""
Browser Load Video Standard Node - 标准视频加载节点
"""

import os
import glob
try:
    import folder_paths
except ImportError:
    folder_paths = None

# 尝试导入ComfyUI的标准类型定义
try:
    from comfy_api.latest import InputImpl
    from comfy.comfy_types import IO
except ImportError:
    # 如果新API不可用，使用兼容性导入
    try:
        from comfy import InputImpl
        from comfy.comfy_types import IO
    except ImportError:
        # 如果都不可用，创建兼容性类
        class IO:
            VIDEO = "VIDEO"
        
        class InputImpl:
            @staticmethod
            def VideoFromFile(path):
                return {"video_path": path, "type": "VIDEO"}

class BrowserLoadVideoStandard:
    """
    标准视频加载节点，输出VIDEO类型
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        videos = []
        if folder_paths:
            try:
                input_dir = folder_paths.get_input_directory()
                if input_dir and os.path.exists(input_dir):
                    files = [
                        f
                        for f in os.listdir(input_dir)
                        if os.path.isfile(os.path.join(input_dir, f))
                    ]
                    # 使用ComfyUI的文件过滤功能
                    if hasattr(folder_paths, 'filter_files_content_types'):
                        videos = folder_paths.filter_files_content_types(files, ["video"])
                    else:
                        # 如果没有过滤功能，手动过滤视频格式
                        supported_formats = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}
                        videos = [f for f in files if os.path.splitext(f)[1].lower() in supported_formats]
                    videos.sort()
            except:
                pass
        
        return {
            "required": {
                "video": (sorted(videos), {"video_upload": True}),
            },
        }

    CATEGORY = "video"
    RETURN_TYPES = ("VIDEO",)
    RETURN_NAMES = ("video",)
    FUNCTION = "load_video"

    def load_video(self, video):
        if not video:
            raise ValueError("No video file selected")
        
        # 获取视频完整路径
        if folder_paths:
            try:
                video_path = folder_paths.get_annotated_filepath(video)
            except:
                # 如果无法获取路径，尝试直接构造
                input_dir = folder_paths.get_input_directory()
                video_path = os.path.join(input_dir, video)
        else:
            video_path = video
        
        # 检查文件是否存在
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video}")
        
        # 返回视频对象
        try:
            video_obj = InputImpl.VideoFromFile(video_path)
            return (video_obj,)
        except Exception as e:
            # 如果InputImpl不可用，返回基本路径信息
            return ({"video_path": video_path, "type": "VIDEO"},)

    @classmethod
    def IS_CHANGED(cls, video):
        if not video:
            return False
        
        # 获取视频完整路径
        if folder_paths:
            try:
                video_path = folder_paths.get_annotated_filepath(video)
            except:
                return False
        else:
            return False
        
        # 检查文件是否存在和修改时间
        if not os.path.exists(video_path):
            return False
        
        # 使用修改时间作为变化检测
        mod_time = os.path.getmtime(video_path)
        return mod_time

    @classmethod
    def VALIDATE_INPUTS(cls, video):
        if not video:
            return True  # 允许空输入
        
        # 检查文件是否存在
        if folder_paths:
            try:
                video_path = folder_paths.get_annotated_filepath(video)
                return os.path.exists(video_path)
            except:
                return False
        else:
            return os.path.exists(video) if video else False

# 注册节点
NODE_CLASS_MAPPINGS = {
    "BrowserLoadVideoStandard": BrowserLoadVideoStandard,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BrowserLoadVideoStandard": "Browser Load Video",
}