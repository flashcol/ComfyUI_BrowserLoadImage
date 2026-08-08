import { app } from "../../scripts/app.js";

// 添加调试信息
console.log("BrowserLoadImage extension loading...");

// 注册扩展
app.registerExtension({
    name: "ComfyUI.BrowserLoadImage",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // 检查是否是图片节点
        if (nodeData.name === "BrowserLoadImage") {
            console.log("Registering BrowserLoadImage node definition");
            
            // 重写onNodeCreated方法
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const ret = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                
                console.log("BrowserLoadImage node created, adding widgets...");
                
                // 延迟添加widget，确保DOM已准备好
                // setTimeout(() => {
                    addBrowseWidget(this, "image");
                // }, 100);
                
                return ret;

            };
        }
        
        // 检查是否是视频转图片节点
        if (nodeData.name === "BrowserLoadVideoToImage") {
            console.log("Registering BrowserLoadVideoToImage node definition");
            
            // 重写onNodeCreated方法
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const ret = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                
                console.log("BrowserLoadVideoToImage node created, adding widgets...");
                
                // 延迟添加widget，确保DOM已准备好
                // setTimeout(() => {
                    addBrowseWidget(this, "video");
                // }, 100);
                
                return ret;

            };
        }
        
        // 检查是否是标准视频节点
        if (nodeData.name === "BrowserLoadVideoStandard") {
            console.log("Registering BrowserLoadVideoStandard node definition");
            
            // 重写onNodeCreated方法
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const ret = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                
                console.log("BrowserLoadVideoStandard node created, adding widgets...");
                
                // 延迟添加widget，确保DOM已准备好
                // setTimeout(() => {
                    addBrowseWidget(this, "video");
                // }, 100);
                
                return ret;

            };
        }
    }
});

// 添加浏览widget到节点
function addBrowseWidget(node, mediaType) {
    // 检查是否已经添加了widget
    if (node._browseWidgetAdded) {
        console.log("Browse widget already added");
        return;
    }
    node._browseWidgetAdded = true;
    
    console.log(`Adding browse widget to BrowserLoad${mediaType === 'video' ? 'Video' : 'Image'} node`);
    
    // 找到对应的widget
    const mediaWidget = node.widgets.find(w => w.name === mediaType);
    if (!mediaWidget) {
        console.log(`${mediaType === 'video' ? 'Video' : 'Image'} widget not found`);
        return;
    }
    
    // 添加浏览按钮widget
    const browseWidget = node.addWidget(
        "button",  // widget类型
        mediaType === 'video' ? "浏览视频" : "浏览图片",  // 显示文本
        "browse",   // 名称
        () => {       // 回调函数
            openMediaModal(node, mediaWidget, mediaType);
        }
    );
    
    console.log("Browse widget added successfully");
}

// 打开媒体选择弹窗
function openMediaModal(node, mediaWidget, mediaType) {
    // 如果弹窗已存在，先关闭
    if (window.mediaPreviewModal) {
        window.mediaPreviewModal.remove();
    }
    
    // 创建弹窗
    const modal = document.createElement("div");
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.8);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
    `;
    
    // 创建弹窗内容
    const modalContent = document.createElement("div");
    modalContent.style.cssText = `
        background-color: #2a2a2a;
        border-radius: 8px;
        padding: 20px;
        width: 800px;
        height: 600px;
        overflow: hidden;
        position: relative;
        border: 1px solid #444;
        display: flex;
        flex-direction: column;
    `;
    
    // 标题
    const title = document.createElement("div");
    title.textContent = mediaType === 'video' ? "选择视频" : "选择图片";
    title.style.cssText = `
        color: white;
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 15px;
        text-align: center;
    `;
    
    // 关闭按钮
    const closeButton = document.createElement("button");
    closeButton.textContent = "×";
    closeButton.style.cssText = `
        position: absolute;
        top: 10px;
        right: 10px;
        background: none;
        border: none;
        color: #999;
        font-size: 24px;
        cursor: pointer;
        padding: 0;
        width: 30px;
        height: 30px;
    `;
    closeButton.onclick = () => {
        modal.remove();
        window.mediaPreviewModal = null;
    };
    
    // 搜索框容器
    const searchContainer = document.createElement("div");
    searchContainer.style.cssText = `
        margin-bottom: 15px;
        position: relative;
    `;
    
    // 搜索框
    const searchInput = document.createElement("input");
    searchInput.type = "text";
    searchInput.placeholder = mediaType === 'video' ? "搜索视频名称..." : "搜索图片名称...";
    searchInput.style.cssText = `
        width: 100%;
        padding: 8px 12px;
        background-color: #333;
        border: 1px solid #555;
        border-radius: 4px;
        color: white;
        font-size: 14px;
        outline: none;
        box-sizing: border-box;
    `;
    searchInput.onfocus = () => {
        searchInput.style.borderColor = '#666';
    };
    searchInput.onblur = () => {
        searchInput.style.borderColor = '#555';
    };
    
    // 清除搜索按钮
    const clearButton = document.createElement("button");
    clearButton.textContent = "×";
    clearButton.style.cssText = `
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
        width: 20px;
        height: 20px;
        display: none;
    `;
    clearButton.onclick = () => {
        searchInput.value = '';
        clearButton.style.display = 'none';
        filterMedia();
    };
    
    // 监听搜索输入
    searchInput.oninput = () => {
        clearButton.style.display = searchInput.value ? 'block' : 'none';
        filterMedia();
    };
    
    searchContainer.appendChild(searchInput);
    searchContainer.appendChild(clearButton);
    
    // 媒体网格
    const mediaGrid = document.createElement("div");
    mediaGrid.style.cssText = `
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
        gap: 12px;
        flex: 1;
        overflow-y: scroll;
        padding: 10px;
        border: 1px solid #444;
        border-radius: 4px;
        scrollbar-width: thin;
        scrollbar-color: #666 #333;
    `;
    
    // 添加Webkit滚动条样式
    const style = document.createElement('style');
    style.textContent = `
        .media-grid::-webkit-scrollbar {
            width: 12px;
        }
        .media-grid::-webkit-scrollbar-track {
            background: #333;
            border-radius: 6px;
        }
        .media-grid::-webkit-scrollbar-thumb {
            background: #666;
            border-radius: 6px;
            border: 2px solid #333;
        }
        .media-grid::-webkit-scrollbar-thumb:hover {
            background: #777;
        }
        .media-grid::-webkit-scrollbar-thumb:active {
            background: #555;
        }
    `;
    document.head.appendChild(style);
    mediaGrid.className = 'media-grid';
    
    // 获取所有可用媒体
    const availableMedia = mediaWidget.options ? mediaWidget.options.values : [];
    console.log(`Available ${mediaType}s for modal:`, availableMedia);
    
    // 过滤和渲染媒体的函数
    function filterMedia() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        
        // 保存当前滚动位置
        const scrollTop = mediaGrid.scrollTop;
        
        // 清空网格
        mediaGrid.innerHTML = '';
        
        // 过滤媒体
        const filteredMedia = searchTerm 
            ? availableMedia.filter(media => media.toLowerCase().includes(searchTerm))
            : availableMedia;
        
        if (!availableMedia || availableMedia.length === 0) {
            const emptyMessage = document.createElement("div");
            emptyMessage.style.cssText = `
                color: #999;
                font-size: 14px;
                grid-column: 1/-1;
                text-align: center;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 200px;
            `;
            emptyMessage.textContent = `没有找到${mediaType === 'video' ? '视频' : '图片'}文件`;
            mediaGrid.appendChild(emptyMessage);
        } else if (filteredMedia.length === 0) {
            const emptyMessage = document.createElement("div");
            emptyMessage.style.cssText = `
                color: #999;
                font-size: 14px;
                grid-column: 1/-1;
                text-align: center;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 200px;
            `;
            emptyMessage.textContent = "没有找到匹配的媒体";
            mediaGrid.appendChild(emptyMessage);
        } else {
            // 添加媒体
            filteredMedia.forEach((media, index) => {
                const isSelected = media === mediaWidget.value;
                const mediaUrl = `/view?filename=${encodeURIComponent(media)}&subfolder=&type=input`;
                
                const mediaItem = document.createElement("div");
                mediaItem.style.cssText = `
                    background-color: ${isSelected ? '#444' : '#333'};
                    border: ${isSelected ? '2px solid #666' : '1px solid #555'};
                    border-radius: 6px;
                    padding: 10px;
                    cursor: pointer;
                    text-align: center;
                    transition: all 0.2s ease;
                    display: flex;
                    flex-direction: column;
                    min-height: 200px;
                `;
                mediaItem.onmouseover = () => {
                    mediaItem.style.backgroundColor = '#3a3a3a';
                    mediaItem.style.transform = 'scale(1.02)';
                };
                mediaItem.onmouseout = () => {
                    mediaItem.style.backgroundColor = isSelected ? '#444' : '#333';
                    mediaItem.style.transform = 'scale(1)';
                };
                
                // 创建媒体容器
                const mediaContainer = document.createElement("div");
                mediaContainer.style.cssText = `
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: 8px;
                    min-height: 150px;
                `;
                
                if (mediaType === 'video') {
                    // 对于视频，创建视频元素
                    const videoElement = document.createElement("video");
                    videoElement.src = mediaUrl;
                    videoElement.style.cssText = `
                        max-width: 140px;
                        max-height: 140px;
                        width: auto;
                        height: auto;
                        object-fit: contain;
                        border-radius: 4px;
                        border: 1px solid #555;
                    `;
                    videoElement.muted = true;
                    videoElement.loop = true;
                    videoElement.onmouseover = () => {
                        videoElement.play();
                    };
                    videoElement.onmouseout = () => {
                        videoElement.pause();
                        videoElement.currentTime = 0;
                    };
                    videoElement.onerror = () => {
                        // 视频加载失败时显示占位符
                        const placeholder = document.createElement("div");
                        placeholder.style.cssText = `
                            width: 140px;
                            height: 140px;
                            background-color: #444;
                            border-radius: 4px;
                            border: 1px solid #555;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: #999;
                            font-size: 12px;
                        `;
                        placeholder.textContent = "视频";
                        videoElement.parentNode.replaceChild(placeholder, videoElement);
                    };
                    mediaContainer.appendChild(videoElement);
                } else {
                    // 对于图片，创建图片元素
                    const imgElement = document.createElement("img");
                    imgElement.src = mediaUrl;
                    imgElement.style.cssText = `
                        max-width: 140px;
                        max-height: 140px;
                        width: auto;
                        height: auto;
                        object-fit: contain;
                        border-radius: 4px;
                        border: 1px solid #555;
                    `;
                    imgElement.onerror = () => {
                        imgElement.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAiIGhlaWdodD0iODAiIHZpZXdCb3g9IjAgMCA4MCA4MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjgwIiBoZWlnaHQ9IjgwIiBmaWxsPSIjMzMzIi8+CjxwYXRoIGQ9Ik0yNSAyNUw1NSA1NUwyNSA1NVYyNVoiIGZpbGw9IiM2NjYiLz4KPGNpcmNsZSBjeD0iNDAiIGN5PSI0MCIgcj0iMTAiIGZpbGw9IiM5OTkiLz4KPC9zdmc+C';
                    };
                    mediaContainer.appendChild(imgElement);
                }
                
                // 创建文件名容器
                const fileNameContainer = document.createElement("div");
                fileNameContainer.style.cssText = `
                    margin-top: auto;
                `;
                
                const fileName = document.createElement("div");
                fileName.style.cssText = `
                    color: ${isSelected ? '#fff' : '#ccc'};
                    font-size: 11px;
                    word-break: break-word;
                    line-height: 1.3;
                    text-align: center;
                    width: 100%;
                    overflow-wrap: break-word;
                    hyphens: auto;
                `;
                fileName.textContent = media;
                
                fileNameContainer.appendChild(fileName);
                
                mediaItem.appendChild(mediaContainer);
                mediaItem.appendChild(fileNameContainer);
                
                mediaItem.onclick = () => {
                    console.log(`Selected ${mediaType}:`, media);
                    
                    // 选择媒体
                    mediaWidget.value = media;
                    if (mediaWidget.callback) {
                        mediaWidget.callback(media);
                    }
                    
                    // 关闭弹窗
                    modal.remove();
                    window.mediaPreviewModal = null;
                };
                
                mediaGrid.appendChild(mediaItem);
            });
        }
        
        // 恢复滚动位置
        mediaGrid.scrollTop = scrollTop;
    }
    
    // 初始渲染
    filterMedia();
    
    // 组装弹窗
    modalContent.appendChild(title);
    modalContent.appendChild(closeButton);
    modalContent.appendChild(searchContainer);
    modalContent.appendChild(mediaGrid);
    modal.appendChild(modalContent);
    
    // 点击背景关闭
    modal.onclick = (e) => {
        if (e.target === modal) {
            modal.remove();
            window.mediaPreviewModal = null;
        }
    };
    
    // ESC键关闭
    const escHandler = (e) => {
        if (e.key === 'Escape') {
            modal.remove();
            window.mediaPreviewModal = null;
            document.removeEventListener('keydown', escHandler);
        }
    };
    document.addEventListener('keydown', escHandler);
    
    // 自动聚焦搜索框
    setTimeout(() => {
        searchInput.focus();
    }, 100);
    
    // 添加滚动条拖动优化
    let isScrolling = false;
    mediaGrid.addEventListener('scroll', () => {
        if (!isScrolling) {
            mediaGrid.style.scrollBehavior = 'auto';
            isScrolling = true;
        }
        
        clearTimeout(isScrolling.scrollEndTimeout);
        isScrolling.scrollEndTimeout = setTimeout(() => {
            isScrolling = false;
            mediaGrid.style.scrollBehavior = 'smooth';
        }, 150);
    });
    
    // 添加键盘导航
    modal.addEventListener('keydown', (e) => {
        const scrollAmount = 200; // 每次滚动的像素
        switch(e.key) {
            case 'ArrowDown':
            case 'PageDown':
                e.preventDefault();
                mediaGrid.scrollBy({
                    top: scrollAmount,
                    behavior: 'smooth'
                });
                break;
            case 'ArrowUp':
            case 'PageUp':
                e.preventDefault();
                mediaGrid.scrollBy({
                    top: -scrollAmount,
                    behavior: 'smooth'
                });
                break;
            case 'Home':
                e.preventDefault();
                mediaGrid.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
                break;
            case 'End':
                e.preventDefault();
                mediaGrid.scrollTo({
                    top: mediaGrid.scrollHeight,
                    behavior: 'smooth'
                });
                break;
        }
    });
    
    document.body.appendChild(modal);
    window.mediaPreviewModal = modal;
}

console.log("BrowserLoadImage extension loaded");