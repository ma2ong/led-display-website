#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的前端文件服务器
用于提供LED网站的静态文件服务
"""

import http.server
import socketserver
import os
import sys
import webbrowser
from pathlib import Path

# 设置端口
PORT = 8000

# 获取当前目录
current_dir = Path(__file__).parent

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(current_dir), **kwargs)
    
    def end_headers(self):
        # 添加CORS头部，允许跨域访问
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def start_server():
    """启动前端文件服务器"""
    try:
        # 检查端口是否被占用
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"🌐 前端文件服务器启动成功!")
            print(f"📍 服务地址: http://localhost:{PORT}")
            print(f"📁 服务目录: {current_dir}")
            print(f"🏠 首页地址: http://localhost:{PORT}/index.html")
            print(f"📺 产品页面: http://localhost:{PORT}/products.html")
            print(f"📞 联系我们: http://localhost:{PORT}/contact.html")
            print(f"📰 新闻资讯: http://localhost:{PORT}/news.html")
            print(f"💡 解决方案: http://localhost:{PORT}/solutions.html")
            print(f"💼 成功案例: http://localhost:{PORT}/cases.html")
            print(f"🛟 技术支持: http://localhost:{PORT}/support.html")
            print(f"ℹ️ 关于我们: http://localhost:{PORT}/about.html")
            print("\n按 Ctrl+C 停止服务器")
            
            # 自动打开浏览器
            try:
                webbrowser.open(f'http://localhost:{PORT}/index.html')
            except:
                pass
            
            # 启动服务器
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 10048:  # Windows: 端口被占用
            print(f"❌ 端口 {PORT} 已被占用，请先关闭其他服务或更改端口")
        elif e.errno == 48:   # macOS/Linux: 端口被占用
            print(f"❌ 端口 {PORT} 已被占用，请先关闭其他服务或更改端口")
        else:
            print(f"❌ 启动服务器失败: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        sys.exit(0)

if __name__ == "__main__":
    start_server()