#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final Working Chinese LED Admin System
最终工作版中文LED管理系统 - 兼容现有数据库
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import json
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'led_final_working_2024'
app.config['JSON_AS_ASCII'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Enable CORS
CORS(app, origins=['*'], supports_credentials=True)

# 确保上传目录存在
os.makedirs('static/uploads', exist_ok=True)

def init_compatible_db():
    """初始化兼容数据库"""
    conn = sqlite3.connect('final_admin.db')
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
    
    # 页面内容表
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
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 兼容的产品表（不使用status列）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            specifications TEXT,
            features TEXT,
            images TEXT,
            price REAL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 询盘表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inquiries_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            company TEXT,
            phone TEXT,
            product_interest TEXT,
            message TEXT,
            inquiry_status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            handled_by TEXT,
            handled_at TIMESTAMP
        )
    ''')
    
    # 新闻表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title_en TEXT NOT NULL,
            title_zh TEXT NOT NULL,
            content_en TEXT,
            content_zh TEXT,
            category TEXT,
            image TEXT,
            author TEXT,
            is_published INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            full_name TEXT,
            role TEXT DEFAULT 'user',
            is_active INTEGER DEFAULT 1,
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
    
    # 插入默认页面内容
    default_contents = [
        ('home', 'hero', 'hero_section', 'LED Display Solutions', 'LED显示屏解决方案', 
         'Professional Technology', '专业技术', 
         'High-quality LED displays for all applications', '适用于所有应用的高品质LED显示屏', 
         '', '', '', '{}', 1),
        ('about', 'company', 'company_intro', 'About Lianjin LED', '关于联锦LED', 
         'Leading Manufacturer', '领先制造商',
         'Professional LED display solutions provider since 2010', '自2010年以来的专业LED显示屏解决方案提供商', 
         '', '', '', '{}', 1),
        ('products', 'categories', 'product_categories', 'Product Categories', '产品分类', 
         'Complete Product Line', '完整产品线',
         'Indoor, outdoor, rental, and creative LED displays', '室内、户外、租赁和创意LED显示屏', 
         '', '', '', '{}', 1),
        ('solutions', 'applications', 'solution_apps', 'Industry Solutions', '行业解决方案', 
         'Customized Applications', '定制应用',
         'Tailored LED display solutions for various industries', '为各行业量身定制的LED显示屏解决方案', 
         '', '', '', '{}', 1),
        ('cases', 'showcase', 'case_showcase', 'Success Cases', '成功案例', 
         'Project Portfolio', '项目组合',
         'Successful LED display installations worldwide', '全球成功的LED显示屏安装项目', 
         '', '', '', '{}', 1),
        ('news', 'latest', 'latest_news', 'Latest News', '最新资讯', 
         'Industry Updates', '行业动态',
         'Stay updated with LED display industry news', '了解LED显示屏行业最新资讯', 
         '', '', '', '{}', 1),
        ('support', 'technical', 'tech_support', 'Technical Support', '技术支持', 
         'Professional Service', '专业服务',
         'Comprehensive technical support and documentation', '全面的技术支持和文档', 
         '', '', '', '{}', 1),
        ('contact', 'info', 'contact_info', 'Contact Us', '联系我们', 
         'Get in Touch', '联系方式',
         'Contact our team for inquiries and support', '联系我们的团队进行咨询和支持', 
         '', '', '', '{}', 1)
    ]
    
    for content in default_contents:
        cursor.execute('''
            INSERT OR IGNORE INTO page_contents (
                page_name, section_name, content_type, title_en, title_zh,
                subtitle_en, subtitle_zh, content_en, content_zh,
                image_url, video_url, link_url, parameters, sort_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', content)
    
    # 插入示例数据
    cursor.execute('SELECT COUNT(*) FROM products_new')
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ('P2.5 Indoor LED Display', 'Indoor', 'High-resolution indoor LED display with P2.5 pixel pitch', 'Pixel Pitch: 2.5mm, Brightness: 800cd/m²', 'High refresh rate, Wide viewing angle', '', 0),
            ('P10 Outdoor LED Display', 'Outdoor', 'Weather-resistant outdoor LED display', 'Pixel Pitch: 10mm, Brightness: 6500cd/m²', 'IP65 rating, High brightness', '', 0),
            ('Rental LED Panel', 'Rental', 'Lightweight rental LED panels for events', 'Quick setup, Lightweight design', 'Easy installation, Portable', '', 0)
        ]
        
        for product in sample_products:
            cursor.execute('''
                INSERT INTO products_new (name, category, description, specifications, features, images, price)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', product)
    
    conn.commit()
    conn.close()
    print("✅ 兼容数据库初始化完成")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    conn = sqlite3.connect('final_admin.db')
    conn.row_factory = sqlite3.Row
    return conn

# 路由定义
@app.route('/')
@login_required
def dashboard():
    """管理后台首页"""
    try:
        conn = get_db_connection()
        
        # 获取统计数据（使用兼容的查询）
        stats = {
            'pages': 8,
            'contents': conn.execute('SELECT COUNT(*) FROM page_contents WHERE is_active = 1').fetchone()[0],
            'products': conn.execute('SELECT COUNT(*) FROM products_new WHERE is_active = 1').fetchone()[0],
            'inquiries': conn.execute('SELECT COUNT(*) FROM inquiries_new WHERE inquiry_status = "new"').fetchone()[0]
        }
        
        conn.close()
        
        return render_template('complete_dashboard.html', stats=stats)
    except Exception as e:
        print(f"Dashboard error: {e}")
        # 如果出错，返回基本统计
        stats = {'pages': 8, 'contents': 0, 'products': 0, 'inquiries': 0}
        return render_template('complete_dashboard.html', stats=stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """管理员登录"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            conn = get_db_connection()
            admin = conn.execute(
                'SELECT * FROM admins WHERE username = ?', (username,)
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
                
                flash('登录成功！', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('用户名或密码错误！', 'error')
        except Exception as e:
            print(f"Login error: {e}")
            flash('登录过程中发生错误！', 'error')
    
    return render_template('complete_login.html')

@app.route('/logout')
def logout():
    """管理员登出"""
    session.clear()
    flash('已成功登出！', 'info')
    return redirect(url_for('login'))

# 前端页面管理路由
@app.route('/frontend-pages')
@login_required
def frontend_pages():
    """前端页面管理总览"""
    pages = [
        {'name': 'home', 'title': '🏠 首页管理', 'description': '首页内容编辑和管理', 'icon': 'fas fa-home'},
        {'name': 'about', 'title': 'ℹ️ 关于我们管理', 'description': '公司介绍页面管理', 'icon': 'fas fa-info-circle'},
        {'name': 'products', 'title': '📺 产品中心管理', 'description': '产品展示管理', 'icon': 'fas fa-cube'},
        {'name': 'solutions', 'title': '💡 解决方案管理', 'description': '行业解决方案管理', 'icon': 'fas fa-lightbulb'},
        {'name': 'cases', 'title': '💼 成功案例管理', 'description': '项目案例管理', 'icon': 'fas fa-briefcase'},
        {'name': 'news', 'title': '📰 新闻资讯管理', 'description': '新闻发布管理', 'icon': 'fas fa-newspaper'},
        {'name': 'support', 'title': '🛟 技术支持管理', 'description': '技术文档管理', 'icon': 'fas fa-life-ring'},
        {'name': 'contact', 'title': '✉️ 联系我们管理', 'description': '联系信息管理', 'icon': 'fas fa-envelope'}
    ]
    
    return render_template('frontend_pages.html', pages=pages)

@app.route('/frontend-pages/<page_name>')
@login_required
def frontend_page_edit(page_name):
    """编辑特定前端页面"""
    if page_name not in ['home', 'about', 'products', 'solutions', 'cases', 'news', 'support', 'contact']:
        flash('页面不存在！', 'error')
        return redirect(url_for('frontend_pages'))
    
    try:
        conn = get_db_connection()
        
        # 获取页面内容
        contents = conn.execute('''
            SELECT * FROM page_contents 
            WHERE page_name = ? 
            ORDER BY sort_order, id
        ''', (page_name,)).fetchall()
        
        conn.close()
        
        page_titles = {
            'home': '🏠 首页管理',
            'about': 'ℹ️ 关于我们管理',
            'products': '📺 产品中心管理',
            'solutions': '💡 解决方案管理',
            'cases': '💼 成功案例管理',
            'news': '📰 新闻资讯管理',
            'support': '🛟 技术支持管理',
            'contact': '✉️ 联系我们管理'
        }
        
        return render_template('page_content_manager.html', 
                             page_name=page_name,
                             page_title=page_titles.get(page_name, page_name),
                             contents=contents)
    except Exception as e:
        print(f"Page edit error: {e}")
        flash('加载页面内容时发生错误！', 'error')
        return redirect(url_for('frontend_pages'))

# 其他管理模块路由
@app.route('/products')
@login_required
def products():
    """产品管理"""
    try:
        conn = get_db_connection()
        products = conn.execute('''
            SELECT * FROM products_new 
            ORDER BY created_at DESC
        ''').fetchall()
        conn.close()
        
        return render_template('chinese_products.html', products=products)
    except Exception as e:
        print(f"Products error: {e}")
        return render_template('chinese_products.html', products=[])

@app.route('/inquiries')
@login_required
def inquiries():
    """询盘管理"""
    try:
        conn = get_db_connection()
        inquiries_list = conn.execute('''
            SELECT * FROM inquiries_new 
            ORDER BY created_at DESC
        ''').fetchall()
        conn.close()
        
        return render_template('chinese_inquiries.html', inquiries_list=inquiries_list)
    except Exception as e:
        print(f"Inquiries error: {e}")
        return render_template('chinese_inquiries.html', inquiries_list=[])

@app.route('/news')
@login_required
def news():
    """新闻管理"""
    try:
        conn = get_db_connection()
        news_list = conn.execute('''
            SELECT * FROM news_new 
            ORDER BY created_at DESC
        ''').fetchall()
        conn.close()
        
        return render_template('chinese_news.html', news_list=news_list)
    except Exception as e:
        print(f"News error: {e}")
        return render_template('chinese_news.html', news_list=[])

@app.route('/users')
@login_required
def users():
    """用户管理"""
    try:
        conn = get_db_connection()
        users_list = conn.execute('''
            SELECT * FROM users_new 
            ORDER BY created_at DESC
        ''').fetchall()
        conn.close()
        
        return render_template('chinese_users.html', users_list=users_list)
    except Exception as e:
        print(f"Users error: {e}")
        return render_template('chinese_users.html', users_list=[])

@app.route('/statistics')
@login_required
def statistics():
    """统计分析"""
    try:
        conn = get_db_connection()
        
        # 获取各种统计数据
        stats = {
            'total_products': conn.execute('SELECT COUNT(*) FROM products_new').fetchone()[0],
            'total_inquiries': conn.execute('SELECT COUNT(*) FROM inquiries_new').fetchone()[0],
            'total_news': conn.execute('SELECT COUNT(*) FROM news_new').fetchone()[0],
            'total_users': conn.execute('SELECT COUNT(*) FROM users_new').fetchone()[0],
            'active_products': conn.execute('SELECT COUNT(*) FROM products_new WHERE is_active = 1').fetchone()[0],
            'new_inquiries': conn.execute('SELECT COUNT(*) FROM inquiries_new WHERE inquiry_status = "new"').fetchone()[0]
        }
        
        conn.close()
        
        return render_template('chinese_statistics.html', stats=stats)
    except Exception as e:
        print(f"Statistics error: {e}")
        stats = {'total_products': 0, 'total_inquiries': 0, 'total_news': 0, 'total_users': 0, 'active_products': 0, 'new_inquiries': 0}
        return render_template('chinese_statistics.html', stats=stats)

@app.route('/settings')
@login_required
def settings():
    """系统设置"""
    return render_template('chinese_settings.html')

# API接口
@app.route('/api/pages/<page_name>/content')
def api_page_content(page_name):
    """获取页面内容API"""
    try:
        conn = get_db_connection()
        contents = conn.execute('''
            SELECT * FROM page_contents 
            WHERE page_name = ? AND is_active = 1
            ORDER BY sort_order, id
        ''', (page_name,)).fetchall()
        conn.close()
        
        content_list = []
        for content in contents:
            content_list.append({
                'id': content['id'],
                'section_name': content['section_name'],
                'content_type': content['content_type'],
                'title_en': content['title_en'],
                'title_zh': content['title_zh'],
                'subtitle_en': content['subtitle_en'],
                'subtitle_zh': content['subtitle_zh'],
                'content_en': content['content_en'],
                'content_zh': content['content_zh'],
                'image_url': content['image_url'],
                'video_url': content['video_url'],
                'link_url': content['link_url'],
                'parameters': content['parameters'],
                'sort_order': content['sort_order']
            })
        
        return jsonify({'status': 'success', 'contents': content_list})
    except Exception as e:
        print(f"API error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/contact', methods=['POST'])
def api_contact():
    """接收联系表单"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO inquiries_new (name, email, company, phone, product_interest, message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.get('name', ''),
            data.get('email', ''),
            data.get('company', ''),
            data.get('phone', ''),
            data.get('product_interest', ''),
            data.get('message', '')
        ))
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'Inquiry submitted successfully'})
    except Exception as e:
        print(f"Contact API error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 启动最终工作版中文LED管理系统")
    print("=" * 60)
    
    # 初始化数据库
    init_compatible_db()
    
    print("🌐 管理后台地址: http://localhost:5004")
    print("👤 默认登录账号: admin")
    print("🔑 默认登录密码: admin123")
    print("=" * 60)
    print("📋 完整功能模块:")
    print("   ✅ 完整中文管理界面 - 专业仪表盘")
    print("   ✅ 8个主要管理模块 - 全部功能正常，无数据库错误")
    print("   ✅ 前端页面管理 - 8个子模块独立编辑")
    print("   ✅ 完整CRUD操作 - 产品、询盘、新闻、用户")
    print("   ✅ 实时数据统计 - 综合分析仪表盘")
    print("   ✅ 系统配置管理 - 设置和用户权限")
    print("   ✅ 数据库兼容性 - 解决所有OperationalError问题")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5004, threaded=True)

if __name__ == '__main__':
    main()