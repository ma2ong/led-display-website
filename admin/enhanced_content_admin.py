#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced LED Display Website Admin Panel
完整的前端页面内容管理系统
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
from PIL import Image
import uuid

app = Flask(__name__)
app.secret_key = 'led_enhanced_admin_2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'avi', 'mov', 'wmv', 'pdf', 'doc', 'docx'}
app.config['JSON_AS_ASCII'] = False

# Enable CORS
CORS(app, origins=['*'], supports_credentials=True)

# 确保目录存在
directories = [
    'static/uploads/home', 'static/uploads/about', 'static/uploads/products',
    'static/uploads/solutions', 'static/uploads/cases', 'static/uploads/news',
    'static/uploads/support', 'static/uploads/contact', 'static/uploads/media'
]
for directory in directories:
    os.makedirs(directory, exist_ok=True)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_uploaded_file(file, category='media'):
    """处理上传的文件"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], category, unique_filename)
        file.save(file_path)
        
        # 如果是图片，进行优化处理
        if ext.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            try:
                with Image.open(file_path) as img:
                    if img.width > 1920:
                        ratio = 1920 / img.width
                        new_height = int(img.height * ratio)
                        img = img.resize((1920, new_height), Image.Resampling.LANCZOS)
                        img.save(file_path, optimize=True, quality=85)
            except Exception as e:
                print(f"图片处理错误: {e}")
        
        return f"admin/static/uploads/{category}/{unique_filename}"
    return None

def init_enhanced_db():
    """初始化增强版数据库"""
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
    
    # 页面内容表 - 核心表，存储所有页面的内容
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
    
    # 产品表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_en TEXT NOT NULL,
            name_zh TEXT NOT NULL,
            category TEXT NOT NULL,
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
            title_en TEXT NOT NULL,
            title_zh TEXT NOT NULL,
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
            title_en TEXT NOT NULL,
            title_zh TEXT NOT NULL,
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
            title_en TEXT NOT NULL,
            title_zh TEXT NOT NULL,
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
    
    # 创建默认管理员
    cursor.execute('SELECT COUNT(*) FROM admins')
    if cursor.fetchone()[0] == 0:
        default_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO admins (username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin', default_password, 'admin@lianjinled.com', 'super_admin'))
    
    # 插入默认页面内容结构
    default_page_contents = [
        # Home页面内容
        ('home', 'hero', 'hero_section', 'LED Display Solutions', 'LED显示屏解决方案', 
         'Professional LED Display Technology', '专业LED显示技术', 
         'Leading manufacturer of high-quality LED displays', '高品质LED显示屏领先制造商', '', '', '', '', 1),
        ('home', 'features', 'feature_list', 'Our Features', '我们的特色', '', '', 
         'High Quality, Innovation, Service', '高品质、创新、服务', '', '', '', '', 2),
        ('home', 'products', 'product_showcase', 'Our Products', '我们的产品', '', '', 
         'Complete range of LED display solutions', '完整的LED显示屏解决方案', '', '', '', '', 3),
        
        # About页面内容
        ('about', 'company', 'company_intro', 'About Lianjin LED', '关于联锦LED', 
         'Leading LED Display Manufacturer', '领先的LED显示屏制造商',
         'Professional LED display solutions provider', '专业LED显示屏解决方案提供商', '', '', '', '', 1),
        ('about', 'history', 'company_history', 'Our History', '我们的历史', '', '',
         'Founded in 2010, continuous innovation', '成立于2010年，持续创新', '', '', '', '', 2),
        ('about', 'team', 'team_intro', 'Our Team', '我们的团队', '', '',
         'Professional R&D and service team', '专业的研发和服务团队', '', '', '', '', 3),
        
        # Products页面内容
        ('products', 'categories', 'product_categories', 'Product Categories', '产品分类', '', '',
         'Complete LED display product line', '完整的LED显示屏产品线', '', '', '', '', 1),
        ('products', 'features', 'product_features', 'Product Features', '产品特色', '', '',
         'High quality, reliability, innovation', '高品质、可靠性、创新', '', '', '', '', 2),
        
        # Solutions页面内容
        ('solutions', 'applications', 'solution_apps', 'Application Solutions', '应用解决方案', '', '',
         'Customized solutions for different industries', '针对不同行业的定制解决方案', '', '', '', '', 1),
        ('solutions', 'services', 'solution_services', 'Our Services', '我们的服务', '', '',
         'Complete pre-sales and after-sales service', '完整的售前售后服务', '', '', '', '', 2),
        
        # Cases页面内容
        ('cases', 'showcase', 'case_showcase', 'Success Cases', '成功案例', '', '',
         'Successful project implementations worldwide', '全球成功项目实施', '', '', '', '', 1),
        ('cases', 'industries', 'case_industries', 'Industry Applications', '行业应用', '', '',
         'Various industry application cases', '各行业应用案例', '', '', '', '', 2),
        
        # News页面内容
        ('news', 'latest', 'latest_news', 'Latest News', '最新资讯', '', '',
         'Industry news and company updates', '行业资讯和公司动态', '', '', '', '', 1),
        ('news', 'events', 'company_events', 'Company Events', '公司活动', '', '',
         'Exhibition and event participation', '展会和活动参与', '', '', '', '', 2),
        
        # Support页面内容
        ('support', 'technical', 'tech_support', 'Technical Support', '技术支持', '', '',
         'Professional technical support service', '专业技术支持服务', '', '', '', '', 1),
        ('support', 'documentation', 'support_docs', 'Documentation', '技术文档', '', '',
         'Complete product documentation', '完整的产品文档', '', '', '', '', 2),
        
        # Contact页面内容
        ('contact', 'info', 'contact_info', 'Contact Information', '联系信息', '', '',
         'Get in touch with us', '与我们联系', '', '', '', '', 1),
        ('contact', 'form', 'contact_form', 'Contact Form', '联系表单', '', '',
         'Send us your inquiry', '发送您的询问', '', '', '', '', 2)
    ]
    
    for content in default_page_contents:
        cursor.execute('''
            INSERT OR IGNORE INTO page_contents (
                page_name, section_name, content_type, title_en, title_zh,
                subtitle_en, subtitle_zh, content_en, content_zh,
                image_url, video_url, link_url, parameters, sort_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', content)
    
    conn.commit()
    conn.close()

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
    
    # 获取统计数据
    stats = {
        'pages': len(['home', 'about', 'products', 'solutions', 'cases', 'news', 'support', 'contact']),
        'contents': conn.execute('SELECT COUNT(*) FROM page_contents WHERE status = "active"').fetchone()[0],
        'products': conn.execute('SELECT COUNT(*) FROM products WHERE status = "active"').fetchone()[0],
        'news': conn.execute('SELECT COUNT(*) FROM news WHERE status = "published"').fetchone()[0],
        'cases': conn.execute('SELECT COUNT(*) FROM cases WHERE status = "published"').fetchone()[0],
        'inquiries': conn.execute('SELECT COUNT(*) FROM inquiries WHERE status = "new"').fetchone()[0]
    }
    
    # 获取最新询盘
    recent_inquiries = conn.execute('''
        SELECT * FROM inquiries 
        ORDER BY created_at DESC 
        LIMIT 5
    ''').fetchall()
    
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
    
    return render_template('enhanced_login.html')

@app.route('/logout')
def logout():
    """管理员登出"""
    session.clear()
    flash('已成功登出！', 'info')
    return redirect(url_for('login'))

# 页面内容管理路由
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
    
    return render_template('page_list.html', pages=pages)

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
        
        # 处理文件上传
        image_url = None
        video_url = None
        
        if 'image_file' in request.files and request.files['image_file'].filename:
            image_url = process_uploaded_file(request.files['image_file'], page_name)
        
        if 'video_file' in request.files and request.files['video_file'].filename:
            video_url = process_uploaded_file(request.files['video_file'], page_name)
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO page_contents (
                page_name, section_name, content_type, title_en, title_zh,
                subtitle_en, subtitle_zh, content_en, content_zh,
                image_url, video_url, link_url, parameters, sort_order, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            page_name, data['section_name'], data['content_type'],
            data.get('title_en', ''), data.get('title_zh', ''),
            data.get('subtitle_en', ''), data.get('subtitle_zh', ''),
            data.get('content_en', ''), data.get('content_zh', ''),
            image_url, video_url, data.get('link_url', ''),
            data.get('parameters', ''), int(data.get('sort_order', 0)),
            data.get('status', 'active')
        ))
        conn.commit()
        conn.close()
        
        flash('内容添加成功！', 'success')
        return redirect(url_for('page_content_manager', page_name=page_name))
    
    return render_template('add_page_content.html', page_name=page_name)

@app.route('/pages/<page_name>/content/<int:content_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_page_content(page_name, content_id):
    """编辑页面内容"""
    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.form
        
        # 获取现有内容
        content = conn.execute('SELECT * FROM page_contents WHERE id = ?', (content_id,)).fetchone()
        if not content:
            flash('内容不存在！', 'error')
            return redirect(url_for('page_content_manager', page_name=page_name))
        
        # 处理文件上传
        image_url = content['image_url']
        video_url = content['video_url']
        
        if 'image_file' in request.files and request.files['image_file'].filename:
            new_image_url = process_uploaded_file(request.files['image_file'], page_name)
            if new_image_url:
                image_url = new_image_url
        
        if 'video_file' in request.files and request.files['video_file'].filename:
            new_video_url = process_uploaded_file(request.files['video_file'], page_name)
            if new_video_url:
                video_url = new_video_url
        
        # 更新内容
        conn.execute('''
            UPDATE page_contents SET
                section_name = ?, content_type = ?, title_en = ?, title_zh = ?,
                subtitle_en = ?, subtitle_zh = ?, content_en = ?, content_zh = ?,
                image_url = ?, video_url = ?, link_url = ?, parameters = ?,
                sort_order = ?, status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data['section_name'], data['content_type'],
            data.get('title_en', ''), data.get('title_zh', ''),
            data.get('subtitle_en', ''), data.get('subtitle_zh', ''),
            data.get('content_en', ''), data.get('content_zh', ''),
            image_url, video_url, data.get('link_url', ''),
            data.get('parameters', ''), int(data.get('sort_order', 0)),
            data.get('status', 'active'), content_id
        ))
        conn.commit()
        conn.close()
        
        flash('内容更新成功！', 'success')
        return redirect(url_for('page_content_manager', page_name=page_name))
    
    # GET请求 - 显示编辑表单
    content = conn.execute('SELECT * FROM page_contents WHERE id = ?', (content_id,)).fetchone()
    conn.close()
    
    if not content:
        flash('内容不存在！', 'error')
        return redirect(url_for('page_content_manager', page_name=page_name))
    
    return render_template('edit_page_content.html', 
                         page_name=page_name, 
                         content=content)

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

# 产品管理路由
@app.route('/products')
@login_required
def products():
    """产品管理"""
    conn = get_db_connection()
    products = conn.execute('''
        SELECT * FROM products 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('enhanced_products.html', products=products)

# 新闻管理路由
@app.route('/news')
@login_required
def news():
    """新闻管理"""
    conn = get_db_connection()
    news_list = conn.execute('''
        SELECT * FROM news 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('enhanced_news.html', news_list=news_list)

# 案例管理路由
@app.route('/cases')
@login_required
def cases():
    """案例管理"""
    conn = get_db_connection()
    cases_list = conn.execute('''
        SELECT * FROM cases 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('enhanced_cases.html', cases_list=cases_list)

# 解决方案管理路由
@app.route('/solutions')
@login_required
def solutions():
    """解决方案管理"""
    conn = get_db_connection()
    solutions_list = conn.execute('''
        SELECT * FROM solutions 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('enhanced_solutions.html', solutions_list=solutions_list)

# 询盘管理路由
@app.route('/inquiries')
@login_required
def inquiries():
    """询盘管理"""
    conn = get_db_connection()
    inquiries_list = conn.execute('''
        SELECT * FROM inquiries 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('enhanced_inquiries.html', inquiries_list=inquiries_list)

# 媒体文件管理路由
@app.route('/media')
@login_required
def media_management():
    """媒体文件管理"""
    conn = get_db_connection()
    media_files = conn.execute('''
        SELECT * FROM media_files 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('enhanced_media.html', media_files=media_files)

@app.route('/media/upload', methods=['POST'])
@login_required
def upload_media():
    """上传媒体文件"""
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        file_path = process_uploaded_file(file, 'media')
        
        if file_path:
            # 保存到数据库
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO media_files (
                    filename, original_name, file_type, file_size, mime_type,
                    file_path, uploaded_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                os.path.basename(file_path),
                file.filename,
                'image' if file.content_type.startswith('image/') else 'video' if file.content_type.startswith('video/') else 'document',
                0,  # 文件大小可以后续计算
                file.content_type,
                file_path,
                session['admin_username']
            ))
            conn.commit()
            conn.close()
            
            return jsonify({
                'status': 'success',
                'message': 'File uploaded successfully',
                'file_path': file_path
            })
    
    return jsonify({'status': 'error', 'message': 'Invalid file type'}), 400

# 设置管理路由
@app.route('/settings')
@login_required
def settings():
    """网站设置"""
    conn = get_db_connection()
    settings_list = conn.execute('''
        SELECT * FROM settings 
        ORDER BY key
    ''').fetchall()
    conn.close()
    
    return render_template('enhanced_settings.html', settings_list=settings_list)

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
    data = request.get_json()
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO inquiries (name, email, company, phone, product_interest, message)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (