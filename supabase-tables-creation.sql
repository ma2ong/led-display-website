-- LED显示屏网站 - Supabase数据库表创建脚本
-- 请将此代码复制到Supabase SQL Editor中执行

-- 删除现有表（如果存在）
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS inquiries CASCADE;
DROP TABLE IF EXISTS news CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 创建产品表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    price NUMERIC(10,2),
    image_url TEXT,
    specifications TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建询盘表
CREATE TABLE inquiries (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    company TEXT,
    message TEXT,
    status TEXT DEFAULT 'new',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建新闻表
CREATE TABLE news (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    author TEXT,
    status TEXT DEFAULT 'published',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'admin',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 插入LED产品示例数据
INSERT INTO products (name, category, description, price, image_url, specifications) VALUES
('室内LED显示屏P2.5', 'indoor', '高清室内LED显示屏，适用于会议室、展厅等场所', 8500.00, '/assets/products/indoor-p2.5.jpg', '像素间距：2.5mm
亮度：800cd/㎡
刷新率：3840Hz'),
('户外LED显示屏P10', 'outdoor', '高亮度户外LED显示屏，防水防尘，适用于户外广告', 12000.00, '/assets/products/outdoor-p10.jpg', '像素间距：10mm
亮度：6500cd/㎡
防护等级：IP65'),
('租赁LED显示屏P3.91', 'rental', '轻便租赁LED显示屏，快速安装，适用于舞台演出', 9800.00, '/assets/products/rental-p3.91.jpg', '像素间距：3.91mm
重量：6.5kg/㎡
安装：快锁设计'),
('创意LED显示屏', 'creative', '异形创意LED显示屏，可定制各种造型', 15000.00, '/assets/products/creative-led.jpg', '可定制形状
高刷新率
无缝拼接'),
('小间距LED显示屏P1.25', 'indoor', '超高清小间距LED显示屏，适用于指挥中心', 18000.00, '/assets/products/fine-pitch-p1.25.jpg', '像素间距：1.25mm
亮度：600cd/㎡
对比度：5000:1'),
('透明LED显示屏', 'creative', '透明LED显示屏，通透率高，适用于玻璃幕墙', 22000.00, '/assets/products/transparent-led.jpg', '通透率：85%
亮度：4000cd/㎡
厚度：10mm'),
('柔性LED显示屏', 'creative', '可弯曲柔性LED显示屏，适用于弧形安装', 16000.00, '/assets/products/flexible-led.jpg', '弯曲半径：R≥500mm
厚度：8mm
重量：5kg/㎡'),
('互动LED地砖屏', 'creative', '互动感应LED地砖屏，支持触控互动', 25000.00, '/assets/products/interactive-floor.jpg', '承重：2000kg/㎡
感应：红外感应
防护：IP65'),
('球形LED显示屏', 'creative', '360度球形LED显示屏，全方位显示', 35000.00, '/assets/products/sphere-led.jpg', '直径：1-5米可选
像素：P4-P10
控制：360度显示'),
('LED条形屏', 'indoor', '超长比例LED条形屏，适用于信息发布', 6800.00, '/assets/products/bar-led.jpg', '比例：32:9
分辨率：3840×1080
亮度：500cd/㎡'),
('户外LED广告牌', 'outdoor', '大型户外LED广告显示屏，高亮防水', 45000.00, '/assets/products/outdoor-billboard.jpg', '尺寸：6×3米
亮度：8000cd/㎡
寿命：100000小时'),
('LED舞台背景屏', 'rental', '专业舞台LED背景屏，快速搭建', 28000.00, '/assets/products/stage-led.jpg', '模块化设计
快速安装
高刷新率：7680Hz');

-- 插入新闻示例数据
INSERT INTO news (title, content, author, status) VALUES
('LED显示屏技术新突破', 'LED显示屏技术在2024年取得重大突破，像素密度和亮度都有显著提升，为用户带来更优质的视觉体验。我们的新一代产品采用了最新的封装技术，实现了更高的对比度和更广的色域。', 'admin', 'published'),
('公司荣获行业大奖', '我公司在LED显示屏行业评选中荣获最佳创新奖，这是对我们技术实力的认可。我们将继续致力于LED显示技术的创新发展，为客户提供更优质的产品和服务。', 'admin', 'published'),
('新产品发布会成功举办', '我公司新一代LED显示屏产品发布会在深圳成功举办，吸引了众多客户参与。新产品在亮度、对比度、能耗等方面都有显著改进，获得了客户的一致好评。', 'admin', 'published'),
('LED显示屏市场前景广阔', '根据最新市场研究报告，LED显示屏市场预计在未来五年内将保持快速增长，特别是在智慧城市和数字标牌领域需求旺盛。', 'admin', 'published'),
('环保LED技术获得认证', '我公司的环保LED显示屏技术获得了国际环保认证，产品在节能减排方面表现优异，符合绿色发展理念。', 'admin', 'published'),
('5G+LED显示屏应用案例', '我公司成功部署了多个5G+LED显示屏应用案例，实现了远程实时控制和内容推送，为智慧城市建设提供了有力支持。', 'admin', 'published');

-- 插入管理员用户
INSERT INTO users (username, password, role) VALUES
('admin', 'admin123', 'admin');

-- 创建索引以提高查询性能
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_inquiries_status ON inquiries(status);
CREATE INDEX idx_news_status ON news(status);
CREATE INDEX idx_users_username ON users(username);

-- 验证表创建成功
SELECT 'products' as table_name, COUNT(*) as record_count FROM products
UNION ALL
SELECT 'inquiries' as table_name, COUNT(*) as record_count FROM inquiries
UNION ALL
SELECT 'news' as table_name, COUNT(*) as record_count FROM news
UNION ALL
SELECT 'users' as table_name, COUNT(*) as record_count FROM users;