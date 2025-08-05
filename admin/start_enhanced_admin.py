#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced LED Admin System Startup Script
增强版LED管理系统启动脚本
"""

import os
import sys
import sqlite3
from werkzeug.security import generate_password_hash

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_and_create_database():
    """检查并创建数据库"""
    db_path = 'enhanced_admin.db'
    
    if not os.path.exists(db_path):
        print("📊 创建新的数据库...")
        create_database()
    else:
        print("✅ 数据库已存在")

def create_database():
    """创建数据库结构"""
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
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 简化的产品表
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
         'High-quality LED displays', '高品质LED显示屏', '', '', '', '{}', 1),
        ('about', 'company', 'company_intro', 'About Us', '关于我们', 
         'Professional Manufacturer', '专业制造商',
         'Leading LED display company', '领先的LED显示屏公司', '', '', '', '{}', 1),
        ('products', 'categories', 'product_categories', 'Products', '产品中心', 
         'Complete Solutions', '完整解决方案',
         'Various LED display products', '各种LED显示屏产品', '', '', '', '{}', 1),
        ('solutions', 'applications', 'solution_apps', 'Solutions', '解决方案', 
         'Industry Applications', '行业应用',
         'Customized solutions', '定制解决方案', '', '', '', '{}', 1),
        ('cases', 'showcase', 'case_showcase', 'Cases', '成功案例', 
         'Success Stories', '成功故事',
         'Project implementations', '项目实施', '', '', '', '{}', 1),
        ('news', 'latest', 'latest_news', 'News', '新闻资讯', 
         'Latest Updates', '最新动态',
         'Industry news', '行业资讯', '', '', '', '{}', 1),
        ('support', 'technical', 'tech_support', 'Support', '技术支持', 
         'Professional Service', '专业服务',
         'Technical assistance', '技术协助', '', '', '', '{}', 1),
        ('contact', 'info', 'contact_info', 'Contact', '联系我们', 
         'Get in Touch', '联系方式',
         'Contact information', '联系信息', '', '', '', '{}', 1)
    ]
    
    for content in default_contents:
        cursor.execute('''
            INSERT OR IGNORE INTO page_contents (
                page_name, section_name, content_type, title_en, title_zh,
                subtitle_en, subtitle_zh, content_en, content_zh,
                image_url, video_url, link_url, parameters, sort_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', content)
    
    conn.commit()
    conn.close()
    print("✅ 数据库创建完成")

def start_admin():
    """启动管理系统"""
    try:
        from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
        from flask_cors import CORS
        from werkzeug.security import check_password_hash
        from functools import wraps
        
        app = Flask(__name__)
        app.secret_key = 'led_enhanced_admin_2024'
        app.config['JSON_AS_ASCII'] = False
        CORS(app)
        
        def login_required(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if 'admin_id' not in session:
                    return redirect(url_for('login'))
                return f(*args, **kwargs)
            return decorated_function
        
        def get_db_connection():
            conn = sqlite3.connect('enhanced_admin.db')
            conn.row_factory = sqlite3.Row
            return conn
        
        @app.route('/')
        @login_required
        def dashboard():
            conn = get_db_connection()
            stats = {
                'pages': 8,
                'contents': conn.execute('SELECT COUNT(*) FROM page_contents WHERE status = "active"').fetchone()[0],
                'products': conn.execute('SELECT COUNT(*) FROM products WHERE status = "active"').fetchone()[0],
                'inquiries': conn.execute('SELECT COUNT(*) FROM inquiries WHERE status = "new"').fetchone()[0]
            }
            conn.close()
            return render_template('enhanced_dashboard.html', stats=stats)
        
        @app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                
                conn = get_db_connection()
                admin = conn.execute('SELECT * FROM admins WHERE username = ?', (username,)).fetchone()
                conn.close()
                
                if admin and check_password_hash(admin['password_hash'], password):
                    session['admin_id'] = admin['id']
                    session['admin_username'] = admin['username']
                    flash('登录成功！', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('用户名或密码错误！', 'error')
            
            return '''
            <!DOCTYPE html>
            <html lang="zh-CN">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>登录 - LED管理后台</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
                    .login-card { background: white; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); max-width: 400px; width: 100%; }
                    .login-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; text-align: center; border-radius: 20px 20px 0 0; }
                </style>
            </head>
            <body>
                <div class="login-card">
                    <div class="login-header">
                        <h3><i class="fas fa-tv me-2"></i>LED管理后台</h3>
                        <p class="mb-0">增强版内容管理系统</p>
                    </div>
                    <div class="p-4">
                        <form method="POST">
                            <div class="mb-3">
                                <label class="form-label">用户名</label>
                                <input type="text" class="form-control" name="username" value="admin" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">密码</label>
                                <input type="password" class="form-control" name="password" value="admin123" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">登录</button>
                        </form>
                        <div class="mt-3 text-center">
                            <small class="text-muted">默认账号: admin / admin123</small>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            '''
        
        @app.route('/logout')
        def logout():
            session.clear()
            flash('已成功登出！', 'info')
            return redirect(url_for('login'))
        
        @app.route('/pages')
        @login_required
        def page_list():
            pages = [
                {'name': 'home', 'title': '首页', 'description': '网站首页内容管理'},
                {'name': 'about', 'title': '关于我们', 'description': '公司介绍和团队信息'},
                {'name': 'products', 'title': '产品中心', 'description': '产品展示和分类管理'},
                {'name': 'solutions', 'title': '解决方案', 'description': '行业解决方案展示'},
                {'name': 'cases', 'title': '成功案例', 'description': '项目案例展示'},
                {'name': 'news', 'title': '新闻资讯', 'description': '公司新闻和行业动态'},
                {'name': 'support', 'title': '技术支持', 'description': '技术支持和服务信息'},
                {'name': 'contact', 'title': '联系我们', 'description': '联系方式和表单管理'}
            ]
            return render_template('page_list_complete.html', pages=pages)
        
        @app.route('/pages/<page_name>')
        @login_required
        def page_content_manager(page_name):
            conn = get_db_connection()
            contents = conn.execute('''
                SELECT * FROM page_contents 
                WHERE page_name = ? 
                ORDER BY sort_order, id
            ''', (page_name,)).fetchall()
            conn.close()
            
            page_titles = {
                'home': '首页管理', 'about': '关于我们', 'products': '产品中心',
                'solutions': '解决方案', 'cases': '成功案例', 'news': '新闻资讯',
                'support': '技术支持', 'contact': '联系我们'
            }
            
            return render_template('page_content_manager.html', 
                                 page_name=page_name,
                                 page_title=page_titles.get(page_name, page_name),
                                 contents=contents)
        
        @app.route('/api/pages/<page_name>/content')
        def api_page_content(page_name):
            conn = get_db_connection()
            contents = conn.execute('''
                SELECT * FROM page_contents 
                WHERE page_name = ? AND status = 'active'
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
        
        print("🌐 管理后台地址: http://localhost:5001")
        print("👤 默认登录账号: admin")
        print("🔑 默认登录密码: admin123")
        print("=" * 60)
        
        app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("请确保已安装必要的依赖包:")
        print("pip install flask flask-cors werkzeug pillow")

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 启动增强版LED显示屏管理后台")
    print("=" * 60)
    
    # 切换到admin目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 检查并创建数据库
    check_and_create_database()
    
    # 启动管理系统
    start_admin()

if __name__ == '__main__':
    main()
