-- ============================================
-- 页面内容管理系统数据库表结构
-- ============================================

-- 1. 页面内容表 - 存储每个页面的可编辑内容
CREATE TABLE IF NOT EXISTS page_contents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    page_name VARCHAR(100) NOT NULL, -- 页面名称 (index, about, products等)
    content_key VARCHAR(100) NOT NULL, -- 内容键 (hero_title, hero_subtitle等)
    content_value TEXT, -- 内容值
    content_type VARCHAR(50) DEFAULT 'text', -- 内容类型 (text, html, image, json)
    language VARCHAR(10) DEFAULT 'en', -- 语言版本
    is_active BOOLEAN DEFAULT true, -- 是否启用
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),
    UNIQUE(page_name, content_key, language)
);

-- 2. 页面区块表 - 存储页面的动态区块内容
CREATE TABLE IF NOT EXISTS page_sections (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    page_name VARCHAR(100) NOT NULL,
    section_name VARCHAR(100) NOT NULL, -- 区块名称 (hero, features, testimonials等)
    section_order INTEGER DEFAULT 0, -- 区块排序
    section_data JSONB, -- 区块数据 (存储复杂结构)
    is_visible BOOLEAN DEFAULT true, -- 是否显示
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),
    UNIQUE(page_name, section_name)
);

-- 3. 网站设置表 - 存储全局网站设置
CREATE TABLE IF NOT EXISTS site_settings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL, -- 设置键
    setting_value TEXT, -- 设置值
    setting_type VARCHAR(50) DEFAULT 'text', -- 设置类型
    category VARCHAR(50) DEFAULT 'general', -- 设置分类
    description TEXT, -- 设置描述
    is_public BOOLEAN DEFAULT false, -- 是否公开（前端可访问）
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- 4. 内容版本历史表 - 记录内容修改历史
CREATE TABLE IF NOT EXISTS content_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL, -- 表名
    record_id UUID NOT NULL, -- 记录ID
    old_value JSONB, -- 旧值
    new_value JSONB, -- 新值
    action VARCHAR(20) NOT NULL, -- 操作类型 (insert, update, delete)
    changed_by UUID REFERENCES auth.users(id),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- 5. 页面元数据表 - 存储页面SEO和元数据
CREATE TABLE IF NOT EXISTS page_metadata (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    page_name VARCHAR(100) UNIQUE NOT NULL,
    page_title VARCHAR(255), -- 页面标题
    meta_description TEXT, -- 元描述
    meta_keywords TEXT, -- 关键词
    og_title VARCHAR(255), -- Open Graph标题
    og_description TEXT, -- Open Graph描述
    og_image VARCHAR(500), -- Open Graph图片
    custom_meta JSONB, -- 自定义元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- 创建索引以提高查询性能
CREATE INDEX idx_page_contents_page_name ON page_contents(page_name);
CREATE INDEX idx_page_contents_active ON page_contents(is_active);
CREATE INDEX idx_page_sections_page_name ON page_sections(page_name);
CREATE INDEX idx_page_sections_visible ON page_sections(is_visible);
CREATE INDEX idx_site_settings_category ON site_settings(category);
CREATE INDEX idx_content_history_table_record ON content_history(table_name, record_id);

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc', NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表添加触发器
CREATE TRIGGER update_page_contents_updated_at BEFORE UPDATE ON page_contents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_page_sections_updated_at BEFORE UPDATE ON page_sections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_site_settings_updated_at BEFORE UPDATE ON site_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_page_metadata_updated_at BEFORE UPDATE ON page_metadata
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

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
INSERT INTO page_contents (page_name, content_key, content_value, content_type) VALUES
    ('index', 'hero_title', 'Professional LED Display Solutions', 'text'),
    ('index', 'hero_subtitle', 'Leading provider of high-quality LED displays for indoor, outdoor, and rental applications worldwide.', 'text'),
    ('index', 'hero_button_text', 'Explore Products', 'text'),
    ('index', 'section_title', 'Our LED Display Solutions', 'text'),
    ('index', 'section_subtitle', 'Comprehensive range of professional LED displays for every application', 'text'),
    ('about', 'page_title', 'About Lianjin LED', 'text'),
    ('about', 'page_description', 'Learn about our company, mission, and commitment to LED display excellence.', 'text'),
    ('products', 'page_title', 'LED Display Products', 'text'),
    ('products', 'page_description', 'Browse our complete range of professional LED display solutions.', 'text')
ON CONFLICT (page_name, content_key, language) DO NOTHING;

-- 创建RLS策略
ALTER TABLE page_contents ENABLE ROW LEVEL SECURITY;
ALTER TABLE page_sections ENABLE ROW LEVEL SECURITY;
ALTER TABLE site_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE page_metadata ENABLE ROW LEVEL SECURITY;

-- 公开读取策略（前端可以读取）
CREATE POLICY "Public read access for active page contents" ON page_contents
    FOR SELECT USING (is_active = true);

CREATE POLICY "Public read access for visible page sections" ON page_sections
    FOR SELECT USING (is_visible = true);

CREATE POLICY "Public read access for public site settings" ON site_settings
    FOR SELECT USING (is_public = true);

CREATE POLICY "Public read access for page metadata" ON page_metadata
    FOR SELECT USING (true);

-- 管理员写入策略（需要认证）
CREATE POLICY "Authenticated users can manage page contents" ON page_contents
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can manage page sections" ON page_sections
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can manage site settings" ON site_settings
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can view content history" ON content_history
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can manage page metadata" ON page_metadata
    FOR ALL USING (auth.role() = 'authenticated');

-- 创建内容管理视图
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

-- 授权视图访问
GRANT SELECT ON v_page_contents TO anon;
GRANT ALL ON v_page_contents TO authenticated;

COMMENT ON TABLE page_contents IS '页面内容表 - 存储所有页面的可编辑内容';
COMMENT ON TABLE page_sections IS '页面区块表 - 存储页面的动态区块';
COMMENT ON TABLE site_settings IS '网站设置表 - 存储全局配置';
COMMENT ON TABLE content_history IS '内容历史表 - 记录所有内容变更';
COMMENT ON TABLE page_metadata IS '页面元数据表 - 存储SEO相关信息';
