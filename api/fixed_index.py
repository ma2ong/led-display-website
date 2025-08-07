from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import json
from datetime import datetime

# 创建Flask应用
app = Flask(__name__, 
           template_folder='../admin/templates',
           static_folder='../')
app.secret_key = 'your-secret-key-here-change-in-production'
CORS(app)

# 数据库路径函数
def get_database_path():
    """获取数据库路径，兼容Windows和Linux系统"""
    if os.name == 'nt':  # Windows系统
        return os.path.join(os.getcwd(), 'led_admin.db')
    else:  # Linux/Unix系统 (Vercel)
        return '/tmp/database.db'

def get_database_connection():
    """获取数据库连接"""
    db_path = get_database_path()
    return sqlite3.connect(db_path)

# 数据库初始化
def init_database():
    """初始化数据库"""
    db_path = get_database_path()
    
    # 确保目录存在
    os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
    
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建产品表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                price REAL,
                image_url TEXT,
                specifications TEXT,
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
                message TEXT,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建新闻表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                author TEXT,
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
        
        # 插入示例数据
        sample_products = [
            ('室内LED显示屏P2.5', 'indoor', '高清室内LED显示屏，适用于会议室、展厅等场所', 8500.00, '/assets/products/indoor-p2.5.jpg', '像素间距：2.5mm\n亮度：800cd/㎡\n刷新率：3840Hz'),
            ('户外LED显示屏P10', 'outdoor', '高亮度户外LED显示屏，防水防尘，适用于户外广告', 12000.00, '/assets/products/outdoor-p10.jpg', '像素间距：10mm\n亮度：6500cd/㎡\n防护等级：IP65'),
            ('租赁LED显示屏P3.91', 'rental', '轻便租赁LED显示屏，快速安装，适用于舞台演出', 9800.00, '/assets/products/rental-p3.91.jpg', '像素间距：3.91mm\n重量：6.5kg/㎡\n安装：快锁设计'),
            ('创意LED显示屏', 'creative', '异形创意LED显示屏，可定制各种造型', 15000.00, '/assets/products/creative-led.jpg', '可定制形状\n高刷新率\n无缝拼接')
        ]
        
        cursor.executemany('''
            INSERT INTO products (name, category, description, price, image_url, specifications)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_products)
        
        # 插入管理员用户
        cursor.execute('''
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        ''', ('admin', 'admin123', 'admin'))
        
        conn.commit()
        conn.close()
        print(f"数据库初始化完成: {db_path}")

# 初始化数据库
init_database()

# 静态文件路由
@app.route('/')
def index():
    return send_from_directory('../', 'homepage.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('../', filename)

# API路由
@app.route('/api/products')
def api_products():
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    
    products_list = []
    for product in products:
        products_list.append({
            'id': product[0],
            'name': product[1],
            'category': product[2],
            'description': product[3],
            'price': product[4],
            'image_url': product[5],
            'specifications': product[6]
        })
    
    return jsonify(products_list)

@app.route('/api/contact', methods=['POST'])
def api_contact():
    data = request.get_json()
    
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO inquiries (name, email, phone, company, message)
        VALUES (?, ?, ?, ?, ?)
    ''', (data.get('name'), data.get('email'), data.get('phone'), 
          data.get('company'), data.get('message')))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'message': '询盘提交成功'})

# 管理员路由
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('chinese_login.html', error='用户名或密码错误')
    
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    
    return render_template('chinese_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    
    # 获取统计数据
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM products')
    products_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM inquiries WHERE status = "new"')
    pending_inquiries = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM news WHERE status = "published"')
    published_news = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users')
    active_users = cursor.fetchone()[0]
    
    conn.close()
    
    stats = {
        'products': products_count,
        'inquiries': pending_inquiries,
        'news': published_news,
        'users': active_users,
        'visits': 1234
    }
    
    return render_template('chinese_dashboard.html', stats=stats)

@app.route('/admin/products')
def admin_products():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
    products = cursor.fetchall()
    conn.close()
    
    return render_template('chinese_products.html', products=products)

@app.route('/admin/inquiries')
def admin_inquiries():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inquiries ORDER BY created_at DESC')
    inquiries = cursor.fetchall()
    conn.close()
    
    return render_template('chinese_inquiries.html', inquiries=inquiries)

@app.route('/admin/news')
def admin_news():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM news ORDER BY created_at DESC')
    news = cursor.fetchall()
    conn.close()
    
    return render_template('chinese_news.html', news=news)

@app.route('/admin/users')
def admin_users():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
    users = cursor.fetchall()
    conn.close()
    
    return render_template('chinese_users.html', users=users)

@app.route('/admin/frontend-pages')
def admin_frontend_pages():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    
    return render_template('admin_frontend_pages.html')

@app.route('/admin/settings')
def admin_settings():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    
    return render_template('chinese_settings.html')

@app.route('/admin/statistics')
def admin_statistics():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    
    return render_template('chinese_statistics.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect(url_for('admin'))
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import json
from datetime import datetime

# 创建Flask应用
app = Flask(__name__, 
           template_folder='../admin/templates',
           static_folder='../')
app.secret_key = 'your-secret-key-here-change-in-production'
CORS(app)

# 数据库路径函数
def get_database_path():
    """获取数据库路径，兼容Windows和Linux系统"""
    if os.name == 'nt':  # Windows系统
        return os.path.join(os.getcwd(), 'led_admin.db')
    else:  # Linux/Unix系统 (Vercel)
        return '/tmp/database.db'

def get_database_connection():
    """获取数据库连接"""
    db_path = get_database_path()
    return sqlite3.connect(db_path)

# 数据库初始化
def init_database():
    """初始化数据库"""
    db_path = get_database_path()
    
    # 确保目录存在
    os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
    
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建产品表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                price REAL,
                image_url TEXT,
                specifications TEXT,
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
                message TEXT,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建新闻表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                author TEXT,
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
        
        # 插入示例数据
        sample_products = [
            ('室内LED显示屏P2.5', 'indoor', '高清室内LED显示屏，适用于会议室、展厅等场所', 8500.00, '/assets/products/indoor-p2.5.jpg', '像素间距：2.5mm\n亮度：800cd/㎡\n刷新率：3840Hz'),
            ('户外LED显示屏P10', 'outdoor', '高亮度户外LED显示屏，防水防尘，适用于户外广告', 12000.00, '/assets/products/outdoor-p10.jpg', '像素间距：10mm\n亮度：6500cd/㎡\n防护等级：IP65'),
            ('租赁LED显示屏P3.91', 'rental', '轻便租赁LED显示屏，快速安装，适用于舞台演出', 9800.00, '/assets/products/rental-p3.91.jpg', '像素间距：3.91mm\n重量：6.5kg/㎡\n安装：快锁设计'),
            ('创意LED显示屏', 'creative', '异形创意LED显示屏，可定制各种造型', 15000.00, '/assets/products/creative-led.jpg', '可定制形状\n高刷新率\n无缝拼接')
        ]
        
        cursor.executemany('''
            INSERT INTO products (name, category, description, price, image_url, specifications)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_products)
        
        # 插入管理员用户
        cursor.execute('''
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        ''', ('admin', 'admin123', 'admin'))
        
        conn.commit()
        conn.close()
        print(f"数据库初始化完成: {db_path}")

# 初始化数据库
init_database()

# 静态文件路由
@app.route('/')
def index():
    return send_from_directory('../', 'homepage.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('../', filename)

# API路由
@app.route('/api/products')
def api_products():
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    
    products_list = []
    for product in products:
        products_list.append({
            'id': product[0],
            'name': product[1],
            'category': product[2],
            'description': product[3],
            'price': product[4],
            'image_url': product[5],
            'specifications': product[6]
        })
    
    return jsonify(products_list)

@app.route('/api/contact', methods=['POST'])
def api_contact():
    data = request.get_json()
    
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO inquiries (name, email, phone, company, message)
        VALUES (?, ?, ?, ?, ?)
    ''', (data.get('name'), data.get('email'), data.get('phone'), 
          data.get('company'), data.get('message')))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'message': '询盘提交成功'})

# 管理员路由
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('chinese_login.html', error='用户名或密码错误')
    
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    
    return render_template('chinese_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    
    # 获取统计数据
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM products')
    products_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM inquiries WHERE status = "new"')
    pending_inquiries = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM news WHERE status = "published"')
    published_news = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users')
    active_users = cursor.fetchone()[0]
    
    conn.close()
    
    stats = {
        'products': products_count,
        'inquiries': pending_inquiries,
        'news': published_news,
        'users': active_users,
        'visits': 1234
    }
    
    return render_template('chinese_dashboard.html', stats=stats)

@app.route('/admin/products')
def admin_products():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
    products = cursor.fetchall()
    conn.close()
    
    return render_template('chinese_products.html', products=products)

@app.route('/admin/inquiries')
def admin_inquiries():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inquiries ORDER BY created_at DESC')
    inquiries = cursor.fetchall()
    conn.close()
    
    return render_template('chinese_inquiries.html', inquiries=inquiries)

@app.route('/admin/news')
def admin_news():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM news ORDER BY created_at DESC')
    news = cursor.fetchall()
    conn.close()
    
    return render_template('chinese_news.html', news=news)

@app.route('/admin/users')
def admin_users():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
    users = cursor.fetchall()
    conn.close()
    
    return render_template('chinese_users.html', users=users)

@app.route('/admin/frontend-pages')
def admin_frontend_pages():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    
    return render_template('admin_frontend_pages.html')

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import json
from datetime import datetime

# 创建Flask应用
app = Flask(__name__, 
           template_folder='../admin/templates',
           static_folder='../')
app.secret_key = 'your-secret-key-here-change-in-production'
CORS(app)

# 数据库路径函数
def get_database_path():
    """获取数据库路径，兼容Windows和Linux系统"""
    if os.name == 'nt':  # Windows系统
        return os.path.join(os.getcwd(), 'led_admin.db')
    else:  # Linux/Unix系统 (Vercel)
        return '/tmp/database.db'

def get_database_connection():
    """获取数据库连接"""
    db_path = get_database_path()
    return sqlite3.connect(db_path)

# 数据库初始化
def init_database():
    """初始化数据库"""
    db_path = get_database_path()
    
    # 确保目录存在
    os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
    
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建产品表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                price REAL,
                image_url TEXT,
                specifications TEXT,
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
                message TEXT,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建新闻表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                author TEXT,
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
        
        # 插入示例数据
        sample_products = [
            ('室内LED显示屏P2.5', 'indoor', '高清室内LED显示屏，适用于会议室、展厅等场所', 8500.00, '/assets/products/indoor-p2.5.jpg', '像素间距：2.5mm\n亮度：800cd/㎡\n刷新率：3840Hz'),
            ('户外LED显示屏P10', 'outdoor', '高亮度户外LED显示屏，防水防尘，适用于户外广告', 12000.00, '/assets/products/outdoor-p10.jpg', '像素间距：10mm\n亮度：6500cd/㎡\n防护等级：IP65'),
            ('租赁LED显示屏P3.91', 'rental', '轻便租赁LED显示屏，快速安装，适用于舞台演出', 9800.00, '/assets/products/rental-p3.91.jpg', '像素间距：3.91mm\n重量：6.5kg/㎡\n安装：快锁设计'),
            ('创意LED显示屏', 'creative', '异形创意LED显示屏，可定制各种造型', 15000.00, '/assets/products/creative-led.jpg', '可定制形状\n高刷新率\n无缝拼接')
        ]
        
        cursor.executemany('''
            INSERT INTO products (name, category, description, price, image_url, specifications)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_products)
        
        # 插入管理员用户
        cursor.execute('''
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        ''', ('admin', 'admin123', 'admin'))
        
        conn.commit()
        conn.close()
        print(f"数据库初始化完成: {db_path}")

# 初始化数据库
init_database()

# 静态文件路由
@app.route('/')
def index():
    return send_from_directory('../', 'homepage.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('../', filename)

# API路由
@app.route('/api/products')
def api_products():
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    
    products_list = []
    for product in products:
        products_list.append({
            'id': product[0],
            'name': product[1],
            'category': product[2],
            'description': product[3],
            'price': product[4],
            'image_url': product[5],
            'specifications': product[6]
        })
    
    return jsonify(products_list)

@app.route('/api/contact', methods=['POST'])
def api_contact():
    data = request.get_json()
    
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO inquiries (name, email, phone, company, message)
        VALUES (?, ?, ?, ?, ?)
    ''', (data.get('name'), data.get('email'), data.get('phone'), 
          data.get('company'), data.get('message')))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'message': '询盘提交成功'})

# 管理员路由
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('chinese_login.html', error='用户名或密码错误')
    
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    
    return render_template('chinese_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    
    # 获取统计数据
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM products')
    products_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM inquiries WHERE status = "new"')
    pending_inquiries = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM news WHERE status = "published"')
    published_news = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users')
    active_users = cursor.fetchone()[0]
    
    conn.close()
    
    stats = {
        'products': products_count,
        'inquiries': pending_inquiries,
        'news': published_news,
        'users': active_users,
        'visits': 1234
    }
    
    return render_template('chinese_dashboard.html', stats=stats)

@app.route('/admin/products')
def admin_products():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
    products = cursor.fetchall()
    conn.close()
    
    return render_template('chinese_products.html', products=products)

@app.route('/admin/inquiries')
def admin_inquiries():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inquiries ORDER BY created_at DESC')
    inquiries = cursor.fetchall()
    conn.close()
    
    return render_template('chinese_inquiries.html', inquiries=inquiries)

@app.route('/admin/news')
def admin_news():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM news ORDER BY created_at DESC')
    news = cursor.fetchall()
    conn.close()
    
    return render_template('chinese_news.html', news=news)

@app.route('/admin/users')
def admin_users():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
    users = cursor.fetchall()
    conn.close()
    
    return render_template('chinese_users.html', users=users)

@app.route('/admin/frontend-pages')
def admin_frontend_pages():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    
    return render_template('admin_frontend_pages.html')

@app.route('/admin/settings')
def admin_settings():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin'))
    
    return render_template('chinese_settings.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect(url_for('admin'))

# 前后端联动API接口
@app.route('/api/content')
def api_content():
    """获取网站内容数据"""
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # 获取公司信息
        company_info = {
            'name': '联进LED显示屏',
            'description': '专业LED显示屏制造商，提供室内外LED显示屏解决方案',
            'address': '深圳市宝安区西乡街道',
            'phone': '+86-755-12345678',
            'email': 'info@lianjin-led.com'
        }
        
        # 获取最新新闻
        cursor.execute('SELECT * FROM news WHERE status = "published" ORDER BY created_at DESC LIMIT 6')
        news_data = cursor.fetchall()
        news_list = []
        for news in news_data:
            news_list.append({
                'id': news[0],
                'title': news[1],
                'content': news[2][:200] + '...' if len(news[2]) > 200 else news[2],
                'author': news[3],
                'created_at': news[5]
            })
        
        conn.close()
        
        content_data = {
            'company': company_info,
            'news': news_list,
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'content': content_data
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/health')
def api_health():
    """健康检查端点"""
    return jsonify({
        'status': 'success',
        'message': 'API is running',
        'timestamp': datetime.now().isoformat(),
        'database': get_database_path()
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)