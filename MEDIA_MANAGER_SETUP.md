# 📸 图片管理系统部署指南

## 🎯 系统概述

这是一个基于 **Supabase Storage** 的网页版图片管理系统，让您可以：

- ✅ **浏览器直接上传** - 无需使用 Git 命令
- ✅ **拖拽上传** - 支持批量上传图片
- ✅ **分类管理** - 自动按类别组织图片
- ✅ **实时预览** - 上传前预览图片
- ✅ **CDN 加速** - 图片自动通过 CDN 分发
- ✅ **安全管理** - 只有管理员可以上传/删除

---

## 🚀 快速部署（3 步完成）

### 第 1 步：创建 Supabase Storage Bucket

1. 登录 **Supabase Dashboard**: https://supabase.com/dashboard
2. 选择您的项目
3. 左侧菜单 → 点击 **Storage**
4. 点击 **New Bucket** 按钮
5. 填写以下信息：
   ```
   Bucket Name: led-images
   Public bucket: ✅ 勾选（重要！）
   File size limit: 5 MB
   Allowed MIME types: image/* （可选）
   ```
6. 点击 **Create bucket**

**✅ 验证**: 您应该能在 Storage 页面看到 `led-images` bucket

---

### 第 2 步：运行 SQL 配置脚本

1. 在 Supabase Dashboard 左侧菜单 → 点击 **SQL Editor**
2. 点击 **New Query**
3. 打开项目文件 `database/setup_storage.sql`
4. **复制全部内容** 到 SQL Editor
5. 点击 **Run** 按钮执行

**执行内容**：
- ✅ 创建 Storage RLS 策略（公开读取、管理员上传/删除）
- ✅ 创建 `image_metadata` 表（存储图片元数据）
- ✅ 创建 `image_categories` 表（图片分类）
- ✅ 创建统计函数和索引

**✅ 验证**: 在 **Table Editor** 中应该能看到 `image_metadata` 和 `image_categories` 两个新表

---

### 第 3 步：访问图片管理后台

1. 部署完成后，访问：
   ```
   https://your-domain.vercel.app/admin/media-manager.html
   ```

2. 使用管理员账号登录

3. 开始上传图片！

---

## 📖 使用指南

### 上传图片

#### 方式 1: 拖拽上传（推荐）
1. 选择分类（产品图片、案例图片、证书等）
2. 将图片文件直接拖拽到虚线框内
3. 预览图片
4. 点击 **上传全部**

#### 方式 2: 点击选择
1. 选择分类
2. 点击 **点击选择文件**
3. 在文件选择器中选择图片
4. 点击 **上传全部**

### 图片要求

- **支持格式**: JPG, PNG, WebP, GIF
- **文件大小**: 最大 5MB
- **建议尺寸**:
  - 产品主图: 800x600
  - 案例图片: 1200x800
  - 背景图: 1920x1080
  - Logo: 300x100 (PNG 透明)

### 管理图片

#### 查看图片
- 点击分类按钮过滤图片
- 使用搜索框查找图片
- 查看统计信息（总数、大小等）

#### 复制图片 URL
1. 找到要使用的图片
2. 点击 **复制** 按钮
3. URL 已复制到剪贴板
4. 可以在网页中使用这个 URL

#### 删除图片
1. 点击图片查看详情
2. 点击 **删除** 按钮
3. 确认删除

---

## 🗂️ 图片分类说明

| 分类 | 用途 | 示例 |
|------|------|------|
| **产品图片** | LED 显示屏产品照片 | 室外屏、小间距、租赁屏 |
| **案例图片** | 项目案例和应用场景 | 商场、体育场、机场 |
| **证书资质** | 公司证书和资质文件 | CE、FCC、ISO9001 |
| **关于我们** | 公司照片、团队合影 | 厂房、生产线、团队 |
| **解决方案** | 行业解决方案配图 | 零售方案、控制室 |
| **新闻资讯** | 新闻配图 | 展会、发布会 |
| **技术支持** | 技术文档配图 | 安装图、说明图 |
| **背景图片** | 页面背景和 Banner | Hero 背景图 |
| **Logo 图标** | 公司 Logo 和图标 | 主 Logo、白色 Logo |
| **其他** | 其他类型图片 | 未分类图片 |

---

## 🔗 在网页中使用图片

### 方式 1: 直接使用 CDN URL

上传后，每张图片都有一个公开的 CDN URL，例如：
```
https://abc123.supabase.co/storage/v1/object/public/led-images/products/1699999999-abc123.jpg
```

在 HTML 中使用：
```html
<img src="https://abc123.supabase.co/storage/v1/object/public/led-images/products/..."
     alt="产品图片">
```

### 方式 2: 动态加载（未来功能）

可以通过 API 获取分类下的所有图片：
```javascript
const { data } = await supabase
  .from('image_metadata')
  .select('*')
  .eq('category', 'products')
  .eq('is_active', true)
```

---

## 🎨 替换现有占位图片

### 步骤：

1. **打开 IMAGE_CHECKLIST.md** 查看需要替换的图片列表

2. **按优先级上传**：
   - 第一优先级: 首页 + Logo + 5张产品主图 (10张)
   - 第二优先级: 产品详情图 (15-20张)
   - 第三优先级: 证书 + 公司照片 (8-10张)
   - 第四优先级: 案例和其他 (20-30张)

3. **上传图片**：
   - 进入媒体管理器
   - 选择对应分类
   - 上传图片

4. **复制 URL**：
   - 上传完成后，点击复制 URL
   - 记录下 URL

5. **更新网页代码**：
   - 打开对应的 HTML 文件
   - 找到占位图片的 `<img>` 标签
   - 替换 `src` 属性为新的 URL
   - 提交更新到 Git

### 示例：

**旧代码** (index.html:120):
```html
<img src="https://via.placeholder.com/800x600" alt="LED显示屏">
```

**新代码**:
```html
<img src="https://abc123.supabase.co/storage/v1/object/public/led-images/products/outdoor-led-main.jpg"
     alt="室外LED显示屏">
```

---

## 🔧 集成到管理后台导航

为了方便访问，建议将媒体管理器添加到管理后台导航菜单。

### 更新 admin/dashboard.html

在导航菜单中添加：

```html
<nav class="nav flex-column">
    <a class="nav-link active" href="dashboard.html">
        <i class="fas fa-tachometer-alt"></i> 仪表板
    </a>

    <!-- 新增：媒体管理 -->
    <a class="nav-link" href="media-manager.html">
        <i class="fas fa-images"></i> 媒体管理
    </a>

    <a class="nav-link" href="products.html">
        <i class="fas fa-box"></i> 产品管理
    </a>
    <!-- 其他菜单项... -->
</nav>
```

---

## 📊 存储空间管理

### 查看使用情况

在 Supabase Dashboard:
1. 左侧菜单 → **Storage**
2. 点击 `led-images` bucket
3. 查看文件列表和存储使用量

### 免费额度

Supabase 免费计划提供：
- **1GB** 存储空间
- **2GB** 带宽/月

对于约 150 张图片（每张 100-500KB），大约需要 **20-75MB**，完全够用。

### 升级存储

如果需要更多空间，可以升级到 Pro 计划（$25/月）：
- **100GB** 存储空间
- **200GB** 带宽/月

---

## 🔒 安全说明

### RLS 策略

系统已配置以下安全策略：

1. **公开读取**: 任何人都可以查看图片（通过公开 URL）
2. **管理员上传**: 只有已认证的管理员可以上传图片
3. **管理员删除**: 只有超级管理员和管理员可以删除图片

### 文件验证

- 自动验证文件类型（只允许图片）
- 限制文件大小（最大 5MB）
- 使用唯一文件名防止冲突

---

## 🐛 常见问题

### Q1: 上传失败，显示 "Bucket not found"

**解决**: 确保已在 Supabase Dashboard 创建 `led-images` bucket，并且名称完全一致。

### Q2: 上传失败，显示 "Access denied"

**解决**:
1. 确保 bucket 设置为 **Public**
2. 确保已运行 `setup_storage.sql` 脚本
3. 确保已用管理员账号登录

### Q3: 图片上传成功但不显示

**解决**:
1. 检查浏览器控制台是否有 CORS 错误
2. 确认 bucket 设置为 Public
3. 尝试直接访问图片 URL，确认可访问

### Q4: 如何批量删除图片？

**方法 1** (推荐): 在 Supabase Dashboard:
1. Storage → led-images
2. 选择多个文件
3. 点击 Delete

**方法 2**: 在媒体管理器中逐个删除

### Q5: 能否直接替换原来的文件名？

**答**: 系统自动生成唯一文件名（`timestamp-random.ext`）防止冲突。原始文件名保存在 `image_metadata` 表中。

---

## 📈 下一步优化

完成图片上传后，可以继续 **Phase 2 性能优化**：

1. ✅ **自动 WebP 转换** - 减少 60% 文件大小
2. ✅ **响应式图片** - 根据设备加载不同尺寸
3. ✅ **懒加载** - 提升页面加载速度
4. ✅ **CDN 缓存优化** - 更快的全球访问速度

详见 `PHASE2_PLAN.md`

---

## 📞 需要帮助？

如果遇到问题：

1. 检查 Supabase Dashboard 的 Logs（左侧菜单 → Logs）
2. 查看浏览器控制台的错误信息
3. 确认所有部署步骤都已完成
4. 联系技术支持

---

## ✅ 部署检查清单

部署前请确认：

- [ ] Supabase Storage bucket `led-images` 已创建
- [ ] Bucket 设置为 Public
- [ ] `setup_storage.sql` 已在 SQL Editor 中执行
- [ ] `image_metadata` 和 `image_categories` 表已创建
- [ ] 代码已提交并推送到 Git
- [ ] Vercel 已自动部署完成
- [ ] 能访问 `/admin/media-manager.html`
- [ ] 管理员账号可以登录
- [ ] 测试上传一张图片成功

**完成后，您就可以开始替换网站上的占位图片了！** 🎉
