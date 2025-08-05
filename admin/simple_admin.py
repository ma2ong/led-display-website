#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple and stable admin system for LED website
Rollback to a working version without complex features
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'led_admin_secret_key_2024'

# Database configuration
DATABASE = 'led_website.db'

def init_database():
    """Initialize the database with basic tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            price REAL,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create inquiries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            company TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create news table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            author TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create admin users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default admin user if not exists
    cursor.execute('SELECT COUNT(*) FROM admin_users WHERE username = ?', ('admin',))
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO admin_users (username, password) VALUES (?, ?)', 
                      ('admin', 'admin123'))
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM admin_users WHERE username = ? AND password = ?',
                           (username, password)).fetchone()
        conn.close()
        
        if user:
            session['logged_in'] = True
            session['username'] = username
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
        <title>LED网站管理系统 - 登录</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card mt-5">
                        <div class="card-header">
                            <h3 class="text-center">LED网站管理系统</h3>
                        </div>
                        <div class="card-body">
                            {% with messages = get_flashed_messages(with_categories=true) %}
                                {% if messages %}
                                    {% for category, message in messages %}
                                        <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }}">
                                            {{ message }}
                                        </div>
                                    {% endfor %}
                                {% endif %}
                            {% endwith %}
                            
                            <form method="POST">
                                <div class="mb-3">
                                    <label for="username" class="form-label">用户名</label>
                                    <input type="text" class="form-control" id="username" name="username" required>
                                </div>
                                <div class="mb-3">
                                    <label for="password" class="form-label">密码</label>
                                    <input type="password" class="form-control" id="password" name="password" required>
                                </div>
                                <button type="submit" class="btn btn-primary w-100">登录</button>
                            </form>
                            
                            <div class="mt-3 text-center">
                                <small class="text-muted">
                                    默认账号: admin / admin123
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    """Admin logout"""
    session.clear()
    flash('已成功退出登录！', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    """Admin dashboard"""
    conn = get_db_connection()
    
    # Get statistics
    product_count = conn.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    inquiry_count = conn.execute('SELECT COUNT(*) FROM inquiries').fetchone()[0]
    news_count = conn.execute('SELECT COUNT(*) FROM news').fetchone()[0]
    
    # Get recent inquiries
    recent_inquiries = conn.execute(
        'SELECT * FROM inquiries ORDER BY created_at DESC LIMIT 5'
    ).fetchall()
    
    conn.close()
    
    return f'''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LED网站管理系统 - 仪表板</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container-fluid">
                <a class="navbar-brand" href="/">LED管理系统</a>
                <div class="navbar-nav ms-auto">
                    <span class="navbar-text me-3">欢迎, {session.get('username', 'Admin')}</span>
                    <a class="nav-link" href="{url_for('logout')}">退出</a>
                </div>
            </div>
        </nav>
        
        <div class="container-fluid">
            <div class="row">
                <nav class="col-md-3 col-lg-2 d-md-block bg-light sidebar">
                    <div class="position-sticky pt-3">
                        <ul class="nav flex-column">
                            <li class="nav-item">
                                <a class="nav-link active" href="/">
                                    <i class="fas fa-tachometer-alt"></i> 仪表板
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="{url_for('products')}">
                                    <i class="fas fa-box"></i> 产品管理
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="{url_for('inquiries')}">
                                    <i class="fas fa-envelope"></i> 客户询盘
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="{url_for('news')}">
                                    <i class="fas fa-newspaper"></i> 新闻管理
                                </a>
                            </li>
                        </ul>
                    </div>
                </nav>
                
                <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4">
                    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                        <h1 class="h2">仪表板</h1>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-4">
                            <div class="card text-white bg-primary mb-3">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between">
                                        <div>
                                            <h4>{product_count}</h4>
                                            <p>产品总数</p>
                                        </div>
                                        <div>
                                            <i class="fas fa-box fa-2x"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-4">
                            <div class="card text-white bg-success mb-3">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between">
                                        <div>
                                            <h4>{inquiry_count}</h4>
                                            <p>客户询盘</p>
                                        </div>
                                        <div>
                                            <i class="fas fa-envelope fa-2x"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-4">
                            <div class="card text-white bg-info mb-3">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between">
                                        <div>
                                            <h4>{news_count}</h4>
                                            <p>新闻文章</p>
                                        </div>
                                        <div>
                                            <i class="fas fa-newspaper fa-2x"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-12">
                            <div class="card">
                                <div class="card-header">
                                    <h5>最新客户询盘</h5>
                                </div>
                                <div class="card-body">
                                    <div class="table-responsive">
                                        <table class="table table-striped">
                                            <thead>
                                                <tr>
                                                    <th>姓名</th>
                                                    <th>邮箱</th>
                                                    <th>公司</th>
                                                    <th>时间</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {''.join([f'<tr><td>{inquiry["name"]}</td><td>{inquiry["email"]}</td><td>{inquiry["company"] or "未填写"}</td><td>{inquiry["created_at"]}</td></tr>' for inquiry in recent_inquiries])}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''

@app.route('/products')
@login_required
def products():
    """Product management"""
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY created_at DESC').fetchall()
    conn.close()
    
    return f'''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>产品管理 - LED网站管理系统</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container-fluid">
                <a class="navbar-brand" href="/">LED管理系统</a>
                <div class="navbar-nav ms-auto">
                    <span class="navbar-text me-3">欢迎, {session.get('username', 'Admin')}</span>
                    <a class="nav-link" href="{url_for('logout')}">退出</a>
                </div>
            </div>
        </nav>
        
        <div class="container-fluid">
            <div class="row">
                <nav class="col-md-3 col-lg-2 d-md-block bg-light sidebar">
                    <div class="position-sticky pt-3">
                        <ul class="nav flex-column">
                            <li class="nav-item">
                                <a class="nav-link" href="/">
                                    <i class="fas fa-tachometer-alt"></i> 仪表板
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link active" href="{url_for('products')}">
                                    <i class="fas fa-box"></i> 产品管理
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="{url_for('inquiries')}">
                                    <i class="fas fa-envelope"></i> 客户询盘
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="{url_for('news')}">
                                    <i class="fas fa-newspaper"></i> 新闻管理
                                </a>
                            </li>
                        </ul>
                    </div>
                </nav>
                
                <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4">
                    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                        <h1 class="h2">产品管理</h1>
                        <button class="btn btn-primary" onclick="addProduct()">
                            <i class="fas fa-plus"></i> 添加产品
                        </button>
                    </div>
                    
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>产品名称</th>
                                    <th>分类</th>
                                    <th>价格</th>
                                    <th>创建时间</th>
                                    <th>操作</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([f'<tr><td>{product["id"]}</td><td>{product["name"]}</td><td>{product["category"]}</td><td>{product["price"] or "未设置"}</td><td>{product["created_at"]}</td><td><button class="btn btn-sm btn-warning me-1">编辑</button><button class="btn btn-sm btn-danger">删除</button></td></tr>' for product in products])}
                            </tbody>
                        </table>
                    </div>
                </main>
            </div>
        </div>
        
        <script>
            function addProduct() {{
                alert('添加产品功能开发中...');
            }}
        </script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''

@app.route('/inquiries')
@login_required
def inquiries():
    """Inquiry management"""
    conn = get_db_connection()
    inquiries = conn.execute('SELECT * FROM inquiries ORDER BY created_at DESC').fetchall()
    conn.close()
    
    return f'''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>客户询盘 - LED网站管理系统</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container-fluid">
                <a class="navbar-brand" href="/">LED管理系统</a>
                <div class="navbar-nav ms-auto">
                    <span class="navbar-text me-3">欢迎, {session.get('username', 'Admin')}</span>
                    <a class="nav-link" href="{url_for('logout')}">退出</a>
                </div>
            </div>
        </nav>
        
        <div class="container-fluid">
            <div class="row">
                <nav class="col-md-3 col-lg-2 d-md-block bg-light sidebar">
                    <div class="position-sticky pt-3">
                        <ul class="nav flex-column">
                            <li class="nav-item">
                                <a class="nav-link" href="/">
                                    <i class="fas fa-tachometer-alt"></i> 仪表板
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="{url_for('products')}">
                                    <i class="fas fa-box"></i> 产品管理
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link active" href="{url_for('inquiries')}">
                                    <i class="fas fa-envelope"></i> 客户询盘
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="{url_for('news')}">
                                    <i class="fas fa-newspaper"></i> 新闻管理
                                </a>
                            </li>
                        </ul>
                    </div>
                </nav>
                
                <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4">
                    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                        <h1 class="h2">客户询盘</h1>
                    </div>
                    
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>姓名</th>
                                    <th>邮箱</th>
                                    <th>电话</th>
                                    <th>公司</th>
                                    <th>询盘时间</th>
                                    <th>操作</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([f'<tr><td>{inquiry["id"]}</td><td>{inquiry["name"]}</td><td>{inquiry["email"]}</td><td>{inquiry["phone"] or "未填写"}</td><td>{inquiry["company"] or "未填写"}</td><td>{inquiry["created_at"]}</td><td><button class="btn btn-sm btn-info">查看详情</button></td></tr>' for inquiry in inquiries])}
                            </tbody>
                        </table>
                    </div>
                </main>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''

@app.route('/news')
@login_required
def news():
    """News management"""
    conn = get_db_connection()
    news_list = conn.execute('SELECT * FROM news ORDER BY created_at DESC').fetchall()
    conn.close()
    
    return f'''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>新闻管理 - LED网站管理系统</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container-fluid">
                <a class="navbar-brand" href="/">LED管理系统</a>
                <div class="navbar-nav ms-auto">
                    <span class="navbar-text me-3">欢迎, {session.get('username', 'Admin')}</span>
                    <a class="nav-link" href="{url_for('logout')}">退出</a>
                </div>
            </div>
        </nav>
        
        <div class="container-fluid">
            <div class="row">
                <nav class="col-md-3 col-lg-2 d-md-block bg-light sidebar">
                    <div class="position-sticky pt-3">
                        <ul class="nav flex-column">
                            <li class="nav-item">
                                <a class="nav-link" href="/">
                                    <i class="fas fa-tachometer-alt"></i> 仪表板
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="{url_for('products')}">
                                    <i class="fas fa-box"></i> 产品管理
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="{url_for('inquiries')}">
                                    <i class="fas fa-envelope"></i> 客户询盘
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link active" href="{url_for('news')}">
                                    <i class="fas fa-newspaper"></i> 新闻管理
                                </a>
                            </li>
                        </ul>
                    </div>
                </nav>
                
                <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4">
                    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                        <h1 class="h2">新闻管理</h1>
                        <button class="btn btn-primary" onclick="addNews()">
                            <i class="fas fa-plus"></i> 添加新闻
                        </button>
                    </div>
                    
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>标题</th>
                                    <th>作者</th>
                                    <th>发布时间</th>
                                    <th>操作</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([f'<tr><td>{news_item["id"]}</td><td>{news_item["title"]}</td><td>{news_item["author"] or "管理员"}</td><td>{news_item["created_at"]}</td><td><button class="btn btn-sm btn-warning me-1">编辑</button><button class="btn btn-sm btn-danger">删除</button></td></tr>' for news_item in news_list])}
                            </tbody>
                        </table>
                    </div>
                </main>
            </div>
        </div>
        
        <script>
            function addNews() {{
                alert('添加新闻功能开发中...');
            }}
        </script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''

# API endpoints for frontend integration
@app.route('/api/contact', methods=['POST'])
def api_contact():
    """Handle contact form submissions"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO inquiries (name, email, phone, company, message)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data.get('name'),
            data.get('email'),
            data.get('phone'),
            data.get('company'),
            data.get('message')
        ))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '询盘提交成功！'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'提交失败: {str(e)}'})

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    print("🚀 Simple LED Admin System Starting...")
    print("📍 Admin URL: http://localhost:5000")
    print("👤 Default Login: admin / admin123")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=False)