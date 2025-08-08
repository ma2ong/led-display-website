#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加测试产品到后端管理系统
"""

import sqlite3
from datetime import datetime

def add_test_products():
    """添加测试产品数据"""
    conn = sqlite3.connect('final_admin.db')
    cursor = conn.cursor()
    
    # 清空现有产品（可选）
    cursor.execute('DELETE FROM products_new')
    
    # 添加测试产品
    test_products = [
        {
            'name': 'P2.5室内LED显示屏',
            'category': 'Indoor',
            'description': '高分辨率室内LED显示屏，适用于会议室、展厅等场所',
            'specifications': '像素间距: 2.5mm, 亮度: 800cd/m², 刷新率: 3840Hz',
            'features': '高刷新率, 广视角, 低功耗',
            'images': '/images/products/p25-indoor.jpg',
            'price': 2500.0
        },
        {
            'name': 'P4户外LED显示屏',
            'category': 'Outdoor',
            'description': '防水防尘户外LED显示屏，适用于广告牌、体育场等',
            'specifications': '像素间距: 4mm, 亮度: 6500cd/m², 防护等级: IP65',
            'features': '高亮度, 防水防尘, 耐候性强',
            'images': '/images/products/p4-outdoor.jpg',
            'price': 1800.0
        },
        {
            'name': '租赁LED显示屏',
            'category': 'Rental',
            'description': '轻便易装的租赁LED显示屏，适用于演出、会议等临时活动',
            'specifications': '像素间距: 3.91mm, 重量: 7kg/㎡, 快速安装',
            'features': '轻薄设计, 快速安装, 高精度',
            'images': '/images/products/rental-led.jpg',
            'price': 3200.0
        },
        {
            'name': '透明LED显示屏',
            'category': 'Transparent',
            'description': '高透明度LED显示屏，适用于玻璃幕墙、橱窗展示',
            'specifications': '透明度: 85%, 像素间距: 10mm, 通透性好',
            'features': '高透明度, 节能环保, 美观大方',
            'images': '/images/products/transparent-led.jpg',
            'price': 4500.0
        },
        {
            'name': '创意LED显示屏',
            'category': 'Creative',
            'description': '可定制形状的创意LED显示屏，适用于艺术装置、特殊场景',
            'specifications': '可定制尺寸, 柔性设计, 多种形状',
            'features': '创意设计, 柔性弯曲, 个性定制',
            'images': '/images/products/creative-led.jpg',
            'price': 5800.0
        }
    ]
    
    # 插入测试产品
    for product in test_products:
        cursor.execute('''
            INSERT INTO products_new (name, category, description, specifications, features, images, price, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''', (
            product['name'],
            product['category'],
            product['description'],
            product['specifications'],
            product['features'],
            product['images'],
            product['price']
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ 成功添加了 {len(test_products)} 个测试产品到后端管理系统")
    print("现在您可以在前端网站上看到这些产品了！")

if __name__ == '__main__':
    add_test_products()