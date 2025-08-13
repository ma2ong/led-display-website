-- =====================================================
-- 步骤2: 创建新表
-- =====================================================

-- 创建页面内容表（如果不存在）
CREATE TABLE IF NOT EXISTS page_contents (
    id BIGSERIAL PRIMARY KEY,
    page_name VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500),
    subtitle VARCHAR(500),
    content TEXT,
    image_url TEXT,
    meta_description TEXT,
    keywords TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建系统设置表（如果不存在）
CREATE TABLE IF NOT EXISTS system_settings (
    id BIGSERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(50) DEFAULT 'text',
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建或更新触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为新表添加更新时间触发器
DROP TRIGGER IF EXISTS update_page_contents_updated_at ON page_contents;
CREATE TRIGGER update_page_contents_updated_at BEFORE UPDATE ON page_contents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_system_settings_updated_at ON system_settings;
CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
