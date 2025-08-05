# 🚀 Supabase + Vercel 一键部署指南

## 概述

本指南将帮您使用现代化的 Supabase + Vercel 架构部署LED网站，实现：
- ✅ 无服务器后端（Supabase）
- ✅ 边缘计算前端（Vercel）
- ✅ 实时数据同步
- ✅ 内置用户认证
- ✅ 自动扩展能力

## 🎯 架构优势

### 传统架构 vs 现代架构

| 特性 | 传统架构 | Supabase + Vercel |
|------|----------|-------------------|
| 服务器管理 | 需要维护服务器 | 完全无服务器 |
| 数据库 | SQLite本地文件 | PostgreSQL云数据库 |
| 扩展性 | 手动扩展 | 自动扩展 |
| 认证系统 | 自建认证 | 内置Auth系统 |
| 实时功能 | 需要WebSocket | 内置实时订阅 |
| 部署复杂度 | 复杂配置 | 一键部署 |
| 成本 | 固定服务器成本 | 按使用量付费 |

## 🛠️ 快速开始

### 方法一：一键部署脚本

```bash
# 运行一键部署脚本
node deploy-supabase-vercel.js
```

### 方法二：手动部署

#### 1. 准备环境

```bash
# 安装依赖
npm install

# 安装CLI工具
npm install -g supabase vercel
```

#### 2. 设置Supabase

```bash
# 初始化Supabase项目
supabase init

# 启动本地开发环境
supabase start

# 应用数据库架构
supabase db reset
```

#### 3. 配置环境变量

创建 `.env.local` 文件：

```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

#### 4. 部署到Vercel

```bash
# 构建项目
npm run build

# 部署到Vercel
vercel --prod
```

## 📊 数据库架构

### 核心表结构

```sql
-- 产品表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    specifications TEXT,
    price DECIMAL(10,2),
    image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 询盘表
CREATE TABLE inquiries (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    company TEXT,
    message TEXT NOT NULL,
    status TEXT DEFAULT 'new',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 新闻表
CREATE TABLE news (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author TEXT DEFAULT 'Admin',
    status TEXT DEFAULT 'published',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 行级安全策略（RLS）

```sql
-- 启用RLS
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE inquiries ENABLE ROW LEVEL SECURITY;
ALTER TABLE news ENABLE ROW LEVEL SECURITY;

-- 产品策略：公开读取，认证用户写入
CREATE POLICY "Products are viewable by everyone" 
ON products FOR SELECT USING (true);

CREATE POLICY "Products are manageable by authenticated users" 
ON products FOR ALL USING (auth.role() = 'authenticated');
```

## 🔐 认证系统

### Supabase Auth集成

```javascript
import { supabase } from '../lib/supabase'

// 登录
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'admin@example.com',
  password: 'your_password'
})

// 获取当前用户
const { data: { user } } = await supabase.auth.getUser()

// 登出
await supabase.auth.signOut()
```

### 用户角色管理

```sql
-- 用户配置表
CREATE TABLE user_profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    username TEXT UNIQUE,
    role TEXT DEFAULT 'admin',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🌐 API端点

### RESTful API设计

```javascript
// 获取产品列表
GET /api/supabase-api?endpoint=products

// 创建新产品
POST /api/supabase-api?endpoint=products

// 更新产品
PUT /api/supabase-api?endpoint=products&id=1

// 删除产品
DELETE /api/supabase-api?endpoint=products&id=1
```

### 实时订阅

```javascript
import { SupabaseRealtime } from '../lib/supabase'

// 订阅询盘更新
const subscription = SupabaseRealtime.subscribeToInquiries((payload) => {
  console.log('新询盘:', payload.new)
})

// 取消订阅
subscription.unsubscribe()
```

## 🚀 部署配置

### Vercel配置

```json
{
  "version": 2,
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_SUPABASE_URL": "@supabase_url",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY": "@supabase_anon_key"
  }
}
```

### 环境变量设置

在Vercel Dashboard中设置：

1. `NEXT_PUBLIC_SUPABASE_URL` - Supabase项目URL
2. `NEXT_PUBLIC_SUPABASE_ANON_KEY` - 匿名访问密钥
3. `SUPABASE_SERVICE_ROLE_KEY` - 服务角色密钥

## 📈 性能优化

### 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_inquiries_status ON inquiries(status);
CREATE INDEX idx_news_status ON news(status);
```

### 缓存策略

```javascript
// 使用Vercel Edge缓存
export const config = {
  runtime: 'edge',
}

// 设置缓存头
return new Response(JSON.stringify(data), {
  headers: {
    'Cache-Control': 's-maxage=60, stale-while-revalidate'
  }
})
```

## 🔧 故障排除

### 常见问题

1. **Supabase连接失败**
   - 检查环境变量配置
   - 确认项目URL和密钥正确

2. **RLS策略阻止访问**
   - 检查行级安全策略
   - 确认用户认证状态

3. **Vercel部署失败**
   - 检查构建日志
   - 确认依赖项正确安装

### 调试工具

```javascript
// 启用Supabase调试
const supabase = createClient(url, key, {
  auth: {
    debug: true
  }
})

// 查看详细错误
console.log('Supabase error:', error.message, error.details)
```

## 📚 进阶功能

### 文件存储

```javascript
// 上传文件到Supabase Storage
const { data, error } = await supabase.storage
  .from('products')
  .upload('image.jpg', file)
```

### 边缘函数

```javascript
// Supabase Edge Functions
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

serve(async (req) => {
  // 处理请求
  return new Response('Hello from Edge Function!')
})
```

### 实时协作

```javascript
// 实时协作功能
const channel = supabase.channel('room1')
  .on('broadcast', { event: 'cursor' }, (payload) => {
    console.log('Cursor moved:', payload)
  })
  .subscribe()
```

## 🎉 部署完成

部署成功后，您将获得：

- 🌐 **前端网站**: https://your-app.vercel.app
- 🔧 **后台管理**: https://your-app.vercel.app/admin
- 📊 **Supabase Dashboard**: https://supabase.com/dashboard
- 📈 **Vercel Analytics**: https://vercel.com/analytics

## 📞 支持

如需帮助，请参考：
- [Supabase文档](https://supabase.com/docs)
- [Vercel文档](https://vercel.com/docs)
- [Next.js文档](https://nextjs.org/docs)

---

**🎊 恭喜！您已成功部署现代化的LED网站系统！**