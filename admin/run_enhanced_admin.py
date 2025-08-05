#!/usr/bin/env python3
"""
Enhanced Admin System Startup Script
Run this to start the comprehensive admin backend for Lianjin LED website
"""

import os
import sys
import sqlite3
from werkzeug.security import generate_password_hash

def create_default_user():
    """Create default admin user if none exists"""
    conn = sqlite3.connect('enhanced_admin.db')
    cursor = conn.cursor()
    
    # Check if any users exist
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
        # Create default admin user
        password_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, is_active)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@lianjinled.com', password_hash, 'admin', True))
        
        conn.commit()
        print("✓ Default admin user created:")
        print("  Username: admin")
        print("  Password: admin123")
        print("  Please change the password after first login!")
    
    conn.close()

def create_sample_content():
    """Create sample content for demonstration"""
    conn = sqlite3.connect('enhanced_admin.db')
    cursor = conn.cursor()
    
    # Check if content already exists
    cursor.execute('SELECT COUNT(*) FROM page_content')
    content_count = cursor.fetchone()[0]
    
    if content_count == 0:
        sample_content = [
            # Home page content
            ('home', 'Hero Section', 'mixed', 
             '<h1>Welcome to Lianjin LED</h1><p>Leading manufacturer of professional LED display solutions</p>',
             'https://via.placeholder.com/1200x600/667eea/ffffff?text=Hero+Image',
             'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
             '{"containerWidth": "full", "textAlign": "center"}', 0, True),
            
            ('home', 'Company Overview', 'text',
             '<h2>About Lianjin LED</h2><p>With over 15 years of experience in LED display technology, we provide innovative solutions for various industries.</p>',
             '', '', '{"containerWidth": "container", "textAlign": "left"}', 1, True),
            
            # About page content
            ('about', 'Company History', 'text',
             '<h2>Our Story</h2><p>Founded in 2008, Lianjin LED has grown from a small startup to a leading LED display manufacturer.</p>',
             '', '', '{"containerWidth": "container", "textAlign": "left"}', 0, True),
            
            ('about', 'Team Photo', 'image',
             'Our dedicated team of professionals',
             'https://via.placeholder.com/800x400/667eea/ffffff?text=Team+Photo',
             '', '{"containerWidth": "container", "textAlign": "center"}', 1, True),
            
            # Products page content
            ('products', 'Product Categories', 'text',
             '<h2>Our Product Range</h2><p>Comprehensive LED display solutions for every need</p>',
             '', '', '{"containerWidth": "container", "textAlign": "left"}', 0, True),
            
            # Solutions page content
            ('solutions', 'Industry Solutions', 'mixed',
             '<h2>Tailored Solutions</h2><p>We provide customized LED display solutions for various industries</p>',
             'https://via.placeholder.com/600x400/667eea/ffffff?text=Solutions',
             '', '{"containerWidth": "container", "textAlign": "left"}', 0, True),
            
            # Cases page content
            ('cases', 'Success Stories', 'text',
             '<h2>Our Success Stories</h2><p>Discover how we have helped clients achieve their goals</p>',
             '', '', '{"containerWidth": "container", "textAlign": "left"}', 0, True),
            
            # News page content
            ('news', 'Latest Updates', 'text',
             '<h2>Company News</h2><p>Stay updated with our latest developments and industry insights</p>',
             '', '', '{"containerWidth": "container", "textAlign": "left"}', 0, True),
            
            # Support page content
            ('support', 'Technical Support', 'text',
             '<h2>We are here to help</h2><p>Get technical support and documentation for our products</p>',
             '', '', '{"containerWidth": "container", "textAlign": "left"}', 0, True),
            
            # Contact page content
            ('contact', 'Get in Touch', 'mixed',
             '<h2>Contact Us</h2><p>Ready to discuss your LED display needs? Get in touch with our team</p>',
             'https://via.placeholder.com/400x300/667eea/ffffff?text=Contact+Us',
             '', '{"containerWidth": "container", "textAlign": "left"}', 0, True),
        ]
        
        for content in sample_content:
            cursor.execute('''
                INSERT INTO page_content 
                (page_name, section_name, content_type, content_data, image_url, video_url, parameters, sort_order, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', content)
        
        conn.commit()
        print("✓ Sample content created for all pages")
    
    conn.close()

def main():
    """Main startup function"""
    print("🚀 Starting Enhanced Lianjin LED Admin System...")
    print("=" * 50)
    
    # Import the enhanced app
    try:
        from simple_enhanced_admin import app, init_db
        
        # Initialize database
        print("📊 Initializing database...")
        init_db()
        
        # Create default user
        print("👤 Setting up default user...")
        create_default_user()
        
        # Create sample content
        print("📝 Creating sample content...")
        create_sample_content()
        
        print("=" * 50)
        print("✅ Enhanced Admin System Ready!")
        print("")
        print("🌐 Admin Panel: http://localhost:5001")
        print("👤 Default Login:")
        print("   Username: admin")
        print("   Password: admin123")
        print("")
        print("📋 Available Pages to Manage:")
        print("   • Home Page")
        print("   • About Us")
        print("   • Products")
        print("   • Solutions")
        print("   • Cases")
        print("   • News")
        print("   • Support")
        print("   • Contact")
        print("")
        print("🔧 Features:")
        print("   • Rich text editor with formatting")
        print("   • Image upload and management")
        print("   • Video embedding (YouTube/Vimeo)")
        print("   • Mixed content sections")
        print("   • Advanced parameters and styling")
        print("   • Real-time preview")
        print("   • Content ordering and activation")
        print("")
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Start the Flask app
        app.run(debug=True, host='0.0.0.0', port=5001)
        
    except ImportError as e:
        print(f"❌ Error importing enhanced admin app: {e}")
        print("Make sure simple_enhanced_admin.py exists in the same directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting admin system: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()