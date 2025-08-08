import sqlite3
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# 数据库路径
DB_PATH = 'admin_system.db'

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/products', methods=['GET'])
def get_products():
    """获取所有产品数据"""
    try:
        conn = get_db_connection()
        products = conn.execute('SELECT * FROM products_new ORDER BY id DESC').fetchall()
        conn.close()
        
        products_list = []
        for product in products:
            products_list.append({
                'id': product['id'],
                'name': product['name'],
                'category': product['category'],
                'price': product['price'],
                'description': product['description'],
                'image_url': product['image_url'],
                'specifications': product['specifications'],
                'status': product['status'],
                'created_at': product['created_at']
            })
        
        return jsonify({
            'success': True,
            'data': products_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/news', methods=['GET'])
def get_news():
    """获取所有新闻数据"""
    try:
        conn = get_db_connection()
        news = conn.execute('SELECT * FROM news_new ORDER BY id DESC').fetchall()
        conn.close()
        
        news_list = []
        for item in news:
            news_list.append({
                'id': item['id'],
                'title': item['title'],
                'content': item['content'],
                'summary': item['summary'],
                'image_url': item['image_url'],
                'status': item['status'],
                'created_at': item['created_at']
            })
        
        return jsonify({
            'success': True,
            'data': news_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/page-content/<page_name>', methods=['GET'])
def get_page_content(page_name):
    """获取页面内容"""
    try:
        conn = get_db_connection()
        content = conn.execute(
            'SELECT * FROM page_contents WHERE page_name = ?', 
            (page_name,)
        ).fetchone()
        conn.close()
        
        if content:
            return jsonify({
                'success': True,
                'data': {
                    'page_name': content['page_name'],
                    'content': json.loads(content['content']) if content['content'] else {},
                    'updated_at': content['updated_at']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Page content not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/inquiries', methods=['GET'])
def get_inquiries():
    """获取所有询盘数据"""
    try:
        conn = get_db_connection()
        inquiries = conn.execute('SELECT * FROM inquiries_new ORDER BY id DESC').fetchall()
        conn.close()
        
        inquiries_list = []
        for inquiry in inquiries:
            inquiries_list.append({
                'id': inquiry['id'],
                'name': inquiry['name'],
                'email': inquiry['email'],
                'phone': inquiry['phone'],
                'company': inquiry['company'],
                'message': inquiry['message'],
                'status': inquiry['status'],
                'created_at': inquiry['created_at']
            })
        
        return jsonify({
            'success': True,
            'data': inquiries_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5005, host='0.0.0.0')