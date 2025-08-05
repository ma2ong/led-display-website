#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
联进LED网站集成服务器
将前端和后台管理集成到同一个端口，解决端口访问问题
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
from flask_cors import CORS
from pathlib import Path

app = Flask(__name__, 
           template_folder='admin/templates',
           static_folder='.')
CORS(app)
app.secret_key = 'led_website_secret_key_2024'

# 数据库初始化
def init_database():
    """初始化数据库"""
    conn = sqlite3.connect('admin/database.db')
    cursor = conn.cursor()
    
    # 创建产品表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            specifications TEXT,
            price REAL,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建询盘表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            company TEXT,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建新闻表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT DEFAULT 'Admin',
            status TEXT DEFAULT 'published',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 插入默认管理员用户
    cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', 'admin123'))
    
    # 插入示例产品数据
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ('P2.5室内LED显示屏', '室内LED', 'P2.5高清室内LED显示屏，适用于会议室、展厅等场所', '像素间距:2.5mm\n亮度:800cd/㎡\n刷新率:3840Hz', 1200.0, '/assets/products/indoor-led.jpg'),
            ('P10户外LED显示屏', '户外LED', 'P10高亮度户外LED显示屏，防水防尘，适用于户外广告', '像素间距:10mm\n亮度:6500cd/㎡\n防护等级:IP65', 800.0, '/assets/products/outdoor-led.jpg'),
            ('租赁LED显示屏', '租赁LED', '轻便易装的租赁LED显示屏，适用于演出、会议等临时场合', '重量:6.5kg/㎡\n厚度:75mm\n安装:快锁设计', 1500.0, '/assets/products/rental-led.jpg'),
            ('透明LED显示屏', '透明LED', '高透明度LED显示屏，不影响采光，适用于玻璃幕墙', '透明度:85%\n像素间距:3.9mm\n厚度:10mm', 2000.0, '/assets/products/transparent-led.jpg')
        ]
        cursor.executemany('INSERT INTO products (name, category, description, specifications, price, image_url) VALUES (?, ?, ?, ?, ?, ?)', sample_products)
    
    conn.commit()
    conn.close()

# 前端路由
@app.route('/')
def index():
    """首页"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """服务静态文件"""
    if filename.endswith('.html'):
        return send_from_directory('.', filename)
    elif filename.startswith('css/') or filename.startswith('js/') or filename.startswith('assets/'):
        return send_from_directory('.', filename)
    else:
        return send_from_directory('.', filename)

# API路由
@app.route('/api/products')
def api_products():
    """产品API"""
    conn = sqlite3.connect('admin/database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
    products = []
    for row in cursor.fetchall():
        products.append({
            'id': row[0],
            'name': row[1],
            'category': row[2],
            'description': row[3],
            'specifications': row[4],
            'price': row[5],
            'image_url': row[6],
            'created_at': row[7]
        })
    conn.close()
    return jsonify(products)

@app.route('/api/contact', methods=['POST'])
def api_contact():
    """联系表单API"""
    data = request.get_json()
    
    conn = sqlite3.connect('admin/database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO inquiries (name, email, phone, company, message)
        VALUES (?, ?, ?, ?, ?)
    ''', (data.get('name'), data.get('email'), data.get('phone'), 
          data.get('company', ''), data.get('message')))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'message': '询盘提交成功！'})

@app.route('/api/content')
def api_content():
    """获取页面内容API"""
    try:
        # 读取内容文件
        content_file = 'data/content.json'
        if os.path.exists(content_file):
            with open(content_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
        else:
            # 默认内容
            content = {
                "company": {
                    "name": "深圳联进科技有限公司",
                    "slogan": "专业LED显示屏制造商",
                    "description": "17年专业经验，为全球客户提供高品质LED显示解决方案"
                },
                "stats": {
                    "projects": 1500,
                    "clients": 800,
                    "countries": 50,
                    "experience": 17
                }
            }
        
        return jsonify({
            'status': 'success',
            'data': content
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/health')
def api_health():
    """健康检查API"""
    return jsonify({
        'status': 'success',
        'message': 'API is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/news/latest')
def api_latest_news():
    """获取最新新闻API"""
    try:
        conn = sqlite3.connect('admin/database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM news WHERE status = "published" ORDER BY created_at DESC LIMIT 3')
        news_data = cursor.fetchall()
        conn.close()
        
        news_list = []
        for news in news_data:
            news_list.append({
                'id': news[0],
                'title': news[1],
                'content': news[2],
                'summary': news[2][:100] + '...' if len(news[2]) > 100 else news[2],
                'author': news[3],
                'created_at': news[5]
            })
        
        return jsonify({
            'status': 'success',
            'data': news_list
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/products/featured')
def api_featured_products():
    """获取特色产品API"""
    try:
        conn = sqlite3.connect('admin/database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products ORDER BY created_at DESC LIMIT 4')
        products = cursor.fetchall()
        conn.close()
        
        products_list = []
        for product in products:
            products_list.append({
                'id': product[0],
                'name': product[1],
                'category': product[2],
                'description': product[3],
                'price': product[5],
                'image_url': product[6]
            })
        
        return jsonify({
            'status': 'success',
            'data': products_list
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# 后台管理路由
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    """管理员登录页面和处理登录"""
    print(f"Admin route accessed with method: {request.method}")  # Debug log
    
    if request.method == 'GET':
        if 'admin_logged_in' in session:
            return redirect(url_for('admin_dashboard'))
        return render_template('admin_login.html')
    
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Login attempt: {username}")  # Debug log
        
        conn = sqlite3.connect('admin/database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            session['user_id'] = user[0]
            session['username'] = username
            session['role'] = user[3]
            print("Login successful")  # Debug log
            return redirect(url_for('admin_dashboard'))
        else:
            print("Login failed")  # Debug log
            return render_template('admin_login.html', error='用户名或密码错误')
    
    # Fallback for any other method
    return render_template('admin_login.html', error='请求方法不支持')

@app.route('/admin/login', methods=['POST'])
def admin_do_login():
    """处理登录 - 重定向到主登录处理"""
    return admin_login()

@app.route('/admin/logout')
def admin_logout():
    """退出登录"""
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """管理员仪表盘"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    # 获取统计数据
    conn = sqlite3.connect('admin/database.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM products')
    products_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM inquiries WHERE status = "new"')
    pending_inquiries = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM news WHERE status = "published"')
    published_news = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users')
    active_users = cursor.fetchone()[0]
    
    # 获取最近询盘
    cursor.execute('''
        SELECT id, name, email, message, created_at, status 
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
    
    return render_template('chinese_dashboard.html', stats=stats)

@app.route('/admin/products')
def admin_products():
    """产品管理"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect('admin/database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
    products = cursor.fetchall()
    conn.close()
    
    return render_template('chinese_products.html', products=products)

@app.route('/admin/inquiries')
def admin_inquiries():
    """询盘管理"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect('admin/database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inquiries ORDER BY created_at DESC')
    inquiries = cursor.fetchall()
    conn.close()
    
    return render_template('chinese_inquiries.html', inquiries=inquiries)

@app.route('/admin/news')
def admin_news():
    """新闻管理"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect('admin/database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM news ORDER BY created_at DESC')
    news = cursor.fetchall()
    conn.close()
    
    return render_template('chinese_news.html', news=news)

@app.route('/admin/users')
def admin_users():
    """用户管理"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect('admin/database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
    users = cursor.fetchall()
    conn.close()
    
    return render_template('chinese_users.html', users=users)

@app.route('/admin/settings')
def admin_settings():
    """系统设置"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    return render_template('chinese_settings.html')

@app.route('/admin/statistics')
def admin_statistics():
    """数据统计"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    return render_template('chinese_statistics.html')

@app.route('/admin/frontend-pages')
def admin_frontend_pages():
    """前端页面管理"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    return render_template('admin_frontend_pages.html')

@app.route('/admin/frontend-pages/<page_name>')
def admin_page_editor(page_name):
    """页面内容编辑器"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    # 页面信息
    page_info = {
        'name': page_name,
        'title': f'{page_name.title()} 页面管理',
        'description': f'管理 {page_name} 页面的所有内容区块'
    }
    
    return render_template('content_editor.html', page_info=page_info)

@app.route('/admin/view-frontend')
def view_frontend():
    """查看前端网站"""
    return redirect('/')

if __name__ == '__main__':
    print("🚀 联进LED网站集成服务器启动中...")
    print("=" * 60)
    
    # 初始化数据库
    init_database()
    print("✅ 数据库初始化完成")
    
    print("🌐 前端网站: http://localhost:8080")
    print("🔧 后台管理: http://localhost:8080/admin")
    print("🔑 登录信息: admin / admin123")
    print("=" * 60)
    print("✅ 服务器启动完成，按 Ctrl+C 停止")
    
    app.run(host='0.0.0.0', port=8080, debug=False)