#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建完整的图片文件结构
将前端网站中引用的所有图片按照相应位置和命名储存到assets文件夹
"""

import os
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import requests

def create_placeholder_image(width, height, text, filename):
    """创建占位符图片"""
    # 创建图片
    img = Image.new('RGB', (width, height), color='#f8f9fa')
    draw = ImageDraw.Draw(img)
    
    # 尝试使用系统字体，如果失败则使用默认字体
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            font = ImageFont.load_default()
    
    # 计算文本位置
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # 绘制文本
    draw.text((x, y), text, fill='#6c757d', font=font)
    
    # 绘制边框
    draw.rectangle([0, 0, width-1, height-1], outline='#dee2e6', width=2)
    
    # 保存图片
    img.save(filename, 'JPEG', quality=85)
    print(f"✅ 创建占位符图片: {filename}")

def create_directory_structure():
    """创建完整的目录结构"""
    directories = [
        'assets/products',
        'assets/news', 
        'assets/cases',
        'assets/about',
        'assets/solutions',
        'assets/support',
        'assets/contact',
        'assets/logos',
        'assets/icons',
        'assets/backgrounds',
        'assets/banners',
        'assets/team',
        'assets/certificates',
        'assets/gallery'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 创建目录: {directory}")

def create_product_images():
    """创建产品相关图片"""
    product_images = {
        # 主页Hero区域
        'assets/products/led-display-hero.jpg': (1200, 800, 'LED Display Hero'),
        
        # 产品分类图片
        'assets/products/indoor-led-display.jpg': (800, 600, 'Indoor LED Display'),
        'assets/products/outdoor-led-display.jpg': (800, 600, 'Outdoor LED Display'),
        'assets/products/rental-led-display.jpg': (800, 600, 'Rental LED Display'),
        'assets/products/transparent-led-display.jpg': (800, 600, 'Transparent LED'),
        'assets/products/creative-led-display.jpg': (800, 600, 'Creative LED'),
        'assets/products/industrial-led-solutions.jpg': (800, 600, 'Industrial LED'),
        
        # Fine Pitch LED 产品页面
        'assets/products/fine-pitch-led-main.jpg': (1200, 800, 'Fine Pitch LED Main'),
        'assets/products/fine-pitch-p0.9.jpg': (600, 400, 'P0.9 Fine Pitch'),
        'assets/products/fine-pitch-p1.25.jpg': (600, 400, 'P1.25 Fine Pitch'),
        'assets/products/fine-pitch-p1.56.jpg': (600, 400, 'P1.56 Fine Pitch'),
        'assets/products/fine-pitch-control-room.jpg': (800, 600, 'Control Room'),
        'assets/products/fine-pitch-broadcast.jpg': (800, 600, 'Broadcast Studio'),
        
        # Outdoor LED 产品页面
        'assets/products/outdoor-led-main.jpg': (1200, 800, 'Outdoor LED Main'),
        'assets/products/outdoor-billboard.jpg': (800, 600, 'Outdoor Billboard'),
        'assets/products/outdoor-stadium.jpg': (800, 600, 'Stadium Display'),
        'assets/products/outdoor-street.jpg': (800, 600, 'Street Display'),
        
        # Rental LED 产品页面
        'assets/products/rental-led-main.jpg': (1200, 800, 'Rental LED Main'),
        'assets/products/rental-stage.jpg': (800, 600, 'Stage Display'),
        'assets/products/rental-event.jpg': (800, 600, 'Event Display'),
        'assets/products/rental-concert.jpg': (800, 600, 'Concert Display'),
        
        # Creative LED 产品页面
        'assets/products/creative-led-main.jpg': (1200, 800, 'Creative LED Main'),
        'assets/products/creative-curved.jpg': (800, 600, 'Curved Display'),
        'assets/products/creative-sphere.jpg': (800, 600, 'Sphere Display'),
        'assets/products/creative-irregular.jpg': (800, 600, 'Irregular Shape'),
        
        # Transparent LED 产品页面
        'assets/products/transparent-led-main.jpg': (1200, 800, 'Transparent LED Main'),
        'assets/products/transparent-window.jpg': (800, 600, 'Window Display'),
        'assets/products/transparent-facade.jpg': (800, 600, 'Building Facade'),
        'assets/products/transparent-retail.jpg': (800, 600, 'Retail Window'),
        
        # 产品详情图片
        'assets/products/product-detail-1.jpg': (600, 400, 'Product Detail 1'),
        'assets/products/product-detail-2.jpg': (600, 400, 'Product Detail 2'),
        'assets/products/product-detail-3.jpg': (600, 400, 'Product Detail 3'),
        
        # 产品规格图片
        'assets/products/specifications-chart.jpg': (800, 600, 'Specifications'),
        'assets/products/installation-guide.jpg': (800, 600, 'Installation Guide'),
        'assets/products/maintenance-guide.jpg': (800, 600, 'Maintenance Guide')
    }
    
    for filepath, (width, height, text) in product_images.items():
        if not os.path.exists(filepath):
            create_placeholder_image(width, height, text, filepath)

def create_case_images():
    """创建案例相关图片"""
    case_images = {
        # 案例主页图片
        'assets/cases/cases-hero.jpg': (1200, 800, 'Success Cases'),
        
        # 商业案例
        'assets/cases/commercial-mall.jpg': (800, 600, 'Shopping Mall'),
        'assets/cases/commercial-office.jpg': (800, 600, 'Office Building'),
        'assets/cases/commercial-hotel.jpg': (800, 600, 'Hotel Lobby'),
        'assets/cases/commercial-restaurant.jpg': (800, 600, 'Restaurant'),
        
        # 广播案例
        'assets/cases/broadcast-studio.jpg': (800, 600, 'TV Studio'),
        'assets/cases/broadcast-news.jpg': (800, 600, 'News Room'),
        'assets/cases/broadcast-weather.jpg': (800, 600, 'Weather Station'),
        
        # 活动案例
        'assets/cases/event-conference.jpg': (800, 600, 'Conference'),
        'assets/cases/event-exhibition.jpg': (800, 600, 'Exhibition'),
        'assets/cases/event-wedding.jpg': (800, 600, 'Wedding'),
        'assets/cases/event-concert.jpg': (800, 600, 'Concert'),
        
        # 体育案例
        'assets/cases/sports-stadium.jpg': (800, 600, 'Stadium'),
        'assets/cases/sports-arena.jpg': (800, 600, 'Sports Arena'),
        'assets/cases/sports-gym.jpg': (800, 600, 'Gymnasium'),
        
        # 交通案例
        'assets/cases/transport-airport.jpg': (800, 600, 'Airport'),
        'assets/cases/transport-subway.jpg': (800, 600, 'Subway Station'),
        'assets/cases/transport-bus.jpg': (800, 600, 'Bus Station'),
        
        # 案例详情图片
        'assets/cases/case-before.jpg': (600, 400, 'Before Installation'),
        'assets/cases/case-after.jpg': (600, 400, 'After Installation'),
        'assets/cases/case-process.jpg': (600, 400, 'Installation Process')
    }
    
    for filepath, (width, height, text) in case_images.items():
        if not os.path.exists(filepath):
            create_placeholder_image(width, height, text, filepath)

def create_news_images():
    """创建新闻相关图片"""
    news_images = {
        # 新闻主页
        'assets/news/news-hero.jpg': (1200, 800, 'Latest News'),
        
        # 公司新闻
        'assets/news/company-announcement.jpg': (800, 600, 'Company News'),
        'assets/news/company-expansion.jpg': (800, 600, 'Business Expansion'),
        'assets/news/company-award.jpg': (800, 600, 'Industry Award'),
        'assets/news/company-partnership.jpg': (800, 600, 'New Partnership'),
        
        # 产品新闻
        'assets/news/product-launch.jpg': (800, 600, 'Product Launch'),
        'assets/news/product-innovation.jpg': (800, 600, 'Innovation'),
        'assets/news/product-upgrade.jpg': (800, 600, 'Product Upgrade'),
        
        # 行业新闻
        'assets/news/industry-trend.jpg': (800, 600, 'Industry Trend'),
        'assets/news/industry-report.jpg': (800, 600, 'Market Report'),
        'assets/news/industry-exhibition.jpg': (800, 600, 'Trade Show'),
        
        # 技术新闻
        'assets/news/technology-breakthrough.jpg': (800, 600, 'Tech Breakthrough'),
        'assets/news/technology-research.jpg': (800, 600, 'R&D Progress'),
        
        # 新闻缩略图
        'assets/news/news-thumb-1.jpg': (400, 300, 'News Thumbnail 1'),
        'assets/news/news-thumb-2.jpg': (400, 300, 'News Thumbnail 2'),
        'assets/news/news-thumb-3.jpg': (400, 300, 'News Thumbnail 3')
    }
    
    for filepath, (width, height, text) in news_images.items():
        if not os.path.exists(filepath):
            create_placeholder_image(width, height, text, filepath)

def create_about_images():
    """创建关于我们相关图片"""
    about_images = {
        # 关于我们主页
        'assets/about/about-hero.jpg': (1200, 800, 'About Lianjin LED'),
        
        # 公司图片
        'assets/about/company-building.jpg': (800, 600, 'Company Building'),
        'assets/about/company-factory.jpg': (800, 600, 'Manufacturing'),
        'assets/about/company-office.jpg': (800, 600, 'Office Environment'),
        'assets/about/company-warehouse.jpg': (800, 600, 'Warehouse'),
        
        # 团队图片
        'assets/about/team-leadership.jpg': (800, 600, 'Leadership Team'),
        'assets/about/team-engineering.jpg': (800, 600, 'Engineering Team'),
        'assets/about/team-sales.jpg': (800, 600, 'Sales Team'),
        'assets/about/team-support.jpg': (800, 600, 'Support Team'),
        
        # 生产线图片
        'assets/about/production-line-1.jpg': (800, 600, 'Production Line 1'),
        'assets/about/production-line-2.jpg': (800, 600, 'Production Line 2'),
        'assets/about/quality-control.jpg': (800, 600, 'Quality Control'),
        'assets/about/testing-lab.jpg': (800, 600, 'Testing Laboratory'),
        
        # 认证证书
        'assets/certificates/iso9001.jpg': (600, 400, 'ISO 9001'),
        'assets/certificates/ce-certificate.jpg': (600, 400, 'CE Certificate'),
        'assets/certificates/fcc-certificate.jpg': (600, 400, 'FCC Certificate'),
        'assets/certificates/rohs-certificate.jpg': (600, 400, 'RoHS Certificate')
    }
    
    for filepath, (width, height, text) in about_images.items():
        if not os.path.exists(filepath):
            create_placeholder_image(width, height, text, filepath)

def create_solutions_images():
    """创建解决方案相关图片"""
    solutions_images = {
        # 解决方案主页
        'assets/solutions/solutions-hero.jpg': (1200, 800, 'LED Solutions'),
        
        # 商业解决方案
        'assets/solutions/commercial-retail.jpg': (800, 600, 'Retail Solution'),
        'assets/solutions/commercial-corporate.jpg': (800, 600, 'Corporate Solution'),
        'assets/solutions/commercial-hospitality.jpg': (800, 600, 'Hospitality Solution'),
        
        # 广播解决方案
        'assets/solutions/broadcast-studio.jpg': (800, 600, 'Studio Solution'),
        'assets/solutions/broadcast-control.jpg': (800, 600, 'Control Room'),
        'assets/solutions/broadcast-virtual.jpg': (800, 600, 'Virtual Studio'),
        
        # 活动解决方案
        'assets/solutions/events-stage.jpg': (800, 600, 'Stage Solution'),
        'assets/solutions/events-conference.jpg': (800, 600, 'Conference Solution'),
        'assets/solutions/events-exhibition.jpg': (800, 600, 'Exhibition Solution'),
        
        # 租赁解决方案
        'assets/solutions/rental-portable.jpg': (800, 600, 'Portable Solution'),
        'assets/solutions/rental-modular.jpg': (800, 600, 'Modular Solution'),
        'assets/solutions/rental-quick.jpg': (800, 600, 'Quick Setup'),
        
        # 解决方案图表
        'assets/solutions/solution-diagram-1.jpg': (800, 600, 'Solution Diagram 1'),
        'assets/solutions/solution-diagram-2.jpg': (800, 600, 'Solution Diagram 2'),
        'assets/solutions/workflow-chart.jpg': (800, 600, 'Workflow Chart')
    }
    
    for filepath, (width, height, text) in solutions_images.items():
        if not os.path.exists(filepath):
            create_placeholder_image(width, height, text, filepath)

def create_support_images():
    """创建支持相关图片"""
    support_images = {
        # 支持主页
        'assets/support/support-hero.jpg': (1200, 800, 'Technical Support'),
        
        # 技术支持
        'assets/support/technical-support.jpg': (800, 600, 'Tech Support Team'),
        'assets/support/remote-support.jpg': (800, 600, 'Remote Support'),
        'assets/support/onsite-support.jpg': (800, 600, 'On-site Support'),
        
        # 安装服务
        'assets/support/installation-service.jpg': (800, 600, 'Installation Service'),
        'assets/support/installation-team.jpg': (800, 600, 'Installation Team'),
        'assets/support/installation-tools.jpg': (800, 600, 'Professional Tools'),
        
        # 维护服务
        'assets/support/maintenance-service.jpg': (800, 600, 'Maintenance Service'),
        'assets/support/maintenance-schedule.jpg': (800, 600, 'Maintenance Schedule'),
        'assets/support/spare-parts.jpg': (800, 600, 'Spare Parts'),
        
        # 培训服务
        'assets/support/training-program.jpg': (800, 600, 'Training Program'),
        'assets/support/training-materials.jpg': (800, 600, 'Training Materials'),
        'assets/support/training-certificate.jpg': (800, 600, 'Training Certificate'),
        
        # 下载资源
        'assets/support/user-manual.jpg': (600, 400, 'User Manual'),
        'assets/support/software-download.jpg': (600, 400, 'Software Download'),
        'assets/support/driver-download.jpg': (600, 400, 'Driver Download')
    }
    
    for filepath, (width, height, text) in support_images.items():
        if not os.path.exists(filepath):
            create_placeholder_image(width, height, text, filepath)

def create_contact_images():
    """创建联系我们相关图片"""
    contact_images = {
        # 联系我们主页
        'assets/contact/contact-hero.jpg': (1200, 800, 'Contact Us'),
        
        # 办公地点
        'assets/contact/office-location.jpg': (800, 600, 'Office Location'),
        'assets/contact/office-interior.jpg': (800, 600, 'Office Interior'),
        'assets/contact/meeting-room.jpg': (800, 600, 'Meeting Room'),
        
        # 联系方式图片
        'assets/contact/contact-phone.jpg': (400, 300, 'Phone Contact'),
        'assets/contact/contact-email.jpg': (400, 300, 'Email Contact'),
        'assets/contact/contact-address.jpg': (400, 300, 'Address'),
        
        # 地图相关
        'assets/contact/office-map.jpg': (800, 600, 'Office Map'),
        'assets/contact/location-pin.jpg': (400, 300, 'Location Pin')
    }
    
    for filepath, (width, height, text) in contact_images.items():
        if not os.path.exists(filepath):
            create_placeholder_image(width, height, text, filepath)

def create_logo_and_icons():
    """创建Logo和图标"""
    logo_images = {
        # 公司Logo
        'assets/logos/lianjin-logo.png': (300, 100, 'Lianjin LED Logo'),
        'assets/logos/lianjin-logo-white.png': (300, 100, 'Logo White'),
        'assets/logos/lianjin-logo-dark.png': (300, 100, 'Logo Dark'),
        
        # 产品图标
        'assets/icons/indoor-icon.png': (64, 64, 'Indoor'),
        'assets/icons/outdoor-icon.png': (64, 64, 'Outdoor'),
        'assets/icons/rental-icon.png': (64, 64, 'Rental'),
        'assets/icons/transparent-icon.png': (64, 64, 'Transparent'),
        'assets/icons/creative-icon.png': (64, 64, 'Creative'),
        
        # 服务图标
        'assets/icons/support-icon.png': (64, 64, 'Support'),
        'assets/icons/warranty-icon.png': (64, 64, 'Warranty'),
        'assets/icons/installation-icon.png': (64, 64, 'Installation'),
        'assets/icons/maintenance-icon.png': (64, 64, 'Maintenance')
    }
    
    for filepath, (width, height, text) in logo_images.items():
        if not os.path.exists(filepath):
            # PNG格式用于Logo和图标
            img = Image.new('RGBA', (width, height), color=(248, 249, 250, 255))
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            draw.text((x, y), text, fill=(108, 117, 125, 255), font=font)
            draw.rectangle([0, 0, width-1, height-1], outline=(222, 226, 230, 255), width=1)
            
            img.save(filepath, 'PNG')
            print(f"✅ 创建图标: {filepath}")

def create_background_images():
    """创建背景图片"""
    background_images = {
        # 页面背景
        'assets/backgrounds/hero-bg-1.jpg': (1920, 1080, 'Hero Background 1'),
        'assets/backgrounds/hero-bg-2.jpg': (1920, 1080, 'Hero Background 2'),
        'assets/backgrounds/section-bg-1.jpg': (1920, 600, 'Section Background 1'),
        'assets/backgrounds/section-bg-2.jpg': (1920, 600, 'Section Background 2'),
        
        # 横幅图片
        'assets/banners/promotion-banner.jpg': (1200, 300, 'Promotion Banner'),
        'assets/banners/event-banner.jpg': (1200, 300, 'Event Banner'),
        'assets/banners/product-banner.jpg': (1200, 300, 'Product Banner')
    }
    
    for filepath, (width, height, text) in background_images.items():
        if not os.path.exists(filepath):
            create_placeholder_image(width, height, text, filepath)

def create_image_index():
    """创建图片索引文件"""
    index_content = """# 🖼️ 网站图片文件索引

## 📁 目录结构说明

### assets/products/ - 产品相关图片
- `led-display-hero.jpg` - 主页Hero区域主图 (1200x800px)
- `indoor-led-display.jpg` - 室内LED显示屏 (800x600px)
- `outdoor-led-display.jpg` - 户外LED显示屏 (800x600px)
- `rental-led-display.jpg` - 租赁LED显示屏 (800x600px)
- `transparent-led-display.jpg` - 透明LED显示屏 (800x600px)
- `creative-led-display.jpg` - 创意LED显示屏 (800x600px)
- `industrial-led-solutions.jpg` - 工业LED解决方案 (800x600px)

#### Fine Pitch LED 产品页面图片
- `fine-pitch-led-main.jpg` - Fine Pitch主图 (1200x800px)
- `fine-pitch-p0.9.jpg` - P0.9产品图 (600x400px)
- `fine-pitch-p1.25.jpg` - P1.25产品图 (600x400px)
- `fine-pitch-p1.56.jpg` - P1.56产品图 (600x400px)
- `fine-pitch-control-room.jpg` - 控制室应用 (800x600px)
- `fine-pitch-broadcast.jpg` - 广播演播室应用 (800x600px)

#### Outdoor LED 产品页面图片
- `outdoor-led-main.jpg` - 户外LED主图 (1200x800px)
- `outdoor-billboard.jpg` - 户外广告牌 (800x600px)
- `outdoor-stadium.jpg` - 体育场显示屏 (800x600px)
- `outdoor-street.jpg` - 街道显示屏 (800x600px)

#### Rental LED 产品页面图片
- `rental-led-main.jpg` - 租赁LED主图 (1200x800px)
- `rental-stage.jpg` - 舞台显示屏 (800x600px)
- `rental-event.jpg` - 活动显示屏 (800x600px)
- `rental-concert.jpg` - 演唱会显示屏 (800x600px)

#### Creative LED 产品页面图片
- `creative-led-main.jpg` - 创意LED主图 (1200x800px)
- `creative-curved.jpg` - 弯曲显示屏 (800x600px)
- `creative-sphere.jpg` - 球形显示屏 (800x600px)
- `creative-irregular.jpg` - 异形显示屏 (800x600px)

#### Transparent LED 产品页面图片
- `transparent-led-main.jpg` - 透明LED主图 (1200x800px)
- `transparent-window.jpg` - 橱窗显示屏 (800x600px)
- `transparent-facade.jpg` - 建筑幕墙 (800x600px)
- `transparent-retail.jpg` - 零售橱窗 (800x600px)

### assets/cases/ - 案例相关图片
- `cases-hero.jpg` - 案例页面主图 (1200x800px)
- `commercial-*.jpg` - 商业案例图片 (800x600px)
- `broadcast-*.jpg` - 广播案例图片 (800x600px)
- `event-*.jpg` - 活动案例图片 (800x600px)
- `sports-*.jpg` - 体育案例图片 (800x600px)
- `transport-*.jpg` - 交通案例图片 (800x600px)

### assets/news/ - 新闻相关图片
- `news-hero.jpg` - 新闻页面主图 (1200x800px)
- `company-*.jpg` - 公司新闻图片 (800x600px)
- `product-*.jpg` - 产品新闻图片 (800x600px)
- `industry-*.jpg` - 行业新闻图片 (800x600px)
- `technology-*.jpg` - 技术新闻图片 (800x600px)
- `news-thumb-*.jpg` - 新闻缩略图 (400x300px)

### assets/about/ - 关于我们相关图片
- `about-hero.jpg` - 关于我们主图 (1200x800px)
- `company-*.jpg` - 公司图片 (800x600px)
- `team-*.jpg` - 团队图片 (800x600px)
- `production-*.jpg` - 生产线图片 (800x600px)

### assets/solutions/ - 解决方案相关图片
- `solutions-hero.jpg` - 解决方案主图 (1200x800px)
- `commercial-*.jpg` - 商业解决方案 (800x600px)
- `broadcast-*.jpg` - 广播解决方案 (800x600px)
- `events-*.jpg` - 活动解决方案 (800x600px)
- `rental-*.jpg` - 租赁解决方案 (800x600px)

### assets/support/ - 支持相关图片
- `support-hero.jpg` - 支持页面主图 (1200x800px)
- `technical-*.jpg` - 技术支持图片 (800x600px)
- `installation-*.jpg` - 安装服务图片 (800x600px)
- `maintenance-*.jpg` - 维护服务图片 (800x600px)
- `training-*.jpg` - 培训服务图片 (800x600px)

### assets/contact/ - 联系我们相关图片
- `contact-hero.jpg` - 联系页面主图 (1200x800px)
- `office-*.jpg` - 办公室图片 (800x600px)
- `contact-*.jpg` - 联系方式图片 (400x300px)

### assets/logos/ - Logo和品牌图片
- `lianjin-logo.png` - 主Logo (300x100px)
- `lianjin-logo-white.png` - 白色Logo (300x100px)
- `lianjin-logo-dark.png` - 深色Logo (300x100px)

### assets/icons/ - 图标文件
- `*-icon.png` - 各种功能图标 (64x64px)

### assets/certificates/ - 认证证书
- `iso9001.jpg` - ISO 9001认证 (600x400px)
- `ce-certificate.jpg` - CE认证 (600x400px)
- `fcc-certificate.jpg` - FCC认证 (600x400px)
- `rohs-certificate.jpg` - RoHS认证 (600x400px)

### assets/backgrounds/ - 背景图片
- `hero-bg-*.jpg` - Hero区域背景 (1920x1080px)
- `section-bg-*.jpg` - 章节背景 (1920x600px)

### assets/banners/ - 横幅图片
- `*-banner.jpg` - 各种横幅图片 (1200x300px)

## 🔄 图片替换说明

1. **保持文件名不变** - 直接替换同名文件即可
2. **保持尺寸比例** - 建议使用相同或相近的尺寸
3. **优化文件大小** - 建议每张图片小于500KB
4. **使用合适格式** - 照片用JPG，图标用PNG
5. **确保图片质量** - 使用高质量的产品图片

## 📋 替换优先级

### 高优先级（必须替换）
1. `assets/products/led-display-hero.jpg` - 主页横幅
2. `assets/products/indoor-led-display.jpg` - 室内LED
3. `assets/products/outdoor-led-display.jpg` - 户外LED
4. `assets/products/rental-led-display.jpg` - 租赁LED
5. `assets/products/transparent-led-display.jpg` - 透明LED
6. `assets/products/creative-led-display.jpg` - 创意LED

### 中优先级（建议替换）
1. 各产品页面的主图
2. 案例页面图片
3. 关于我们页面图片

### 低优先级（可选替换）
1. 新闻图片
2. 支持页面图片
3. 背景图片
"""
    
    with open('assets/IMAGE_INDEX.md', 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print("✅ 图片索引文件已创建: assets/IMAGE_INDEX.md")

def main():
    """主函数"""
    print("🖼️  创建完整的网站图片文件结构")
    print("=" * 60)
    
    # 创建目录结构
    print("\n📁 创建目录结构...")
    create_directory_structure()
    
    # 创建各类图片
    print("\n🎨 创建产品图片...")
    create_product_images()
    
    print("\n📰 创建案例图片...")
    create_case_images()
    
    print("\n📢 创建新闻图片...")
    create_news_images()
    
    print("\n🏢 创建关于我们图片...")
    create_about_images()
    
    print("\n💡 创建解决方案图片...")
    create_solutions_images()
    
    print("\n🛠️ 创建支持图片...")
    create_support_images()
    
    print("\n📞 创建联系我们图片...")
    create_contact_images()
    
    print("\n🎯 创建Logo和图标...")
    create_logo_and_icons()
    
    print("\n🌄 创建背景图片...")
    create_background_images()
    
    print("\n📋 创建图片索引...")
    create_image_index()
    
    print("\n" + "=" * 60)
    print("🎉 图片文件结构创建完成！")
    print("\n📊 统计信息:")
    
    # 统计创建的文件数量
    total_files = 0
    for root, dirs, files in os.walk('assets'):
        total_files += len([f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))])
    
    print(f"   📁 创建目录: {len([d for d in os.listdir('assets') if os.path.isdir(os.path.join('assets', d))])} 个")
    print(f"   🖼️  创建图片: {total_files} 张")
    
    print("\n📝 接下来您可以:")
    print("   1. 查看 assets/IMAGE_INDEX.md 了解所有图片的用途")
    print("   2. 将您的真实图片替换对应的占位符图片")
    print("   3. 保持文件名不变，直接覆盖即可")
    print("   4. 建议优先替换高优先级的图片")
    
    print("\n💡 提示:")
    print("   • 所有图片都已按照网站实际需要的尺寸创建")
    print("   • 文件名与HTML中引用的路径完全对应")
    print("   • 直接替换同名文件即可生效")
    print("   • 建议使用高质量的产品图片")

if __name__ == "__main__":
    main()
