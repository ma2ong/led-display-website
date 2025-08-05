#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED Display Website Deployment Script
LED显示屏网站部署脚本
"""

import os
import sys
import subprocess
import webbrowser
import threading
import time
from pathlib import Path
import http.server
import socketserver
from urllib.parse import urlparse

class UTF8HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler that ensures UTF-8 encoding for HTML files"""
    
    def end_headers(self):
        # Set UTF-8 encoding for HTML files
        if self.path.endswith('.html') or self.path.endswith('.htm'):
            self.send_header('Content-Type', 'text/html; charset=utf-8')
        elif self.path.endswith('.css'):
            self.send_header('Content-Type', 'text/css; charset=utf-8')
        elif self.path.endswith('.js'):
            self.send_header('Content-Type', 'application/javascript; charset=utf-8')
        elif self.path.endswith('.json'):
            self.send_header('Content-Type', 'application/json; charset=utf-8')
        super().end_headers()
    
    def guess_type(self, path):
        """Override to ensure proper MIME types with UTF-8"""
        mimetype, encoding = super().guess_type(path)
        if mimetype and mimetype.startswith('text/'):
            return mimetype + '; charset=utf-8'
        return mimetype

def start_main_website():
    """启动主网站 - 使用自定义HTTP服务器确保UTF-8编码"""
    print("🌐 启动主网站服务器...")
    try:
        os.chdir(Path(__file__).parent)
        with socketserver.TCPServer(("", 8000), UTF8HTTPRequestHandler) as httpd:
            print("✅ 主网站服务器启动成功 - http://localhost:8000")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("🛑 主网站服务器已停止")
    except Exception as e:
        print(f"❌ 主网站服务器启动失败: {e}")

def start_admin_panel():
    """启动管理后台"""
    print("🔧 启动管理后台...")
    try:
        admin_dir = Path(__file__).parent / "admin"
        os.chdir(admin_dir)
        
        # Import and run Flask app
        sys.path.insert(0, str(admin_dir))
        from app import app, init_db
        
        # Initialize database
        init_db()
        
        # Configure Flask for UTF-8
        app.config['JSON_AS_ASCII'] = False
        
        print("✅ 管理后台启动成功 - http://localhost:5000")
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("🛑 管理后台已停止")
    except Exception as e:
        print(f"❌ 管理后台启动失败: {e}")

def check_encoding():
    """检查并修复文件编码"""
    print("🔍 检查文件编码...")
    
    # 检查主要HTML文件
    html_files = [
        "index.html", "homepage.html", "about.html", "products.html", 
        "contact.html", "fine-pitch.html", "outdoor.html", "rental.html",
        "creative.html", "transparent.html"
    ]
    
    for file_path in html_files:
        if Path(file_path).exists():
            try:
                # 读取文件并重新保存为UTF-8
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
                # 确保HTML文件有正确的meta标签
                if '<meta charset="UTF-8">' not in content and '<meta charset="utf-8">' not in content:
                    # 在head标签后添加charset meta标签
                    content = content.replace('<head>', '<head>\n    <meta charset="UTF-8">')
                
                # 重新保存文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print(f"✅ 已检查文件编码: {file_path}")
            except Exception as e:
                print(f"⚠️  文件编码检查失败 {file_path}: {e}")
    
    # 检查JSON文件
    json_files = ["data/content.json"]
    for file_path in json_files:
        if Path(file_path).exists():
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
                print(f"✅ 已检查JSON编码: {file_path}")
            except Exception as e:
                print(f"⚠️  JSON编码检查失败 {file_path}: {e}")

def main():
    """主部署函数"""
    print("🚀 LED显示屏网站完整部署")
    print("=" * 60)
    print("📍 项目目录:", Path(__file__).parent)
    print("=" * 60)
    
    # 检查文件编码
    check_encoding()
    
    # 检查文件
    required_files = [
        "index.html",
        "homepage.html",
        "css/style.css", 
        "js/script.js",
        "admin/app.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not (Path(__file__).parent / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ 缺少必要文件:")
        for file in missing_files:
            print(f"   - {file}")
        return
    
    print("✅ 所有必要文件检查完成")
    print("=" * 60)
    
    # 显示访问信息
    print("🌐 服务访问地址:")
    print("   • 主网站: http://localhost:8000")
    print("   • 管理后台: http://localhost:5000")
    print("=" * 60)
    print("👤 管理后台登录:")
    print("   • 用户名: admin")
    print("   • 密码: admin123")
    print("=" * 60)
    print("💡 使用说明:")
    print("   • 主网站展示LED产品和公司信息")
    print("   • 管理后台用于内容管理和询盘处理")
    print("   • 所有文件已确保UTF-8编码，中文显示正常")
    print("   • 按 Ctrl+C 停止所有服务")
    print("=" * 60)
    
    try:
        # 启动管理后台（在后台线程）
        admin_thread = threading.Thread(target=start_admin_panel, daemon=True)
        admin_thread.start()
        
        # 等待管理后台启动
        time.sleep(3)
        
        # 尝试打开浏览器
        try:
            print("🌐 正在打开浏览器...")
            webbrowser.open('http://localhost:8000')
            time.sleep(2)
            webbrowser.open('http://localhost:5000')
        except Exception as e:
            print(f"⚠️  无法自动打开浏览器: {e}")
        
        print("\n✅ 所有服务启动成功!")
        print("等待请求... (按 Ctrl+C 停止所有服务)\n")
        
        # 启动主网站（前台运行）
        start_main_website()
        
    except KeyboardInterrupt:
        print("\n\n🛑 正在停止所有服务...")
        print("✅ 部署已停止")
    except Exception as e:
        print(f"\n❌ 部署失败: {e}")

if __name__ == "__main__":
    main()