from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import json
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database initialization
def init_db():
    conn = sqlite3.connect('admin_database.db')
    c = conn.cursor()
    
    # Enhanced content management table
    c.execute('''CREATE TABLE IF NOT EXISTS page_content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        page_name TEXT NOT NULL,
        section_name TEXT NOT NULL,
        content_type TEXT NOT NULL,
        content_data TEXT,
        image_url TEXT,
        video_url TEXT,
        parameters TEXT,
        sort_order INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Media management table
    c.execute('''CREATE TABLE IF NOT EXISTS media_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        original_name TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_size INTEGER,
        upload_path TEXT NOT NULL,
        page_name TEXT,
        section_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Enhanced products table
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        specifications TEXT,
        features TEXT,
        applications TEXT,
        images TEXT,
        videos TEXT,
        brochure_url TEXT,
        price_range TEXT,
        is_featured BOOLEAN DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        sort_order INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # News and articles table
    c.execute('''CREATE TABLE IF NOT EXISTS news_articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        subtitle TEXT,
        content TEXT,
        excerpt TEXT,
        featured_image TEXT,
        category TEXT,
        tags TEXT,
        author TEXT,
        is_published BOOLEAN DEFAULT 0,
        publish_date TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Cases/Projects table
    c.execute('''CREATE TABLE IF NOT EXISTS case_studies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        client_name TEXT,
        project_type TEXT,
        location TEXT,
        description TEXT,
        challenge TEXT,
        solution TEXT,
        results TEXT,
        images TEXT,
        videos TEXT,
        products_used TEXT,
        project_date TEXT,
        is_featured BOOLEAN DEFAULT 0,
        is_published BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Solutions table
    c.execute('''CREATE TABLE IF NOT EXISTS solutions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        features TEXT,
        benefits TEXT,
        applications TEXT,
        related_products TEXT,
        images TEXT,
        videos TEXT,
        brochure_url TEXT,
        is_active BOOLEAN DEFAULT 1,
        sort_order INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Support content table
    c.execute('''CREATE TABLE IF NOT EXISTS support_content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        content_type TEXT NOT NULL,
        content TEXT,
        file_url TEXT,
        download_count INTEGER DEFAULT 0,
        is_public BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Existing tables (inquiries, quotes, users, etc.)
    c.execute('''CREATE TABLE IF NOT EXISTS inquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        company TEXT,
        message TEXT,
        product_interest TEXT,
        status TEXT DEFAULT 'new',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS quotes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        company TEXT,
        product_type TEXT,
        quantity TEXT,
        specifications TEXT,
        message TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT,
        role TEXT DEFAULT 'admin',
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Insert default admin user if not exists
    c.execute("SELECT COUNT(*) FROM admin_users WHERE username = 'admin'")
    if c.fetchone()[0] == 0:
        password_hash = generate_password_hash('admin123')
        c.execute("INSERT INTO admin_users (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
                 ('admin', password_hash, 'admin@lianjinled.com', 'super_admin'))
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Authentication decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Utility functions
def get_db_connection():
    conn = sqlite3.connect('admin_database.db')
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'pdf', 'doc', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM admin_users WHERE username = ? AND is_active = 1', 
                           (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('登录成功！', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('用户名或密码错误！', 'error')
    
    return render_template('login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('已成功退出登录！', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    conn = get_db_connection()
    
    # Get statistics
    stats = {
        'products': conn.execute('SELECT COUNT(*) FROM products WHERE is_active = 1').fetchone()[0],
        'inquiries': conn.execute('SELECT COUNT(*) FROM inquiries WHERE status = "new"').fetchone()[0],
        'quotes': conn.execute('SELECT COUNT(*) FROM quotes WHERE status = "pending"').fetchone()[0],
        'cases': conn.execute('SELECT COUNT(*) FROM case_studies WHERE is_published = 1').fetchone()[0],
        'news': conn.execute('SELECT COUNT(*) FROM news_articles WHERE is_published = 1').fetchone()[0],
        'solutions': conn.execute('SELECT COUNT(*) FROM solutions WHERE is_active = 1').fetchone()[0]
    }
    
    # Get recent activities
    recent_inquiries = conn.execute('SELECT * FROM inquiries ORDER BY created_at DESC LIMIT 5').fetchall()
    recent_quotes = conn.execute('SELECT * FROM quotes ORDER BY created_at DESC LIMIT 5').fetchall()
    
    conn.close()
    
    return render_template('enhanced_dashboard.html', 
                         stats=stats, 
                         recent_inquiries=recent_inquiries,
                         recent_quotes=recent_quotes)

# Page Content Management Routes
@app.route('/admin/content/<page_name>')
@login_required
def manage_page_content(page_name):
    conn = get_db_connection()
    content_sections = conn.execute(
        'SELECT * FROM page_content WHERE page_name = ? ORDER BY sort_order, section_name',
        (page_name,)
    ).fetchall()
    conn.close()
    
    return render_template('page_content_manager.html', 
                         page_name=page_name, 
                         content_sections=content_sections)

@app.route('/admin/content/<page_name>/edit/<int:section_id>')
@app.route('/admin/content/<page_name>/edit')
@login_required
def edit_page_content(page_name, section_id=None):
    conn = get_db_connection()
    
    if section_id:
        content = conn.execute('SELECT * FROM page_content WHERE id = ?', (section_id,)).fetchone()
    else:
        content = None
    
    conn.close()
    
    return render_template('content_editor.html', 
                         page_name=page_name, 
                         content=content)

@app.route('/admin/content/save', methods=['POST'])
@login_required
def save_page_content():
    data = request.get_json()
    
    conn = get_db_connection()
    
    if data.get('id'):
        # Update existing content
        conn.execute('''UPDATE page_content 
                       SET section_name=?, content_type=?, content_data=?, 
                           image_url=?, video_url=?, parameters=?, 
                           sort_order=?, updated_at=CURRENT_TIMESTAMP
                       WHERE id=?''',
                    (data['section_name'], data['content_type'], data['content_data'],
                     data.get('image_url'), data.get('video_url'), data.get('parameters'),
                     data.get('sort_order', 0), data['id']))
    else:
        # Insert new content
        conn.execute('''INSERT INTO page_content 
                       (page_name, section_name, content_type, content_data, 
                        image_url, video_url, parameters, sort_order)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (data['page_name'], data['section_name'], data['content_type'], 
                     data['content_data'], data.get('image_url'), data.get('video_url'),
                     data.get('parameters'), data.get('sort_order', 0)))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': '内容保存成功！'})

# Enhanced Products Management
@app.route('/admin/products')
@login_required
def admin_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY sort_order, created_at DESC').fetchall()
    conn.close()
    return render_template('enhanced_products.html', products=products)

@app.route('/admin/products/edit/<int:product_id>')
@app.route('/admin/products/new')
@login_required
def edit_product(product_id=None):
    conn = get_db_connection()
    
    if product_id:
        product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    else:
        product = None
    
    conn.close()
    
    return render_template('enhanced_product_form.html', product=product)

# News Management
@app.route('/admin/news')
@login_required
def admin_news():
    conn = get_db_connection()
    articles = conn.execute('SELECT * FROM news_articles ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('enhanced_news.html', articles=articles)

@app.route('/admin/news/edit/<int:article_id>')
@app.route('/admin/news/new')
@login_required
def edit_news(article_id=None):
    conn = get_db_connection()
    
    if article_id:
        article = conn.execute('SELECT * FROM news_articles WHERE id = ?', (article_id,)).fetchone()
    else:
        article = None
    
    conn.close()
    
    return render_template('enhanced_news_form.html', article=article)

# Cases Management
@app.route('/admin/cases')
@login_required
def admin_cases():
    conn = get_db_connection()
    cases = conn.execute('SELECT * FROM case_studies ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('enhanced_cases.html', cases=cases)

@app.route('/admin/cases/edit/<int:case_id>')
@app.route('/admin/cases/new')
@login_required
def edit_case(case_id=None):
    conn = get_db_connection()
    
    if case_id:
        case = conn.execute('SELECT * FROM case_studies WHERE id = ?', (case_id,)).fetchone()
    else:
        case = None
    
    conn.close()
    
    return render_template('enhanced_case_form.html', case=case)

# Solutions Management
@app.route('/admin/solutions')
@login_required
def admin_solutions():
    conn = get_db_connection()
    solutions = conn.execute('SELECT * FROM solutions ORDER BY sort_order, created_at DESC').fetchall()
    conn.close()
    return render_template('enhanced_solutions.html', solutions=solutions)

@app.route('/admin/solutions/edit/<int:solution_id>')
@app.route('/admin/solutions/new')
@login_required
def edit_solution(solution_id=None):
    conn = get_db_connection()
    
    if solution_id:
        solution = conn.execute('SELECT * FROM solutions WHERE id = ?', (solution_id,)).fetchone()
    else:
        solution = None
    
    conn.close()
    
    return render_template('enhanced_solution_form.html', solution=solution)

# Support Content Management
@app.route('/admin/support')
@login_required
def admin_support():
    conn = get_db_connection()
    support_items = conn.execute('SELECT * FROM support_content ORDER BY category, created_at DESC').fetchall()
    conn.close()
    return render_template('enhanced_support.html', support_items=support_items)

# Media Management
@app.route('/admin/media')
@login_required
def admin_media():
    conn = get_db_connection()
    media_files = conn.execute('SELECT * FROM media_files ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('media_management.html', media_files=media_files)

@app.route('/admin/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有选择文件'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Save to database
        conn = get_db_connection()
        conn.execute('''INSERT INTO media_files 
                       (filename, original_name, file_type, file_size, upload_path, page_name, section_name)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (unique_filename, filename, file.content_type, 
                     os.path.getsize(file_path), file_path,
                     request.form.get('page_name'), request.form.get('section_name')))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': '文件上传成功',
            'filename': unique_filename,
            'url': f'/static/uploads/{unique_filename}'
        })
    
    return jsonify({'success': False, 'message': '不支持的文件类型'})

# API endpoints for frontend synchronization
@app.route('/api/content/<page_name>')
def api_get_page_content(page_name):
    conn = get_db_connection()
    content = conn.execute(
        'SELECT * FROM page_content WHERE page_name = ? AND is_active = 1 ORDER BY sort_order',
        (page_name,)
    ).fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in content])

@app.route('/api/products')
def api_get_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products WHERE is_active = 1 ORDER BY sort_order').fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in products])

# Existing routes (inquiries, quotes, etc.)
@app.route('/admin/inquiries')
@login_required
def admin_inquiries():
    conn = get_db_connection()
    inquiries = conn.execute('SELECT * FROM inquiries ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('inquiries.html', inquiries=inquiries)

@app.route('/admin/quotes')
@login_required
def admin_quotes():
    conn = get_db_connection()
    quotes = conn.execute('SELECT * FROM quotes ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('quotes.html', quotes=quotes)

@app.route('/admin/settings')
@login_required
def admin_settings():
    return render_template('settings.html')

@app.route('/admin/users')
@login_required
def admin_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM admin_users ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('users.html', users=users)

@app.route('/admin/statistics')
@login_required
def admin_statistics():
    return render_template('statistics.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)