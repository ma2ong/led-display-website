#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Flask-based LED Display Admin System
Full-featured admin panel with database management
"""

import os
import sys
import json
import sqlite3
import threading
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs

# Flask app configuration
app = Flask(__name__, 
           template_folder='admin/templates',
           static_folder='admin/static')
app.secret_key = 'led_display_admin_secret_key_2024'
CORS(app, origins=['*'], supports_credentials=True)

# Database configuration
DATABASE = 'admin/led_display.db'
UPLOAD_FOLDER = 'admin/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def init_database():
    """Initialize the database with all required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            specifications TEXT,
            price REAL,
            image_url TEXT,
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
            phone TEXT,
            company TEXT,
            subject TEXT,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Quotes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            company TEXT,
            product_type TEXT,
            quantity INTEGER,
            specifications TEXT,
            budget REAL,
            message TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # News table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            summary TEXT,
            image_url TEXT,
            status TEXT DEFAULT 'published',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Cases table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            client TEXT NOT NULL,
            industry TEXT,
            description TEXT NOT NULL,
            solution TEXT,
            results TEXT,
            image_url TEXT,
            status TEXT DEFAULT 'published',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create default admin user
    cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
    if cursor.fetchone()[0] == 0:
        password_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin', password_hash, 'admin@leddisplay.com', 'admin'))
    
    # Insert sample products
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ('Indoor P1.25 LED Display', 'indoor', 'Ultra-fine pitch indoor LED display for high-resolution applications', 'P1.25, 4K resolution, 500x500mm cabinet', 2500.00, '/assets/indoor-led.jpg'),
            ('Outdoor P6 LED Display', 'outdoor', 'Weather-resistant outdoor LED display for advertising', 'P6, IP65, 960x960mm cabinet', 1200.00, '/assets/outdoor-led.jpg'),
            ('Rental P3.91 LED Display', 'rental', 'Lightweight rental LED display for events', 'P3.91, 500x500mm, quick lock system', 800.00, '/assets/rental-led.jpg'),
            ('Transparent LED Display', 'transparent', 'See-through LED display for glass facades', '70% transparency, P7.8, lightweight', 3500.00, '/assets/transparent-led.jpg'),
            ('Creative Curved LED', 'creative', 'Flexible LED display for creative installations', 'Bendable, custom shapes, P2.5', 4000.00, '/assets/creative-led.jpg'),
            ('Industrial Control Room Display', 'industrial', '24/7 operation LED display for control rooms', 'P1.56, 24/7 operation, redundant backup', 5000.00, '/assets/industrial-led.jpg')
        ]
        
        for product in sample_products:
            cursor.execute('''
                INSERT INTO products (name, category, description, specifications, price, image_url)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', product)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

# Authentication decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Routes
@app.route('/admin')
@login_required
def dashboard():
    """Admin dashboard"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) FROM products WHERE status = "active"')
    active_products = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM inquiries WHERE status = "new"')
    new_inquiries = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM quotes WHERE status = "pending"')
    pending_quotes = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM news WHERE status = "published"')
    published_news = cursor.fetchone()[0]
    
    # Get recent activities
    cursor.execute('''
        SELECT 'inquiry' as type, name, created_at FROM inquiries 
        UNION ALL
        SELECT 'quote' as type, name, created_at FROM quotes
        ORDER BY created_at DESC LIMIT 10
    ''')
    recent_activities = cursor.fetchall()
    
    conn.close()
    
    stats = {
        'active_products': active_products,
        'new_inquiries': new_inquiries,
        'pending_quotes': pending_quotes,
        'published_news': published_news
    }
    
    return render_template('dashboard.html', stats=stats, activities=recent_activities)

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/admin/logout')
def logout():
    """Admin logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/admin/products')
@login_required
def products():
    """Product management"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
    products = cursor.fetchall()
    conn.close()
    return render_template('products.html', products=products)

@app.route('/admin/inquiries')
@login_required
def inquiries():
    """Inquiry management"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inquiries ORDER BY created_at DESC')
    inquiries = cursor.fetchall()
    conn.close()
    return render_template('inquiries.html', inquiries=inquiries)

@app.route('/admin/quotes')
@login_required
def quotes():
    """Quote management"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM quotes ORDER BY created_at DESC')
    quotes = cursor.fetchall()
    conn.close()
    return render_template('quotes.html', quotes=quotes)

@app.route('/admin/news')
@login_required
def news():
    """News management"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM news ORDER BY created_at DESC')
    news = cursor.fetchall()
    conn.close()
    return render_template('news.html', news=news)

@app.route('/admin/cases')
@login_required
def cases():
    """Case studies management"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cases ORDER BY created_at DESC')
    cases = cursor.fetchall()
    conn.close()
    return render_template('cases.html', cases=cases)

# API Routes
@app.route('/api/status')
def api_status():
    """API status check"""
    return jsonify({
        'status': 'active',
        'message': 'LED Display API is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/products')
def api_products():
    """Get all active products"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE status = "active"')
    products = cursor.fetchall()
    conn.close()
    
    product_list = []
    for product in products:
        product_list.append({
            'id': product[0],
            'name': product[1],
            'category': product[2],
            'description': product[3],
            'specifications': product[4],
            'price': product[5],
            'image_url': product[6]
        })
    
    return jsonify({'products': product_list})

@app.route('/api/contact', methods=['POST'])
def api_contact():
    """Handle contact form submissions"""
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO inquiries (name, email, phone, company, subject, message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.get('name'),
            data.get('email'),
            data.get('phone', ''),
            data.get('company', ''),
            data.get('subject', 'Website Contact'),
            data.get('message')
        ))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Contact form submitted successfully!'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quote', methods=['POST'])
def api_quote():
    """Handle quote request submissions"""
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        required_fields = ['name', 'email', 'product_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO quotes (name, email, phone, company, product_type, quantity, specifications, budget, message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('name'),
            data.get('email'),
            data.get('phone', ''),
            data.get('company', ''),
            data.get('product_type'),
            data.get('quantity', 1),
            data.get('specifications', ''),
            data.get('budget', 0),
            data.get('message', '')
        ))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Quote request submitted successfully!'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Static file serving for frontend
@app.route('/')
def index():
    """Serve the main website"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

def create_upload_folder():
    """Create upload folder if it doesn't exist"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

def main():
    """Main function to start the complete admin server"""
    print("🚀 Starting Complete LED Display Admin System")
    print("="*50)
    
    # Create necessary directories
    os.makedirs('admin', exist_ok=True)
    create_upload_folder()
    
    # Initialize database
    init_database()
    
    print("✅ Complete Flask admin system ready")
    print("📊 Admin Panel: http://localhost:8080/admin")
    print("🔐 Login: admin / admin123")
    print("🌐 Website: http://localhost:8080/")
    print("📡 API Status: http://localhost:8080/api/status")
    
    # Start Flask app
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)

if __name__ == '__main__':
    main()