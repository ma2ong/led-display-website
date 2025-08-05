#!/usr/bin/env python3
"""
Fix Enhanced Admin System - Ensure proper database initialization
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

def init_enhanced_database():
    """Initialize the enhanced admin database with all required tables"""
    
    # Remove existing database if it exists to start fresh
    if os.path.exists('enhanced_admin.db'):
        os.remove('enhanced_admin.db')
        print("🗑️  Removed existing database")
    
    conn = sqlite3.connect('enhanced_admin.db')
    cursor = conn.cursor()
    
    print("📊 Creating database tables...")
    
    # Users table for admin authentication
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    print("✓ Users table created")
    
    # Enhanced content management table
    cursor.execute('''
        CREATE TABLE page_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_name TEXT NOT NULL,
            section_name TEXT NOT NULL,
            content_type TEXT NOT NULL DEFAULT 'text',
            content_data TEXT,
            image_url TEXT,
            video_url TEXT,
            parameters TEXT,
            sort_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ Page content table created")
    
    # Products table
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            specifications TEXT,
            image_url TEXT,
            video_url TEXT,
            price_range TEXT,
            features TEXT,
            applications TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ Products table created")
    
    # Solutions table
    cursor.execute('''
        CREATE TABLE solutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT,
            description TEXT,
            content TEXT,
            image_url TEXT,
            video_url TEXT,
            case_studies TEXT,
            benefits TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ Solutions table created")
    
    # Cases table
    cursor.execute('''
        CREATE TABLE cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            client TEXT,
            industry TEXT,
            location TEXT,
            description TEXT,
            challenge TEXT,
            solution TEXT,
            results TEXT,
            image_url TEXT,
            video_url TEXT,
            gallery_images TEXT,
            project_date DATE,
            is_featured BOOLEAN DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ Cases table created")
    
    # News table
    cursor.execute('''
        CREATE TABLE news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT,
            summary TEXT,
            content TEXT,
            author TEXT,
            image_url TEXT,
            video_url TEXT,
            tags TEXT,
            publish_date DATE,
            is_published BOOLEAN DEFAULT 0,
            is_featured BOOLEAN DEFAULT 0,
            views INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ News table created")
    
    # Support content table
    cursor.execute('''
        CREATE TABLE support_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            category TEXT,
            tags TEXT,
            file_url TEXT,
            download_count INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ Support content table created")
    
    # Inquiries table
    cursor.execute('''
        CREATE TABLE inquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            company TEXT,
            phone TEXT,
            country TEXT,
            product_interest TEXT,
            message TEXT,
            status TEXT DEFAULT 'new',
            assigned_to TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ Inquiries table created")
    
    # Create default admin user
    password_hash = generate_password_hash('admin123')
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, role, is_active)
        VALUES (?, ?, ?, ?, ?)
    ''', ('admin', 'admin@lianjinled.com', password_hash, 'admin', True))
    print("✓ Default admin user created")
    
    # Insert sample content for demonstration
    sample_content = [
        # Home page content
        ('home', 'Hero Section', 'mixed', 
         '<h1>Welcome to Lianjin LED</h1><p>Leading manufacturer of professional LED display solutions worldwide</p>',
         '/assets/hero-image.jpg', '', 
         '{"containerWidth": "full", "textAlign": "center", "backgroundColor": "#667eea"}', 0, True),
        
        ('home', 'Company Overview', 'text',
         '<h2>About Lianjin LED</h2><p>With over 15 years of experience in LED display technology, we provide innovative solutions for retail, sports, advertising, and corporate environments.</p>',
         '', '', '{"containerWidth": "container", "textAlign": "left"}', 1, True),
        
        ('home', 'Featured Products', 'mixed',
         '<h2>Our Featured Products</h2><p>Discover our latest LED display innovations</p>',
         '/assets/products-showcase.jpg', '', 
         '{"containerWidth": "container", "textAlign": "center"}', 2, True),
        
        # About page content
        ('about', 'Company History', 'text',
         '<h2>Our Story</h2><p>Founded in 2008, Lianjin LED has grown from a small startup to a leading LED display manufacturer serving clients globally.</p>',
         '', '', '{"containerWidth": "container", "textAlign": "left"}', 0, True),
        
        ('about', 'Team Photo', 'image',
         'Our dedicated team of engineers and professionals',
         '/assets/team-photo.jpg', '', 
         '{"containerWidth": "container", "textAlign": "center"}', 1, True),
        
        ('about', 'Mission Statement', 'text',
         '<h2>Our Mission</h2><p>To deliver cutting-edge LED display solutions that exceed customer expectations and drive business success.</p>',
         '', '', '{"containerWidth": "container", "textAlign": "left"}', 2, True),
        
        # Products page content
        ('products', 'Product Categories', 'text',
         '<h2>LED Display Solutions</h2><p>Explore our comprehensive range of LED display products designed for various applications.</p>',
         '', '', '{"containerWidth": "container", "textAlign": "center"}', 0, True),
        
        ('products', 'Indoor LED Displays', 'mixed',
         '<h3>Indoor LED Displays</h3><p>High-resolution displays perfect for retail, corporate, and entertainment venues.</p>',
         '/assets/indoor-led.jpg', '', 
         '{"containerWidth": "container", "textAlign": "left"}', 1, True),
        
        ('products', 'Outdoor LED Displays', 'mixed',
         '<h3>Outdoor LED Displays</h3><p>Weather-resistant displays built for outdoor advertising and public information.</p>',
         '/assets/outdoor-led.jpg', '', 
         '{"containerWidth": "container", "textAlign": "left"}', 2, True),
        
        # Solutions page content
        ('solutions', 'Industry Solutions', 'text',
         '<h2>Tailored LED Solutions</h2><p>We provide customized LED display solutions for various industries and applications.</p>',
         '', '', '{"containerWidth": "container", "textAlign": "center"}', 0, True),
        
        ('solutions', 'Retail Solutions', 'mixed',
         '<h3>Retail & Shopping Centers</h3><p>Enhance customer experience with dynamic digital displays.</p>',
         '/assets/retail-solution.jpg', '', 
         '{"containerWidth": "container", "textAlign": "left"}', 1, True),
        
        # Cases page content
        ('cases', 'Success Stories', 'text',
         '<h2>Our Success Stories</h2><p>Discover how we have helped businesses transform their visual communication.</p>',
         '', '', '{"containerWidth": "container", "textAlign": "center"}', 0, True),
        
        ('cases', 'Featured Case Study', 'mixed',
         '<h3>Times Square Digital Billboard</h3><p>A landmark installation showcasing our premium outdoor LED technology.</p>',
         '/assets/times-square-case.jpg', 'https://www.youtube.com/watch?v=example', 
         '{"containerWidth": "container", "textAlign": "left"}', 1, True),
        
        # News page content
        ('news', 'Latest News', 'text',
         '<h2>Company News & Updates</h2><p>Stay informed about our latest developments, product launches, and industry insights.</p>',
         '', '', '{"containerWidth": "container", "textAlign": "center"}', 0, True),
        
        # Support page content
        ('support', 'Technical Support', 'text',
         '<h2>Technical Support</h2><p>Get the help you need with our comprehensive support resources and expert assistance.</p>',
         '', '', '{"containerWidth": "container", "textAlign": "center"}', 0, True),
        
        ('support', 'Documentation', 'mixed',
         '<h3>Product Documentation</h3><p>Access user manuals, installation guides, and technical specifications.</p>',
         '/assets/documentation.jpg', '', 
         '{"containerWidth": "container", "textAlign": "left"}', 1, True),
        
        # Contact page content
        ('contact', 'Contact Information', 'text',
         '<h2>Get in Touch</h2><p>Contact our team for inquiries, support, or partnership opportunities.</p>',
         '', '', '{"containerWidth": "container", "textAlign": "center"}', 0, True),
        
        ('contact', 'Office Locations', 'mixed',
         '<h3>Our Offices</h3><p>Visit us at our global locations or reach out through our contact form.</p>',
         '/assets/office-locations.jpg', '', 
         '{"containerWidth": "container", "textAlign": "left"}', 1, True),
    ]
    
    for content in sample_content:
        cursor.execute('''
            INSERT INTO page_content 
            (page_name, section_name, content_type, content_data, image_url, video_url, parameters, sort_order, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', content)
    
    print("✓ Sample content inserted")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 Enhanced admin database initialized successfully!")
    print("\n📋 Login Credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n🚀 You can now run: python simple_enhanced_admin.py")

if __name__ == '__main__':
    init_enhanced_database()