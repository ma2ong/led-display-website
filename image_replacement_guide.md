# 🖼️ 静态网站图片替换指南

## 📋 需要替换的图片清单

### 1. 主页横幅图片
- **文件路径**: `assets/products/led-display-hero.jpg`
- **建议尺寸**: 1200x800px
- **用途**: 首页Hero区域的主要展示图片
- **描述**: 专业LED显示屏解决方案的主图

### 2. 产品分类图片
由于当前使用的是Font Awesome图标，如果您想替换为实际产品图片，需要修改以下部分：

#### 室内LED显示屏
- **当前**: Font Awesome图标 `fas fa-building`
- **建议图片**: `assets/products/indoor-led.jpg` (800x600px)

#### 户外LED显示屏  
- **当前**: Font Awesome图标 `fas fa-sun`
- **建议图片**: `assets/products/outdoor-led.jpg` (800x600px)

#### 租赁LED显示屏
- **当前**: Font Awesome图标 `fas fa-magic`
- **建议图片**: `assets/products/rental-led.jpg` (800x600px)

#### 透明LED显示屏
- **当前**: Font Awesome图标 `fas fa-eye`
- **建议图片**: `assets/products/transparent-led.jpg` (800x600px)

#### 创意LED显示屏
- **当前**: Font Awesome图标 `fas fa-palette`
- **建议图片**: `assets/products/creative-led.jpg` (800x600px)

#### 工业解决方案
- **当前**: Font Awesome图标 `fas fa-industry`
- **建议图片**: `assets/products/industrial-led.jpg` (800x600px)

## 🔧 替换步骤

### 步骤1: 准备图片文件
1. 将您的图片重命名为对应的文件名
2. 确保图片格式为 JPG 或 PNG
3. 优化图片大小（建议每张图片 < 500KB）

### 步骤2: 上传图片到正确位置
```
项目根目录/
├── assets/
│   └── products/
│       ├── led-display-hero.jpg     (必需 - 主页横幅)
│       ├── indoor-led.jpg           (可选 - 室内LED)
│       ├── outdoor-led.jpg          (可选 - 户外LED)
│       ├── rental-led.jpg           (可选 - 租赁LED)
│       ├── transparent-led.jpg      (可选 - 透明LED)
│       ├── creative-led.jpg         (可选 - 创意LED)
│       └── industrial-led.jpg       (可选 - 工业方案)
```

### 步骤3: 修改HTML文件（如果要替换图标为图片）
如果您想将Font Awesome图标替换为实际产品图片，需要修改 `index.html` 文件中的相应部分。

例如，将室内LED的图标替换为图片：

**原代码**:
```html
<div class="product-image bg-light d-flex align-items-center justify-content-center">
    <i class="fas fa-building display-4 text-primary"></i>
</div>
```

**修改为**:
```html
<div class="product-image bg-light">
    <img src="assets/products/indoor-led.jpg" alt="Indoor LED Display" class="img-fluid">
</div>
```

## 📝 图片命名规范

### 建议的文件命名：
- 使用小写字母
- 用连字符分隔单词
- 包含描述性关键词
- 示例：`indoor-led-display.jpg`, `outdoor-billboard-screen.jpg`

### 图片优化建议：
1. **压缩图片**: 使用在线工具如 TinyPNG 压缩图片
2. **选择合适格式**: 
   - 照片使用 JPG
   - 图标/简单图形使用 PNG
3. **响应式考虑**: 准备不同尺寸的图片用于不同设备

## 🚀 快速替换方法

### 方法1: 仅替换主页横幅图片
1. 准备一张 1200x800px 的LED显示屏图片
2. 重命名为 `led-display-hero.jpg`
3. 放入 `assets/products/` 目录
4. 完成！

### 方法2: 完整替换所有产品图片
1. 准备6张产品图片（每个产品分类一张）
2. 按照上述命名规范重命名
3. 放入 `assets/products/` 目录
4. 修改 `index.html` 文件中的相应HTML代码
5. 测试网站显示效果

## ⚠️ 注意事项

1. **图片路径**: 确保图片路径与HTML中引用的路径完全一致
2. **文件大小**: 过大的图片会影响网站加载速度
3. **图片质量**: 确保图片清晰度适合网站展示
4. **版权问题**: 确保使用的图片有合法使用权
5. **备份原文件**: 替换前备份原始文件

## 🔍 测试检查

替换图片后，请检查：
- [ ] 图片是否正常显示
- [ ] 图片加载速度是否合理
- [ ] 在不同设备上的显示效果
- [ ] 图片是否与网站整体风格协调

完成以上步骤后，您的静态网站就会显示您自己的产品图片了！