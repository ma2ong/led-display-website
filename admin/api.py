#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED Display Admin API
提供前端网站和后台管理系统之间的API接口
"""

from flask import Blueprint, request, jsonify, current_app
import sqlite3
import json
import os
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect('led_admin.db')
    conn.row_factory = sqlite3.Row
    return conn

@api_bp.route('/products', methods=['GET'])
def get_products():
    """获取产品列表 - 供前端网站使用"""
    try:
        conn = get_db_connection()
        products = conn.execute('''
            SELECT * FROM products WHERE status = 'active'
            ORDER BY created_at DESC
        ''').fetchall()
        conn.close()
        
        products_list = []
        for product in products:
            products_list.append({
                'id': product['id'],
                'name_en': product['name_en'],
                'name_zh': product['name_zh'],
                'category': product['category'],
                'description_en': product['description_en'],
                'description_zh': product['description_zh'],
                'specifications': product['specifications'],
                'features': product['features'],
                'images': product['images'],
                'price': product['price'],
                'created_at': product['created_at']
            })
        
        # 同时更新前端数据文件
        update_frontend_data()
        
        return jsonify({
            'status': 'success',
            'count': len(products_list),
            'products': products_list
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/contact', methods=['POST'])
def submit_contact():
    """接收联系表单提交"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        # 验证必填字段
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO inquiries (name, email, company, phone, product_interest, message, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'new', CURRENT_TIMESTAMP)
        ''', (
            data.get('name'),
            data.get('email'),
            data.get('company', ''),
            data.get('phone', ''),
            data.get('product', ''),
            data.get('message')
        ))
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Thank you for your inquiry! We will contact you soon.'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to submit inquiry. Please try again.'
        }), 500

@api_bp.route('/quote', methods=['POST'])
def submit_quote():
    """接收报价请求提交"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        # 验证必填字段
        required_fields = ['name', 'email', 'company']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO quotes (
                name, email, company, product_type, display_size, quantity,
                requirements, timeline, budget, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', CURRENT_TIMESTAMP)
        ''', (
            data.get('name'),
            data.get('email'),
            data.get('company'),
            data.get('product_type', ''),
            data.get('display_size', ''),
            int(data.get('quantity', 0)) if data.get('quantity') else None,
            data.get('requirements', ''),
            data.get('timeline', ''),
            data.get('budget', '')
        ))
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Thank you for your quote request! We will prepare a customized quote for you.'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to submit quote request. Please try again.'
        }), 500

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """获取统计数据"""
    try:
        conn = get_db_connection()
        
        stats = {
            'products': conn.execute('SELECT COUNT(*) FROM products WHERE status = "active"').fetchone()[0],
            'inquiries': conn.execute('SELECT COUNT(*) FROM inquiries').fetchone()[0],
            'new_inquiries': conn.execute('SELECT COUNT(*) FROM inquiries WHERE status = "new"').fetchone()[0],
            'quotes': conn.execute('SELECT COUNT(*) FROM quotes').fetchone()[0],
            'pending_quotes': conn.execute('SELECT COUNT(*) FROM quotes WHERE status = "pending"').fetchone()[0]
        }
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def update_frontend_data():
    """更新前端数据文件"""
    try:
        conn = get_db_connection()
        
        # 获取产品数据
        products = conn.execute('''
            SELECT * FROM products WHERE status = 'active'
            ORDER BY created_at DESC
        ''').fetchall()
        
        # 获取公司设置
        settings = conn.execute('SELECT key, value FROM settings').fetchall()
        settings_dict = {setting['key']: setting['value'] for setting in settings}
        
        conn.close()
        
        # 构建前端数据结构
        frontend_data = {
            'company': {
                'name_en': settings_dict.get('site_title_en', 'Lianjin LED Display'),
                'name_zh': settings_dict.get('site_title_zh', '联锦LED显示屏'),
                'phone': settings_dict.get('company_phone', '+86-755-1234-5678'),
                'email': settings_dict.get('company_email', 'info@lianjinled.com'),
                'address_en': settings_dict.get('company_address_en', 'Shenzhen, China'),
                'address_zh': settings_dict.get('company_address_zh', '中国深圳')
            },
            'products': []
        }
        
        # 添加产品数据
        for product in products:
            frontend_data['products'].append({
                'id': product['id'],
                'name_en': product['name_en'],
                'name_zh': product['name_zh'],
                'category': product['category'],
                'description_en': product['description_en'],
                'description_zh': product['description_zh'],
                'specifications': product['specifications'],
                'features': product['features'],
                'images': product['images'],
                'price': product['price']
            })
        
        # 确保data目录存在
        data_dir = os.path.join('..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # 写入前端数据文件
        data_file = os.path.join(data_dir, 'content.json')
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(frontend_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Frontend data updated: {data_file}")
        
    except Exception as e:
        print(f"❌ Failed to update frontend data: {e}")

@api_bp.route('/sync', methods=['POST'])
def sync_data():
    """手动同步数据到前端"""
    try:
        update_frontend_data()
        return jsonify({
            'status': 'success',
            'message': 'Data synchronized successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# 错误处理
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'API endpoint not found'
    }), 404

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500