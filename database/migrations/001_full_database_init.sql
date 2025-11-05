-- ============================================
-- 完整数据库初始化脚本
-- 包含所有必需的表（从 create_tables.sql + 新的管理员表）
-- ============================================

-- ============================================
-- 第一部分：基础内容管理表
-- ============================================

-- 1. 页面内容表
CREATE TABLE IF NOT EXISTS page_contents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    page_name VARCHAR(100) NOT NULL,
    content_key VARCHAR(100) NOT NULL,
    content_value TEXT,
    content_type VARCHAR(50) DEFAULT 'text',
    language VARCHAR(10) DEFAULT 'en',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    created_by UUID,
    updated_by UUID,
    UNIQUE(page_name, content_key, language)
);

-- 2. 页面区块表
CREATE TABLE IF NOT EXISTS page_sections (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    page_name VARCHAR(100) NOT NULL,
    section_name VARCHAR(100) NOT NULL,
    section_order INTEGER DEFAULT 0,
    section_data JSONB,
    is_visible BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    created_by UUID,
    updated_by UUID,
    UNIQUE(page_name, section_name)
);

-- 3. 网站设置表
CREATE TABLE IF NOT EXISTS site_settings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(50) DEFAULT 'text',
    category VARCHAR(50) DEFAULT 'general',
    description TEXT,
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- 4. 内容版本历史表
CREATE TABLE IF NOT EXISTS content_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id UUID NOT NULL,
    old_value JSONB,
    new_value JSONB,
    action VARCHAR(20) NOT NULL,
    changed_by UUID,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- 5. 页面元数据表
CREATE TABLE IF NOT EXISTS page_metadata (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    page_name VARCHAR(100) UNIQUE NOT NULL,
    page_title VARCHAR(255),
    meta_description TEXT,
    meta_keywords TEXT,
    og_title VARCHAR(255),
    og_description TEXT,
    og_image VARCHAR(500),
    custom_meta JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- ============================================
-- 第二部分：管理员系统表
-- ============================================

-- 6. 管理员用户表
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

-- 7. 管理员登录日志表
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

-- ============================================
-- 第三部分：创建索引
-- ============================================

-- 基础表索引
CREATE INDEX IF NOT EXISTS idx_page_contents_page_name ON page_contents(page_name);
CREATE INDEX IF NOT EXISTS idx_page_contents_active ON page_contents(is_active);
CREATE INDEX IF NOT EXISTS idx_page_sections_page_name ON page_sections(page_name);
CREATE INDEX IF NOT EXISTS idx_page_sections_visible ON page_sections(is_visible);
CREATE INDEX IF NOT EXISTS idx_site_settings_category ON site_settings(category);
CREATE INDEX IF NOT EXISTS idx_content_history_table_record ON content_history(table_name, record_id);

-- 管理员表索引
CREATE INDEX IF NOT EXISTS idx_admin_users_user_id ON admin_users(user_id);
CREATE INDEX IF NOT EXISTS idx_admin_users_email ON admin_users(email);
CREATE INDEX IF NOT EXISTS idx_admin_users_role ON admin_users(role);
CREATE INDEX IF NOT EXISTS idx_admin_login_logs_user_id ON admin_login_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_admin_login_logs_login_at ON admin_login_logs(login_at);

-- ============================================
-- 第四部分：创建更新时间触发器函数
-- ============================================

-- 创建触发器函数（如果不存在）
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc', NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表添加触发器
DROP TRIGGER IF EXISTS update_page_contents_updated_at ON page_contents;
CREATE TRIGGER update_page_contents_updated_at
BEFORE UPDATE ON page_contents
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_page_sections_updated_at ON page_sections;
CREATE TRIGGER update_page_sections_updated_at
BEFORE UPDATE ON page_sections
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_site_settings_updated_at ON site_settings;
CREATE TRIGGER update_site_settings_updated_at
BEFORE UPDATE ON site_settings
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_page_metadata_updated_at ON page_metadata;
CREATE TRIGGER update_page_metadata_updated_at
BEFORE UPDATE ON page_metadata
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_admin_users_updated_at ON admin_users;
CREATE TRIGGER update_admin_users_updated_at
BEFORE UPDATE ON admin_users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 第五部分：插入默认数据
-- ============================================

-- 插入默认网站设置
INSERT INTO site_settings (setting_key, setting_value, setting_type, category, description, is_public) VALUES
    ('site_name', 'Lianjin LED', 'text', 'general', '网站名称', true),
    ('site_tagline', 'Professional LED Display Solutions', 'text', 'general', '网站标语', true),
    ('company_email', 'info@lianjinled.com', 'email', 'contact', '公司邮箱', true),
    ('company_phone', '+86 123 4567 8900', 'phone', 'contact', '公司电话', true),
    ('company_address', 'Shenzhen, China', 'text', 'contact', '公司地址', true),
    ('footer_copyright', '© 2024 Lianjin LED. All rights reserved.', 'text', 'footer', '页脚版权信息', true),
    ('social_facebook', 'https://facebook.com/lianjinled', 'url', 'social', 'Facebook链接', true),
    ('social_twitter', 'https://twitter.com/lianjinled', 'url', 'social', 'Twitter链接', true),
    ('social_linkedin', 'https://linkedin.com/company/lianjinled', 'url', 'social', 'LinkedIn链接', true),
    ('maintenance_mode', 'false', 'boolean', 'system', '维护模式', false)
ON CONFLICT (setting_key) DO NOTHING;

-- 插入示例页面内容
INSERT INTO page_contents (page_name, content_key, content_value, content_type, language) VALUES
    ('index', 'hero_title', 'Professional LED Display Solutions', 'text', 'en'),
    ('index', 'hero_subtitle', 'Leading provider of high-quality LED displays for indoor, outdoor, and rental applications worldwide.', 'text', 'en'),
    ('index', 'hero_button_text', 'Explore Products', 'text', 'en'),
    ('about', 'page_title', 'About Lianjin LED', 'text', 'en'),
    ('about', 'page_description', 'Learn about our company, mission, and commitment to LED display excellence.', 'text', 'en'),
    ('products', 'page_title', 'LED Display Products', 'text', 'en'),
    ('products', 'page_description', 'Browse our complete range of professional LED display solutions.', 'text', 'en')
ON CONFLICT (page_name, content_key, language) DO NOTHING;

-- ============================================
-- 第六部分：启用 RLS（行级安全）
-- ============================================

ALTER TABLE page_contents ENABLE ROW LEVEL SECURITY;
ALTER TABLE page_sections ENABLE ROW LEVEL SECURITY;
ALTER TABLE site_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE page_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_login_logs ENABLE ROW LEVEL SECURITY;

-- ============================================
-- 第七部分：基础表的 RLS 策略（公开读取）
-- ============================================

-- page_contents 公开读取策略
DROP POLICY IF EXISTS "Public read access for active page contents" ON page_contents;
CREATE POLICY "Public read access for active page contents" ON page_contents
    FOR SELECT USING (is_active = true);

-- page_sections 公开读取策略
DROP POLICY IF EXISTS "Public read access for visible page sections" ON page_sections;
CREATE POLICY "Public read access for visible page sections" ON page_sections
    FOR SELECT USING (is_visible = true);

-- site_settings 公开读取策略
DROP POLICY IF EXISTS "Public read access for public site settings" ON site_settings;
CREATE POLICY "Public read access for public site settings" ON site_settings
    FOR SELECT USING (is_public = true);

-- page_metadata 公开读取策略
DROP POLICY IF EXISTS "Public read access for page metadata" ON page_metadata;
CREATE POLICY "Public read access for page metadata" ON page_metadata
    FOR SELECT USING (true);

-- ============================================
-- 第八部分：管理员表的 RLS 策略
-- ============================================

-- admin_users 表策略
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

-- admin_login_logs 表策略
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

-- ============================================
-- 第九部分：内容管理表的管理员写入策略
-- ============================================

-- page_contents 管理员管理策略
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

-- page_sections 管理员管理策略
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

-- site_settings 管理员管理策略
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

-- page_metadata 管理员管理策略
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

-- content_history 查看策略
DROP POLICY IF EXISTS "Authenticated users can view content history" ON content_history;
CREATE POLICY "Authenticated users can view content history" ON content_history
    FOR SELECT USING (auth.role() = 'authenticated');

-- ============================================
-- 第十部分：创建辅助函数
-- ============================================

-- 检查是否为管理员
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

-- 获取管理员角色
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

-- 记录管理员登录
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

-- ============================================
-- 第十一部分：创建视图
-- ============================================

-- 页面内容视图
CREATE OR REPLACE VIEW v_page_contents AS
SELECT
    pc.id,
    pc.page_name,
    pc.content_key,
    pc.content_value,
    pc.content_type,
    pc.language,
    pc.is_active,
    pc.updated_at,
    pm.page_title,
    pm.meta_description
FROM page_contents pc
LEFT JOIN page_metadata pm ON pc.page_name = pm.page_name
WHERE pc.is_active = true
ORDER BY pc.page_name, pc.content_key;

-- 管理员用户视图
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
GRANT SELECT ON v_page_contents TO anon, authenticated;
GRANT SELECT ON v_admin_users TO authenticated;

-- ============================================
-- 第十二部分：添加注释
-- ============================================

COMMENT ON TABLE page_contents IS '页面内容表 - 存储所有页面的可编辑内容';
COMMENT ON TABLE page_sections IS '页面区块表 - 存储页面的动态区块';
COMMENT ON TABLE site_settings IS '网站设置表 - 存储全局配置';
COMMENT ON TABLE content_history IS '内容历史表 - 记录所有内容变更';
COMMENT ON TABLE page_metadata IS '页面元数据表 - 存储SEO相关信息';
COMMENT ON TABLE admin_users IS '管理员用户表 - 存储系统管理员信息和角色';
COMMENT ON TABLE admin_login_logs IS '管理员登录日志表 - 记录所有登录尝试';

COMMENT ON FUNCTION is_admin() IS '检查当前用户是否为管理员';
COMMENT ON FUNCTION get_admin_role() IS '获取当前用户的管理员角色';
COMMENT ON FUNCTION log_admin_login IS '记录管理员登录日志';

-- ============================================
-- 完成验证
-- ============================================

SELECT
    '✅ Database initialization completed successfully!' as status,
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public') as total_tables,
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_name IN (
        'page_contents', 'page_sections', 'site_settings', 'content_history',
        'page_metadata', 'admin_users', 'admin_login_logs'
    )) as created_tables;
