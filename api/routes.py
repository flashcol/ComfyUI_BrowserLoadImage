"""
HTTP 接口：/bli/list /bli/delete /bli/move /bli/mkdir /bli/rename
          /bli/trash/list /bli/trash/restore /bli/trash/purge
"""

import os

from aiohttp import web

from ..nodes import fileops
from ..nodes.utils import (
    iter_input_files, SUPPORTED_IMAGE_FORMATS, SUPPORTED_VIDEO_FORMATS,
)

_FORMATS = {"image": SUPPORTED_IMAGE_FORMATS, "video": SUPPORTED_VIDEO_FORMATS}


def register_routes(routes):
    async def _json(request):
        try:
            data = await request.json()
        except Exception:
            raise fileops.FileOpError("invalid JSON body")
        if not isinstance(data, dict):
            raise fileops.FileOpError("invalid JSON body")
        return data

    def _str_list(value):
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            raise fileops.FileOpError("expected a list of strings")
        return value

    def _guard(handler):
        async def wrapper(request):
            try:
                return web.json_response(await handler(request))
            except fileops.FileOpError as e:
                return web.json_response({"error": str(e)}, status=400)
            except OSError as e:
                return web.json_response({"error": str(e)}, status=500)
        return wrapper

    @routes.get("/bli/list")
    @_guard
    async def bli_list(request):
        formats = _FORMATS.get(request.query.get("type", "image"))
        if formats is None:
            raise fileops.FileOpError("invalid type")
        files = sorted(
            f for f in iter_input_files()
            if os.path.splitext(f)[1].lower() in formats
        )
        return {"files": files, "folders": fileops.list_folders()}

    @routes.post("/bli/delete")
    @_guard
    async def bli_delete(request):
        data = await _json(request)
        return fileops.delete_items(_str_list(data.get("paths")))

    @routes.post("/bli/move")
    @_guard
    async def bli_move(request):
        data = await _json(request)
        folder = data.get("folder", "")
        if not isinstance(folder, str):
            raise fileops.FileOpError("invalid folder")
        return fileops.move_files(_str_list(data.get("files")), folder)

    @routes.post("/bli/mkdir")
    @_guard
    async def bli_mkdir(request):
        data = await _json(request)
        return {"folder": fileops.make_folder(data.get("name"))}

    @routes.post("/bli/rename")
    @_guard
    async def bli_rename(request):
        data = await _json(request)
        return {"path": fileops.rename_item(data.get("path"), data.get("name"))}

    @routes.get("/bli/trash/list")
    @_guard
    async def bli_trash_list(request):
        formats = _FORMATS.get(request.query.get("type", "image"))
        if formats is None:
            raise fileops.FileOpError("invalid type")
        return fileops.trash_list(formats, request.query.get("folder"))

    @routes.post("/bli/trash/restore")
    @_guard
    async def bli_trash_restore(request):
        data = await _json(request)
        if data.get("folder") is not None:
            return fileops.trash_restore_in(data["folder"], _str_list(data.get("files")))
        return fileops.trash_restore(_str_list(data.get("names")))

    @routes.post("/bli/trash/purge")
    @_guard
    async def bli_trash_purge(request):
        data = await _json(request)
        if data.get("all") is True:
            return fileops.trash_purge(None)
        if data.get("folder") is not None:
            return fileops.trash_purge_in(data["folder"], _str_list(data.get("files")))
        return fileops.trash_purge(_str_list(data.get("names")))
