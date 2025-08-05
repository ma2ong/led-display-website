#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED Display Website Admin Panel
基于Flask的后端管理系统
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
app.secret_key = 'led_admin_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'avi', 'mov', 'wmv'}
app.config['JSON_AS_ASCII'] = False  # Ensure UTF-8 for JSON responses

# Enable CORS for all routes - CloudStudio compatible
CORS(app, origins=['*'], supports_credentials=True)

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/uploads/products', exist_ok=True)
os.makedirs('static/uploads/news', exist_ok=True)
os.makedirs('static/uploads/cases', exist_ok=True)

# 确保前端assets目录存在
frontend_assets = os.path.join('..', 'assets', 'products')
os.makedirs(frontend_assets, exist_ok=True)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_uploaded_image(file, category='products'):
    """处理上传的图片"""
    if file and allowed_file(file.filename):
        # 生成唯一文件名
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        # 保存到admin静态目录
        admin_path = os.path.join(app.config['UPLOAD_FOLDER'], category, unique_filename)
        file.save(admin_path)
        
        # 同时复制到前端assets目录
        frontend_path = os.path.join('..', 'assets', category, unique_filename)
        
        # 使用PIL处理图片并保存到前端目录
        try:
            with Image.open(admin_path) as img:
                # 优化图片大小
                if img.width > 1200:
                    ratio = 1200 / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((1200, new_height), Image.Resampling.LANCZOS)
                
                # 保存到前端目录
                img.save(frontend_path, optimize=True, quality=85)
        except Exception as e:
            print(f"图片处理错误: {e}")
            # 如果处理失败，直接复制文件
            import shutil
            shutil.copy2(admin_path, frontend_path)
        
        return f"assets/{category}/{unique_filename}"
    return None

def process_uploaded_video(file, category='products'):
    """处理上传的视频"""
    if file and allowed_file(file.filename):
        # 生成唯一文件名
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        # 保存到admin静态目录
        admin_path = os.path.join(app.config['UPLOAD_FOLDER'], category, unique_filename)
        file.save(admin_path)
        
        # 同时复制到前端assets目录
        frontend_path = os.path.join('..', 'assets', category, unique_filename)
        
        # 直接复制视频文件
        try:
            import shutil
            shutil.copy2(admin_path, frontend_path)
        except Exception as e:
            print(f"视频处理错误: {e}")
        
        return f"assets/{category}/{unique_filename}"
    return None

# 数据库初始化
def init_db():
    """初始化数据库"""
    conn = sqlite3.connect('led_admin.db')
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
    
    # 报价请求表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            company TEXT NOT NULL,
            product_type TEXT,
            display_size TEXT,
            quantity INTEGER,
            requirements TEXT,
            timeline TEXT,
            budget TEXT,
            status TEXT DEFAULT 'pending',
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
    
    # 创建默认管理员账户
    cursor.execute('SELECT COUNT(*) FROM admins')
    if cursor.fetchone()[0] == 0:
        default_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO admins (username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin', default_password, 'admin@lianjinled.com', 'super_admin'))
    
    # 插入前端网页已有的产品数据
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        default_products = [
            ('Fine Pitch LED Display', '小间距LED显示屏', 'fine-pitch', 
             'Ultra-high resolution displays with pixel pitches from P0.9 to P1.56, perfect for control rooms, broadcast studios, and corporate environments.',
             '像素间距从P0.9到P1.56的超高分辨率显示屏，完美适用于控制室、广播演播室和企业环境。',
             'Pixel Pitch: P0.9-P1.56\nResolution: 4K/8K\nBrightness: 600-1200 nits\nRefresh Rate: 3840Hz\nViewing Angle: 160°/160°',
             '4K/8K Resolution, Seamless Splicing, High Refresh Rate',
             'assets/products/fine-pitch-led.jpg', 'active'),
            
            ('Outdoor LED Display', '户外LED显示屏', 'outdoor',
             'Weather-resistant displays for outdoor advertising and information with high brightness and energy efficiency.',
             '适用于户外广告和信息显示的防风雨显示屏，具有高亮度和节能特性。',
             'Pixel Pitch: P3-P10\nBrightness: 5000-8000 nits\nIP Rating: IP65\nOperating Temperature: -40°C to +60°C\nViewing Distance: 3-100m',
             'IP65 Waterproof, High Brightness, Energy Efficient',
             'assets/products/outdoor-led.jpg', 'active'),
            
            ('Indoor LED Display', '室内LED显示屏', 'indoor',
             'High-quality displays for indoor commercial and corporate applications with full color display and easy installation.',
             '适用于室内商业和企业应用的高质量显示屏，具有全彩显示和易于安装的特点。',
             'Pixel Pitch: P1.25-P4\nBrightness: 800-1500 nits\nRefresh Rate: 1920-3840Hz\nColor Temperature: 3200K-9300K\nLifespan: 100,000 hours',
             'Full Color Display, Easy Installation, Low Maintenance',
             'assets/products/indoor-led.jpg', 'active'),
            
            ('Transparent LED Display', '透明LED显示屏', 'transparent',
             'Innovative transparent displays that blend seamlessly with architecture while delivering stunning visual impact.',
             '与建筑完美融合的创新透明显示屏，同时提供令人惊叹的视觉冲击。',
             'Transparency: 70-90%\nPixel Pitch: P3.91-P7.81\nBrightness: 4000-6000 nits\nWeight: 12kg/m²\nMaintenance: Front/Rear',
             '90% Transparency, Lightweight Design, Creative Applications',
             'assets/products/transparent-led.jpg', 'active'),
            
            ('Creative LED Display', '创意LED显示屏', 'creative',
             'Custom-shaped displays for unique architectural and artistic applications with flexible design options.',
             '适用于独特建筑和艺术应用的定制形状显示屏，具有灵活的设计选项。',
             'Shape: Customizable\nPixel Pitch: P1.25-P10\nCurve Radius: R≥500mm\nInstallation: Flexible\nControl: Professional',
             'Custom Shapes, Flexible Design, Artistic Integration',
             'assets/products/creative-led.jpg', 'active'),
            
            ('Rental LED Display', '租赁LED显示屏', 'rental',
             'Portable and quick-setup displays for events and temporary installations with lightweight and durable design.',
             '适用于活动和临时安装的便携式快速安装显示屏，具有轻量化和耐用的设计。',
             'Pixel Pitch: P2.6-P4.81\nWeight: 6-8kg/panel\nSetup Time: <30min\nConnection: Quick Lock\nFlight Case: Available',
             'Quick Setup, Lightweight, Durable Design',
             'assets/products/rental-led.jpg', 'active')
        ]
        
        for product in default_products:
            cursor.execute('''
                INSERT INTO products (
                    name_en, name_zh, category, description_en, description_zh,
                    specifications, features, images, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', product)
    
    # 插入默认设置
    default_settings = [
        ('site_title_en', 'Lianjin LED Display', 'English site title'),
        ('site_title_zh', '联锦LED显示屏', 'Chinese site title'),
        ('company_phone', '+86-755-1234-5678', 'Company phone number'),
        ('company_email', 'info@lianjinled.com', 'Company email'),
        ('company_address_en', 'Shenzhen, Guangdong Province, China', 'English address'),
        ('company_address_zh', '中国广东省深圳市', 'Chinese address')
    ]
    
    for key, value, desc in default_settings:
        cursor.execute('''
            INSERT OR IGNORE INTO settings (key, value, description)
            VALUES (?, ?, ?)
        ''', (key, value, desc))
    
    conn.commit()
    conn.close()

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 数据库连接函数
def get_db_connection():
    conn = sqlite3.connect('led_admin.db')
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
        'products': conn.execute('SELECT COUNT(*) FROM products WHERE status = "active"').fetchone()[0],
        'news': conn.execute('SELECT COUNT(*) FROM news WHERE status = "published"').fetchone()[0],
        'cases': conn.execute('SELECT COUNT(*) FROM cases WHERE status = "published"').fetchone()[0],
        'inquiries': conn.execute('SELECT COUNT(*) FROM inquiries WHERE status = "new"').fetchone()[0],
        'quotes': conn.execute('SELECT COUNT(*) FROM quotes WHERE status = "pending"').fetchone()[0]
    }
    
    # 获取最新询盘
    recent_inquiries = conn.execute('''
        SELECT * FROM inquiries 
        ORDER BY created_at DESC 
        LIMIT 5
    ''').fetchall()
    
    # 获取最新报价请求
    recent_quotes = conn.execute('''
        SELECT * FROM quotes 
        ORDER BY created_at DESC 
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_inquiries=recent_inquiries,
                         recent_quotes=recent_quotes)

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
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """管理员登出"""
    session.clear()
    flash('已成功登出！', 'info')
    return redirect(url_for('login'))

# 产品管理
@app.route('/products')
@login_required
def products():
    """产品列表"""
    conn = get_db_connection()
    products = conn.execute('''
        SELECT * FROM products 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('products.html', products=products)

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """添加产品"""
    if request.method == 'POST':
        data = request.form
        
        # 处理图片上传
        image_path = None
        if 'product_image' in request.files:
            file = request.files['product_image']
            if file.filename != '':
                image_path = process_uploaded_image(file, 'products')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (
                name_en, name_zh, category, description_en, description_zh,
                specifications, features, images, price, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name_en'], data['name_zh'], data['category'],
            data['description_en'], data['description_zh'],
            data['specifications'], data['features'],
            image_path or data.get('images', ''),
            float(data['price']) if data['price'] else None,
            data['status']
        ))
        
        # 获取新创建的产品ID
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        flash('产品添加成功！', 'success')
        return redirect(url_for('products'))
    
    # 获取产品分类
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM product_categories ORDER BY sort_order').fetchall()
    conn.close()
    
    return render_template('product_form.html', action='add', categories=categories)

@app.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    """编辑产品"""
    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.form
        
        # 处理新图片上传
        if 'new_images' in request.files:
            new_images = request.files.getlist('new_images')
            new_alts = request.form.getlist('new_image_alts')
            
            for i, file in enumerate(new_images):
                if file and file.filename != '':
                    image_path = process_uploaded_image(file, 'products')
                    if image_path:
                        alt_text = new_alts[i] if i < len(new_alts) else ''
                        is_primary = request.form.get('new_primary_image') == str(i+1)
                        
                        conn.execute('''
                            INSERT INTO product_images (product_id, image_url, alt_text, is_primary)
                            VALUES (?, ?, ?, ?)
                        ''', (id, image_path, alt_text, is_primary))
        
        # 处理新视频上传
        if 'new_videos' in request.files:
            new_videos = request.files.getlist('new_videos')
            new_titles = request.form.getlist('new_video_titles')
            new_descriptions = request.form.getlist('new_video_descriptions')
            
            for i, file in enumerate(new_videos):
                if file and file.filename != '':
                    video_path = process_uploaded_video(file, 'products')
                    if video_path:
                        title = new_titles[i] if i < len(new_titles) else ''
                        description = new_descriptions[i] if i < len(new_descriptions) else ''
                        
                        conn.execute('''
                            INSERT INTO product_videos (product_id, video_url, title, description)
                            VALUES (?, ?, ?, ?)
                        ''', (id, video_path, title, description))
        
        # 更新产品基本信息
        conn.execute('''
            UPDATE products SET
                name_en = ?, name_zh = ?, category = ?, description_en = ?, description_zh = ?,
                specifications = ?, features = ?, price = ?, status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data['name_en'], data['name_zh'], data['category'],
            data['description_en'], data['description_zh'],
            data['specifications'], data['features'],
            float(data['price']) if data['price'] else None,
            data['status'], id
        ))
        
        # 更新现有图片的alt文本
        for key, value in data.items():
            if key.startswith('alt_text_'):
                image_id = key.split('_')[-1]
                conn.execute('UPDATE product_images SET alt_text = ? WHERE id = ?', (value, image_id))
        
        # 更新现有视频信息
        for key, value in data.items():
            if key.startswith('video_title_'):
                video_id = key.split('_')[-1]
                conn.execute('UPDATE product_videos SET title = ? WHERE id = ?', (value, video_id))
            elif key.startswith('video_desc_'):
                video_id = key.split('_')[-1]
                conn.execute('UPDATE product_videos SET description = ? WHERE id = ?', (value, video_id))
        
        conn.commit()
        conn.close()
        
        flash('产品更新成功！', 'success')
        return redirect(url_for('products'))
    
    # GET请求 - 显示编辑表单
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    if not product:
        flash('产品不存在！', 'error')
        return redirect(url_for('products'))
    
    # 获取产品分类
    categories = conn.execute('SELECT * FROM product_categories ORDER BY sort_order').fetchall()
    
    # 获取产品图片
    product_images = conn.execute('''
        SELECT * FROM product_images WHERE product_id = ? ORDER BY sort_order, id
    ''', (id,)).fetchall()
    
    # 获取产品视频
    product_videos = conn.execute('''
        SELECT * FROM product_videos WHERE product_id = ? ORDER BY sort_order, id
    ''', (id,)).fetchall()
    
    # 获取SEO设置
    seo = conn.execute('''
        SELECT * FROM seo_settings WHERE page_name = ?
    ''', (f'product_{id}',)).fetchone()
    
    # 获取产品统计
    product_stats = {
        'views': 0,  # 可以从日志表获取
        'inquiries': conn.execute('SELECT COUNT(*) FROM inquiries WHERE product_interest LIKE ?', (f'%{product["category"]}%',)).fetchone()[0]
    }
    
    conn.close()
    
    return render_template('product_edit.html', 
                         product=product, 
                         categories=categories,
                         product_images=product_images,
                         product_videos=product_videos,
                         seo=seo,
                         product_stats=product_stats)

@app.route('/products/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    """删除产品"""
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    flash('产品删除成功！', 'success')
    return redirect(url_for('products'))

# 询盘管理
@app.route('/inquiries')
@login_required
def inquiries():
    """询盘列表"""
    conn = get_db_connection()
    inquiries = conn.execute('''
        SELECT * FROM inquiries 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('inquiries.html', inquiries=inquiries)

@app.route('/inquiries/<int:id>/status', methods=['POST'])
@login_required
def update_inquiry_status(id):
    """更新询盘状态"""
    status = request.form.get('status')
    
    conn = get_db_connection()
    conn.execute('''
        UPDATE inquiries 
        SET status = ?, handled_by = ?, handled_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (status, session['admin_username'], id))
    conn.commit()
    conn.close()
    
    flash('询盘状态更新成功！', 'success')
    return redirect(url_for('inquiries'))

# 报价管理
@app.route('/quotes')
@login_required
def quotes():
    """报价请求列表"""
    conn = get_db_connection()
    quotes = conn.execute('''
        SELECT * FROM quotes 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('quotes.html', quotes=quotes)

@app.route('/quotes/<int:id>/status', methods=['POST'])
@login_required
def update_quote_status(id):
    """更新报价状态"""
    status = request.form.get('status')
    
    conn = get_db_connection()
    conn.execute('''
        UPDATE quotes 
        SET status = ?, handled_by = ?, handled_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (status, session['admin_username'], id))
    conn.commit()
    conn.close()
    
    flash('报价状态更新成功！', 'success')
    return redirect(url_for('quotes'))

# API接口 - 用于前端网站
@app.route('/api/contact', methods=['POST'])
def api_contact():
    """接收联系表单"""
    data = request.get_json()
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO inquiries (name, email, company, phone, product_interest, message)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name'), data.get('email'), data.get('company'),
        data.get('phone'), data.get('product'), data.get('message')
    ))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'message': 'Thank you for your inquiry!'})

@app.route('/api/products', methods=['GET'])
def api_products():
    """获取产品列表API - 供前端网站使用"""
    conn = get_db_connection()
    products = conn.execute('''
        SELECT * FROM products WHERE status = 'active'
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    products_list = []
    for product in products:
        products_list.append({
            'id': product['id'],
            'name_en': product['name_en'],
            'name_zh': product['name_zh'],
            'category': product['category'],
            'description_en': product['description_en'],
            'description_zh': product['description_zh'],
            'specifications': product['specifications'],
            'features': product['features'],
            'images': product['images'],
            'price': product['price']
        })
    
    response = jsonify({'status': 'success', 'products': products_list})
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

# 内容管理路由
@app.route('/content')
@login_required
def content_management():
    """内容管理页面"""
    conn = get_db_connection()
    contents = conn.execute('''
        SELECT * FROM page_contents 
        ORDER BY page_name, sort_order, section_name
    ''').fetchall()
    conn.close()
    
    return render_template('content_management.html', contents=contents)

@app.route('/content/add', methods=['POST'])
@login_required
def add_content():
    """添加内容"""
    data = request.form
    
    conn = get_db_connection()
    
    # 处理文件上传
    image_url = None
    video_url = None
    
    if data['content_type'] == 'image' and 'image_file' in request.files:
        file = request.files['image_file']
        if file.filename != '':
            image_url = process_uploaded_image(file, 'content')
    
    if data['content_type'] == 'video' and 'video_file' in request.files:
        file = request.files['video_file']
        if file.filename != '':
            video_url = process_uploaded_video(file, 'content')
    
    conn.execute('''
        INSERT INTO page_contents (
            page_name, section_name, content_type, content_en, content_zh,
            image_url, video_url, sort_order, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['page_name'], data['section_name'], data['content_type'],
        data.get('content_en', ''), data.get('content_zh', ''),
        image_url, video_url, int(data.get('sort_order', 0)), data['status']
    ))
    
    conn.commit()
    conn.close()
    
    flash('内容添加成功！', 'success')
    return redirect(url_for('content_management'))

@app.route('/content/edit/<int:id>', methods=['POST'])
@login_required
def edit_content(id):
    """编辑内容"""
    data = request.form
    
    conn = get_db_connection()
    
    # 获取现有内容
    content = conn.execute('SELECT * FROM page_contents WHERE id = ?', (id,)).fetchone()
    if not content:
        flash('内容不存在！', 'error')
        return redirect(url_for('content_management'))
    
    # 处理文件上传
    image_url = content['image_url']
    video_url = content['video_url']
    
    if 'image_file' in request.files:
        file = request.files['image_file']
        if file.filename != '':
            new_image_url = process_uploaded_image(file, 'content')
            if new_image_url:
                image_url = new_image_url
    
    if 'video_file' in request.files:
        file = request.files['video_file']
        if file.filename != '':
            new_video_url = process_uploaded_video(file, 'content')
            if new_video_url:
                video_url = new_video_url
    
    conn.execute('''
        UPDATE page_contents SET
            section_name = ?, content_en = ?, content_zh = ?,
            image_url = ?, video_url = ?, sort_order = ?, status = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (
        data['section_name'], data.get('content_en', ''), data.get('content_zh', ''),
        image_url, video_url, int(data.get('sort_order', 0)), data['status'], id
    ))
    
    conn.commit()
    conn.close()
    
    flash('内容更新成功！', 'success')
    return redirect(url_for('content_management'))

@app.route('/content/delete/<int:id>', methods=['POST'])
@login_required
def delete_content(id):
    """删除内容"""
    conn = get_db_connection()
    conn.execute('DELETE FROM page_contents WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    flash('内容删除成功！', 'success')
    return redirect(url_for('content_management'))

@app.route('/api/content/<int:id>')
@login_required
def get_content_api(id):
    """获取内容API"""
    conn = get_db_connection()
    content = conn.execute('SELECT * FROM page_contents WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if content:
        return jsonify({
            'status': 'success',
            'data': dict(content)
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Content not found'
        }), 404

# 产品图片/视频删除路由
@app.route('/products/image/delete/<int:id>', methods=['POST'])
@login_required
def delete_product_image(id):
    """删除产品图片"""
    conn = get_db_connection()
    conn.execute('DELETE FROM product_images WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})

@app.route('/products/video/delete/<int:id>', methods=['POST'])
@login_required
def delete_product_video(id):
    """删除产品视频"""
    conn = get_db_connection()
    conn.execute('DELETE FROM product_videos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})

@app.route('/products/duplicate/<int:id>', methods=['POST'])
@login_required
def duplicate_product(id):
    """复制产品"""
    conn = get_db_connection()
    
    # 获取原产品
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    if not product:
        flash('产品不存在！', 'error')
        return redirect(url_for('products'))
    
    # 创建副本
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (
            name_en, name_zh, category, description_en, description_zh,
            specifications, features, images, price, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        f"{product['name_en']} (Copy)",
        f"{product['name_zh']} (副本)",
        product['category'],
        product['description_en'],
        product['description_zh'],
        product['specifications'],
        product['features'],
        product['images'],
        product['price'],
        'draft'
    ))
    
    new_product_id = cursor.lastrowid
    
    # 复制图片
    images = conn.execute('SELECT * FROM product_images WHERE product_id = ?', (id,)).fetchall()
    for img in images:
        conn.execute('''
            INSERT INTO product_images (product_id, image_url, alt_text, sort_order, is_primary)
            VALUES (?, ?, ?, ?, ?)
        ''', (new_product_id, img['image_url'], img['alt_text'], img['sort_order'], img['is_primary']))
    
    # 复制视频
    videos = conn.execute('SELECT * FROM product_videos WHERE product_id = ?', (id,)).fetchall()
    for video in videos:
        conn.execute('''
            INSERT INTO product_videos (product_id, video_url, thumbnail_url, title, description, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (new_product_id, video['video_url'], video['thumbnail_url'], video['title'], video['description'], video['sort_order']))
    
    conn.commit()
    conn.close()
    
    flash('产品复制成功！', 'success')
    return redirect(url_for('edit_product', id=new_product_id))

@app.route('/products/preview/<int:id>')
@login_required
def preview_product(id):
    """预览产品"""
    conn = get_db_connection()
    
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    if not product:
        flash('产品不存在！', 'error')
        return redirect(url_for('products'))
    
    # 获取产品图片和视频
    product_images = conn.execute('SELECT * FROM product_images WHERE product_id = ? ORDER BY sort_order', (id,)).fetchall()
    product_videos = conn.execute('SELECT * FROM product_videos WHERE product_id = ? ORDER BY sort_order', (id,)).fetchall()
    
    conn.close()
    
    return render_template('product_preview.html', 
                         product=product,
                         product_images=product_images,
                         product_videos=product_videos)

# 媒体文件管理
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
    
    return render_template('media_management.html', media_files=media_files)

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
        # 确定文件类型
        file_type = 'image' if file.content_type.startswith('image/') else 'video' if file.content_type.startswith('video/') else 'document'
        
        # 处理文件上传
        if file_type == 'image':
            file_path = process_uploaded_image(file, 'media')
        elif file_type == 'video':
            file_path = process_uploaded_video(file, 'media')
        else:
            # 处理其他文件类型
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'media', unique_filename)
            file.save(file_path)
            file_path = f"assets/media/{unique_filename}"
        
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
                file_type,
                len(file.read()),
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

@app.route('/media/delete/<int:id>', methods=['POST'])
@login_required
def delete_media_file(id):
    """删除媒体文件"""
    conn = get_db_connection()
    
    # 获取文件信息
    media_file = conn.execute('SELECT * FROM media_files WHERE id = ?', (id,)).fetchone()
    if not media_file:
        conn.close()
        return jsonify({'status': 'error', 'message': 'File not found'}), 404
    
    # 删除物理文件
    try:
        admin_file_path = os.path.join('static', 'uploads', media_file['filename'])
        if os.path.exists(admin_file_path):
            os.remove(admin_file_path)
        
        # 删除前端文件
        frontend_file_path = os.path.join('..', media_file['file_path'])
        if os.path.exists(frontend_file_path):
            os.remove(frontend_file_path)
    except Exception as e:
        print(f"删除文件错误: {e}")
    
    # 从数据库删除记录
    conn.execute('DELETE FROM media_files WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})

# 注册API蓝图
try:
    from api import api_bp
    app.register_blueprint(api_bp)
    print("✅ API Blueprint registered successfully")
except ImportError:
    print("⚠️  Warning: API blueprint not found, continuing without it")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED Display Website Admin Panel
基于Flask的后端管理系统
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
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
app.secret_key = 'led_admin_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['JSON_AS_ASCII'] = False  # Ensure UTF-8 for JSON responses

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/uploads/products', exist_ok=True)
os.makedirs('static/uploads/news', exist_ok=True)
os.makedirs('static/uploads/cases', exist_ok=True)

# 确保前端assets目录存在
frontend_assets = os.path.join('..', 'assets', 'products')
os.makedirs(frontend_assets, exist_ok=True)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_uploaded_image(file, category='products'):
    """处理上传的图片"""
    if file and allowed_file(file.filename):
        # 生成唯一文件名
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        # 保存到admin静态目录
        admin_path = os.path.join(app.config['UPLOAD_FOLDER'], category, unique_filename)
        file.save(admin_path)
        
        # 同时复制到前端assets目录
        frontend_path = os.path.join('..', 'assets', category, unique_filename)
        
        # 使用PIL处理图片并保存到前端目录
        try:
            with Image.open(admin_path) as img:
                # 优化图片大小
                if img.width > 1200:
                    ratio = 1200 / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((1200, new_height), Image.Resampling.LANCZOS)
                
                # 保存到前端目录
                img.save(frontend_path, optimize=True, quality=85)
        except Exception as e:
            print(f"图片处理错误: {e}")
            # 如果处理失败，直接复制文件
            import shutil
            shutil.copy2(admin_path, frontend_path)
        
        return f"assets/{category}/{unique_filename}"
    return None

# 数据库初始化
def init_db():
    """初始化数据库"""
    conn = sqlite3.connect('led_admin.db')
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
    
    # 报价请求表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            company TEXT NOT NULL,
            product_type TEXT,
            display_size TEXT,
            quantity INTEGER,
            requirements TEXT,
            timeline TEXT,
            budget TEXT,
            status TEXT DEFAULT 'pending',
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
    
    # 创建默认管理员账户
    cursor.execute('SELECT COUNT(*) FROM admins')
    if cursor.fetchone()[0] == 0:
        default_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO admins (username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin', default_password, 'admin@lianjinled.com', 'super_admin'))
    
    # 插入前端网页已有的产品数据
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        default_products = [
            ('Fine Pitch LED Display', '小间距LED显示屏', 'fine-pitch', 
             'Ultra-high resolution displays with pixel pitches from P0.9 to P1.56, perfect for control rooms, broadcast studios, and corporate environments.',
             '像素间距从P0.9到P1.56的超高分辨率显示屏，完美适用于控制室、广播演播室和企业环境。',
             'Pixel Pitch: P0.9-P1.56\nResolution: 4K/8K\nBrightness: 600-1200 nits\nRefresh Rate: 3840Hz\nViewing Angle: 160°/160°',
             '4K/8K Resolution, Seamless Splicing, High Refresh Rate',
             'assets/products/fine-pitch-led.jpg', 'active'),
            
            ('Outdoor LED Display', '户外LED显示屏', 'outdoor',
             'Weather-resistant displays for outdoor advertising and information with high brightness and energy efficiency.',
             '适用于户外广告和信息显示的防风雨显示屏，具有高亮度和节能特性。',
             'Pixel Pitch: P3-P10\nBrightness: 5000-8000 nits\nIP Rating: IP65\nOperating Temperature: -40°C to +60°C\nViewing Distance: 3-100m',
             'IP65 Waterproof, High Brightness, Energy Efficient',
             'assets/products/outdoor-led.jpg', 'active'),
            
            ('Indoor LED Display', '室内LED显示屏', 'indoor',
             'High-quality displays for indoor commercial and corporate applications with full color display and easy installation.',
             '适用于室内商业和企业应用的高质量显示屏，具有全彩显示和易于安装的特点。',
             'Pixel Pitch: P1.25-P4\nBrightness: 800-1500 nits\nRefresh Rate: 1920-3840Hz\nColor Temperature: 3200K-9300K\nLifespan: 100,000 hours',
             'Full Color Display, Easy Installation, Low Maintenance',
             'assets/products/indoor-led.jpg', 'active'),
            
            ('Transparent LED Display', '透明LED显示屏', 'transparent',
             'Innovative transparent displays that blend seamlessly with architecture while delivering stunning visual impact.',
             '与建筑完美融合的创新透明显示屏，同时提供令人惊叹的视觉冲击。',
             'Transparency: 70-90%\nPixel Pitch: P3.91-P7.81\nBrightness: 4000-6000 nits\nWeight: 12kg/m²\nMaintenance: Front/Rear',
             '90% Transparency, Lightweight Design, Creative Applications',
             'assets/products/transparent-led.jpg', 'active'),
            
            ('Creative LED Display', '创意LED显示屏', 'creative',
             'Custom-shaped displays for unique architectural and artistic applications with flexible design options.',
             '适用于独特建筑和艺术应用的定制形状显示屏，具有灵活的设计选项。',
             'Shape: Customizable\nPixel Pitch: P1.25-P10\nCurve Radius: R≥500mm\nInstallation: Flexible\nControl: Professional',
             'Custom Shapes, Flexible Design, Artistic Integration',
             'assets/products/creative-led.jpg', 'active'),
            
            ('Rental LED Display', '租赁LED显示屏', 'rental',
             'Portable and quick-setup displays for events and temporary installations with lightweight and durable design.',
             '适用于活动和临时安装的便携式快速安装显示屏，具有轻量化和耐用的设计。',
             'Pixel Pitch: P2.6-P4.81\nWeight: 6-8kg/panel\nSetup Time: <30min\nConnection: Quick Lock\nFlight Case: Available',
             'Quick Setup, Lightweight, Durable Design',
             'assets/products/rental-led.jpg', 'active')
        ]
        
        for product in default_products:
            cursor.execute('''
                INSERT INTO products (
                    name_en, name_zh, category, description_en, description_zh,
                    specifications, features, images, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', product)
    
    # 插入默认设置
    default_settings = [
        ('site_title_en', 'Lianjin LED Display', 'English site title'),
        ('site_title_zh', '联锦LED显示屏', 'Chinese site title'),
        ('company_phone', '+86-755-1234-5678', 'Company phone number'),
        ('company_email', 'info@lianjinled.com', 'Company email'),
        ('company_address_en', 'Shenzhen, Guangdong Province, China', 'English address'),
        ('company_address_zh', '中国广东省深圳市', 'Chinese address')
    ]
    
    for key, value, desc in default_settings:
        cursor.execute('''
            INSERT OR IGNORE INTO settings (key, value, description)
            VALUES (?, ?, ?)
        ''', (key, value, desc))
    
    conn.commit()
    conn.close()

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 数据库连接函数
def get_db_connection():
    conn = sqlite3.connect('led_admin.db')
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
        'products': conn.execute('SELECT COUNT(*) FROM products WHERE status = "active"').fetchone()[0],
        'news': conn.execute('SELECT COUNT(*) FROM news WHERE status = "published"').fetchone()[0],
        'cases': conn.execute('SELECT COUNT(*) FROM cases WHERE status = "published"').fetchone()[0],
        'inquiries': conn.execute('SELECT COUNT(*) FROM inquiries WHERE status = "new"').fetchone()[0],
        'quotes': conn.execute('SELECT COUNT(*) FROM quotes WHERE status = "pending"').fetchone()[0]
    }
    
    # 获取最新询盘
    recent_inquiries = conn.execute('''
        SELECT * FROM inquiries 
        ORDER BY created_at DESC 
        LIMIT 5
    ''').fetchall()
    
    # 获取最新报价请求
    recent_quotes = conn.execute('''
        SELECT * FROM quotes 
        ORDER BY created_at DESC 
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_inquiries=recent_inquiries,
                         recent_quotes=recent_quotes)

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
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """管理员登出"""
    session.clear()
    flash('已成功登出！', 'info')
    return redirect(url_for('login'))

# 产品管理
@app.route('/products')
@login_required
def products():
    """产品列表"""
    conn = get_db_connection()
    products = conn.execute('''
        SELECT * FROM products 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('products.html', products=products)

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """添加产品"""
    if request.method == 'POST':
        data = request.form
        
        # 处理图片上传
        image_path = None
        if 'product_image' in request.files:
            file = request.files['product_image']
            if file.filename != '':
                image_path = process_uploaded_image(file, 'products')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (
                name_en, name_zh, category, description_en, description_zh,
                specifications, features, images, price, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name_en'], data['name_zh'], data['category'],
            data['description_en'], data['description_zh'],
            data['specifications'], data['features'],
            image_path or data.get('images', ''),
            float(data['price']) if data['price'] else None,
            data['status']
        ))
        
        # 获取新创建的产品ID
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        flash('产品添加成功！', 'success')
        return redirect(url_for('products'))
    
    return render_template('product_form.html', action='add')

@app.route('/products/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    """删除产品"""
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    flash('产品删除成功！', 'success')
    return redirect(url_for('products'))

# 询盘管理
@app.route('/inquiries')
@login_required
def inquiries():
    """询盘列表"""
    conn = get_db_connection()
    inquiries = conn.execute('''
        SELECT * FROM inquiries 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('inquiries.html', inquiries=inquiries)

@app.route('/inquiries/<int:id>/status', methods=['POST'])
@login_required
def update_inquiry_status(id):
    """更新询盘状态"""
    status = request.form.get('status')
    
    conn = get_db_connection()
    conn.execute('''
        UPDATE inquiries 
        SET status = ?, handled_by = ?, handled_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (status, session['admin_username'], id))
    conn.commit()
    conn.close()
    
    flash('询盘状态更新成功！', 'success')
    return redirect(url_for('inquiries'))

# 报价管理
@app.route('/quotes')
@login_required
def quotes():
    """报价请求列表"""
    conn = get_db_connection()
    quotes = conn.execute('''
        SELECT * FROM quotes 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('quotes.html', quotes=quotes)

@app.route('/quotes/<int:id>/status', methods=['POST'])
@login_required
def update_quote_status(id):
    """更新报价状态"""
    status = request.form.get('status')
    
    conn = get_db_connection()
    conn.execute('''
        UPDATE quotes 
        SET status = ?, handled_by = ?, handled_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (status, session['admin_username'], id))
    conn.commit()
    conn.close()
    
    flash('报价状态更新成功！', 'success')
    return redirect(url_for('quotes'))

# API接口 - 用于前端网站
@app.route('/api/contact', methods=['POST'])
def api_contact():
    """接收联系表单"""
    data = request.get_json()
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO inquiries (name, email, company, phone, product_interest, message)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name'), data.get('email'), data.get('company'),
        data.get('phone'), data.get('product'), data.get('message')
    ))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'message': 'Thank you for your inquiry!'})

@app.route('/api/products', methods=['GET'])
def api_products():
    """获取产品列表API - 供前端网站使用"""
    conn = get_db_connection()
    products = conn.execute('''
        SELECT * FROM products WHERE status = 'active'
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    products_list = []
    for product in products:
        products_list.append({
            'id': product['id'],
            'name_en': product['name_en'],
            'name_zh': product['name_zh'],
            'category': product['category'],
            'description_en': product['description_en'],
            'description_zh': product['description_zh'],
            'specifications': product['specifications'],
            'features': product['features'],
            'images': product['images'],
            'price': product['price']
        })
    
    response = jsonify({'status': 'success', 'products': products_list})
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED Display Website Admin Panel
基于Flask的后端管理系统
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
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
app.secret_key = 'led_admin_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['JSON_AS_ASCII'] = False  # Ensure UTF-8 for JSON responses

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/uploads/products', exist_ok=True)
os.makedirs('static/uploads/news', exist_ok=True)
os.makedirs('static/uploads/cases', exist_ok=True)

# 确保前端assets目录存在
frontend_assets = os.path.join('..', 'assets', 'products')
os.makedirs(frontend_assets, exist_ok=True)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_uploaded_image(file, category='products'):
    """处理上传的图片"""
    if file and allowed_file(file.filename):
        # 生成唯一文件名
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        # 保存到admin静态目录
        admin_path = os.path.join(app.config['UPLOAD_FOLDER'], category, unique_filename)
        file.save(admin_path)
        
        # 同时复制到前端assets目录
        frontend_path = os.path.join('..', 'assets', category, unique_filename)
        
        # 使用PIL处理图片并保存到前端目录
        try:
            with Image.open(admin_path) as img:
                # 优化图片大小
                if img.width > 1200:
                    ratio = 1200 / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((1200, new_height), Image.Resampling.LANCZOS)
                
                # 保存到前端目录
                img.save(frontend_path, optimize=True, quality=85)
        except Exception as e:
            print(f"图片处理错误: {e}")
            # 如果处理失败，直接复制文件
            import shutil
            shutil.copy2(admin_path, frontend_path)
        
        return f"assets/{category}/{unique_filename}"
    return None

# 数据库初始化
def init_db():
    """初始化数据库"""
    conn = sqlite3.connect('led_admin.db')
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
    
    # 报价请求表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            company TEXT NOT NULL,
            product_type TEXT,
            display_size TEXT,
            quantity INTEGER,
            requirements TEXT,
            timeline TEXT,
            budget TEXT,
            status TEXT DEFAULT 'pending',
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
    
    # 创建默认管理员账户
    cursor.execute('SELECT COUNT(*) FROM admins')
    if cursor.fetchone()[0] == 0:
        default_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO admins (username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin', default_password, 'admin@lianjinled.com', 'super_admin'))
    
    # 插入前端网页已有的产品数据
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        default_products = [
            ('Fine Pitch LED Display', '小间距LED显示屏', 'fine-pitch', 
             'Ultra-high resolution displays with pixel pitches from P0.9 to P1.56, perfect for control rooms, broadcast studios, and corporate environments.',
             '像素间距从P0.9到P1.56的超高分辨率显示屏，完美适用于控制室、广播演播室和企业环境。',
             'Pixel Pitch: P0.9-P1.56\nResolution: 4K/8K\nBrightness: 600-1200 nits\nRefresh Rate: 3840Hz\nViewing Angle: 160°/160°',
             '4K/8K Resolution, Seamless Splicing, High Refresh Rate',
             'assets/products/fine-pitch-led.jpg', 'active'),
            
            ('Outdoor LED Display', '户外LED显示屏', 'outdoor',
             'Weather-resistant displays for outdoor advertising and information with high brightness and energy efficiency.',
             '适用于户外广告和信息显示的防风雨显示屏，具有高亮度和节能特性。',
             'Pixel Pitch: P3-P10\nBrightness: 5000-8000 nits\nIP Rating: IP65\nOperating Temperature: -40°C to +60°C\nViewing Distance: 3-100m',
             'IP65 Waterproof, High Brightness, Energy Efficient',
             'assets/products/outdoor-led.jpg', 'active'),
            
            ('Indoor LED Display', '室内LED显示屏', 'indoor',
             'High-quality displays for indoor commercial and corporate applications with full color display and easy installation.',
             '适用于室内商业和企业应用的高质量显示屏，具有全彩显示和易于安装的特点。',
             'Pixel Pitch: P1.25-P4\nBrightness: 800-1500 nits\nRefresh Rate: 1920-3840Hz\nColor Temperature: 3200K-9300K\nLifespan: 100,000 hours',
             'Full Color Display, Easy Installation, Low Maintenance',
             'assets/products/indoor-led.jpg', 'active'),
            
            ('Transparent LED Display', '透明LED显示屏', 'transparent',
             'Innovative transparent displays that blend seamlessly with architecture while delivering stunning visual impact.',
             '与建筑完美融合的创新透明显示屏，同时提供令人惊叹的视觉冲击。',
             'Transparency: 70-90%\nPixel Pitch: P3.91-P7.81\nBrightness: 4000-6000 nits\nWeight: 12kg/m²\nMaintenance: Front/Rear',
             '90% Transparency, Lightweight Design, Creative Applications',
             'assets/products/transparent-led.jpg', 'active'),
            
            ('Creative LED Display', '创意LED显示屏', 'creative',
             'Custom-shaped displays for unique architectural and artistic applications with flexible design options.',
             '适用于独特建筑和艺术应用的定制形状显示屏，具有灵活的设计选项。',
             'Shape: Customizable\nPixel Pitch: P1.25-P10\nCurve Radius: R≥500mm\nInstallation: Flexible\nControl: Professional',
             'Custom Shapes, Flexible Design, Artistic Integration',
             'assets/products/creative-led.jpg', 'active'),
            
            ('Rental LED Display', '租赁LED显示屏', 'rental',
             'Portable and quick-setup displays for events and temporary installations with lightweight and durable design.',
             '适用于活动和临时安装的便携式快速安装显示屏，具有轻量化和耐用的设计。',
             'Pixel Pitch: P2.6-P4.81\nWeight: 6-8kg/panel\nSetup Time: <30min\nConnection: Quick Lock\nFlight Case: Available',
             'Quick Setup, Lightweight, Durable Design',
             'assets/products/rental-led.jpg', 'active')
        ]
        
        for product in default_products:
            cursor.execute('''
                INSERT INTO products (
                    name_en, name_zh, category, description_en, description_zh,
                    specifications, features, images, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', product)
    
    # 插入默认设置
    default_settings = [
        ('site_title_en', 'Lianjin LED Display', 'English site title'),
        ('site_title_zh', '联锦LED显示屏', 'Chinese site title'),
        ('company_phone', '+86-755-1234-5678', 'Company phone number'),
        ('company_email', 'info@lianjinled.com', 'Company email'),
        ('company_address_en', 'Shenzhen, Guangdong Province, China', 'English address'),
        ('company_address_zh', '中国广东省深圳市', 'Chinese address')
    ]
    
    for key, value, desc in default_settings:
        cursor.execute('''
            INSERT OR IGNORE INTO settings (key, value, description)
            VALUES (?, ?, ?)
        ''', (key, value, desc))
    
    conn.commit()
    conn.close()

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 数据库连接函数
def get_db_connection():
    conn = sqlite3.connect('led_admin.db')
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
        'products': conn.execute('SELECT COUNT(*) FROM products WHERE status = "active"').fetchone()[0],
        'news': conn.execute('SELECT COUNT(*) FROM news WHERE status = "published"').fetchone()[0],
        'cases': conn.execute('SELECT COUNT(*) FROM cases WHERE status = "published"').fetchone()[0],
        'inquiries': conn.execute('SELECT COUNT(*) FROM inquiries WHERE status = "new"').fetchone()[0],
        'quotes': conn.execute('SELECT COUNT(*) FROM quotes WHERE status = "pending"').fetchone()[0]
    }
    
    # 获取最新询盘
    recent_inquiries = conn.execute('''
        SELECT * FROM inquiries 
        ORDER BY created_at DESC 
        LIMIT 5
    ''').fetchall()
    
    # 获取最新报价请求
    recent_quotes = conn.execute('''
        SELECT * FROM quotes 
        ORDER BY created_at DESC 
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_inquiries=recent_inquiries,
                         recent_quotes=recent_quotes)

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
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """管理员登出"""
    session.clear()
    flash('已成功登出！', 'info')
    return redirect(url_for('login'))

# 产品管理
@app.route('/products')
@login_required
def products():
    """产品列表"""
    conn = get_db_connection()
    products = conn.execute('''
        SELECT * FROM products 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('products.html', products=products)

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """添加产品"""
    if request.method == 'POST':
        data = request.form
        
        # 处理图片上传
        image_path = None
        if 'product_image' in request.files:
            file = request.files['product_image']
            if file.filename != '':
                image_path = process_uploaded_image(file, 'products')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (
                name_en, name_zh, category, description_en, description_zh,
                specifications, features, images, price, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name_en'], data['name_zh'], data['category'],
            data['description_en'], data['description_zh'],
            data['specifications'], data['features'],
            image_path or data.get('images', ''),
            float(data['price']) if data['price'] else None,
            data['status']
        ))
        
        # 获取新创建的产品ID
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        flash('产品添加成功！', 'success')
        return redirect(url_for('products'))
    
    return render_template('product_form.html', action='add')

@app.route('/products/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    """删除产品"""
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    flash('产品删除成功！', 'success')
    return redirect(url_for('products'))

# 询盘管理
@app.route('/inquiries')
@login_required
def inquiries():
    """询盘列表"""
    conn = get_db_connection()
    inquiries = conn.execute('''
        SELECT * FROM inquiries 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('inquiries.html', inquiries=inquiries)

@app.route('/inquiries/<int:id>/status', methods=['POST'])
@login_required
def update_inquiry_status(id):
    """更新询盘状态"""
    status = request.form.get('status')
    
    conn = get_db_connection()
    conn.execute('''
        UPDATE inquiries 
        SET status = ?, handled_by = ?, handled_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (status, session['admin_username'], id))
    conn.commit()
    conn.close()
    
    flash('询盘状态更新成功！', 'success')
    return redirect(url_for('inquiries'))

# 报价管理
@app.route('/quotes')
@login_required
def quotes():
    """报价请求列表"""
    conn = get_db_connection()
    quotes = conn.execute('''
        SELECT * FROM quotes 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('quotes.html', quotes=quotes)

@app.route('/quotes/<int:id>/status', methods=['POST'])
@login_required
def update_quote_status(id):
    """更新报价状态"""
    status = request.form.get('status')
    
    conn = get_db_connection()
    conn.execute('''
        UPDATE quotes 
        SET status = ?, handled_by = ?, handled_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (status, session['admin_username'], id))
    conn.commit()
    conn.close()
    
    flash('报价状态更新成功！', 'success')
    return redirect(url_for('quotes'))

# API接口 - 用于前端网站
@app.route('/api/contact', methods=['POST'])
def api_contact():
    """接收联系表单"""
    data = request.get_json()
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO inquiries (name, email, company, phone, product_interest, message)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name'), data.get('email'), data.get('company'),
        data.get('phone'), data.get('product'), data.get('message')
    ))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'message': 'Thank you for your inquiry!'})

@app.route('/api/products', methods=['GET'])
def api_products():
    """获取产品列表API - 供前端网站使用"""
    conn = get_db_connection()
    products = conn.execute('''
        SELECT * FROM products WHERE status = 'active'
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    products_list = []
    for product in products:
        products_list.append({
            'id': product['id'],
            'name_en': product['name_en'],
            'name_zh': product['name_zh'],
            'category': product['category'],
            'description_en': product['description_en'],
            'description_zh': product['description_zh'],
            'specifications': product['specifications'],
            'features': product['features'],
            'images': product['images'],
            'price': product['price']
        })
    
    response = jsonify({'status': 'success', 'products': products_list})
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

# 注册API蓝图
try:
    from api import api_bp
    app.register_blueprint(api_bp)
except ImportError:
    print("Warning: API blueprint not found, continuing without it")

if __name__ == '__main__':
    init_db()
    print("🚀 LED Display Admin Panel Starting...")
    print("📍 Admin URL: http://localhost:5000")
    print("👤 Default Login: admin / admin123")
    print("🔗 API Endpoints: http://localhost:5000/api/")
    print("=" * 50)
    
    # CloudStudio compatible configuration
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True, use_reloader=False)
