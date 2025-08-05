#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED网站项目一键部署脚本
支持多种部署环境的自动化部署
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path

class LEDWebsiteDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.deployment_configs = {
            'local': {
                'name': '本地开发环境',
                'frontend_port': 8080,
                'admin_port': 5003,
                'use_pm2': False
            },
            'production': {
                'name': '生产环境',
                'frontend_port': 8080,
                'admin_port': 5003,
                'use_pm2': True,
                'use_nginx': True
            },
            'docker': {
                'name': 'Docker容器部署',
                'use_docker': True
            }
        }
    
    def print_banner(self):
        """打印部署横幅"""
        print("=" * 60)
        print("🚀 LED网站项目一键部署工具")
        print("=" * 60)
        print()
    
    def check_requirements(self):
        """检查部署环境要求"""
        print("🔍 检查部署环境...")
        
        # 检查Python版本
        python_version = sys.version_info
        if python_version.major < 3 or python_version.minor < 7:
            print("❌ Python版本过低，需要Python 3.7+")
            return False
        print(f"✅ Python版本: {python_version.major}.{python_version.minor}")
        
        # 检查必要的Python包
        required_packages = ['flask', 'flask_cors']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package} 已安装")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package} 未安装")
        
        if missing_packages:
            print(f"\n📦 正在安装缺失的包: {', '.join(missing_packages)}")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, 
                             check=True, capture_output=True)
                print("✅ 依赖包安装完成")
            except subprocess.CalledProcessError as e:
                print(f"❌ 依赖包安装失败: {e}")
                return False
        
        return True
    
    def create_production_files(self):
        """创建生产环境配置文件"""
        print("\n📝 创建生产环境配置文件...")
        
        # 创建PM2配置文件
        pm2_config = {
            "apps": [
                {
                    "name": "led-frontend",
                    "script": "simple_server.py",
                    "cwd": str(self.project_root),
                    "interpreter": "python3",
                    "env": {
                        "PORT": "8080",
                        "NODE_ENV": "production"
                    },
                    "instances": 1,
                    "exec_mode": "fork",
                    "watch": False,
                    "max_memory_restart": "1G",
                    "error_file": "./logs/frontend-error.log",
                    "out_file": "./logs/frontend-out.log",
                    "log_file": "./logs/frontend-combined.log"
                },
                {
                    "name": "led-admin",
                    "script": "admin/complete_chinese_admin.py",
                    "cwd": str(self.project_root),
                    "interpreter": "python3",
                    "env": {
                        "PORT": "5003",
                        "NODE_ENV": "production"
                    },
                    "instances": 1,
                    "exec_mode": "fork",
                    "watch": False,
                    "max_memory_restart": "1G",
                    "error_file": "./logs/admin-error.log",
                    "out_file": "./logs/admin-out.log",
                    "log_file": "./logs/admin-combined.log"
                }
            ]
        }
        
        with open(self.project_root / 'ecosystem.config.json', 'w', encoding='utf-8') as f:
            json.dump(pm2_config, f, indent=2, ensure_ascii=False)
        print("✅ PM2配置文件已创建")
        
        # 创建Nginx配置文件
        nginx_config = """server {
    listen 80;
    server_name your-domain.com;  # 请替换为您的域名
    
    # 前端网站
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 启用缓存
        proxy_cache_bypass $http_upgrade;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
    }
    
    # 后台管理系统
    location /admin {
        proxy_pass http://127.0.0.1:5003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 静态文件缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        proxy_pass http://127.0.0.1:8080;
    }
    
    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}"""
        
        with open(self.project_root / 'nginx-led-website.conf', 'w', encoding='utf-8') as f:
            f.write(nginx_config)
        print("✅ Nginx配置文件已创建")
        
        # 创建Docker配置文件
        dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建日志目录
RUN mkdir -p logs

# 暴露端口
EXPOSE 8080 5003

# 启动脚本
CMD ["python", "start_fullstack.py"]"""
        
        with open(self.project_root / 'Dockerfile', 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
        print("✅ Dockerfile已创建")
        
        # 创建docker-compose.yml
        docker_compose_content = """version: '3.8'
services:
  led-website:
    build: .
    ports:
      - "80:8080"
      - "5003:5003"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - NODE_ENV=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080"]
      interval: 30s
      timeout: 10s
      retries: 3"""
        
        with open(self.project_root / 'docker-compose.yml', 'w', encoding='utf-8') as f:
            f.write(docker_compose_content)
        print("✅ docker-compose.yml已创建")
        
        # 创建requirements.txt
        requirements_content = """Flask==2.3.3
Flask-CORS==4.0.0
Werkzeug==2.3.7"""
        
        with open(self.project_root / 'requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        print("✅ requirements.txt已创建")
    
    def create_startup_script(self):
        """创建启动脚本"""
        print("\n🚀 创建启动脚本...")
        
        startup_script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import threading
import subprocess
from pathlib import Path

def start_frontend():
    \"\"\"启动前端服务\"\"\"
    print("🌐 启动前端服务 (端口 8080)...")
    os.system("python simple_server.py")

def start_admin():
    \"\"\"启动后台管理服务\"\"\"
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
        print("\\n🛑 正在停止服务...")
        sys.exit(0)

if __name__ == "__main__":
    main()"""
        
        with open(self.project_root / 'start_fullstack.py', 'w', encoding='utf-8') as f:
            f.write(startup_script)
        
        # 使脚本可执行
        os.chmod(self.project_root / 'start_fullstack.py', 0o755)
        print("✅ 启动脚本已创建")
    
    def create_deployment_scripts(self):
        """创建部署脚本"""
        print("\n📜 创建部署脚本...")
        
        # 创建生产环境部署脚本
        production_deploy = """#!/bin/bash
# LED网站生产环境部署脚本

echo "🚀 开始部署LED网站到生产环境..."

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用root权限运行此脚本"
    exit 1
fi

# 更新系统
echo "📦 更新系统包..."
apt update && apt upgrade -y

# 安装必要软件
echo "🔧 安装必要软件..."
apt install -y python3 python3-pip python3-venv nginx ufw

# 安装Node.js和PM2
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt install -y nodejs
npm install -g pm2

# 创建项目目录
PROJECT_DIR="/var/www/led-website"
mkdir -p $PROJECT_DIR
cp -r . $PROJECT_DIR/
cd $PROJECT_DIR

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 配置Nginx
cp nginx-led-website.conf /etc/nginx/sites-available/led-website
ln -sf /etc/nginx/sites-available/led-website /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# 配置防火墙
ufw allow 22
ufw allow 80
ufw allow 443
ufw --force enable

# 启动服务
pm2 start ecosystem.config.json
pm2 save
pm2 startup

echo "✅ 部署完成!"
echo "🌐 网站地址: http://your-domain.com"
echo "⚙️ 管理后台: http://your-domain.com/admin"
echo "👤 管理员账号: admin / admin123"
"""
        
        with open(self.project_root / 'deploy_production.sh', 'w', encoding='utf-8') as f:
            f.write(production_deploy)
        os.chmod(self.project_root / 'deploy_production.sh', 0o755)
        
        # 创建Docker部署脚本
        docker_deploy = """#!/bin/bash
# LED网站Docker部署脚本

echo "🐳 开始Docker部署..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "📦 安装Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl start docker
    systemctl enable docker
fi

# 检查docker-compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "📦 安装docker-compose..."
    curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# 构建并启动容器
echo "🚀 构建并启动容器..."
docker-compose up -d --build

echo "✅ Docker部署完成!"
echo "🌐 网站地址: http://localhost"
echo "⚙️ 管理后台: http://localhost:5003"
"""
        
        with open(self.project_root / 'deploy_docker.sh', 'w', encoding='utf-8') as f:
            f.write(docker_deploy)
        os.chmod(self.project_root / 'deploy_docker.sh', 0o755)
        
        print("✅ 部署脚本已创建")
    
    def show_deployment_options(self):
        """显示部署选项"""
        print("\n🎯 请选择部署方式:")
        print("1. 本地开发环境 (推荐用于测试)")
        print("2. 生产环境部署 (云服务器)")
        print("3. Docker容器部署")
        print("4. 仅创建配置文件")
        print("0. 退出")
        
        while True:
            try:
                choice = input("\n请输入选择 (0-4): ").strip()
                if choice in ['0', '1', '2', '3', '4']:
                    return choice
                else:
                    print("❌ 无效选择，请输入0-4之间的数字")
            except KeyboardInterrupt:
                print("\n👋 部署已取消")
                sys.exit(0)
    
    def deploy_local(self):
        """本地部署"""
        print("\n🏠 开始本地部署...")
        
        # 创建日志目录
        os.makedirs(self.project_root / 'logs', exist_ok=True)
        
        print("✅ 本地环境配置完成")
        print("\n🚀 启动服务:")
        print("方式1: 运行 python start_fullstack.py")
        print("方式2: 分别运行以下命令:")
        print("  - python simple_server.py")
        print("  - python admin/complete_chinese_admin.py")
        
        # 询问是否立即启动
        start_now = input("\n是否立即启动服务? (y/n): ").strip().lower()
        if start_now in ['y', 'yes', '是']:
            print("🚀 正在启动服务...")
            os.system("python start_fullstack.py")
    
    def deploy_production(self):
        """生产环境部署"""
        print("\n🏭 生产环境部署准备...")
        print("📋 部署清单:")
        print("  ✅ PM2配置文件")
        print("  ✅ Nginx配置文件")
        print("  ✅ 部署脚本")
        print("  ✅ 启动脚本")
        
        print("\n📝 接下来的步骤:")
        print("1. 将项目文件上传到服务器")
        print("2. 在服务器上运行: sudo bash deploy_production.sh")
        print("3. 修改nginx-led-website.conf中的域名")
        print("4. 配置SSL证书 (可选)")
        
        print("\n💡 提示: 详细部署指南请查看 DEPLOYMENT_GUIDE_COMPLETE.md")
    
    def deploy_docker(self):
        """Docker部署"""
        print("\n🐳 Docker部署准备...")
        print("📋 Docker文件:")
        print("  ✅ Dockerfile")
        print("  ✅ docker-compose.yml")
        print("  ✅ requirements.txt")
        
        print("\n📝 部署步骤:")
        print("1. 确保服务器已安装Docker和docker-compose")
        print("2. 运行: bash deploy_docker.sh")
        print("3. 或手动运行: docker-compose up -d --build")
        
        # 询问是否立即构建
        build_now = input("\n是否立即构建Docker镜像? (y/n): ").strip().lower()
        if build_now in ['y', 'yes', '是']:
            print("🐳 正在构建Docker镜像...")
            try:
                subprocess.run(['docker-compose', 'up', '-d', '--build'], check=True)
                print("✅ Docker部署完成!")
            except subprocess.CalledProcessError as e:
                print(f"❌ Docker部署失败: {e}")
            except FileNotFoundError:
                print("❌ Docker或docker-compose未安装")
    
    def run(self):
        """运行部署工具"""
        self.print_banner()
        
        if not self.check_requirements():
            print("❌ 环境检查失败，请解决上述问题后重试")
            sys.exit(1)
        
        # 创建配置文件
        self.create_production_files()
        self.create_startup_script()
        self.create_deployment_scripts()
        
        # 显示部署选项
        choice = self.show_deployment_options()
        
        if choice == '0':
            print("👋 部署已取消")
            return
        elif choice == '1':
            self.deploy_local()
        elif choice == '2':
            self.deploy_production()
        elif choice == '3':
            self.deploy_docker()
        elif choice == '4':
            print("✅ 所有配置文件已创建完成!")
            print("📁 生成的文件:")
            print("  - ecosystem.config.json (PM2配置)")
            print("  - nginx-led-website.conf (Nginx配置)")
            print("  - Dockerfile (Docker配置)")
            print("  - docker-compose.yml (Docker Compose配置)")
            print("  - requirements.txt (Python依赖)")
            print("  - start_fullstack.py (启动脚本)")
            print("  - deploy_production.sh (生产环境部署脚本)")
            print("  - deploy_docker.sh (Docker部署脚本)")
            print("\n💡 详细部署指南请查看: DEPLOYMENT_GUIDE_COMPLETE.md")

if __name__ == "__main__":
    deployer = LEDWebsiteDeployer()
    deployer.run()
