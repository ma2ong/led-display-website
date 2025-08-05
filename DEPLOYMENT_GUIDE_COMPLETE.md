# 🚀 LED网站项目完整部署指南

## 📋 项目概述

您的LED网站项目包含：
- **前端网站** (端口 8080) - 展示型网站
- **后台管理系统** (端口 5003) - 中文管理界面
- **数据库** - SQLite数据库存储产品、询盘等数据

## 🎯 部署选项

### 选项1: 云服务器部署 (推荐)

#### 1.1 准备云服务器
- **推荐配置**: 2核4G内存，40G硬盘
- **操作系统**: Ubuntu 20.04 LTS 或 CentOS 7+
- **云服务商**: 阿里云、腾讯云、华为云等

#### 1.2 服务器环境配置

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python 3.8+
sudo apt install python3 python3-pip python3-venv -y

# 安装Nginx (用于反向代理)
sudo apt install nginx -y

# 安装PM2 (进程管理)
sudo npm install -g pm2
```

#### 1.3 上传项目文件

```bash
# 创建项目目录
mkdir -p /var/www/led-website
cd /var/www/led-website

# 上传所有项目文件到此目录
# 可以使用scp、rsync或git clone
```

#### 1.4 安装Python依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install flask flask-cors sqlite3
```

#### 1.5 配置Nginx反向代理

创建Nginx配置文件：

```bash
sudo nano /etc/nginx/sites-available/led-website
```

配置内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名
    
    # 前端网站
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 后台管理系统
    location /admin {
        proxy_pass http://127.0.0.1:5003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/led-website /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 1.6 使用PM2启动服务

创建PM2配置文件：

```bash
nano ecosystem.config.js
```

配置内容：

```javascript
module.exports = {
  apps: [
    {
      name: 'led-frontend',
      script: 'python3',
      args: 'simple_server.py',
      cwd: '/var/www/led-website',
      interpreter: '/var/www/led-website/venv/bin/python3',
      env: {
        PORT: 8080
      }
    },
    {
      name: 'led-admin',
      script: 'python3',
      args: 'admin/complete_chinese_admin.py',
      cwd: '/var/www/led-website',
      interpreter: '/var/www/led-website/venv/bin/python3',
      env: {
        PORT: 5003
      }
    }
  ]
};
```

启动服务：

```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### 选项2: Docker部署

#### 2.1 创建Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080 5003

CMD ["python", "start_fullstack.py"]
```

#### 2.2 创建docker-compose.yml

```yaml
version: '3.8'
services:
  led-website:
    build: .
    ports:
      - "80:8080"
      - "5003:5003"
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

#### 2.3 部署命令

```bash
docker-compose up -d
```

### 选项3: 宝塔面板部署 (简单易用)

#### 3.1 安装宝塔面板

```bash
# CentOS
yum install -y wget && wget -O install.sh http://download.bt.cn/install/install_6.0.sh && sh install.sh

# Ubuntu
wget -O install.sh http://download.bt.cn/install/install-ubuntu_6.0.sh && sudo bash install.sh
```

#### 3.2 在宝塔面板中操作

1. 登录宝塔面板
2. 安装Python项目管理器
3. 创建新的Python项目
4. 上传项目文件
5. 配置启动脚本
6. 设置反向代理

### 选项4: Vercel部署 (免费选项)

#### 4.1 准备vercel.json

```json
{
  "version": 2,
  "builds": [
    {
      "src": "simple_server.py",
      "use": "@vercel/python"
    },
    {
      "src": "admin/complete_chinese_admin.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/admin/(.*)",
      "dest": "/admin/complete_chinese_admin.py"
    },
    {
      "src": "/(.*)",
      "dest": "/simple_server.py"
    }
  ]
}
```

#### 4.2 部署命令

```bash
npm i -g vercel
vercel --prod
```

## 🔧 生产环境配置

### 安全配置

1. **修改默认密码**：
```python
# 在admin/complete_chinese_admin.py中修改
ADMIN_USERNAME = "your_admin_username"
ADMIN_PASSWORD = "your_secure_password"
```

2. **启用HTTPS**：
```bash
# 使用Let's Encrypt免费SSL证书
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

3. **防火墙配置**：
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 性能优化

1. **启用Gzip压缩** (Nginx配置)：
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
```

2. **静态文件缓存**：
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 📊 监控和维护

### 日志监控

```bash
# 查看PM2日志
pm2 logs

# 查看Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 数据备份

```bash
# 创建备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /var/www/led-website/data/admin.db /var/www/led-website/backups/admin_$DATE.db
```

### 自动更新脚本

```bash
#!/bin/bash
cd /var/www/led-website
git pull origin main
pm2 restart all
```

## 🌐 域名配置

1. **购买域名** (推荐.com域名)
2. **DNS解析配置**：
   - A记录: @ -> 服务器IP
   - A记录: www -> 服务器IP
   - CNAME记录: admin -> 主域名

## 📱 移动端优化

项目已包含响应式设计，自动适配移动设备。

## 🔍 SEO优化

1. **网站地图生成**
2. **Meta标签优化**
3. **结构化数据标记**
4. **页面加载速度优化**

## 📞 技术支持

如果在部署过程中遇到问题：

1. **检查日志文件**
2. **确认端口是否被占用**
3. **验证防火墙设置**
4. **检查Python依赖是否完整安装**

## 🎉 部署完成检查清单

- [ ] 前端网站可以正常访问
- [ ] 后台管理系统可以正常登录
- [ ] 产品管理功能正常
- [ ] 询盘管理功能正常
- [ ] 数据库读写正常
- [ ] SSL证书配置完成
- [ ] 域名解析正确
- [ ] 监控和备份脚本配置完成

## 💡 推荐部署方案

**对于初学者**: 选择宝塔面板部署
**对于开发者**: 选择云服务器 + Nginx + PM2
**对于预算有限**: 选择Vercel免费部署
**对于企业级**: 选择Docker + 云服务器集群

选择适合您技术水平和预算的部署方案，按照指南逐步操作即可成功部署您的LED网站项目！