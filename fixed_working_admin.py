from flask import Flask, request, jsonify, redirect, session, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

# 创建Flask应用
app = Flask(__name__, static_folder='.')
app.secret_key = 'your-secret-key-here-change-in-production'
CORS(app)

def get_database_connection():
    """获取数据库连接"""
    db_path = os.path.join(os.getcwd(), 'led_admin.db')
    return sqlite3.connect(db_path)

# 静态文件路由
@app.route('/')
def index():
    return send_from_directory('.', 'homepage.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# 简单的管理员登录页面
@app.route('/admin')
def admin():
    if session.get('admin_logged_in'):
        return redirect('/admin/dashboard')
    
    return '''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>管理员登录</title>
        <style>
            body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 0; height: 100vh; display: flex; align-items: center; justify-content: center; }
            .login-container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
            .login-header { text-align: center; margin-bottom: 30px; }
            .login-header h2 { color: #333; margin: 0; }
            .form-group { margin-bottom: 20px; }
            .form-group label { display: block; margin-bottom: 5px; color: #555; font-weight: bold; }
            .form-group input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; box-sizing: border-box; }
            .btn-login { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; transition: background 0.3s; }
            .btn-login:hover { background: #5a6fd8; }
            .error { color: red; text-align: center; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="login-header">
                <h2>LED显示屏管理系统</h2>
                <p>请登录以继续</p>
            </div>
            <form method="POST" action="/admin/login">
                <div class="form-group">
                    <label for="username">用户名</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">密码</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn-login">登录</button>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/admin/login', methods=['POST'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username == 'admin' and password == 'admin123':
        session['admin_logged_in'] = True
        session['admin_username'] = username
        return redirect('/admin/dashboard')
    else:
        return redirect('/admin?error=1')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect('/admin')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect('/admin')
    
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
    
    return f'''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>管理仪表板</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container-fluid">
            <div class="row">
                <div class="col-md-2 bg-dark text-white p-3" style="min-height: 100vh;">
                    <h5><i class="fas fa-tv"></i> LED管理系统</h5>
                    <hr>
                    <ul class="nav flex-column">
                        <li class="nav-item"><a class="nav-link text-white active" href="/admin/dashboard"><i class="fas fa-tachometer-alt"></i> 仪表板</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/products"><i class="fas fa-box"></i> 产品管理</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/inquiries"><i class="fas fa-envelope"></i> 询盘管理</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/news"><i class="fas fa-newspaper"></i> 新闻管理</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/api-test"><i class="fas fa-code"></i> API测试</a></li>
                        <li class="nav-item"><hr></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/"><i class="fas fa-globe"></i> 查看网站</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/logout"><i class="fas fa-sign-out-alt"></i> 退出登录</a></li>
                    </ul>
                </div>
                <div class="col-md-10 p-4">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h2>管理仪表板</h2>
                        <span class="badge bg-success">在线</span>
                    </div>
                    
                    <div class="row mb-4">
                        <div class="col-md-3">
                            <div class="card bg-primary text-white">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between">
                                        <div>
                                            <h4>{products_count}</h4>
                                            <p>产品总数</p>
                                        </div>
                                        <i class="fas fa-box fa-2x"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card bg-warning text-white">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between">
                                        <div>
                                            <h4>{pending_inquiries}</h4>
                                            <p>待处理询盘</p>
                                        </div>
                                        <i class="fas fa-envelope fa-2x"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card bg-success text-white">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between">
                                        <div>
                                            <h4>{published_news}</h4>
                                            <p>已发布新闻</p>
                                        </div>
                                        <i class="fas fa-newspaper fa-2x"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card bg-info text-white">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between">
                                        <div>
                                            <h4>{active_users}</h4>
                                            <p>系统用户</p>
                                        </div>
                                        <i class="fas fa-users fa-2x"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h5>快速操作</h5>
                                </div>
                                <div class="card-body">
                                    <a href="/admin/products" class="btn btn-primary me-2 mb-2">管理产品</a>
                                    <a href="/admin/inquiries" class="btn btn-warning me-2 mb-2">处理询盘</a>
                                    <a href="/admin/news" class="btn btn-success me-2 mb-2">发布新闻</a>
                                    <a href="/admin/api-test" class="btn btn-info me-2 mb-2">测试API</a>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h5>系统状态</h5>
                                </div>
                                <div class="card-body">
                                    <p><i class="fas fa-database text-success"></i> 数据库: 正常运行</p>
                                    <p><i class="fas fa-server text-success"></i> 服务器: 正常运行</p>
                                    <p><i class="fas fa-cloud text-primary"></i> Supabase: 已配置</p>
                                    <p><i class="fas fa-globe text-info"></i> 网站: 在线</p>
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

@app.route('/admin/products')
def admin_products():
    if not session.get('admin_logged_in'):
        return redirect('/admin')
    
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
    products = cursor.fetchall()
    conn.close()
    
    products_html = ""
    for product in products:
        products_html += f"""
        <tr>
            <td>{product[0]}</td>
            <td>{product[1]}</td>
            <td>{product[2]}</td>
            <td>{product[3][:50]}...</td>
            <td>¥{product[4]}</td>
            <td><span class="badge bg-success">正常</span></td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>产品管理</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container-fluid">
            <div class="row">
                <div class="col-md-2 bg-dark text-white p-3" style="min-height: 100vh;">
                    <h5><i class="fas fa-tv"></i> LED管理系统</h5>
                    <hr>
                    <ul class="nav flex-column">
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/dashboard"><i class="fas fa-tachometer-alt"></i> 仪表板</a></li>
                        <li class="nav-item"><a class="nav-link text-white active" href="/admin/products"><i class="fas fa-box"></i> 产品管理</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/inquiries"><i class="fas fa-envelope"></i> 询盘管理</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/news"><i class="fas fa-newspaper"></i> 新闻管理</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/api-test"><i class="fas fa-code"></i> API测试</a></li>
                        <li class="nav-item"><hr></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/"><i class="fas fa-globe"></i> 查看网站</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/logout"><i class="fas fa-sign-out-alt"></i> 退出登录</a></li>
                    </ul>
                </div>
                <div class="col-md-10 p-4">
                    <h2><i class="fas fa-box"></i> 产品管理</h2>
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>产品名称</th>
                                    <th>分类</th>
                                    <th>描述</th>
                                    <th>价格</th>
                                    <th>状态</th>
                                </tr>
                            </thead>
                            <tbody>
                                {products_html}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/admin/inquiries')
def admin_inquiries():
    if not session.get('admin_logged_in'):
        return redirect('/admin')
    
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inquiries ORDER BY created_at DESC')
    inquiries = cursor.fetchall()
    conn.close()
    
    inquiries_html = ""
    for inquiry in inquiries:
        inquiries_html += f"""
        <tr>
            <td>{inquiry[0]}</td>
            <td>{inquiry[1]}</td>
            <td>{inquiry[2]}</td>
            <td>{inquiry[3] or ''}</td>
            <td>{inquiry[4] or ''}</td>
            <td>{inquiry[5][:50]}...</td>
            <td><span class="badge bg-primary">{inquiry[6]}</span></td>
            <td>{inquiry[7]}</td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>询盘管理</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container-fluid">
            <div class="row">
                <div class="col-md-2 bg-dark text-white p-3" style="min-height: 100vh;">
                    <h5><i class="fas fa-tv"></i> LED管理系统</h5>
                    <hr>
                    <ul class="nav flex-column">
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/dashboard"><i class="fas fa-tachometer-alt"></i> 仪表板</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/products"><i class="fas fa-box"></i> 产品管理</a></li>
                        <li class="nav-item"><a class="nav-link text-white active" href="/admin/inquiries"><i class="fas fa-envelope"></i> 询盘管理</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/news"><i class="fas fa-newspaper"></i> 新闻管理</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/api-test"><i class="fas fa-code"></i> API测试</a></li>
                        <li class="nav-item"><hr></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/"><i class="fas fa-globe"></i> 查看网站</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/logout"><i class="fas fa-sign-out-alt"></i> 退出登录</a></li>
                    </ul>
                </div>
                <div class="col-md-10 p-4">
                    <h2><i class="fas fa-envelope"></i> 询盘管理</h2>
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>姓名</th>
                                    <th>邮箱</th>
                                    <th>电话</th>
                                    <th>公司</th>
                                    <th>消息</th>
                                    <th>状态</th>
                                    <th>创建时间</th>
                                </tr>
                            </thead>
                            <tbody>
                                {inquiries_html}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/admin/news')
def admin_news():
    if not session.get('admin_logged_in'):
        return redirect('/admin')
    
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM news ORDER BY created_at DESC')
    news_list = cursor.fetchall()
    conn.close()
    
    news_html = ""
    for news in news_list:
        news_html += f"""
        <tr>
            <td>{news[0]}</td>
            <td>{news[1]}</td>
            <td>{news[2][:100]}...</td>
            <td>{news[3]}</td>
            <td><span class="badge bg-success">{news[4]}</span></td>
            <td>{news[5]}</td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>新闻管理</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container-fluid">
            <div class="row">
                <div class="col-md-2 bg-dark text-white p-3" style="min-height: 100vh;">
                    <h5><i class="fas fa-tv"></i> LED管理系统</h5>
                    <hr>
                    <ul class="nav flex-column">
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/dashboard"><i class="fas fa-tachometer-alt"></i> 仪表板</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/products"><i class="fas fa-box"></i> 产品管理</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/inquiries"><i class="fas fa-envelope"></i> 询盘管理</a></li>
                        <li class="nav-item"><a class="nav-link text-white active" href="/admin/news"><i class="fas fa-newspaper"></i> 新闻管理</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/api-test"><i class="fas fa-code"></i> API测试</a></li>
                        <li class="nav-item"><hr></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/"><i class="fas fa-globe"></i> 查看网站</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/logout"><i class="fas fa-sign-out-alt"></i> 退出登录</a></li>
                    </ul>
                </div>
                <div class="col-md-10 p-4">
                    <h2><i class="fas fa-newspaper"></i> 新闻管理</h2>
                    <div class="table-responsive">
                        <table class="table table-striped">
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
                </div>
            </div>
        </div>
    </body>
    </html>
    """

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
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .test-result { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px; margin: 10px 0; }
            .success { border-color: #28a745; background-color: #d4edda; }
            .error { border-color: #dc3545; background-color: #f8d7da; }
            pre { background: #f8f9fa; padding: 10px; border-radius: 5px; max-height: 300px; overflow-y: auto; }
        </style>
    </head>
    <body>
        <div class="container-fluid">
            <div class="row">
                <div class="col-md-2 bg-dark text-white p-3" style="min-height: 100vh;">
                    <h5><i class="fas fa-tv"></i> LED管理系统</h5>
                    <hr>
                    <ul class="nav flex-column">
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/dashboard"><i class="fas fa-tachometer-alt"></i> 仪表板</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/products"><i class="fas fa-box"></i> 产品管理</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/inquiries"><i class="fas fa-envelope"></i> 询盘管理</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/news"><i class="fas fa-newspaper"></i> 新闻管理</a></li>
                        <li class="nav-item"><a class="nav-link text-white active" href="/admin/api-test"><i class="fas fa-code"></i> API测试</a></li>
                        <li class="nav-item"><hr></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/"><i class="fas fa-globe"></i> 查看网站</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/admin/logout"><i class="fas fa-sign-out-alt"></i> 退出登录</a></li>
                    </ul>
                </div>
                <div class="col-md-10 p-4">
                    <h2><i class="fas fa-code"></i> API测试中心</h2>
                    
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5>🔗 连接状态检测</h5>
                        </div>
                        <div class="card-body">
                            <button class="btn btn-primary" onclick="testConnection()">测试连接状态</button>
                            <div id="connectionResult" class="test-result" style="display:none;"></div>
                        </div>
                    </div>
                    
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5>📦 本地API测试</h5>
                        </div>
                        <div class="card-body">
                            <button class="btn btn-success me-2" onclick="testLocalAPI('products')">测试本地产品</button>
                            <button class="btn btn-success me-2" onclick="testLocalAPI('news')">测试本地新闻</button>
                            <button class="btn btn-success me-2" onclick="testLocalAPI('stats')">测试本地统计</button>
                            <div id="localResult" class="test-result" style="display:none;"></div>
                        </div>
                    </div>
                    
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5>☁️ Supabase云数据库测试</h5>
                        </div>
                        <div class="card-body">
                            <button class="btn btn-info me-2" onclick="testSupabase('products')">测试云产品</button>
                            <button class="btn btn-info me-2" onclick="testSupabase('news')">测试云新闻</button>
                            <button class="btn btn-info me-2" onclick="testSupabase('inquiries')">测试云询盘</button>
                            <div id="supabaseResult" class="test-result" style="display:none;"></div>
                        </div>
                    </div>
                    
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5>📝 表单提交测试</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-3">
                                    <input type="text" class="form-control" id="testName" placeholder="姓名">
                                </div>
                                <div class="col-md-3">
                                    <input type="email" class="form-control" id="testEmail" placeholder="邮箱">
                                </div>
                                <div class="col-md-3">
                                    <input type="text" class="form-control" id="testPhone" placeholder="电话">
                                </div>
                                <div class="col-md-3">
                                    <textarea class="form-control" id="testMessage" placeholder="留言内容"></textarea>
                                </div>
                            </div>
                            <div class="mt-3">
                                <button class="btn btn-warning me-2" onclick="submitTestForm('local')">提交到本地</button>
                                <button class="btn btn-warning me-2" onclick="submitTestForm('supabase')">提交到Supabase</button>
                            </div>
                            <div id="formResult" class="test-result" style="display:none;"></div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h5>📊 系统信息</h5>
                        </div>
                        <div class="card-body">
                            <button class="btn btn-secondary" onclick="getSystemInfo()">获取系统信息</button>
                            <div id="systemResult" class="test-result" style="display:none;"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
        function showResult(elementId, content, isSuccess = true) {
            const element = document.getElementById(elementId);
            element.style.display = 'block';
            element.className = isSuccess ? 'test-result success' : 'test-result error';
            element.innerHTML = content;
        }
        
        function testConnection() {
            showResult('connectionResult', '<i class="fas fa-spinner fa-spin"></i> 检测中...', true);
            
            fetch('/api/health')
                .then(response => response.json())
                .then(data => {
                    showResult('connectionResult', 
                        `<i class="fas fa-check-circle text-success"></i> <strong>连接成功!</strong><br>
                        <pre>${JSON.stringify(data, null, 2)}</pre>`, true);
                })
                .catch(error => {
                    showResult('connectionResult', 
                        `<i class="fas fa-times-circle text-danger"></i> <strong>连接失败:</strong> ${error.message}`, false);
                });
        }
        
        function testLocalAPI(endpoint) {
            showResult('localResult', '<i class="fas fa-spinner fa-spin"></i> 测试中...', true);
            
            fetch(`/api/${endpoint}`)
                .then(response => response.json())
                .then(data => {
                    showResult('localResult', 
                        `<i class="fas fa-check-circle text-success"></i> <strong>本地API测试成功 (${endpoint}):</strong><br>
                        <pre>${JSON.stringify(data, null, 2)}</pre>`, true);
                })
                .catch(error => {
                    showResult('localResult', 
                        `<i class="fas fa-times-circle text-danger"></i> <strong>本地API测试失败:</strong> ${error.message}`, false);
                });
        }
        
        function testSupabase(endpoint) {
            showResult('supabaseResult', '<i class="fas fa-spinner fa-spin"></i> 测试Supabase...', true);
            showResult('supabaseResult', 
                `<i class="fas fa-info-circle text-info"></i> <strong>Supabase测试:</strong><br>
                Supabase集成需要在前端页面中测试。请访问主网站查看Supabase功能。<br>
                <strong>Supabase项目:</strong> https://jirudzbqcxviytcmxegf.supabase.co`, true);
        }
        
        function submitTestForm(target) {
            const name = document.getElementById('testName').value;
            const email = document.getElementById('testEmail').value;
            const phone = document.getElementById('testPhone').value;
            const message = document.getElementById('testMessage').value;
            
            if (!name || !email || !message) {
                showResult('formResult', 
                    `<i class="fas fa-exclamation-triangle text-warning"></i> <strong>请填写必要字段:</strong> 姓名、邮箱、留言`, false);
                return;
            }
            
            showResult('formResult', '<i class="fas fa-spinner fa-spin"></i> 提交中...', true);
            
            const formData = { name, email, phone, message };
            
            fetch('/api/contact', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                showResult('formResult', 
                    `<i class="fas fa-check-circle text-success"></i> <strong>表单提交成功 (${target}):</strong><br>
                    <pre>${JSON.stringify(data, null, 2)}</pre>`, true);
                // 清空表单
                document.getElementById('testName').value = '';
                document.getElementById('testEmail').value = '';
                document.getElementById('testPhone').value = '';
                document.getElementById('testMessage').value = '';
            })
            .catch(error => {
                showResult('formResult', 
                    `<i class="fas fa-times-circle text-danger"></i> <strong>表单提交失败:</strong> ${error.message}`, false);
            });
        }
        
        function getSystemInfo() {
            showResult('systemResult', '<i class="fas fa-spinner fa-spin"></i> 获取系统信息...', true);
            
            const systemInfo = {
                database: 'led_admin.db',
                server: 'Flask Development Server',
                port: '5002',
                supabase: 'https://jirudzbqcxviytcmxegf.supabase.co',
                status: 'Running',
                timestamp: new Date().toISOString()
            };
            
            showResult('systemResult', 
                `<i class="fas fa-info-circle text-info"></i> <strong>系统信息:</strong><br>
                <pre>${JSON.stringify(systemInfo, null, 2)}</pre>`, true);
        }
        </script>
    </body>
    </html>
    '''

# API路由
@app.route('/api/products')
def api_products():
    try:
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
        
        return jsonify({
            'status': 'success',
            'data': products_list
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/contact', methods=['POST'])
def api_contact():
    try:
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
        
        return jsonify({
            'status': 'success', 
            'message': '询盘提交成功'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/news')
def api_news():
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM news WHERE status = "published" ORDER BY created_at DESC LIMIT 10')
        news_data = cursor.fetchall()
        conn.close()
        
        news_list = []
        for news in news_data:
            news_list.append({
                'id': news[0],
                'title': news[1],
                'content': news[2],
                'author': news[3],
                'status': news[4],
                'created_at': news[5]
            })
        
        return jsonify({
            'status': 'success',
            'data': news_list
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/products/featured')
def api_featured_products():
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products ORDER BY created_at DESC LIMIT 4')
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
                'image': product[5] or f'/assets/products/product-{product[0]}.jpg'
            })
        
        return jsonify({
            'status': 'success',
            'data': products_list
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/stats')
def api_stats():
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM products')
        products_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM inquiries')
        inquiries_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM news WHERE status = "published"')
        news_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users')
        users_count = cursor.fetchone()[0]
        
        conn.close()
        
        stats_data = {
            'products': products_count,
            'inquiries': inquiries_count,
            'news': news_count,
            'users': users_count,
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'data': stats_data
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/news/latest')
def api_latest_news():
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM news WHERE status = "published" ORDER BY created_at DESC LIMIT 3')
        news_data = cursor.fetchall()
        conn.close()
        
        news_list = []
        for news in news_data:
            news_list.append({
                'id': news[0],
                'title': news[1],
                'content': news[2],
                'summary': news[2][:100] + '...' if len(news[2]) > 100 else news[2],
                'author': news[3],
                'created_at': news[5],
                'image': f'/assets/news/news-thumb-{news[0]}.jpg'
            })
        
        return jsonify({
            'status': 'success',
            'data': news_list
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/health')
def api_health():
    return jsonify({
        'status': 'success',
        'message': 'API is running',
        'database': 'led_admin.db',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, port=5002)
