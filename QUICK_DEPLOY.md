# 🚀 一键部署脚本和命令

本文件包含所有可以**直接复制粘贴**的命令和脚本，最小化手动操作。

---

## 步骤 1：Vercel 环境变量（必须手动）

### 📋 复制以下内容

访问：https://vercel.com/dashboard → 您的项目 → Settings → Environment Variables

**然后逐个添加以下 4 个变量**（每个都勾选所有 3 个环境）：

```
变量 1：
名称：VITE_SUPABASE_URL
值：https://jirudzbqcxviytcmxegf.supabase.co

变量 2：
名称：VITE_SUPABASE_ANON_KEY
值：eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y214ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4

变量 3：
名称：SUPABASE_URL
值：https://jirudzbqcxviytcmxegf.supabase.co

变量 4：
名称：SUPABASE_ANON_KEY
值：eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y214ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4
```

**操作时长**：约 3-5 分钟

---

## 步骤 2：Supabase 数据库迁移（一键复制）

### 📋 操作步骤

1. 访问：https://supabase.com/dashboard
2. 进入您的项目 → SQL Editor → New Query
3. **复制下面的完整 SQL 脚本**
4. 粘贴到 SQL Editor
5. 点击 **Run** 或按 Ctrl+Enter

### 🔽 复制以下完整 SQL 脚本

<details>
<summary>点击展开 SQL 脚本（全选复制）</summary>

```sql
-- ============================================
-- LED 显示网站 - 第一阶段安全改进
-- 数据库迁移脚本 v1.0.0
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
CREATE INDEX IF NOT EXISTS idx_admin_users_user_id ON admin_users(user_id);
CREATE INDEX IF NOT EXISTS idx_admin_users_email ON admin_users(email);
CREATE INDEX IF NOT EXISTS idx_admin_users_role ON admin_users(role);
CREATE INDEX IF NOT EXISTS idx_admin_login_logs_user_id ON admin_login_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_admin_login_logs_login_at ON admin_login_logs(login_at);

-- 4. 创建更新时间触发器
DROP TRIGGER IF EXISTS update_admin_users_updated_at ON admin_users;
CREATE TRIGGER update_admin_users_updated_at
BEFORE UPDATE ON admin_users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 5. 启用 RLS
ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_login_logs ENABLE ROW LEVEL SECURITY;

-- 6. RLS 策略 - admin_users
DROP POLICY IF EXISTS "Admins can view all admin users" ON admin_users;
CREATE POLICY "Admins can view all admin users" ON admin_users
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM admin_users
            WHERE user_id = auth.uid()
            AND is_active = true
            AND role IN ('super_admin', 'admin')
        )
    );

DROP POLICY IF EXISTS "Only super admins can create admin users" ON admin_users;
CREATE POLICY "Only super admins can create admin users" ON admin_users
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM admin_users
            WHERE user_id = auth.uid()
            AND is_active = true
            AND role = 'super_admin'
        )
    );

DROP POLICY IF EXISTS "Only super admins can update admin users" ON admin_users;
CREATE POLICY "Only super admins can update admin users" ON admin_users
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM admin_users
            WHERE user_id = auth.uid()
            AND is_active = true
            AND role = 'super_admin'
        )
    );

DROP POLICY IF EXISTS "Only super admins can delete admin users" ON admin_users;
CREATE POLICY "Only super admins can delete admin users" ON admin_users
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM admin_users
            WHERE user_id = auth.uid()
            AND is_active = true
            AND role = 'super_admin'
        )
    );

-- 7. RLS 策略 - admin_login_logs
DROP POLICY IF EXISTS "Admins can view all login logs" ON admin_login_logs;
CREATE POLICY "Admins can view all login logs" ON admin_login_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM admin_users
            WHERE user_id = auth.uid()
            AND is_active = true
            AND role IN ('super_admin', 'admin')
        )
    );

DROP POLICY IF EXISTS "System can insert login logs" ON admin_login_logs;
CREATE POLICY "System can insert login logs" ON admin_login_logs
    FOR INSERT WITH CHECK (true);

-- 8. 更新现有表的 RLS 策略
DROP POLICY IF EXISTS "Authenticated users can manage page contents" ON page_contents;
DROP POLICY IF EXISTS "Only admins can manage page contents" ON page_contents;
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
DROP POLICY IF EXISTS "Only admins can manage page sections" ON page_sections;
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
DROP POLICY IF EXISTS "Only admins can manage site settings" ON site_settings;
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
DROP POLICY IF EXISTS "Only admins can manage page metadata" ON page_metadata;
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
        user_id, email, ip_address, user_agent, login_status, failure_reason
    ) VALUES (
        p_user_id, p_email, p_ip_address, p_user_agent, p_login_status, p_failure_reason
    ) RETURNING id INTO log_id;

    IF p_login_status = 'success' THEN
        UPDATE admin_users SET last_login_at = NOW() WHERE user_id = p_user_id;
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
COMMENT ON TABLE admin_users IS '管理员用户表';
COMMENT ON TABLE admin_login_logs IS '管理员登录日志表';
COMMENT ON FUNCTION is_admin() IS '检查当前用户是否为管理员';
COMMENT ON FUNCTION get_admin_role() IS '获取当前用户的管理员角色';
COMMENT ON FUNCTION log_admin_login IS '记录管理员登录日志';

-- 12. 验证迁移
SELECT 'Migration completed successfully!' as status,
       (SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'admin_users') as admin_users_table,
       (SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'admin_login_logs') as login_logs_table;
```

</details>

### ✅ 验证成功

执行完成后，运行以下验证命令：

```sql
-- 应该返回 2 个表
SELECT table_name FROM information_schema.tables
WHERE table_name IN ('admin_users', 'admin_login_logs');
```

**操作时长**：约 2-3 分钟（复制粘贴 + 点击 Run）

---

## 步骤 3：创建管理员账号（分步复制）

### 第 3.1 步：在 Supabase Auth 创建用户

1. 访问：https://supabase.com/dashboard
2. 进入项目 → **Authentication** → **Users** → **Add user**
3. 选择 **Create new user**
4. 填写：

```
Email: admin@lianjinled.com
Password: [您设置一个强密码，例如：Admin@2025!Secure]
✅ 勾选 "Auto Confirm User"
```

5. 点击 **Create user**
6. **复制显示的 User UID**（重要！）

---

### 第 3.2 步：添加到管理员表（一键复制）

📋 **复制以下 SQL，替换 YOUR_USER_ID_HERE 后执行**：

```sql
-- 替换 YOUR_USER_ID_HERE 为步骤 3.1 复制的 User UID
INSERT INTO admin_users (user_id, email, full_name, role, is_active)
VALUES (
    'YOUR_USER_ID_HERE',  -- 👈 替换这里
    'admin@lianjinled.com',  -- 如果用了其他邮箱，也要替换
    'System Administrator',
    'super_admin',
    true
);
```

**示例**（假设您的 User UID 是 `abc123-def456...`）：
```sql
INSERT INTO admin_users (user_id, email, full_name, role, is_active)
VALUES (
    'abc123-def456-789abc-defghi',
    'admin@lianjinled.com',
    'System Administrator',
    'super_admin',
    true
);
```

### ✅ 验证成功

```sql
-- 应该看到您刚创建的管理员
SELECT * FROM admin_users;
```

**操作时长**：约 3-5 分钟

---

## 步骤 4：重新部署（可选）

如果 Vercel 没有自动部署，手动触发：

1. 访问：https://vercel.com/dashboard
2. 进入项目 → **Deployments**
3. 最新部署 → 点击 **...** → **Redeploy**

**操作时长**：约 1 分钟（等待部署 2-3 分钟）

---

## 🎯 总结：3 个步骤，所有命令可复制

| 步骤 | 操作 | 时间 | 可复制内容 |
|------|------|------|-----------|
| 1 | Vercel 环境变量 | 3-5 分钟 | ✅ 4 个变量名和值 |
| 2 | 数据库迁移 | 2-3 分钟 | ✅ 完整 SQL 脚本 |
| 3 | 创建管理员 | 3-5 分钟 | ✅ INSERT SQL 语句 |
| 4 | 重新部署 | 1 分钟 | 手动点击 |

**总用时**: 约 10-15 分钟

---

## 🧪 测试登录（完成后）

访问：`https://您的域名.vercel.app/admin/login.html`

输入：
```
Email: admin@lianjinled.com（或您的邮箱）
Password: [您设置的密码]
```

**成功标志**：
- ✅ 显示 "登录成功！"
- ✅ 跳转到 `/admin.html` 管理后台

---

## 🐛 快速故障排除

### 问题：登录失败

**解决**：
```sql
-- 1. 检查用户是否在 auth.users
SELECT id, email FROM auth.users WHERE email = 'admin@lianjinled.com';

-- 2. 检查是否在 admin_users
SELECT * FROM admin_users WHERE email = 'admin@lianjinled.com';

-- 3. 如果第 1 步有结果，第 2 步没有，执行：
INSERT INTO admin_users (user_id, email, full_name, role, is_active)
VALUES ('用户ID', 'admin@lianjinled.com', 'Admin', 'super_admin', true);
```

### 问题：Supabase 连接失败

**解决**：
1. 检查 Vercel 环境变量是否保存
2. 确认环境变量选择了所有 3 个环境
3. 重新部署 Vercel

---

**所有命令都可以直接复制粘贴，最小化手动输入！** 🚀
