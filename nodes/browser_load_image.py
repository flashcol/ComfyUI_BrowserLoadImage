"""
Browser Load Image Node - 完全按照ComfyUI原生Load Image节点标准实现
"""

import os
import torch
from PIL import Image, ImageOps
import numpy as np

try:
    import folder_paths
except ImportError:
    folder_paths = None

class BrowserLoadImage:
    """
    完全按照ComfyUI原生Load Image节点标准实现的Browser Load Image节点
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # 获取input目录中的图片列表
        images = []
        if folder_paths:
            try:
                input_dir = folder_paths.get_input_directory()
                if input_dir and os.path.exists(input_dir):
                    # 扫描支持的图片格式
                    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.gif'}
                    for file in os.listdir(input_dir):
                        if os.path.isfile(os.path.join(input_dir, file)):
                            ext = os.path.splitext(file)[1].lower()
                            if ext in supported_formats:
                                images.append(file)
                    images.sort()
            except:
                pass
        
        if images:
            return {
                "required": {
                    "image": (images, {"default": images[0], "image_upload": True}),
                }
            }
        else:
            # 如果没有图片，使用空列表
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
        if not image:
            return False
        
        # 获取图片完整路径
        if folder_paths:
            try:
                image_path = folder_paths.get_annotated_filepath(image)
            except:
                # 如果无法获取路径，返回False
                return False
        else:
            return False
        
        # 检查文件是否存在和修改时间
        if not os.path.exists(image_path):
            return False
        
        mtime = os.path.getmtime(image_path)
        return mtime
    
    @classmethod
    def VALIDATE_INPUTS(cls, image):
        if not image:
            return True  # 允许空输入
        
        # 检查文件是否存在
        if folder_paths:
            try:
                image_path = folder_paths.get_annotated_filepath(image)
                return os.path.exists(image_path)
            except:
                return False
        else:
            return False
    
    def load_image(self, image):
        """完全按照ComfyUI原生Load Image节点标准实现的图片加载方法"""
        if not image:
            # 如果没有选择图片，返回默认值
            return (torch.zeros((1, 64, 64, 3), dtype=torch.float32), 
                   torch.ones((1, 64, 64), dtype=torch.float32))
        
        # 获取图片完整路径
        if folder_paths:
            try:
                image_path = folder_paths.get_annotated_filepath(image)
            except:
                # 如果无法获取路径，尝试直接构造
                input_dir = folder_paths.get_input_directory()
                image_path = os.path.join(input_dir, image)
        else:
            # 如果folder_paths不可用，使用相对路径
            image_path = image
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image}")
        
        '''
        # 使用PIL加载图片
        img = Image.open(image_path)
        
        # 处理EXIF方向信息
        img = ImageOps.exif_transpose(img)
        
        # 处理多帧图片（如GIF动画），只取第一帧
        if hasattr(img, 'is_animated') and img.is_animated:
            img.seek(0)
            img = img.convert('RGB')
        else:
            # 转换为RGB格式
            img = img.convert("RGB")
        
        # 转换为numpy数组并归一化到[0,1]
        image_np = np.array(img).astype(np.float32) / 255.0
        
        # 转换为torch.Tensor，添加batch维度 [B, H, W, C]
        image_tensor = torch.from_numpy(image_np)[None,]
        
        # 创建mask
        if 'A' in img.getbands():
            # 如果有alpha通道，使用alpha通道创建mask
            mask_np = np.array(img.getchannel('A')).astype(np.float32) / 255.0
            mask_tensor = torch.from_numpy(mask_np)[None,]
        else:
            # 如果没有alpha通道，创建白色mask
            mask_tensor = torch.ones((1, image_tensor.shape[1], image_tensor.shape[2]), dtype=torch.float32)
        
        return (image_tensor, mask_tensor)
        '''
        try:
            i = Image.open(image_path)
            i = ImageOps.exif_transpose(i)
            image = i.convert("RGB")
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            
            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)[None,]
            else:
                mask = torch.zeros((1, image.shape[1], image.shape[2]), dtype=torch.float32)
            
            return (image, mask)
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            # 返回一个1x1的空图像和掩码
            empty_image = torch.zeros((1, 1, 1, 3), dtype=torch.float32)
            empty_mask = torch.zeros((1, 1, 1), dtype=torch.float32)
            return (empty_image, empty_mask)      
# 注册节点
NODE_CLASS_MAPPINGS = {
    "BrowserLoadImage": BrowserLoadImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BrowserLoadImage": "Browser Load Image",
}