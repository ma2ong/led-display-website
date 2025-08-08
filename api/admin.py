#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vercel部署的Flask管理系统API
Flask Admin System API for Vercel Deployment
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import json
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'complete_chinese_led_admin_2024'
app.config['JSON_AS_ASCII'] = False

# Enable CORS
CORS(app, origins=['*'], supports_credentials=True)

def init_complete_database():
    """初始化完整数据库结构"""
    conn = sqlite3.connect('/tmp/complete_admin.db')
    cursor = conn.cursor()
    
    # 管理员表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'admin',
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # 前端页面内容表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frontend_pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_name TEXT NOT NULL,
            section_name TEXT NOT NULL,
            content_type TEXT NOT NULL,
            title_zh TEXT,
            title_en TEXT,
            subtitle_zh TEXT,
            subtitle_en TEXT,
            content_zh TEXT,
            content_en TEXT,
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
            name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            specifications TEXT,
            features TEXT,
            images TEXT,
            price REAL,
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
    
    # 新闻表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            category TEXT,
            image TEXT,
            author TEXT,
            status TEXT DEFAULT 'published',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 系统设置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    # 插入默认前端页面内容
    insert_default_frontend_content(cursor)
    
    # 插入默认系统设置
    insert_default_settings(cursor)
    
    conn.commit()
    conn.close()

def insert_default_frontend_content(cursor):
    """插入默认前端页面内容"""
    default_contents = [
        # 首页内容
        ('home', 'hero', 'hero_section', 'LED显示屏解决方案', 'LED Display Solutions', 
         '专业LED显示技术', 'Professional LED Display Technology',
         '高品质LED显示屏，适用于各种应用场景', 'High-quality LED displays for various applications',
         '', '', '', '{}', 1),
        
        ('home', 'features', 'feature_list', '我们的优势', 'Our Advantages',
         '为什么选择我们', 'Why Choose Us',
         '高亮度、节能环保、长寿命、专业服务', 'High brightness, energy efficiency, long lifespan, professional service',
         '', '', '', '{}', 2),
        
        # 关于我们内容
        ('about', 'company', 'company_intro', '关于联锦LED', 'About Lianjin LED',
         '专业LED显示屏制造商', 'Professional LED Display Manufacturer',
         '自2010年以来的领先LED显示屏制造商，致力于提供高品质产品', 'Leading LED display manufacturer since 2010, committed to providing high-quality products',
         '', '', '', '{}', 1),
    ]
    
    for content in default_contents:
        cursor.execute('''
            INSERT OR IGNORE INTO frontend_pages (
                page_name, section_name, content_type, title_zh, title_en,
                subtitle_zh, subtitle_en, content_zh, content_en,
                image_url, video_url, link_url, parameters, sort_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', content)

def insert_default_settings(cursor):
    """插入默认系统设置"""
    default_settings = [
        ('site_name', '联锦LED显示屏', '网站名称'),
        ('site_description', '专业LED显示屏制造商', '网站描述'),
        ('contact_email', 'info@lianjinled.com', '联系邮箱'),
        ('contact_phone', '+86-755-12345678', '联系电话'),
        ('company_address', '深圳市南山区科技园', '公司地址')
    ]
    
    for setting in default_settings:
        cursor.execute('''
            INSERT OR IGNORE INTO system_settings (setting_key, setting_value, description)
            VALUES (?, ?, ?)
        ''', setting)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return jsonify({'status': 'error', 'message': '需要登录'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    conn = sqlite3.connect('/tmp/complete_admin.db')
    conn.row_factory = sqlite3.Row
    return conn

# 初始化数据库
init_complete_database()

# API路由
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """管理员登录API"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        conn = get_db_connection()
        admin = conn.execute(
            'SELECT * FROM admins WHERE username = ? AND status = "active"', (username,)
        ).fetchone()
        conn.close()
        
        if admin and check_password_hash(admin['password_hash'], password):
            session['admin_id'] = admin['id']
            session['admin_username'] = admin['username']
            session['admin_role'] = admin['role']
            
            # 更新最后登录时间
            conn = get_db_connection()
            conn.execute(
                'UPDATE admins SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                (admin['id'],)
            )
            conn.commit()
            conn.close()
            
            return jsonify({
                'status': 'success', 
                'message': '登录成功',
                'admin': {
                    'id': admin['id'],
                    'username': admin['username'],
                    'role': admin['role']
                }
            })
        else:
            return jsonify({'status': 'error', 'message': '用户名或密码错误'}), 401
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/dashboard')
@login_required
def admin_dashboard():
    """管理后台仪表盘数据"""
    try:
        conn = get_db_connection()
        
        # 获取统计数据
        stats = {
            'pages': 8,
            'contents': conn.execute('SELECT COUNT(*) FROM frontend_pages WHERE status = "active"').fetchone()[0],
            'products': conn.execute('SELECT COUNT(*) FROM products').fetchone()[0],
            'inquiries': conn.execute('SELECT COUNT(*) FROM inquiries').fetchone()[0],
            'news': conn.execute('SELECT COUNT(*) FROM news').fetchone()[0],
            'admins': conn.execute('SELECT COUNT(*) FROM admins').fetchone()[0]
        }
        
        # 获取最新询盘
        recent_inquiries = conn.execute('''
            SELECT * FROM inquiries 
            ORDER BY created_at DESC 
            LIMIT 5
        ''').fetchall()
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'stats': stats,
            'recent_inquiries': [dict(row) for row in recent_inquiries]
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/frontend/<page_name>')
@login_required
def get_frontend_content(page_name):
    """获取前端页面内容"""
    try:
        conn = get_db_connection()
        contents = conn.execute('''
            SELECT * FROM frontend_pages 
            WHERE page_name = ? 
            ORDER BY sort_order, id
        ''', (page_name,)).fetchall()
        conn.close()
        
        content_list = [dict(row) for row in contents]
        
        return jsonify({'status': 'success', 'contents': content_list})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/frontend/<page_name>', methods=['POST'])
@login_required
def update_frontend_content(page_name):
    """更新前端页面内容"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        
        # 更新或插入内容
        if data.get('id'):
            # 更新现有内容
            conn.execute('''
                UPDATE frontend_pages 
                SET title_zh = ?, subtitle_zh = ?, content_zh = ?, 
                    image_url = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                data.get('title_zh', ''),
                data.get('subtitle_zh', ''),
                data.get('content_zh', ''),
                data.get('image_url', ''),
                data['id']
            ))
        else:
            # 插入新内容
            conn.execute('''
                INSERT INTO frontend_pages 
                (page_name, section_name, content_type, title_zh, subtitle_zh, content_zh, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                page_name,
                data.get('section_name', ''),
                data.get('content_type', 'text_content'),
                data.get('title_zh', ''),
                data.get('subtitle_zh', ''),
                data.get('content_zh', ''),
                data.get('image_url', '')
            ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': '内容更新成功'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/products')
@login_required
def get_products():
    """获取产品列表"""
    try:
        conn = get_db_connection()
        products = conn.execute('''
            SELECT * FROM products 
            ORDER BY created_at DESC
        ''').fetchall()
        conn.close()
        
        product_list = [dict(row) for row in products]
        
        return jsonify({'status': 'success', 'products': product_list})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/inquiries')
@login_required
def get_inquiries():
    """获取询盘列表"""
    try:
        conn = get_db_connection()
        inquiries = conn.execute('''
            SELECT * FROM inquiries 
            ORDER BY created_at DESC
        ''').fetchall()
        conn.close()
        
        inquiry_list = [dict(row) for row in inquiries]
        
        return jsonify({'status': 'success', 'inquiries': inquiry_list})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/news')
@login_required
def get_news():
    """获取新闻列表"""
    try:
        conn = get_db_connection()
        news_list = conn.execute('''
            SELECT * FROM news 
            ORDER BY created_at DESC
        ''').fetchall()
        conn.close()
        
        news_data = [dict(row) for row in news_list]
        
        return jsonify({'status': 'success', 'news': news_data})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Vercel处理函数
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True)