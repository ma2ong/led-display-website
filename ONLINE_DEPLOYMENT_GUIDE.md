# 🚀 联进LED网站在线部署指南

## 📋 部署选项概览

### 1. 🆓 免费部署选项 (推荐新手)

#### A. Vercel 部署 (最简单)
- **优点**: 完全免费，自动HTTPS，全球CDN
- **适用**: 静态网站 + 无服务器函数
- **步骤**:
  1. 访问 [vercel.com](https://vercel.com)
  2. 用GitHub账号登录
  3. 上传项目文件
  4. 自动部署完成

#### B. Netlify 部署
- **优点**: 免费，支持表单处理
- **适用**: 静态网站
- **步骤**:
  1. 访问 [netlify.com](https://netlify.com)
  2. 拖拽项目文件夹到部署区域
  3. 获得免费域名

#### C. GitHub Pages
- **优点**: 与GitHub集成，免费
- **限制**: 仅支持静态网站
- **步骤**:
  1. 创建GitHub仓库
  2. 上传网站文件
  3. 启用GitHub Pages

### 2. 💰 付费云服务器部署 (推荐生产环境)

#### A. 阿里云ECS
- **价格**: ¥99/月起
- **优点**: 国内访问快，中文支持
- **配置**: 2核4G，40G SSD

#### B. 腾讯云CVM  
- **价格**: ¥95/月起
- **优点**: 微信生态集成
- **配置**: 2核4G，50G SSD

#### C. 华为云ECS
- **价格**: ¥108/月起
- **优点**: 企业级稳定性
- **配置**: 2核4G，40G SSD

## 🎯 推荐部署方案

### 方案1: 快速上线 (Vercel + 静态网站)
```bash
# 1. 准备静态文件
python deploy_production.py

# 2. 上传到Vercel
# - 访问 vercel.com
# - 上传生成的 static_website 文件夹
# - 获得 https://your-site.vercel.app 域名
```

### 方案2: 完整功能 (云服务器 + 动态后台)
```bash
# 1. 购买云服务器 (推荐阿里云)
# 2. 安装环境
sudo apt update
sudo apt install python3 python3-pip nginx

# 3. 上传项目文件
scp -r . root@your-server-ip:/var/www/led-website/

# 4. 安装依赖
cd /var/www/led-website
pip3 install flask

# 5. 配置Nginx
sudo cp nginx_led.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/nginx_led.conf /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# 6. 启动服务
python3 quick_deploy.py
```

## 📁 部署文件说明

### 已生成的部署文件:
- `docker-compose.yml` - Docker容器编排
- `Dockerfile` - Docker镜像构建
- `nginx_led.conf` - Nginx配置
- `systemd_led.service` - 系统服务配置
- `requirements.txt` - Python依赖
- `vercel.json` - Vercel部署配置
- `deploy.sh` - 一键部署脚本

## 🔧 一键部署脚本

### 使用Docker部署:
```bash
# 构建并启动
docker-compose up -d

# 访问网站
# 前端: http://your-domain:8080
# 后台: http://your-domain:5003
```

### 使用传统方式部署:
```bash
# 运行部署脚本
chmod +x deploy.sh
./deploy.sh

# 或使用Python脚本
python3 quick_deploy.py
```

## 🌐 域名配置

### 1. 购买域名
- 阿里云域名: [wanwang.aliyun.com](https://wanwang.aliyun.com)
- 腾讯云域名: [dnspod.cloud.tencent.com](https://dnspod.cloud.tencent.com)
- GoDaddy: [godaddy.com](https://godaddy.com)

### 2. DNS解析配置
```
类型: A
主机记录: @
记录值: 你的服务器IP
TTL: 600

类型: A  
主机记录: www
记录值: 你的服务器IP
TTL: 600
```

### 3. SSL证书配置
```bash
# 使用Let's Encrypt免费证书
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 📊 监控和维护

### 1. 服务状态检查
```bash
# 检查服务状态
systemctl status led-website

# 查看日志
journalctl -u led-website -f

# 重启服务
systemctl restart led-website
```

### 2. 备份策略
```bash
# 数据库备份
cp admin/database.db backup/database_$(date +%Y%m%d).db

# 文件备份
tar -czf backup/website_$(date +%Y%m%d).tar.gz .
```

## 🚨 故障排除

### 常见问题:
1. **端口被占用**: 修改配置文件中的端口号
2. **权限问题**: 使用 `sudo` 运行命令
3. **防火墙阻拦**: 开放8080和5003端口
4. **域名解析**: 检查DNS配置是否正确

### 联系支持:
- 阿里云工单系统
- 腾讯云在线客服  
- 技术QQ群: [群号]

## 💡 性能优化建议

1. **启用Gzip压缩**
2. **配置CDN加速**
3. **优化图片大小**
4. **启用浏览器缓存**
5. **使用Redis缓存**

---

## 🎉 部署完成检查清单

- [ ] 前端网站可正常访问
- [ ] 后台管理系统可登录
- [ ] 产品管理功能正常
- [ ] 询盘管理功能正常
- [ ] 域名解析正确
- [ ] SSL证书配置
- [ ] 监控系统运行
- [ ] 备份策略实施

**部署成功后，您的LED网站将拥有:**
- ✅ 专业的前端展示网站
- ✅ 功能完整的后台管理系统
- ✅ 产品管理和询盘处理功能
- ✅ 响应式设计，支持手机访问
- ✅ SEO优化，搜索引擎友好
- ✅ 安全的HTTPS访问