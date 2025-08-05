#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
联进LED后台管理系统 - 完整版
Complete LED Admin Management System
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_cors import CORS
import sqlite3
import os
import json
from datetime import datetime, timedelta
import hashlib
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# 数据库初始化
def init_database():
    """初始化数据库"""
    conn = sqlite3.connect('led_admin.db')
    cursor = conn.cursor()
    
    # 用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    # 产品表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            specifications TEXT,
            price REAL,
            image_url TEXT,
            video_url TEXT,
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
            phone TEXT,
            company TEXT,
            subject TEXT,
            message TEXT,
            status TEXT DEFAULT 'pending',
            priority TEXT DEFAULT 'normal',
            assigned_to TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            response TEXT,
            response_at TIMESTAMP
        )
    ''')
    
    # 新闻表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            summary TEXT,
            author TEXT,
            category TEXT,
            image_url TEXT,
            video_url TEXT,
            status TEXT DEFAULT 'draft',
            publish_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            views INTEGER DEFAULT 0
        )
    ''')
    
    # 页面内容表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS page_contents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_name TEXT NOT NULL,
            section_name TEXT NOT NULL,
            content_type TEXT NOT NULL,
            content_data TEXT,
            display_order INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
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
            setting_type TEXT DEFAULT 'text',
            description TEXT,
            category TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 访问统计表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visit_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_url TEXT,
            ip_address TEXT,
            user_agent TEXT,
            referrer TEXT,
            visit_date DATE,
            visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 插入默认管理员用户
    cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
    if cursor.fetchone()[0] == 0:
        password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (username, password, role, email)
            VALUES (?, ?, ?, ?)
        ''', ('admin', password_hash, 'super_admin', 'admin@liangjin-led.com'))
    
    # 插入示例产品数据
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ('室内LED显示屏', 'indoor', 'P2.5高清室内LED显示屏，适用于会议室、展厅等场所', 'P2.5, 1920x1080, 500cd/m²', 15000.00, '/assets/products/indoor-p25.jpg', '', 'active'),
            ('户外LED显示屏', 'outdoor', 'P10户外全彩LED显示屏，防水防尘，适用于户外广告', 'P10, IP65, 6500cd/m²', 25000.00, '/assets/products/outdoor-p10.jpg', '', 'active'),
            ('租赁LED显示屏', 'rental', '轻薄租赁LED显示屏，快速安装，适用于舞台演出', 'P3.91, 500x500mm, 轻薄设计', 8000.00, '/assets/products/rental-p391.jpg', '', 'active'),
            ('创意LED显示屏', 'creative', '异形创意LED显示屏，可定制各种造型', '柔性屏, 可弯曲, 定制化', 30000.00, '/assets/products/creative-flexible.jpg', '', 'active')
        ]
        cursor.executemany('''
            INSERT INTO products (name, category, description, specifications, price, image_url, video_url, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_products)
    
    # 插入默认页面内容
    cursor.execute('SELECT COUNT(*) FROM page_contents')
    if cursor.fetchone()[0] == 0:
        default_contents = [
            ('home', 'hero_title', 'text', '联进LED - 专业LED显示屏制造商', 1),
            ('home', 'hero_subtitle', 'text', '提供高品质的室内外LED显示屏解决方案', 2),
            ('home', 'hero_image', 'image', '/assets/products/led-display-hero.jpg', 3),
            ('about', 'company_intro', 'text', '联进LED成立于2010年，专注于LED显示屏的研发、生产和销售...', 1),
            ('about', 'company_image', 'image', '/assets/about/company-building.jpg', 2),
            ('products', 'page_title', 'text', '产品中心', 1),
            ('products', 'page_description', 'text', '我们提供全系列LED显示屏产品', 2),
            ('solutions', 'page_title', 'text', '解决方案', 1),
            ('solutions', 'page_description', 'text', '为不同行业提供专业的LED显示解决方案', 2),
            ('cases', 'page_title', 'text', '成功案例', 1),
            ('cases', 'page_description', 'text', '查看我们的成功项目案例', 2),
            ('news', 'page_title', 'text', '新闻资讯', 1),
            ('news', 'page_description', 'text', '了解LED行业最新动态', 2),
            ('support', 'page_title', 'text', '技术支持', 1),
            ('support', 'page_description', 'text', '专业的技术支持和售后服务', 2),
            ('contact', 'page_title', 'text', '联系我们', 1),
            ('contact', 'company_address', 'text', '深圳市宝安区西乡街道固戍社区', 2),
            ('contact', 'company_phone', 'text', '+86-755-12345678', 3),
            ('contact', 'company_email', 'text', 'info@liangjin-led.com', 4)
        ]
        cursor.executemany('''
            INSERT INTO page_contents (page_name, section_name, content_type, content_data, display_order)
            VALUES (?, ?, ?, ?, ?)
        ''', default_contents)
    
    # 插入系统设置
    cursor.execute('SELECT COUNT(*) FROM system_settings')
    if cursor.fetchone()[0] == 0:
        default_settings = [
            ('site_title', '联进LED官网', 'text', '网站标题', 'basic'),
            ('site_description', '专业LED显示屏制造商', 'text', '网站描述', 'basic'),
            ('company_name', '深圳联进LED科技有限公司', 'text', '公司名称', 'company'),
            ('company_address', '深圳市宝安区西乡街道固戍社区', 'text', '公司地址', 'company'),
            ('company_phone', '+86-755-12345678', 'text', '公司电话', 'company'),
            ('company_email', 'info@liangjin-led.com', 'email', '公司邮箱', 'company'),
            ('backup_enabled', 'true', 'boolean', '启用自动备份', 'system'),
            ('backup_frequency', '24', 'number', '备份频率(小时)', 'system')
        ]
        cursor.executemany('''
            INSERT INTO system_settings (setting_key, setting_value, setting_type, description, category)
            VALUES (?, ?, ?, ?, ?)
        ''', default_settings)
    
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")

# 登录验证装饰器
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# 路由定义
@app.route('/admin')
def admin_login():
    """管理员登录页面"""
    if 'user_id' in session:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username and password:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            conn = sqlite3.connect('led_admin.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, role FROM users 
                WHERE username = ? AND password = ? AND status = 'active'
            ''', (username, password_hash))
            
            user = cursor.fetchone()
            if user:
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['role'] = user[2]
                
                # 更新最后登录时间
                cursor.execute('''
                    UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
                ''', (user[0],))
                conn.commit()
                conn.close()
                
                flash('登录成功！', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                conn.close()
                flash('用户名或密码错误！', 'error')
        else:
            flash('请输入用户名和密码！', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """管理员仪表盘"""
    conn = sqlite3.connect('led_admin.db')
    cursor = conn.cursor()
    
    # 获取统计数据
    cursor.execute('SELECT COUNT(*) FROM products WHERE status = "active"')
    products_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM inquiries WHERE status = "pending"')
    pending_inquiries = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM news WHERE status = "published"')
    published_news = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE status = "active"')
    active_users = cursor.fetchone()[0]
    
    # 获取最近询盘
    cursor.execute('''
        SELECT id, name, email, subject, created_at, status 
        FROM inquiries 
        ORDER BY created_at DESC 
        LIMIT 5
    ''')
    recent_inquiries = cursor.fetchall()
    
    # 获取最近新闻
    cursor.execute('''
        SELECT id, title, author, created_at, status 
        FROM news 
        ORDER BY created_at DESC 
        LIMIT 5
    ''')
    recent_news = cursor.fetchall()
    
    conn.close()
    
    stats = {
        'products_count': products_count,
        'pending_inquiries': pending_inquiries,
        'published_news': published_news,
        'active_users': active_users,
        'recent_inquiries': recent_inquiries,
        'recent_news': recent_news
    }
    
    return render_template('admin_dashboard.html', stats=stats)

@app.route('/admin/products')
@login_required
def admin_products():
    """产品管理"""
    conn = sqlite3.connect('led_admin.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, category, price, status, created_at 
        FROM products 
        ORDER BY created_at DESC
    ''')
    products = cursor.fetchall()
    conn.close()
    
    return render_template('admin_products.html', products=products)

@app.route('/admin/inquiries')
@login_required
def admin_inquiries():
    """询盘管理"""
    conn = sqlite3.connect('led_admin.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, email, company, subject, status, priority, created_at 
        FROM inquiries 
        ORDER BY created_at DESC
    ''')
    inquiries = cursor.fetchall()
    conn.close()
    
    return render_template('admin_inquiries.html', inquiries=inquiries)

@app.route('/admin/news')
@login_required
def admin_news():
    """新闻管理"""
    conn = sqlite3.connect('led_admin.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, author, category, status, publish_date, created_at 
        FROM news 
        ORDER BY created_at DESC
    ''')
    news = cursor.fetchall()
    conn.close()
    
    return render_template('admin_news.html', news=news)

@app.route('/admin/frontend-pages')
@login_required
def admin_frontend_pages():
    """前端页面管理"""
    return render_template('admin_frontend_pages.html')

@app.route('/admin/frontend-pages/<page_name>')
@login_required
def admin_page_editor(page_name):
    """页面内容编辑器"""
    conn = sqlite3.connect('led_admin.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, section_name, content_type, content_data, display_order 
        FROM page_contents 
        WHERE page_name = ? AND status = 'active'
        ORDER BY display_order
    ''', (page_name,))
    contents = cursor.fetchall()
    conn.close()
    
    return render_template('admin_page_editor.html', page_name=page_name, contents=contents)

@app.route('/admin/users')
@login_required
def admin_users():
    """用户管理"""
    conn = sqlite3.connect('led_admin.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, username, email, role, status, created_at, last_login 
        FROM users 
        ORDER BY created_at DESC
    ''')
    users = cursor.fetchall()
    conn.close()
    
    return render_template('admin_users.html', users=users)

@app.route('/admin/settings')
@login_required
def admin_settings():
    """系统设置"""
    conn = sqlite3.connect('led_admin.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT setting_key, setting_value, setting_type, description, category 
        FROM system_settings 
        ORDER BY category, setting_key
    ''')
    settings = cursor.fetchall()
    conn.close()
    
    # 按类别分组设置
    grouped_settings = {}
    for setting in settings:
        category = setting[4] or 'other'
        if category not in grouped_settings:
            grouped_settings[category] = []
        grouped_settings[category].append(setting)
    
    return render_template('admin_settings.html', grouped_settings=grouped_settings)

@app.route('/admin/statistics')
@login_required
def admin_statistics():
    """数据统计"""
    conn = sqlite3.connect('led_admin.db')
    cursor = conn.cursor()
    
    # 获取各种统计数据
    stats = {}
    
    # 产品统计
    cursor.execute('SELECT category, COUNT(*) FROM products GROUP BY category')
    stats['products_by_category'] = cursor.fetchall()
    
    # 询盘统计
    cursor.execute('SELECT status, COUNT(*) FROM inquiries GROUP BY status')
    stats['inquiries_by_status'] = cursor.fetchall()
    
    # 新闻统计
    cursor.execute('SELECT category, COUNT(*) FROM news GROUP BY category')
    stats['news_by_category'] = cursor.fetchall()
    
    # 月度统计
    cursor.execute('''
        SELECT strftime('%Y-%m', created_at) as month, COUNT(*) 
        FROM inquiries 
        WHERE created_at >= date('now', '-12 months')
        GROUP BY month 
        ORDER BY month
    ''')
    stats['monthly_inquiries'] = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_statistics.html', stats=stats)

@app.route('/admin/logout')
def admin_logout():
    """退出登录"""
    session.clear()
    flash('已成功退出登录！', 'info')
    return redirect(url_for('admin_login'))

# API路由
@app.route('/api/admin/products', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def api_products():
    """产品API"""
    conn = sqlite3.connect('led_admin.db')
    cursor = conn.cursor()
    
    if request.method == 'GET':
        cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
        products = cursor.fetchall()
        conn.close()
        return jsonify({'success': True, 'data': products})
    
    elif request.method == 'POST':
        data = request.json
        cursor.execute('''
            INSERT INTO products (name, category, description, specifications, price, image_url, video_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data['name'], data['category'], data['description'], 
              data['specifications'], data['price'], data['image_url'], data['video_url']))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': '产品添加成功'})
    
    # 其他HTTP方法的处理...
    conn.close()
    return jsonify({'success': False, 'message': '不支持的操作'})

if __name__ == '__main__':
    # 初始化数据库
    init_database()
    
    print("🚀 联进LED后台管理系统启动中...")
    print("============================================================")
    print("✅ 数据库初始化完成")
    print("🌐 管理后台: http://localhost:5000/admin")
    print("🔑 登录信息: admin / admin123")
    print("============================================================")
    print("✅ 服务器启动完成，按 Ctrl+C 停止")
    
    app.run(debug=True, host='0.0.0.0', port=5000)