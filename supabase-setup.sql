-- =====================================================
-- CodeBuddy LED Website 数据库初始化脚本
-- =====================================================

-- 创建产品表
CREATE TABLE IF NOT EXISTS products (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    image_url TEXT,
    specifications TEXT,
    features JSONB DEFAULT '[]',
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建询盘表
CREATE TABLE IF NOT EXISTS inquiries (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    company VARCHAR(255),
    subject VARCHAR(255),
    message TEXT NOT NULL,
    product_interest VARCHAR(100),
    country VARCHAR(100),
    newsletter BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'new',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建新闻表
CREATE TABLE IF NOT EXISTS news (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT,
    summary TEXT,
    image_url TEXT,
    author VARCHAR(255) DEFAULT 'Admin',
    published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建用户表（管理员）
CREATE TABLE IF NOT EXISTS admin_users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(500) NOT NULL,
    role VARCHAR(50) DEFAULT 'admin',
    active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 插入示例产品数据
INSERT INTO products (name, category, description, price, image_url, specifications, features) VALUES
('Indoor LED Display P2.5', 'indoor', 'High-resolution indoor LED displays perfect for retail stores, corporate offices, conference rooms, and entertainment venues.', 8500.00, '/assets/products/indoor-p2.5.jpg', 'Pixel Pitch: 2.5mm
Brightness: 800cd/㎡
Refresh Rate: 3840Hz', '["Ultra-fine pixel pitch", "Seamless splicing technology", "Front and rear service access", "High refresh rate"]'),

('Outdoor LED Display P10', 'outdoor', 'Weather-resistant outdoor LED displays designed for advertising billboards, sports stadiums, and public information systems.', 12000.00, '/assets/products/outdoor-p10.jpg', 'Pixel Pitch: 10mm
Brightness: 6500cd/㎡
Protection: IP65', '["High brightness up to 10,000 nits", "IP65/IP67 waterproof rating", "Anti-UV and corrosion resistant", "Temperature range: -40°C to +60°C"]'),

('Rental LED Display P3.91', 'rental', 'Flexible and portable rental LED displays perfect for events, concerts, conferences, and temporary installations.', 9800.00, '/assets/products/rental-p3.91.jpg', 'Pixel Pitch: 3.91mm
Weight: 6.5kg/㎡
Installation: Quick lock design', '["Lightweight aluminum cabinet design", "Quick lock system for fast setup", "Flight case packaging included", "Tool-free assembly"]'),

('Transparent LED Display', 'transparent', 'Innovative transparent LED displays that maintain visibility while displaying content, perfect for retail windows and glass facades.', 15000.00, '/assets/products/transparent-led.jpg', 'Transparency: 70-90%
Weight: 12kg/m²
Energy Efficient', '["70-90% transparency rate", "Ultra-lightweight design (12kg/m²)", "Easy maintenance from front/back", "Energy-efficient LED technology"]'),

('Creative LED Display', 'creative', 'Custom-shaped LED displays including curved, spherical, and irregular shapes for unique architectural applications.', 18000.00, '/assets/products/creative-led.jpg', 'Custom shapes
Flexible modules
360° display capability', '["360° cylindrical displays", "Flexible and bendable modules", "Custom shapes and sizes", "Interactive touch capabilities"]'),

('Fine Pitch LED Display', 'fine-pitch', 'Ultra-high resolution fine pitch LED displays for close viewing applications such as broadcast studios and command centers.', 25000.00, '/assets/products/fine-pitch.jpg', 'Pixel Pitch: P0.9-P1.5
Ultra HD resolution
Seamless splicing', '["P0.9, P1.2, P1.5 pixel pitch options", "Ultra-high resolution and clarity", "Flicker-free technology", "Wide color gamut support"]')

ON CONFLICT (id) DO NOTHING;

-- 插入示例新闻数据
INSERT INTO news (title, content, summary, image_url, published) VALUES
('LED显示技术的最新发展趋势', '随着技术的不断进步，LED显示屏在分辨率、亮度和能效方面都有了显著提升。本文探讨了当前LED显示技术的最新发展方向...', '探索LED显示技术的最新发展和未来趋势', '/assets/news/news-1.jpg', true),

('户外LED显示屏在智慧城市中的应用', '智慧城市建设中，户外LED显示屏发挥着越来越重要的作用。它们不仅提供信息显示功能，还成为城市形象的重要载体...', '了解LED显示屏如何助力智慧城市建设', '/assets/news/news-2.jpg', true),

('室内小间距LED显示屏市场前景分析', '随着显示技术的发展，小间距LED显示屏在会议室、展厅等场所的应用越来越广泛。本文分析了其市场前景和发展趋势...', '分析小间距LED显示屏的市场前景和应用场景', '/assets/news/news-3.jpg', true)

ON CONFLICT (id) DO NOTHING;

-- 创建RLS (Row Level Security) 策略
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE inquiries ENABLE ROW LEVEL SECURITY;
ALTER TABLE news ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;

-- 产品表：允许读取已发布的产品
CREATE POLICY "Products are viewable by everyone" ON products
    FOR SELECT USING (status = 'active');

CREATE POLICY "Products are insertable by authenticated users" ON products
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Products are updatable by authenticated users" ON products
    FOR UPDATE USING (auth.role() = 'authenticated');

-- 询盘表：允许插入，管理员可查看
CREATE POLICY "Inquiries are insertable by everyone" ON inquiries
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Inquiries are viewable by authenticated users" ON inquiries
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Inquiries are updatable by authenticated users" ON inquiries
    FOR UPDATE USING (auth.role() = 'authenticated');

-- 新闻表：已发布的新闻所有人可看
CREATE POLICY "Published news are viewable by everyone" ON news
    FOR SELECT USING (published = true);

CREATE POLICY "News are manageable by authenticated users" ON news
    FOR ALL USING (auth.role() = 'authenticated');

-- 用户表：仅管理员可访问
CREATE POLICY "Admin users are manageable by service role only" ON admin_users
    FOR ALL USING (auth.role() = 'service_role');

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为所有表添加更新时间触发器
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inquiries_updated_at BEFORE UPDATE ON inquiries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_news_updated_at BEFORE UPDATE ON news
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_admin_users_updated_at BEFORE UPDATE ON admin_users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建索引以提高性能
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);
CREATE INDEX IF NOT EXISTS idx_inquiries_status ON inquiries(status);
CREATE INDEX IF NOT EXISTS idx_inquiries_created_at ON inquiries(created_at);
CREATE INDEX IF NOT EXISTS idx_news_published ON news(published);
CREATE INDEX IF NOT EXISTS idx_news_created_at ON news(created_at);

-- 完成设置
-- =====================================================
-- 数据库初始化完成！
-- 
-- 你现在可以使用以下功能：
-- 1. 产品管理 (products 表)
-- 2. 询盘管理 (inquiries 表) 
-- 3. 新闻管理 (news 表)
-- 4. 用户管理 (admin_users 表)
-- 
-- 所有表都启用了RLS安全策略
-- =====================================================
