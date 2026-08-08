# ComfyUI Browser Load Image

Enhanced Load Image / Video nodes for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) with a visual browser interface.

![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom_Node-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- **Visual Media Browser** — Browse and select images/videos from the input folder with a thumbnail grid modal
- **Hover Preview** — Hover over any thumbnail to see a large preview with filename and original dimensions
- **Configurable Preview Size** — Choose preview size from dropdown (320 / 480 / 640 / 768 / 1024)
- **Draggable Modal** — Drag the title bar to reposition the modal
- **Resizable Modal** — Drag the bottom-right corner to resize (min 400×300)
- **Maximize Button** — Click □ or double-click the title bar to toggle fullscreen
- **Remember Layout** — Check "记住窗口" to persist your preferred window position and size
- **Search & Filter** — Real-time search to quickly find files by name
- **Keyboard Navigation** — Arrow keys, PageUp/Down, Home/End for scrolling; ESC to close

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
```

Restart ComfyUI after installation.

### Dependencies

- **Image node**: No extra dependencies (uses PIL/Pillow included with ComfyUI)
- **Video nodes**: Requires `opencv-python` (`pip install opencv-python`)

## 🖱️ Usage

1. Add a **Browser Load Image** node to your workflow
2. Click the **"浏览图片"** (Browse Images) button
3. Browse, search, and click a thumbnail to select it
4. The selected file is set as the node's input

## 📁 Project Structure

```
ComfyUI_BrowserLoadImage/
├── __init__.py              # Plugin entry point
├── nodes/
│   ├── utils.py             # Shared utilities
│   ├── browser_load_image.py
│   ├── browser_load_video.py
│   └── browser_load_video_standard.py
├── web/
│   ├── js/browserLoadImage.js   # Frontend extension
│   └── css/browserLoadImage.css # Stylesheet reference
├── config/settings.py       # Constants
└── tests/test_nodes.py      # Unit tests
```

## 🧪 Running Tests

```bash
cd ComfyUI/custom_nodes/ComfyUI_BrowserLoadImage
python -m pytest tests/ -v
```

## 📄 License

[MIT License](LICENSE)
