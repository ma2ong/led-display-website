#!/bin/bash
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
