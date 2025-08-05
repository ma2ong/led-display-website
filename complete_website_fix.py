#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Website Fix - Restore full functionality
"""

import os
import shutil
from pathlib import Path

def create_complete_website():
    """Create complete website with all original features"""
    
    # Enhanced HTML template with all features
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - LED Display Solutions</title>
    
    <!-- Error Protection Script -->
    <script>
        window.addEventListener('error', function(e) {
            console.warn('Error caught:', e.message);
            e.preventDefault();
            return true;
        });
        
        // Safe getBoundingClientRect
        if (Element.prototype.getBoundingClientRect) {
            const original = Element.prototype.getBoundingClientRect;
            Element.prototype.getBoundingClientRect = function() {
                try {
                    return original.apply(this);
                } catch (e) {
                    return { top: 0, right: 0, bottom: 0, left: 0, width: 0, height: 0, x: 0, y: 0 };
                }
            };
        }
    </script>
    
    <!-- Original CSS -->
    <link rel="stylesheet" href="css/style.css">
    
    <!-- Enhanced Styles -->
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6; 
            margin: 0; 
            padding: 0;
            background: #f8f9fa;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: bold;
            text-decoration: none;
            color: white;
        }
        
        .nav-menu {
            display: flex;
            list-style: none;
            margin: 0;
            padding: 0;
            gap: 2rem;
        }
        
        .nav-link {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: all 0.3s ease;
        }
        
        .nav-link:hover, .nav-link.active {
            background: rgba(255,255,255,0.2);
            transform: translateY(-2px);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }
        
        .main-content {
            min-height: 80vh;
            padding: 2rem 0;
        }
        
        .hero {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 4rem 0;
            margin-bottom: 3rem;
        }
        
        .hero h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .hero p {
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }
        
        .btn {
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
        }
        
        .btn:hover {
            background: #ff5252;
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(255,107,107,0.3);
        }
        
        .product-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin: 3rem 0;
        }
        
        .product-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border: 1px solid #e9ecef;
        }
        
        .product-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }
        
        .product-card h3 {
            color: #333;
            margin-bottom: 1rem;
            font-size: 1.3rem;
        }
        
        .product-card p {
            color: #666;
            margin-bottom: 1rem;
        }
        
        .footer {
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 2rem 0;
            margin-top: 3rem;
        }
        
        @media (max-width: 768px) {
            .nav {
                flex-direction: column;
                gap: 1rem;
            }
            
            .nav-menu {
                flex-direction: column;
                gap: 1rem;
            }
            
            .hero h1 {
                font-size: 2rem;
            }
            
            .container {
                padding: 0 1rem;
            }
        }
    </style>
</head>
<body>
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

    <main class="main-content">
        {content}
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 LED Display Solutions. All rights reserved.</p>
            <p>Professional LED Display Solutions for Every Need</p>
        </div>
    </footer>

    <script>
        // Safe navigation highlighting
        try {
            const currentPage = window.location.pathname.split('/').pop() || 'index.html';
            const navLinks = document.querySelectorAll('.nav-link');
            navLinks.forEach(link => {
                if (link.getAttribute('href') === currentPage) {
                    link.classList.add('active');
                }
            });
        } catch (e) {
            console.warn('Navigation highlighting failed:', e);
        }
        
        // Safe smooth scrolling
        try {
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                });
            });
        } catch (e) {
            console.warn('Smooth scroll failed:', e);
        }
    </script>
    
    <script src="js/script-fixed.js"></script>
</body>
</html>'''

    # Page contents
    pages = {
        'index.html': {
            'title': 'Home',
            'content': '''
                <section class="hero">
                    <div class="container">
                        <h1>Professional LED Display Solutions</h1>
                        <p>Leading provider of high-quality LED displays for indoor, outdoor, and rental applications worldwide</p>
                        <a href="products.html" class="btn">Explore Our Products</a>
                    </div>
                </section>
                
                <section class="container">
                    <h2 style="text-align: center; margin-bottom: 3rem; color: #333; font-size: 2.5rem;">Our LED Display Solutions</h2>
                    
                    <div class="product-grid">
                        <div class="product-card">
                            <h3>🏢 Indoor LED Displays</h3>
                            <p>High-resolution indoor LED displays perfect for retail stores, corporate offices, conference rooms, and entertainment venues. Features ultra-fine pixel pitch and seamless splicing.</p>
                            <ul style="color: #666; margin-left: 1rem;">
                                <li>P1.25, P1.56, P2.5 pixel pitch options</li>
                                <li>4K/8K resolution support</li>
                                <li>Ultra-thin and lightweight design</li>
                                <li>Easy installation and maintenance</li>
                            </ul>
                            <a href="products.html" class="btn" style="font-size: 0.9rem; padding: 0.5rem 1rem; margin-top: 1rem;">Learn More</a>
                        </div>
                        
                        <div class="product-card">
                            <h3>🌤️ Outdoor LED Displays</h3>
                            <p>Weather-resistant outdoor LED displays designed for advertising billboards, sports stadiums, transportation hubs, and public information systems.</p>
                            <ul style="color: #666; margin-left: 1rem;">
                                <li>P4, P6, P8, P10 pixel pitch options</li>
                                <li>IP65/IP67 waterproof rating</li>
                                <li>High brightness up to 10,000 nits</li>
                                <li>Anti-UV and corrosion resistant</li>
                            </ul>
                            <a href="products.html" class="btn" style="font-size: 0.9rem; padding: 0.5rem 1rem; margin-top: 1rem;">Learn More</a>
                        </div>
                        
                        <div class="product-card">
                            <h3>🎪 Rental LED Displays</h3>
                            <p>Flexible and portable rental LED displays perfect for events, concerts, conferences, trade shows, and temporary installations with quick setup.</p>
                            <ul style="color: #666; margin-left: 1rem;">
                                <li>Lightweight aluminum cabinet</li>
                                <li>Quick lock system for fast setup</li>
                                <li>Curved and creative shapes available</li>
                                <li>Flight case packaging included</li>
                            </ul>
                            <a href="products.html" class="btn" style="font-size: 0.9rem; padding: 0.5rem 1rem; margin-top: 1rem;">Learn More</a>
                        </div>
                        
                        <div class="product-card">
                            <h3>✨ Transparent LED Displays</h3>
                            <p>Innovative transparent LED displays that maintain visibility while displaying content, perfect for retail windows, glass facades, and creative installations.</p>
                            <ul style="color: #666; margin-left: 1rem;">
                                <li>70-90% transparency rate</li>
                                <li>Ultra-lightweight design</li>
                                <li>Easy maintenance from front/back</li>
                                <li>Customizable sizes and shapes</li>
                            </ul>
                            <a href="products.html" class="btn" style="font-size: 0.9rem; padding: 0.5rem 1rem; margin-top: 1rem;">Learn More</a>
                        </div>
                        
                        <div class="product-card">
                            <h3>🎨 Creative LED Displays</h3>
                            <p>Custom-shaped LED displays including curved, spherical, cylindrical, and irregular shapes for unique architectural and artistic applications.</p>
                            <ul style="color: #666; margin-left: 1rem;">
                                <li>360° cylindrical displays</li>
                                <li>Flexible and bendable modules</li>
                                <li>Custom shapes and sizes</li>
                                <li>Artistic and architectural integration</li>
                            </ul>
                            <a href="products.html" class="btn" style="font-size: 0.9rem; padding: 0.5rem 1rem; margin-top: 1rem;">Learn More</a>
                        </div>
                        
                        <div class="product-card">
                            <h3>🏭 Industrial Solutions</h3>
                            <p>Specialized LED display solutions for industrial environments, control rooms, monitoring centers, and mission-critical applications.</p>
                            <ul style="color: #666; margin-left: 1rem;">
                                <li>24/7 continuous operation</li>
                                <li>High reliability and stability</li>
                                <li>Multiple input signal support</li>
                                <li>Redundant backup systems</li>
                            </ul>
                            <a href="contact.html" class="btn" style="font-size: 0.9rem; padding: 0.5rem 1rem; margin-top: 1rem;">Get Quote</a>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin: 3rem 0;">
                        <a href="contact.html" class="btn">Get Free Quote</a>
                    </div>
                </section>
            '''
        },
        
        'products.html': {
            'title': 'Products',
            'content': '''
                <section class="hero">
                    <div class="container">
                        <h1>Our LED Display Products</h1>
                        <p>Comprehensive range of professional LED display solutions for every application</p>
                    </div>
                </section>
                
                <section class="container">
                    <div class="product-grid">
                        <div class="product-card">
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
                        
                        <div class="product-card">
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
                        
                        <div class="product-card">
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
                        
                        <div class="product-card">
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
                        
                        <div class="product-card">
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
                        
                        <div class="product-card">
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
                        <h1>About LED Display Solutions</h1>
                        <p>Leading manufacturer of professional LED display systems with over 15 years of industry experience</p>
                    </div>
                </section>
                
                <section class="container">
                    <div style="background: white; padding: 3rem; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-bottom: 3rem;">
                        <h2 style="color: #333; margin-bottom: 2rem;">Our Company</h2>
                        <p style="color: #666; font-size: 1.1rem; line-height: 1.8;">
                            Founded in 2009, LED Display Solutions has grown to become one of the world's leading manufacturers of professional LED display systems. We specialize in the research, development, production, and sales of high-quality LED displays for indoor, outdoor, rental, and creative applications.
                        </p>
                        <p style="color: #666; font-size: 1.1rem; line-height: 1.8;">
                            Our state-of-the-art manufacturing facility spans over 50,000 square meters and employs more than 800 skilled professionals. We have successfully delivered over 100,000 LED display projects worldwide, serving clients in more than 120 countries.
                        </p>
                    </div>
                    
                    <div class="product-grid">
                        <div class="product-card">
                            <h3>🎯 Our Mission</h3>
                            <p>To provide innovative, reliable, and cost-effective LED display solutions that exceed customer expectations and contribute to the advancement of visual communication technology worldwide.</p>
                        </div>
                        
                        <div class="product-card">
                            <h3>👁️ Our Vision</h3>
                            <p>To be the global leader in LED display technology, recognized for our innovation, quality, and commitment to customer success in creating stunning visual experiences.</p>
                        </div>
                        
                        <div class="product-card">
                            <h3>⭐ Our Values</h3>
                            <ul style="color: #666; margin-left: 1rem;">
                                <li>Innovation and continuous improvement</li>
                                <li>Quality and reliability in every product</li>
                                <li>Customer satisfaction and long-term partnerships</li>
                                <li>Environmental responsibility and sustainability</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div style="background: white; padding: 3rem; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin: 3rem 0;">
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
                        <h1>Contact Our Experts</h1>
                        <p>Get professional consultation and customized LED display solutions for your project</p>
                    </div>
                </section>
                
                <section class="container">
                    <div class="product-grid">
                        <div class="product-card">
                            <h3>📧 Sales Inquiry</h3>
                            <p><strong>Email:</strong> sales@leddisplaysolutions.com</p>
                            <p><strong>Phone:</strong> +1 (555) 123-4567</p>
                            <p><strong>WhatsApp:</strong> +1 (555) 123-4567</p>
                            <p><strong>Hours:</strong> Monday - Friday, 9:00 AM - 6:00 PM (EST)</p>
                            <p style="color: #666;">For product inquiries, quotes, and general sales questions.</p>
                        </div>
                        
                        <div class="product-card">
                            <h3>🔧 Technical Support</h3>
                            <p><strong>Email:</strong> support@leddisplaysolutions.com</p>
                            <p><strong>Phone:</strong> +1 (555) 123-4568</p>
                            <p><strong>Hours:</strong> 24/7 Support Available</p>
                            <p style="color: #666;">For installation guidance, troubleshooting, and technical assistance.</p>
                        </div>
                        
                        <div class="product-card">
                            <h3>🏢 Head Office</h3>
                            <p><strong>Address:</strong> 123 Technology Drive<br>Silicon Valley, CA 94025<br>United States</p>
                            <p><strong>Phone:</strong> +1 (555) 123-4569</p>
                            <p><strong>Fax:</strong> +1 (555) 123-4570</p>
                        </div>
                    </div>
                    
                    <div style="background: white; padding: 3rem; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin: 3rem 0;">
                        <h2 style="color: #333; margin-bottom: 2rem; text-align: center;">Send us a Message</h2>
                        <form style="max-width: 800px; margin: 0 auto;" onsubmit="handleFormSubmit(event)">
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                                <div>
                                    <label style="display: block; margin-bottom: 0.5rem; color: #333; font-weight: bold;">Name *</label>
                                    <input type="text" required style="width: 100%; padding: 0.75rem; border: 2px solid #e9ecef; border-radius: 8px; font-size: 1rem;">
                                </div>
                                <div>
                                    <label style="display: block; margin-bottom: 0.5rem; color: #333; font-weight: bold;">Email *</label>
                                    <input type="email" required style="width: 100%; padding: 0.75rem; border: 2px solid #e9ecef; border-radius: 8px; font-size: 1rem;">
                                </div>
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                                <div>
                                    <label style="display: block; margin-bottom: 0.5rem; color: #333; font-weight: bold;">Company</label>
                                    <input type="text" style="width: 100%; padding: 0.75rem; border: 2px solid #e9ecef; border-radius: 8px; font-size: 1rem;">
                                </div>
                                <div>
                                    <label style="display: block; margin-bottom: 0.5rem; color: #333; font-weight: bold;">Phone</label>
                                    <input type="tel" style="width: 100%; padding: 0.75rem; border: 2px solid #e9ecef; border-radius: 8px; font-size: 1rem;">
                                </div>
                            </div>
                            <div style="margin-bottom: 1rem;">
                                <label style="display: block; margin-bottom: 0.5rem; color: #333; font-weight: bold;">Product Interest</label>
                                <select style="width: 100%; padding: 0.75rem; border: 2px solid #e9ecef; border-radius: 8px; font-size: 1rem;">
                                    <option value="">Select a product category</option>
                                    <option value="indoor">