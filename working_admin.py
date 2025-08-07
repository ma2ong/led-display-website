from flask import Flask, request, jsonify, redirect, session, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__, static_folder='.')
app.secret_key = 'your-secret-key-here'
CORS(app)

def get_db():
    return sqlite3.connect('led_admin.db')

@app.route('/')
def index():
    return send_from_directory('.', 'homepage.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

@app.route('/admin')
def admin_login():
    if session.get('admin_logged_in'):
        return redirect('/admin/dashboard')
    
    return '''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>管理员登录</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 50px; }
            .login-container { max-width: 400px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h2 { text-align: center; color: #333; margin-bottom: 30px; }
            input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
            button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #0056b3; }
            .error { color: red; text-align: center; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h2>🔐 管理员登录</h2>
            <form method="POST" action="/admin/login">
                <input type="text" name="username" placeholder="用户名" required>
                <input type="password" name="password" placeholder="密码" required>
                <button type="submit">登录</button>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username == 'admin' and password == 'admin123':
        session['admin_logged_in'] = True
        return redirect('/admin/dashboard')
    else:
        return redirect('/admin?error=1')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect('/admin')
    
    # 获取统计数据
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM products')
    products_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM inquiries')
    inquiries_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM news')
    news_count = cursor.fetchone()[0]
    
    conn.close()
    
    return f'''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>管理后台</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; background: #f5f5f5; }}
            .header {{ background: #007bff; color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }}
            .container {{ max-width: 1200px; margin: 20px auto; padding: 0 20px; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}
            .stat-number {{ font-size: 2em; font-weight: bold; color: #007bff; }}
            .nav-buttons {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
            .nav-btn {{ display: block; padding: 15px; background: #007bff; color: white; text-decoration: none; text-align: center; border-radius: 5px; }}
            .nav-btn:hover {{ background: #0056b3; }}
            .logout {{ background: #dc3545; padding: 8px 16px; color: white; text-decoration: none; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏢 LED显示屏管理系统</h1>
            <a href="/admin/logout" class="logout">退出登录</a>
        </div>
        <div class="container">
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{products_count}</div>
                    <div>产品数量</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{inquiries_count}</div>
                    <div>客户询盘</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{news_count}</div>
                    <div>新闻文章</div>
                </div>
            </div>
            <div class="nav-buttons">
                <a href="/admin/products" class="nav-btn">📦 产品管理</a>
                <a href="/admin/inquiries" class="nav-btn">📧 询盘管理</a>
                <a href="/admin/news" class="nav-btn">📰 新闻管理</a>
                <a href="/admin/api-test" class="nav-btn">🔧 API测试</a>
                <a href="/" class="nav-btn">🌐 查看网站</a>
                <a href="/test-integration.html" class="nav-btn">🧪 集成测试</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/admin/products')
def admin_products():
    if not session.get('admin_logged_in'):
        return redirect('/admin')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
    products = cursor.fetchall()
    conn.close()
    
    products_html = ""
    for product in products:
        products_html += f'''
        <tr>
            <td>{product[0]}</td>
            <td>{product[1]}</td>
            <td>{product[2]}</td>
            <td>{product[4]}</td>
            <td>{product[7]}</td>
        </tr>
        '''
    
    return f'''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>产品管理</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; background: #f5f5f5; }}
            .header {{ background: #007bff; color: white; padding: 15px 20px; }}
            .container {{ max-width: 1200px; margin: 20px auto; padding: 0 20px; }}
            table {{ width: 100%; background: white; border-collapse: collapse; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #f8f9fa; font-weight: bold; }}
            .back-btn {{ display: inline-block; margin-bottom: 20px; padding: 10px 20px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📦 产品管理</h1>
        </div>
        <div class="container">
            <a href="/admin/dashboard" class="back-btn">← 返回仪表板</a>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>产品名称</th>
                        <th>分类</th>
                        <th>价格</th>
                        <th>创建时间</th>
                    </tr>
                </thead>
                <tbody>
                    {products_html}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    '''

@app.route('/admin/inquiries')
def admin_inquiries():
    if not session.get('admin_logged_in'):
        return redirect('/admin')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inquiries ORDER BY created_at DESC')
    inquiries = cursor.fetchall()
    conn.close()
    
    inquiries_html = ""
    for inquiry in inquiries:
        inquiries_html += f'''
        <tr>
            <td>{inquiry[0]}</td>
            <td>{inquiry[1]}</td>
            <td>{inquiry[2]}</td>
            <td>{inquiry[3] or ''}</td>
            <td>{inquiry[6]}</td>
            <td>{inquiry[7]}</td>
        </tr>
        '''
    
    return f'''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>询盘管理</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; background: #f5f5f5; }}
            .header {{ background: #007bff; color: white; padding: 15px 20px; }}
            .container {{ max-width: 1200px; margin: 20px auto; padding: 0 20px; }}
            table {{ width: 100%; background: white; border-collapse: collapse; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #f8f9fa; font-weight: bold; }}
            .back-btn {{ display: inline-block; margin-bottom: 20px; padding: 10px 20px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📧 询盘管理</h1>
        </div>
        <div class="container">
            <a href="/admin/dashboard" class="back-btn">← 返回仪表板</a>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>姓名</th>
                        <th>邮箱</th>
                        <th>电话</th>
                        <th>状态</th>
                        <th>提交时间</th>
                    </tr>
                </thead>
                <tbody>
                    {inquiries_html}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    '''

@app.route('/admin/api-test')
def admin_api_test():
    if not session.get('admin_logged_in'):
        return redirect('/admin')
    
    return '''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>API测试</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; background: #f5f5f5; }
            .header { background: #007bff; color: white; padding: 15px 20px; }
            .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
            .test-section { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            button { padding: 10px 20px; margin: 5px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border: 1px solid #dee2e6; max-height: 300px; overflow-y: auto; }
            .back-btn { display: inline-block; margin-bottom: 20px; padding: 10px 20px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔧 API测试</h1>
        </div>
        <div class="container">
            <a href="/admin/dashboard" class="back-btn">← 返回仪表板</a>
            
            <div class="test-section">
                <h3>📦 产品API测试</h3>
                <button onclick="testAPI('/api/products')">获取所有产品</button>
                <button onclick="testAPI('/api/products/featured')">获取特色产品</button>
                <div id="products-result" class="result"></div>
            </div>
            
            <div class="test-section">
                <h3>📰 新闻API测试</h3>
                <button onclick="testAPI('/api/news')">获取新闻列表</button>
                <button onclick="testAPI('/api/news/latest')">获取最新新闻</button>
                <div id="news-result" class="result"></div>
            </div>
            
            <div class="test-section">
                <h3>📊 系统API测试</h3>
                <button onclick="testAPI('/api/health')">健康检查</button>
                <button onclick="testAPI('/api/stats')">获取统计数据</button>
                <div id="system-result" class="result"></div>
            </div>
        </div>
        
        <script>
            async function testAPI(endpoint) {
                const resultId = endpoint.includes('products') ? 'products-result' : 
                                endpoint.includes('news') ? 'news-result' : 'system-result';
                const resultDiv = document.getElementById(resultId);
                
                resultDiv.innerHTML = '<div style="color: #6c757d;">🔄 测试中...</div>';
                
                try {
                    const response = await fetch(endpoint);
                    const data = await response.json();
                    resultDiv.innerHTML = `<div style="color: #28a745;">✅ 成功</div><pre>${JSON.stringify(data, null, 2)}</pre>`;
                } catch (error) {
                    resultDiv.innerHTML = `<div style="color: #dc3545;">❌ 错误: ${error.message}</div>`;
                }
            }
        </script>
    </body>
    </html>
    '''

@app.route('/admin/news')
def admin_news():
    if not session.get('admin_logged_in'):
        return redirect('/admin')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM news ORDER BY created_at DESC')
    news_list = cursor.fetchall()
    conn.close()
    
    news_html = ""
    for news in news_list:
        news_html += f'''
        <tr>
            <td>{news[0]}</td>
            <td>{news[1]}</td>
            <td>{news[2][:100]}...</td>
            <td>{news[3]}</td>
            <td>{news[4]}</td>
            <td>{news[5]}</td>
        </tr>
        '''
    
    return f'''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>新闻管理</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; background: #f5f5f5; }}
            .header {{ background: #007bff; color: white; padding: 15px 20px; }}
            .container {{ max-width: 1200px; margin: 20px auto; padding: 0 20px; }}
            table {{ width: 100%; background: white; border-collapse: collapse; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #f8f9fa; font-weight: bold; }}
            .back-btn {{ display: inline-block; margin-bottom: 20px; padding: 10px 20px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📰 新闻管理</h1>
        </div>
        <div class="container">
            <a href="/admin/dashboard" class="back-btn">← 返回仪表板</a>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>标题</th>
                        <th>内容</th>
                        <th>作者</th>
                        <th>状态</th>
                        <th>创建时间</th>
                    </tr>
                </thead>
                <tbody>
                    {news_html}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    '''

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin')

# API路由
@app.route('/api/products')
def api_products():
    conn = get_db()
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

@app.route('/api/products/featured')
def api_products_featured():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products LIMIT 4')
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

@app.route('/api/news')
def api_news():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM news WHERE status = "published" ORDER BY created_at DESC')
    news_list = cursor.fetchall()
    conn.close()
    
    news_data = []
    for news in news_list:
        news_data.append({
            'id': news[0],
            'title': news[1],
            'content': news[2],
            'author': news[3],
            'status': news[4],
            'created_at': news[5]
        })
    
    return jsonify(news_data)

@app.route('/api/news/latest')
def api_news_latest():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM news WHERE status = "published" ORDER BY created_at DESC LIMIT 3')
    news_list = cursor.fetchall()
    conn.close()
    
    news_data = []
    for news in news_list:
        news_data.append({
            'id': news[0],
            'title': news[1],
            'content': news[2],
            'author': news[3],
            'status': news[4],
            'created_at': news[5]
        })
    
    return jsonify(news_data)

@app.route('/api/contact', methods=['POST'])
def api_contact():
    data = request.get_json()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO inquiries (name, email, phone, company, message)
        VALUES (?, ?, ?, ?, ?)
    ''', (data.get('name'), data.get('email'), data.get('phone'), 
          data.get('company'), data.get('message')))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'message': '询盘提交成功'})

@app.route('/api/stats')
def api_stats():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM products')
    products_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM inquiries')
    inquiries_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM news')
    news_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users')
    users_count = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'products': products_count,
        'inquiries': inquiries_count,
        'news': news_count,
        'users': users_count,
        'status': 'success',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health')
def api_health():
    return jsonify({
        'status': 'success',
        'message': 'API is running',
        'timestamp': datetime.now().isoformat(),
        'database': 'led_admin.db'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5002)