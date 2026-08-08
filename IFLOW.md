# ComfyUI Browser Load Image 插件

## 项目概述

ComfyUI Browser Load Image 是一个增强型图片加载插件，为 ComfyUI 提供了带有浏览器界面的图片加载节点。该插件完全按照 ComfyUI 原生 Load Image 节点的标准实现，同时添加了图形化图片选择功能，使用户能够通过可视化界面浏览和选择输入文件夹中的图片。

## 技术架构

### 后端架构
- **Python 3.x**：基于 ComfyUI 插件系统
- **PIL (Pillow)**：图像处理和格式转换
- **NumPy**：图像数据处理
- **PyTorch**：图像张量转换
- **folder_paths**：ComfyUI 核心路径管理模块

### 前端架构
- **JavaScript ES6+**：前端交互逻辑
- **CSS3**：样式和动画效果
- **HTML5**：弹窗界面结构

## 项目结构

```
ComfyUI_BrowserLoadImage/
├── __init__.py                 # 插件入口点，注册节点和Web目录
├── config/
│   └── settings.py             # 插件配置设置
├── nodes/
│   ├── __init__.py
│   └── browser_load_image.py   # 核心节点实现
├── web/
│   ├── css/
│   │   └── browserLoadImage.css # 样式文件
│   └── js/
│       └── browserLoadImage.js  # 前端交互逻辑
├── tests/
│   └── test_nodes.py           # 测试文件
├── requirements.txt            # Python依赖
├── package.json               # Node.js构建配置
├── ComfyUI_API参考手册.md       # API参考文档
└── ComfyUI插件开发技术规范.md    # 开发规范文档
```

## 构建和运行

### 开发环境设置

1. **安装 ComfyUI**：
   ```bash
   # 确保已安装 ComfyUI
   git clone https://github.com/comfyanonymous/ComfyUI
   cd ComfyUI
   ```

2. **安装插件**：
   ```bash
   # 将插件复制到 ComfyUI/custom_nodes 目录
   cp -r ComfyUI_BrowserLoadImage ComfyUI/custom_nodes/
   ```

3. **安装依赖**：
   ```bash
   # 安装Python依赖（通常已包含在ComfyUI中）
   cd ComfyUI/custom_nodes/ComfyUI_BrowserLoadImage
   pip install -r requirements.txt
   ```

4. **前端构建**：
   ```bash
   # 安装Node.js依赖并构建
   npm install
   npm run build
   ```

### 开发命令

```bash
# 开发模式（监听文件变化并自动构建）
npm run dev

# 运行测试
npm test

# 代码检查
npm run lint

# 修复代码格式
npm run lint-fix

# 启动本地服务器
npm run serve
```

## 核心功能

### 1. 图片扫描和加载
- 自动扫描 ComfyUI 输入文件夹中的图片
- 支持多种图片格式：JPG, PNG, BMP, WebP, TIFF, GIF
- 处理 EXIF 方向信息
- 自动提取 Alpha 通道作为掩码

### 2. 图形化浏览器界面
- 弹窗式图片选择界面
- 缩略图预览功能
- 图片网格布局，支持大量图片浏览
- 选中状态视觉反馈

### 3. 节点集成
- 完全兼容 ComfyUI 原生 Load Image 节点
- 输出格式：IMAGE 和 MASK 张量
- 支持工作流保存和加载
- 自动检测文件变化

## 开发规范

### 代码风格
- **Python**：遵循 PEP 8 规范
- **JavaScript**：使用 ESLint 配置，ES6+ 语法
- **注释**：使用中文注释，关键逻辑添加说明

### 命名约定
- **节点类**：使用 PascalCase，如 `BrowserLoadImage`
- **函数方法**：使用 snake_case，如 `load_image`
- **变量**：使用 snake_case，语义化命名
- **文件名**：Python 使用 snake_case，JavaScript 使用 camelCase

### 错误处理
- 使用 try/except 捕获异常
- 提供友好的错误信息
- 避免插件错误影响整个 ComfyUI

## API 参考

### 节点定义

```python
class BrowserLoadImage:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (images, {"default": images[0], "image_upload": True}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "load_image"
    CATEGORY = "image"
```

### 前端扩展注册

```javascript
app.registerExtension({
    name: "ComfyUI.BrowserLoadImage",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "BrowserLoadImage") {
            // 自定义节点行为
        }
    }
});
```

## 测试

### 单元测试
```bash
# 运行Python测试
python -m pytest tests/

# 运行JavaScript测试
npm test
```

### 手动测试
1. 在 ComfyUI 中创建 Browser Load Image 节点
2. 在输入文件夹中放置测试图片
3. 点击"浏览图片"按钮测试弹窗功能
4. 验证图片加载和工作流执行

## 性能优化

### 后端优化
- 缓存目录扫描结果
- 延迟加载大图片
- 使用 PIL 的 thumbnail 方法处理大图像

### 前端优化
- 实现缩略图懒加载
- 使用虚拟滚动处理大量图片
- 缓存已加载的缩略图

## 故障排除

### 常见问题
1. **图片不显示**：检查输入文件夹路径和图片格式
2. **弹窗不出现**：检查浏览器控制台错误信息
3. **节点加载失败**：确认插件路径和依赖安装

### 调试技巧
- 启用 DEBUG_MODE 查看详细日志
- 使用浏览器开发者工具检查前端问题
- 检查 ComfyUI 控制台输出

## 贡献指南

1. Fork 项目仓库
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 创建 Pull Request

## 许可证

MIT License - 详见 LICENSE 文件

## 相关资源

- [ComfyUI 官方仓库](https://github.com/comfyanonymous/ComfyUI)
- [ComfyUI 插件开发指南](https://github.com/comfyanonymous/ComfyUI/wiki)
- [PIL/Pillow 文档](https://pillow.readthedocs.io/)
- [PyTorch 文档](https://pytorch.org/docs/)