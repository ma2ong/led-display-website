# 🔧 分步数据库初始化指南

如果遇到错误，请按照以下步骤**逐步执行**，每执行一步都验证结果。

---

## 步骤 1：清理旧的策略（安全起见）

**目的**：删除可能冲突的旧策略

```sql
-- 清理所有可能存在的旧策略
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT schemaname, tablename, policyname
        FROM pg_policies
        WHERE schemaname = 'public'
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON %I.%I', r.policyname, r.schemaname, r.tablename);
    END LOOP;
END $$;

SELECT 'Old policies cleaned' as status;
```

**验证**：应该显示 "Old policies cleaned"

---

## 步骤 2：创建基础表

**目的**：创建所有表结构

```sql
-- 创建基础内容表
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

SELECT 'Basic tables created' as status;
```

**验证**：

```sql
-- 应该返回 5 个表
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('page_contents', 'page_sections', 'site_settings', 'content_history', 'page_metadata')
ORDER BY table_name;
```

---

## 步骤 3：创建管理员表

**目的**：创建管理员系统相关表

```sql
-- 创建管理员用户表
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

-- 创建管理员登录日志表
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

SELECT 'Admin tables created' as status;
```

**验证**：

```sql
-- 应该返回 2 个表
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('admin_users', 'admin_login_logs')
ORDER BY table_name;
```

---

## 步骤 4：创建索引

```sql
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

SELECT 'Indexes created' as status;
```

---

## 步骤 5：创建触发器

```sql
-- 创建更新时间函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc', NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为基础表添加触发器
DROP TRIGGER IF EXISTS update_page_contents_updated_at ON page_contents;
CREATE TRIGGER update_page_contents_updated_at
BEFORE UPDATE ON page_contents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_page_sections_updated_at ON page_sections;
CREATE TRIGGER update_page_sections_updated_at
BEFORE UPDATE ON page_sections FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_site_settings_updated_at ON site_settings;
CREATE TRIGGER update_site_settings_updated_at
BEFORE UPDATE ON site_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_page_metadata_updated_at ON page_metadata;
CREATE TRIGGER update_page_metadata_updated_at
BEFORE UPDATE ON page_metadata FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_admin_users_updated_at ON admin_users;
CREATE TRIGGER update_admin_users_updated_at
BEFORE UPDATE ON admin_users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

SELECT 'Triggers created' as status;
```

---

## 步骤 6：插入默认数据

```sql
-- 插入网站设置
INSERT INTO site_settings (setting_key, setting_value, setting_type, category, description, is_public) VALUES
    ('site_name', 'Lianjin LED', 'text', 'general', '网站名称', true),
    ('site_tagline', 'Professional LED Display Solutions', 'text', 'general', '网站标语', true),
    ('company_email', 'info@lianjinled.com', 'email', 'contact', '公司邮箱', true),
    ('company_phone', '+86 123 4567 8900', 'phone', 'contact', '公司电话', true),
    ('company_address', 'Shenzhen, China', 'text', 'contact', '公司地址', true)
ON CONFLICT (setting_key) DO NOTHING;

-- 插入示例页面内容
INSERT INTO page_contents (page_name, content_key, content_value, content_type, language) VALUES
    ('index', 'hero_title', 'Professional LED Display Solutions', 'text', 'en'),
    ('index', 'hero_subtitle', 'Leading provider of high-quality LED displays.', 'text', 'en')
ON CONFLICT (page_name, content_key, language) DO NOTHING;

SELECT 'Default data inserted' as status;
```

---

## 步骤 7：启用 RLS

```sql
ALTER TABLE page_contents ENABLE ROW LEVEL SECURITY;
ALTER TABLE page_sections ENABLE ROW LEVEL SECURITY;
ALTER TABLE site_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE page_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_login_logs ENABLE ROW LEVEL SECURITY;

SELECT 'RLS enabled' as status;
```

---

## 步骤 8：创建公开读取策略

```sql
-- page_contents 公开读取
DROP POLICY IF EXISTS "Public read access for active page contents" ON page_contents;
CREATE POLICY "Public read access for active page contents" ON page_contents
FOR SELECT USING (is_active = true);

-- page_sections 公开读取
DROP POLICY IF EXISTS "Public read access for visible page sections" ON page_sections;
CREATE POLICY "Public read access for visible page sections" ON page_sections
FOR SELECT USING (is_visible = true);

-- site_settings 公开读取
DROP POLICY IF EXISTS "Public read access for public site settings" ON site_settings;
CREATE POLICY "Public read access for public site settings" ON site_settings
FOR SELECT USING (is_public = true);

-- page_metadata 公开读取
DROP POLICY IF EXISTS "Public read access for page metadata" ON page_metadata;
CREATE POLICY "Public read access for page metadata" ON page_metadata
FOR SELECT USING (true);

SELECT 'Public read policies created' as status;
```

---

## 步骤 9：创建管理员读取策略

```sql
-- admin_users 查看策略
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

-- admin_login_logs 查看策略
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

-- 系统可以插入登录日志
DROP POLICY IF EXISTS "System can insert login logs" ON admin_login_logs;
CREATE POLICY "System can insert login logs" ON admin_login_logs
FOR INSERT WITH CHECK (true);

SELECT 'Admin read policies created' as status;
```

---

## 步骤 10：创建管理员写入策略

```sql
-- 只有超级管理员可以创建管理员
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

-- 只有超级管理员可以更新管理员
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

-- 只有超级管理员可以删除管理员
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

SELECT 'Admin write policies created' as status;
```

---

## 步骤 11：创建内容管理策略

```sql
-- page_contents 管理策略
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

-- page_sections 管理策略
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

-- site_settings 管理策略
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

-- page_metadata 管理策略
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

SELECT 'Content management policies created' as status;
```

---

## 步骤 12：创建辅助函数

```sql
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
) RETURNS UUID AS $$
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

SELECT 'Helper functions created' as status;
```

---

## 最终验证

```sql
-- 验证所有表都已创建
SELECT
    '✅ All tables created!' as status,
    COUNT(*) as table_count
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'page_contents', 'page_sections', 'site_settings',
    'content_history', 'page_metadata', 'admin_users', 'admin_login_logs'
);

-- 应该返回 table_count = 7
```

---

## 使用方式

**逐步执行**：
1. 复制步骤 1 的SQL → 粘贴到 Supabase → Run
2. 看到成功后，复制步骤 2 → 粘贴 → Run
3. 依次执行步骤 3-12
4. 最后执行"最终验证"

**每一步都会显示成功消息**，如果某一步出错，停下来告诉我错误信息。

这样可以准确定位问题出在哪一步！
