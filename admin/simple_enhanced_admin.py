from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import sqlite3
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.secret_key = 'lianjin-led-admin-2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database initialization
def init_db():
    conn = sqlite3.connect('admin.db')
    cursor = conn.cursor()
    
    # Page content management table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS page_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_name TEXT NOT NULL,
            section_name TEXT NOT NULL,
            content_type TEXT NOT NULL DEFAULT 'text',
            title TEXT,
            content_data TEXT,
            image_url TEXT,
            video_url TEXT,
            parameters TEXT,
            sort_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Users table for admin authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create default admin user if not exists
    cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
    if cursor.fetchone()[0] == 0:
        password_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, password_hash) 
            VALUES (?, ?)
        ''', ('admin', password_hash))
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get content statistics
    conn = sqlite3.connect('admin.db')
    cursor = conn.cursor()
    
    stats = {}
    pages = ['home', 'about', 'products', 'solutions', 'cases', 'news', 'support', 'contact']
    
    for page in pages:
        cursor.execute('SELECT COUNT(*) FROM page_content WHERE page_name = ?', (page,))
        stats[page] = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template('simple_dashboard.html', stats=stats, pages=pages)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('admin.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, password_hash FROM users WHERE username = ? AND is_active = 1', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('simple_login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/page/<page_name>')
def manage_page(page_name):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('admin.db')
    cursor = conn.cursor()
    
    # Get all content for this page
    cursor.execute('''
        SELECT id, section_name, content_type, title, content_data, image_url, video_url, 
               parameters, sort_order, is_active, created_at
        FROM page_content 
        WHERE page_name = ? 
        ORDER BY sort_order, created_at
    ''', (page_name,))
    
    content_items = cursor.fetchall()
    conn.close()
    
    return render_template('page_manager.html', 
                         page_name=page_name, 
                         content_items=content_items)

@app.route('/page/<page_name>/edit')
@app.route('/page/<page_name>/edit/<int:content_id>')
def edit_page_content(page_name, content_id=None):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    content = None
    if content_id:
        conn = sqlite3.connect('admin.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, section_name, content_type, title, content_data, image_url, video_url, 
                   parameters, sort_order, is_active
            FROM page_content 
            WHERE id = ?
        ''', (content_id,))
        content = cursor.fetchone()
        conn.close()
    
    return render_template('content_editor_simple.html', 
                         page_name=page_name, 
                         content=content)

@app.route('/save_content', methods=['POST'])
def save_content():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    try:
        data = request.get_json()
        
        conn = sqlite3.connect('admin.db')
        cursor = conn.cursor()
        
        if data.get('id'):
            # Update existing content
            cursor.execute('''
                UPDATE page_content 
                SET section_name = ?, content_type = ?, title = ?, content_data = ?, 
                    image_url = ?, video_url = ?, parameters = ?, 
                    sort_order = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                data['section_name'], data['content_type'], data.get('title', ''),
                data['content_data'], data.get('image_url'), data.get('video_url'), 
                data.get('parameters'), data['sort_order'], data['is_active'], data['id']
            ))
        else:
            # Insert new content
            cursor.execute('''
                INSERT INTO page_content 
                (page_name, section_name, content_type, title, content_data, image_url, 
                 video_url, parameters, sort_order, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['page_name'], data['section_name'], data['content_type'], 
                data.get('title', ''), data['content_data'], data.get('image_url'), 
                data.get('video_url'), data.get('parameters'), data['sort_order'], data['is_active']
            ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Content saved successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/delete_content/<int:content_id>', methods=['POST'])
def delete_content(content_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    try:
        conn = sqlite3.connect('admin.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM page_content WHERE id = ?', (content_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Content deleted successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    if file:
        # Generate unique filename
        filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Return the URL
        file_url = f'/uploads/{filename}'
        return jsonify({'success': True, 'url': file_url})
    
    return jsonify({'success': False, 'message': 'Upload failed'})

# API endpoint for frontend to get content
@app.route('/api/content/<page_name>')
def api_get_content(page_name):
    conn = sqlite3.connect('admin.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT section_name, content_type, title, content_data, image_url, video_url, 
               parameters, sort_order
        FROM page_content 
        WHERE page_name = ? AND is_active = 1
        ORDER BY sort_order, created_at
    ''', (page_name,))
    
    content_items = cursor.fetchall()
    conn.close()
    
    # Convert to JSON format
    content_data = []
    for item in content_items:
        content_data.append({
            'section_name': item[0],
            'content_type': item[1],
            'title': item[2],
            'content_data': item[3],
            'image_url': item[4],
            'video_url': item[5],
            'parameters': json.loads(item[6]) if item[6] else {},
            'sort_order': item[7]
        })
    
    return jsonify(content_data)

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return app.send_static_file(os.path.join('uploads', filename))

if __name__ == '__main__':
    app.run(debug=True, port=5002)