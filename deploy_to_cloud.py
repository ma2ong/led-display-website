#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
联进LED网站云端部署脚本
支持多种云平台一键部署
"""

import os
import sys
import json
import zipfile
import shutil
from pathlib import Path

def print_banner():
    """打印部署横幅"""
    print("=" * 60)
    print("🚀 联进LED网站 - 云端部署工具")
    print("=" * 60)
    print()

def create_static_package():
    """创建静态网站部署包"""
    print("📦 创建静态网站部署包...")
    
    # 创建静态部署目录
    static_dir = Path("static_deployment")
    if static_dir.exists():
        shutil.rmtree(static_dir)
    static_dir.mkdir()
    
    # 复制前端文件
    files_to_copy = [
        "index.html", "about.html", "products.html", "solutions.html",
        "cases.html", "news.html", "support.html", "contact.html",
        "css/", "js/", "assets/", "data/"
    ]
    
    for file_path in files_to_copy:
        src = Path(file_path)
        if src.exists():
            if src.is_dir():
                shutil.copytree(src, static_dir / src.name, dirs_exist_ok=True)
            else:
                shutil.copy2(src, static_dir / src.name)
    
    # 创建Vercel配置
    vercel_config = {
        "version": 2,
        "name": "led-website",
        "builds": [
            {
                "src": "*.html",
                "use": "@vercel/static"
            }
        ],
        "routes": [
            {
                "src": "/",
                "dest": "/index.html"
            },
            {
                "src": "/api/products",
                "dest": "/data/products.json"
            }
        ]
    }
    
    with open(static_dir / "vercel.json", "w", encoding="utf-8") as f:
        json.dump(vercel_config, f, indent=2, ensure_ascii=False)
    
    # 创建Netlify配置
    netlify_config = """
[build]
  publish = "."

[[redirects]]
  from = "/api/products"
  to = "/data/products.json"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
"""
    
    with open(static_dir / "netlify.toml", "w", encoding="utf-8") as f:
        f.write(netlify_config)
    
    print(f"✅ 静态部署包已创建: {static_dir}")
    return static_dir

def create_docker_package():
    """创建Docker部署包"""
    print("🐳 创建Docker部署包...")
    
    docker_dir = Path("docker_deployment")
    if docker_dir.exists():
        shutil.rmtree(docker_dir)
    docker_dir.mkdir()
    
    # 复制所有项目文件
    for item in Path(".").iterdir():
        if item.name not in [".git", "__pycache__", "node_modules", "docker_deployment", "static_deployment"]:
            if item.is_dir():
                shutil.copytree(item, docker_dir / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, docker_dir / item.name)
    
    # 创建优化的Dockerfile
    dockerfile_content = """
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    nginx \\
    supervisor \\
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 安装Python依赖
RUN pip install --no-cache-dir flask

# 配置Nginx
COPY nginx_led.conf /etc/nginx/sites-available/default

# 配置Supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 暴露端口
EXPOSE 80 5003

# 启动命令
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
"""
    
    with open(docker_dir / "Dockerfile", "w") as f:
        f.write(dockerfile_content)
    
    # 创建Supervisor配置
    supervisor_config = """
[supervisord]
nodaemon=true

[program:nginx]
command=nginx -g "daemon off;"
autostart=true
autorestart=true

[program:frontend]
command=python simple_server.py
directory=/app
autostart=true
autorestart=true

[program:admin]
command=python admin/complete_chinese_admin.py
directory=/app
autostart=true
autorestart=true
"""
    
    with open(docker_dir / "supervisord.conf", "w") as f:
        f.write(supervisor_config)
    
    print(f"✅ Docker部署包已创建: {docker_dir}")
    return docker_dir

def create_cloud_scripts():
    """创建云服务器部署脚本"""
    print("☁️ 创建云服务器部署脚本...")
    
    # 阿里云部署脚本
    aliyun_script = """#!/bin/bash
# 阿里云ECS部署脚本

echo "🚀 开始部署联进LED网站到阿里云ECS..."

# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要软件
sudo apt install -y python3 python3-pip nginx git

# 安装Python依赖
pip3 install flask

# 配置防火墙
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8080
sudo ufw allow 5003
sudo ufw --force enable

# 配置Nginx
sudo cp nginx_led.conf /etc/nginx/sites-available/led-website
sudo ln -sf /etc/nginx/sites-available/led-website /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

# 配置系统服务
sudo cp systemd_led.service /etc/systemd/system/led-website.service
sudo systemctl daemon-reload
sudo systemctl enable led-website
sudo systemctl start led-website

# 安装SSL证书
sudo apt install -y certbot python3-certbot-nginx
echo "请运行以下命令配置SSL证书:"
echo "sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com"

echo "✅ 部署完成!"
echo "前端网站: http://your-domain"
echo "后台管理: http://your-domain/admin"
"""
    
    with open("deploy_aliyun.sh", "w") as f:
        f.write(aliyun_script)
    
    # 腾讯云部署脚本
    tencent_script = """#!/bin/bash
# 腾讯云CVM部署脚本

echo "🚀 开始部署联进LED网站到腾讯云CVM..."

# 更新系统
sudo yum update -y

# 安装必要软件
sudo yum install -y python3 python3-pip nginx git

# 安装Python依赖
pip3 install flask

# 配置防火墙
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=5003/tcp
sudo firewall-cmd --reload

# 配置Nginx
sudo cp nginx_led.conf /etc/nginx/conf.d/led-website.conf
sudo nginx -t && sudo systemctl restart nginx
sudo systemctl enable nginx

# 配置系统服务
sudo cp systemd_led.service /etc/systemd/system/led-website.service
sudo systemctl daemon-reload
sudo systemctl enable led-website
sudo systemctl start led-website

echo "✅ 部署完成!"
echo "前端网站: http://your-domain"
echo "后台管理: http://your-domain/admin"
"""
    
    with open("deploy_tencent.sh", "w") as f:
        f.write(tencent_script)
    
    # 设置执行权限
    os.chmod("deploy_aliyun.sh", 0o755)
    os.chmod("deploy_tencent.sh", 0o755)
    
    print("✅ 云服务器部署脚本已创建")

def create_deployment_packages():
    """创建所有部署包"""
    print_banner()
    
    print("🎯 选择部署方式:")
    print("1. 静态网站部署 (Vercel/Netlify) - 免费")
    print("2. Docker容器部署 - 云服务器")
    print("3. 传统服务器部署 - 云服务器")
    print("4. 创建所有部署包")
    
    choice = input("\n请选择 (1-4): ").strip()
    
    if choice == "1":
        static_dir = create_static_package()
        print(f"\n🎉 静态部署包已准备完成!")
        print(f"📁 部署文件位置: {static_dir}")
        print("\n📋 部署步骤:")
        print("1. 访问 https://vercel.com 或 https://netlify.com")
        print("2. 上传 static_deployment 文件夹")
        print("3. 等待自动部署完成")
        
    elif choice == "2":
        docker_dir = create_docker_package()
        print(f"\n🎉 Docker部署包已准备完成!")
        print(f"📁 部署文件位置: {docker_dir}")
        print("\n📋 部署步骤:")
        print("1. 上传文件到云服务器")
        print("2. 运行: docker build -t led-website .")
        print("3. 运行: docker run -d -p 80:80 -p 5003:5003 led-website")
        
    elif choice == "3":
        create_cloud_scripts()
        print(f"\n🎉 云服务器部署脚本已准备完成!")
        print("\n📋 部署步骤:")
        print("1. 上传所有文件到云服务器")
        print("2. 阿里云运行: ./deploy_aliyun.sh")
        print("3. 腾讯云运行: ./deploy_tencent.sh")
        
    elif choice == "4":
        create_static_package()
        create_docker_package()
        create_cloud_scripts()
        print(f"\n🎉 所有部署包已准备完成!")
        
    else:
        print("❌ 无效选择")
        return
    
    print("\n📖 详细部署指南请查看: ONLINE_DEPLOYMENT_GUIDE.md")

if __name__ == "__main__":
    create_deployment_packages()