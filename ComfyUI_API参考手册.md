# ComfyUI API参考手册

## 1. 核心API概览

本手册提供ComfyUI插件开发所需的关键API参考，重点关注与图片加载和浏览相关的接口。

## 2. 后端API

### 2.1 节点注册API

| API | 描述 | 示例 |
|-----|------|------|
| `NODE_CLASS_MAPPINGS` | 注册自定义节点类 | `NODE_CLASS_MAPPINGS = {"EnhancedLoadImage": EnhancedLoadImage}` |
| `NODE_DISPLAY_NAME_MAPPINGS` | 定义节点显示名称 | `NODE_DISPLAY_NAME_MAPPINGS = {"EnhancedLoadImage": "Enhanced Load Image"}` |
| `WEB_DIRECTORY` | 定义Web资源目录 | `WEB_DIRECTORY = os.path.join(os.path.dirname(__file__), "web")` |

### 2.2 文件路径API

| API | 描述 | 参数 | 返回值 |
|-----|------|------|--------|
| `folder_paths.get_input_directory()` | 获取输入目录路径 | 无 | 输入目录的绝对路径 |
| `folder_paths.get_output_directory()` | 获取输出目录路径 | 无 | 输出目录的绝对路径 |
| `folder_paths.get_temp_directory()` | 获取临时目录路径 | 无 | 临时目录的绝对路径 |
| `folder_paths.get_annotated_filepath(filename)` | 获取带注释的文件路径 | `filename`: 文件名 | 完整的文件路径 |

### 2.3 图像处理API

| API | 描述 | 参数 | 返回值 |
|-----|------|------|--------|
| `Image.open(path)` | 打开图像文件 | `path`: 图像文件路径 | PIL Image对象 |
| `ImageOps.exif_transpose(image)` | 根据EXIF信息旋转图像 | `image`: PIL Image对象 | 旋转后的PIL Image对象 |
| `np.array(image)` | 将PIL图像转换为NumPy数组 | `image`: PIL Image对象 | NumPy数组 |
| `torch.from_numpy(array)` | 将NumPy数组转换为PyTorch张量 | `array`: NumPy数组 | PyTorch张量 |

### 2.4 节点类API

#### 2.4.1 必需方法和属性

| 方法/属性 | 描述 | 返回值 |
|-----------|------|--------|
| `INPUT_TYPES()` | 定义节点输入类型 | 包含required和optional输入的字典 |
| `RETURN_TYPES` | 定义节点输出类型 | 输出类型的元组 |
| `RETURN_NAMES` | 定义节点输出名称 | 输出名称的元组 |
| `FUNCTION` | 指定处理函数名称 | 字符串 |
| `CATEGORY` | 指定节点分类 | 字符串 |

#### 2.4.2 可选方法和属性

| 方法/属性 | 描述 | 返回值 |
|-----------|------|--------|
| `IS_CHANGED()` | 检查节点是否已更改 | 布尔值或时间戳 |
| `VALIDATE_INPUTS()` | 验证输入参数 | 布尔值 |
| `get_extra_network_info()` | 获取额外网络信息 | 字典 |

## 3. 前端API

### 3.1 扩展注册API

| API | 描述 | 参数 |
|-----|------|------|
| `app.registerExtension(extension)` | 注册前端扩展 | `extension`: 扩展对象 |

### 3.2 扩展对象属性

| 属性 | 描述 | 类型 |
|-----|------|------|
| `name` | 扩展名称 | 字符串 |
| `async beforeRegisterNodeDef(nodeType, nodeData, app)` | 节点定义前的处理 | 异步函数 |
| `async nodeCreated(node)` | 节点创建后的处理 | 异步函数 |
| `async setup()` | 扩展设置 | 异步函数 |

### 3.3 节点UI API

| API | 描述 | 参数 |
|-----|------|------|
| `node.addWidget(type, name, value, callback, options)` | 添加小部件 | 多个参数 |
| `node.widgets` | 获取节点的所有小部件 | 属性 |
| `node.setSize([width, height])` | 设置节点大小 | `[width, height]`: 尺寸数组 |
| `node.serialize_widgets` | 序列化小部件 | 方法 |

### 3.4 ComfyUI API接口

| API | 描述 | 参数 | 返回值 |
|-----|------|------|--------|
| `api.fetchApi(url, options)` | 发送API请求 | `url`: 请求URL, `options`: 请求选项 | Promise |
| `api.getNodeDef(nodeId)` | 获取节点定义 | `nodeId`: 节点ID | 节点定义对象 |
| `api.addEventListener(event, callback)` | 添加事件监听器 | `event`: 事件名称, `callback`: 回调函数 | 无 |

## 4. 图片浏览器API

### 4.1 后端API

| API | 描述 | 参数 | 返回值 |
|-----|------|------|--------|
| `scan_images(directory)` | 扫描目录中的图像 | `directory`: 目录路径 | 图像路径列表 |
| `load_image(image_path)` | 加载图像 | `image_path`: 图像路径 | 图像张量和掩码 |

### 4.2 前端API

| API | 描述 | 参数 | 返回值 |
|-----|------|------|--------|
| `createImageBrowser(node, inputName, inputData)` | 创建图像浏览器 | 多个参数 | 图像浏览器对象 |
| `loadThumbnail(imagePath)` | 加载缩略图 | `imagePath`: 图像路径 | Promise<URL> |
| `updateImageList(images)` | 更新图像列表 | `images`: 图像路径数组 | 无 |

## 5. 事件系统

### 5.1 后端事件

| 事件 | 描述 | 触发时机 |
|------|------|----------|
| `execution_start` | 执行开始 | 工作流开始执行时 |
| `execution_error` | 执行错误 | 工作流执行出错时 |
| `execution_cached` | 执行缓存 | 使用缓存结果时 |

### 5.2 前端事件

| 事件 | 描述 | 触发时机 | 事件数据 |
|------|------|----------|----------|
| `comfy.nodeCreated` | 节点创建 | 创建新节点时 | 节点对象 |
| `comfy.nodeRemoved` | 节点移除 | 移除节点时 | 节点ID |
| `comfy.workflowLoaded` | 工作流加载 | 加载工作流时 | 工作流数据 |
| `comfy.status` | 状态更新 | 状态变化时 | 状态对象 |

## 6. 数据格式规范

### 6.1 图像数据格式

```python
# 图像张量格式
# 形状: [batch_size, height, width, channels]
# 数据类型: torch.float32
# 值范围: 0.0-1.0
image_tensor = torch.zeros((1, height, width, 3), dtype=torch.float32)

# 掩码张量格式
# 形状: [batch_size, height, width]
# 数据类型: torch.float32
# 值范围: 0.0-1.0 (0表示透明，1表示不透明)
mask_tensor = torch.zeros((1, height, width), dtype=torch.float32)
```

### 6.2 节点定义格式

```python
# 节点定义格式
node_definition = {
    "name": "节点名称",
    "category": "节点分类",
    "input": {
        "required": {
            "参数名": ["参数类型", {"选项": "值"}]
        },
        "optional": {
            "参数名": ["参数类型", {"选项": "值"}]
        }
    },
    "output": ["输出类型1", "输出类型2"],
    "output_name": ["输出名称1", "输出名称2"],
    "output_is_list": [False, False]
}
```

### 6.3 工作流格式

```json
{
  "nodes": [
    {
      "id": 1,
      "type": "EnhancedLoadImage",
      "pos": [100, 100],
      "size": [200, 100],
      "inputs": {},
      "outputs": {},
      "properties": {
        "image": "example.png"
      }
    }
  ],
  "links": [
    {
      "id": 1,
      "origin_id": 1,
      "origin_slot": 0,
      "target_id": 2,
      "target_slot": 0
    }
  ]
}
```

## 7. 错误处理

### 7.1 后端错误处理

```python
# 推荐的错误处理模式
try:
    # 可能引发异常的代码
    image = Image.open(image_path)
except FileNotFoundError:
    print(f"Error: Image file not found: {image_path}")
    # 返回默认图像或错误信息
    return (default_image, default_mask)
except Exception as e:
    print(f"Error loading image {image_path}: {str(e)}")
    # 返回默认图像或错误信息
    return (default_image, default_mask)
```

### 7.2 前端错误处理

```javascript
// 推荐的错误处理模式
async function loadImage(path) {
    try {
        const response = await api.fetchApi(`/view?filename=${encodeURIComponent(path)}`);
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        const blob = await response.blob();
        return URL.createObjectURL(blob);
    } catch (error) {
        console.error(`Error loading image ${path}:`, error);
        // 显示错误UI或返回默认图像
        return defaultImageUrl;
    }
}
```

## 8. 性能优化技巧

### 8.1 后端优化

| 技巧 | 描述 | 示例 |
|------|------|------|
| 缓存扫描结果 | 缓存目录扫描结果以提高性能 | 使用字典存储目录内容和最后修改时间 |
| 延迟加载 | 仅在需要时加载图像 | 在节点执行时而非初始化时加载图像 |
| 图像缩放 | 加载前缩放大图像 | 使用PIL的`thumbnail`方法 |

### 8.2 前端优化

| 技巧 | 描述 | 示例 |
|------|------|------|
| 懒加载 | 仅加载可见区域的缩略图 | 使用IntersectionObserver监控可见性 |
| 缓存缩略图 | 缓存已加载的缩略图 | 使用Map存储缩略图URL |
| 虚拟滚动 | 仅渲染可见区域的项目 | 使用虚拟滚动库或自定义实现 |

## 9. 调试技巧

### 9.1 后端调试

| 技巧 | 描述 | 示例 |
|------|------|------|
| 日志记录 | 使用日志记录关键信息 | `print(f"Loading image: {image_path}")` |
| 检查点 | 在关键点添加检查点 | 在函数开始和结束处添加日志 |
| 异常捕获 | 捕获并记录异常 | 使用try/except并记录详细错误信息 |

### 9.2 前端调试

| 技巧 | 描述 | 示例 |
|------|------|------|
| 控制台日志 | 使用控制台记录信息 | `console.log("Image browser initialized")` |
| 元素检查 | 检查DOM元素 | 使用浏览器开发者工具 |
| 网络监控 | 监控网络请求 | 使用浏览器网络面板 |

---

*API参考手册版本：1.0*  
*最后更新：2023年12月5日*