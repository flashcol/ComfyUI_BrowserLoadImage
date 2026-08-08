"""
Browser Load Video To Image Node - 将视频转换为图片序列
"""

import os
import torch
from PIL import Image, ImageOps
import numpy as np
import cv2

try:
    import folder_paths
except ImportError:
    folder_paths = None

class BrowserLoadVideoToImage:
    """
    将视频转换为图片序列的Browser Load Video To Image节点
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # 获取input目录中的视频列表
        videos = []
        if folder_paths:
            try:
                input_dir = folder_paths.get_input_directory()
                if input_dir and os.path.exists(input_dir):
                    # 扫描支持的视频格式
                    supported_formats = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}
                    for file in os.listdir(input_dir):
                        if os.path.isfile(os.path.join(input_dir, file)):
                            ext = os.path.splitext(file)[1].lower()
                            if ext in supported_formats:
                                videos.append(file)
                    videos.sort()
            except:
                pass
        
        if videos:
            return {
                "required": {
                    "video": (videos, {"default": videos[0], "video_upload": True}),
                    "force_rate": ("INT", {"default": 0, "min": 0, "max": 60, "step": 1}),
                    "force_size": ("INT", {"default": 0, "min": 0, "max": 8192, "step": 1}),
                    "frame_load_cap": ("INT", {"default": 0, "min": 0, "max": 100000, "step": 1}),
                }
            }
        else:
            # 如果没有视频，使用空列表
            return {
                "required": {
                    "video": ([],),
                    "force_rate": ("INT", {"default": 0, "min": 0, "max": 60, "step": 1}),
                    "force_size": ("INT", {"default": 0, "min": 0, "max": 8192, "step": 1}),
                    "frame_load_cap": ("INT", {"default": 0, "min": 0, "max": 100000, "step": 1}),
                }
            }
    
    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("images", "frame_count", "fps")
    FUNCTION = "load_video"
    CATEGORY = "image"
    OUTPUT_NODE = False
    
    @classmethod
    def IS_CHANGED(cls, video, force_rate, force_size, frame_load_cap):
        if not video:
            return False
        
        # 获取视频完整路径
        if folder_paths:
            try:
                video_path = folder_paths.get_annotated_filepath(video)
            except:
                # 如果无法获取路径，返回False
                return False
        else:
            return False
        
        # 检查文件是否存在和修改时间
        if not os.path.exists(video_path):
            return False
        
        mtime = os.path.getmtime(video_path)
        return mtime
    
    @classmethod
    def VALIDATE_INPUTS(cls, video, force_rate, force_size, frame_load_cap):
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
            return False
    
    def load_video(self, video, force_rate=0, force_size=0, frame_load_cap=0):
        """将视频转换为图片序列的方法"""
        if not video:
            # 如果没有选择视频，返回默认值
            return (torch.zeros((1, 64, 64, 3), dtype=torch.float32), 1, 30)
        
        # 获取视频完整路径
        if folder_paths:
            try:
                video_path = folder_paths.get_annotated_filepath(video)
            except:
                # 如果无法获取路径，尝试直接构造
                input_dir = folder_paths.get_input_directory()
                video_path = os.path.join(input_dir, video)
        else:
            # 如果folder_paths不可用，使用相对路径
            video_path = video
        
        # 检查文件是否存在
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video}")
        
        try:
            # 使用OpenCV加载视频
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {video}")
            
            # 获取视频信息
            original_fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # 计算目标尺寸
            if force_size > 0:
                # 保持宽高比
                aspect_ratio = original_width / original_height
                if original_width > original_height:
                    target_width = force_size
                    target_height = int(force_size / aspect_ratio)
                else:
                    target_height = force_size
                    target_width = int(force_size * aspect_ratio)
            else:
                target_width = original_width
                target_height = original_height
            
            # 计算目标帧率
            target_fps = force_rate if force_rate > 0 else original_fps
            
            # 计算帧间隔
            frame_interval = max(1, int(original_fps / target_fps))
            
            # 计算要加载的帧数
            frames_to_load = min(frame_count, frame_load_cap) if frame_load_cap > 0 else frame_count
            
            # 读取帧
            frames = []
            frame_idx = 0
            loaded_frames = 0
            
            while loaded_frames < frames_to_load:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # 调整尺寸
                if force_size > 0:
                    frame = cv2.resize(frame, (target_width, target_height))
                
                # 转换颜色空间 BGR -> RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # 归一化到[0,1]
                frame = frame.astype(np.float32) / 255.0
                
                frames.append(frame)
                loaded_frames += 1
                frame_idx += frame_interval
            
            cap.release()
            
            if not frames:
                raise ValueError(f"Could not read any frames from video: {video}")
            
            # 转换为torch张量 [F, H, W, C]
            video_tensor = torch.from_numpy(np.array(frames))
            
            return (video_tensor, len(frames), target_fps)
            
        except Exception as e:
            print(f"Error loading video {video_path}: {e}")
            # 返回一个1帧的空视频
            empty_video = torch.zeros((1, 1, 1, 3), dtype=torch.float32)
            return (empty_video, 1, 30)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "BrowserLoadVideoToImage": BrowserLoadVideoToImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BrowserLoadVideoToImage": "Browser Load Video to Image",
}