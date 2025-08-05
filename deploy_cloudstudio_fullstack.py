#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CloudStudio Full-Stack Deployment for LED Display Website
Optimized for cloud deployment with both frontend and backend
"""

import os
import sys
import subprocess
import threading
import time
import signal

def setup_environment():
    """Setup environment for CloudStudio"""
    print("🔧 Setting up environment...")
    
    # Install required packages
    packages = [
        "flask==2.3.3",
        "werkzeug==2.3.7", 
        "flask-cors==4.0.0",
        "pillow==10.0.1"
    ]
    
    for package in packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"⚠️ Failed to install {package}")
    
    return True

def start_backend():
    """Start backend server"""
    print("🚀 Starting backend server on port 5000...")
    
    def run_backend():
        try:
            os.chdir("admin")
            # Initialize database first
            subprocess.run([sys.executable, "-c", """
import sys
sys.path.append('.')
from app import init_db
init_db()
print('Database initialized successfully')
"""], check=True)
            
            # Start Flask app
            subprocess.run([sys.executable, "app.py"])
        except Exception as e:
            print(f"Backend error: {e}")
    
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    time.sleep(3)
    print("✅ Backend server started")

def start_frontend():
    """Start frontend server"""
    print("🌐 Starting frontend server on port 8080...")
    
    def run_frontend():
        try:
            os.chdir("..")  # Back to root directory
            subprocess.run([sys.executable, "-m", "http.server", "8080"])
        except Exception as e:
            print(f"Frontend error: {e}")
    
    frontend_thread = threading.Thread(target=run_frontend, daemon=True)
    frontend_thread.start()
    time.sleep(2)
    print("✅ Frontend server started")

def main():
    """Main function"""
    print("🚀 CloudStudio Full-Stack Deployment")
    print("="*40)
    
    setup_environment()
    start_backend()
    start_frontend()
    
    print("\n🎉 DEPLOYMENT SUCCESSFUL!")
    print("="*40)
    print("🌐 Frontend: Port 8080")
    print("🔧 Admin Panel: Port 5000")
    print("📡 API: Port 5000/api")
    print("\n🔐 Admin Login:")
    print("   Username: admin")
    print("   Password: admin123")
    print("="*40)
    
    # Keep running
    try:
        print("\n⏳ Servers running... Press Ctrl+C to stop")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")

if __name__ == "__main__":
    main()