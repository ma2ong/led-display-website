#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple HTTP Server with API for LED Display Website
Serves static files and provides basic API endpoints
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

class LEDDisplayHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='.', **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        # API status endpoint
        if parsed_path.path == '/api/status':
            self.send_json_response({
                'status': 'success',
                'message': 'LED Display Website API is running',
                'timestamp': datetime.now().isoformat()
            })
            return
        
        # API products endpoint
        elif parsed_path.path == '/api/products':
            try:
                products = self.get_products()
                self.send_json_response({
                    'status': 'success',
                    'products': products
                })
            except Exception as e:
                self.send_json_response({
                    'status': 'error',
                    'message': str(e)
                }, 500)
            return
        
        # Admin panel - simple HTML response
        elif parsed_path.path == '/admin' or parsed_path.path == '/admin/':
            self.send_admin_panel()
            return
        
        # Default to serving static files
        else:
            # Handle root path
            if parsed_path.path == '/':
                self.path = '/index.html'
            
            # Serve static files
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        # Contact API
        if parsed_path.path == '/api/contact':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # Save to database
                self.save_inquiry(data)
                
                self.send_json_response({
                    'status': 'success',
                    'message': 'Thank you for your inquiry!'
                })
            except Exception as e:
                self.send_json_response({
                    'status': 'error',
                    'message': str(e)
                }, 500)
            return
        
        # Quote API
        elif parsed_path.path == '/api/quote':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # Save to database
                self.save_quote(data)
                
                self.send_json_response({
                    'status': 'success',
                    'message': 'Quote request submitted successfully!'
                })
            except Exception as e:
                self.send_json_response({
                    'status': 'error',
                    'message': str(e)
                }, 500)
            return
        
        # Default 404
        self.send_error(404)
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def send_admin_panel(self):
        """Send simple admin panel HTML"""
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LED Display Admin Panel</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }
        .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; margin-bottom: 5px; }
        .stat-label { font-size: 0.9em; opacity: 0.9; }
        .section { margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
        .api-endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
        .method { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; margin-right: 10px; }
        .get { background: #28a745; color: white; }
        .post { background: #007bff; color: white; }
        .login-info { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .btn { display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }
        .btn:hover { background: #0056b3; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: bold; }
        .status-new { color: #28a745; font-weight: bold; }
        .status-pending { color: #ffc107; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 LED Display Admin Panel</h1>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="products-count">6</div>
                <div class="stat-label">Active Products</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="inquiries-count">0</div>
                <div class="stat-label">New Inquiries</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="quotes-count">0</div>
                <div class="stat-label">Pending Quotes</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">✅</div>
                <div class="stat-label">System Status</div>
            </div>
        </div>
        
        <div class="login-info">
            <strong>🔐 Admin Access:</strong> This is a simplified admin panel. For full admin features, use the Flask-based admin system.
            <br><strong>Default Login:</strong> admin / admin123
        </div>
        
        <div class="section">
            <h2>📡 API Endpoints</h2>
            <div class="api-endpoint">
                <span class="method get">GET</span>
                <strong>/api/status</strong> - Check API status
            </div>
            <div class="api-endpoint">
                <span class="method get">GET</span>
                <strong>/api/products</strong> - Get all active products
            </div>
            <div class="api-endpoint">
                <span class="method post">POST</span>
                <strong>/api/contact</strong> - Submit contact form
            </div>
            <div class="api-endpoint">
                <span class="method post">POST</span>
                <strong>/api/quote</strong> - Submit quote request
            </div>
        </div>
        
        <div class="section">
            <h2>🌐 Website Pages</h2>
            <a href="/" class="btn">Homepage</a>
            <a href="/products.html" class="btn">Products</a>
            <a href="/about.html" class="btn">About</a>
            <a href="/contact.html" class="btn">Contact</a>
            <a href="/solutions.html" class="btn">Solutions</a>
            <a href="/cases.html" class="btn">Cases</a>
            <a href="/news.html" class="btn">News</a>
            <a href="/support.html" class="btn">Support</a>
        </div>
        
        <div class="section">
            <h2>📊 Recent Activity</h2>
            <p>✅ Database initialized successfully</p>
            <p>✅ 6 sample products loaded</p>
            <p>✅ API endpoints active</p>
            <p>✅ Frontend website accessible</p>
            <p>✅ Contact forms connected to backend</p>
        </div>
        
        <div class="section">
            <h2>🔗 Quick Links</h2>
            <a href="/api/status" class="btn" target="_blank">API Status</a>
            <a href="/api/products" class="btn" target="_blank">Products API</a>
            <a href="/" class="btn">Back to Website</a>
        </div>
    </div>
    
    <script>
        // Load stats from API
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                console.log('API Status:', data);
            })
            .catch(error => {
                console.error('API Error:', error);
            });
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def get_products(self):
        """Get products from database"""
        try:
            conn = sqlite3.connect('led_simple.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM products WHERE status = "active" ORDER BY created_at DESC')
            products = cursor.fetchall()
            conn.close()
            
            return [dict(product) for product in products]
        except Exception as e:
            print(f"Database error: {e}")
            return []
    
    def save_inquiry(self, data):
        """Save inquiry to database"""
        conn = sqlite3.connect('led_simple.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO inquiries (name, email, company, phone, product_interest, message, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('name', ''),
            data.get('email', ''),
            data.get('company', ''),
            data.get('phone', ''),
            data.get('product', ''),
            data.get('message', ''),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def save_quote(self, data):
        """Save quote request to database"""
        conn = sqlite3.connect('led_simple.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO quotes (name, email, company, product_type, display_size, 
                              quantity, requirements, timeline, budget, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('name', ''),
            data.get('email', ''),
            data.get('company', ''),
            data.get('product_type', ''),
            data.get('display_size', ''),
            data.get('quantity', 0),
            data.get('requirements', ''),
            data.get('timeline', ''),
            data.get('budget', ''),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()

def init_simple_db():
    """Initialize simple database"""
    conn = sqlite3.connect('led_simple.db')
    cursor = conn.cursor()
    
    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_en TEXT NOT NULL,
            name_zh TEXT NOT NULL,
            category TEXT NOT NULL,
            description_en TEXT,
            description_zh TEXT,
            specifications TEXT,
            features TEXT,
            images TEXT,
            price REAL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Inquiries table
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Quotes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            company TEXT NOT NULL,
            product_type TEXT,
            display_size TEXT,
            quantity INTEGER,
            requirements TEXT,
            timeline TEXT,
            budget TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample products if none exist
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ('Fine Pitch LED Display', '小间距LED显示屏', 'fine-pitch', 
             'Ultra-high resolution displays with pixel pitches from P0.9 to P1.56, perfect for control rooms, broadcast studios, and corporate environments.',
             '像素间距从P0.9到P1.56的超高分辨率显示屏，完美适用于控制室、广播演播室和企业环境。',
             'Pixel Pitch: P0.9-P1.56, Resolution: 4K/8K, Brightness: 600-1200 nits, Refresh Rate: 3840Hz',
             '4K/8K Resolution, Seamless Splicing, High Refresh Rate',
             'assets/products/fine-pitch-led.jpg', 'active'),
            
            ('Outdoor LED Display', '户外LED显示屏', 'outdoor',
             'Weather-resistant displays for outdoor advertising and information with high brightness and energy efficiency.',
             '适用于户外广告和信息显示的防风雨显示屏，具有高亮度和节能特性。',
             'Pixel Pitch: P3-P10, Brightness: 5000-8000 nits, IP Rating: IP65, Operating Temperature: -40°C to +60°C',
             'IP65 Waterproof, High Brightness, Energy Efficient',
             'assets/products/outdoor-led.jpg', 'active'),
            
            ('Indoor LED Display', '室内LED显示屏', 'indoor',
             'High-quality displays for indoor commercial and corporate applications with full color display and easy installation.',
             '适用于室内商业和企业应用的高质量显示屏，具有全彩显示和易于安装的特点。',
             'Pixel Pitch: P1.25-P4, Brightness: 800-1500 nits, Refresh Rate: 1920-3840Hz, Color Temperature: 3200K-9300K',
             'Full Color Display, Easy Installation, Low Maintenance',
             'assets/products/indoor-led.jpg', 'active'),
            
            ('Transparent LED Display', '透明LED显示屏', 'transparent',
             'Innovative transparent displays that blend seamlessly with architecture while delivering stunning visual impact.',
             '与建筑完美融合的创新透明显示屏，同时提供令人惊叹的视觉冲击。',
             'Transparency: 70-90%, Pixel Pitch: P3.91-P7.81, Brightness: 4000-6000 nits, Weight: 12kg/m²',
             '90% Transparency, Lightweight Design, Creative Applications',
             'assets/products/transparent-led.jpg', 'active'),
            
            ('Creative LED Display', '创意LED显示屏', 'creative',
             'Custom-shaped displays for unique architectural and artistic applications with flexible design options.',
             '适用于独特建筑和艺术应用的定制形状显示屏，具有灵活的设计选项。',
             'Shape: Customizable, Pixel Pitch: P1.25-P10, Curve Radius: R≥500mm, Installation: Flexible',
             'Custom Shapes, Flexible Design, Artistic Integration',
             'assets/products/creative-led.jpg', 'active'),
            
            ('Rental LED Display', '租赁LED显示屏', 'rental',
             'Portable and quick-setup displays for events and temporary installations with lightweight and durable design.',
             '适用于活动和临时安装的便携式快速安装显示屏，具有轻量化和耐用的设计。',
             'Pixel Pitch: P2.6-P4.81, Weight: 6-8kg/panel, Setup Time: <30min, Connection: Quick Lock',
             'Quick Setup, Lightweight, Durable Design',
             'assets/products/rental-led.jpg', 'active')
        ]
        
        for product in sample_products:
            cursor.execute('''
                INSERT INTO products (
                    name_en, name_zh, category, description_en, description_zh,
                    specifications, features, images, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', product)
    
    conn.commit()
    conn.close()

def start_server():
    """Start the HTTP server"""
    port = int(os.environ.get('PORT', 8080))
    
    print("🚀 LED Display Website - Simple Server Starting...")
    print("=" * 60)
    print(f"🌐 Website: http://localhost:{port}")
    print(f"🔧 Admin Panel: http://localhost:{port}/admin")
    print(f"📡 API Status: http://localhost:{port}/api/status")
    print(f"📊 Products API: http://localhost:{port}/api/products")
    print("=" * 60)
    
    # Initialize database
    init_simple_db()
    print("✅ Database initialized with sample data")
    
    # Start server
    server = HTTPServer(('0.0.0.0', port), LEDDisplayHandler)
    print(f"✅ Server started on port {port}")
    print("⏳ Server running... Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.server_close()

if __name__ == '__main__':
    start_server()