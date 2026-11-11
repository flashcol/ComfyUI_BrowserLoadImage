# ComfyUI Browser Load Image

Enhanced Load Image / Video nodes for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) with a visual browser interface.

![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom_Node-blue)
![License](https://img.shields.io/badge/License-MIT-green)

![Browser Modal Screenshot](assets/screenshot.png)

## ✨ Features

- **Visual Media Browser** — Browse and select images/videos from the input folder with a thumbnail grid modal
- **Hover Preview** — Hover over any thumbnail to see a large preview with filename and original dimensions
- **Configurable Preview Size** — Choose preview size from dropdown (320 / 480 / 640 / 768 / 1024)
- **Draggable Modal** — Drag the title bar to reposition the modal
- **Resizable Modal** — Drag the bottom-right corner to resize (min 400×300)
- **Maximize Button** — Click □ to toggle fullscreen
- **Remember Layout** — Check "记住窗口" to persist your preferred window position and size (also remembers the last folder)
- **Search & Filter** — Real-time search to quickly find files by name (searches all folders)
- **Keyboard Navigation** — Arrow keys, PageUp/Down, Home/End for scrolling; ESC to close
- **Subfolders (one level)** — Group media into folders under `input/`; navigate with folder cards and a breadcrumb
- **File Management** — Delete, move, rename and batch-select files and folders right in the modal
- **Trash** — Deletions are recoverable: restore to the original location, or purge permanently

## 📦 Included Nodes

| Node | Description | Output |
|------|-------------|--------|
| **Browser Load Image** | Load images with visual browser | IMAGE, MASK |
| **Browser Load Video to Image** | Convert video to image sequence | IMAGE, INT, INT |
| **Browser Load Video** | Load video (standard VIDEO type) | VIDEO |

## 🔧 Installation

### Option 1: ComfyUI Manager (Recommended)

Search for `ComfyUI_BrowserLoadImage` in [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager) and install.

### Option 2: Manual Installation

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/flashcol/ComfyUI_BrowserLoadImage.git
cd ComfyUI_BrowserLoadImage
pip install -r requirements.txt
```

Restart ComfyUI after installation.

### Dependencies

- **Image node**: No extra dependencies (uses PIL/Pillow included with ComfyUI)
- **Video nodes**: Requires `opencv-python` (`pip install opencv-python`)

## 🖱️ Usage

1. Add a **Browser Load Image** node to your workflow
2. Click the **"浏览图片"** (Browse Images) button
3. Browse, search, and click a thumbnail to select it; click a folder card to enter it
4. The selected file is set as the node's input (subfolder files look like `sub/a.png`)

## 🗂️ File Management

All operations act on the `input/` directory and are available in the browser modal.

- **Subfolders** — One level only. Click a folder card to enter it, use the breadcrumb to go back. Create folders with **新建文件夹**.
- **Delete** — Click ✕ on a card, or turn on **管理** (manage mode), multi-select, and press `Delete`. Files and whole folders are moved to `input/.trash/`, never deleted permanently.
- **Move** — In manage mode, select files and click **移动到…**. On a name clash a ` (1)` suffix is added; nothing is overwritten.
- **Rename** — Click ✎ on a card, or select one item in manage mode and press `F2`. A file's extension cannot be changed.

> Moving or renaming changes file paths. Nodes in other saved workflows that reference the old path will not find the file.

### Trash

- Open it with **回收站 (N)** in the toolbar (hover to see the size it occupies). Each deletion records the original path in `input/.trash/.index.json`.
- **Restore** — Back to the original path. A missing original folder is recreated; on a name clash a ` (n)` suffix is added. Entries without an index record are restored to the root.
- **Inspect folders** — Click 👁 on a folder card to look inside a deleted folder. There you can restore or purge individual files; once a folder entry is emptied it disappears from the trash.
- **Purge / Empty trash** — Irreversible, with a confirmation dialog. The trash is never cleaned automatically.

### HTTP API

Registered on ComfyUI's server (all paths are validated to stay inside `input/`):
`GET /bli/list`, `POST /bli/delete`, `/bli/move`, `/bli/mkdir`, `/bli/rename`,
`GET /bli/trash/list`, `POST /bli/trash/restore`, `/bli/trash/purge`.

## 📁 Project Structure

```
ComfyUI_BrowserLoadImage/
├── __init__.py              # Plugin entry point (registers nodes and API)
├── api/
│   └── routes.py            # /bli/* HTTP endpoints
├── nodes/
│   ├── utils.py             # Shared utilities (media listing, path resolving)
│   ├── fileops.py           # Delete / move / rename / trash operations
│   ├── browser_load_image.py
│   ├── browser_load_video.py
│   └── browser_load_video_standard.py
├── web/
│   ├── js/browserLoadImage.js   # Frontend extension
│   └── css/browserLoadImage.css # Stylesheet reference
├── config/settings.py       # Constants
└── tests/
    ├── test_nodes.py        # Node and utility tests
    └── test_fileops.py      # File management and trash tests
```

## 🧪 Running Tests

```bash
cd ComfyUI/custom_nodes/ComfyUI_BrowserLoadImage
python -m pytest tests/ -v
```

## 📄 License

[MIT License](LICENSE)
