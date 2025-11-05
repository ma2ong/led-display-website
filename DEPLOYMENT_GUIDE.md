# 🚀 安全部署指南

本指南将帮助您安全地部署 LED 显示网站，并配置必要的环境变量和管理员账号。

---

## 📋 目录

1. [Vercel 环境变量配置](#vercel-环境变量配置)
2. [Supabase 数据库设置](#supabase-数据库设置)
3. [创建管理员账号](#创建管理员账号)
4. [验证部署](#验证部署)
5. [故障排除](#故障排除)

---

## 1. Vercel 环境变量配置

### 步骤 1.1: 登录 Vercel

1. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
2. 选择您的项目 `led-display-website`

### 步骤 1.2: 配置环境变量

进入 **Settings** → **Environment Variables**，添加以下变量：

#### 必需的环境变量

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `VITE_SUPABASE_URL` | `https://jirudzbqcxviytcmxegf.supabase.co` | Supabase 项目 URL |
| `VITE_SUPABASE_ANON_KEY` | `eyJhbGci...` | Supabase 匿名密钥 |
| `SUPABASE_URL` | `https://jirudzbqcxviytcmxegf.supabase.co` | 用于 API 路由 |
| `SUPABASE_ANON_KEY` | `eyJhbGci...` | 用于 API 路由 |

#### 可选的环境变量

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `VITE_ADMIN_EMAIL` | `admin@lianjinled.com` | 默认管理员邮箱 |
| `VITE_ENABLE_PWA` | `false` | 是否启用 PWA |
| `VITE_ENABLE_REALTIME` | `true` | 是否启用实时同步 |
| `NODE_ENV` | `production` | 运行环境 |

### 步骤 1.3: 选择环境

为每个环境变量选择应用范围：
- ✅ **Production** - 生产环境（必选）
- ✅ **Preview** - 预览环境（推荐）
- ✅ **Development** - 开发环境（可选）

### 步骤 1.4: 保存并重新部署

1. 点击 **Save** 保存环境变量
2. 进入 **Deployments** 标签
3. 找到最新的部署，点击右侧的 **...** 菜单
4. 选择 **Redeploy** 重新部署

---

## 2. Supabase 数据库设置

### 步骤 2.1: 执行管理员表迁移

在 Supabase Dashboard 中执行以下 SQL：

1. 登录 [Supabase Dashboard](https://supabase.com/dashboard)
2. 选择项目 `jirudzbqcxviytcmxegf`
3. 进入 **SQL Editor**
4. 点击 **New Query**
5. 复制并执行 `database/migrations/001_create_admin_users.sql` 中的内容

### 步骤 2.2: 验证表创建

执行以下 SQL 验证表已创建：

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('admin_users', 'admin_login_logs');
```

应该返回：
```
table_name
--------------
admin_users
admin_login_logs
```

---

## 3. 创建管理员账号

### 步骤 3.1: 在 Supabase Auth 创建用户

1. 进入 Supabase Dashboard → **Authentication** → **Users**
2. 点击 **Add user** → **Create new user**
3. 填写信息：
   - **Email**: `admin@lianjinled.com`（或您的管理员邮箱）
   - **Password**: 设置一个强密码（至少 8 位，包含大小写字母和数字）
   - **Auto Confirm User**: ✅ 勾选（跳过邮件验证）
4. 点击 **Create user**

### 步骤 3.2: 获取用户 ID

创建用户后，复制显示的 **User UID**（例如：`a1b2c3d4-e5f6-7890-abcd-ef1234567890`）

### 步骤 3.3: 将用户添加到管理员表

在 SQL Editor 中执行（替换 `USER_ID` 和邮箱）：

```sql
INSERT INTO admin_users (user_id, email, full_name, role, is_active)
VALUES (
    'USER_ID_HERE',  -- 替换为上一步复制的 User UID
    'admin@lianjinled.com',  -- 管理员邮箱
    'System Administrator',  -- 管理员姓名
    'super_admin',  -- 角色：super_admin / admin / editor / viewer
    true  -- 是否激活
);
```

**示例**：
```sql
INSERT INTO admin_users (user_id, email, full_name, role, is_active)
VALUES (
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'admin@lianjinled.com',
    'System Administrator',
    'super_admin',
    true
);
```

### 步骤 3.4: 验证管理员创建成功

执行以下 SQL：

```sql
SELECT * FROM admin_users;
```

应该看到刚创建的管理员记录。

---

## 4. 验证部署

### 步骤 4.1: 访问网站

打开浏览器，访问：
- **生产环境**: `https://your-project.vercel.app`
- **管理后台登录页**: `https://your-project.vercel.app/admin/login.html`

### 步骤 4.2: 测试管理员登录

1. 访问管理后台登录页
2. 输入创建的管理员邮箱和密码
3. 点击 **登录**
4. 如果成功，应该跳转到 `/admin.html` 管理后台

### 步骤 4.3: 检查浏览器控制台

按 `F12` 打开开发者工具，检查：
- ✅ 没有 JavaScript 错误
- ✅ 网络请求正常（200 OK）
- ✅ Supabase 连接成功

---

## 5. 故障排除

### 问题 1: "登录失败" 或 "用户名或密码错误"

**可能原因**：
- 环境变量未配置或配置错误
- 用户未添加到 `admin_users` 表
- 密码输入错误

**解决方法**：
1. 检查 Vercel 环境变量是否正确配置
2. 在 Supabase SQL Editor 执行：
   ```sql
   SELECT * FROM admin_users WHERE email = 'your-email@example.com';
   ```
3. 确认用户存在且 `is_active = true`
4. 尝试在 Supabase Dashboard 重置密码

---

### 问题 2: "您没有管理员权限"

**可能原因**：
- 用户在 `auth.users` 中存在，但未添加到 `admin_users` 表

**解决方法**：
执行 SQL 添加用户到管理员表：
```sql
-- 首先查找用户 ID
SELECT id, email FROM auth.users WHERE email = 'your-email@example.com';

-- 然后添加到管理员表
INSERT INTO admin_users (user_id, email, full_name, role, is_active)
VALUES ('user-id-from-above', 'your-email@example.com', 'Admin Name', 'super_admin', true);
```

---

### 问题 3: Supabase 连接失败

**可能原因**：
- Supabase URL 或密钥错误
- Supabase 项目暂停或删除
- RLS 策略阻止访问

**解决方法**：
1. 验证 Supabase 项目是否正常运行
2. 检查环境变量中的 URL 和密钥是否正确
3. 在 Supabase Dashboard 检查 RLS 策略：
   ```sql
   -- 检查 RLS 是否启用
   SELECT tablename, rowsecurity
   FROM pg_tables
   WHERE schemaname = 'public'
   AND tablename = 'admin_users';
   ```

---

### 问题 4: 环境变量未生效

**解决方法**：
1. 确认环境变量已保存
2. 确认选择了正确的环境（Production/Preview/Development）
3. **重要**：修改环境变量后必须重新部署：
   - 进入 Vercel Dashboard → Deployments
   - 点击最新部署的 **...** 菜单 → **Redeploy**

---

### 问题 5: 模块导入错误（"Cannot use import statement outside a module"）

**可能原因**：
- HTML 中的 `<script>` 标签缺少 `type="module"`
- 文件路径错误

**解决方法**：
确保 HTML 中的脚本标签包含 `type="module"`：
```html
<script type="module">
  import { handleLogin } from '../js/admin-auth.js'
  // ...
</script>
```

---

## 🔒 安全最佳实践

### 1. 强密码策略
- ✅ 至少 12 位字符
- ✅ 包含大小写字母、数字和特殊字符
- ✅ 不使用常见密码或个人信息

### 2. 定期更换密码
- 建议每 90 天更换一次管理员密码

### 3. 启用双因素认证（未来）
- 计划集成 Supabase Auth 的 MFA 功能

### 4. 限制管理员数量
- 只创建必要的管理员账号
- 定期审查管理员列表

### 5. 监控登录日志
定期查看登录日志，检测异常活动：
```sql
SELECT
    email,
    ip_address,
    login_status,
    login_at
FROM admin_login_logs
ORDER BY login_at DESC
LIMIT 50;
```

---

## 📝 快速参考

### 重要 URL

| 名称 | URL |
|------|-----|
| Vercel Dashboard | https://vercel.com/dashboard |
| Supabase Dashboard | https://supabase.com/dashboard |
| 网站前台 | https://your-project.vercel.app |
| 管理后台登录 | https://your-project.vercel.app/admin/login.html |
| 管理后台 | https://your-project.vercel.app/admin.html |

### 重要文件

| 文件 | 说明 |
|------|------|
| `.env` | 本地开发环境变量（不提交到 Git） |
| `.env.example` | 环境变量示例文件 |
| `vercel.json` | Vercel 部署配置 |
| `database/migrations/001_create_admin_users.sql` | 管理员表 SQL |
| `lib/supabase-client.js` | 统一的 Supabase 客户端 |
| `js/admin-auth.js` | 管理员认证逻辑 |

### 常用 SQL 命令

```sql
-- 查看所有管理员
SELECT * FROM admin_users;

-- 查看登录日志
SELECT * FROM admin_login_logs ORDER BY login_at DESC LIMIT 20;

-- 重置管理员密码（在 Supabase Auth 中）
-- Dashboard → Authentication → Users → 选择用户 → Reset Password

-- 禁用管理员
UPDATE admin_users SET is_active = false WHERE email = 'user@example.com';

-- 启用管理员
UPDATE admin_users SET is_active = true WHERE email = 'user@example.com';

-- 修改管理员角色
UPDATE admin_users SET role = 'editor' WHERE email = 'user@example.com';
```

---

## ✅ 部署检查清单

在将网站投入生产使用前，请确认：

- [ ] Vercel 环境变量已配置
- [ ] Supabase 数据库迁移已执行
- [ ] 至少创建了一个超级管理员账号
- [ ] 管理员可以成功登录
- [ ] 浏览器控制台没有错误
- [ ] RLS 策略正常工作
- [ ] `.env` 文件已添加到 `.gitignore`
- [ ] 硬编码的密钥已从代码中移除
- [ ] CSP 和安全头部已配置
- [ ] HTTPS 强制启用
- [ ] 所有敏感信息已从 Git 历史中移除

---

## 🆘 需要帮助？

如果遇到问题，请：
1. 检查本文档的"故障排除"部分
2. 查看浏览器控制台的错误信息
3. 查看 Vercel 部署日志
4. 查看 Supabase 日志（Dashboard → Logs）

---

**最后更新**: 2025-11-05
**版本**: 1.0.0
