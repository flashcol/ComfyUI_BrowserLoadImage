import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

// ===== CSS 样式（注入一次） =====
const BLI_STYLES = `
.bli-modal-overlay {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-color: rgba(0, 0, 0, 0.6);
    z-index: 10000;
}
.bli-modal {
    position: absolute;
    background-color: #2a2a2a;
    border-radius: 8px;
    border: 1px solid #444;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}
.bli-modal-title {
    color: white;
    font-size: 15px;
    font-weight: bold;
    padding: 12px 20px;
    text-align: center;
    cursor: move;
    user-select: none;
    -webkit-user-select: none;
    border-bottom: 1px solid #3a3a3a;
    flex-shrink: 0;
    background-color: #2f2f2f;
}
.bli-modal-close {
    position: absolute;
    top: 8px; right: 10px;
    background: none;
    border: none;
    color: #999;
    font-size: 22px;
    cursor: pointer;
    padding: 0;
    width: 30px; height: 30px;
    line-height: 30px;
    text-align: center;
    border-radius: 4px;
    z-index: 1;
    transition: all 0.15s ease;
}
.bli-modal-close:hover {
    color: #fff;
    background-color: rgba(255, 255, 255, 0.1);
}
.bli-modal-maximize {
    position: absolute;
    top: 8px;
    right: 42px;
    background: none;
    border: none;
    color: #999;
    font-size: 14px;
    cursor: pointer;
    padding: 0;
    width: 30px; height: 30px;
    line-height: 30px;
    text-align: center;
    border-radius: 4px;
    z-index: 1;
    transition: all 0.15s ease;
}
.bli-modal-maximize:hover {
    color: #fff;
    background-color: rgba(255, 255, 255, 0.1);
}
.bli-toolbar {
    padding: 10px 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
}
.bli-search-wrapper {
    position: relative;
    flex: 1;
}
.bli-search-input {
    width: 100%;
    padding: 8px 32px 8px 12px;
    background-color: #333;
    border: 1px solid #555;
    border-radius: 4px;
    color: white;
    font-size: 14px;
    outline: none;
    box-sizing: border-box;
    transition: border-color 0.15s ease;
}
.bli-search-input:focus {
    border-color: #777;
}
.bli-search-clear {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: #999;
    font-size: 18px;
    cursor: pointer;
    padding: 0;
    width: 20px; height: 20px;
    line-height: 20px;
    text-align: center;
    display: none;
}
.bli-search-clear:hover { color: #fff; }
.bli-preview-select {
    background: #333;
    color: #ccc;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 7px 6px;
    font-size: 13px;
    cursor: pointer;
    outline: none;
    flex-shrink: 0;
}
.bli-preview-select:focus { border-color: #777; }
.bli-remember-label {
    display: flex;
    align-items: center;
    gap: 5px;
    color: #999;
    font-size: 12px;
    cursor: pointer;
    white-space: nowrap;
    flex-shrink: 0;
    user-select: none;
    -webkit-user-select: none;
}
.bli-remember-label:hover { color: #ccc; }
.bli-remember-label input[type="checkbox"] {
    accent-color: #777;
    cursor: pointer;
    margin: 0;
}
.bli-media-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 12px;
    flex: 1;
    overflow-y: auto;
    padding: 10px 20px 20px;
    scrollbar-width: thin;
    scrollbar-color: #666 #333;
}
.bli-media-grid::-webkit-scrollbar { width: 10px; }
.bli-media-grid::-webkit-scrollbar-track { background: #333; border-radius: 5px; }
.bli-media-grid::-webkit-scrollbar-thumb { background: #666; border-radius: 5px; border: 2px solid #333; }
.bli-media-grid::-webkit-scrollbar-thumb:hover { background: #777; }
.bli-media-item {
    background-color: #333;
    border: 1px solid #555;
    border-radius: 6px;
    padding: 10px;
    cursor: pointer;
    text-align: center;
    transition: all 0.2s ease;
    display: flex;
    flex-direction: column;
    min-height: 200px;
    content-visibility: auto;
    contain-intrinsic-size: 120px 200px;
}
.bli-media-item:hover {
    background-color: #3a3a3a;
    transform: scale(1.02);
    border-color: #666;
}
.bli-media-item.selected {
    background-color: #444;
    border: 2px solid #777;
}
.bli-media-preview {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 8px;
    min-height: 150px;
}
.bli-media-preview img,
.bli-media-preview video {
    max-width: 140px;
    max-height: 140px;
    width: auto; height: auto;
    object-fit: contain;
    border-radius: 4px;
    border: 1px solid #555;
}
.bli-video-placeholder {
    width: 140px; height: 140px;
    background-color: #444;
    border-radius: 4px;
    border: 1px solid #555;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #999;
    font-size: 12px;
}
.bli-filename-container { margin-top: auto; }
.bli-filename {
    color: #ccc;
    font-size: 11px;
    word-break: break-word;
    line-height: 1.3;
    text-align: center;
    overflow-wrap: break-word;
    hyphens: auto;
}
.bli-media-item.selected .bli-filename { color: #fff; }
.bli-empty-message {
    color: #999;
    font-size: 14px;
    grid-column: 1 / -1;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 200px;
}
.bli-resize-handle {
    position: absolute;
    right: 0; bottom: 0;
    width: 18px; height: 18px;
    cursor: nwse-resize;
}
.bli-resize-handle::after {
    content: "";
    position: absolute;
    right: 4px; bottom: 4px;
    width: 8px; height: 8px;
    border-right: 2px solid #666;
    border-bottom: 2px solid #666;
}
.bli-resize-handle:hover::after { border-color: #aaa; }
.bli-modal.bli-interacting .bli-media-item {
    transition: none !important;
    transform: none !important;
}
.bli-modal.bli-interacting .bli-media-grid {
    pointer-events: none;
}
.bli-hover-preview {
    position: fixed;
    z-index: 10001;
    background: #1a1a1a;
    border: 1px solid #555;
    border-radius: 8px;
    padding: 8px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.15s ease;
    max-width: calc(var(--bli-preview-max, 480) * 1px + 16px);
}
.bli-hover-preview.visible {
    opacity: 1;
}
.bli-hover-preview img,
.bli-hover-preview video {
    display: block;
    max-width: calc(var(--bli-preview-max, 480) * 1px);
    max-height: calc(var(--bli-preview-max, 480) * 1px);
    width: auto;
    height: auto;
    object-fit: contain;
    border-radius: 4px;
}
.bli-hover-preview-info {
    color: #aaa;
    font-size: 12px;
    text-align: center;
    margin-top: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.bli-tool-btn {
    background: #333;
    color: #ccc;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 7px 10px;
    font-size: 13px;
    cursor: pointer;
    flex-shrink: 0;
    white-space: nowrap;
}
.bli-tool-btn:hover { border-color: #777; color: #fff; }
.bli-tool-btn.active { background: #4a5a78; border-color: #6d86b8; color: #fff; }
.bli-crumb {
    padding: 0 20px 4px;
    color: #aaa;
    font-size: 13px;
    flex-shrink: 0;
    user-select: none;
}
.bli-crumb-link { color: #8ab4f8; cursor: pointer; }
.bli-crumb-link:hover { text-decoration: underline; }
.bli-crumb-current { color: #fff; }
.bli-crumb-hint { color: #888; }
.bli-manage-bar {
    display: none;
    align-items: center;
    gap: 8px;
    padding: 4px 20px 8px;
    flex-shrink: 0;
}
.bli-manage-info { color: #ccc; font-size: 13px; margin-right: auto; }
.bli-btn {
    background: #3a3a3a;
    color: #ddd;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 5px 12px;
    font-size: 13px;
    cursor: pointer;
}
.bli-btn:hover:not(:disabled) { border-color: #888; color: #fff; }
.bli-btn:disabled { opacity: 0.4; cursor: default; }
.bli-btn-primary { background: #3d5a8a; border-color: #5b7db5; color: #fff; }
.bli-btn-danger { background: #6b2d2d; border-color: #9a4444; color: #fff; }
.bli-media-item { position: relative; }
.bli-card-actions {
    position: absolute;
    top: 4px; right: 4px;
    display: none;
    gap: 4px;
}
.bli-media-item:hover .bli-card-actions { display: flex; }
.bli-card-actions button {
    width: 22px; height: 22px;
    padding: 0;
    line-height: 20px;
    font-size: 12px;
    background: rgba(0, 0, 0, 0.7);
    color: #ddd;
    border: 1px solid #666;
    border-radius: 4px;
    cursor: pointer;
}
.bli-card-actions button:hover { background: #555; color: #fff; }
.bli-card-actions .bli-act-del:hover { background: #8a3333; }
.bli-card-check {
    position: absolute;
    top: 6px; left: 6px;
    width: 16px; height: 16px;
    border: 2px solid #999;
    border-radius: 3px;
    background: rgba(0, 0, 0, 0.5);
    display: none;
}
.bli-modal.bli-manage .bli-card-check { display: block; }
.bli-media-item.checked { border: 2px solid #6d86b8; background-color: #3a4358; }
.bli-media-item.checked .bli-card-check { background: #6d86b8; border-color: #fff; }
.bli-folder-icon { font-size: 64px; }
.bli-trash-meta { color: #888; font-size: 10px; margin-top: 2px; }
.bli-rename-input {
    width: 100%;
    box-sizing: border-box;
    background: #222;
    color: #fff;
    border: 1px solid #6d86b8;
    border-radius: 3px;
    font-size: 11px;
    padding: 2px 4px;
    outline: none;
}
.bli-toast {
    position: absolute;
    left: 50%; bottom: 20px;
    transform: translateX(-50%);
    background: #5a2a2a;
    color: #fff;
    border: 1px solid #9a4444;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
    z-index: 5;
    max-width: 80%;
}
.bli-dialog-layer {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0, 0, 0, 0.45);
    display: flex;
    align-items: center;
    justify-content: center;
}
.bli-dialog {
    background: #2f2f2f;
    border: 1px solid #555;
    border-radius: 8px;
    padding: 16px 20px;
    min-width: 320px;
    max-width: 480px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
}
.bli-dialog-title { color: #fff; font-size: 15px; font-weight: bold; margin-bottom: 10px; }
.bli-dialog-msg { color: #ccc; font-size: 13px; white-space: pre-wrap; word-break: break-all; margin-bottom: 10px; }
.bli-dialog-input, .bli-dialog-select {
    width: 100%;
    box-sizing: border-box;
    background: #333;
    color: #fff;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 7px 10px;
    font-size: 14px;
    outline: none;
}
.bli-dialog-btns { display: flex; justify-content: flex-end; gap: 8px; margin-top: 14px; }
`;

// ===== 节点 -> 媒体类型映射 =====
const NODE_MEDIA_MAP = {
    "BrowserLoadImage": "image",
    "BrowserLoadVideoToImage": "video",
    "BrowserLoadVideoStandard": "video",
};

// ===== 媒体类型 -> widget 名称映射 =====
const MEDIA_WIDGET_NAME = {
    "image": "image",
    "video": "video",
};

// ===== 偏好存储 =====
const STORAGE_KEY = "bli-modal-prefs";
const PREVIEW_SIZES = [320, 480, 640, 768, 1024];
const DEFAULT_PREFS = { previewSize: 480, remember: false, lastFolder: "", x: -1, y: -1, w: 800, h: 600 };

// 相对路径辅助："sub/a.png" -> 文件夹 "sub" / 文件名 "a.png"
function dirOf(rel) { const i = rel.indexOf("/"); return i < 0 ? "" : rel.slice(0, i); }
function baseOf(rel) { return rel.slice(rel.indexOf("/") + 1); }
function viewUrl(rel) {
    return "/view?filename=" + encodeURIComponent(baseOf(rel))
        + "&subfolder=" + encodeURIComponent(dirOf(rel)) + "&type=input";
}

function loadPrefs() {
    try { return Object.assign({}, DEFAULT_PREFS, JSON.parse(localStorage.getItem(STORAGE_KEY))); }
    catch { return Object.assign({}, DEFAULT_PREFS); }
}
function savePrefs(p) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(p)); } catch {}
}

/**
 * 注入 CSS 样式（仅一次，通过 ID 去重）
 */
function injectStyles() {
    if (document.getElementById("bli-styles")) return;
    const style = document.createElement("style");
    style.id = "bli-styles";
    style.textContent = BLI_STYLES;
    document.head.appendChild(style);
}

// ===== 注册 ComfyUI 扩展 =====
app.registerExtension({
    name: "ComfyUI.BrowserLoadImage",

    async beforeRegisterNodeDef(nodeType, nodeData, _app) {
        const mediaType = NODE_MEDIA_MAP[nodeData.name];
        if (!mediaType) return;

        const origOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const ret = origOnNodeCreated
                ? origOnNodeCreated.apply(this, arguments)
                : undefined;
            addBrowseWidget(this, mediaType);
            return ret;
        };
    },
});

/**
 * 为节点添加「浏览」按钮 widget
 */
function addBrowseWidget(node, mediaType) {
    if (node._browseWidgetAdded) return;
    node._browseWidgetAdded = true;

    const widgetName = MEDIA_WIDGET_NAME[mediaType];
    const mediaWidget = node.widgets.find((w) => w.name === widgetName);
    if (!mediaWidget) return;

    node.addWidget(
        "button",
        mediaType === "video" ? "浏览视频" : "浏览图片",
        "browse",
        () => openMediaModal(node, mediaWidget, mediaType)
    );
}

/**
 * 打开媒体选择弹窗
 * 支持：拖拽标题栏移动、右下角缩放、搜索过滤、键盘导航
 */
function openMediaModal(_node, mediaWidget, mediaType) {
    // 移除已有弹窗
    const existing = document.getElementById("bli-modal-overlay");
    if (existing) existing.remove();

    injectStyles();

    // ===== 创建 DOM 结构 =====

    // 遮罩层
    const overlay = document.createElement("div");
    overlay.id = "bli-modal-overlay";
    overlay.className = "bli-modal-overlay";

    // 弹窗主体（absolute 定位）
    const modal = document.createElement("div");
    modal.className = "bli-modal";
    const prefs = loadPrefs();
    const initW = prefs.remember && prefs.w > 0 ? prefs.w : 800;
    const initH = prefs.remember && prefs.h > 0 ? prefs.h : 600;
    modal.style.width = initW + "px";
    modal.style.height = initH + "px";
    if (prefs.remember && prefs.x >= 0 && prefs.y >= 0) {
        modal.style.left = Math.min(prefs.x, window.innerWidth - 200) + "px";
        modal.style.top = Math.min(prefs.y, window.innerHeight - 100) + "px";
    } else {
        modal.style.left = Math.max(0, (window.innerWidth - initW) / 2) + "px";
        modal.style.top = Math.max(0, (window.innerHeight - initH) / 2) + "px";
    }

    // 标题栏
    const titleBar = document.createElement("div");
    titleBar.className = "bli-modal-title";
    titleBar.textContent = mediaType === "video" ? "选择视频" : "选择图片";

    // 关闭按钮
    const closeBtn = document.createElement("button");
    closeBtn.className = "bli-modal-close";
    closeBtn.textContent = "\u00d7";
    closeBtn.onclick = closeModal;

    // 最大化按钮
    const maxBtn = document.createElement("button");
    maxBtn.className = "bli-modal-maximize";
    maxBtn.textContent = "\u25a1"; // □
    maxBtn.title = "最大化";
    let isMaximized = false;
    let restoreRect = null;

    function toggleMaximize() {
        if (isMaximized) {
            // 恢复
            modal.style.left = restoreRect.x + "px";
            modal.style.top = restoreRect.y + "px";
            modal.style.width = restoreRect.w + "px";
            modal.style.height = restoreRect.h + "px";
            maxBtn.textContent = "\u25a1";
            maxBtn.title = "最大化";
            resizeHandle.style.display = "";
            isMaximized = false;
        } else {
            // 保存当前位置
            restoreRect = {
                x: modal.offsetLeft,
                y: modal.offsetTop,
                w: modal.offsetWidth,
                h: modal.offsetHeight,
            };
            // 最大化（留 8px 边距）
            const pad = 8;
            modal.style.left = pad + "px";
            modal.style.top = pad + "px";
            modal.style.width = (window.innerWidth - pad * 2) + "px";
            modal.style.height = (window.innerHeight - pad * 2) + "px";
            maxBtn.textContent = "\u2750";
            maxBtn.title = "还原";
            resizeHandle.style.display = "none";
            isMaximized = true;
        }
    }

    maxBtn.onclick = toggleMaximize;

    // 工具栏
    const toolbar = document.createElement("div");
    toolbar.className = "bli-toolbar";

    // 搜索框
    const searchWrapper = document.createElement("div");
    searchWrapper.className = "bli-search-wrapper";

    const searchInput = document.createElement("input");
    searchInput.type = "text";
    searchInput.className = "bli-search-input";
    searchInput.placeholder = mediaType === "video" ? "搜索视频名称..." : "搜索图片名称...";

    const clearBtn = document.createElement("button");
    clearBtn.className = "bli-search-clear";
    clearBtn.textContent = "\u00d7";
    clearBtn.onclick = () => {
        searchInput.value = "";
        clearBtn.style.display = "none";
        renderMedia();
    };

    searchInput.oninput = () => {
        clearBtn.style.display = searchInput.value ? "block" : "none";
        renderMedia();
    };

    searchWrapper.appendChild(searchInput);
    searchWrapper.appendChild(clearBtn);
    toolbar.appendChild(searchWrapper);

    // 新建文件夹 / 管理模式开关
    const newFolderBtn = document.createElement("button");
    newFolderBtn.className = "bli-tool-btn";
    newFolderBtn.textContent = "新建文件夹";
    newFolderBtn.onclick = doNewFolder;
    toolbar.appendChild(newFolderBtn);

    const manageBtn = document.createElement("button");
    manageBtn.className = "bli-tool-btn";
    manageBtn.textContent = "管理";
    manageBtn.title = "多选、批量删除/移动";
    manageBtn.onclick = () => setManageMode(!manageMode);
    toolbar.appendChild(manageBtn);

    const trashBtn = document.createElement("button");
    trashBtn.className = "bli-tool-btn";
    trashBtn.textContent = "回收站";
    trashBtn.onclick = () => setTrashMode(!trashMode);
    toolbar.appendChild(trashBtn);

    // 预览尺寸下拉
    const previewSelect = document.createElement("select");
    previewSelect.className = "bli-preview-select";
    previewSelect.title = "悬浮预览最大尺寸";
    PREVIEW_SIZES.forEach((size) => {
        const opt = document.createElement("option");
        opt.value = size;
        opt.textContent = "预览 " + size;
        if (size === prefs.previewSize) opt.selected = true;
        previewSelect.appendChild(opt);
    });
    previewSelect.onchange = () => {
        const p = loadPrefs();
        p.previewSize = parseInt(previewSelect.value, 10);
        savePrefs(p);
        hoverPreview.style.setProperty("--bli-preview-max", previewSelect.value);
    };
    toolbar.appendChild(previewSelect);

    // 记住窗口复选框
    const rememberLabel = document.createElement("label");
    rememberLabel.className = "bli-remember-label";
    const rememberCb = document.createElement("input");
    rememberCb.type = "checkbox";
    rememberCb.checked = prefs.remember;
    rememberLabel.appendChild(rememberCb);
    rememberLabel.append("记住窗口");
    rememberCb.onchange = () => {
        const p = loadPrefs();
        if (rememberCb.checked) {
            p.remember = true;
            p.x = modal.offsetLeft;
            p.y = modal.offsetTop;
            p.w = modal.offsetWidth;
            p.h = modal.offsetHeight;
        } else {
            p.remember = false;
        }
        savePrefs(p);
    };
    toolbar.appendChild(rememberLabel);

    // 媒体网格
    const mediaGrid = document.createElement("div");
    mediaGrid.className = "bli-media-grid";

    // 缩放手柄
    const resizeHandle = document.createElement("div");
    resizeHandle.className = "bli-resize-handle";

    // ===== 悬浮预览 =====

    const hoverPreview = document.createElement("div");
    hoverPreview.className = "bli-hover-preview";
    hoverPreview.style.setProperty("--bli-preview-max", String(prefs.previewSize));
    document.body.appendChild(hoverPreview);
    let previewMX = 0, previewMY = 0;

    function positionPreview(mx, my) {
        const gap = 20;
        const pw = hoverPreview.offsetWidth || 200;
        const ph = hoverPreview.offsetHeight || 200;
        let x = mx + gap;
        let y = my + gap;
        if (x + pw > window.innerWidth - 10) x = mx - pw - gap;
        if (y + ph > window.innerHeight - 10) y = my - ph - gap;
        hoverPreview.style.left = Math.max(5, x) + "px";
        hoverPreview.style.top = Math.max(5, y) + "px";
    }

    // ===== 文件管理：状态与接口 =====

    let files = mediaWidget.options && mediaWidget.options.values
        ? mediaWidget.options.values.slice() : [];
    let folders = Array.from(new Set(files.filter((m) => m.includes("/")).map((m) => dirOf(m)))).sort();
    let currentFolder = "";
    let manageMode = false;
    const selected = new Set(); // "f:路径"（文件） / "d:名称"（文件夹）
    const cardEls = new Map();
    let activeDialog = null;
    {
        const curDir = mediaWidget.value ? dirOf(mediaWidget.value) : "";
        const want = curDir || prefs.lastFolder || "";
        if (want && folders.includes(want)) currentFolder = want;
    }

    function showToast(msg) {
        const t = document.createElement("div");
        t.className = "bli-toast";
        t.textContent = msg;
        modal.appendChild(t);
        setTimeout(() => t.remove(), 3500);
    }

    async function bliPost(path, body) {
        const r = await api.fetchApi(path, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
        const data = await r.json().catch(() => ({}));
        if (!r.ok) throw new Error(data.error || ("HTTP " + r.status));
        return data;
    }

    async function refresh() {
        try {
            const r = await api.fetchApi("/bli/list?type=" + mediaType);
            if (!r.ok) throw new Error("HTTP " + r.status);
            const data = await r.json();
            files = data.files;
            folders = data.folders;
            // 同步回 widget，避免 combo 残留已删除/已移动的旧路径
            if (mediaWidget.options) mediaWidget.options.values = files;
        } catch (e) {
            showToast("刷新列表失败：" + e.message);
        }
        if (currentFolder && !folders.includes(currentFolder)) currentFolder = "";
        await loadTrash();
        renderMedia();
    }

    function setWidgetValue(v) {
        mediaWidget.value = v;
        if (mediaWidget.callback) mediaWidget.callback(v);
        if (app.graph) app.graph.setDirtyCanvas(true, true);
    }

    function showDialog({ title, message, content, okText = "确定", danger = false }) {
        return new Promise((resolve) => {
            const layer = document.createElement("div");
            layer.className = "bli-dialog-layer";
            const box = document.createElement("div");
            box.className = "bli-dialog";
            const h = document.createElement("div");
            h.className = "bli-dialog-title";
            h.textContent = title;
            box.appendChild(h);
            if (message) {
                const m = document.createElement("div");
                m.className = "bli-dialog-msg";
                m.textContent = message;
                box.appendChild(m);
            }
            if (content) box.appendChild(content);
            const btns = document.createElement("div");
            btns.className = "bli-dialog-btns";
            const cancel = document.createElement("button");
            cancel.className = "bli-btn";
            cancel.textContent = "取消";
            const ok = document.createElement("button");
            ok.className = "bli-btn" + (danger ? " bli-btn-danger" : " bli-btn-primary");
            ok.textContent = okText;
            btns.appendChild(cancel);
            btns.appendChild(ok);
            box.appendChild(btns);
            layer.appendChild(box);

            const done = (v) => {
                layer.remove();
                activeDialog = null;
                resolve(v);
            };
            activeDialog = { cancel: () => done(false) };
            cancel.onclick = () => done(false);
            ok.onclick = () => done(true);
            layer.onclick = (e) => { if (e.target === layer) done(false); };
            layer.addEventListener("keydown", (e) => {
                e.stopPropagation();
                if (e.key === "Escape") done(false);
                else if (e.key === "Enter" && e.target.tagName !== "SELECT") ok.click();
            });
            overlay.appendChild(layer);
            const first = box.querySelector("input, select");
            (first || ok).focus();
            if (first && first.select) first.select();
        });
    }

    function parseKeys() {
        const out = { files: [], dirs: [] };
        selected.forEach((k) => {
            if (k.startsWith("f:")) out.files.push(k.slice(2));
            else out.dirs.push(k.slice(2));
        });
        return out;
    }

    function folderCount(name) {
        return files.filter((f) => dirOf(f) === name).length;
    }

    function widgetAffected(paths) {
        const cur = mediaWidget.value;
        return !!cur && paths.some((p) => cur === p || cur.startsWith(p + "/"));
    }

    // ===== 文件管理：操作 =====

    async function doDelete(fileList, dirList) {
        const lines = [];
        if (dirList.length) {
            lines.push("文件夹（连同其中全部文件）：");
            dirList.forEach((d) => lines.push("  " + d + "/  （" + folderCount(d) + " 个媒体文件）"));
        }
        if (fileList.length) {
            lines.push("文件 " + fileList.length + " 个：");
            fileList.slice(0, 6).forEach((f) => lines.push("  " + f));
            if (fileList.length > 6) lines.push("  ……");
        }
        lines.push("", "将移入 input/.trash/，可手动找回。");
        const ok = await showDialog({
            title: "确认删除", message: lines.join("\n"), okText: "删除", danger: true,
        });
        if (!ok) return;
        const paths = dirList.concat(fileList);
        try {
            const res = await bliPost("/bli/delete", { paths });
            const hit = widgetAffected(res.deleted);
            selected.clear();
            await refresh();
            if (hit) setWidgetValue(files[0] || "");
            if (res.failed.length) {
                showToast("部分删除失败：" + res.failed[0].path + "（" + res.failed[0].reason + "）");
            }
        } catch (e) {
            showToast("删除失败：" + e.message);
        }
    }

    async function doMove(fileList) {
        if (!fileList.length) return;
        const sel = document.createElement("select");
        sel.className = "bli-dialog-select";
        const targets = [""].concat(folders);
        targets.forEach((f) => {
            const o = document.createElement("option");
            o.value = f;
            o.textContent = f ? f + "/" : "（根目录）";
            sel.appendChild(o);
        });
        const ok = await showDialog({
            title: "移动 " + fileList.length + " 个文件到",
            message: "注意：其他工作流里引用旧路径的节点将找不到文件。",
            content: sel, okText: "移动",
        });
        if (!ok) return;
        try {
            const res = await bliPost("/bli/move", { files: fileList, folder: sel.value });
            const cur = mediaWidget.value;
            const hit = res.moved.find((m) => m.from === cur);
            selected.clear();
            if (hit) setWidgetValue(hit.to);
            await refresh();
            if (res.failed.length) {
                showToast("部分移动失败：" + res.failed[0].path + "（" + res.failed[0].reason + "）");
            }
        } catch (e) {
            showToast("移动失败：" + e.message);
        }
    }

    async function doNewFolder() {
        const input = document.createElement("input");
        input.type = "text";
        input.className = "bli-dialog-input";
        input.placeholder = "文件夹名称";
        const ok = await showDialog({ title: "新建文件夹", content: input, okText: "创建" });
        if (!ok) return;
        try {
            await bliPost("/bli/mkdir", { name: input.value.trim() });
            await refresh();
        } catch (e) {
            showToast("新建失败：" + e.message);
        }
    }

    function startRename(kind, path, nameEl) {
        const isFile = kind === "f";
        const full = isFile ? baseOf(path) : path;
        const dot = isFile ? full.lastIndexOf(".") : -1;
        const stem = dot > 0 ? full.slice(0, dot) : full;
        const ext = dot > 0 ? full.slice(dot) : "";
        const input = document.createElement("input");
        input.type = "text";
        input.className = "bli-rename-input";
        input.value = stem;
        nameEl.replaceWith(input);
        input.focus();
        input.select();
        let finished = false;

        const cancel = () => {
            if (finished) return;
            finished = true;
            input.replaceWith(nameEl);
        };
        const commit = async () => {
            if (finished) return;
            const newName = input.value.trim() + ext;
            if (newName === full) { cancel(); return; }
            finished = true;
            try {
                const res = await bliPost("/bli/rename", { path, name: newName });
                const cur = mediaWidget.value;
                if (isFile && cur === path) {
                    setWidgetValue(res.path);
                } else if (!isFile && cur && cur.startsWith(path + "/")) {
                    setWidgetValue(res.path + cur.slice(path.length));
                }
                selected.clear();
                await refresh();
            } catch (e) {
                input.replaceWith(nameEl);
                showToast("重命名失败：" + e.message);
            }
        };
        input.onkeydown = (e) => {
            e.stopPropagation();
            if (e.key === "Enter") commit();
            else if (e.key === "Escape") cancel();
        };
        input.onblur = cancel;
        input.onclick = (e) => e.stopPropagation();
        input.ondblclick = (e) => e.stopPropagation();
    }

    // ===== 管理栏 / 面包屑 =====

    const crumbBar = document.createElement("div");
    crumbBar.className = "bli-crumb";

    function goFolder(name) {
        currentFolder = name;
        const p = loadPrefs();
        p.lastFolder = name;
        savePrefs(p);
        renderMedia();
        mediaGrid.scrollTop = 0;
    }

    function renderCrumb() {
        crumbBar.innerHTML = "";
        if (trashMode) {
            const back = document.createElement("span");
            back.className = "bli-crumb-link";
            back.textContent = "全部";
            back.onclick = () => setTrashMode(false);
            const cur = document.createElement("span");
            cur.className = "bli-crumb-current";
            cur.textContent = "回收站";
            const sep = document.createElement("span");
            sep.textContent = "  \u203a  ";
            [back, sep, cur].forEach((el) => crumbBar.appendChild(el));
            return;
        }
        const searching = !!searchInput.value.trim();
        const root = document.createElement("span");
        root.textContent = "全部";
        if (currentFolder && !searching) {
            root.className = "bli-crumb-link";
            root.onclick = () => goFolder("");
        }
        crumbBar.appendChild(root);
        if (searching) {
            const s = document.createElement("span");
            s.className = "bli-crumb-hint";
            s.textContent = "  ›  搜索结果（所有文件夹）";
            crumbBar.appendChild(s);
        } else if (currentFolder) {
            const sep = document.createElement("span");
            sep.textContent = "  ›  ";
            const cur = document.createElement("span");
            cur.className = "bli-crumb-current";
            cur.textContent = currentFolder;
            crumbBar.appendChild(sep);
            crumbBar.appendChild(cur);
        }
    }

    const manageBar = document.createElement("div");
    manageBar.className = "bli-manage-bar";
    const manageInfo = document.createElement("span");
    manageInfo.className = "bli-manage-info";
    function mkBtn(text, onclick) {
        const b = document.createElement("button");
        b.className = "bli-btn";
        b.textContent = text;
        b.onclick = onclick;
        return b;
    }
    const btnAll = mkBtn("全选", () => {
        const view = visibleFileKeys();
        const allOn = view.length && view.every((k) => selected.has(k));
        view.forEach((k) => (allOn ? selected.delete(k) : selected.add(k)));
        renderMedia();
    });
    const btnMove = mkBtn("移动到…", () => doMove(parseKeys().files));
    const btnDel = mkBtn("删除所选", () => {
        const s = parseKeys();
        doDelete(s.files, s.dirs);
    });
    btnDel.classList.add("bli-btn-danger");
    const btnClear = mkBtn("取消选择", () => { selected.clear(); renderMedia(); });
    [manageInfo, btnAll, btnMove, btnDel, btnClear].forEach((el) => manageBar.appendChild(el));

    function updateManageBar() {
        const s = parseKeys();
        manageInfo.textContent = "已选 " + s.files.length + " 个文件"
            + (s.dirs.length ? "、" + s.dirs.length + " 个文件夹" : "");
        btnMove.disabled = s.files.length === 0;
        btnDel.disabled = selected.size === 0;
        btnClear.disabled = selected.size === 0;
    }

    function visibleFileKeys() {
        const term = searchInput.value.toLowerCase().trim();
        const list = term
            ? files.filter((m) => m.toLowerCase().includes(term))
            : files.filter((m) => dirOf(m) === currentFolder);
        return list.map((m) => "f:" + m);
    }

    function setManageMode(on) {
        manageMode = on;
        selected.clear();
        manageBtn.classList.toggle("active", on);
        modal.classList.toggle("bli-manage", on || trashMode);
        manageBar.style.display = on ? "flex" : "none";
        renderMedia();
    }

    // ===== 回收站 =====

    let trashMode = false;
    let trashEntries = [];
    let trashInfo = { count: 0, size: 0 };
    const tSelected = new Set(); // 回收站条目名

    function fmtSize(n) {
        if (n < 1024) return n + " B";
        if (n < 1024 * 1024) return (n / 1024).toFixed(1) + " KB";
        if (n < 1024 * 1024 * 1024) return (n / 1024 / 1024).toFixed(1) + " MB";
        return (n / 1024 / 1024 / 1024).toFixed(2) + " GB";
    }

    function updateTrashBtn() {
        trashBtn.textContent = "回收站" + (trashInfo.count ? " (" + trashInfo.count + ")" : "");
        trashBtn.title = "回收站共 " + trashInfo.count + " 项，占用 " + fmtSize(trashInfo.size);
    }

    async function loadTrash() {
        try {
            const r = await api.fetchApi("/bli/trash/list?type=" + mediaType);
            if (!r.ok) throw new Error("HTTP " + r.status);
            const data = await r.json();
            trashEntries = data.entries;
            trashInfo = { count: data.total_count, size: data.total_size };
            updateTrashBtn();
        } catch (e) {
            showToast("读取回收站失败：" + e.message);
        }
    }

    const trashBar = document.createElement("div");
    trashBar.className = "bli-manage-bar";
    trashBar.style.display = "none";
    const trashInfoEl = document.createElement("span");
    trashInfoEl.className = "bli-manage-info";
    const tBtnAll = mkBtn("全选", () => {
        const view = trashView();
        const allOn = view.length && view.every((e) => tSelected.has(e.name));
        view.forEach((e) => (allOn ? tSelected.delete(e.name) : tSelected.add(e.name)));
        renderMedia();
    });
    const tBtnRestore = mkBtn("还原", () => trashRestore());
    const tBtnPurge = mkBtn("彻底删除", () => trashPurge(false));
    tBtnPurge.classList.add("bli-btn-danger");
    const tBtnEmpty = mkBtn("清空回收站", () => trashPurge(true));
    tBtnEmpty.classList.add("bli-btn-danger");
    const tBtnBack = mkBtn("返回", () => setTrashMode(false));
    [trashInfoEl, tBtnAll, tBtnRestore, tBtnPurge, tBtnEmpty, tBtnBack]
        .forEach((el) => trashBar.appendChild(el));

    function trashView() {
        const term = searchInput.value.toLowerCase().trim();
        return trashEntries.filter((e) => !term
            || e.orig.toLowerCase().includes(term) || e.name.toLowerCase().includes(term));
    }

    function updateTrashBar() {
        trashInfoEl.textContent = "已选 " + tSelected.size + " 项  ·  回收站共 "
            + trashInfo.count + " 项（" + fmtSize(trashInfo.size) + "）";
        tBtnRestore.disabled = tSelected.size === 0;
        tBtnPurge.disabled = tSelected.size === 0;
        tBtnEmpty.disabled = trashInfo.count === 0;
    }

    async function setTrashMode(on) {
        if (on && manageMode) setManageMode(false);
        trashMode = on;
        tSelected.clear();
        trashBtn.classList.toggle("active", on);
        manageBtn.style.display = on ? "none" : "";
        newFolderBtn.style.display = on ? "none" : "";
        modal.classList.toggle("bli-manage", on || manageMode);
        manageBar.style.display = !on && manageMode ? "flex" : "none";
        trashBar.style.display = on ? "flex" : "none";
        renderMedia();
        if (on) {
            await loadTrash();
            renderMedia();
        }
    }

    async function trashRestore() {
        const names = Array.from(tSelected);
        if (!names.length) return;
        try {
            const res = await bliPost("/bli/trash/restore", { names });
            tSelected.clear();
            await refresh();
            if (res.failed.length) {
                showToast("部分还原失败：" + res.failed[0].path + "（" + res.failed[0].reason + "）");
            }
        } catch (e) {
            showToast("还原失败：" + e.message);
        }
    }

    async function trashPurge(all) {
        const names = Array.from(tSelected);
        if (!all && !names.length) return;
        const ok = await showDialog({
            title: all ? "清空回收站" : "彻底删除",
            message: (all
                ? "将永久删除回收站中全部 " + trashInfo.count + " 项（" + fmtSize(trashInfo.size) + "）。"
                : "将永久删除所选 " + names.length + " 项。") + "\n此操作不可恢复。",
            okText: all ? "清空" : "彻底删除",
            danger: true,
        });
        if (!ok) return;
        try {
            const res = await bliPost("/bli/trash/purge", all ? { all: true } : { names });
            tSelected.clear();
            await refresh();
            if (res.failed.length) {
                showToast("部分删除失败：" + res.failed[0].path + "（" + res.failed[0].reason + "）");
            }
        } catch (e) {
            showToast("删除失败：" + e.message);
        }
    }

    function bindTrashHover(item, entry, url) {
        item.addEventListener("mouseenter", (e) => {
            previewMX = e.clientX;
            previewMY = e.clientY;
            hoverPreview.innerHTML = "";
            const info = document.createElement("div");
            info.className = "bli-hover-preview-info";
            info.textContent = entry.orig;
            let el;
            if (mediaType === "video") {
                el = document.createElement("video");
                el.muted = true;
                el.autoplay = true;
                el.loop = true;
            } else {
                el = document.createElement("img");
                el.onload = () => {
                    info.textContent = entry.orig + "  \u00b7  " + el.naturalWidth + " \u00d7 " + el.naturalHeight;
                    positionPreview(previewMX, previewMY);
                };
            }
            el.src = url;
            hoverPreview.appendChild(el);
            hoverPreview.appendChild(info);
            positionPreview(previewMX, previewMY);
            requestAnimationFrame(() => hoverPreview.classList.add("visible"));
        });
        item.addEventListener("mousemove", (e) => {
            previewMX = e.clientX;
            previewMY = e.clientY;
            positionPreview(previewMX, previewMY);
        });
        item.addEventListener("mouseleave", () => hoverPreview.classList.remove("visible"));
    }

    function renderTrash(term) {
        // 清理已不存在的选中项
        const alive = new Set(trashEntries.map((e) => e.name));
        tSelected.forEach((n) => { if (!alive.has(n)) tSelected.delete(n); });
        const list = trashView();
        updateTrashBar();

        if (!list.length) {
            const msg = document.createElement("div");
            msg.className = "bli-empty-message";
            msg.textContent = term ? "没有找到匹配的条目" : "回收站是空的";
            mediaGrid.appendChild(msg);
            return;
        }

        list.forEach((entry) => {
            const item = document.createElement("div");
            item.className = "bli-media-item" + (tSelected.has(entry.name) ? " checked" : "");

            const preview = document.createElement("div");
            preview.className = "bli-media-preview";
            const url = "/view?filename=" + encodeURIComponent(entry.name)
                + "&subfolder=.trash&type=input";
            if (entry.kind === "folder") {
                preview.classList.add("bli-folder-icon");
                preview.textContent = "\uD83D\uDCC1";
            } else if (mediaType === "video") {
                const vid = document.createElement("video");
                vid.src = url;
                vid.muted = true;
                preview.appendChild(vid);
            } else {
                const img = document.createElement("img");
                img.src = url;
                preview.appendChild(img);
            }

            const nameBox = document.createElement("div");
            nameBox.className = "bli-filename-container";
            const nameEl = document.createElement("div");
            nameEl.className = "bli-filename";
            nameEl.textContent = entry.kind === "folder"
                ? entry.orig + "/  (" + entry.count + ")" : entry.orig;
            const meta = document.createElement("div");
            meta.className = "bli-trash-meta";
            meta.textContent = new Date(entry.at * 1000).toLocaleString() + "  ·  " + fmtSize(entry.size);
            nameBox.appendChild(nameEl);
            nameBox.appendChild(meta);

            const cb = document.createElement("div");
            cb.className = "bli-card-check";

            item.appendChild(preview);
            item.appendChild(nameBox);
            item.appendChild(cb);
            item.onclick = () => {
                if (tSelected.has(entry.name)) tSelected.delete(entry.name);
                else tSelected.add(entry.name);
                item.classList.toggle("checked", tSelected.has(entry.name));
                updateTrashBar();
            };
            if (entry.kind === "file") bindTrashHover(item, entry, url);
            mediaGrid.appendChild(item);
        });
    }

    // ===== 渲染媒体列表 =====

    function makeActions(kind, path, nameEl) {
        const box = document.createElement("div");
        box.className = "bli-card-actions";
        const ren = document.createElement("button");
        ren.textContent = "\u270E";
        ren.title = "重命名";
        ren.onclick = (e) => { e.stopPropagation(); startRename(kind, path, nameEl); };
        const del = document.createElement("button");
        del.textContent = "\u2715";
        del.title = "删除（移入回收目录）";
        del.className = "bli-act-del";
        del.onclick = (e) => {
            e.stopPropagation();
            if (kind === "d") doDelete([], [path]); else doDelete([path], []);
        };
        box.appendChild(ren);
        box.appendChild(del);
        return box;
    }

    function addCheck(item, key) {
        const cb = document.createElement("div");
        cb.className = "bli-card-check";
        item.appendChild(cb);
        item.dataset.key = key;
        cardEls.set(key, item);
        if (selected.has(key)) item.classList.add("checked");
    }

    function toggleSelect(key, item) {
        if (selected.has(key)) selected.delete(key); else selected.add(key);
        item.classList.toggle("checked", selected.has(key));
        updateManageBar();
    }

    function renderMedia() {
        const term = searchInput.value.toLowerCase().trim();
        const scrollPos = mediaGrid.scrollTop;
        mediaGrid.innerHTML = "";
        cardEls.clear();
        hoverPreview.classList.remove("visible");
        renderCrumb();
        if (trashMode) { renderTrash(term); return; }

        // 清理已不存在的选中项
        selected.forEach((k) => {
            const p = k.slice(2);
            if (k.startsWith("f:") ? !files.includes(p) : !folders.includes(p)) selected.delete(k);
        });
        updateManageBar();

        const searching = !!term;
        const viewFiles = searching
            ? files.filter((m) => m.toLowerCase().includes(term))
            : files.filter((m) => dirOf(m) === currentFolder);
        const viewFolders = !searching && !currentFolder ? folders : [];

        if (!viewFiles.length && !viewFolders.length) {
            const msg = document.createElement("div");
            msg.className = "bli-empty-message";
            msg.textContent = searching
                ? "没有找到匹配的媒体"
                : (files.length || folders.length)
                    ? "这个文件夹是空的"
                    : (mediaType === "video" ? "没有找到视频文件" : "没有找到图片文件");
            mediaGrid.appendChild(msg);
            return;
        }

        viewFolders.forEach((name) => {
            const key = "d:" + name;
            const item = document.createElement("div");
            item.className = "bli-media-item bli-folder-item";
            const icon = document.createElement("div");
            icon.className = "bli-media-preview bli-folder-icon";
            icon.textContent = "\uD83D\uDCC1";
            const nameBox = document.createElement("div");
            nameBox.className = "bli-filename-container";
            const nameEl = document.createElement("div");
            nameEl.className = "bli-filename";
            nameEl.textContent = name + "  (" + folderCount(name) + ")";
            nameBox.appendChild(nameEl);
            item.appendChild(icon);
            item.appendChild(nameBox);
            addCheck(item, key);
            item.appendChild(makeActions("d", name, nameEl));
            item.onclick = () => {
                if (manageMode) toggleSelect(key, item);
                else goFolder(name);
            };
            mediaGrid.appendChild(item);
        });

        viewFiles.forEach((media) => {
            const isSelected = media === mediaWidget.value;
            const url = viewUrl(media);
            const key = "f:" + media;

            const item = document.createElement("div");
            item.className = "bli-media-item" + (isSelected ? " selected" : "");

            // 预览
            const preview = document.createElement("div");
            preview.className = "bli-media-preview";

            if (mediaType === "video") {
                const vid = document.createElement("video");
                vid.src = url;
                vid.muted = true;
                vid.loop = true;
                vid.onmouseover = () => vid.play();
                vid.onmouseout = () => { vid.pause(); vid.currentTime = 0; };
                vid.onerror = () => {
                    const ph = document.createElement("div");
                    ph.className = "bli-video-placeholder";
                    ph.textContent = "视频";
                    vid.parentNode.replaceChild(ph, vid);
                };
                preview.appendChild(vid);
            } else {
                const img = document.createElement("img");
                img.src = url;
                img.onerror = () => {
                    img.src = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAiIGhlaWdodD0iODAiIHZpZXdCb3g9IjAgMCA4MCA4MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iODAiIGhlaWdodD0iODAiIGZpbGw9IiMzMzMiLz48Y2lyY2xlIGN4PSI0MCIgY3k9IjQwIiByPSIxMCIgZmlsbD0iIzk5OSIvPjwvc3ZnPg==";
                };
                preview.appendChild(img);
            }

            // 文件名（搜索结果里显示完整相对路径）
            const nameBox = document.createElement("div");
            nameBox.className = "bli-filename-container";
            const nameEl = document.createElement("div");
            nameEl.className = "bli-filename";
            nameEl.textContent = searching ? media : baseOf(media);
            nameBox.appendChild(nameEl);

            item.appendChild(preview);
            item.appendChild(nameBox);
            addCheck(item, key);
            item.appendChild(makeActions("f", media, nameEl));

            // 点击：管理模式下勾选，否则选用并关闭
            item.onclick = () => {
                if (manageMode) { toggleSelect(key, item); return; }
                setWidgetValue(media);
                closeModal();
            };

            // 悬浮大图预览
            item.addEventListener("mouseenter", (e) => {
                previewMX = e.clientX;
                previewMY = e.clientY;
                hoverPreview.innerHTML = "";

                const info = document.createElement("div");
                info.className = "bli-hover-preview-info";
                info.textContent = media;

                if (mediaType === "video") {
                    const vid = document.createElement("video");
                    vid.src = url;
                    vid.muted = true;
                    vid.autoplay = true;
                    vid.loop = true;
                    hoverPreview.appendChild(vid);
                } else {
                    const img = document.createElement("img");
                    img.src = url;
                    img.onload = () => {
                        info.textContent = media + "  \u00b7  " + img.naturalWidth + " \u00d7 " + img.naturalHeight;
                        positionPreview(previewMX, previewMY);
                    };
                    hoverPreview.appendChild(img);
                }

                hoverPreview.appendChild(info);
                positionPreview(previewMX, previewMY);
                requestAnimationFrame(() => hoverPreview.classList.add("visible"));
            });

            item.addEventListener("mousemove", (e) => {
                previewMX = e.clientX;
                previewMY = e.clientY;
                positionPreview(previewMX, previewMY);
            });

            item.addEventListener("mouseleave", () => {
                hoverPreview.classList.remove("visible");
            });

            mediaGrid.appendChild(item);
        });

        mediaGrid.scrollTop = scrollPos;
    }

    // ===== 组装 DOM =====

    modal.appendChild(titleBar);
    modal.appendChild(maxBtn);
    modal.appendChild(closeBtn);
    modal.appendChild(toolbar);
    modal.appendChild(crumbBar);
    modal.appendChild(manageBar);
    modal.appendChild(trashBar);
    modal.appendChild(mediaGrid);
    modal.appendChild(resizeHandle);
    overlay.appendChild(modal);
    document.body.appendChild(overlay);

    // 初始渲染 + 聚焦搜索框
    renderMedia();
    refresh();
    setTimeout(() => searchInput.focus(), 50);

    // ===== 关闭逻辑 =====

    function closeModal() {
        // 保存窗口布局
        const p = loadPrefs();
        if (rememberCb.checked) {
            p.remember = true;
            p.x = modal.offsetLeft;
            p.y = modal.offsetTop;
            p.w = modal.offsetWidth;
            p.h = modal.offsetHeight;
        }
        savePrefs(p);

        hoverPreview.remove();
        overlay.remove();
        document.removeEventListener("keydown", onKeyDown);
        document.removeEventListener("mousemove", onMouseMove);
        document.removeEventListener("mouseup", onMouseUp);
    }

    // 点击遮罩关闭
    overlay.onclick = (e) => {
        if (e.target === overlay) closeModal();
    };

    // ESC 关闭
    function onKeyDown(e) {
        if (activeDialog) {
            if (e.key === "Escape") activeDialog.cancel();
            return;
        }
        if (e.key === "Escape") {
            closeModal();
            return;
        }
        const tag = e.target && e.target.tagName;
        if ((tag === "INPUT" || tag === "SELECT") && e.target !== searchInput) return;
        if (manageMode && e.target !== searchInput && selected.size) {
            if (e.key === "Delete") {
                const sel = parseKeys();
                doDelete(sel.files, sel.dirs);
                return;
            }
            if (e.key === "F2" && selected.size === 1) {
                e.preventDefault();
                const key = Array.from(selected)[0];
                const card = cardEls.get(key);
                const nameEl = card && card.querySelector(".bli-filename");
                if (nameEl) startRename(key.slice(0, 1), key.slice(2), nameEl);
                return;
            }
        }
        // 键盘导航（仅在搜索框未聚焦时，或使用 PageUp/Down 时）
        const scrollAmount = 200;
        switch (e.key) {
            case "ArrowDown":
            case "PageDown":
                e.preventDefault();
                mediaGrid.scrollBy({ top: scrollAmount, behavior: "smooth" });
                break;
            case "ArrowUp":
            case "PageUp":
                e.preventDefault();
                mediaGrid.scrollBy({ top: -scrollAmount, behavior: "smooth" });
                break;
            case "Home":
                if (document.activeElement !== searchInput) {
                    e.preventDefault();
                    mediaGrid.scrollTo({ top: 0, behavior: "smooth" });
                }
                break;
            case "End":
                if (document.activeElement !== searchInput) {
                    e.preventDefault();
                    mediaGrid.scrollTo({ top: mediaGrid.scrollHeight, behavior: "smooth" });
                }
                break;
        }
    }
    document.addEventListener("keydown", onKeyDown);

    // ===== 拖拽 & 缩放 =====

    let isDragging = false, isResizing = false;
    let startX = 0, startY = 0;
    let startLeft = 0, startTop = 0, startWidth = 0, startHeight = 0;
    let rafId = null, lastMoveX = 0, lastMoveY = 0;
    const MIN_W = 400, MIN_H = 300;

    // 拖拽：标题栏 mousedown — 使用移动阈值(4px)，防止双击抖动触发拖拽
    titleBar.addEventListener("mousedown", (e) => {
        if (isMaximized) return;
        if (e.button !== 0) return; // 只响应左键
        startX = e.clientX;
        startY = e.clientY;
        startLeft = modal.offsetLeft;
        startTop = modal.offsetTop;
        let dragStarted = false;

        const onPendingMove = (me) => {
            if (!dragStarted && (Math.abs(me.clientX - startX) > 4 || Math.abs(me.clientY - startY) > 4)) {
                dragStarted = true;
                isDragging = true;
                modal.classList.add("bli-interacting");
                document.body.style.userSelect = "none";
            }
        };
        const onPendingUp = () => {
            document.removeEventListener("mousemove", onPendingMove);
            document.removeEventListener("mouseup", onPendingUp);
        };
        document.addEventListener("mousemove", onPendingMove);
        document.addEventListener("mouseup", onPendingUp);
        e.preventDefault();
    });



    // 缩放：手柄 mousedown
    resizeHandle.onmousedown = (e) => {
        isResizing = true;
        startX = e.clientX;
        startY = e.clientY;
        startWidth = modal.offsetWidth;
        startHeight = modal.offsetHeight;
        modal.classList.add("bli-interacting");
        document.body.style.userSelect = "none";
        e.preventDefault();
        e.stopPropagation();
    };

    // rAF 节流：每帧最多更新一次布局
    function applyInteraction() {
        rafId = null;
        if (isDragging) {
            modal.style.left = (startLeft + lastMoveX - startX) + "px";
            modal.style.top = (startTop + lastMoveY - startY) + "px";
        } else if (isResizing) {
            modal.style.width = Math.max(MIN_W, startWidth + lastMoveX - startX) + "px";
            modal.style.height = Math.max(MIN_H, startHeight + lastMoveY - startY) + "px";
        }
    }

    function onMouseMove(e) {
        if (!isDragging && !isResizing) return;
        lastMoveX = e.clientX;
        lastMoveY = e.clientY;
        if (!rafId) {
            rafId = requestAnimationFrame(applyInteraction);
        }
    }

    function onMouseUp() {
        if (isDragging || isResizing) {
            if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
            applyInteraction();
            modal.classList.remove("bli-interacting");
            document.body.style.userSelect = "";
        }
        isDragging = false;
        isResizing = false;
    }

    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
}