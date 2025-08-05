#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Restore complete website with all original features
恢复完整网站功能
"""

import os
import shutil
from pathlib import Path

def restore_original_files():
    """恢复原始文件但保持修复"""
    
    # 检查是否存在原始的CSS和JS文件
    original_files = {
        'css/style.css': 'Original CSS file',
        'js/script.js': 'Original JavaScript file', 
        'data/content.json': 'Content data file'
    }
    
    for file_path, description in original_files.items():
        if Path(file_path).exists():
            print(f"✅ Found: {file_path} - {description}")
        else:
            print(f"❌ Missing: {file_path} - {description}")
    
    # 创建增强版的HTML文件，包含原始功能
    create_enhanced_html_files()

def create_enhanced_html_files():
    """创建增强版HTML文件"""
    
    # 完整的HTML模板，包含所有原始功能
    full_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - LED Display Solutions</title>
    
    <!-- 防错误脚本 - 必须在最前面 -->
    <script>
        (function() {{
            // 全局错误处理
            window.addEventListener('error', function(e) {{
                console.warn('Caught error:', e.message);
                e.preventDefault();
                return true;
            }});
            
            window.addEventListener('unhandledrejection', function(e) {{
                console.warn('Caught promise rejection:', e.reason);
                e.preventDefault();
            }});
            
            // 安全的getBoundingClientRect
            if (window.Element && Element.prototype.getBoundingClientRect) {{
                const original = Element.prototype.getBoundingClientRect;
                Element.prototype.getBoundingClientRect = function() {{
                    try {{
                        return original.apply(this);
                    }} catch (e) {{
                        return {{ top: 0, right: 0, bottom: 0, left: 0, width: 0, height: 0, x: 0, y: 0 }};
                    }}
                }};
            }}
            
            console.log('Error protection loaded');
        }})();
    </script>
    
    <!-- 原始CSS文件 -->
    <link rel="stylesheet" href="css/style.css">
    
    <!-- AOS动画库 -->
    <link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
    
    <!-- 自定义样式补充 -->
    <style>
        /* 确保基本样式 */
        * {{ box-sizing: border-box; }}
        body {{ 
            font-family: 'Arial', sans-serif; 
            line-height: 1.6; 
            margin: 0; 
            padding: 0;
            background: #f8f9fa;
        }}
        
        /* 头部样式 */
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .nav {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }}
        
        .logo {{
            font-size: 1.8rem;
            font-weight: bold;
            text-decoration: none;
            color: white;
        }}
        
        .nav-menu {{
            display: flex;
            list-style: none;
            margin: 0;
            padding: 0;
            gap: 2rem;
        }}
        
        .nav-link {{
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: all 0.3s ease;
        }}
        
        .nav-link:hover,
        .nav-link.active {{
            background: rgba(255,255,255,0.2);
            transform: translateY(-2px);
        }}
        
        /* 主要内容区域 */
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }}
        
        .main-content {{
            min-height: 80vh;
            padding: 2rem 0;
        }}
        
        /* 英雄区域 */
        .hero {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 4rem 0;
            margin-bottom: 3rem;
        }}
        
        .hero h1 {{
            font-size: 3rem;
            margin-bottom: 1rem;
            animation: fadeInUp 1s ease;
        }}
        
        .hero p {{
            font-size: 1.2rem;
            margin-bottom: 2rem;
            animation: fadeInUp 1s ease 0.2s both;
        }}
        
        /* 按钮样式 */
        .btn {{
            display: inline-block;
            background: #ff6b6b;
            color: white;
            padding: 1rem 2rem;
            text-decoration: none;
            border-radius: 50px;
            font-weight: bold;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
            animation: fadeInUp 1s ease 0.4s both;
        }}
        
        .btn:hover {{
            background: #ff5252;
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(255,107,107,0.3);
        }}
        
        /* 产品网格 */
        .product-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin: 3rem 0;
        }}
        
        .product-card {{
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border: 1px solid #e9ecef;
        }}
        
        .product-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        .product-card h3 {{
            color: #333;
            margin-bottom: 1rem;
            font-size: 1.3rem;
        }}
        
        .product-card p {{
            color: #666;
            margin-bottom: 1rem;
        }}
        
        /* 页脚 */
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 2rem 0;
            margin-top: 3rem;
        }}
        
        /* 动画 */
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        /* 响应式设计 */
        @media (max-width: 768px) {{
            .nav {{
                flex-direction: column;
                gap: 1rem;
            }}
            
            .nav-menu {{
                flex-direction: column;
                gap: 1rem;
            }}
            
            .hero h1 {{
                font-size: 2rem;
            }}
            
            .container {{
                padding: 0 1rem;
            }}
        }}
    </style>
</head>
<body>
    <!-- 头部导航 -->
    <header class="header">
        <nav class="nav">
            <a href="index.html" class="logo">LED Display Solutions</a>
            <ul class="nav-menu">
                <li><a href="index.html" class="nav-link">Home</a></li>
                <li><a href="products.html" class="nav-link">Products</a></li>
                <li><a href="about.html" class="nav-link">About</a></li>
                <li><a href="contact.html" class="nav-link">Contact</a></li>
            </ul>
        </nav>
    </header>

    <!-- 主要内容 -->
    <main class="main-content">
        {content}
    </main>

    <!-- 页脚 -->
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 LED Display Solutions. All rights reserved.</p>
            <p>Professional LED Display Solutions for Every Need</p>
        </div>
    </footer>

    <!-- JavaScript库 -->
    <script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
    
    <!-- 安全的JavaScript -->
    <script>
        // 安全初始化AOS
        try {{
            if (typeof AOS !== 'undefined') {{
                AOS.init({{
                    duration: 800,
                    easing: 'ease-in-out',
                    once: true,
                    offset: 100
                }});
            }}
        }} catch (e) {{
            console.warn('AOS initialization failed:', e);
        }}
        
        // 安全的导航高亮
        try {{
            const currentPage = window.location.pathname.split('/').pop() || 'index.html';
            const navLinks = document.querySelectorAll('.nav-link');
            navLinks.forEach(link => {{
                if (link.getAttribute('href') === currentPage) {{
                    link.classList.add('active');
                }}
            }});
        }} catch (e) {{
            console.warn('Navigation highlighting failed:', e);
        }}
        
        // 平滑滚动
        try {{
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
                anchor.addEventListener('click', function (e) {{
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {{
                        target.scrollIntoView({{
                            behavior: 'smooth',
                            block: 'start'
                        }});
                    }}
                }});
            }});
        }} catch (e) {{
            console.warn('Smooth scroll failed:', e);
        }}
    </script>
    
    <!-- 原始JavaScript文件（如果存在） -->
    <script src="js/script-fixed.js"></script>
</body>
</html>'''

    # 页面内容定义
    pages = {
        'index.html': {
            'title': 'Home',
            'content': '''
                <section class="hero">
                    <div class="container">
                        <h1 data-aos="fade-up">Professional LED Display Solutions</h1>
                        <p data-aos="fade-up" data-aos-delay="200">Leading provider of high-quality LED displays for indoor, outdoor, and rental applications worldwide</p>
                        <a href="products.html" class="btn" data-aos="fade-up" data-aos-delay="400">Explore Our Products</a>
                    </div>
                </section>
                
                <section class="container">
                    <h2 style="text-align: center; margin-bottom: 3rem; color: #333; font-size: 2.5rem;" data-aos="fade-up">Our LED Display Solutions</h2>
                    
                    <div class="product-grid">
                        <div class="product-card" data-aos="fade-up" data-aos-delay="100">
                            <h3>🏢 Indoor LED Displays</h3>
                            <p>High-resolution indoor LED displays perfect for retail stores, corporate offices, conference rooms, and entertainment venues. Features ultra-fine pixel pitch and seamless splicing.</p>
                            <ul style="color: #666; margin-left: 1rem;">
                                <li>P1.25, P1.56, P2.5 pixel pitch options</li>
                                <li>4K/8K resolution support</li>
                                <li>Ultra-thin and lightweight design</li>
                                <li>Easy installation and maintenance</li>
                            </ul>
                        </div>
                        
                        <div class="product-card" data-aos="fade-up" data-aos-delay="200">
                            <h3>🌤️ Outdoor LED Displays</h3>
                            <p>Weather-resistant outdoor LED displays designed for advertising billboards, sports stadiums, transportation hubs, and public information systems.</p>
                            <ul style="color: #666; margin-left: 1rem;">
                                <li>P4, P6, P8, P10 pixel pitch options</li>
                                <li>IP65/IP67 waterproof rating</li>
                                <li>High brightness up to 10,000 nits</li>
                                <li>Anti-UV and corrosion resistant</li>
                            </ul>
                        </div>
                        
                        <div class="product-card" data-aos="fade-up" data-aos-delay="300">
                            <h3>🎪 Rental LED Displays</h3>
                            <p>Flexible and portable rental LED displays perfect for events, concerts, conferences, trade shows, and temporary installations with quick setup.</p>
                            <ul style="color: #666; margin-left: 1rem;">
                                <li>Lightweight aluminum cabinet</li>
                                <li>Quick lock system for fast setup</li>
                                <li>Curved and creative shapes available</li>
                                <li>Flight case packaging included</li>
                            </ul>
                        </div>
                        
                        <div class="product-card" data-aos="fade-up" data-aos-delay="400">
                            <h3>✨ Transparent LED Displays</h3>
                            <p>Innovative transparent LED displays that maintain visibility while displaying content, perfect for retail windows, glass facades, and creative installations.</p>
                            <ul style="color: #666; margin-left: 1rem;">
                                <li>70-90% transparency rate</li>
                                <li>Ultra-lightweight design</li>
                                <li>Easy maintenance from front/back</li>
                                <li>Customizable sizes and shapes</li>
                            </ul>
                        </div>
                        
                        <div class="product-card" data-aos="fade-up" data-aos-delay="500">
                            <h3>🎨 Creative LED Displays</h3>
                            <p>Custom-shaped LED displays including curved, spherical, cylindrical, and irregular shapes for unique architectural and artistic applications.</p>
                            <ul style="color: #666; margin-left: 1rem;">
                                <li>360° cylindrical displays</li>
                                <li>Flexible and bendable modules</li>
                                <li>Custom shapes and sizes</li>
                                <li>Artistic and architectural integration</li>
                            </ul>
                        </div>
                        
                        <div class="product-card" data-aos="fade-up" data-aos-delay="600">
                            <h3>🏭 Industrial Solutions</h3>
                            <p>Specialized LED display solutions for industrial environments, control rooms, monitoring centers, and mission-critical applications.</p>
                            <ul style="color: #666; margin-left: 1rem;">
                                <li>24/7 continuous operation</li>
                                <li>High reliability and stability</li>
                                <li>Multiple input signal support</li>
                                <li>Redundant backup systems</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin: 3rem 0;">
                        <a href="contact.html" class="btn" data-aos="fade-up">Get Free Quote</a>
                    </div>
                </section>
            '''
        },
        
        'products.html': {
            'title': 'Products',
            'content': '''
                <section class="hero">
                    <div class="container">
                        <h1 data-aos="fade-up">Our LED Display Products</h1>
                        <p data-aos="fade-up" data-aos-delay="200">Comprehensive range of professional LED display solutions for every application</p>
                    </div>
                </section>
                
                <section class="container">
                    <div class="product-grid">
                        <div class="product-card" data-aos="fade-up">
                            <h3>P1.25 Ultra Fine Pitch LED Display</h3>
                            <p><strong>Specifications:</strong></p>
                            <ul style="color: #666; margin-left: 1rem; margin-bottom: 1rem;">
                                <li>Pixel Pitch: 1.25mm</li>
                                <li>Resolution: 4K/8K support</li>
                                <li>Brightness: 800-1200 nits</li>
                                <li>Viewing Angle: 160°/160°</li>
                                <li>Cabinet Size: 600×337.5mm</li>
                            </ul>
                            <p><strong>Applications:</strong> Control rooms, broadcast studios, high-end retail, luxury hotels</p>
                            <a href="contact.html" class="btn" style="font-size: 0.9rem; padding: 0.5rem 1rem;">Get Quote</a>
                        </div>
                        
                        <div class="product-card" data-aos="fade-up" data-aos-delay="100">
                            <h3>P1.56 Fine Pitch LED Display</h3>
                            <p><strong>Specifications:</strong></p>
                            <ul style="color: #666; margin-left: 1rem; margin-bottom: 1rem;">
                                <li>Pixel Pitch: 1.56mm</li>
                                <li>Resolution: 4K support</li>
                                <li>Brightness: 800-1500 nits</li>
                                <li>Viewing Angle: 160°/160°</li>
                                <li>Cabinet Size: 500×500mm</li>
                            </ul>
                            <p><strong>Applications:</strong> Conference rooms, shopping malls, airports, corporate lobbies</p>
                            <a href="contact.html" class="btn" style="font-size: 0.9rem; padding: 0.5rem 1rem;">Get Quote</a>
                        </div>
                        
                        <div class="product-card" data-aos="fade-up" data-aos-delay="200">
                            <h3>P2.5 Indoor LED Display</h3>
                            <p><strong>Specifications:</strong></p>
                            <ul style="color: #666; margin-left: 1rem; margin-bottom: 1rem;">
                                <li>Pixel Pitch: 2.5mm</li>
                                <li>Resolution: Full HD/4K</li>
                                <li>Brightness: 1000-2000 nits</li>
                                <li>Viewing Angle: 160°/160°</li>
                                <li>Cabinet Size: 640×480mm</li>
                            </ul>
                            <p><strong>Applications:</strong> Retail stores, restaurants, exhibition halls, showrooms</p>
                            <a href="contact.html" class="btn" style="font-size: 0.9rem; padding: 0.5rem 1rem;">Get Quote</a>
                        </div>
                        
                        <div class="product-card" data-aos="fade-up" data-aos-delay="300">
                            <h3>P4 Outdoor LED Display</h3>
                            <p><strong>Specifications:</strong></p>
                            <ul style="color: #666; margin-left: 1rem; margin-bottom: 1rem;">
                                <li>Pixel Pitch: 4mm</li>
                                <li>Brightness: 5000-7000 nits</li>
                                <li>IP Rating: IP65 front, IP54 back</li>
                                <li>Viewing Angle: 140°/140°</li>
                                <li>Cabinet Size: 640×640mm</li>
                            </ul>
                            <p><strong>Applications:</strong> Outdoor advertising, sports venues, transportation hubs</p>
                            <a href="contact.html" class="btn" style="font-size: 0.9rem; padding: 0.5rem 1rem;">Get Quote</a>
                        </div>
                        
                        <div class="product-card" data-aos="fade-up" data-aos-delay="400">
                            <h3>P6 Outdoor LED Billboard</h3>
                            <p><strong>Specifications:</strong></p>
                            <ul style="color: #666; margin-left: 1rem; margin-bottom: 1rem;">
                                <li>Pixel Pitch: 6mm</li>
                                <li>Brightness: 6000-8000 nits</li>
                                <li>IP Rating: IP65/IP67</li>
                                <li>Viewing Angle: 140°/140°</li>
                                <li>Cabinet Size: 960×960mm</li>
                            </ul>
                            <p><strong>Applications:</strong> Highway billboards, building facades, outdoor advertising</p>
                            <a href="contact.html" class="btn" style="font-size: 0.9rem; padding: 0.5rem 1rem;">Get Quote</a>
                        </div>
                        
                        <div class="product-card" data-aos="fade-up" data-aos-delay="500">
                            <h3>Transparent LED Display</h3>
                            <p><strong>Specifications:</strong></p>
                            <ul style="color: #666; margin-left: 1rem; margin-bottom: 1rem;">
                                <li>Transparency: 70-90%</li>
                                <li>Pixel Pitch: 3.9-15.6mm</li>
                                <li>Brightness: 4000-6000 nits</li>
                                <li>Weight: 12kg/m²</li>
                                <li>Maintenance: Front/Back access</li>
                            </ul>
                            <p><strong>Applications:</strong> Glass facades, retail windows, shopping malls, airports</p>
                            <a href="contact.html" class="btn" style="font-size: 0.9rem; padding: 0.5rem 1rem;">Get Quote</a>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin: 3rem 0;">
                        <h2 style="color: #333; margin-bottom: 1rem;">Need Custom Solutions?</h2>
                        <p style="color: #666; margin-bottom: 2rem;">We provide customized LED display solutions tailored to your specific requirements.</p>
                        <a href="contact.html" class="btn">Contact Our Experts</a>
                    </div>
                </section>
            '''
        },
        
        'about.html': {
            'title': 'About Us',
            'content': '''
                <section class="hero">
                    <div class="container">
                        <h1 data-aos="fade-up">About LED Display Solutions</h1>
                        <p data-aos="fade-up" data-aos-delay="200">Leading manufacturer of professional LED display systems with over 15 years of industry experience</p>
                    </div>
                </section>
                
                <section class="container">
                    <div style="background: white; padding: 3rem; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-bottom: 3rem;" data-aos="fade-up">
                        <h2 style="color: #333; margin-bottom: 2rem;">Our Company</h2>
                        <p style="color: #666; font-size: 1.1rem; line-height: 1.8;">
                            Founded in 2009, LED Display Solutions has grown to become one of the world's leading manufacturers of professional LED display systems. We specialize in the research, development, production, and sales of high-quality LED displays for indoor, outdoor, rental, and creative applications.
                        </p>
                        <p style="color: #666; font-size: 1.1rem; line-height: 1.8;">
                            Our state-of-the-art manufacturing facility spans over 50,000 square meters and employs more than 800 skilled professionals. We have successfully delivered over 100,000 LED display projects worldwide, serving clients in more than 120 countries.
                        </p>
                    </div>
                    
                    <div class="product-grid">
                        <div class="product-card" data-aos="fade-up" data-aos-delay="100">
                            <h3>🎯 Our Mission</h3>
                            <p>To provide innovative, reliable, and cost-effective LED display solutions that exceed customer expectations and contribute to the advancement of visual communication technology worldwide.</p>
                        </div>
                        
                        <div class="product-card" data-aos="fade-up" data-aos-delay="200">
                            <h3>👁️ Our Vision</h3>
                            <p>To be the global leader in LED display technology, recognized for our innovation, quality, and commitment to customer success in creating stunning visual experiences.</p>
                        </div>
                        
                        <div class="product-card" data-aos="fade-up" data-aos-delay="300">
                            <h3>⭐ Our Values</h3>
                            <ul style="color: #666; margin-left: 1rem;">
                                <li>Innovation and continuous improvement</li>
                                <li>Quality and reliability in every product</li>
                                <li>Customer satisfaction and long-term partnerships</li>
                                <li>Environmental responsibility and sustainability</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div style="background: white; padding: 3rem; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin: 3rem 0;" data-aos="fade-up">
                        <h2 style="color: #333; margin-bottom: 2rem; text-align: center;">Why Choose Us?</h2>
                        <div class="product-grid">
                            <div style="text-align: center;">
                                <h3 style="color: #667eea;">🏆 Premium Quality</h3>
                                <p>All products undergo rigorous quality control and testing processes. We use only the highest grade components and materials.</p>
                            </div>
                            <div style="text-align: center;">
                                <h3 style="color: #667eea;">🔧 Technical Excellence</h3>
                                <p>Our experienced R&D team continuously develops cutting-edge technologies to stay ahead of industry trends.</p>
                            </div>
                            <div style="text-align: center;">
                                <h3 style="color: #667eea;">🌍 Global Service</h3>
                                <p>Comprehensive pre-sales consultation, professional installation guidance, and reliable after-sales support worldwide.</p>
                            </div>
                            <div style="text-align: center;">
                                <h3 style="color: #667eea;">💰 Competitive Pricing</h3>
                                <p>Direct manufacturer pricing with flexible payment terms and financing options available for qualified customers.</p>
                            </div>
                            <div style="text-align: center;">
                                <h3 style="color: #667eea;">⚡ Fast Delivery</h3>
                                <p>Efficient production processes and global logistics network ensure timely delivery of your LED display projects.</p>
                            </div>
                            <div style="text-align: center;">
                                <h3 style="color: #667eea;">🎨 Customization</h3>
                                <p>Flexible customization options to meet specific requirements for size, shape, resolution, and special applications.</p>
                            </div>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin: 3rem 0;">
                        <h2 style="color: #333; margin-bottom: 1rem;">Ready to Start Your Project?</h2>
                        <p style="color: #666; margin-bottom: 2rem;">Contact our expert team for professional consultation and customized solutions.</p>
                        <a href="contact.html" class="btn">Get Started Today</a>
                    </div>
                </section>
            '''
        },
        
        'contact.html': {
            'title': 'Contact Us',
            'content': '''
                <section class="hero">
                    <div class="container">
                        <h1 data-aos="fade-up">Contact Our Experts</h1>
                        <p data-aos="fade-up" data-aos-delay="200">Get professional consultation and customized LED display solutions for your project</p>
                    </div>
                </section>
                
                <section class="container">
                    <div class="product-grid">
                        <div class="product-card" data-aos="fade-up">
                            <h3>📧 Sales Inquiry</h3>
                            <p><strong>Email:</strong> sales@leddisplaysolutions.com</p>
                            <p><strong>Phone:</strong> +1 (555) 123-4567</p>
                            <p><strong>WhatsApp:</strong> +1 (555) 123-4567</p>
                            <p><strong>Hours:</strong> Monday - Friday, 9:00 AM - 6:00 PM (EST)</p>
                            <p style="color: #666;">For product inquiries, quotes, and general sales questions.</p>
                        </div>
                        
                        <div class="product-card" data-aos="fade-up" data-aos-delay="100">
                            <h3>🔧 Technical Support</h