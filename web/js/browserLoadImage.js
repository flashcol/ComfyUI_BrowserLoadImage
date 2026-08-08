import { app } from "../../scripts/app.js";

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
.bli-search-container {
    padding: 10px 20px;
    position: relative;
    flex-shrink: 0;
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
    right: 28px;
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

    // 弹窗主体（absolute 定位，居中初始化）
    const modal = document.createElement("div");
    modal.className = "bli-modal";
    const initW = 800, initH = 600;
    modal.style.width = initW + "px";
    modal.style.height = initH + "px";
    modal.style.left = Math.max(0, (window.innerWidth - initW) / 2) + "px";
    modal.style.top = Math.max(0, (window.innerHeight - initH) / 2) + "px";

    // 标题栏
    const titleBar = document.createElement("div");
    titleBar.className = "bli-modal-title";
    titleBar.textContent = mediaType === "video" ? "选择视频" : "选择图片";

    // 关闭按钮
    const closeBtn = document.createElement("button");
    closeBtn.className = "bli-modal-close";
    closeBtn.textContent = "\u00d7";
    closeBtn.onclick = closeModal;

    // 搜索框
    const searchContainer = document.createElement("div");
    searchContainer.className = "bli-search-container";

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

    searchContainer.appendChild(searchInput);
    searchContainer.appendChild(clearBtn);

    // 媒体网格
    const mediaGrid = document.createElement("div");
    mediaGrid.className = "bli-media-grid";

    // 缩放手柄
    const resizeHandle = document.createElement("div");
    resizeHandle.className = "bli-resize-handle";

    // ===== 渲染媒体列表 =====

    const availableMedia = mediaWidget.options ? mediaWidget.options.values : [];

    function renderMedia() {
        const term = searchInput.value.toLowerCase().trim();
        const scrollPos = mediaGrid.scrollTop;
        mediaGrid.innerHTML = "";

        const filtered = term
            ? availableMedia.filter((m) => m.toLowerCase().includes(term))
            : availableMedia;

        if (!availableMedia.length || !filtered.length) {
            const msg = document.createElement("div");
            msg.className = "bli-empty-message";
            msg.textContent = !availableMedia.length
                ? (mediaType === "video" ? "没有找到视频文件" : "没有找到图片文件")
                : "没有找到匹配的媒体";
            mediaGrid.appendChild(msg);
            return;
        }

        filtered.forEach((media) => {
            const isSelected = media === mediaWidget.value;
            const url = "/view?filename=" + encodeURIComponent(media) + "&subfolder=&type=input";

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

            // 文件名
            const nameBox = document.createElement("div");
            nameBox.className = "bli-filename-container";
            const nameEl = document.createElement("div");
            nameEl.className = "bli-filename";
            nameEl.textContent = media;
            nameBox.appendChild(nameEl);

            item.appendChild(preview);
            item.appendChild(nameBox);

            // 点击选择
            item.onclick = () => {
                mediaWidget.value = media;
                if (mediaWidget.callback) mediaWidget.callback(media);
                closeModal();
            };

            mediaGrid.appendChild(item);
        });

        mediaGrid.scrollTop = scrollPos;
    }

    // ===== 组装 DOM =====

    modal.appendChild(titleBar);
    modal.appendChild(closeBtn);
    modal.appendChild(searchContainer);
    modal.appendChild(mediaGrid);
    modal.appendChild(resizeHandle);
    overlay.appendChild(modal);
    document.body.appendChild(overlay);

    // 初始渲染 + 聚焦搜索框
    renderMedia();
    setTimeout(() => searchInput.focus(), 50);

    // ===== 关闭逻辑 =====

    function closeModal() {
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
        if (e.key === "Escape") {
            closeModal();
            return;
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

    // 拖拽：标题栏 mousedown
    titleBar.onmousedown = (e) => {
        isDragging = true;
        startX = e.clientX;
        startY = e.clientY;
        startLeft = modal.offsetLeft;
        startTop = modal.offsetTop;
        modal.classList.add("bli-interacting");
        document.body.style.userSelect = "none";
        e.preventDefault();
    };

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