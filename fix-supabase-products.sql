-- Supabase产品表修复脚本
-- 在Supabase SQL Editor中执行此脚本

-- 1. 检查当前表结构
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'products' 
ORDER BY ordinal_position;

-- 2. 删除现有表和策略（如果存在问题）
DROP POLICY IF EXISTS "Products are viewable by everyone" ON products;
DROP POLICY IF EXISTS "Products are insertable by everyone" ON products;
DROP POLICY IF EXISTS "Products are insertable by authenticated users" ON products;
DROP POLICY IF EXISTS "Products are updatable by authenticated users" ON products;
DROP POLICY IF EXISTS "Products are deletable by authenticated users" ON products;

DROP TABLE IF EXISTS products CASCADE;

-- 3. 重新创建products表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    specifications TEXT,
    price NUMERIC(10,2),
    image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. 启用行级安全策略
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- 5. 创建宽松的策略（允许所有操作）
CREATE POLICY "Enable all operations for products" 
ON products FOR ALL 
USING (true) 
WITH CHECK (true);

-- 6. 插入测试数据
INSERT INTO products (name, category, description, specifications, price, image_url) VALUES
('P2.5室内LED显示屏', 'indoor', 'P2.5高清室内LED显示屏，适用于会议室、展厅等场所', '像素间距:2.5mm
亮度:800cd/㎡
刷新率:3840Hz', 1200.00, '/assets/products/indoor-led.jpg'),

('P10户外LED显示屏', 'outdoor', 'P10高亮度户外LED显示屏，防水防尘，适用于户外广告', '像素间距:10mm
亮度:6500cd/㎡
防护等级:IP65', 800.00, '/assets/products/outdoor-led.jpg'),

('租赁LED显示屏', 'rental', '轻便易装的租赁LED显示屏，适用于演出、会议等临时场合', '重量:6.5kg/㎡
厚度:75mm
安装:快锁设计', 1500.00, '/assets/products/rental-led.jpg'),

('透明LED显示屏', 'creative', '高透明度LED显示屏，不影响采光，适用于玻璃幕墙', '透明度:85%
像素间距:3.9mm
厚度:10mm', 2000.00, '/assets/products/transparent-led.jpg'),

('小间距LED显示屏P1.25', 'indoor', '超高清小间距LED显示屏，适用于指挥中心', '像素间距:1.25mm
亮度:600cd/㎡
对比度:5000:1', 18000.00, '/assets/products/fine-pitch-p1.25.jpg'),

('柔性LED显示屏', 'creative', '可弯曲柔性LED显示屏，适用于弧形安装', '弯曲半径:R≥500mm
厚度:8mm
重量:5kg/㎡', 16000.00, '/assets/products/flexible-led.jpg');

-- 7. 验证数据插入
SELECT 
    COUNT(*) as total_products,
    COUNT(CASE WHEN category = 'indoor' THEN 1 END) as indoor_count,
    COUNT(CASE WHEN category = 'outdoor' THEN 1 END) as outdoor_count,
    COUNT(CASE WHEN category = 'rental' THEN 1 END) as rental_count,
    COUNT(CASE WHEN category = 'creative' THEN 1 END) as creative_count
FROM products;

-- 8. 显示所有产品
SELECT id, name, category, price, created_at FROM products ORDER BY created_at DESC;

-- 9. 测试插入权限
INSERT INTO products (name, category, description, price) VALUES
('测试产品', 'indoor', '这是一个测试产品，用于验证插入权限', 999.99);

-- 10. 验证测试插入
SELECT * FROM products WHERE name = '测试产品';

-- 11. 清理测试数据
DELETE FROM products WHERE name = '测试产品';

-- 完成提示
SELECT '✅ products表修复完成！现在可以正常进行读写操作。' as status;