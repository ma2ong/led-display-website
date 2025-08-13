-- =====================================================
-- 步骤3: 插入默认数据 (修正版)
-- =====================================================

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

-- 插入一些示例产品数据（如果不存在）- 去掉status字段
INSERT INTO products (name, category, description, price, image_url) VALUES
('P2.5室内高清显示屏', 'indoor', '适用于会议室、展厅的高清LED显示屏', 8500.00, '/assets/products/indoor-p2.5.jpg'),
('P10户外大屏幕', 'outdoor', '适用于广告牌、体育场的户外LED大屏', 12000.00, '/assets/products/outdoor-p10.jpg'),
('P3.91租赁显示屏', 'rental', '适用于演出、会议的便携式LED显示屏', 9800.00, '/assets/products/rental-p3.91.jpg')
ON CONFLICT (name) DO NOTHING;

-- 插入示例新闻数据
INSERT INTO news (title, content, summary, author, published) VALUES
('LED显示技术发展趋势2025', 'LED显示技术在2025年将迎来新的发展机遇，小间距技术不断突破，透明显示应用场景扩大...', '探讨2025年LED显示技术的发展方向和市场趋势', 'Admin', true),
('户外LED显示屏的安装注意事项', '户外LED显示屏的安装需要考虑防水、散热、结构稳定性等多个因素...', '户外LED显示屏安装的专业指导', 'Admin', true),
('小间距LED显示屏市场分析', '小间距LED显示屏市场在近年来快速发展，主要应用于高端会议室、监控中心等场所...', '分析小间距LED显示屏的市场现状和前景', 'Admin', true)
ON CONFLICT (title) DO NOTHING;
