"""
input 目录文件操作：删除（移入 .trash）、移动、新建文件夹、重命名。

约束：
- 只允许操作 input 目录内的内容，分组仅支持一级子文件夹。
- 路径一律使用相对路径（正斜杠）："a.png" 或 "sub/a.png"。
- 以 '.' 开头的名称视为隐藏（如 .trash），不允许通过接口访问。
"""

import os
import re
import shutil
import time

from .utils import (
    SUPPORTED_IMAGE_FORMATS, SUPPORTED_VIDEO_FORMATS, folder_paths,
)

TRASH_DIR = ".trash"
ALL_MEDIA_FORMATS = SUPPORTED_IMAGE_FORMATS | SUPPORTED_VIDEO_FORMATS

_ILLEGAL_NAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


class FileOpError(Exception):
    """文件操作失败（消息可直接展示给用户）"""


def input_root():
    if not folder_paths:
        raise FileOpError("input directory unavailable")
    root = folder_paths.get_input_directory()
    if not root or not os.path.isdir(root):
        raise FileOpError("input directory unavailable")
    return os.path.realpath(root)


def _split_rel(rel):
    if not isinstance(rel, str) or not rel:
        raise FileOpError("invalid path")
    rel = rel.replace("\\", "/")
    if rel.startswith("/") or re.match(r"^[A-Za-z]:", rel):
        raise FileOpError("invalid path")
    parts = rel.split("/")
    for p in parts:
        if p in ("", ".", "..") or p.startswith(".") or ":" in p:
            raise FileOpError("invalid path")
    return parts


def safe_resolve(rel, kind):
    """将相对路径解析为 input 目录内的绝对路径。

    Args:
        rel: 相对路径
        kind: "file"（最多 sub/name 两级）或 "folder"（仅一级）

    Returns:
        (绝对路径, 规范化相对路径)
    """
    parts = _split_rel(rel)
    if kind == "folder" and len(parts) != 1:
        raise FileOpError("only one level of folders is supported")
    if kind == "file" and len(parts) > 2:
        raise FileOpError("only one level of folders is supported")
    root = input_root()
    full = os.path.realpath(os.path.join(root, *parts))
    try:
        inside = os.path.commonpath([root, full]) == root
    except ValueError:
        inside = False
    if not inside or full == root:
        raise FileOpError("path escapes input directory")
    return full, "/".join(parts)


def _check_media_ext(name):
    if os.path.splitext(name)[1].lower() not in ALL_MEDIA_FORMATS:
        raise FileOpError("unsupported file type: " + name)


def validate_name(name):
    """校验单个文件/文件夹名称（不含路径）。"""
    if not isinstance(name, str) or not name:
        raise FileOpError("name is empty")
    if name != name.strip() or name.endswith("."):
        raise FileOpError("name must not start/end with space or end with '.'")
    if name.startswith("."):
        raise FileOpError("name must not start with '.'")
    if _ILLEGAL_NAME_CHARS.search(name):
        raise FileOpError("name contains illegal characters")
    if len(name) > 200:
        raise FileOpError("name too long")
    if os.path.splitext(name)[0].upper() in _RESERVED_NAMES:
        raise FileOpError("reserved name")


def _unique_path(directory, name):
    """目标已存在时追加 ' (n)' 后缀，永不覆盖。"""
    base, ext = os.path.splitext(name)
    candidate = os.path.join(directory, name)
    n = 1
    while os.path.exists(candidate):
        candidate = os.path.join(directory, f"{base} ({n}){ext}")
        n += 1
    return candidate


def list_folders():
    """返回 input 下的一级子文件夹名（排序，不含隐藏目录）。"""
    root = input_root()
    return sorted(
        n for n in os.listdir(root)
        if not n.startswith(".") and os.path.isdir(os.path.join(root, n))
    )


def delete_items(paths):
    """把文件或整个文件夹移入 input/.trash/。

    Returns:
        {"deleted": [...], "failed": [{"path", "reason"}]}
    """
    root = input_root()
    trash = os.path.join(root, TRASH_DIR)
    deleted, failed = [], []
    for rel in paths:
        try:
            parts = _split_rel(rel)
            kind = "folder" if len(parts) == 1 and os.path.isdir(
                os.path.join(root, parts[0])) else "file"
            full, norm = safe_resolve(rel, kind)
            if kind == "file":
                _check_media_ext(full)
            if not os.path.exists(full):
                deleted.append(norm)  # 已不存在，视为已删除
                continue
            os.makedirs(trash, exist_ok=True)
            stamp = time.strftime("%Y%m%d-%H%M%S")
            dest = _unique_path(trash, f"{stamp}_{os.path.basename(full)}")
            shutil.move(full, dest)
            deleted.append(norm)
        except (FileOpError, OSError) as e:
            failed.append({"path": rel, "reason": str(e)})
    return {"deleted": deleted, "failed": failed}


def make_folder(name):
    validate_name(name)
    full, norm = safe_resolve(name, "folder")
    if os.path.exists(full):
        raise FileOpError("already exists")
    os.mkdir(full)
    return norm


def move_files(files, folder):
    """把文件移动到一级子文件夹（folder 为空字符串表示根目录）。

    Returns:
        {"moved": [{"from", "to"}], "failed": [{"path", "reason"}]}
    """
    root = input_root()
    if folder:
        dest_dir, folder = safe_resolve(folder, "folder")
        if not os.path.isdir(dest_dir):
            raise FileOpError("target folder does not exist")
    else:
        dest_dir = root
    moved, failed = [], []
    for rel in files:
        try:
            full, norm = safe_resolve(rel, "file")
            _check_media_ext(full)
            if not os.path.isfile(full):
                raise FileOpError("file not found")
            if os.path.dirname(full) == dest_dir:
                continue
            dest = _unique_path(dest_dir, os.path.basename(full))
            shutil.move(full, dest)
            new_rel = (folder + "/" if folder else "") + os.path.basename(dest)
            moved.append({"from": norm, "to": new_rel})
        except (FileOpError, OSError) as e:
            failed.append({"path": rel, "reason": str(e)})
    return {"moved": moved, "failed": failed}


def rename_item(path, new_name):
    """重命名文件（保持扩展名不变）或一级子文件夹。

    Returns:
        新的相对路径
    """
    root = input_root()
    parts = _split_rel(path)
    kind = "folder" if len(parts) == 1 and os.path.isdir(
        os.path.join(root, parts[0])) else "file"
    full, norm = safe_resolve(path, kind)
    if not os.path.exists(full):
        raise FileOpError("not found")
    validate_name(new_name)
    if kind == "file":
        _check_media_ext(full)
        if os.path.splitext(new_name)[1].lower() != os.path.splitext(full)[1].lower():
            raise FileOpError("file extension must not change")
    target = os.path.join(os.path.dirname(full), new_name)
    # 仅大小写不同（Windows）时 target 与 full 是同一文件，允许
    if os.path.exists(target) and not os.path.samefile(target, full):
        raise FileOpError("target already exists")
    os.rename(full, target)
    return "/".join(parts[:-1] + [new_name])
