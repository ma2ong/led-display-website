#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED网站项目快速部署脚本
一键启动前端和后台管理系统
"""

import os
import sys
import time
import threading
import webbrowser
from pathlib import Path

def print_banner():
    """打印启动横幅"""
    print("=" * 60)
    print("🚀 LED网站项目 - 快速启动")
    print("=" * 60)
    print()

def start_frontend():
    """启动前端服务"""
    print("🌐 启动前端服务 (端口 8080)...")
    os.system("python simple_server.py")

def start_admin():
    """启动后台管理服务"""
    print("⚙️ 启动后台管理服务 (端口 5003)...")
    os.system("python admin/complete_chinese_admin.py")

def main():
    """主函数"""
    print_banner()
    
    print("🔍 检查项目文件...")
    
    # 检查必要文件
    required_files = [
        'simple_server.py',
        'admin/complete_chinese_admin.py',
        'index.html'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        sys.exit(1)
    
    print("✅ 项目文件检查完成")
    
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    
    print("\n🚀 正在启动服务...")
    
    # 启动前端服务
    frontend_thread = threading.Thread(target=start_frontend)
    frontend_thread.daemon = True
    frontend_thread.start()
    
    # 等待前端服务启动
    time.sleep(3)
    
    # 启动后台管理服务
    admin_thread = threading.Thread(target=start_admin)
    admin_thread.daemon = True
    admin_thread.start()
    
    # 等待后台服务启动
    time.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ LED网站项目启动成功!")
    print("=" * 60)
    print("🌐 前端网站: http://localhost:8080")
    print("⚙️ 后台管理: http://localhost:5003")
    print("👤 管理员账号: admin")
    print("🔑 管理员密码: admin123")
    print("=" * 60)
    print("💡 提示:")
    print("  - 在后台管理中点击'查看前端网站'可快速跳转")
    print("  - 所有修改会实时反映到前端页面")
    print("  - 按 Ctrl+C 停止所有服务")
    print("=" * 60)
    
    # 询问是否自动打开浏览器
    try:
        open_browser = input("\n是否自动打开浏览器? (y/n): ").strip().lower()
        if open_browser in ['y', 'yes', '是']:
            print("🌐 正在打开浏览器...")
            webbrowser.open('http://localhost:8080')
            time.sleep(1)
            webbrowser.open('http://localhost:5003')
    except KeyboardInterrupt:
        pass
    
    print("\n⏳ 服务运行中... 按 Ctrl+C 停止服务")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        print("👋 感谢使用LED网站项目!")
        sys.exit(0)

if __name__ == "__main__":
    main()