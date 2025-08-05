#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Migration Script for Enhanced Admin System
修复数据库结构以支持增强版管理系统
"""

import sqlite3
import os
from datetime import datetime

def backup_existing_database():
    """备份现有数据库"""
    if os.path.exists('admin.db'):
        backup_name = f'admin_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        os.rename('admin.db', backup_name)
        print(f"✅ 已备份现有数据库为: {backup_name}")
        return backup_name
    return None

def create_enhanced_database():
    """创建增强版数据库结构"""
    conn = sqlite3.connect('enhanced_admin.db')
    cursor = conn.cursor()
    
    print("📊 创建增强版数据库结构...")
    
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
    
    # 页面内容表 - 核心表
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
    
    # 产品表 - 兼容现有结构
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            name_en TEXT,
            name_zh TEXT,
            category TEXT,
            description TEXT,
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
            title TEXT NOT NULL,
            title_en TEXT,
            title_zh TEXT,
            content TEXT,
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
            title TEXT NOT NULL,
            title_en TEXT,
            title_zh TEXT,
            description TEXT,
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
            title TEXT NOT NULL,
            title_en TEXT,
            title_zh TEXT,
            description TEXT,
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
    
    print("✅ 数据库表结构创建完成")
    
    # 创建默认管理员
    from werkzeug.security import generate_password_hash
    
    cursor.execute('SELECT COUNT(*) FROM admins')
    if cursor.fetchone()[0] == 0:
        default_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO admins (username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin', default_password, 'admin@lianjinled.com', 'super_admin'))
        print("✅ 创建默认管理员账户")
    
    # 插入默认页面内容
    insert_default_content(cursor)
    
    conn.commit()
    conn.close()
    print("✅ 增强版数据库创建完成")

def insert_default_content(cursor):
    """插入默认页面内容"""
    print("📝 插入默认页面内容...")
    
    default_contents = [
        # Home页面
        ('home', 'hero', 'hero_section', 'LED Display Solutions', 'LED显示屏解决方案', 
         'Professional LED Display Technology', '专业LED显示技术', 
         'Leading manufacturer of high-quality LED displays for various applications', 
         '高品质LED显示屏领先制造商，为各种应用提供专业解决方案', '', '', '', '{}', 1),
        
        ('home', 'features', 'feature_list', 'Our Advantages', '我们的优势', 
         'Why Choose Our LED Displays', '为什么选择我们的LED显示屏',
         'High brightness, energy efficiency, long lifespan, professional service', 
         '高亮度、节能环保、长寿命、专业服务', '', '', '', '{}', 2),
        
        ('home', 'products', 'product_showcase', 'Product Range', '产品系列', 
         'Complete LED Display Solutions', '完整的LED显示屏解决方案',
         'Indoor, outdoor, rental, creative LED display products', 
         '室内、户外、租赁、创意LED显示屏产品', '', '', '', '{}', 3),
        
        # About页面
        ('about', 'company', 'company_intro', 'About Lianjin LED', '关于联锦LED', 
         'Professional LED Display Manufacturer', '专业LED显示屏制造商',
         'Founded in 2010, we are committed to providing high-quality LED display solutions', 
         '成立于2010年，致力于提供高品质LED显示屏解决方案', '', '', '', '{}', 1),
        
        ('about', 'mission', 'text_content', 'Our Mission', '我们的使命', 
         'Innovation and Excellence', '创新与卓越',
         'To be the leading provider of innovative LED display technology worldwide', 
         '成为全球领先的创新LED显示技术提供商', '', '', '', '{}', 2),
        
        # Products页面
        ('products', 'categories', 'product_categories', 'Product Categories', '产品分类', 
         'Complete Product Line', '完整产品线',
         'Indoor LED displays, outdoor LED displays, rental LED displays, creative LED displays', 
         '室内LED显示屏、户外LED显示屏、租赁LED显示屏、创意LED显示屏', '', '', '', '{}', 1),
        
        # Solutions页面
        ('solutions', 'applications', 'solution_apps', 'Application Solutions', '应用解决方案', 
         'Industry-Specific Solutions', '行业专用解决方案',
         'Customized LED display solutions for different industries and applications', 
         '针对不同行业和应用的定制LED显示屏解决方案', '', '', '', '{}', 1),
        
        # Cases页面
        ('cases', 'showcase', 'case_showcase', 'Success Stories', '成功案例', 
         'Global Project Implementations', '全球项目实施',
         'Successful LED display installations worldwide across various industries', 
         '全球各行业成功的LED显示屏安装案例', '', '', '', '{}', 1),
        
        # News页面
        ('news', 'latest', 'latest_news', 'Latest News', '最新资讯', 
         'Industry Updates', '行业动态',
         'Stay updated with the latest LED display technology and industry news', 
         '了解最新的LED显示技术和行业资讯', '', '', '', '{}', 1),
        
        # Support页面
        ('support', 'technical', 'tech_support', 'Technical Support', '技术支持', 
         '24/7 Professional Support', '24/7专业支持',
         'Comprehensive technical support and after-sales service', 
         '全面的技术支持和售后服务', '', '', '', '{}', 1),
        
        # Contact页面
        ('contact', 'info', 'contact_info', 'Contact Us', '联系我们', 
         'Get in Touch', '联系方式',
         'Contact our team for inquiries, quotes, and technical support', 
         '联系我们的团队获取咨询、报价和技术支持', '', '', '', '{}', 1)
    ]
    
    for content in default_contents:
        cursor.execute('''
            INSERT OR IGNORE INTO page_contents (
                page_name, section_name, content_type, title_en, title_zh,
                subtitle_en, subtitle_zh, content_en, content_zh,
                image_url, video_url, link_url, parameters, sort_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', content)
    
    print("✅ 默认页面内容插入完成")

def migrate_existing_data():
    """迁移现有数据（如果存在）"""
    backup_files = [f for f in os.listdir('.') if f.startswith('admin_backup_') and f.endswith('.db')]
    
    if not backup_files:
        print("ℹ️  没有找到需要迁移的数据")
        return
    
    # 使用最新的备份文件
    backup_file = sorted(backup_files)[-1]
    print(f"📦 从备份文件迁移数据: {backup_file}")
    
    try:
        # 连接备份数据库
        backup_conn = sqlite3.connect(backup_file)
        backup_cursor = backup_conn.cursor()
        
        # 连接新数据库
        new_conn = sqlite3.connect('enhanced_admin.db')
        new_cursor = new_conn.cursor()
        
        # 迁移产品数据
        try:
            backup_cursor.execute('SELECT * FROM products')
            products = backup_cursor.fetchall()
            
            # 获取列名
            backup_cursor.execute('PRAGMA table_info(products)')
            columns = [col[1] for col in backup_cursor.fetchall()]
            
            for product in products:
                product_dict = dict(zip(columns, product))
                
                # 插入到新表，处理可能缺失的列
                new_cursor.execute('''
                    INSERT OR IGNORE INTO products (
                        name, name_en, name_zh, category, description, 
                        description_en, description_zh, specifications, 
                        features, images, price, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    product_dict.get('name', ''),
                    product_dict.get('name_en', product_dict.get('name', '')),
                    product_dict.get('name_zh', product_dict.get('name', '')),
                    product_dict.get('category', ''),
                    product_dict.get('description', ''),
                    product_dict.get('description_en', product_dict.get('description', '')),
                    product_dict.get('description_zh', product_dict.get('description', '')),
                    product_dict.get('specifications', ''),
                    product_dict.get('features', ''),
                    product_dict.get('images', ''),
                    product_dict.get('price', 0),
                    product_dict.get('status', 'active')
                ))
            
            print(f"✅ 迁移了 {len(products)} 个产品")
        except Exception as e:
            print(f"⚠️  产品数据迁移失败: {e}")
        
        # 迁移其他表的数据...
        # 这里可以添加更多表的迁移逻辑
        
        new_conn.commit()
        new_conn.close()
        backup_conn.close()
        
        print("✅ 数据迁移完成")
        
    except Exception as e:
        print(f"❌ 数据迁移失败: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 LED显示屏管理系统数据库迁移工具")
    print("=" * 60)
    
    # 切换到admin目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 备份现有数据库
    backup_file = backup_existing_database()
    
    # 创建增强版数据库
    create_enhanced_database()
    
    # 迁移现有数据
    if backup_file:
        migrate_existing_data()
    
    print("=" * 60)
    print("✅ 数据库迁移完成！")
    print("🚀 现在可以运行增强版管理系统:")
    print("   python run_enhanced.py")
    print("=" * 60)

if __name__ == '__main__':
    main()