"""
Browser Load 节点的公共工具模块
消除三个节点间的重复代码
"""

import os

try:
    import folder_paths
except ImportError:
    folder_paths = None

# ===== 常量 =====
SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.gif'}
SUPPORTED_VIDEO_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}


def iter_input_files():
    """列出 input 根目录及其一级子文件夹下的所有文件（相对路径，正斜杠）。

    以 '.' 开头的目录（如 .trash）和文件会被跳过。
    """
    files = []
    if not folder_paths:
        return files

    input_dir = folder_paths.get_input_directory()
    if not input_dir or not os.path.exists(input_dir):
        return files

    # os.scandir 的 DirEntry 自带类型信息，Windows 上无需对每个文件再 stat
    try:
        with os.scandir(input_dir) as it:
            for entry in it:
                name = entry.name
                if name.startswith('.'):
                    continue
                if entry.is_file():
                    files.append(name)
                elif entry.is_dir():
                    try:
                        with os.scandir(entry.path) as sub_it:
                            for sub in sub_it:
                                if not sub.name.startswith('.') and sub.is_file():
                                    files.append(name + "/" + sub.name)
                    except OSError:
                        pass
    except OSError:
        return []
    return files


def list_media_files(supported_formats):
    """扫描 input 目录（含一级子文件夹），返回排序后的相对路径列表。

    Args:
        supported_formats: 支持的文件扩展名集合，如 {'.jpg', '.png'}

    Returns:
        排序后的相对路径列表，子文件夹中的文件形如 "sub/a.png"
    """
    files = [
        f for f in iter_input_files()
        if os.path.splitext(f)[1].lower() in supported_formats
    ]
    files.sort()
    return files


def resolve_media_path(filename):
    """将文件名解析为完整的文件系统路径。

    Args:
        filename: 文件名（来自 INPUT_TYPES 的 widget 值）

    Returns:
        文件的完整路径

    Raises:
        ValueError: 文件名为空
    """
    if not filename:
        raise ValueError("No file selected")

    if folder_paths:
        try:
            return folder_paths.get_annotated_filepath(filename)
        except Exception:
            input_dir = folder_paths.get_input_directory()
            return os.path.join(input_dir, filename)

    return filename


def is_changed(filename):
    """通用 IS_CHANGED 实现，基于文件修改时间。

    Returns:
        文件修改时间戳（float），或 False 表示无变化/文件不存在
    """
    if not filename or not folder_paths:
        return False

    try:
        filepath = folder_paths.get_annotated_filepath(filename)
    except Exception:
        return False

    if not os.path.exists(filepath):
        return False

    return os.path.getmtime(filepath)


def validate_input(filename):
    """通用 VALIDATE_INPUTS 实现。

    Returns:
        True 如果输入有效（文件存在或输入为空），False 否则
    """
    if not filename:
        return True

    if folder_paths:
        try:
            filepath = folder_paths.get_annotated_filepath(filename)
            return os.path.exists(filepath)
        except Exception:
            return False

    return False
