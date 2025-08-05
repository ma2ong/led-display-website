#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stable LED Website Admin System
Simple, reliable admin interface without complex dependencies
"""

from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify, flash
import sqlite3
import os
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = 'led_admin_secret_key_2024'

# Database setup
def init_db():
    conn = sqlite3.connect('led_website.db')
    cursor = conn.cursor()
    
    # Create tables
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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            author TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default admin user
    admin_password = hashlib.md5('admin123'.encode()).hexdigest()
    cursor.execute('''
        INSERT OR IGNORE INTO admin_users (username, password_hash) 
        VALUES (?, ?)
    ''', ('admin', admin_password))
    
    conn.commit()
    conn.close()

# Login template
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LED Admin Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .login-container { min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-card { background: white; border-radius: 15px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="col-md-4">
            <div class="login-card p-5">
                <div class="text-center mb-4">
                    <h2 class="text-primary">🔧 LED Admin</h2>
                    <p class="text-muted">Management System</p>
                </div>
                
                {% if error %}
                <div class="alert alert-danger">{{ error }}</div>
                {% endif %}
                
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label">Username</label>
                        <input type="text" class="form-control" name="username" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Password</label>
                        <input type="password" class="form-control" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Login</button>
                </form>
                
                <div class="text-center mt-3">
                    <small class="text-muted">Default: admin / admin123</small>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

# Dashboard template
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LED Admin Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .sidebar { background: #2c3e50; min-height: 100vh; }
        .sidebar a { color: #ecf0f1; text-decoration: none; padding: 15px 20px; display: block; }
        .sidebar a:hover { background: #34495e; color: white; }
        .sidebar a.active { background: #3498db; }
        .main-content { background: #f8f9fa; min-height: 100vh; }
        .stat-card { background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .stat-number { font-size: 2rem; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-2 sidebar">
                <div class="p-3">
                    <h4 class="text-white">🔧 LED Admin</h4>
                </div>
                <nav>
                    <a href="{{ url_for('dashboard') }}" class="active"><i class="fas fa-tachometer-alt"></i> Dashboard</a>
                    <a href="{{ url_for('products') }}"><i class="fas fa-box"></i> Products</a>
                    <a href="{{ url_for('inquiries') }}"><i class="fas fa-envelope"></i> Inquiries</a>
                    <a href="{{ url_for('news') }}"><i class="fas fa-newspaper"></i> News</a>
                    <a href="{{ url_for('logout') }}"><i class="fas fa-sign-out-alt"></i> Logout</a>
                </nav>
            </div>
            
            <!-- Main Content -->
            <div class="col-md-10 main-content">
                <div class="p-4">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h1>Dashboard</h1>
                        <span class="text-muted">Welcome, {{ session.username }}</span>
                    </div>
                    
                    <!-- Statistics Cards -->
                    <div class="row">
                        <div class="col-md-3">
                            <div class="stat-card text-center">
                                <i class="fas fa-box fa-2x text-primary mb-2"></i>
                                <div class="stat-number text-primary">{{ stats.products }}</div>
                                <div class="text-muted">Products</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card text-center">
                                <i class="fas fa-envelope fa-2x text-success mb-2"></i>
                                <div class="stat-number text-success">{{ stats.inquiries }}</div>
                                <div class="text-muted">Inquiries</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card text-center">
                                <i class="fas fa-newspaper fa-2x text-info mb-2"></i>
                                <div class="stat-number text-info">{{ stats.news }}</div>
                                <div class="text-muted">News Articles</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card text-center">
                                <i class="fas fa-calendar fa-2x text-warning mb-2"></i>
                                <div class="stat-number text-warning">{{ stats.today_inquiries }}</div>
                                <div class="text-muted">Today's Inquiries</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Recent Inquiries -->
                    <div class="row mt-4">
                        <div class="col-12">
                            <div class="stat-card">
                                <h5><i class="fas fa-envelope"></i> Recent Inquiries</h5>
                                <div class="table-responsive">
                                    <table class="table table-hover">
                                        <thead>
                                            <tr>
                                                <th>Name</th>
                                                <th>Email</th>
                                                <th>Company</th>
                                                <th>Message</th>
                                                <th>Date</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {% for inquiry in recent_inquiries %}
                                            <tr>
                                                <td>{{ inquiry.name }}</td>
                                                <td>{{ inquiry.email }}</td>
                                                <td>{{ inquiry.company or 'N/A' }}</td>
                                                <td>{{ inquiry.message[:50] }}...</td>
                                                <td>{{ inquiry.created_at }}</td>
                                            </tr>
                                            {% else %}
                                            <tr>
                                                <td colspan="5" class="text-center text-muted">No inquiries yet</td>
                                            </tr>
                                            {% endfor %}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

# Products template
PRODUCTS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Products - LED Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .sidebar { background: #2c3e50; min-height: 100vh; }
        .sidebar a { color: #ecf0f1; text-decoration: none; padding: 15px 20px; display: block; }
        .sidebar a:hover { background: #34495e; color: white; }
        .main-content { background: #f8f9fa; min-height: 100vh; }
        .content-card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-2 sidebar">
                <div class="p-3">
                    <h4 class="text-white">🔧 LED Admin</h4>
                </div>
                <nav>
                    <a href="{{ url_for('dashboard') }}"><i class="fas fa-tachometer-alt"></i> Dashboard</a>
                    <a href="{{ url_for('products') }}" class="active"><i class="fas fa-box"></i> Products</a>
                    <a href="{{ url_for('inquiries') }}"><i class="fas fa-envelope"></i> Inquiries</a>
                    <a href="{{ url_for('news') }}"><i class="fas fa-newspaper"></i> News</a>
                    <a href="{{ url_for('logout') }}"><i class="fas fa-sign-out-alt"></i> Logout</a>
                </nav>
            </div>
            
            <!-- Main Content -->
            <div class="col-md-10 main-content">
                <div class="p-4">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h1><i class="fas fa-box"></i> Products Management</h1>
                        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addProductModal">
                            <i class="fas fa-plus"></i> Add Product
                        </button>
                    </div>
                    
                    <div class="content-card">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Name</th>
                                        <th>Category</th>
                                        <th>Price</th>
                                        <th>Created</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for product in products %}
                                    <tr>
                                        <td>{{ product.id }}</td>
                                        <td>{{ product.name }}</td>
                                        <td><span class="badge bg-primary">{{ product.category }}</span></td>
                                        <td>${{ "%.2f"|format(product.price or 0) }}</td>
                                        <td>{{ product.created_at }}</td>
                                        <td>
                                            <button class="btn btn-sm btn-outline-primary">Edit</button>
                                            <button class="btn btn-sm btn-outline-danger">Delete</button>
                                        </td>
                                    </tr>
                                    {% else %}
                                    <tr>
                                        <td colspan="6" class="text-center text-muted">No products found</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# Inquiries template
INQUIRIES_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inquiries - LED Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .sidebar { background: #2c3e50; min-height: 100vh; }
        .sidebar a { color: #ecf0f1; text-decoration: none; padding: 15px 20px; display: block; }
        .sidebar a:hover { background: #34495e; color: white; }
        .main-content { background: #f8f9fa; min-height: 100vh; }
        .content-card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-2 sidebar">
                <div class="p-3">
                    <h4 class="text-white">🔧 LED Admin</h4>
                </div>
                <nav>
                    <a href="{{ url_for('dashboard') }}"><i class="fas fa-tachometer-alt"></i> Dashboard</a>
                    <a href="{{ url_for('products') }}"><i class="fas fa-box"></i> Products</a>
                    <a href="{{ url_for('inquiries') }}" class="active"><i class="fas fa-envelope"></i> Inquiries</a>
                    <a href="{{ url_for('news') }}"><i class="fas fa-newspaper"></i> News</a>
                    <a href="{{ url_for('logout') }}"><i class="fas fa-sign-out-alt"></i> Logout</a>
                </nav>
            </div>
            
            <!-- Main Content -->
            <div class="col-md-10 main-content">
                <div class="p-4">
                    <h1><i class="fas fa-envelope"></i> Customer Inquiries</h1>
                    
                    <div class="content-card mt-4">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Name</th>
                                        <th>Email</th>
                                        <th>Phone</th>
                                        <th>Company</th>
                                        <th>Message</th>
                                        <th>Date</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for inquiry in inquiries %}
                                    <tr>
                                        <td>{{ inquiry.id }}</td>
                                        <td>{{ inquiry.name }}</td>
                                        <td>{{ inquiry.email }}</td>
                                        <td>{{ inquiry.phone or 'N/A' }}</td>
                                        <td>{{ inquiry.company or 'N/A' }}</td>
                                        <td>{{ inquiry.message[:100] }}...</td>
                                        <td>{{ inquiry.created_at }}</td>
                                    </tr>
                                    {% else %}
                                    <tr>
                                        <td colspan="7" class="text-center text-muted">No inquiries found</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

# News template
NEWS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News - LED Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .sidebar { background: #2c3e50; min-height: 100vh; }
        .sidebar a { color: #ecf0f1; text-decoration: none; padding: 15px 20px; display: block; }
        .sidebar a:hover { background: #34495e; color: white; }
        .main-content { background: #f8f9fa; min-height: 100vh; }
        .content-card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-2 sidebar">
                <div class="p-3">
                    <h4 class="text-white">🔧 LED Admin</h4>
                </div>
                <nav>
                    <a href="{{ url_for('dashboard') }}"><i class="fas fa-tachometer-alt"></i> Dashboard</a>
                    <a href="{{ url_for('products') }}"><i class="fas fa-box"></i> Products</a>
                    <a href="{{ url_for('inquiries') }}"><i class="fas fa-envelope"></i> Inquiries</a>
                    <a href="{{ url_for('news') }}" class="active"><i class="fas fa-newspaper"></i> News</a>
                    <a href="{{ url_for('logout') }}"><i class="fas fa-sign-out-alt"></i> Logout</a>
                </nav>
            </div>
            
            <!-- Main Content -->
            <div class="col-md-10 main-content">
                <div class="p-4">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h1><i class="fas fa-newspaper"></i> News Management</h1>
                        <button class="btn btn-primary">
                            <i class="fas fa-plus"></i> Add News
                        </button>
                    </div>
                    
                    <div class="content-card">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Title</th>
                                        <th>Author</th>
                                        <th>Created</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for article in news %}
                                    <tr>
                                        <td>{{ article.id }}</td>
                                        <td>{{ article.title }}</td>
                                        <td>{{ article.author or 'Admin' }}</td>
                                        <td>{{ article.created_at }}</td>
                                        <td>
                                            <button class="btn btn-sm btn-outline-primary">Edit</button>
                                            <button class="btn btn-sm btn-outline-danger">Delete</button>
                                        </td>
                                    </tr>
                                    {% else %}
                                    <tr>
                                        <td colspan="5" class="text-center text-muted">No news articles found</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

# Routes
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        conn = sqlite3.connect('led_website.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, username FROM admin_users WHERE username = ? AND password_hash = ?', 
                      (username, password_hash))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error='Invalid username or password')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('led_website.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) as count FROM products')
    products_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM inquiries')
    inquiries_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM news')
    news_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM inquiries WHERE date(created_at) = date("now")')
    today_inquiries = cursor.fetchone()['count']
    
    # Get recent inquiries
    cursor.execute('SELECT * FROM inquiries ORDER BY created_at DESC LIMIT 5')
    recent_inquiries = cursor.fetchall()
    
    conn.close()
    
    stats = {
        'products': products_count,
        'inquiries': inquiries_count,
        'news': news_count,
        'today_inquiries': today_inquiries
    }
    
    return render_template_string(DASHBOARD_TEMPLATE, stats=stats, recent_inquiries=recent_inquiries)

@app.route('/products')
def products():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('led_website.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
    products = cursor.fetchall()
    conn.close()
    
    return render_template_string(PRODUCTS_TEMPLATE, products=products)

@app.route('/inquiries')
def inquiries():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('led_website.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inquiries ORDER BY created_at DESC')
    inquiries = cursor.fetchall()
    conn.close()
    
    return render_template_string(INQUIRIES_TEMPLATE, inquiries=inquiries)

@app.route('/news')
def news():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('led_website.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM news ORDER BY created_at DESC')
    news = cursor.fetchall()
    conn.close()
    
    return render_template_string(NEWS_TEMPLATE, news=news)

# API endpoint for contact form
@app.route('/api/contact', methods=['POST'])
def api_contact():
    try:
        data = request.get_json()
        
        conn = sqlite3.connect('led_website.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO inquiries (name, email, phone, company, message)
            VALUES (?, ?, ?, ?, ?)
        ''', (data.get('name'), data.get('email'), data.get('phone'), 
              data.get('company'), data.get('message')))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Inquiry submitted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    init_db()
    print("🚀 LED Admin System Starting...")
    print("📍 Admin URL: http://localhost:5000")
    print("👤 Default Login: admin / admin123")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)