# LED网站Vercel部署指南

## 已准备的文件
✅ `vercel.json` - Vercel配置文件
✅ `requirements.txt` - Python依赖
✅ `api/index.py` - 适配Vercel的主应用文件

## 部署步骤

### 方法一：通过Vercel CLI（推荐）
```bash
# 1. 安装Vercel CLI
npm i -g vercel

# 2. 登录Vercel账户
vercel login

# 3. 在项目根目录执行部署
vercel --prod
```

### 方法二：通过GitHub集成
1. 将项目代码推送到GitHub仓库
2. 访问 https://vercel.com
3. 点击"New Project"
4. 选择您的GitHub仓库
5. 点击"Deploy"

## 部署后访问地址
- **前端网站**: `https://your-project-name.vercel.app`
- **后台管理**: `https://your-project-name.vercel.app/admin`

## 管理员登录信息
- **用户名**: `admin`
- **密码**: `admin123`

## 功能特性

### 前端功能
- ✅ 专业LED显示屏展示
- ✅ 产品分类（室内、户外、租赁、创意LED）
- ✅ 响应式设计，支持移动端
- ✅ 联系表单和询盘功能
- ✅ 新闻资讯展示

### 后台管理功能
- ✅ 完整中文管理界面
- ✅ 产品管理（增删改查）
- ✅ 询盘管理和处理
- ✅ 新闻管理和发布
- ✅ 前端页面内容管理
- ✅ 用户权限管理
- ✅ 系统设置配置
- ✅ 数据统计分析

### 前端页面管理子模块
- 🏠 首页管理
- ℹ️ 关于我们管理
- 📺 产品中心管理
- 💡 解决方案管理
- 💼 成功案例管理
- 📰 新闻资讯管理
- 🛟 技术支持管理
- ✉️ 联系我们管理

## 技术架构
- **前端**: HTML5 + CSS3 + JavaScript
- **后端**: Flask (Python)
- **数据库**: SQLite (适配Vercel无服务器环境)
- **部署平台**: Vercel
- **API**: RESTful API设计

## 注意事项
1. Vercel使用无服务器架构，数据库存储在 `/tmp` 目录
2. 每次部署会重置数据库，生产环境建议使用外部数据库
3. 静态文件通过相对路径访问
4. 所有模板文件已适配Vercel目录结构

## 故障排除
如果部署失败，请检查：
1. `vercel.json` 配置是否正确
2. `requirements.txt` 依赖是否完整
3. Python版本兼容性（建议Python 3.8+）
4. 模板文件路径是否正确

## 生产环境优化建议
1. 使用外部数据库（如PostgreSQL、MySQL）
2. 配置环境变量管理敏感信息
3. 启用HTTPS和安全头
4. 配置CDN加速静态资源
5. 设置监控和日志记录

部署完成后，您将拥有一个完全功能的LED显示屏网站，包含专业的前端展示和强大的后台管理系统！