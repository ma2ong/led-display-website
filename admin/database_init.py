#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Admin Database Initialization
"""

import sqlite3
from werkzeug.security import generate_password_hash

def init_enhanced_db():
    """初始化增强版数据库"""
    conn = sqlite3.connect('enhanced_admin.db')
    cursor = conn.cursor()
    
    # 管理员表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # 页面内容表 - 核心表，存储所有页面的内容
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS page_contents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_name TEXT NOT NULL,
            section_name TEXT NOT NULL,
            content_type TEXT NOT NULL,
            title_en TEXT,
            title_zh TEXT,
            subtitle_en TEXT,
            subtitle_zh TEXT,
            content_en TEXT,
            content_zh TEXT,
            image_url TEXT,
            video_url TEXT,
            link_url TEXT,
            parameters TEXT,
            sort_order INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 产品表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_en TEXT NOT NULL,
            name_zh TEXT NOT NULL,
            category TEXT NOT NULL,
            description_en TEXT,
            description_zh TEXT,
            specifications TEXT,
            features TEXT,
            images TEXT,
            videos TEXT,
            price REAL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 新闻表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title_en TEXT NOT NULL,
            title_zh TEXT NOT NULL,
            content_en TEXT,
            content_zh TEXT,
            category TEXT,
            image TEXT,
            author TEXT,
            status TEXT DEFAULT 'published',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 案例表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title_en TEXT NOT NULL,
            title_zh TEXT NOT NULL,
            description_en TEXT,
            description_zh TEXT,
            category TEXT,
            location TEXT,
            client TEXT,
            images TEXT,
            project_date DATE,
            status TEXT DEFAULT 'published',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 解决方案表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title_en TEXT NOT NULL,
            title_zh TEXT NOT NULL,
            description_en TEXT,
            description_zh TEXT,
            category TEXT,
            image TEXT,
            features TEXT,
            applications TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 询盘表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            company TEXT,
            phone TEXT,
            product_interest TEXT,
            message TEXT,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            handled_by TEXT,
            handled_at TIMESTAMP
        )
    ''')
    
    # 网站设置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 媒体文件表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS media_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_size INTEGER,
            mime_type TEXT,
            file_path TEXT NOT NULL,
            uploaded_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建默认管理员
    cursor.execute('SELECT COUNT(*) FROM admins')
    if cursor.fetchone()[0] == 0:
        default_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO admins (username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin', default_password, 'admin@lianjinled.com', 'super_admin'))
    
    # 插入默认页面内容结构
    default_page_contents = [
        # Home页面内容
        ('home', 'hero', 'hero_section', 'LED Display Solutions', 'LED显示屏解决方案', 
         'Professional LED Display Technology', '专业LED显示技术', 
         'Leading manufacturer of high-quality LED displays', '高品质LED显示屏领先制造商', '', '', '', '', 1),
        ('home', 'features', 'feature_list', 'Our Features', '我们的特色', '', '', 
         'High Quality, Innovation, Service', '高品质、创新、服务', '', '', '', '', 2),
        ('home', 'products', 'product_showcase', 'Our Products', '我们的产品', '', '', 
         'Complete range of LED display solutions', '完整的LED显示屏解决方案', '', '', '', '', 3),
        
        # About页面内容
        ('about', 'company', 'company_intro', 'About Lianjin LED', '关于联锦LED', 
         'Leading LED Display Manufacturer', '领先的LED显示屏制造商',
         'Professional LED display solutions provider', '专业LED显示屏解决方案提供商', '', '', '', '', 1),
        ('about', 'history', 'company_history', 'Our History', '我们的历史', '', '',
         'Founded in 2010, continuous innovation', '成立于2010年，持续创新', '', '', '', '', 2),
        ('about', 'team', 'team_intro', 'Our Team', '我们的团队', '', '',
         'Professional R&D and service team', '专业的研发和服务团队', '', '', '', '', 3),
        
        # Products页面内容
        ('products', 'categories', 'product_categories', 'Product Categories', '产品分类', '', '',
         'Complete LED display product line', '完整的LED显示屏产品线', '', '', '', '', 1),
        ('products', 'features', 'product_features', 'Product Features', '产品特色', '', '',
         'High quality, reliability, innovation', '高品质、可靠性、创新', '', '', '', '', 2),
        
        # Solutions页面内容
        ('solutions', 'applications', 'solution_apps', 'Application Solutions', '应用解决方案', '', '',
         'Customized solutions for different industries', '针对不同行业的定制解决方案', '', '', '', '', 1),
        ('solutions', 'services', 'solution_services', 'Our Services', '我们的服务', '', '',
         'Complete pre-sales and after-sales service', '完整的售前售后服务', '', '', '', '', 2),
        
        # Cases页面内容
        ('cases', 'showcase', 'case_showcase', 'Success Cases', '成功案例', '', '',
         'Successful project implementations worldwide', '全球成功项目实施', '', '', '', '', 1),
        ('cases', 'industries', 'case_industries', 'Industry Applications', '行业应用', '', '',
         'Various industry application cases', '各行业应用案例', '', '', '', '', 2),
        
        # News页面内容
        ('news', 'latest', 'latest_news', 'Latest News', '最新资讯', '', '',
         'Industry news and company updates', '行业资讯和公司动态', '', '', '', '', 1),
        ('news', 'events', 'company_events', 'Company Events', '公司活动', '', '',
         'Exhibition and event participation', '展会和活动参与', '', '', '', '', 2),
        
        # Support页面内容
        ('support', 'technical', 'tech_support', 'Technical Support', '技术支持', '', '',
         'Professional technical support service', '专业技术支持服务', '', '', '', '', 1),
        ('support', 'documentation', 'support_docs', 'Documentation', '技术文档', '', '',
         'Complete product documentation', '完整的产品文档', '', '', '', '', 2),
        
        # Contact页面内容
        ('contact', 'info', 'contact_info', 'Contact Information', '联系信息', '', '',
         'Get in touch with us', '与我们联系', '', '', '', '', 1),
        ('contact', 'form', 'contact_form', 'Contact Form', '联系表单', '', '',
         'Send us your inquiry', '发送您的询问', '', '', '', '', 2)
    ]
    
    for content in default_page_contents:
        cursor.execute('''
            INSERT OR IGNORE INTO page_contents (
                page_name, section_name, content_type, title_en, title_zh,
                subtitle_en, subtitle_zh, content_en, content_zh,
                image_url, video_url, link_url, parameters, sort_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', content)
    
    # 插入默认产品数据
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        default_products = [
            ('Fine Pitch LED Display', '小间距LED显示屏', 'fine-pitch', 
             'Ultra-high resolution displays with pixel pitches from P0.9 to P1.56',
             '像素间距从P0.9到P1.56的超高分辨率显示屏',
             'Pixel Pitch: P0.9-P1.56\nResolution: 4K/8K\nBrightness: 600-1200 nits',
             '4K/8K Resolution, Seamless Splicing, High Refresh Rate',
             'assets/products/fine-pitch-led.jpg', '', 0, 'active'),
            
            ('Outdoor LED Display', '户外LED显示屏', 'outdoor',
             'Weather-resistant displays for outdoor advertising and information',
             '适用于户外广告和信息显示的防风雨显示屏',
             'Pixel Pitch: P3-P10\nBrightness: 5000-8000 nits\nIP Rating: IP65',
             'IP65 Waterproof, High Brightness, Energy Efficient',
             'assets/products/outdoor-led.jpg', '', 0, 'active'),
            
            ('Indoor LED Display', '室内LED显示屏', 'indoor',
             'High-quality displays for indoor commercial and corporate applications',
             '适用于室内商业和企业应用的高质量显示屏',
             'Pixel Pitch: P1.25-P4\nBrightness: 800-1500 nits\nRefresh Rate: 1920-3840Hz',
             'Full Color Display, Easy Installation, Low Maintenance',
             'assets/products/indoor-led.jpg', '', 0, 'active')
        ]
        
        for product in default_products:
            cursor.execute('''
                INSERT INTO products (
                    name_en, name_zh, category, description_en, description_zh,
                    specifications, features, images, videos, price, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', product)
    
    conn.commit()
    conn.close()
    print("✅ Enhanced database initialized successfully!")

if __name__ == '__main__':
    init_enhanced_db()