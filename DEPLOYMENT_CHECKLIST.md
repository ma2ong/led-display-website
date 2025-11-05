# 📋 部署和测试检查清单

**项目**: LED 显示网站 - 第一阶段安全改进
**日期**: 2025-11-05

---

## 🎯 部署目标

部署并测试第一阶段的所有安全改进，确保：
- ✅ 新的认证系统正常工作
- ✅ 管理员可以成功登录
- ✅ 权限系统运行正常
- ✅ 安全头部配置正确
- ✅ 登录日志正常记录

---

## 📝 部署前准备

### ✅ 检查代码是否已推送

在本地执行：
```bash
cd /home/user/led-display-website
git status
git log --oneline -5
```

**确认**：
- [ ] 最新提交包含 "第一阶段：安全修复完成"
- [ ] 本地没有未提交的更改
- [ ] 代码已推送到远程仓库

---

## 第 1 步：配置 Vercel 环境变量 🌍

### 1.1 登录 Vercel

1. 打开浏览器，访问：https://vercel.com/dashboard
2. 使用您的账号登录
3. 找到项目：`led-display-website`

### 1.2 进入环境变量设置

1. 点击项目名称进入项目详情
2. 点击顶部的 **Settings** 标签
3. 在左侧菜单点击 **Environment Variables**

### 1.3 添加环境变量

点击 **Add New** 按钮，逐个添加以下变量：

#### 变量 1: VITE_SUPABASE_URL
```
Name: VITE_SUPABASE_URL
Value: https://jirudzbqcxviytcmxegf.supabase.co

Environments:
✅ Production
✅ Preview
✅ Development
```

#### 变量 2: VITE_SUPABASE_ANON_KEY
```
Name: VITE_SUPABASE_ANON_KEY
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y214ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4

Environments:
✅ Production
✅ Preview
✅ Development
```

#### 变量 3: SUPABASE_URL
```
Name: SUPABASE_URL
Value: https://jirudzbqcxviytcmxegf.supabase.co

Environments:
✅ Production
✅ Preview
✅ Development
```

#### 变量 4: SUPABASE_ANON_KEY
```
Name: SUPABASE_ANON_KEY
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y214ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4

Environments:
✅ Production
✅ Preview
✅ Development
```

### 1.4 保存确认

- [ ] 所有 4 个环境变量都已添加
- [ ] 每个变量都选择了所有 3 个环境（Production, Preview, Development）
- [ ] 点击了 **Save** 按钮

**截图建议**: 建议截图保存，确认所有变量已正确配置。

---

## 第 2 步：执行 Supabase 数据库迁移 🗄️

### 2.1 登录 Supabase Dashboard

1. 打开浏览器，访问：https://supabase.com/dashboard
2. 使用您的账号登录
3. 找到项目：`jirudzbqcxviytcmxegf`（或您的项目名称）

### 2.2 打开 SQL Editor

1. 在左侧菜单点击 **SQL Editor**
2. 点击 **New Query** 按钮

### 2.3 准备迁移脚本

在您的本地计算机上，打开文件：
```
database/migrations/001_create_admin_users.sql
```

**或者直接使用以下内容**（已包含完整脚本）：

<details>
<summary>点击展开完整的 SQL 脚本（310 行）</summary>

```sql
-- ============================================
-- 管理员用户表和安全策略
-- Migration: 001_create_admin_users
-- ============================================

-- 1. 创建管理员用户表
CREATE TABLE IF NOT EXISTS admin_users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'editor' CHECK (role IN ('super_admin', 'admin', 'editor', 'viewer')),
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id),
    UNIQUE(email)
);

-- 2. 创建管理员登录日志表
CREATE TABLE IF NOT EXISTS admin_login_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255),
    ip_address VARCHAR(45),
    user_agent TEXT,
    login_status VARCHAR(20) DEFAULT 'success' CHECK (login_status IN ('success', 'failed', 'blocked')),
    failure_reason TEXT,
    login_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 创建索引
CREATE INDEX idx_admin_users_user_id ON admin_users(user_id);
CREATE INDEX idx_admin_users_email ON admin_users(email);
CREATE INDEX idx_admin_users_role ON admin_users(role);
CREATE INDEX idx_admin_login_logs_user_id ON admin_login_logs(user_id);
CREATE INDEX idx_admin_login_logs_login_at ON admin_login_logs(login_at);

-- 4. 创建更新时间触发器
CREATE TRIGGER update_admin_users_updated_at
BEFORE UPDATE ON admin_users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 5. 启用 RLS
ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_login_logs ENABLE ROW LEVEL SECURITY;

-- 6. RLS 策略 - admin_users 表
CREATE POLICY "Admins can view all admin users" ON admin_users
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM admin_users
            WHERE user_id = auth.uid()
            AND is_active = true
            AND role IN ('super_admin', 'admin')
        )
    );

CREATE POLICY "Only super admins can create admin users" ON admin_users
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM admin_users
            WHERE user_id = auth.uid()
            AND is_active = true
            AND role = 'super_admin'
        )
    );

CREATE POLICY "Only super admins can update admin users" ON admin_users
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM admin_users
            WHERE user_id = auth.uid()
            AND is_active = true
            AND role = 'super_admin'
        )
    );

CREATE POLICY "Only super admins can delete admin users" ON admin_users
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM admin_users
            WHERE user_id = auth.uid()
            AND is_active = true
            AND role = 'super_admin'
        )
    );

-- 7. RLS 策略 - admin_login_logs 表
CREATE POLICY "Admins can view all login logs" ON admin_login_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM admin_users
            WHERE user_id = auth.uid()
            AND is_active = true
            AND role IN ('super_admin', 'admin')
        )
    );

CREATE POLICY "System can insert login logs" ON admin_login_logs
    FOR INSERT WITH CHECK (true);

-- 8. 更新现有表的 RLS 策略
DROP POLICY IF EXISTS "Authenticated users can manage page contents" ON page_contents;
CREATE POLICY "Only admins can manage page contents" ON page_contents
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM admin_users
            WHERE user_id = auth.uid()
            AND is_active = true
            AND role IN ('super_admin', 'admin', 'editor')
        )
    );

DROP POLICY IF EXISTS "Authenticated users can manage page sections" ON page_sections;
CREATE POLICY "Only admins can manage page sections" ON page_sections
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM admin_users
            WHERE user_id = auth.uid()
            AND is_active = true
            AND role IN ('super_admin', 'admin', 'editor')
        )
    );

DROP POLICY IF EXISTS "Authenticated users can manage site settings" ON site_settings;
CREATE POLICY "Only admins can manage site settings" ON site_settings
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM admin_users
            WHERE user_id = auth.uid()
            AND is_active = true
            AND role IN ('super_admin', 'admin')
        )
    );

DROP POLICY IF EXISTS "Authenticated users can manage page metadata" ON page_metadata;
CREATE POLICY "Only admins can manage page metadata" ON page_metadata
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM admin_users
            WHERE user_id = auth.uid()
            AND is_active = true
            AND role IN ('super_admin', 'admin', 'editor')
        )
    );

-- 9. 创建辅助函数
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM admin_users
        WHERE user_id = auth.uid()
        AND is_active = true
        AND role IN ('super_admin', 'admin', 'editor')
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION get_admin_role()
RETURNS VARCHAR AS $$
DECLARE
    user_role VARCHAR;
BEGIN
    SELECT role INTO user_role
    FROM admin_users
    WHERE user_id = auth.uid()
    AND is_active = true;

    RETURN user_role;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION log_admin_login(
    p_user_id UUID,
    p_email VARCHAR,
    p_ip_address VARCHAR DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_login_status VARCHAR DEFAULT 'success',
    p_failure_reason TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    log_id UUID;
BEGIN
    INSERT INTO admin_login_logs (
        user_id,
        email,
        ip_address,
        user_agent,
        login_status,
        failure_reason
    ) VALUES (
        p_user_id,
        p_email,
        p_ip_address,
        p_user_agent,
        p_login_status,
        p_failure_reason
    ) RETURNING id INTO log_id;

    IF p_login_status = 'success' THEN
        UPDATE admin_users
        SET last_login_at = NOW()
        WHERE user_id = p_user_id;
    END IF;

    RETURN log_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 10. 创建视图
CREATE OR REPLACE VIEW v_admin_users AS
SELECT
    au.id,
    au.user_id,
    au.email,
    au.full_name,
    au.role,
    au.is_active,
    au.last_login_at,
    au.created_at,
    u.email_confirmed_at,
    u.phone,
    u.created_at as auth_created_at
FROM admin_users au
LEFT JOIN auth.users u ON au.user_id = u.id
WHERE au.is_active = true
ORDER BY au.created_at DESC;

GRANT SELECT ON v_admin_users TO authenticated;

-- 11. 添加注释
COMMENT ON TABLE admin_users IS '管理员用户表 - 存储系统管理员信息和角色';
COMMENT ON TABLE admin_login_logs IS '管理员登录日志表 - 记录所有登录尝试';
COMMENT ON FUNCTION is_admin() IS '检查当前用户是否为管理员';
COMMENT ON FUNCTION get_admin_role() IS '获取当前用户的管理员角色';
COMMENT ON FUNCTION log_admin_login IS '记录管理员登录日志';
```

</details>

### 2.4 执行迁移脚本

1. 复制上面的完整 SQL 脚本
2. 粘贴到 Supabase SQL Editor 中
3. 点击 **Run** 按钮（或按 Ctrl+Enter）
4. 等待执行完成

### 2.5 验证迁移成功

在 SQL Editor 中执行以下验证脚本：

```sql
-- 验证表是否创建成功
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('admin_users', 'admin_login_logs');

-- 验证函数是否创建成功
SELECT routine_name
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name IN ('is_admin', 'get_admin_role', 'log_admin_login');
```

**预期结果**：

应该看到：
```
table_name
--------------
admin_users
admin_login_logs

routine_name
--------------
is_admin
get_admin_role
log_admin_login
```

### 2.6 检查清单

- [ ] SQL 脚本执行成功，没有错误
- [ ] `admin_users` 表已创建
- [ ] `admin_login_logs` 表已创建
- [ ] 3 个辅助函数已创建
- [ ] RLS 策略已应用

---

## 第 3 步：创建第一个管理员账号 👤

### 3.1 在 Supabase Auth 创建用户

1. 在 Supabase Dashboard 左侧菜单点击 **Authentication**
2. 点击 **Users** 标签
3. 点击右上角的 **Add user** 按钮
4. 选择 **Create new user**

### 3.2 填写用户信息

```
Email: admin@lianjinled.com
（或使用您自己的邮箱）

Password:
（设置一个强密码，至少 12 位，包含大小写字母、数字和特殊字符）
例如：Admin@2025!Secure

✅ Auto Confirm User: 勾选此项（跳过邮件验证）
```

**重要**：请记住您设置的密码！

### 3.3 创建用户并复制 User ID

1. 点击 **Create user** 按钮
2. 用户创建成功后，在用户列表中找到刚创建的用户
3. **复制 User UID**（格式类似：`a1b2c3d4-e5f6-7890-abcd-ef1234567890`）

### 3.4 将用户添加到管理员表

回到 **SQL Editor**，执行以下 SQL（替换实际值）：

```sql
INSERT INTO admin_users (user_id, email, full_name, role, is_active)
VALUES (
    'YOUR_USER_ID_HERE',  -- 替换为步骤 3.3 复制的 User UID
    'admin@lianjinled.com',  -- 替换为您的邮箱
    'System Administrator',  -- 可以修改为您的名字
    'super_admin',  -- 角色：super_admin（最高权限）
    true  -- 激活状态
);
```

**示例**（请使用您实际的 User ID）：
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

### 3.5 验证管理员创建成功

执行以下 SQL：

```sql
SELECT * FROM admin_users;
```

**预期结果**：应该看到一行记录，包含：
- ✅ 您的邮箱
- ✅ 角色为 `super_admin`
- ✅ `is_active` 为 `true`

### 3.6 检查清单

- [ ] 在 Supabase Auth 创建了用户
- [ ] 勾选了 "Auto Confirm User"
- [ ] 复制了 User UID
- [ ] 在 `admin_users` 表中添加了记录
- [ ] 验证查询返回了正确的记录
- [ ] **记住了密码**（非常重要！）

---

## 第 4 步：在 Vercel 重新部署 🚀

### 4.1 进入 Vercel Deployments

1. 回到 Vercel Dashboard
2. 进入您的项目
3. 点击顶部的 **Deployments** 标签

### 4.2 触发重新部署

**方法 1：通过 Git 推送（推荐）**

代码已经推送到 Git，Vercel 应该会自动部署。检查是否有最新的部署正在进行。

**方法 2：手动重新部署**

如果没有自动部署，或者需要强制重新部署：

1. 找到最新的部署记录
2. 点击右侧的 **...** （三个点）菜单
3. 选择 **Redeploy**
4. 确认重新部署

### 4.3 等待部署完成

部署通常需要 1-3 分钟。查看部署状态：

- 🟡 **Building** - 正在构建
- 🟢 **Ready** - 部署成功
- 🔴 **Error** - 部署失败（查看日志）

### 4.4 检查部署日志

点击部署记录，查看：
- ✅ **Build Logs** - 构建日志（应该成功）
- ✅ **Functions** - 无服务器函数（检查 API 路由）

### 4.5 获取部署 URL

部署成功后，复制生产环境 URL：
```
https://your-project-name.vercel.app
```

### 4.6 检查清单

- [ ] 部署已触发
- [ ] 部署状态显示 "Ready"
- [ ] 构建日志没有错误
- [ ] 已复制生产环境 URL

---

## 第 5 步：测试管理员登录功能 🔐

### 5.1 访问登录页

在浏览器中打开：
```
https://your-project-name.vercel.app/admin/login.html
```

### 5.2 检查页面加载

**按 F12 打开开发者工具**，检查：

#### Console 标签
- [ ] 没有 JavaScript 错误（红色）
- [ ] 可能有一些信息日志（蓝色/灰色）

#### Network 标签
- [ ] 页面资源加载成功（200 OK）
- [ ] 没有 404 或 500 错误

### 5.3 尝试登录

输入在步骤 3 创建的管理员账号：

```
Email: admin@lianjinled.com（您的邮箱）
Password: （您设置的密码）
```

点击 **登录** 按钮

### 5.4 预期行为

**成功登录**：
- ✅ 显示 "登录成功！正在跳转..." 消息
- ✅ 1 秒后自动跳转到 `/admin.html`

**如果失败**：
- ❌ 显示错误消息
- 📝 记录错误消息，继续到"故障排除"部分

### 5.5 检查浏览器控制台

在 Console 中查看：
- [ ] 没有网络错误
- [ ] Supabase 连接成功
- [ ] Auth 状态正常

### 5.6 检查清单

- [ ] 登录页面正常加载
- [ ] 没有 JavaScript 错误
- [ ] 可以输入邮箱和密码
- [ ] 点击登录后有响应
- [ ] 成功登录并跳转到管理后台（或记录了错误）

---

## 第 6 步：验证权限系统 🔑

### 6.1 检查管理后台访问

如果登录成功，应该自动跳转到 `/admin.html`

检查：
- [ ] 页面显示管理后台界面
- [ ] 可以看到导航菜单
- [ ] 没有权限错误提示

### 6.2 验证会话持久性

1. 刷新页面（F5）
2. 检查是否仍然保持登录状态
3. 不应该被重定向到登录页

### 6.3 测试登出功能

如果管理后台有登出按钮：
1. 点击登出
2. 应该被重定向到登录页
3. localStorage 应该被清空

### 6.4 测试未登录访问

1. 清除浏览器 localStorage（F12 → Application → Local Storage → Clear）
2. 尝试直接访问 `/admin.html`
3. 应该被自动重定向到登录页

### 6.5 检查清单

- [ ] 登录后可以访问管理后台
- [ ] 刷新页面保持登录状态
- [ ] 登出功能正常
- [ ] 未登录无法访问管理后台

---

## 第 7 步：检查安全头部配置 🛡️

### 7.1 使用浏览器开发者工具

打开任意页面（例如首页），按 F12：

1. 切换到 **Network** 标签
2. 刷新页面（F5）
3. 点击第一个请求（通常是 HTML 文档）
4. 查看 **Headers** 标签 → **Response Headers**

### 7.2 验证安全头部

检查以下响应头部是否存在：

#### 必需的安全头部

```
✅ X-Frame-Options: DENY
✅ X-Content-Type-Options: nosniff
✅ Referrer-Policy: strict-origin-when-cross-origin
✅ Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
✅ Content-Security-Policy: default-src 'self'; script-src...
```

### 7.3 使用在线工具验证

访问：https://securityheaders.com

输入您的网站 URL，检查评分：
- 🎯 **目标评分**: A 或 A+
- 📊 **当前应该**: B+ 或更高

### 7.4 检查 HTTPS 强制

1. 尝试访问 `http://your-project.vercel.app`（注意是 http）
2. 应该自动重定向到 `https://`

### 7.5 检查清单

- [ ] X-Frame-Options 头部存在
- [ ] X-Content-Type-Options 头部存在
- [ ] Strict-Transport-Security (HSTS) 头部存在
- [ ] Content-Security-Policy 头部存在
- [ ] HTTP 自动重定向到 HTTPS
- [ ] SecurityHeaders.com 评分为 B+ 或更高

---

## 第 8 步：验证登录日志记录 📝

### 8.1 查看登录日志

回到 Supabase Dashboard → SQL Editor，执行：

```sql
SELECT
    email,
    ip_address,
    user_agent,
    login_status,
    login_at
FROM admin_login_logs
ORDER BY login_at DESC
LIMIT 10;
```

### 8.2 预期结果

应该看到：
- ✅ 至少一条记录（您刚才的登录）
- ✅ `email` 字段是您的邮箱
- ✅ `ip_address` 有 IP 地址（可能是您的公网 IP）
- ✅ `user_agent` 包含浏览器信息
- ✅ `login_status` 为 `success`
- ✅ `login_at` 是最近的时间

### 8.3 测试失败登录记录

1. 回到登录页
2. 输入错误的密码
3. 尝试登录
4. 再次查询登录日志

应该看到：
- ✅ 新增一条记录
- ✅ `login_status` 为 `failed`
- ✅ `failure_reason` 包含错误原因

### 8.4 检查管理员最后登录时间

```sql
SELECT email, last_login_at FROM admin_users;
```

应该看到 `last_login_at` 已更新为您最近的登录时间。

### 8.5 检查清单

- [ ] 登录日志表有记录
- [ ] 成功登录被记录
- [ ] 失败登录被记录
- [ ] IP 地址被记录
- [ ] User Agent 被记录
- [ ] 最后登录时间已更新

---

## 🎉 部署成功！

如果所有步骤都通过，恭喜您！第一阶段的安全改进已成功部署。

### ✅ 完成情况总结

- [x] Vercel 环境变量已配置
- [x] 数据库迁移已执行
- [x] 管理员账号已创建
- [x] 项目已重新部署
- [x] 管理员可以登录
- [x] 权限系统正常工作
- [x] 安全头部配置正确
- [x] 登录日志正常记录

---

## 🐛 故障排除

### 问题 1: 登录失败 - "Invalid login credentials"

**可能原因**：
- 邮箱或密码输入错误
- 用户未在 Supabase Auth 中创建
- 用户邮箱未确认

**解决方法**：

1. 检查 Supabase Auth 用户列表，确认用户存在
2. 确认勾选了 "Auto Confirm User"
3. 尝试在 Supabase Dashboard 重置密码：
   - Authentication → Users → 选择用户 → Reset Password

---

### 问题 2: 登录失败 - "您没有管理员权限"

**可能原因**：
- 用户存在于 `auth.users`，但不在 `admin_users` 表中

**解决方法**：

```sql
-- 1. 检查用户是否在 auth.users 中
SELECT id, email FROM auth.users WHERE email = 'your-email@example.com';

-- 2. 检查用户是否在 admin_users 中
SELECT * FROM admin_users WHERE email = 'your-email@example.com';

-- 3. 如果不存在，添加到 admin_users
INSERT INTO admin_users (user_id, email, full_name, role, is_active)
VALUES (
    'user-id-from-step-1',
    'your-email@example.com',
    'Your Name',
    'super_admin',
    true
);
```

---

### 问题 3: Supabase 连接失败

**可能原因**：
- 环境变量未配置或配置错误
- Vercel 未重新部署

**解决方法**：

1. 检查 Vercel 环境变量是否正确
2. 检查 Supabase URL 和 Anon Key 是否正确
3. 强制重新部署 Vercel 项目
4. 清除浏览器缓存后重试

---

### 问题 4: JavaScript 模块错误

**错误信息**：
```
Cannot use import statement outside a module
```

**解决方法**：

检查 HTML 文件中的 script 标签是否包含 `type="module"`：
```html
<script type="module">
  import { handleLogin } from '../js/admin-auth.js'
  // ...
</script>
```

---

### 问题 5: 环境变量未生效

**解决方法**：

1. 确认在 Vercel 保存了环境变量
2. 确认选择了正确的环境（Production/Preview/Development）
3. **重要**：修改环境变量后必须重新部署
4. 在 Vercel Deployments 中找到最新部署，点击 Redeploy

---

### 问题 6: 页面无限重定向

**可能原因**：
- 会话验证逻辑错误
- localStorage 损坏

**解决方法**：

1. 清除浏览器所有数据：
   - F12 → Application → Storage → Clear site data
2. 清除浏览器缓存
3. 重启浏览器
4. 重新尝试登录

---

## 📞 需要帮助？

如果遇到其他问题：

1. **查看浏览器控制台**：F12 → Console，复制错误信息
2. **查看 Vercel 日志**：Deployments → 点击部署 → View Function Logs
3. **查看 Supabase 日志**：Dashboard → Logs
4. **检查网络请求**：F12 → Network，查看失败的请求

**常用调试 SQL**：

```sql
-- 查看所有管理员
SELECT * FROM admin_users;

-- 查看最近的登录日志
SELECT * FROM admin_login_logs ORDER BY login_at DESC LIMIT 20;

-- 查看所有 Auth 用户
SELECT id, email, email_confirmed_at, created_at FROM auth.users;

-- 检查 RLS 策略
SELECT tablename, policyname
FROM pg_policies
WHERE tablename IN ('admin_users', 'admin_login_logs');
```

---

## 🔄 回滚方案

如果部署后出现严重问题，可以回滚到之前的版本：

### 在 Vercel 回滚

1. Deployments → 找到之前的稳定部署
2. 点击 **...** → **Promote to Production**

### 在 Git 回滚

```bash
# 查看提交历史
git log --oneline

# 回滚到之前的提交
git revert HEAD

# 推送回滚
git push
```

---

## 📊 测试报告模板

完成测试后，填写以下报告：

```
## LED 显示网站 - 第一阶段部署测试报告

**测试日期**: ________
**测试人员**: ________
**部署环境**: Production

### 1. 环境变量配置
- [ ] VITE_SUPABASE_URL 已配置
- [ ] VITE_SUPABASE_ANON_KEY 已配置
- [ ] SUPABASE_URL 已配置
- [ ] SUPABASE_ANON_KEY 已配置

### 2. 数据库迁移
- [ ] admin_users 表已创建
- [ ] admin_login_logs 表已创建
- [ ] RLS 策略已应用
- [ ] 辅助函数已创建

### 3. 管理员账号
- [ ] 第一个管理员已创建
- [ ] 邮箱: ________________
- [ ] 角色: super_admin
- [ ] 状态: is_active = true

### 4. 登录功能
- [ ] 登录页面正常加载
- [ ] 可以成功登录
- [ ] 登录后跳转到管理后台
- [ ] 会话保持正常
- [ ] 登出功能正常

### 5. 权限系统
- [ ] 未登录无法访问管理后台
- [ ] 登录后可以访问
- [ ] 刷新页面保持登录

### 6. 安全头部
- [ ] X-Frame-Options 已配置
- [ ] HSTS 已配置
- [ ] CSP 已配置
- [ ] SecurityHeaders.com 评分: ____

### 7. 登录日志
- [ ] 成功登录被记录
- [ ] 失败登录被记录
- [ ] IP 地址被记录
- [ ] 最后登录时间更新

### 问题记录
（如有问题，请在此记录）

### 总体评价
- [ ] 所有功能正常
- [ ] 部分功能有问题（见问题记录）
- [ ] 需要回滚

**签名**: ________
```

---

## ✅ 下一步

部署和测试完成后，您可以：

1. ✅ **继续第二阶段优化**（性能优化）
2. ✅ **创建更多管理员账号**（不同角色）
3. ✅ **配置监控和告警**
4. ✅ **进行压力测试**

**准备好继续第二阶段了吗？**

第二阶段将进行性能优化：
- 配置 Vite 构建工具
- 优化图片资源
- 代码分割和懒加载
- 本地化 CDN 依赖

---

**文档版本**: 1.0.0
**最后更新**: 2025-11-05
