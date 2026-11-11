"""
input 目录文件操作：删除（移入 .trash）、移动、新建文件夹、重命名。

约束：
- 只允许操作 input 目录内的内容，分组仅支持一级子文件夹。
- 路径一律使用相对路径（正斜杠）："a.png" 或 "sub/a.png"。
- 以 '.' 开头的名称视为隐藏（如 .trash），不允许通过接口访问。
"""

import json
import os
import re
import shutil
import time

from .utils import (
    SUPPORTED_IMAGE_FORMATS, SUPPORTED_VIDEO_FORMATS, folder_paths,
)

TRASH_DIR = ".trash"
TRASH_INDEX = ".index.json"  # 记录回收条目的原路径，用于还原
_TRASH_PREFIX = re.compile(r"^\d{8}-\d{6}_")
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
    index = None
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
            if index is None:
                index = _load_index(trash)
            index[os.path.basename(dest)] = {
                "orig": norm, "kind": kind, "at": int(time.time()),
            }
            deleted.append(norm)
        except (FileOpError, OSError) as e:
            failed.append({"path": rel, "reason": str(e)})
    if index is not None:
        _save_index(trash, index)
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


# ===== 回收站 =====

def _trash_path():
    return os.path.join(input_root(), TRASH_DIR)


def _load_index(trash):
    """读取索引；缺失或损坏时返回空字典（还原时回退到根目录）。"""
    try:
        with open(os.path.join(trash, TRASH_INDEX), encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_index(trash, index):
    """原子写入索引（先写临时文件再替换）。"""
    tmp = os.path.join(trash, TRASH_INDEX + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False)
    os.replace(tmp, os.path.join(trash, TRASH_INDEX))


def _trash_entry(name):
    """把回收站条目名解析为 .trash 内的绝对路径（只允许单层名称）。"""
    if (not isinstance(name, str) or not name or name.startswith(".")
            or "/" in name or "\\" in name or ":" in name):
        raise FileOpError("invalid trash entry")
    trash = os.path.realpath(_trash_path())
    full = os.path.realpath(os.path.join(trash, name))
    if os.path.dirname(full) != trash:
        raise FileOpError("invalid trash entry")
    return full


def _tree_stats(path):
    """返回 (媒体文件数, 总字节数, 图片数, 视频数)。"""
    if os.path.isfile(path):
        ext = os.path.splitext(path)[1].lower()
        return (1, os.path.getsize(path),
                int(ext in SUPPORTED_IMAGE_FORMATS), int(ext in SUPPORTED_VIDEO_FORMATS))
    count, size, images, videos = 0, 0, 0, 0
    for dirpath, _dirs, names in os.walk(path):
        for n in names:
            try:
                size += os.path.getsize(os.path.join(dirpath, n))
            except OSError:
                pass
            ext = os.path.splitext(n)[1].lower()
            if ext in ALL_MEDIA_FORMATS:
                count += 1
                images += ext in SUPPORTED_IMAGE_FORMATS
                videos += ext in SUPPORTED_VIDEO_FORMATS
    return count, size, images, videos


def _trash_list_root(formats):
    """列出回收站条目。文件按 formats 过滤，文件夹条目始终显示。

    Returns:
        {"entries": [...], "total_count": n, "total_size": bytes}
    """
    trash = _trash_path()
    if not os.path.isdir(trash):
        return {"entries": [], "total_count": 0, "total_size": 0}
    index = _load_index(trash)
    entries, total_count, total_size = [], 0, 0
    for name in os.listdir(trash):
        if name.startswith("."):
            continue
        full = os.path.join(trash, name)
        is_dir = os.path.isdir(full)
        count, size, images, videos = _tree_stats(full)
        total_count += 1
        total_size += size
        if not is_dir and os.path.splitext(name)[1].lower() not in formats:
            continue
        rec = index.get(name) if isinstance(index.get(name), dict) else {}
        try:
            mtime = int(os.path.getmtime(full))
        except OSError:
            mtime = 0
        entries.append({
            "name": name,
            "kind": "folder" if is_dir else "file",
            "orig": rec.get("orig") or _TRASH_PREFIX.sub("", name),
            "at": rec.get("at") or mtime,
            "size": size,
            "count": count,
            "images": images,
            "videos": videos,
        })
    entries.sort(key=lambda e: e["at"], reverse=True)
    return {"entries": entries, "total_count": total_count, "total_size": total_size}


def trash_restore(names):
    """还原到原路径：原文件夹不存在则重建，重名时加 ' (n)' 后缀，不覆盖。

    Returns:
        {"restored": [{"name", "to"}], "failed": [{"path", "reason"}]}
    """
    root = input_root()
    trash = _trash_path()
    index = _load_index(trash)
    restored, failed = [], []
    for name in names:
        try:
            full = _trash_entry(name)
            if not os.path.exists(full):
                raise FileOpError("not found")
            kind = "folder" if os.path.isdir(full) else "file"
            rec = index.get(name) if isinstance(index.get(name), dict) else {}
            orig = rec.get("orig") or _TRASH_PREFIX.sub("", name)
            try:
                target, _ = safe_resolve(orig, kind)
            except FileOpError:  # 索引被篡改/损坏：回退到根目录
                target = os.path.join(root, _TRASH_PREFIX.sub("", name))
            dest_dir = os.path.dirname(target)
            os.makedirs(dest_dir, exist_ok=True)
            dest = _unique_path(dest_dir, os.path.basename(target))
            shutil.move(full, dest)
            index.pop(name, None)
            restored.append({"name": name, "to": os.path.relpath(dest, root).replace("\\", "/")})
        except (FileOpError, OSError) as e:
            failed.append({"path": str(name), "reason": str(e)})
    if os.path.isdir(trash):
        _save_index(trash, index)
    return {"restored": restored, "failed": failed}


def trash_purge(names=None):
    """彻底删除回收站条目；names 为 None 表示清空回收站。不可恢复。

    Returns:
        {"purged": [...], "failed": [{"path", "reason"}]}
    """
    trash = _trash_path()
    if not os.path.isdir(trash):
        return {"purged": [], "failed": []}
    if names is None:
        names = [n for n in os.listdir(trash) if not n.startswith(".")]
    index = _load_index(trash)
    purged, failed = [], []
    for name in names:
        try:
            full = _trash_entry(name)
            if os.path.isdir(full) and not os.path.islink(full):
                shutil.rmtree(full)
            elif os.path.lexists(full):
                os.remove(full)
            index.pop(name, None)
            purged.append(name)
        except (FileOpError, OSError) as e:
            failed.append({"path": str(name), "reason": str(e)})
    _save_index(trash, index)
    return {"purged": purged, "failed": failed}


# ----- 回收站内的文件夹条目：查看 / 单文件还原 / 单文件彻底删除 -----

def trash_list(formats, folder=None):
    """folder 为 None 时列出回收站条目；否则列出该文件夹条目内的媒体文件。

    Returns:
        folder 为 None：_trash_list_root 的结果
        否则：{"entries": [{"name","kind","at","size"}], "folder", "orig"}
    """
    if folder is None:
        return _trash_list_root(formats)
    full = _trash_folder_entry(folder)
    index = _load_index(_trash_path())
    rec = index.get(folder) if isinstance(index.get(folder), dict) else {}
    try:
        at = rec.get("at") or int(os.path.getmtime(full))
    except OSError:
        at = 0
    entries = []
    for n in sorted(os.listdir(full)):
        p = os.path.join(full, n)
        if (n.startswith(".") or not os.path.isfile(p)
                or os.path.splitext(n)[1].lower() not in formats):
            continue
        entries.append({"name": n, "kind": "file", "at": at, "size": os.path.getsize(p)})
    return {"entries": entries, "folder": folder, "orig": _orig_of(folder, index)}


def _trash_folder_entry(folder):
    full = _trash_entry(folder)
    if not os.path.isdir(full):
        raise FileOpError("not a folder entry")
    return full


def _orig_of(name, index):
    rec = index.get(name) if isinstance(index.get(name), dict) else {}
    return rec.get("orig") or _TRASH_PREFIX.sub("", name)


def _inner_file(folder_full, fname):
    """解析回收站文件夹条目内的单个媒体文件（只允许单层名称）。"""
    if (not isinstance(fname, str) or not fname or fname.startswith(".")
            or "/" in fname or "\\" in fname or ":" in fname):
        raise FileOpError("invalid file name")
    _check_media_ext(fname)
    full = os.path.join(folder_full, fname)
    if not os.path.isfile(full):
        raise FileOpError("not found")
    if os.path.dirname(os.path.realpath(full)) != os.path.realpath(folder_full):
        raise FileOpError("invalid file name")
    return full


def _remove_if_empty(folder_full, index, name):
    """文件夹条目被取空后移除它及其索引记录。"""
    if not os.listdir(folder_full):
        os.rmdir(folder_full)
        index.pop(name, None)
        return True
    return False


def trash_restore_in(folder, files):
    """把回收站文件夹条目里的若干文件还原到原文件夹（缺失则重建，重名加后缀）。

    Returns:
        {"restored": [{"name","to"}], "failed": [...], "folder_removed": bool}
    """
    root = input_root()
    trash = _trash_path()
    full = _trash_folder_entry(folder)
    index = _load_index(trash)
    try:
        target_dir, _ = safe_resolve(_orig_of(folder, index), "folder")
    except FileOpError:  # 索引损坏/被篡改：回退到根目录下的同名文件夹
        target_dir = os.path.join(root, _TRASH_PREFIX.sub("", folder))
    restored, failed = [], []
    for f in files:
        try:
            src = _inner_file(full, f)
            os.makedirs(target_dir, exist_ok=True)
            dest = _unique_path(target_dir, f)
            shutil.move(src, dest)
            restored.append({
                "name": f,
                "to": os.path.relpath(dest, root).replace("\\", "/"),
            })
        except (FileOpError, OSError) as e:
            failed.append({"path": str(f), "reason": str(e)})
    removed = _remove_if_empty(full, index, folder)
    _save_index(trash, index)
    return {"restored": restored, "failed": failed, "folder_removed": removed}


def trash_purge_in(folder, files):
    """彻底删除回收站文件夹条目里的若干文件（不可恢复）。

    Returns:
        {"purged": [...], "failed": [...], "folder_removed": bool}
    """
    trash = _trash_path()
    full = _trash_folder_entry(folder)
    index = _load_index(trash)
    purged, failed = [], []
    for f in files:
        try:
            os.remove(_inner_file(full, f))
            purged.append(f)
        except (FileOpError, OSError) as e:
            failed.append({"path": str(f), "reason": str(e)})
    removed = _remove_if_empty(full, index, folder)
    _save_index(trash, index)
    return {"purged": purged, "failed": failed, "folder_removed": removed}
