-- =====================================================
-- CodeBuddy LED Website 数据库更新脚本
-- 更新时间: 2025年01月13日
-- 用途: 支持完整管理后台功能
-- =====================================================

-- 确保所有表都存在并具有正确结构

-- 更新产品表
ALTER TABLE products ADD COLUMN IF NOT EXISTS features JSONB DEFAULT '[]';
ALTER TABLE products ADD COLUMN IF NOT EXISTS specifications TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS image_url TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- 更新询盘表
ALTER TABLE inquiries ADD COLUMN IF NOT EXISTS phone VARCHAR(50);
ALTER TABLE inquiries ADD COLUMN IF NOT EXISTS country VARCHAR(100);
ALTER TABLE inquiries ADD COLUMN IF NOT EXISTS newsletter BOOLEAN DEFAULT FALSE;
ALTER TABLE inquiries ADD COLUMN IF NOT EXISTS product_interest VARCHAR(100);
ALTER TABLE inquiries ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- 更新新闻表
ALTER TABLE news ADD COLUMN IF NOT EXISTS summary TEXT;
ALTER TABLE news ADD COLUMN IF NOT EXISTS image_url TEXT;
ALTER TABLE news ADD COLUMN IF NOT EXISTS author VARCHAR(255) DEFAULT 'Admin';
ALTER TABLE news ADD COLUMN IF NOT EXISTS published BOOLEAN DEFAULT FALSE;
ALTER TABLE news ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

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

-- 插入默认系统设置
INSERT INTO system_settings (setting_key, setting_value, setting_type, description) VALUES
('site_name', '联锦LED显示屏', 'text', '网站名称'),
('contact_email', 'info@lianjinled.com', 'email', '联系邮箱'),
('contact_phone', '+86-755-12345678', 'text', '联系电话'),
('company_address', '深圳市南山区科技园', 'text', '公司地址'),
('site_description', '专业LED显示屏制造商，提供17年行业经验', 'textarea', '网站描述')
ON CONFLICT (setting_key) DO NOTHING;

-- 插入默认页面内容
INSERT INTO page_contents (page_name, title, subtitle, content, image_url) VALUES
('home', '首页 - 专业LED显示解决方案', '联锦LED显示屏', '我们是专业的LED显示屏制造商，拥有17年行业经验，提供高质量的显示解决方案', '/assets/hero/hero-bg.jpg'),
('about', '关于我们 - 专业LED显示厂商', '17年专业经验', '联锦LED是专业的显示屏制造商，致力于为客户提供优质的LED显示解决方案', '/assets/about/company-bg.jpg'),
('products', '产品中心 - LED显示屏系列', '全系列LED显示产品', '涵盖室内、户外、租赁、透明、创意等各类LED显示屏产品', '/assets/products/products-banner.jpg'),
('solutions', '解决方案 - 行业LED显示应用', '专业行业解决方案', '为不同行业提供定制化的LED显示解决方案', '/assets/solutions/solutions-bg.jpg'),
('cases', '成功案例 - LED显示项目展示', '经典项目案例', '展示我们在各行业的成功LED显示项目案例', '/assets/cases/cases-bg.jpg'),
('news', '新闻资讯 - LED行业动态', '最新行业资讯', '了解LED显示行业的最新动态和技术发展', '/assets/news/news-bg.jpg'),
('support', '技术支持 - LED显示服务', '全方位技术支持', '提供专业的LED显示屏技术支持和售后服务', '/assets/support/support-bg.jpg'),
('contact', '联系我们 - LED显示咨询', '专业咨询服务', '联系我们获取专业的LED显示解决方案咨询', '/assets/contact/contact-bg.jpg')
ON CONFLICT (page_name) DO NOTHING;

-- 更新现有产品数据，添加特性和规格
UPDATE products SET 
    features = CASE 
        WHEN category = 'indoor' THEN '["超细间距", "无缝拼接", "前后维护", "高刷新率"]'::jsonb
        WHEN category = 'outdoor' THEN '["高亮度10000nits", "IP65/IP67防水", "抗UV防腐蚀", "工作温度-40°C到+60°C"]'::jsonb
        WHEN category = 'rental' THEN '["轻量化铝制箱体", "快锁系统", "航空箱包装", "免工具安装"]'::jsonb
        WHEN category = 'transparent' THEN '["70-90%透明度", "超轻设计12kg/㎡", "前后维护", "节能LED技术"]'::jsonb
        WHEN category = 'creative' THEN '["360°圆柱显示", "柔性可弯曲", "定制形状", "交互触控"]'::jsonb
        ELSE '["高质量显示", "稳定可靠", "易于维护", "节能环保"]'::jsonb
    END,
    specifications = CASE 
        WHEN category = 'indoor' THEN E'像素间距: 2.5mm\\n亮度: 800cd/㎡\\n刷新率: 3840Hz'
        WHEN category = 'outdoor' THEN E'像素间距: 10mm\\n亮度: 6500cd/㎡\\n防护等级: IP65'
        WHEN category = 'rental' THEN E'像素间距: 3.91mm\\n重量: 6.5kg/㎡\\n安装: 快锁设计'
        WHEN category = 'transparent' THEN E'透明度: 70-90%\\n重量: 12kg/m²\\n节能高效'
        WHEN category = 'creative' THEN E'定制形状\\n柔性模组\\n360°显示能力'
        ELSE E'标准规格\\n高清显示\\n稳定运行'
    END
WHERE features IS NULL OR specifications IS NULL;

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

-- 更新RLS策略
-- 页面内容表：已发布的内容所有人可看
ALTER TABLE page_contents ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Page contents are viewable by everyone" ON page_contents
    FOR SELECT USING (active = true);
CREATE POLICY "Page contents are manageable by authenticated users" ON page_contents
    FOR ALL USING (auth.role() = 'authenticated');

-- 系统设置表：仅管理员可访问
ALTER TABLE system_settings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "System settings are manageable by authenticated users only" ON system_settings
    FOR ALL USING (auth.role() = 'authenticated');

-- 创建索引以提高性能
CREATE INDEX IF NOT EXISTS idx_page_contents_name ON page_contents(page_name);
CREATE INDEX IF NOT EXISTS idx_page_contents_active ON page_contents(active);
CREATE INDEX IF NOT EXISTS idx_system_settings_key ON system_settings(setting_key);

-- 插入一些示例数据进行测试
INSERT INTO products (name, category, description, price, image_url, status) VALUES
('P2.5室内高清显示屏', 'indoor', '适用于会议室、展厅的高清LED显示屏', 8500.00, '/assets/products/indoor-p2.5.jpg', 'active'),
('P10户外大屏幕', 'outdoor', '适用于广告牌、体育场的户外LED大屏', 12000.00, '/assets/products/outdoor-p10.jpg', 'active'),
('P3.91租赁显示屏', 'rental', '适用于演出、会议的便携式LED显示屏', 9800.00, '/assets/products/rental-p3.91.jpg', 'active')
ON CONFLICT (name) DO NOTHING;

INSERT INTO news (title, content, summary, author, published) VALUES
('LED显示技术发展趋势2025', 'LED显示技术在2025年将迎来新的发展机遇，小间距技术不断突破，透明显示应用场景扩大...', '探讨2025年LED显示技术的发展方向和市场趋势', 'Admin', true),
('户外LED显示屏的安装注意事项', '户外LED显示屏的安装需要考虑防水、散热、结构稳定性等多个因素...', '户外LED显示屏安装的专业指导', 'Admin', true),
('小间距LED显示屏市场分析', '小间距LED显示屏市场在近年来快速发展，主要应用于高端会议室、监控中心等场所...', '分析小间距LED显示屏的市场现状和前景', 'Admin', true)
ON CONFLICT (title) DO NOTHING;

-- 完成更新
-- =====================================================
-- 数据库更新完成！
-- 
-- 新增功能:
-- 1. 页面内容管理系统
-- 2. 系统设置管理
-- 3. 完善的产品特性和规格
-- 4. 示例数据用于测试
-- 
-- 所有表都启用了RLS安全策略
-- 管理后台现在可以完整使用所有功能
-- =====================================================
