# LED Display Admin Panel
## LED显示屏管理后台系统

A comprehensive content management system for the LED Display B2B website, built with Flask and SQLite.

## 🌟 Features | 功能特点

### 📊 Dashboard | 仪表盘
- Real-time statistics and metrics
- Recent inquiries and quote requests
- Quick action shortcuts
- System status monitoring

### 🖥️ Product Management | 产品管理
- Add/Edit/Delete LED display products
- Bilingual content support (English/Chinese)
- Product categorization and specifications
- Image upload and management
- Price and inventory tracking

### 📰 News Management | 新闻管理
- Create and publish news articles
- Multi-language content editing
- Category management
- Draft and publish workflow
- SEO-friendly content structure

### 📋 Case Studies | 案例管理
- Showcase successful projects
- Client testimonials and project details
- Image galleries and project specifications
- Category-based organization

### 📧 Inquiry Management | 询盘管理
- Handle customer inquiries
- Contact form submissions
- Status tracking and follow-up
- Customer information management

### 💰 Quote Management | 报价管理
- Process quote requests
- Multi-step quote form data
- Project requirements tracking
- Quote generation and follow-up

### ⚙️ System Settings | 系统设置
- Website configuration
- Company information management
- User account management
- Data backup and restore

## 🚀 Quick Start | 快速开始

### Prerequisites | 系统要求
- Python 3.7+
- Flask 2.3+
- SQLite (included with Python)

### Installation | 安装步骤

1. **Navigate to admin directory | 进入管理目录**
   ```bash
   cd admin
   ```

2. **Install dependencies | 安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the admin panel | 启动管理后台**
   ```bash
   python start_admin.py
   ```
   
   Or run directly:
   ```bash
   python app.py
   ```

4. **Access the admin panel | 访问管理后台**
   - URL: http://localhost:5000
   - Username: `admin`
   - Password: `admin123`

## 📁 File Structure | 文件结构

```
admin/
├── app.py                 # Main Flask application
├── start_admin.py         # Startup script
├── requirements.txt       # Python dependencies
├── led_admin.db          # SQLite database (auto-created)
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── login.html        # Login page
│   ├── dashboard.html    # Dashboard
│   ├── products.html     # Product list
│   ├── product_form.html # Product add/edit form
│   ├── news.html         # News list
│   ├── news_form.html    # News add/edit form
│   ├── cases.html        # Case studies
│   ├── inquiries.html    # Customer inquiries
│   ├── quotes.html       # Quote requests
│   └── settings.html     # System settings
└── static/
    └── uploads/          # File uploads directory
```

## 🗄️ Database Schema | 数据库结构

### Tables | 数据表

1. **admins** - Administrator accounts
2. **products** - LED display products
3. **news** - News articles and blog posts
4. **cases** - Project case studies
5. **inquiries** - Customer contact inquiries
6. **quotes** - Quote requests
7. **settings** - System configuration

### Key Features | 主要特性
- Automatic database initialization
- Default admin account creation
- Bilingual content support
- Timestamp tracking
- Status management

## 🔧 Configuration | 配置说明

### Default Settings | 默认设置
- **Admin Username**: admin
- **Admin Password**: admin123 (⚠️ Change immediately after first login)
- **Database**: SQLite (led_admin.db)
- **Upload Directory**: static/uploads/
- **Max File Size**: 16MB

### Security Recommendations | 安全建议
1. Change default admin password immediately
2. Use strong passwords (minimum 8 characters)
3. Regular database backups
4. Monitor access logs
5. Keep system updated

## 🌐 API Endpoints | API接口

### Public APIs | 公开接口
- `POST /api/contact` - Submit contact form
- `POST /api/quote` - Submit quote request

### Admin APIs | 管理接口
- `GET /` - Dashboard
- `GET /products` - Product management
- `GET /news` - News management
- `GET /cases` - Case management
- `GET /inquiries` - Inquiry management
- `GET /quotes` - Quote management
- `GET /settings` - System settings

## 🎨 Customization | 自定义设置

### Styling | 样式定制
The admin panel uses Bootstrap 5 with custom CSS variables:
```css
:root {
    --primary-color: #1B365D;
    --secondary-color: #00A0E9;
    --accent-color: #FF6B35;
}
```

### Adding New Features | 添加新功能
1. Create new route in `app.py`
2. Add corresponding HTML template
3. Update navigation in `base.html`
4. Add database tables if needed

## 📊 Usage Guide | 使用指南

### First Time Setup | 首次设置
1. Login with default credentials
2. Change admin password in Settings
3. Update company information
4. Add your first product
5. Configure website settings

### Daily Operations | 日常操作
1. **Check Dashboard** for new inquiries and quotes
2. **Manage Products** - Add/update product information
3. **Handle Inquiries** - Respond to customer contacts
4. **Process Quotes** - Generate quotes for requests
5. **Publish News** - Keep website content fresh

### Content Management | 内容管理
- All content supports bilingual input (English/Chinese)
- Use the status field to control visibility
- Regular backups recommended
- SEO-friendly URLs and meta tags

## 🔍 Troubleshooting | 故障排除

### Common Issues | 常见问题

**Port 5000 already in use | 端口5000被占用**
```bash
# Find process using port 5000
netstat -ano | findstr :5000
# Kill the process or use different port
```

**Database locked error | 数据库锁定错误**
- Restart the application
- Check file permissions
- Ensure no other processes are using the database

**Login issues | 登录问题**
- Verify username/password
- Check database initialization
- Reset admin password if needed

### Getting Help | 获取帮助
- Check the console for error messages
- Review the Flask debug output
- Contact technical support: admin@lianjinled.com

## 🔄 Updates & Maintenance | 更新和维护

### Regular Maintenance | 定期维护
- **Weekly**: Check for new inquiries and quotes
- **Monthly**: Backup database and uploaded files
- **Quarterly**: Review and update product information
- **Annually**: Security audit and password updates

### Backup Strategy | 备份策略
1. **Database**: Export SQLite database regularly
2. **Files**: Backup uploads directory
3. **Configuration**: Save settings and customizations
4. **Code**: Version control for custom modifications

## 📞 Support | 技术支持

### Contact Information | 联系信息
- **Email**: admin@lianjinled.com
- **Phone**: +86-755-1234-5678
- **Website**: [Company Website]

### Documentation | 文档资源
- Flask Documentation: https://flask.palletsprojects.com/
- Bootstrap Documentation: https://getbootstrap.com/docs/
- SQLite Documentation: https://sqlite.org/docs.html

---

## 📝 License | 许可证

This admin panel is developed for Shenzhen Lianjin Photoelectricity Co., Ltd.
All rights reserved.

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Developed by**: LED Display Team