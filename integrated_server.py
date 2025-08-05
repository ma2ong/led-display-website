#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrated Server for LED Display Website
Combines frontend static files and backend API in one server
"""

import os
import sys
import sqlite3
import json
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
import uuid

app = Flask(__name__, static_folder='.', template_folder='admin/templates')
app.secret_key = 'led_admin_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'assets'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['JSON_AS_ASCII'] = False

# Enable CORS
CORS(app, origins=['*'], supports_credentials=True)

# Ensure directories exist
os.makedirs('assets/products', exist_ok=True)
os.makedirs('assets/uploads', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def init_db():
    """Initialize database"""
    conn = sqlite3.connect('led_admin.db')
    cursor = conn.cursor()
    
    # Admin table
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
    
    # Products table
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
    
    # Inquiries table
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
    
    # Quotes table
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
    
    # Create default admin
    cursor.execute('SELECT COUNT(*) FROM admins')
    if cursor.fetchone()[0] == 0:
        default_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO admins (username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin', default_password, 'admin@lianjinled.com', 'super_admin'))
    
    # Insert sample products
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ('Fine Pitch LED Display', '小间距LED显示屏', 'fine-pitch', 
             'Ultra-high resolution displays perfect for control rooms and corporate environments.',
             '超高分辨率显示屏，完美适用于控制室和企业环境。',
             'Pixel Pitch: P0.9-P1.56, Resolution: 4K/8K, Brightness: 600-1200 nits',
             '4K/8K Resolution, Seamless Splicing, High Refresh Rate',
             'assets/products/fine-pitch-led.jpg', 'active'),
            
            ('Outdoor LED Display', '户外LED显示屏', 'outdoor',
             'Weather-resistant displays for outdoor advertising with high brightness.',
             '适用于户外广告的防风雨显示屏，具有高亮度特性。',
             'Pixel Pitch: P3-P10, Brightness: 5000-8000 nits, IP Rating: IP65',
             'IP65 Waterproof, High Brightness, Energy Efficient',
             'assets/products/outdoor-led.jpg', 'active'),
            
            ('Rental LED Display', '租赁LED显示屏', 'rental',
             'Portable displays for events with quick setup capabilities.',
             '适用于活动的便携式显示屏，具有快速安装能力。',
             'Pixel Pitch: P2.6-P4.81, Weight: 6-8kg/panel, Setup Time: <30min',
             'Quick Setup, Lightweight, Durable Design',
             'assets/products/rental-led.jpg', 'active')
        ]
        
        for product in sample_products:
            cursor.execute('''
                INSERT INTO products (
                    name_en, name_zh, category, description_en, description_zh,
                    specifications, features, images, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', product)
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('led_admin.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Frontend routes - serve static files
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    # Handle HTML files
    if filename.endswith('.html'):
        return send_from_directory('.', filename)
    # Handle CSS files
    elif filename.startswith('css/'):
        return send_from_directory('.', filename)
    # Handle JS files
    elif filename.startswith('js/'):
        return send_from_directory('.', filename)
    # Handle assets
    elif filename.startswith('assets/'):
        return send_from_directory('.', filename)
    # Default
    else:
        return send_from_directory('.', filename)

# Admin routes
@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    conn = get_db_connection()
    
    stats = {
        'products': conn.execute('SELECT COUNT(*) FROM products WHERE status = "active"').fetchone()[0],
        'inquiries': conn.execute('SELECT COUNT(*) FROM inquiries WHERE status = "new"').fetchone()[0],
        'quotes': conn.execute('SELECT COUNT(*) FROM quotes WHERE status = "pending"').fetchone()[0]
    }
    
    recent_inquiries = conn.execute('''
        SELECT * FROM inquiries ORDER BY created_at DESC LIMIT 5
    ''').fetchall()
    
    recent_quotes = conn.execute('''
        SELECT * FROM quotes ORDER BY created_at DESC LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_inquiries=recent_inquiries,
                         recent_quotes=recent_quotes)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
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
            
            flash('登录成功！', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('用户名或密码错误！', 'error')
    
    return render_template('login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.clear()
    flash('已成功登出！', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/products')
@login_required
def admin_products():
    """Product management"""
    conn = get_db_connection()
    products = conn.execute('''
        SELECT * FROM products ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('products.html', products=products)

@app.route('/admin/inquiries')
@login_required
def admin_inquiries():
    """Inquiry management"""
    conn = get_db_connection()
    inquiries = conn.execute('''
        SELECT * FROM inquiries ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('inquiries.html', inquiries=inquiries)

@app.route('/admin/quotes')
@login_required
def admin_quotes():
    """Quote management"""
    conn = get_db_connection()
    quotes = conn.execute('''
        SELECT * FROM quotes ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('quotes.html', quotes=quotes)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    """Add new product"""
    if request.method == 'POST':
        try:
            name_en = request.form['name_en']
            name_zh = request.form['name_zh']
            category = request.form['category']
            description_en = request.form['description_en']
            description_zh = request.form['description_zh']
            specifications = request.form['specifications']
            features = request.form['features']
            price = request.form.get('price')
            status = request.form.get('status', 'active')
            
            # Handle image upload
            image_path = 'assets/products/default.jpg'
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"{uuid.uuid4()}_{filename}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'products', filename)
                    file.save(file_path)
                    image_path = f"assets/products/{filename}"
            
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO products (
                    name_en, name_zh, category, description_en, description_zh,
                    specifications, features, images, price, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name_en, name_zh, category, description_en, description_zh,
                  specifications, features, image_path, price, status))
            conn.commit()
            conn.close()
            
            flash('Product added successfully!', 'success')
            return redirect(url_for('admin_products'))
            
        except Exception as e:
            flash(f'Error adding product: {str(e)}', 'error')
    
    return render_template('product_form.html', product=None, action='add')

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_product(product_id):
    """Edit existing product"""
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    
    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('admin_products'))
    
    if request.method == 'POST':
        try:
            name_en = request.form['name_en']
            name_zh = request.form['name_zh']
            category = request.form['category']
            description_en = request.form['description_en']
            description_zh = request.form['description_zh']
            specifications = request.form['specifications']
            features = request.form['features']
            price = request.form.get('price')
            status = request.form.get('status', 'active')
            
            # Handle image upload
            image_path = product['images']
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"{uuid.uuid4()}_{filename}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'products', filename)
                    file.save(file_path)
                    image_path = f"assets/products/{filename}"
            
            conn.execute('''
                UPDATE products SET
                    name_en = ?, name_zh = ?, category = ?, description_en = ?, description_zh = ?,
                    specifications = ?, features = ?, images = ?, price = ?, status = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (name_en, name_zh, category, description_en, description_zh,
                  specifications, features, image_path, price, status, product_id))
            conn.commit()
            conn.close()
            
            flash('Product updated successfully!', 'success')
            return redirect(url_for('admin_products'))
            
        except Exception as e:
            flash(f'Error updating product: {str(e)}', 'error')
    
    conn.close()
    return render_template('product_form.html', product=product, action='edit')

@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@login_required
def admin_delete_product(product_id):
    """Delete product"""
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
        conn.commit()
        conn.close()
        
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting product: {str(e)}', 'error')
    
    return redirect(url_for('admin_products'))

@app.route('/admin/settings')
@login_required
def admin_settings():
    """System settings"""
    conn = get_db_connection()
    
    # Get current admin info
    admin = conn.execute(
        'SELECT * FROM admins WHERE id = ?', (session['admin_id'],)
    ).fetchone()
    
    # Get system statistics
    stats = {
        'total_products': conn.execute('SELECT COUNT(*) FROM products').fetchone()[0],
        'active_products': conn.execute('SELECT COUNT(*) FROM products WHERE status = "active"').fetchone()[0],
        'total_inquiries': conn.execute('SELECT COUNT(*) FROM inquiries').fetchone()[0],
        'new_inquiries': conn.execute('SELECT COUNT(*) FROM inquiries WHERE status = "new"').fetchone()[0],
        'total_quotes': conn.execute('SELECT COUNT(*) FROM quotes').fetchone()[0],
        'pending_quotes': conn.execute('SELECT COUNT(*) FROM quotes WHERE status = "pending"').fetchone()[0],
        'total_admins': conn.execute('SELECT COUNT(*) FROM admins').fetchone()[0]
    }
    
    conn.close()
    
    return render_template('settings.html', admin=admin, stats=stats)

@app.route('/admin/users')
@login_required
def admin_users():
    """User management"""
    conn = get_db_connection()
    
    # Get all admin users
    users = conn.execute('''
        SELECT id, username, email, role, created_at, last_login
        FROM admins ORDER BY created_at DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('users.html', users=users)

@app.route('/admin/statistics')
@login_required
def admin_statistics():
    """Data statistics"""
    conn = get_db_connection()
    
    # Get comprehensive statistics
    stats = {
        'products': {
            'total': conn.execute('SELECT COUNT(*) FROM products').fetchone()[0],
            'active': conn.execute('SELECT COUNT(*) FROM products WHERE status = "active"').fetchone()[0],
            'inactive': conn.execute('SELECT COUNT(*) FROM products WHERE status = "inactive"').fetchone()[0],
            'by_category': {}
        },
        'inquiries': {
            'total': conn.execute('SELECT COUNT(*) FROM inquiries').fetchone()[0],
            'new': conn.execute('SELECT COUNT(*) FROM inquiries WHERE status = "new"').fetchone()[0],
            'processed': conn.execute('SELECT COUNT(*) FROM inquiries WHERE status = "processed"').fetchone()[0],
            'recent': conn.execute('SELECT COUNT(*) FROM inquiries WHERE date(created_at) >= date("now", "-7 days")').fetchone()[0]
        },
        'quotes': {
            'total': conn.execute('SELECT COUNT(*) FROM quotes').fetchone()[0],
            'pending': conn.execute('SELECT COUNT(*) FROM quotes WHERE status = "pending"').fetchone()[0],
            'approved': conn.execute('SELECT COUNT(*) FROM quotes WHERE status = "approved"').fetchone()[0],
            'rejected': conn.execute('SELECT COUNT(*) FROM quotes WHERE status = "rejected"').fetchone()[0],
            'recent': conn.execute('SELECT COUNT(*) FROM quotes WHERE date(created_at) >= date("now", "-7 days")').fetchone()[0]
        }
    }
    
    # Get product categories statistics
    categories = conn.execute('''
        SELECT category, COUNT(*) as count 
        FROM products 
        WHERE status = "active" 
        GROUP BY category
    ''').fetchall()
    
    for category in categories:
        stats['products']['by_category'][category['category']] = category['count']
    
    # Get recent activity
    recent_inquiries = conn.execute('''
        SELECT name, email, created_at FROM inquiries 
        ORDER BY created_at DESC LIMIT 10
    ''').fetchall()
    
    recent_quotes = conn.execute('''
        SELECT name, company, created_at FROM quotes 
        ORDER BY created_at DESC LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    return render_template('statistics.html', 
                         stats=stats, 
                         recent_inquiries=recent_inquiries,
                         recent_quotes=recent_quotes)

# API routes
@app.route('/api/contact', methods=['POST'])
def api_contact():
    """Contact form API"""
    try:
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
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/products/<category>')
def api_products_by_category(category):
    """Get products by category for frontend"""
    try:
        conn = get_db_connection()
        products = conn.execute('''
            SELECT * FROM products WHERE category = ? AND status = 'active'
            ORDER BY created_at DESC
        ''', (category,)).fetchall()
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
        
        return jsonify({'status': 'success', 'products': products_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/quote', methods=['POST'])
def api_quote():
    """Quote request API"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO quotes (name, email, company, product_type, display_size, 
                              quantity, requirements, timeline, budget)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('name'), data.get('email'), data.get('company'),
            data.get('product_type'), data.get('display_size'),
            data.get('quantity'), data.get('requirements'),
            data.get('timeline'), data.get('budget')
        ))
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'Quote request submitted successfully!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/products', methods=['GET'])
def api_products():
    """Products API"""
    try:
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
        
        return jsonify({'status': 'success', 'products': products_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/content')
def api_content():
    """Content API for frontend synchronization"""
    try:
        # Get website content data
        content = {
            'company': {
                'name': '联锦LED显示屏',
                'name_en': 'Lianjin LED Display',
                'description': '专业LED显示屏制造商，提供高品质的LED显示解决方案',
                'description_en': 'Professional LED display manufacturer providing high-quality LED display solutions',
                'address': '深圳市宝安区西乡街道LED产业园A栋',
                'phone': '+86 755 1234 5678',
                'email': 'info@lianjinled.com',
                'website': 'https://www.lianjinled.com'
            },
            'news': [
                {
                    'id': 1,
                    'title': '联锦LED荣获2024年度优秀LED显示屏企业奖',
                    'title_en': 'Lianjin LED Wins 2024 Outstanding LED Display Company Award',
                    'summary': '在2024年LED显示行业大会上，联锦LED凭借卓越的产品质量和创新技术荣获年度优秀企业奖。',
                    'date': '2024-01-15',
                    'category': 'company_news'
                },
                {
                    'id': 2,
                    'title': '新一代小间距LED显示屏P0.9正式发布',
                    'title_en': 'New Generation Fine Pitch LED Display P0.9 Officially Released',
                    'summary': '联锦LED最新推出的P0.9小间距LED显示屏，具有超高分辨率和出色的显示效果。',
                    'date': '2024-01-10',
                    'category': 'product_news'
                }
            ],
            'cases': [
                {
                    'id': 1,
                    'title': '深圳市政府大楼LED显示屏项目',
                    'title_en': 'Shenzhen Government Building LED Display Project',
                    'description': '为深圳市政府大楼提供了高品质的户外LED显示屏解决方案',
                    'category': 'government',
                    'location': '深圳',
                    'year': '2023',
                    'image': 'assets/cases/government-building.jpg'
                },
                {
                    'id': 2,
                    'title': '万达广场商业LED显示屏',
                    'title_en': 'Wanda Plaza Commercial LED Display',
                    'description': '为全国多个万达广场提供商业级LED显示屏系统',
                    'category': 'commercial',
                    'location': '全国',
                    'year': '2023',
                    'image': 'assets/cases/wanda-plaza.jpg'
                }
            ],
            'solutions': [
                {
                    'id': 1,
                    'title': '智慧城市显示解决方案',
                    'title_en': 'Smart City Display Solutions',
                    'description': '为智慧城市建设提供全方位的LED显示解决方案',
                    'category': 'smart_city',
                    'features': ['高清显示', '远程控制', '节能环保', '智能管理']
                },
                {
                    'id': 2,
                    'title': '商业广告显示解决方案',
                    'title_en': 'Commercial Advertising Display Solutions',
                    'description': '专为商业广告设计的高亮度、高对比度LED显示方案',
                    'category': 'commercial',
                    'features': ['高亮度', '防水防尘', '远程播控', '节能省电']
                }
            ]
        }
        
        return jsonify({'status': 'success', 'content': content})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/status')
def api_status():
    """API status check"""
    return jsonify({
        'status': 'success',
        'message': 'LED Display Website API is running',
        'timestamp': datetime.now().isoformat(),
        'endpoints': [
            '/api/contact - POST contact form',
            '/api/quote - POST quote request', 
            '/api/products - GET products list',
            '/api/content - GET website content',
            '/admin - Admin panel access'
        ]
    })

if __name__ == '__main__':
    print("🚀 LED Display Website - Integrated Server Starting...")
    print("=" * 60)
    
    # Initialize database
    init_db()
    print("✅ Database initialized")
    
    # Server info
    port = int(os.environ.get('PORT', 8080))
    print(f"🌐 Website: http://localhost:{port}")
    print(f"🔧 Admin Panel: http://localhost:{port}/admin")
    print(f"📡 API Status: http://localhost:{port}/api/status")
    print(f"👤 Admin Login: admin / admin123")
    print("=" * 60)
    
    # Start server
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)