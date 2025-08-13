# 🔄 Supabase数据库更新执行指南

## 📋 准备工作

1. **访问Supabase控制台**: https://supabase.com/dashboard/project/jirudzbqcxviytcmxegf
2. **确保已登录**您的Supabase账户
3. **准备分步执行**以确保安全

---

## 🛠️ 分步执行指南

### **第1步：更新现有表结构**

1. 在Supabase左侧导航栏点击 "**SQL Editor**"
2. 点击 "**New query**" 创建新查询
3. 复制以下内容到SQL编辑器：

```sql
-- 复制 supabase-step1-tables.sql 的内容
```

4. 点击 **RUN** 执行
5. 确认执行成功（绿色成功提示）

---

### **第2步：创建新表和触发器**

1. 创建新的SQL查询
2. 复制以下内容：

```sql  
-- 复制 supabase-step2-new-tables.sql 的内容
```

3. 点击 **RUN** 执行
4. 确认新表创建成功

---

### **第3步：插入默认数据**

1. 创建新的SQL查询
2. 复制以下内容：

```sql
-- 复制 supabase-step3-data.sql 的内容
```

3. 点击 **RUN** 执行
4. 确认数据插入成功

---

### **第4步：安全策略和性能优化**

1. 创建新的SQL查询
2. 复制以下内容：

```sql
-- 复制 supabase-step4-security.sql 的内容
```

3. 点击 **RUN** 执行
4. 确认所有策略和索引创建成功

---

## ✅ 验证更新成功

### 检查新表
执行以下查询验证新表创建成功：

```sql
-- 检查page_contents表
SELECT * FROM page_contents LIMIT 5;

-- 检查system_settings表  
SELECT * FROM system_settings LIMIT 5;

-- 检查产品表新增字段
SELECT name, category, features, specifications FROM products LIMIT 3;
```

### 检查数据插入
```sql
-- 检查页面内容数据
SELECT COUNT(*) as page_count FROM page_contents;

-- 检查系统设置数据
SELECT COUNT(*) as settings_count FROM system_settings;

-- 检查产品特性数据
SELECT COUNT(*) as products_with_features FROM products WHERE features IS NOT NULL;
```

---

## 🔧 如果遇到问题

### 常见错误解决：

#### **权限错误**
- 确保您有数据库写入权限
- 检查Supabase项目角色设置

#### **表不存在错误**
- 先运行步骤1-2创建必要的表结构
- 确认基础表（products, news, inquiries）已存在

#### **策略冲突错误**
- 删除现有同名策略后再创建
- 检查RLS策略是否正确启用

#### **数据插入失败**
- 检查唯一约束冲突
- 使用 `ON CONFLICT DO NOTHING` 避免重复插入

---

## 📊 更新完成后的数据库结构

### 新增表：
- ✅ `page_contents` - 页面内容管理
- ✅ `system_settings` - 系统设置管理

### 更新的表：
- ✅ `products` - 新增 features, specifications, image_url, updated_at
- ✅ `inquiries` - 新增 phone, country, newsletter, product_interest, updated_at  
- ✅ `news` - 新增 summary, image_url, author, published, updated_at

### 安全策略：
- ✅ 页面内容：公开读取，管理员编辑
- ✅ 系统设置：仅管理员访问
- ✅ 性能索引：优化查询速度

---

## 🎉 完成后确认

更新完成后，您的管理后台将拥有：

1. **页面内容管理** - 8个页面的完整编辑功能
2. **系统设置管理** - 网站基本信息配置
3. **产品管理增强** - 特性和规格详细管理
4. **新闻管理完善** - 摘要、作者、发布状态
5. **询盘管理扩展** - 更多客户信息字段

**🚀 数据库更新完成后，管理后台的所有功能都将正常工作！**

---

## 📞 需要帮助？

如果在执行过程中遇到任何问题：

1. 检查Supabase控制台的错误信息
2. 确认每一步都成功执行
3. 查看浏览器开发者工具的控制台日志
4. 验证数据库表结构是否正确创建

**记住：分步执行，逐步验证，确保每一步都成功！**
