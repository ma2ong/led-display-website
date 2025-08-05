#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Upgrade Script
升级数据库结构以支持更多功能
"""

import sqlite3
import os
from datetime import datetime

def upgrade_database():
    """升级数据库结构"""
    conn = sqlite3.connect('led_admin.db')
    cursor = conn.cursor()
    
    print("🔄 Upgrading database structure...")
    
    # 1. 页面内容管理表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS page_contents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_name TEXT NOT NULL,
            section_name TEXT NOT NULL,
            content_type TEXT NOT NULL,  -- text, image, video, html
            content_en TEXT,
            content_zh TEXT,
            image_url TEXT,
            video_url TEXT,
            sort_order INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. 媒体文件管理表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS media_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            file_type TEXT NOT NULL,  -- image, video, document
            file_size INTEGER,
            mime_type TEXT,
            file_path TEXT NOT NULL,
            alt_text TEXT,
            description TEXT,
            uploaded_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 3. 网站配置表 (扩展)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS site_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,  -- general, seo, social, contact
            key TEXT NOT NULL,
            value TEXT,
            description TEXT,
            data_type TEXT DEFAULT 'text',  -- text, number, boolean, json
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 4. SEO设置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seo_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_name TEXT NOT NULL,
            title_en TEXT,
            title_zh TEXT,
            description_en TEXT,
            description_zh TEXT,
            keywords_en TEXT,
            keywords_zh TEXT,
            og_image TEXT,
            canonical_url TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 5. 导航菜单表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS navigation_menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER DEFAULT 0,
            name_en TEXT NOT NULL,
            name_zh TEXT NOT NULL,
            url TEXT,
            icon TEXT,
            sort_order INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 6. 产品分类表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_en TEXT NOT NULL,
            name_zh TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            description_en TEXT,
            description_zh TEXT,
            image TEXT,
            sort_order INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 7. 产品图片表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            image_url TEXT NOT NULL,
            alt_text TEXT,
            sort_order INTEGER DEFAULT 0,
            is_primary BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # 8. 产品视频表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            video_url TEXT NOT NULL,
            thumbnail_url TEXT,
            title TEXT,
            description TEXT,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # 9. 用户活动日志表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            table_name TEXT,
            record_id INTEGER,
            old_values TEXT,
            new_values TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 10. 系统设置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            description TEXT,
            category TEXT DEFAULT 'general',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 插入默认页面内容
    default_pages = [
        ('homepage', 'hero_title', 'text', 'Professional LED Display Solutions', '专业LED显示屏解决方案'),
        ('homepage', 'hero_subtitle', 'text', 'Leading provider of high-quality LED displays for indoor, outdoor, and rental applications worldwide', '全球领先的室内、户外和租赁LED显示屏高质量供应商'),
        ('about', 'company_intro', 'text', 'Lianjin LED Display Technology Co., Ltd. is a leading manufacturer of professional LED display solutions.', '联锦LED显示技术有限公司是专业LED显示解决方案的领先制造商。'),
        ('about', 'company_history', 'text', 'Founded in 2007, we have over 17 years of experience in LED display industry.', '成立于2007年，我们在LED显示行业拥有超过17年的经验。'),
        ('contact', 'office_address', 'text', 'Building A, LED Industrial Park, Nanshan District, Shenzhen, China', '中国深圳市南山区LED工业园A栋'),
        ('contact', 'phone_sales', 'text', '+86-755-1234-5678', '+86-755-1234-5678'),
        ('contact', 'email_sales', 'text', 'sales@lianjinled.com', 'sales@lianjinled.com')
    ]
    
    for page_name, section_name, content_type, content_en, content_zh in default_pages:
        cursor.execute('''
            INSERT OR IGNORE INTO page_contents 
            (page_name, section_name, content_type, content_en, content_zh)
            VALUES (?, ?, ?, ?, ?)
        ''', (page_name, section_name, content_type, content_en, content_zh))
    
    # 插入默认产品分类
    default_categories = [
        ('Fine Pitch LED', '小间距LED', 'fine-pitch', 'Ultra-high resolution displays', '超高分辨率显示屏'),
        ('Outdoor LED', '户外LED', 'outdoor', 'Weather-resistant outdoor displays', '防风雨户外显示屏'),
        ('Indoor LED', '室内LED', 'indoor', 'High-quality indoor displays', '高质量室内显示屏'),
        ('Rental LED', '租赁LED', 'rental', 'Portable event displays', '便携式活动显示屏'),
        ('Transparent LED', '透明LED', 'transparent', 'See-through display technology', '透明显示技术'),
        ('Creative LED', '创意LED', 'creative', 'Custom shaped displays', '定制形状显示屏')
    ]
    
    for name_en, name_zh, slug, desc_en, desc_zh in default_categories:
        cursor.execute('''
            INSERT OR IGNORE INTO product_categories 
            (name_en, name_zh, slug, description_en, description_zh)
            VALUES (?, ?, ?, ?, ?)
        ''', (name_en, name_zh, slug, desc_en, desc_zh))
    
    # 插入默认导航菜单
    default_navigation = [
        (0, 'Home', '首页', 'homepage.html', 'fas fa-home', 1),
        (0, 'About', '关于我们', 'about.html', 'fas fa-info-circle', 2),
        (0, 'Products', '产品', '#', 'fas fa-tv', 3),
        (3, 'Fine Pitch LED', '小间距LED', 'fine-pitch.html', '', 1),
        (3, 'Outdoor LED', '户外LED', 'outdoor.html', '', 2),
        (3, 'Indoor LED', '室内LED', 'indoor.html', '', 3),
        (3, 'Rental LED', '租赁LED', 'rental.html', '', 4),
        (3, 'Transparent LED', '透明LED', 'transparent.html', '', 5),
        (3, 'Creative LED', '创意LED', 'creative.html', '', 6),
        (0, 'Solutions', '解决方案', 'solutions.html', 'fas fa-cogs', 4),
        (0, 'Cases', '案例', 'cases.html', 'fas fa-briefcase', 5),
        (0, 'News', '新闻', 'news.html', 'fas fa-newspaper', 6),
        (0, 'Support', '支持', 'support.html', 'fas fa-headset', 7),
        (0, 'Contact', '联系我们', 'contact.html', 'fas fa-envelope', 8)
    ]
    
    for parent_id, name_en, name_zh, url, icon, sort_order in default_navigation:
        cursor.execute('''
            INSERT OR IGNORE INTO navigation_menu 
            (parent_id, name_en, name_zh, url, icon, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (parent_id, name_en, name_zh, url, icon, sort_order))
    
    # 插入默认SEO设置
    default_seo = [
        ('homepage', 'Professional LED Display Solutions | Lianjin LED', '专业LED显示屏解决方案 | 联锦LED', 
         'Leading manufacturer of high-quality LED displays for indoor, outdoor, and rental applications worldwide.',
         '全球领先的室内、户外和租赁LED显示屏高质量制造商。',
         'LED display, LED screen, digital signage, outdoor LED, indoor LED',
         'LED显示屏, LED屏幕, 数字标牌, 户外LED, 室内LED'),
        ('about', 'About Us - LED Display Manufacturer | Lianjin LED', '关于我们 - LED显示屏制造商 | 联锦LED',
         'Learn about Lianjin LED Display Technology - 17+ years of LED display manufacturing experience.',
         '了解联锦LED显示技术 - 17年以上LED显示屏制造经验。',
         'LED manufacturer, LED display company, LED screen factory',
         'LED制造商, LED显示屏公司, LED屏幕工厂'),
        ('contact', 'Contact Us - Get LED Display Quote | Lianjin LED', '联系我们 - 获取LED显示屏报价 | 联锦LED',
         'Contact Lianjin LED for professional LED display solutions and free quotes.',
         '联系联锦LED获取专业LED显示屏解决方案和免费报价。',
         'LED display contact, LED screen quote, LED display support',
         'LED显示屏联系, LED屏幕报价, LED显示屏支持')
    ]
    
    for page_name, title_en, title_zh, desc_en, desc_zh, keywords_en, keywords_zh in default_seo:
        cursor.execute('''
            INSERT OR IGNORE INTO seo_settings 
            (page_name, title_en, title_zh, description_en, description_zh, keywords_en, keywords_zh)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (page_name, title_en, title_zh, desc_en, desc_zh, keywords_en, keywords_zh))
    
    # 插入默认系统设置
    default_system_settings = [
        ('site_maintenance', 'false', 'Enable maintenance mode', 'system'),
        ('max_upload_size', '16777216', 'Maximum file upload size in bytes (16MB)', 'upload'),
        ('allowed_image_types', 'jpg,jpeg,png,gif,webp', 'Allowed image file extensions', 'upload'),
        ('allowed_video_types', 'mp4,avi,mov,wmv', 'Allowed video file extensions', 'upload'),
        ('backup_enabled', 'true', 'Enable automatic database backups', 'system'),
        ('backup_frequency', 'daily', 'Backup frequency (daily, weekly, monthly)', 'system')
    ]
    
    for key, value, description, category in default_system_settings:
        cursor.execute('''
            INSERT OR IGNORE INTO system_settings (key, value, description, category)
            VALUES (?, ?, ?, ?)
        ''', (key, value, description, category))
    
    conn.commit()
    conn.close()
    
    print("✅ Database upgrade completed successfully!")
    print("📊 New tables created:")
    print("   - page_contents (页面内容管理)")
    print("   - media_files (媒体文件管理)")
    print("   - site_config (网站配置)")
    print("   - seo_settings (SEO设置)")
    print("   - navigation_menu (导航菜单)")
    print("   - product_categories (产品分类)")
    print("   - product_images (产品图片)")
    print("   - product_videos (产品视频)")
    print("   - activity_logs (活动日志)")
    print("   - system_settings (系统设置)")

if __name__ == '__main__':
    upgrade_database()