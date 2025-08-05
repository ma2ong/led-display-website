# 🔧 手动Supabase + Vercel部署指南

## 快速部署步骤

### 1. 创建Supabase项目

1. 访问 [https://supabase.com](https://supabase.com)
2. 点击 "Start your project"
3. 创建新组织（如果需要）
4. 点击 "New Project"
5. 填写项目信息：
   - Name: `led-display-website`
   - Database Password: 设置强密码
   - Region: 选择最近的区域

### 2. 配置数据库

在Supabase Dashboard中：

1. 进入 **SQL Editor**
2. 点击 "New Query"
3. 复制粘贴 `supabase/schema.sql` 的内容
4. 点击 "Run" 执行SQL

### 3. 获取API密钥

在项目设置中：

1. 进入 **Settings** > **API**
2. 复制以下信息：
   - Project URL
   - anon public key
   - service_role key (保密)

### 4. 配置环境变量

创建 `.env.local` 文件：

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
NEXT_PUBLIC_SITE_NAME=深圳联进科技有限公司
```

### 5. 安装依赖并测试

```bash
# 安装依赖
npm install

# 本地测试
npm run dev
```

### 6. 部署到Vercel

```bash
# 安装Vercel CLI
npm install -g vercel

# 登录Vercel
vercel login

# 部署项目
vercel --prod
```

### 7. 在Vercel中设置环境变量

在Vercel Dashboard中：

1. 进入项目设置
2. 点击 **Environment Variables**
3. 添加以下变量：
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`

### 8. 创建管理员账户

在Supabase Dashboard中：

1. 进入 **Authentication** > **Users**
2. 点击 "Add user"
3. 填写管理员邮箱和密码
4. 进入 **Table Editor** > **user_profiles**
5. 添加用户配置记录

## 🎉 完成！

现在您可以访问：
- 前端网站: https://your-vercel-app.vercel.app
- 后台管理: https://your-vercel-app.vercel.app/admin

## 故障排除

如果遇到问题：

1. **检查环境变量** - 确保所有密钥正确配置
2. **查看构建日志** - 在Vercel Dashboard中查看部署日志
3. **测试API连接** - 访问 `/api/supabase-api?endpoint=health`
4. **检查RLS策略** - 确保数据库策略正确设置