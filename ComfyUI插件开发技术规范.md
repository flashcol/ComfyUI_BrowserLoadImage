# ComfyUI插件开发技术规范

## 1. 技术架构概述

### 1.1 ComfyUI架构设计

ComfyUI采用模块化、基于节点的架构设计，主要由以下几个核心部分组成：

- **后端系统**：基于Python的服务器端，负责节点执行、图像处理和工作流管理
- **前端界面**：基于JavaScript的Web界面，提供节点编辑、连接和工作流可视化
- **插件系统**：允许扩展ComfyUI功能的模块化系统
- **节点系统**：定义各种处理节点的核心系统

![ComfyUI架构图](architecture.png)

### 1.2 插件系统工作流程

1. **插件加载**：ComfyUI启动时扫描custom_nodes目录
2. **节点注册**：插件通过NODE_CLASS_MAPPINGS注册自定义节点
3. **前端扩展**：通过registerExtension机制扩展前端功能
4. **节点执行**：工作流执行时调用节点的处理函数

## 2. 核心API接口

### 2.1 后端API

#### 2.1.1 节点定义接口

```python
# 节点类必须实现的接口
class CustomNode:
    # 定义节点输入类型
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),  # 必需输入
            },
            "optional": {
                "option": ("STRING", {"default": "default"}),  # 可选输入
            }
        }
    
    # 定义节点输出类型
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    
    # 定义节点功能和分类
    FUNCTION = "process"  # 处理函数名称
    CATEGORY = "image"    # 节点分类
    
    # 节点处理函数
    def process(self, image, option="default"):
        # 处理逻辑
        return (processed_image, mask)
```

#### 2.1.2 插件注册接口

```python
# 在__init__.py中注册节点
NODE_CLASS_MAPPINGS = {
    "CustomNodeName": CustomNode
}

# 定义节点显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "CustomNodeName": "User Friendly Name"
}

# 注册Web目录（用于前端资源）
WEB_DIRECTORY = os.path.join(os.path.dirname(os.path.realpath(__file__)), "web")

def get_web_directories():
    return [WEB_DIRECTORY]
```

### 2.2 前端API

#### 2.2.1 扩展注册接口

```javascript
// 注册前端扩展
app.registerExtension({
    name: "ExtensionName",
    
    // 节点定义前的处理
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "CustomNodeName") {
            // 扩展节点行为
        }
    },
    
    // 节点创建后的处理
    async nodeCreated(node) {
        // 节点创建后的自定义行为
    }
});
```

#### 2.2.2 UI组件接口

```javascript
// 创建自定义UI组件
class CustomComponent {
    constructor() {
        this.element = document.createElement("div");
        // 初始化组件
    }
    
    // 组件方法
    setValue(value) {
        // 设置值
    }
    
    getValue() {
        // 获取值
        return value;
    }
}
```

## 3. 图片加载插件相关API

### 3.1 图片扫描和加载API

#### 3.1.1 文件路径管理

```python
import folder_paths

# 获取输入目录
input_dir = folder_paths.get_input_directory()

# 获取完整文件路径
image_path = folder_paths.get_annotated_filepath(relative_path)
```

#### 3.1.2 图片加载和处理

```python
from PIL import Image, ImageOps
import numpy as np
import torch

# 加载图片
image = Image.open(image_path)
image = ImageOps.exif_transpose(image)  # 处理EXIF方向信息
image = image.convert("RGB")

# 转换为张量
image_tensor = np.array(image).astype(np.float32) / 255.0
image_tensor = torch.from_numpy(image_tensor)[None,]

# 提取掩码（如果有Alpha通道）
if 'A' in image.getbands():
    mask = np.array(image.getchannel('A')).astype(np.float32) / 255.0
    mask = 1. - torch.from_numpy(mask)[None,]
else:
    mask = torch.zeros((1, image_tensor.shape[1], image_tensor.shape[2]), dtype=torch.float32)
```

### 3.2 前端图片浏览API

#### 3.2.1 缩略图加载

```javascript
// 加载缩略图
async function loadThumbnail(imagePath) {
    const response = await api.fetchApi(`/view?filename=${encodeURIComponent(imagePath)}&type=input&subfolder=`);
    const blob = await response.blob();
    return URL.createObjectURL(blob);
}
```

#### 3.2.2 ComfyUI API接口

```javascript
// 导入ComfyUI API
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

// 获取节点数据
const nodeId = node.id;
const nodeData = app.graph.getNodeById(nodeId);

// 发送API请求
api.fetchApi("/api/endpoint", {
    method: "POST",
    body: JSON.stringify(data)
});
```

## 4. 自定义节点开发规范

### 4.1 节点定义规范

1. **输入类型定义**：
   - 使用INPUT_TYPES类方法定义输入参数
   - 区分required和optional参数
   - 为每个参数指定类型和默认值

2. **输出类型定义**：
   - 使用RETURN_TYPES定义输出类型
   - 使用RETURN_NAMES定义输出名称
   - 确保处理函数返回值与定义一致

3. **节点分类**：
   - 使用CATEGORY指定节点分类
   - 常用分类：image, conditioning, latent, sampling

4. **处理函数**：
   - 函数名必须与FUNCTION属性一致
   - 参数名必须与INPUT_TYPES中定义的一致
   - 返回值必须是元组，与RETURN_TYPES对应

### 4.2 节点UI定制规范

1. **Widget定制**：
   - 在INPUT_TYPES中使用特殊属性定制Widget行为
   - 例如：`"image": (sorted(images), {"image_browser": True})`

2. **节点外观定制**：
   - 通过扩展节点的drawNode方法定制节点渲染
   - 可添加预览图像、自定义控件等

3. **交互行为定制**：
   - 通过扩展节点的onNodeCreated方法定制节点创建行为
   - 可添加自定义事件处理、动态UI更新等

## 5. UI集成方式

### 5.1 基本UI集成方法

1. **替换原生Widget**：
   - 找到原始Widget元素
   - 创建自定义UI组件
   - 替换DOM元素

```javascript
// 替换原生Widget
const widget = node.widgets.find(w => w.name === "image");
const container = widget.element.parentElement;
container.innerHTML = "";
container.appendChild(customComponent.element);
```

2. **扩展节点绘制**：
   - 扩展节点的drawNode方法
   - 在原始绘制后添加自定义绘制

```javascript
const originalDrawNode = nodeType.prototype.drawNode;
nodeType.prototype.drawNode = function(ctx) {
    originalDrawNode.apply(this, arguments);
    
    // 自定义绘制代码
    if (this.imgs && this.imgs[0]) {
        const img = this.imgs[0];
        ctx.drawImage(img, x, y, w, h);
    }
};
```

### 5.2 高级UI组件开发

1. **组件生命周期**：
   - 构造函数：初始化DOM元素和事件
   - 更新方法：响应数据变化
   - 销毁方法：清理资源和事件监听

2. **事件处理**：
   - 使用事件委托模式处理大量元素
   - 实现自定义事件通知机制

3. **数据绑定**：
   - 实现setValue/getValue接口
   - 保持UI状态与节点数据同步

## 6. 开发约束和性能要求

### 6.1 开发约束

1. **文件结构约束**：
   - 插件必须放在ComfyUI/custom_nodes目录下
   - 前端资源必须放在插件目录下的web子目录中
   - 必须提供__init__.py作为入口点

2. **命名约束**：
   - 避免与ComfyUI核心模块和其他插件冲突
   - 使用一致的命名前缀

3. **依赖管理**：
   - 明确声明依赖项
   - 提供requirements.txt文件
   - 避免不必要的重量级依赖

### 6.2 性能要求

1. **后端性能**：
   - 图片扫描时间：大目录（1000+图片）<5秒
   - 图片加载时间：单张图片<1秒
   - 内存占用：合理控制，避免内存泄漏

2. **前端性能**：
   - 界面响应时间<200ms
   - 缩略图加载使用懒加载和缓存
   - 大量图片使用分页或虚拟滚动

3. **兼容性要求**：
   - 支持主流浏览器（Chrome, Firefox, Edge, Safari）
   - 支持ComfyUI最新稳定版本
   - 支持Windows, MacOS, Linux平台

## 7. 最佳实践

### 7.1 代码组织最佳实践

1. **模块化设计**：
   - 将功能分解为独立模块
   - 使用类封装相关功能
   - 避免全局状态和变量

2. **错误处理**：
   - 使用try/except捕获异常
   - 提供友好的错误信息
   - 避免插件错误影响整个ComfyUI

3. **资源管理**：
   - 及时释放不再使用的资源
   - 使用上下文管理器（with语句）
   - 实现缓存过期和清理机制

### 7.2 UI开发最佳实践

1. **响应式设计**：
   - 适应不同屏幕尺寸
   - 使用相对单位（%, em）
   - 测试不同分辨率下的显示效果

2. **性能优化**：
   - 减少DOM操作
   - 使用事件委托
   - 实现虚拟滚动或分页

3. **用户体验**：
   - 提供直观的交互反馈
   - 添加适当的加载指示器
   - 支持键盘导航和快捷键

## 8. 常见问题解决方案

### 8.1 图片加载问题

1. **问题**：图片路径解析错误
   **解决方案**：使用`os.path.join`和`os.path.relpath`确保跨平台兼容

2. **问题**：图片格式不支持
   **解决方案**：使用PIL的异常处理，提供友好错误信息

3. **问题**：大图片加载内存溢出
   **解决方案**：实现图片缩放或分块处理

### 8.2 UI集成问题

1. **问题**：自定义UI不显示
   **解决方案**：检查DOM元素挂载点，确保CSS样式正确加载

2. **问题**：事件处理不生效
   **解决方案**：使用事件委托，确保事件绑定在正确的元素上

3. **问题**：样式冲突
   **解决方案**：使用特定前缀避免CSS选择器冲突

### 8.3 性能问题

1. **问题**：大目录扫描缓慢
   **解决方案**：实现增量扫描和缓存机制

2. **问题**：缩略图加载缓慢
   **解决方案**：实现懒加载和预加载策略

3. **问题**：界面响应迟钝
   **解决方案**：使用Web Worker处理耗时操作，避免阻塞主线程

## 9. 参考资源

### 9.1 官方文档

- [ComfyUI GitHub仓库](https://github.com/comfyanonymous/ComfyUI)
- [ComfyUI API文档](https://github.com/comfyanonymous/ComfyUI/wiki)

### 9.2 示例插件

- [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager)
- [ComfyUI Impact Pack](https://github.com/ltdrdata/ComfyUI-Impact-Pack)

### 9.3 开发工具

- [ComfyUI Node Development Template](https://github.com/comfyanonymous/ComfyUI-Custom-Node-Template)
- [ComfyUI Debugging Tools](https://github.com/pythongosssss/ComfyUI-Custom-Scripts)

---

*文档版本：1.0*  
*最后更新：2023年12月5日*