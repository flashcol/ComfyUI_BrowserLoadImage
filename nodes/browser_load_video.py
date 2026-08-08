"""
Browser Load Video To Image Node - 将视频转换为图片序列
"""

import os
import torch
import numpy as np
import cv2

from .utils import (
    list_media_files, resolve_media_path, is_changed, validate_input,
    SUPPORTED_VIDEO_FORMATS,
)


class BrowserLoadVideoToImage:
    """将视频转换为图片序列的节点"""

    @classmethod
    def INPUT_TYPES(cls):
        videos = list_media_files(SUPPORTED_VIDEO_FORMATS)
        video_input = (videos, {"default": videos[0], "video_upload": True}) if videos else ([],)
        return {
            "required": {
                "video": video_input,
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
        return is_changed(video)

    @classmethod
    def VALIDATE_INPUTS(cls, video, force_rate, force_size, frame_load_cap):
        return validate_input(video)

    def load_video(self, video, force_rate=0, force_size=0, frame_load_cap=0):
        """将视频转换为图片序列"""
        if not video:
            return (torch.zeros((1, 64, 64, 3), dtype=torch.float32), 1, 30)

        video_path = resolve_media_path(video)

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video}")

        try:
            # 获取视频信息
            original_fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # 计算目标尺寸（保持宽高比）
            if force_size > 0:
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

            # 计算目标帧率和帧间隔
            target_fps = force_rate if force_rate > 0 else original_fps
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

                if force_size > 0:
                    frame = cv2.resize(frame, (target_width, target_height))

                # BGR -> RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = frame.astype(np.float32) / 255.0

                frames.append(frame)
                loaded_frames += 1
                frame_idx += frame_interval

            if not frames:
                raise ValueError(f"Could not read any frames from video: {video}")

            # [F, H, W, C]
            video_tensor = torch.from_numpy(np.array(frames))
            return (video_tensor, len(frames), target_fps)
        finally:
            cap.release()