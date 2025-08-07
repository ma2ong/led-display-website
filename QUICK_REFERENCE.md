# 🚀 LED网站管理系统 - 快速参考指南

## ⚡ 一键启动

```bash
# 方法1：分别启动（推荐）
cd admin && python complete_chinese_admin_system.py
python start_frontend_server.py

# 方法2：Windows批处理
start_all.bat

# 方法3：Linux/Mac脚本
./start_all.sh
```

## 🌐 访问地址

| 服务 | 地址 | 用途 | 登录信息 |
|------|------|------|----------|
| 后台管理 | http://localhost:5003 | 管理系统 | admin/admin123 |
| 前端网站 | http://localhost:8000 | 展示网站 | 无需登录 |
| 数据库测试 | test-supabase-products.html | 测试工具 | 无需登录 |

## 📁 核心文件

| 文件 | 用途 | 重要性 |
|------|------|--------|
| `admin/complete_chinese_admin_system.py` | 后台主程序 | ⭐⭐⭐⭐⭐ |
| `start_frontend_server.py` | 前端服务器 | ⭐⭐⭐⭐⭐ |
| `admin/admin.db` | 本地数据库 | ⭐⭐⭐⭐ |
| `admin/templates/` | 后台模板 | ⭐⭐⭐⭐ |
| `*.html` | 前端页面 | ⭐⭐⭐ |

## 🔧 常用命令

```bash
# 停止所有Python进程
taskkill /F /IM python.exe

# 检查端口占用
netstat -ano | findstr :5003
netstat -ano | findstr :8000

# 重启服务
cd admin && python complete_chinese_admin_system.py
python start_frontend_server.py
```

## 🛠️ 故障排除

| 问题 | 解决方案 |
|------|----------|
| 端口被占用 | `taskkill /F /IM python.exe` |
| 模板未找到 | 检查 `admin/templates/` 目录 |
| 数据库错误 | 检查 `admin.db` 文件权限 |
| 前端404 | 确认前端服务器运行在8000端口 |

## 📊 功能模块

### 后台管理 (8个模块)
1. 🏠 仪表盘 - 数据概览
2. 📄 前端页面管理 - 内容编辑
3. 📦 产品管理 - 产品CRUD
4. 📧 询盘管理 - 客户询盘
5. 📰 新闻管理 - 新闻发布
6. 👥 用户管理 - 用户权限
7. 📈 统计分析 - 数据分析
8. ⚙️ 系统设置 - 配置管理

### 前端网站 (8个页面)
1. 🏠 首页 - index.html
2. ℹ️ 关于我们 - about.html
3. 📺 产品中心 - products.html
4. 💡 解决方案 - solutions.html
5. 💼 成功案例 - cases.html
6. 📰 新闻资讯 - news.html
7. 🛟 技术支持 - support.html
8. 📞 联系我们 - contact.html

## 🔐 安全信息

| 项目 | 信息 |
|------|------|
| 管理员账号 | admin |
| 管理员密码 | admin123 |
| 密码加密 | SHA-256 |
| 会话管理 | Flask Session |

## 📱 联系方式

| 联系方式 | 信息 |
|----------|------|
| 公司名称 | 深圳联锦LED科技有限公司 |
| 联系电话 | +86-755-12345678 |
| 联系邮箱 | info@lianjinled.com |
| 公司地址 | 深圳市南山区科技园南区高新南七道数字技术园B2栋5楼 |

## 🎯 项目状态

- ✅ 后台管理系统 - 完成
- ✅ 前端展示网站 - 完成
- ✅ 数据库集成 - 完成
- ✅ 错误修复 - 完成
- ✅ 文档编写 - 完成
- ✅ 测试验证 - 完成

**项目状态：** 🎉 完成并正常运行

---

**最后更新：** 2025年8月7日  
**版本：** v1.0.0  
**状态：** 生产就绪 ✅