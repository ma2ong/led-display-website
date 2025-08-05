#!/usr/bin/env python3
"""
初始化完整的中文后台管理系统数据库
"""

import sqlite3
import json
from datetime import datetime
from werkzeug.security import generate_password_hash

def init_complete_database():
    print("🗑️  删除现有数据库...")
    import os
    if os.path.exists('complete_admin.db'):
        os.remove('complete_admin.db')
    
    print("📊 创建数据库表...")
    conn = sqlite3.connect('complete_admin.db')
    cursor = conn.cursor()
    
    # 用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    print("✓ 用户表创建完成")
    
    # 页面内容管理表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS page_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_name TEXT NOT NULL,
            section_name TEXT NOT NULL,
            content_type TEXT NOT NULL DEFAULT 'text',
            content_data TEXT,
            image_url TEXT,
            video_url TEXT,
            parameters TEXT,
            sort_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ 页面内容表创建完成")
    
    # 产品表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            specifications TEXT,
            image_url TEXT,
            video_url TEXT,
            price_range TEXT,
            features TEXT,
            applications TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ 产品表创建完成")
    
    # 询盘表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            company TEXT,
            phone TEXT,
            country TEXT,
            product_interest TEXT,
            message TEXT,
            status TEXT DEFAULT 'new',
            assigned_to TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ 询盘表创建完成")
    
    # 新闻表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT,
            summary TEXT,
            content TEXT,
            author TEXT,
            image_url TEXT,
            video_url TEXT,
            tags TEXT,
            publish_date DATE,
            is_published BOOLEAN DEFAULT 0,
            is_featured BOOLEAN DEFAULT 0,
            views INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ 新闻表创建完成")
    
    # 系统设置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT,
            setting_type TEXT DEFAULT 'text',
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ 系统设置表创建完成")
    
    # 插入默认管理员用户
    admin_password = generate_password_hash('admin123')
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, role, is_active)
        VALUES (?, ?, ?, ?, ?)
    ''', ('admin', 'admin@lianjin-led.com', admin_password, 'admin', 1))
    print("✓ 默认管理员用户创建完成")
    
    # 插入示例产品数据
    sample_products = [
        {
            'name': 'P2.5室内高清LED显示屏',
            'category': '室内显示屏',
            'description': '高分辨率室内LED显示屏，适用于会议室、展厅等场所',
            'specifications': '像素间距：2.5mm\n分辨率：160000点/㎡\n亮度：800-1200cd/㎡\n刷新率：≥3840Hz',
            'price_range': '¥800-1200/㎡',
            'features': '高清显示,低功耗,长寿命,易维护',
            'applications': '会议室,展厅,监控中心,广播电视'
        },
        {
            'name': 'P10户外全彩LED显示屏',
            'category': '户外显示屏',
            'description': '防水防尘户外LED显示屏，适用于广告牌、体育场馆等',
            'specifications': '像素间距：10mm\n分辨率：10000点/㎡\n亮度：≥6500cd/㎡\n防护等级：IP65',
            'price_range': '¥400-600/㎡',
            'features': '高亮度,防水防尘,节能环保,远程控制',
            'applications': '户外广告,体育场馆,交通诱导,商业广场'
        }
    ]
    
    for product in sample_products:
        cursor.execute('''
            INSERT INTO products (name, category, description, specifications, price_range, features, applications, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product['name'], product['category'], product['description'],
            product['specifications'], product['price_range'], 
            product['features'], product['applications'], 1
        ))
    print("✓ 示例产品数据插入完成")
    
    # 插入示例询盘数据
    sample_inquiries = [
        {
            'name': '张先生',
            'email': 'zhang@example.com',
            'company': '某科技有限公司',
            'phone': '13800138000',
            'country': '中国',
            'product_interest': 'P2.5室内显示屏',
            'message': '需要采购会议室用的LED显示屏，请提供详细报价',
            'status': 'new'
        },
        {
            'name': 'John Smith',
            'email': 'john@example.com',
            'company': 'ABC Corp',
            'phone': '+1-555-0123',
            'country': '美国',
            'product_interest': 'P10户外显示屏',
            'message': 'Interested in outdoor LED displays for advertising',
            'status': 'processing'
        }
    ]
    
    for inquiry in sample_inquiries:
        cursor.execute('''
            INSERT INTO inquiries (name, email, company, phone, country, product_interest, message, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            inquiry['name'], inquiry['email'], inquiry['company'],
            inquiry['phone'], inquiry['country'], inquiry['product_interest'],
            inquiry['message'], inquiry['status']
        ))
    print("✓ 示例询盘数据插入完成")
    
    # 插入示例新闻数据
    sample_news = [
        {
            'title': '联进LED荣获2024年度优秀供应商奖',
            'category': '公司新闻',
            'summary': '我公司凭借优质的产品和服务，荣获行业协会颁发的优秀供应商奖',
            'content': '详细新闻内容...',
            'author': '市场部',
            'tags': '获奖,荣誉,供应商',
            'publish_date': '2024-01-15',
            'is_published': 1,
            'is_featured': 1
        },
        {
            'title': '新品发布：超高清P1.25小间距LED显示屏',
            'category': '产品发布',
            'summary': '我公司最新推出P1.25超高清小间距LED显示屏，画质更清晰',
            'content': '产品详细介绍...',
            'author': '技术部',
            'tags': '新品,小间距,高清',
            'publish_date': '2024-01-10',
            'is_published': 1,
            'is_featured': 0
        }
    ]
    
    for news in sample_news:
        cursor.execute('''
            INSERT INTO news (title, category, summary, content, author, tags, publish_date, is_published, is_featured)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            news['title'], news['category'], news['summary'],
            news['content'], news['author'], news['tags'],
            news['publish_date'], news['is_published'], news['is_featured']
        ))
    print("✓ 示例新闻数据插入完成")
    
    # 插入示例页面内容
    sample_page_content = [
        {
            'page_name': 'home',
            'section_name': '首页横幅',
            'content_type': 'mixed',
            'content_data': '专业LED显示屏解决方案提供商',
            'image_url': '/assets/images/hero-banner.jpg',
            'parameters': '{"background_color": "#1a1a1a", "text_color": "#ffffff"}',
            'sort_order': 1,
            'is_active': 1
        },
        {
            'page_name': 'about',
            'section_name': '公司简介',
            'content_type': 'text',
            'content_data': '联进LED显示屏有限公司成立于2010年，专注于LED显示屏的研发、生产和销售...',
            'parameters': '{"font_size": "16px", "line_height": "1.6"}',
            'sort_order': 1,
            'is_active': 1
        },
        {
            'page_name': 'products',
            'section_name': '产品展示',
            'content_type': 'mixed',
            'content_data': '我们提供全系列LED显示屏产品',
            'image_url': '/assets/images/products-showcase.jpg',
            'parameters': '{"layout": "grid", "columns": 3}',
            'sort_order': 1,
            'is_active': 1
        }
    ]
    
    for content in sample_page_content:
        cursor.execute('''
            INSERT INTO page_content (page_name, section_name, content_type, content_data, image_url, parameters, sort_order, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            content['page_name'], content['section_name'], content['content_type'],
            content['content_data'], content.get('image_url', ''), content['parameters'],
            content['sort_order'], content['is_active']
        ))
    print("✓ 示例页面内容插入完成")
    
    # 插入系统设置
    system_settings = [
        ('site_title', '联进LED显示屏有限公司', 'text', '网站标题'),
        ('site_description', '专业LED显示屏解决方案提供商', 'text', '网站描述'),
        ('contact_email', 'info@lianjin-led.com', 'email', '联系邮箱'),
        ('contact_phone', '+86-755-12345678', 'text', '联系电话'),
        ('company_address', '深圳市宝安区某某工业园', 'text', '公司地址'),
        ('backup_frequency', '7', 'number', '备份频率（天）'),
        ('max_upload_size', '10', 'number', '最大上传文件大小（MB）')
    ]
    
    for setting in system_settings:
        cursor.execute('''
            INSERT INTO system_settings (setting_key, setting_value, setting_type, description)
            VALUES (?, ?, ?, ?)
        ''', setting)
    print("✓ 系统设置插入完成")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 完整的中文后台管理系统数据库初始化成功！")
    print("\n📋 登录信息:")
    print("   用户名: admin")
    print("   密码: admin123")
    print("\n🚀 现在可以运行: python complete_chinese_admin.py")

if __name__ == '__main__':
    init_complete_database()