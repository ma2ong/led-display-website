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
        data.get('name'), data.get('email'), data.get('company'),
        data.get('phone'), data.get('product'), data.get('message')
    ))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'message': 'Thank you for your inquiry!'})

if __name__ == '__main__':
    from database_init import init_enhanced_db
    init_enhanced_db()
    print("🚀 Enhanced LED Display Admin Panel Starting...")
    print("📍 Admin URL: http://localhost:5001")
    print("👤 Default Login: admin / admin123")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5001)