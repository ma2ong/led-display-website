-- LED网站数据库架构
-- 创建产品表
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    specifications TEXT,
    price DECIMAL(10,2),
    image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建询盘表
CREATE TABLE IF NOT EXISTS inquiries (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    company TEXT,
    message TEXT NOT NULL,
    status TEXT DEFAULT 'new',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建新闻表
CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author TEXT DEFAULT 'Admin',
    status TEXT DEFAULT 'published',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建用户表（使用Supabase Auth）
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    username TEXT UNIQUE,
    role TEXT DEFAULT 'admin',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 插入示例产品数据
INSERT INTO products (name, category, description, specifications, price, image_url) VALUES
('P2.5室内LED显示屏', '室内LED', 'P2.5高清室内LED显示屏，适用于会议室、展厅等场所', '像素间距:2.5mm\n亮度:800cd/㎡\n刷新率:3840Hz', 1200.00, '/assets/products/indoor-led.jpg'),
('P10户外LED显示屏', '户外LED', 'P10高亮度户外LED显示屏，防水防尘，适用于户外广告', '像素间距:10mm\n亮度:6500cd/㎡\n防护等级:IP65', 800.00, '/assets/products/outdoor-led.jpg'),
('租赁LED显示屏', '租赁LED', '轻便易装的租赁LED显示屏，适用于演出、会议等临时场合', '重量:6.5kg/㎡\n厚度:75mm\n安装:快锁设计', 1500.00, '/assets/products/rental-led.jpg'),
('透明LED显示屏', '透明LED', '高透明度LED显示屏，不影响采光，适用于玻璃幕墙', '透明度:85%\n像素间距:3.9mm\n厚度:10mm', 2000.00, '/assets/products/transparent-led.jpg');

-- 启用行级安全策略
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE inquiries ENABLE ROW LEVEL SECURITY;
ALTER TABLE news ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- 产品表策略（公开读取，管理员写入）
CREATE POLICY "Products are viewable by everyone" ON products FOR SELECT USING (true);
CREATE POLICY "Products are insertable by authenticated users" ON products FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Products are updatable by authenticated users" ON products FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "Products are deletable by authenticated users" ON products FOR DELETE USING (auth.role() = 'authenticated');

-- 询盘表策略（公开插入，管理员查看）
CREATE POLICY "Inquiries are insertable by everyone" ON inquiries FOR INSERT WITH CHECK (true);
CREATE POLICY "Inquiries are viewable by authenticated users" ON inquiries FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Inquiries are updatable by authenticated users" ON inquiries FOR UPDATE USING (auth.role() = 'authenticated');

-- 新闻表策略（公开读取已发布，管理员全权限）
CREATE POLICY "Published news are viewable by everyone" ON news FOR SELECT USING (status = 'published' OR auth.role() = 'authenticated');
CREATE POLICY "News are insertable by authenticated users" ON news FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "News are updatable by authenticated users" ON news FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "News are deletable by authenticated users" ON news FOR DELETE USING (auth.role() = 'authenticated');

-- 用户配置表策略
CREATE POLICY "User profiles are viewable by owner" ON user_profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "User profiles are insertable by owner" ON user_profiles FOR INSERT WITH CHECK (auth.uid() = id);
CREATE POLICY "User profiles are updatable by owner" ON user_profiles FOR UPDATE USING (auth.uid() = id);