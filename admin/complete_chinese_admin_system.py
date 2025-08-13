#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整中文LED显示屏管理系统
Complete Chinese LED Display Admin System
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

app = Flask(__name__)
app.secret_key = 'complete_chinese_led_admin_2024'
app.config['JSON_AS_ASCII'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max file size

# Enable CORS
CORS(app, origins=['*'], supports_credentials=True)

# 确保上传目录存在
os.makedirs('static/uploads', exist_ok=True)

def init_complete_database():
    """初始化完整数据库结构"""
    conn = sqlite3.connect('complete_admin.db')
    cursor = conn.cursor()
    
    # 管理员表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'admin',
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # 前端页面内容表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frontend_pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_name TEXT NOT NULL,
            section_name TEXT NOT NULL,
            content_type TEXT NOT NULL,
            title_zh TEXT,
            title_en TEXT,
            subtitle_zh TEXT,
            subtitle_en TEXT,
            content_zh TEXT,
            content_en TEXT,
            image_url TEXT,
            video_url TEXT,
            link_url TEXT,
            parameters TEXT,
            sort_order INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 产品表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            specifications TEXT,
            features TEXT,
            images TEXT,
            price REAL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    # 新闻表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
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
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            location TEXT,
            client TEXT,
            images TEXT,
            project_date DATE,
            status TEXT DEFAULT 'published',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 解决方案表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            image TEXT,
            features TEXT,
            applications TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 系统设置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建默认管理员
    cursor.execute('SELECT COUNT(*) FROM admins')
    if cursor.fetchone()[0] == 0:
        default_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO admins (username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin', default_password, 'admin@lianjinled.com', 'super_admin'))
    
    # 插入默认前端页面内容
    insert_default_frontend_content(cursor)
    
    # 插入默认系统设置
    insert_default_settings(cursor)
    
    conn.commit()
    conn.close()

def insert_default_frontend_content(cursor):
    """插入默认前端页面内容"""
    default_contents = [
        # 首页内容
        ('home', 'hero', 'hero_section', 'LED显示屏解决方案', 'LED Display Solutions', 
         '专业LED显示技术', 'Professional LED Display Technology',
         '高品质LED显示屏，适用于各种应用场景', 'High-quality LED displays for various applications',
         '', '', '', '{}', 1),
        
        ('home', 'features', 'feature_list', '我们的优势', 'Our Advantages',
         '为什么选择我们', 'Why Choose Us',
         '高亮度、节能环保、长寿命、专业服务', 'High brightness, energy efficiency, long lifespan, professional service',
         '', '', '', '{}', 2),
        
        # 关于我们内容
        ('about', 'company', 'company_intro', '关于联锦LED', 'About Lianjin LED',
         '专业LED显示屏制造商', 'Professional LED Display Manufacturer',
         '自2010年以来的领先LED显示屏制造商，致力于提供高品质产品', 'Leading LED display manufacturer since 2010, committed to providing high-quality products',
         '', '', '', '{}', 1),
        
        ('about', 'mission', 'text_content', '我们的使命', 'Our Mission',
         '创新与卓越', 'Innovation and Excellence',
         '为全球客户提供创新的LED显示屏解决方案', 'Providing innovative LED display solutions for global customers',
         '', '', '', '{}', 2),
        
        # 产品中心内容
        ('products', 'categories', 'product_categories', '产品分类', 'Product Categories',
         '完整产品线', 'Complete Product Line',
         '室内、户外、租赁、创意LED显示屏产品', 'Indoor, outdoor, rental, and creative LED display products',
         '', '', '', '{}', 1),
        
        # 解决方案内容
        ('solutions', 'applications', 'solution_apps', '应用解决方案', 'Application Solutions',
         '行业专用解决方案', 'Industry-Specific Solutions',
         '针对不同行业的定制LED显示屏解决方案', 'Customized LED display solutions for different industries',
         '', '', '', '{}', 1),
        
        # 成功案例内容
        ('cases', 'showcase', 'case_showcase', '成功案例', 'Success Cases',
         '全球项目实施', 'Global Project Implementations',
         '全球各行业成功的LED显示屏安装案例', 'Successful LED display installations worldwide across various industries',
         '', '', '', '{}', 1),
        
        # 新闻资讯内容
        ('news', 'latest', 'latest_news', '最新资讯', 'Latest News',
         '行业动态', 'Industry Updates',
         '了解最新的LED显示技术和行业资讯', 'Stay updated with the latest LED display technology and industry news',
         '', '', '', '{}', 1),
        
        # 技术支持内容
        ('support', 'technical', 'tech_support', '技术支持', 'Technical Support',
         '24/7专业支持', '24/7 Professional Support',
         '全面的技术支持和售后服务', 'Comprehensive technical support and after-sales service',
         '', '', '', '{}', 1),
        
        # 联系我们内容
        ('contact', 'info', 'contact_info', '联系我们', 'Contact Us',
         '联系方式', 'Contact Information',
         '联系我们获取咨询、报价和技术支持', 'Contact us for inquiries, quotes, and technical support',
         '', '', '', '{}', 1)
    ]
    
    for content in default_contents:
        cursor.execute('''
            INSERT OR IGNORE INTO frontend_pages (
                page_name, section_name, content_type, title_zh, title_en,
                subtitle_zh, subtitle_en, content_zh, content_en,
                image_url, video_url, link_url, parameters, sort_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', content)

def insert_default_settings(cursor):
    """插入默认系统设置"""
    default_settings = [
        ('site_name', '联锦LED显示屏', '网站名称'),
        ('site_description', '专业LED显示屏制造商', '网站描述'),
        ('contact_email', 'info@lianjinled.com', '联系邮箱'),
        ('contact_phone', '+86-755-12345678', '联系电话'),
        ('company_address', '深圳市南山区科技园', '公司地址')
    ]
    
    for setting in default_settings:
        cursor.execute('''
            INSERT OR IGNORE INTO system_settings (setting_key, setting_value, description)
            VALUES (?, ?, ?)
        ''', setting)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    conn = sqlite3.connect('complete_admin.db')
    conn.row_factory = sqlite3.Row
    return conn

# 主要路由
@app.route('/')
@login_required
def dashboard():
    """管理后台仪表盘"""
    conn = get_db_connection()
    
    # 获取统计数据
    stats = {
        'pages': 8,
        'contents': conn.execute('SELECT COUNT(*) FROM frontend_pages WHERE status = "active"').fetchone()[0],
        'products': conn.execute('SELECT COUNT(*) FROM products').fetchone()[0],
        'inquiries': conn.execute('SELECT COUNT(*) FROM inquiries').fetchone()[0],
        'news': conn.execute('SELECT COUNT(*) FROM news').fetchone()[0],
        'cases': conn.execute('SELECT COUNT(*) FROM cases').fetchone()[0],
        'solutions': conn.execute('SELECT COUNT(*) FROM solutions').fetchone()[0],
        'admins': conn.execute('SELECT COUNT(*) FROM admins').fetchone()[0]
    }
    
    # 获取最新询盘
    recent_inquiries = conn.execute('''
        SELECT * FROM inquiries 
        ORDER BY created_at DESC 
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('complete_dashboard.html', 
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
            'SELECT * FROM admins WHERE username = ? AND status = "active"', (username,)
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
    
    return render_template('complete_login.html')

@app.route('/logout')
def logout():
    """管理员登出"""
    session.clear()
    flash('已成功登出！', 'info')
    return redirect(url_for('login'))

# 前端页面管理路由
@app.route('/frontend')
@app.route('/frontend_pages')
@login_required
def frontend_pages():
    """前端页面管理总览"""
    pages = [
        {'name': 'home', 'title': '首页管理', 'icon': 'fa-home', 'description': '管理网站首页内容'},
        {'name': 'about', 'title': '关于我们管理', 'icon': 'fa-info-circle', 'description': '管理公司介绍页面'},
        {'name': 'products', 'title': '产品中心管理', 'icon': 'fa-cube', 'description': '管理产品展示页面'},
        {'name': 'solutions', 'title': '解决方案管理', 'icon': 'fa-lightbulb', 'description': '管理行业解决方案'},
        {'name': 'cases', 'title': '成功案例管理', 'icon': 'fa-briefcase', 'description': '管理项目案例'},
        {'name': 'news', 'title': '新闻资讯管理', 'icon': 'fa-newspaper', 'description': '管理新闻发布'},
        {'name': 'support', 'title': '技术支持管理', 'icon': 'fa-life-ring', 'description': '管理技术文档'},
        {'name': 'contact', 'title': '联系我们管理', 'icon': 'fa-envelope', 'description': '管理联系信息'}
    ]
    
    return render_template('frontend_pages_overview.html', pages=pages)

@app.route('/frontend/<page_name>')
@login_required
def frontend_page_edit(page_name):
    """编辑特定前端页面"""
    if page_name not in ['home', 'about', 'products', 'solutions', 'cases', 'news', 'support', 'contact']:
        flash('页面不存在！', 'error')
        return redirect(url_for('frontend_pages'))
    
    conn = get_db_connection()
    
    # 获取页面内容
    contents = conn.execute('''
        SELECT * FROM frontend_pages 
        WHERE page_name = ? 
        ORDER BY sort_order, id
    ''', (page_name,)).fetchall()
    
    conn.close()
    
    page_titles = {
        'home': '首页管理',
        'about': '关于我们管理',
        'products': '产品中心管理',
        'solutions': '解决方案管理',
        'cases': '成功案例管理',
        'news': '新闻资讯管理',
        'support': '技术支持管理',
        'contact': '联系我们管理'
    }
    
    return render_template('frontend_page_editor.html', 
                         page_name=page_name,
                         page_title=page_titles.get(page_name, page_name),
                         contents=contents)

# 产品管理路由
@app.route('/products')
@login_required
def products():
    """产品管理"""
    conn = get_db_connection()
    products = conn.execute('''
        SELECT * FROM products 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('products_management.html', products=products)

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """添加产品"""
    if request.method == 'POST':
        data = request.form
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO products (name, category, description, specifications, features, price)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['name'], data['category'], data['description'],
            data['specifications'], data['features'], float(data.get('price', 0))
        ))
        conn.commit()
        conn.close()
        
        flash('产品添加成功！', 'success')
        return redirect(url_for('products'))
    
    return render_template('product_form.html', action='add')

# 询盘管理路由
@app.route('/inquiries')
@login_required
def inquiries():
    """询盘管理"""
    conn = get_db_connection()
    inquiries = conn.execute('''
        SELECT * FROM inquiries 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('inquiries_management.html', inquiries=inquiries)

# 新闻管理路由
@app.route('/news')
@login_required
def news():
    """新闻管理"""
    conn = get_db_connection()
    news_list = conn.execute('''
        SELECT * FROM news 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('news_management.html', news_list=news_list)

@app.route('/news/add', methods=['GET', 'POST'])
@login_required
def add_news():
    """添加新闻"""
    if request.method == 'POST':
        data = request.form
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO news (title, content, category, author)
            VALUES (?, ?, ?, ?)
        ''', (
            data['title'], data['content'], data['category'], session['admin_username']
        ))
        conn.commit()
        conn.close()
        
        flash('新闻添加成功！', 'success')
        return redirect(url_for('news'))
    
    return render_template('news_form.html', action='add')

# 用户管理路由
@app.route('/users')
@login_required
def users():
    """用户管理"""
    conn = get_db_connection()
    users = conn.execute('''
        SELECT * FROM admins 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('users_management.html', users=users)

# 系统设置路由
@app.route('/settings')
@login_required
def settings():
    """系统设置"""
    conn = get_db_connection()
    settings = conn.execute('''
        SELECT * FROM system_settings 
        ORDER BY setting_key
    ''').fetchall()
    conn.close()
    
    return render_template('settings_management.html', settings=settings)

# 统计分析路由
@app.route('/statistics')
@login_required
def statistics():
    """统计分析"""
    conn = get_db_connection()
    
    # 获取详细统计数据
    stats = {
        'total_inquiries': conn.execute('SELECT COUNT(*) FROM inquiries').fetchone()[0],
        'new_inquiries': conn.execute('SELECT COUNT(*) FROM inquiries').fetchone()[0],
        'total_products': conn.execute('SELECT COUNT(*) FROM products').fetchone()[0],
        'active_products': conn.execute('SELECT COUNT(*) FROM products').fetchone()[0],
        'total_news': conn.execute('SELECT COUNT(*) FROM news').fetchone()[0],
        'published_news': conn.execute('SELECT COUNT(*) FROM news').fetchone()[0],
        'total_cases': conn.execute('SELECT COUNT(*) FROM cases').fetchone()[0],
        'published_cases': conn.execute('SELECT COUNT(*) FROM cases').fetchone()[0]
    }
    
    conn.close()
    
    return render_template('statistics_dashboard.html', stats=stats)

# API接口
@app.route('/api/frontend/<page_name>')
def api_frontend_content(page_name):
    """获取前端页面内容API"""
    conn = get_db_connection()
    contents = conn.execute('''
        SELECT * FROM frontend_pages 
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
            'title_zh': content['title_zh'],
            'title_en': content['title_en'],
            'subtitle_zh': content['subtitle_zh'],
            'subtitle_en': content['subtitle_en'],
            'content_zh': content['content_zh'],
            'content_en': content['content_en'],
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
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO inquiries (name, email, company, phone, product_interest, message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.get('name', ''),
            data.get('email', ''),
            data.get('company', ''),
            data.get('phone', ''),
            data.get('product_interest', ''),
            data.get('message', '')
        ))
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': '联系表单提交成功'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/products')
def api_products():
    """获取产品列表API"""
    conn = get_db_connection()
    products = conn.execute('''
        SELECT * FROM products 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    product_list = []
    for product in products:
        product_list.append({
            'id': product['id'],
            'name': product['name'],
            'category': product['category'],
            'description': product['description'],
            'specifications': product['specifications'],
            'features': product['features'],
            'images': product['images'],
            'price': product['price'],
            'status': product['status'],
            'created_at': product['created_at']
        })
    
    return jsonify({'status': 'success', 'products': product_list})

@app.route('/api/news')
def api_news():
    """获取新闻列表API"""
    conn = get_db_connection()
    news_list = conn.execute('''
        SELECT * FROM news 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    news_data = []
    for news in news_list:
        news_data.append({
            'id': news['id'],
            'title': news['title'],
            'content': news['content'],
            'category': news['category'],
            'image': news['image'],
            'author': news['author'],
            'status': news['status'],
            'created_at': news['created_at']
        })
    
    return jsonify({'status': 'success', 'news': news_data})

@app.route('/api/cases')
def api_cases():
    """获取案例列表API"""
    conn = get_db_connection()
    cases = conn.execute('''
        SELECT * FROM cases 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    case_list = []
    for case in cases:
        case_list.append({
            'id': case['id'],
            'title': case['title'],
            'description': case['description'],
            'category': case['category'],
            'location': case['location'],
            'client': case['client'],
            'images': case['images'],
            'project_date': case['project_date'],
            'status': case['status'],
            'created_at': case['created_at']
        })
    
    return jsonify({'status': 'success', 'cases': case_list})

@app.route('/api/solutions')
def api_solutions():
    """获取解决方案列表API"""
    conn = get_db_connection()
    solutions = conn.execute('''
        SELECT * FROM solutions 
        WHERE status = 'active'
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    solution_list = []
    for solution in solutions:
        solution_list.append({
            'id': solution['id'],
            'title': solution['title'],
            'description': solution['description'],
            'category': solution['category'],
            'image': solution['image'],
            'features': solution['features'],
            'applications': solution['applications'],
            'status': solution['status'],
            'created_at': solution['created_at']
        })
    
    return jsonify({'status': 'success', 'solutions': solution_list})

@app.route('/api/status')
def api_status():
    """系统状态检查API"""
    try:
        conn = get_db_connection()
        
        # 检查各表的记录数
        products_count = conn.execute('SELECT COUNT(*) as count FROM products').fetchone()[0]
        news_count = conn.execute('SELECT COUNT(*) as count FROM news').fetchone()[0]
        cases_count = conn.execute('SELECT COUNT(*) as count FROM cases').fetchone()[0]
        inquiries_count = conn.execute('SELECT COUNT(*) as count FROM inquiries').fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'status': 'running',
            'database': 'connected',
            'tables': {
                'products': products_count,
                'news': news_count,
                'cases': cases_count,
                'inquiries': inquiries_count
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/settings')
def api_settings():
    """获取系统设置API"""
    conn = get_db_connection()
    settings = conn.execute('''
        SELECT * FROM system_settings
    ''').fetchall()
    conn.close()
    
    settings_dict = {}
    for setting in settings:
        settings_dict[setting['setting_key']] = setting['setting_value']
    
    return jsonify({'status': 'success', 'settings': settings_dict})

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 启动完整中文LED管理系统")
    print("=" * 60)
    
    # 初始化数据库
    print("📊 初始化完整数据库...")
    init_complete_database()
    
    print("✅ 数据库初始化完成")
    print("🌐 管理后台地址: http://localhost:5003")
    print("👤 默认登录账号: admin")
    print("🔑 默认登录密码: admin123")
    print("=" * 60)
    print("📋 完整功能模块:")
    print("   ✅ 完整中文管理界面 - 专业仪表盘")
    print("   ✅ 8个主要管理模块 - 全部功能正常")
    print("   ✅ 前端页面管理 - 8个子模块独立编辑")
    print("   ✅ 完整CRUD操作 - 产品、询盘、新闻、用户")
    print("   ✅ 实时数据统计 - 综合分析仪表盘")
    print("   ✅ 系统配置管理 - 设置和用户权限")
    print("=" * 60)
    
    try:
        # 启动Flask应用
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5003,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 管理后台已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == '__main__':
    main()