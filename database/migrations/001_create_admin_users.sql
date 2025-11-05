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

-- 管理员可以查看所有管理员用户
CREATE POLICY "Admins can view all admin users" ON admin_users
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM admin_users
            WHERE user_id = auth.uid()
            AND is_active = true
            AND role IN ('super_admin', 'admin')
        )
    );

-- 只有 super_admin 可以创建新管理员
CREATE POLICY "Only super admins can create admin users" ON admin_users
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM admin_users
            WHERE user_id = auth.uid()
            AND is_active = true
            AND role = 'super_admin'
        )
    );

-- 只有 super_admin 可以修改管理员角色
CREATE POLICY "Only super admins can update admin users" ON admin_users
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM admin_users
            WHERE user_id = auth.uid()
            AND is_active = true
            AND role = 'super_admin'
        )
    );

-- 只有 super_admin 可以删除管理员
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

-- 管理员可以查看所有登录日志
CREATE POLICY "Admins can view all login logs" ON admin_login_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM admin_users
            WHERE user_id = auth.uid()
            AND is_active = true
            AND role IN ('super_admin', 'admin')
        )
    );

-- 系统可以插入登录日志（不需要认证）
CREATE POLICY "System can insert login logs" ON admin_login_logs
    FOR INSERT WITH CHECK (true);

-- 8. 更新现有表的 RLS 策略，要求管理员权限

-- 更新 page_contents 的 RLS 策略
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

-- 更新 page_sections 的 RLS 策略
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

-- 更新 site_settings 的 RLS 策略
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

-- 更新 page_metadata 的 RLS 策略
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

-- 9. 创建辅助函数 - 检查是否为管理员
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

-- 10. 创建辅助函数 - 获取管理员角色
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

-- 11. 创建辅助函数 - 记录登录日志
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

    -- 更新最后登录时间
    IF p_login_status = 'success' THEN
        UPDATE admin_users
        SET last_login_at = NOW()
        WHERE user_id = p_user_id;
    END IF;

    RETURN log_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 12. 插入默认超级管理员（请在生产环境中修改这些信息）
-- 注意：这个管理员需要先在 Supabase Auth 中创建用户账号
-- 然后运行以下 SQL 将该用户设置为管理员

-- 示例：创建默认管理员记录（需要替换实际的 user_id）
-- 在 Supabase Dashboard 中创建用户后，运行：
/*
INSERT INTO admin_users (user_id, email, full_name, role, is_active)
VALUES (
    'your-auth-user-id-here',  -- 从 auth.users 表获取
    'admin@lianjinled.com',
    'System Administrator',
    'super_admin',
    true
);
*/

-- 13. 创建视图 - 管理员用户列表（包含认证信息）
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

-- 授权视图访问
GRANT SELECT ON v_admin_users TO authenticated;

-- 14. 添加注释
COMMENT ON TABLE admin_users IS '管理员用户表 - 存储系统管理员信息和角色';
COMMENT ON TABLE admin_login_logs IS '管理员登录日志表 - 记录所有登录尝试';
COMMENT ON FUNCTION is_admin() IS '检查当前用户是否为管理员';
COMMENT ON FUNCTION get_admin_role() IS '获取当前用户的管理员角色';
COMMENT ON FUNCTION log_admin_login IS '记录管理员登录日志';

-- Migration completed
-- 请在 Supabase Dashboard 中创建第一个管理员用户，然后将其添加到 admin_users 表
