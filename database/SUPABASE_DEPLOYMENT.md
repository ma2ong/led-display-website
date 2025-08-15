# Supabase 数据库部署指南

## 概述
本文档描述如何将项目的数据库更改部署到Supabase。

## 新增的数据库表

本次更新添加了以下数据库表来支持内容管理系统：

1. **page_contents** - 页面内容表，存储所有页面的可编辑内容
2. **page_sections** - 页面区块表，存储页面的动态区块
3. **site_settings** - 网站设置表，存储全局配置
4. **content_history** - 内容历史表，记录所有内容变更
5. **page_metadata** - 页面元数据表，存储SEO相关信息

## 部署方式

### 方式一：使用SQL编辑器（推荐）

1. 登录到你的Supabase项目控制台
2. 进入 **SQL Editor**
3. 复制 `database/create_tables.sql` 文件的内容
4. 粘贴到SQL编辑器中
5. 点击 **RUN** 执行

### 方式二：使用Node.js脚本

1. 在Supabase控制台的 **Settings > API** 中获取 **Service Role Key**
2. 设置环境变量：
   ```bash
   export SUPABASE_SERVICE_KEY=your_service_role_key
   ```
   或在Windows PowerShell中：
   ```powershell
   $env:SUPABASE_SERVICE_KEY="your_service_role_key"
   ```
3. 运行初始化脚本：
   ```bash
   node database/init-supabase.js
   ```

### 方式三：使用Supabase CLI

如果安装了Supabase CLI：
```bash
supabase db push
```

## 验证部署

部署完成后，在Supabase控制台的 **Table Editor** 中应该能看到以下表：
- page_contents
- page_sections  
- site_settings
- content_history
- page_metadata

## 权限配置

数据库表已经配置了行级安全策略（RLS）：
- **公开读取**：匿名用户可以读取启用的内容
- **管理权限**：已认证用户可以进行所有操作

## 预置数据

SQL脚本会自动插入一些默认数据：
- 基础网站设置
- 示例页面内容

## 注意事项

1. **备份数据**：在执行SQL之前，建议备份现有数据
2. **Service Key**：Service Role Key具有完全权限，请妥善保管
3. **RLS策略**：确保启用了行级安全，避免数据泄露
4. **索引优化**：SQL脚本包含了性能优化的索引

## 故障排除

如果遇到问题：

1. **权限错误**：确保使用Service Role Key而不是Anonymous Key
2. **表已存在**：SQL使用了 `IF NOT EXISTS`，重复执行是安全的
3. **连接失败**：检查Supabase URL和密钥配置

## 后续维护

- 定期检查内容历史表的数据量
- 根据需要调整RLS策略
- 监控查询性能，必要时添加索引
