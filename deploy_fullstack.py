#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full-stack deployment script for LED Display Website
Deploys both frontend and backend admin system
"""

import os
import sys
import subprocess
import threading
import time
import json
from pathlib import Path

class FullStackDeployer:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.admin_dir = self.base_dir / "admin"
        self.frontend_port = 8080
        self.backend_port = 5000
        
    def check_requirements(self):
        """Check if all requirements are met"""
        print("🔍 Checking requirements...")
        
        # Check Python
        try:
            python_version = sys.version_info
            if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
                print("❌ Python 3.7+ is required")
                return False
            print(f"✅ Python {python_version.major}.{python_version.minor} found")
        except Exception as e:
            print(f"❌ Python check failed: {e}")
            return False
            
        # Check admin directory
        if not self.admin_dir.exists():
            print("❌ Admin directory not found")
            return False
        print("✅ Admin directory found")
        
        return True
    
    def install_backend_dependencies(self):
        """Install backend dependencies"""
        print("📦 Installing backend dependencies...")
        
        requirements_file = self.admin_dir / "requirements.txt"
        if not requirements_file.exists():
            print("⚠️ requirements.txt not found, creating basic requirements...")
            with open(requirements_file, 'w', encoding='utf-8') as f:
                f.write("""Flask==2.3.3
Werkzeug==2.3.7
flask-cors==4.0.0
Pillow==10.0.1
""")
        
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True, cwd=str(self.admin_dir))
            print("✅ Backend dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def setup_database(self):
        """Setup database"""
        print("🗄️ Setting up database...")
        
        try:
            # Run database setup if exists
            db_setup_file = self.admin_dir / "upgrade_database.py"
            if db_setup_file.exists():
                subprocess.run([sys.executable, str(db_setup_file)], 
                             check=True, cwd=str(self.admin_dir))
                print("✅ Database setup completed")
            else:
                print("⚠️ No database setup script found, will auto-initialize...")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Database setup failed: {e}")
            return False
    
    def start_backend(self):
        """Start backend server"""
        print(f"🚀 Starting backend server on port {self.backend_port}...")
        
        def run_backend():
            try:
                env = os.environ.copy()
                env['FLASK_ENV'] = 'production'
                env['FLASK_DEBUG'] = '0'
                
                subprocess.run([
                    sys.executable, "app.py"
                ], cwd=str(self.admin_dir), env=env)
            except Exception as e:
                print(f"❌ Backend server error: {e}")
        
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()
        
        # Wait for backend to start
        time.sleep(3)
        print("✅ Backend server started")
        return True
    
    def start_frontend(self):
        """Start frontend server"""
        print(f"🌐 Starting frontend server on port {self.frontend_port}...")
        
        def run_frontend():
            try:
                subprocess.run([
                    sys.executable, "-m", "http.server", str(self.frontend_port)
                ], cwd=str(self.base_dir))
            except Exception as e:
                print(f"❌ Frontend server error: {e}")
        
        frontend_thread = threading.Thread(target=run_frontend, daemon=True)
        frontend_thread.start()
        
        # Wait for frontend to start
        time.sleep(2)
        print("✅ Frontend server started")
        return True
    
    def update_frontend_config(self):
        """Update frontend configuration to connect to backend"""
        print("🔧 Updating frontend configuration...")
        
        # Update JavaScript files to use correct backend URL
        js_files = [
            self.base_dir / "js" / "contact-api.js",
            self.base_dir / "js" / "admin-api.js"
        ]
        
        for js_file in js_files:
            if js_file.exists():
                try:
                    with open(js_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Update API base URL
                    content = content.replace(
                        'http://localhost:5000',
                        f'http://localhost:{self.backend_port}'
                    )
                    
                    with open(js_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"✅ Updated {js_file.name}")
                except Exception as e:
                    print(f"⚠️ Failed to update {js_file.name}: {e}")
        
        return True
    
    def display_access_info(self):
        """Display access information"""
        print("\n" + "="*60)
        print("🎉 FULL-STACK DEPLOYMENT SUCCESSFUL!")
        print("="*60)
        print(f"🌐 Frontend Website: http://localhost:{self.frontend_port}")
        print(f"🔧 Admin Panel: http://localhost:{self.backend_port}")
        print(f"📡 API Endpoint: http://localhost:{self.backend_port}/api")
        print("\n📋 Admin Panel Features:")
        print("   • Product Management - Add/Edit LED displays")
        print("   • Content Management - News, cases, solutions") 
        print("   • Customer Inquiries - Contact form submissions")
        print("   • Quote Requests - RFQ management")
        print("   • Media Management - Images and videos")
        print("   • System Settings - Website configuration")
        print("\n🔐 Default Admin Login:")
        print("   URL: http://localhost:5000")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n⚠️  IMPORTANT: Change the default password immediately!")
        print("\n🔗 Frontend-Backend Connection:")
        print("   • Contact forms → Backend API")
        print("   • Product data → Database sync")
        print("   • Real-time content updates")
        print("="*60)
    
    def deploy(self):
        """Main deployment function"""
        print("🚀 Starting Full-Stack Deployment...")
        print("="*50)
        
        if not self.check_requirements():
            return False
        
        if not self.install_backend_dependencies():
            return False
        
        if not self.setup_database():
            return False
        
        if not self.update_frontend_config():
            return False
        
        if not self.start_backend():
            return False
        
        if not self.start_frontend():
            return False
        
        self.display_access_info()
        
        # Keep servers running
        try:
            print("\n⏳ Servers are running... Press Ctrl+C to stop")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down servers...")
            return True

if __name__ == "__main__":
    deployer = FullStackDeployer()
    deployer.deploy()