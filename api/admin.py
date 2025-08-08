from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/api/admin/login', methods=['POST', 'OPTIONS'])
def admin_login():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        data = request.get_json()
        username = data.get('username', '')
        password = data.get('password', '')
        
        # Simple authentication
        if username == 'admin' and password == 'admin123':
            response = jsonify({
                'status': 'success',
                'message': '登录成功',
                'admin': {
                    'id': 1,
                    'username': 'admin',
                    'role': 'super_admin'
                }
            })
        else:
            response = jsonify({
                'status': 'error',
                'message': '用户名或密码错误'
            })
        
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        response = jsonify({
            'status': 'error',
            'message': f'登录失败: {str(e)}'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/api/admin/dashboard', methods=['GET', 'OPTIONS'])
def admin_dashboard():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    response = jsonify({
        'status': 'success',
        'stats': {
            'pages': 8,
            'products': 0,
            'inquiries': 0,
            'news': 0
        },
        'recent_inquiries': []
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/admin/products', methods=['GET', 'OPTIONS'])
def admin_products():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    response = jsonify({
        'status': 'success',
        'products': []
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/admin/inquiries', methods=['GET', 'OPTIONS'])
def admin_inquiries():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    response = jsonify({
        'status': 'success',
        'inquiries': []
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/admin/news', methods=['GET', 'OPTIONS'])
def admin_news():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    response = jsonify({
        'status': 'success',
        'news': []
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# For Vercel serverless deployment
if __name__ == '__main__':
    app.run(debug=True)