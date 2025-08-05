#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fixed Enhanced LED Admin System
修复版增强LED管理系统 - 兼容现有数据库结构
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
app.secret_key = 'led_fixed_enhanced_2024'
app.config['JSON_AS_ASCII'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS
CORS(app, origins=['*'], supports_credentials=True)

# 确保上传目录存在
os.makedirs('static/uploads', exist_ok=True)

def init_compatible_database():
    """初始化兼容的数据库结构"""
    conn = sqlite3.connect('enhanced_admin.db')
    cursor = conn.cursor()
    
    # 检查并创建管理员表
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
    
    # 页面内容表 - 核心功能
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
    
    # 兼容现有产品表结构
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products_compatible (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            specifications TEXT,
            features TEXT,
            images TEXT,
            price REAL,
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
    insert_default_page_contents(cursor)
    
    conn.commit()
    conn.close()

def insert_default_page_contents(cursor):
    """插入默认页面内容"""
    default_contents = [
        # Home页面
        ('home', 'hero', 'hero_section', 'LED Display Solutions', 'LED显示屏解决方案', 
         'Professional Technology', '专业技术', 
         'High-quality LED displays for various applications', '高品质LED显示屏，适用于各种应用场景', 
         '', '', '', '{}', 1),
        
        ('home', 'features', 'feature_list', 'Our Advantages', '我们的优势', 
         'Why Choose Us', '为什么选择我们',
         'High brightness, energy efficiency, long lifespan', '高亮度、节能环保、长寿命', 
         '', '', '', '{}', 2),
        
        ('home', 'products', 'product_showcase', 'Product Range', '产品系列', 
         'Complete Solutions', '完整解决方案',
         'Indoor, outdoor, rental, creative LED displays', '室内、户外、租赁、创意LED显示屏', 
         '', '', '', '{}', 3),
        
        # About页面
        ('about', 'company', 'company_intro', 'About Lianjin LED', '关于联锦LED', 
         'Professional Manufacturer', '专业制造商',
         'Leading LED display manufacturer since 2010', '自2010年以来的领先LED显示屏制造商', 
         '', '', '', '{}', 1),
        
        ('about', 'mission', 'text_content', 'Our Mission', '我们的使命', 
         'Innovation Excellence', '创新卓越',
         'Providing innovative LED display solutions worldwide', '为全球提供创新的LED显示屏解决方案', 
         '', '', '', '{}', 2),
        
        # Products页面
        ('products', 'categories', 'product_categories', 'Product Categories', '产品分类', 
         'Complete Product Line', '完整产品线',
         'Indoor, outdoor, rental, and creative LED displays', '室内、户外、租赁和创意LED显示屏', 
         '', '', '', '{}', 1),
        
        ('products', 'features', 'product_features', 'Product Features', '产品特色', 
         'Advanced Technology', '先进技术',
         'High resolution, excellent color reproduction, reliable performance', '高分辨率、优秀色彩还原、可靠性能', 
         '', '', '', '{}', 2),
        
        # Solutions页面
        ('solutions', 'applications', 'solution_apps', 'Application Solutions', '应用解决方案', 
         'Industry Specific', '行业专用',
         'Customized solutions for different industries', '针对不同行业的定制解决方案', 
         '', '', '', '{}', 1),
        
        ('solutions', 'services', 'solution_services', 'Our Services', '我们的服务', 
         'Complete Support', '全面支持',
         'Design, installation, maintenance, and support', '设计、安装、维护和支持', 
         '', '', '', '{}', 2),
        
        # Cases页面
        ('cases', 'showcase', 'case_showcase', 'Success Stories', '成功案例', 
         'Global Projects', '全球项目',
         'Successful installations worldwide', '全球成功安装案例', 
         '', '', '', '{}', 1),
        
        ('cases', 'industries', 'case_industries', 'Industry Applications', '行业应用', 
         'Various Sectors', '各个行业',
         'Retail, sports, entertainment, corporate applications', '零售、体育、娱乐、企业应用', 
         '', '', '', '{}', 2),
        
        # News页面
        ('news', 'latest', 'latest_news', 'Latest News', '最新资讯', 
         'Industry Updates', '行业动态',
         'Stay updated with LED display technology news', '了解LED显示技术最新资讯', 
         '', '', '', '{}', 1),
        
        ('news', 'events', 'company_events', 'Company Events', '公司活动', 
         'Exhibitions Trade Shows', '展会活动',
         'Participation in industry exhibitions and events', '参与行业展会和活动', 
         '', '', '', '{}', 2),
        
        # Support页面
        ('support', 'technical', 'tech_support', 'Technical Support', '技术支持', 
         '24/7 Support', '24/7支持',
         'Professional technical support and service', '专业技术支持和服务', 
         '', '', '', '{}', 1),
        
        ('support', 'documentation', 'support_docs', 'Documentation', '技术文档', 
         'Complete Resources', '完整资源',
         'User manuals, installation guides, specifications', '用户手册、安装指南、技术规格', 
         '', '', '', '{}', 2),
        
        # Contact页面
        ('contact', 'info', 'contact_info', 'Contact Information', '联系信息', 
         'Get in Touch', '联系方式',
         'Contact us for inquiries and support', '联系我们获取咨询和支持', 
         '', '', '', '{}', 1),
        
        ('contact', 'form', 'contact_form', 'Contact Form', '联系表单', 
         'Send Message', '发送消息',
         'Send us your inquiry or request', '发送您的询问或请求', 
         '', '', '', '{}', 2)
    ]
    
    for content in default_contents:
        cursor.execute('''
            INSERT OR IGNORE INTO page_contents (
                page_name, section_name, content_type, title_en, title_zh,
                subtitle_en, subtitle_zh, content_en, content_zh,
                image_url, video_url, link_url, parameters, sort_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', content)

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

# 路由定义
@app.route('/')
@login_required
def dashboard():
    """管理后台首页"""
    conn = get_db_connection()
    
    # 获取统计数据 - 使用兼容的查询
    try:
        # 尝试查询现有products表
        products_count = conn.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    except:
        # 如果失败，使用兼容表
        try:
            products_count = conn.execute('SELECT COUNT(*) FROM products_compatible').fetchone()[0]
        except:
            products_count = 0
    
    try:
        inquiries_count = conn.execute('SELECT COUNT(*) FROM inquiries WHERE status = "new"').fetchone()[0]
    except:
        inquiries_count = 0
    
    try:
        contents_count = conn.execute('SELECT COUNT(*) FROM page_contents WHERE status = "active"').fetchone()[0]
    except:
        contents_count = 0
    
    stats = {
        'pages': 8,
        'contents': contents_count,
        'products': products_count,
        'inquiries': inquiries_count
    }
    
    # 获取最新询盘
    try:
        recent_inquiries = conn.execute('''
            SELECT * FROM inquiries 
            ORDER BY created_at DESC 
            LIMIT 5
        ''').fetchall()
    except:
        recent_inquiries = []
    
    conn.close()
    
    return render_template('enhanced_dashboard.html', 
                         stats=stats, 
                         recent_inquiries=recent_inquiries)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """管理员登录"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
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
    
    return '''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>登录 - LED管理后台</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .login-card {
                background: white;
                border-radius: 20px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                max-width: 400px;
                width: 100%;
            }
            .login-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 2rem;
                text-align: center;
                border-radius: 20px 20px 0 0;
            }
            .form-control {
                border-radius: 10px;
                border: 2px solid #e9ecef;
                padding: 12px 15px;
            }
            .btn-login {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-weight: 600;
                width: 100%;
            }
        </style>
    </head>
    <body>
        <div class="login-card">
            <div class="login-header">
                <h3><i class="fas fa-tv me-2"></i>LED管理后台</h3>
                <p class="mb-0">增强版内容管理系统</p>
            </div>
            <div class="p-4">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                                {{ message }}
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label">用户名</label>
                        <input type="text" class="form-control" name="username" value="admin" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">密码</label>
                        <input type="password" class="form-control" name="password" value="admin123" required>
                    </div>
                    <button type="submit" class="btn btn-primary btn-login">
                        <i class="fas fa-sign-in-alt me-2"></i>登录
                    </button>
                </form>
                <div class="mt-3 text-center">
                    <small class="text-muted">默认账号: admin / admin123</small>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    """管理员登出"""
    session.clear()
    flash('已成功登出！', 'info')
    return redirect(url_for('login'))

@app.route('/pages')
@login_required
def page_list():
    """页面列表"""
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
    """页面内容管理"""
    if page_name not in ['home', 'about', 'products', 'solutions', 'cases', 'news', 'support', 'contact']:
        flash('页面不存在！', 'error')
        return redirect(url_for('page_list'))
    
    conn = get_db_connection()
    
    # 获取页面内容
    contents = conn.execute('''
        SELECT * FROM page_contents 
        WHERE page_name = ? 
        ORDER BY sort_order, id
    ''', (page_name,)).fetchall()
    
    conn.close()
    
    page_titles = {
        'home': '首页管理',
        'about': '关于我们',
        'products': '产品中心',
        'solutions': '解决方案',
        'cases': '成功案例',
        'news': '新闻资讯',
        'support': '技术支持',
        'contact': '联系我们'
    }
    
    return render_template('page_content_manager.html', 
                         page_name=page_name,
                         page_title=page_titles.get(page_name, page_name),
                         contents=contents)

@app.route('/pages/<page_name>/content/add', methods=['GET', 'POST'])
@login_required
def add_page_content(page_name):
    """添加页面内容"""
    if request.method == 'POST':
        data = request.form
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO page_contents (
                page_name, section_name, content_type, title_en, title_zh,
                subtitle_en, subtitle_zh, content_en, content_zh,
                image_url, video_url, link_url, parameters, sort_order, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            page_name, data.get('section_name', ''), data.get('content_type', ''),
            data.get('title_en', ''), data.get('title_zh', ''),
            data.get('subtitle_en', ''), data.get('subtitle_zh', ''),
            data.get('content_en', ''), data.get('content_zh', ''),
            data.get('image_url', ''), data.get('video_url', ''), data.get('link_url', ''),
            data.get('parameters', '{}'), int(data.get('sort_order', 0)),
            data.get('status', 'active')
        ))
        conn.commit()
        conn.close()
        
        flash('内容添加成功！', 'success')
        return redirect(url_for('page_content_manager', page_name=page_name))
    
    return redirect(url_for('page_content_manager', page_name=page_name))

@app.route('/pages/<page_name>/content/<int:content_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_page_content(page_name, content_id):
    """编辑页面内容"""
    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.form
        
        # 更新内容
        conn.execute('''
            UPDATE page_contents SET
                section_name = ?, content_type = ?, title_en = ?, title_zh = ?,
                subtitle_en = ?, subtitle_zh = ?, content_en = ?, content_zh = ?,
                image_url = ?, video_url = ?, link_url = ?, parameters = ?,
                sort_order = ?, status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data.get('section_name', ''), data.get('content_type', ''),
            data.get('title_en', ''), data.get('title_zh', ''),
            data.get('subtitle_en', ''), data.get('subtitle_zh', ''),
            data.get('content_en', ''), data.get('content_zh', ''),
            data.get('image_url', ''), data.get('video_url', ''), data.get('link_url', ''),
            data.get('parameters', '{}'), int(data.get('sort_order', 0)),
            data.get('status', 'active'), content_id
        ))
        conn.commit()
        conn.close()
        
        flash('内容更新成功！', 'success')
        return redirect(url_for('page_content_manager', page_name=page_name))
    
    conn.close()
    return redirect(url_for('page_content_manager', page_name=page_name))

@app.route('/pages/<page_name>/content/<int:content_id>/delete', methods=['POST'])
@login_required
def delete_page_content(page_name, content_id):
    """删除页面内容"""
    conn = get_db_connection()
    conn.execute('DELETE FROM page_contents WHERE id = ?', (content_id,))
    conn.commit()
    conn.close()
    
    flash('内容删除成功！', 'success')
    return redirect(url_for('page_content_manager', page_name=page_name))

# API接口
@app.route('/api/pages/<page_name>/content')
def api_page_content(page_name):
    """获取页面内容API"""
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

@app.route('/api/contact', methods=['POST'])
def api_contact():
    """接收联系表单"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO inquiries (name, email, company, phone, product_interest, message)
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
        
        return jsonify({'status': 'success', 'message': 'Contact form submitted successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 启动修复版增强LED管理后台")
    print("=" * 60)
    
    # 初始化数据库
    print("📊 初始化兼容数据库...")
    init_compatible_database()
    
    print("✅ 数据库初始化完成")
    print("🌐 管理后台地址: http://localhost:5002")
    print("👤 默认登录账号: admin")
    print("🔑 默认登录密码: admin123")
    print("=" * 60)
    print("📋 功能特色:")
    print("   • 完整的8个前端页面内容管理")
    print("   • 标题、副标题、正文、图片、视频编辑")
    print("   • 中英文双语内容支持")
    print("   • 兼容现有数据库结构")
    print("   • 实时预览和API接口")
    print("=" * 60)
    
    try:
        # 启动Flask应用
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5002,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 管理后台已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == '__main__':
    main()