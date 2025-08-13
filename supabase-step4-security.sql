-- =====================================================
-- 步骤4: 安全策略和性能优化
-- =====================================================

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
        WHEN category = 'indoor' THEN E'像素间距: 2.5mm\n亮度: 800cd/㎡\n刷新率: 3840Hz'
        WHEN category = 'outdoor' THEN E'像素间距: 10mm\n亮度: 6500cd/㎡\n防护等级: IP65'
        WHEN category = 'rental' THEN E'像素间距: 3.91mm\n重量: 6.5kg/㎡\n安装: 快锁设计'
        WHEN category = 'transparent' THEN E'透明度: 70-90%\n重量: 12kg/m²\n节能高效'
        WHEN category = 'creative' THEN E'定制形状\n柔性模组\n360°显示能力'
        ELSE E'标准规格\n高清显示\n稳定运行'
    END
WHERE features IS NULL OR specifications IS NULL;

-- 更新RLS策略
-- 页面内容表：已发布的内容所有人可看
ALTER TABLE page_contents ENABLE ROW LEVEL SECURITY;

-- 删除可能存在的旧策略
DROP POLICY IF EXISTS "Page contents are viewable by everyone" ON page_contents;
DROP POLICY IF EXISTS "Page contents are manageable by authenticated users" ON page_contents;

-- 创建新策略
CREATE POLICY "Page contents are viewable by everyone" ON page_contents
    FOR SELECT USING (active = true);
CREATE POLICY "Page contents are manageable by authenticated users" ON page_contents
    FOR ALL USING (auth.role() = 'authenticated');

-- 系统设置表：仅管理员可访问
ALTER TABLE system_settings ENABLE ROW LEVEL SECURITY;

-- 删除可能存在的旧策略
DROP POLICY IF EXISTS "System settings are manageable by authenticated users only" ON system_settings;

-- 创建新策略
CREATE POLICY "System settings are manageable by authenticated users only" ON system_settings
    FOR ALL USING (auth.role() = 'authenticated');

-- 创建索引以提高性能
CREATE INDEX IF NOT EXISTS idx_page_contents_name ON page_contents(page_name);
CREATE INDEX IF NOT EXISTS idx_page_contents_active ON page_contents(active);
CREATE INDEX IF NOT EXISTS idx_system_settings_key ON system_settings(setting_key);

-- 为产品表添加索引
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);
