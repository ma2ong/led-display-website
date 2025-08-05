#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import threading
import subprocess
from pathlib import Path

def start_frontend():
    """启动前端服务"""
    print("🌐 启动前端服务 (端口 8080)...")
    os.system("python simple_server.py")

def start_admin():
    """启动后台管理服务"""
    print("⚙️ 启动后台管理服务 (端口 5003)...")
    os.system("python admin/complete_chinese_admin.py")

def main():
    print("🚀 LED网站项目启动中...")
    print("=" * 50)
    
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    
    # 启动前端服务
    frontend_thread = threading.Thread(target=start_frontend)
    frontend_thread.daemon = True
    frontend_thread.start()
    
    # 等待前端服务启动
    time.sleep(2)
    
    # 启动后台管理服务
    admin_thread = threading.Thread(target=start_admin)
    admin_thread.daemon = True
    admin_thread.start()
    
    print("✅ 服务启动完成!")
    print("🌐 前端网站: http://localhost:8080")
    print("⚙️ 后台管理: http://localhost:5003")
    print("👤 管理员账号: admin / admin123")
    print("=" * 50)
    print("按 Ctrl+C 停止服务")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        sys.exit(0)

if __name__ == "__main__":
    main()