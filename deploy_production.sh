#!/bin/bash
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
