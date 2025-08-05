#!/usr/bin/env python3
"""
完整的中文后台管理系统
包含产品管理、询盘管理、系统设置、用户管理、数据统计和前端页面管理
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import sqlite3
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.secret_key = 'lianjin-led-admin-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 数据库初始化
def init_db():
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
    
    conn.commit()
    conn.close()

# 初始化数据库
init_db()

@app.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 获取统计数据
    conn = sqlite3.connect('complete_admin.db')
    cursor = conn.cursor()
    
    stats = {}
    
    # 统计各表记录数
    tables = ['products', 'inquiries', 'news', 'page_content']
    for table in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        stats[table] = cursor.fetchone()[0]
    
    # 获取最近询盘
    cursor.execute('''
        SELECT name, company, product_interest, status, created_at 
        FROM inquiries 
        ORDER BY created_at DESC 
        LIMIT 5
    ''')
    recent_inquiries = cursor.fetchall()
    
    # 获取最近新闻
    cursor.execute('''
        SELECT title, category, publish_date, is_published 
        FROM news 
        ORDER BY created_at DESC 
        LIMIT 5
    ''')
    recent_news = cursor.fetchall()
    
    conn.close()
    
    return render_template('chinese_dashboard.html', 
                         stats=stats, 
                         recent_inquiries=recent_inquiries,
                         recent_news=recent_news)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('complete_admin.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, password_hash FROM users WHERE username = ? AND is_active = 1', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误')
    
    return render_template('chinese_login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 前端页面管理
@app.route('/frontend_pages')
def frontend_pages():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    pages = [
        ('home', '首页'),
        ('about', '关于我们'),
        ('products', '产品中心'),
        ('solutions', '解决方案'),
        ('cases', '成功案例'),
        ('news', '新闻资讯'),
        ('support', '技术支持'),
        ('contact', '联系我们')
    ]
    
    return render_template('frontend_pages.html', pages=pages)

@app.route('/page/<page_name>')
def manage_page(page_name):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('complete_admin.db')
    cursor = conn.cursor()
    
    # 获取该页面的所有内容
    cursor.execute('''
        SELECT id, section_name, content_type, content_data, image_url, video_url, 
               parameters, sort_order, is_active, created_at, updated_at
        FROM page_content 
        WHERE page_name = ? 
        ORDER BY sort_order, created_at
    ''', (page_name,))
    
    content_items = cursor.fetchall()
    conn.close()
    
    # 页面名称映射
    page_names = {
        'home': '首页',
        'about': '关于我们',
        'products': '产品中心',
        'solutions': '解决方案',
        'cases': '成功案例',
        'news': '新闻资讯',
        'support': '技术支持',
        'contact': '联系我们'
    }
    
    return render_template('chinese_page_manager.html', 
                         page_name=page_name,
                         page_name_cn=page_names.get(page_name, page_name),
                         content_items=content_items)

@app.route('/page/<page_name>/edit')
@app.route('/page/<page_name>/edit/<int:content_id>')
def edit_page_content(page_name, content_id=None):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    content = None
    if content_id:
        conn = sqlite3.connect('complete_admin.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, section_name, content_type, content_data, image_url, video_url, 
                   parameters, sort_order, is_active
            FROM page_content 
            WHERE id = ?
        ''', (content_id,))
        content = cursor.fetchone()
        conn.close()
    
    # 页面名称映射
    page_names = {
        'home': '首页',
        'about': '关于我们',
        'products': '产品中心',
        'solutions': '解决方案',
        'cases': '成功案例',
        'news': '新闻资讯',
        'support': '技术支持',
        'contact': '联系我们'
    }
    
    return render_template('content_editor_simple.html', 
                         page_name=page_name,
                         page_name_cn=page_names.get(page_name, page_name),
                         content=content)

@app.route('/save_content', methods=['POST'])
def save_content():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'})
    
    try:
        data = request.get_json()
        
        conn = sqlite3.connect('complete_admin.db')
        cursor = conn.cursor()
        
        if data.get('id'):
            # 更新现有内容
            cursor.execute('''
                UPDATE page_content 
                SET section_name = ?, content_type = ?, content_data = ?, 
                    image_url = ?, video_url = ?, parameters = ?, 
                    sort_order = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                data['section_name'], data['content_type'], data['content_data'],
                data.get('image_url'), data.get('video_url'), data.get('parameters'),
                data['sort_order'], data['is_active'], data['id']
            ))
        else:
            # 插入新内容
            cursor.execute('''
                INSERT INTO page_content 
                (page_name, section_name, content_type, content_data, image_url, 
                 video_url, parameters, sort_order, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['page_name'], data['section_name'], data['content_type'], 
                data['content_data'], data.get('image_url'), data.get('video_url'),
                data.get('parameters'), data['sort_order'], data['is_active']
            ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '内容保存成功'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# 产品管理
@app.route('/admin/products')
def admin_products():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('complete_admin.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, category, description, image_url, price_range, is_active, created_at
        FROM products 
        ORDER BY created_at DESC
    ''')
    products = cursor.fetchall()
    conn.close()
    
    return render_template('chinese_products.html', products=products)

@app.route('/admin/products/add')
@app.route('/admin/products/edit/<int:product_id>')
def edit_product(product_id=None):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    product = None
    if product_id:
        conn = sqlite3.connect('complete_admin.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()
        conn.close()
    
    return render_template('chinese_product_form.html', product=product)

# 询盘管理
@app.route('/admin/inquiries')
def admin_inquiries():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('complete_admin.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, email, company, phone, product_interest, 
               status, created_at
        FROM inquiries 
        ORDER BY created_at DESC
    ''')
    inquiries = cursor.fetchall()
    conn.close()
    
    return render_template('chinese_inquiries.html', inquiries=inquiries)

# 新闻管理
@app.route('/admin/news')
def admin_news():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('complete_admin.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, category, summary, author, image_url, 
               publish_date, is_published, is_featured, views, created_at
        FROM news 
        ORDER BY created_at DESC
    ''')
    news = cursor.fetchall()
    conn.close()
    
    return render_template('chinese_news.html', news=news)

# 用户管理
@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('complete_admin.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, username, email, role, is_active, created_at, last_login
        FROM users 
        ORDER BY created_at DESC
    ''')
    users = cursor.fetchall()
    conn.close()
    
    return render_template('chinese_users.html', users=users)

# 系统设置
@app.route('/admin/settings')
def admin_settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('complete_admin.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT setting_key, setting_value, setting_type, description
        FROM system_settings 
        ORDER BY setting_key
    ''')
    settings = cursor.fetchall()
    conn.close()
    
    return render_template('chinese_settings.html', settings=settings)

# 数据统计
@app.route('/admin/statistics')
def admin_statistics():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('complete_admin.db')
    cursor = conn.cursor()
    
    # 获取各种统计数据
    stats = {}
    
    # 产品统计
    cursor.execute('SELECT COUNT(*) FROM products WHERE is_active = 1')
    stats['active_products'] = cursor.fetchone()[0]
    
    # 询盘统计
    cursor.execute('SELECT COUNT(*) FROM inquiries WHERE status = "new"')
    stats['new_inquiries'] = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM inquiries')
    stats['total_inquiries'] = cursor.fetchone()[0]
    
    # 新闻统计
    cursor.execute('SELECT COUNT(*) FROM news WHERE is_published = 1')
    stats['published_news'] = cursor.fetchone()[0]
    
    # 页面内容统计
    cursor.execute('SELECT COUNT(*) FROM page_content WHERE is_active = 1')
    stats['active_content'] = cursor.fetchone()[0]
    
    # 月度询盘趋势
    cursor.execute('''
        SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count
        FROM inquiries 
        WHERE created_at >= date('now', '-12 months')
        GROUP BY month
        ORDER BY month
    ''')
    monthly_inquiries = cursor.fetchall()
    
    conn.close()
    
    return render_template('chinese_statistics.html', 
                         stats=stats, 
                         monthly_inquiries=monthly_inquiries)

# API端点
@app.route('/api/content/<page_name>')
def api_get_content(page_name):
    conn = sqlite3.connect('complete_admin.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT section_name, content_type, content_data, image_url, video_url, 
               parameters, sort_order
        FROM page_content 
        WHERE page_name = ? AND is_active = 1
        ORDER BY sort_order, created_at
    ''', (page_name,))
    
    content_items = cursor.fetchall()
    conn.close()
    
    # 转换为JSON格式
    content_data = []
    for item in content_items:
        content_data.append({
            'section_name': item[0],
            'content_type': item[1],
            'content_data': item[2],
            'image_url': item[3],
            'video_url': item[4],
            'parameters': json.loads(item[5]) if item[5] else {},
            'sort_order': item[6]
        })
    
    return jsonify(content_data)

# 文件上传
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'})
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有文件'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '未选择文件'})
    
    if file:
        # 生成唯一文件名
        filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 返回URL
        file_url = f'/uploads/{filename}'
        return jsonify({'success': True, 'url': file_url})
    
    return jsonify({'success': False, 'message': '上传失败'})

# 删除内容
@app.route('/delete_content/<int:content_id>', methods=['POST'])
def delete_content(content_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'})
    
    try:
        conn = sqlite3.connect('complete_admin.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM page_content WHERE id = ?', (content_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '内容删除成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# 添加缺失的路由来修复BuildError

# 产品详情查看路由
@app.route('/admin/products/view/<int:product_id>')
def view_product(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('complete_admin.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    conn.close()
    
    if not product:
        flash('产品不存在')
        return redirect(url_for('admin_products'))
    
    return render_template('chinese_product_view.html', product=product)

# 询盘详情查看路由
@app.route('/admin/inquiries/view/<int:inquiry_id>')
def view_inquiry(inquiry_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('complete_admin.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inquiries WHERE id = ?', (inquiry_id,))
    inquiry = cursor.fetchone()
    conn.close()
    
    if not inquiry:
        flash('询盘不存在')
        return redirect(url_for('admin_inquiries'))
    
    return render_template('chinese_inquiry_view.html', inquiry=inquiry)

# 新闻详情查看路由
@app.route('/admin/news/view/<int:news_id>')
def view_news(news_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('complete_admin.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM news WHERE id = ?', (news_id,))
    news_item = cursor.fetchone()
    conn.close()
    
    if not news_item:
        flash('新闻不存在')
        return redirect(url_for('admin_news'))
    
    return render_template('chinese_news_view.html', news=news_item)

# 查看前端网站路由
@app.route('/view_frontend')
def view_frontend():
    # 重定向到前端网站首页
    return redirect('http://127.0.0.1:8080')

# 编辑产品路由
@app.route('/admin/products/edit/<int:product_id>')
def edit_product_route(product_id):
    return edit_product(product_id)

# 编辑询盘路由
@app.route('/admin/inquiries/edit/<int:inquiry_id>')
def edit_inquiry(inquiry_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('complete_admin.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inquiries WHERE id = ?', (inquiry_id,))
    inquiry = cursor.fetchone()
    conn.close()
    
    return render_template('chinese_inquiry_form.html', inquiry=inquiry)

# 编辑新闻路由
@app.route('/admin/news/edit/<int:news_id>')
def edit_news(news_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('complete_admin.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM news WHERE id = ?', (news_id,))
    news_item = cursor.fetchone()
    conn.close()
    
    return render_template('chinese_news_form.html', news=news_item)

if __name__ == '__main__':
    # 创建默认管理员用户
    conn = sqlite3.connect('complete_admin.db')
    cursor = conn.cursor()
    
    # 检查是否存在用户
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
        # 创建默认管理员用户
        password_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, is_active)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@lianjinled.com', password_hash, 'admin', True))
        
        conn.commit()
        print("✓ 默认管理员用户已创建:")
        print("  用户名: admin")
        print("  密码: admin123")
    
    conn.close()
    
    app.run(debug=True, port=5003)
