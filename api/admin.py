from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import os
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
CORS(app, supports_credentials=True)

# Database path for Vercel
DB_PATH = '/tmp/admin.db'

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create admins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create frontend_pages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frontend_pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_name TEXT UNIQUE NOT NULL,
            title TEXT,
            content TEXT,
            image_url TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price DECIMAL(10,2),
            image_url TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create inquiries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            message TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create news table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            image_url TEXT,
            published BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default admin user if not exists
    cursor.execute('SELECT COUNT(*) FROM admins WHERE username = ?', ('admin',))
    if cursor.fetchone()[0] == 0:
        hashed_password = generate_password_hash('admin123')
        cursor.execute('INSERT INTO admins (username, password) VALUES (?, ?)', 
                      ('admin', hashed_password))
    
    # Insert default frontend pages if not exists
    default_pages = [
        ('home', '首页', '欢迎来到LED显示屏专业制造商', '/images/hero-bg.jpg'),
        ('about', '关于我们', '我们是专业的LED显示屏制造商', '/images/about-bg.jpg'),
        ('products', '产品中心', '高质量LED显示屏产品', '/images/products-bg.jpg'),
        ('contact', '联系我们', '联系我们获取更多信息', '/images/contact-bg.jpg')
    ]
    
    for page_name, title, content, image_url in default_pages:
        cursor.execute('SELECT COUNT(*) FROM frontend_pages WHERE page_name = ?', (page_name,))
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO frontend_pages (page_name, title, content, image_url) 
                VALUES (?, ?, ?, ?)
            ''', (page_name, title, content, image_url))
    
    conn.commit()
    conn.close()

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'})
        
        # Initialize database
        init_db()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, password FROM admins WHERE username = ?', (username,))
        admin = cursor.fetchone()
        conn.close()
        
        if admin and check_password_hash(admin[2], password):
            session['admin_id'] = admin[0]
            session['admin_username'] = admin[1]
            return jsonify({'success': True, 'message': '登录成功'})
        else:
            return jsonify({'success': False, 'message': '用户名或密码错误'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'登录失败: {str(e)}'})

@app.route('/api/admin/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard statistics"""
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute('SELECT COUNT(*) FROM products')
        products_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM inquiries')
        inquiries_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM news')
        news_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM frontend_pages')
        pages_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'products_count': products_count,
                'inquiries_count': inquiries_count,
                'news_count': news_count,
                'pages_count': pages_count
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取数据失败: {str(e)}'})

@app.route('/api/admin/frontend/<page_name>', methods=['GET'])
def get_frontend_page(page_name):
    """Get frontend page content"""
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM frontend_pages WHERE page_name = ?', (page_name,))
        page = cursor.fetchone()
        conn.close()
        
        if page:
            return jsonify({
                'success': True,
                'data': {
                    'id': page[0],
                    'page_name': page[1],
                    'title': page[2],
                    'content': page[3],
                    'image_url': page[4],
                    'updated_at': page[5]
                }
            })
        else:
            return jsonify({'success': False, 'message': '页面不存在'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取页面失败: {str(e)}'})

@app.route('/api/admin/frontend/<page_name>', methods=['POST'])
def update_frontend_page(page_name):
    """Update frontend page content"""
    try:
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        image_url = data.get('image_url')
        
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE frontend_pages 
            SET title = ?, content = ?, image_url = ?, updated_at = CURRENT_TIMESTAMP
            WHERE page_name = ?
        ''', (title, content, image_url, page_name))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '页面更新成功'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新页面失败: {str(e)}'})

@app.route('/api/admin/products', methods=['GET'])
def get_products():
    """Get all products"""
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
        products = cursor.fetchall()
        conn.close()
        
        products_list = []
        for product in products:
            products_list.append({
                'id': product[0],
                'name': product[1],
                'description': product[2],
                'price': product[3],
                'image_url': product[4],
                'category': product[5],
                'created_at': product[6]
            })
        
        return jsonify({'success': True, 'data': products_list})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取产品失败: {str(e)}'})

@app.route('/api/admin/inquiries', methods=['GET'])
def get_inquiries():
    """Get all inquiries"""
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM inquiries ORDER BY created_at DESC')
        inquiries = cursor.fetchall()
        conn.close()
        
        inquiries_list = []
        for inquiry in inquiries:
            inquiries_list.append({
                'id': inquiry[0],
                'name': inquiry[1],
                'email': inquiry[2],
                'phone': inquiry[3],
                'message': inquiry[4],
                'status': inquiry[5],
                'created_at': inquiry[6]
            })
        
        return jsonify({'success': True, 'data': inquiries_list})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取咨询失败: {str(e)}'})

@app.route('/api/admin/news', methods=['GET'])
def get_news():
    """Get all news"""
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM news ORDER BY created_at DESC')
        news = cursor.fetchall()
        conn.close()
        
        news_list = []
        for item in news:
            news_list.append({
                'id': item[0],
                'title': item[1],
                'content': item[2],
                'image_url': item[3],
                'published': item[4],
                'created_at': item[5]
            })
        
        return jsonify({'success': True, 'data': news_list})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取新闻失败: {str(e)}'})

# Vercel serverless function handler
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)