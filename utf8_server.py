#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced UTF-8 HTTP Server for LED Display Website
"""

import http.server
import socketserver
import os
import sys
import codecs
import mimetypes
import locale
from pathlib import Path

# Configure system to use UTF-8
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, '')
    except:
        pass

# Ensure the server uses UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    elif hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

class UTF8HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """UTF-8 encoding HTTP request handler with improved handling"""
    
    def __init__(self, *args, **kwargs):
        # Set default encoding
        self.default_encoding = 'utf-8'
        super().__init__(*args, **kwargs)
    
    def end_headers(self):
        # Set UTF-8 encoding for all text files
        if hasattr(self, '_content_type_set'):
            super().end_headers()
            return
            
        path = self.translate_path(self.path)
        if os.path.isfile(path):
            _, ext = os.path.splitext(path)
            if ext.lower() in ['.html', '.htm', '.css', '.js', '.json', '.xml', '.txt']:
                content_type = self.guess_type(path)
                if content_type and not 'charset=' in content_type:
                    if content_type.startswith('text/') or content_type in ['application/javascript', 'application/json']:
                        self.send_header('Content-Type', f'{content_type}; charset=utf-8')
                        self._content_type_set = True
        
        super().end_headers()
    
    def guess_type(self, path):
        """Override MIME type guessing"""
        base, ext = os.path.splitext(path)
        if ext in ['.html', '.htm']:
            return 'text/html'
        elif ext == '.css':
            return 'text/css'
        elif ext == '.js':
            return 'application/javascript'
        elif ext == '.json':
            return 'application/json'
        else:
            return super().guess_type(path)
    
    def send_head(self):
        """Override send_head to handle UTF-8 encoding for text files"""
        path = self.translate_path(self.path)
        
        # Handle directory index
        if os.path.isdir(path):
            for index in ["index.html", "index.htm"]:
                index_path = os.path.join(path, index)
                if os.path.exists(index_path):
                    path = index_path
                    break
        
        # Handle file serving with proper encoding
        try:
            if os.path.isfile(path):
                _, ext = os.path.splitext(path)
                if ext.lower() in ['.html', '.htm', '.css', '.js', '.json', '.xml', '.txt']:
                    # For text files, ensure UTF-8 encoding
                    f = open(path, 'rb')
                    fs = os.fstat(f.fileno())
                    content_type = self.guess_type(path)
                    self.send_response(200)
                    self.send_header("Content-type", f"{content_type}; charset=utf-8")
                    self.send_header("Content-Length", str(fs[6]))
                    self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
                    self.end_headers()
                    return f
            
            # For other files, use default handling
            return super().send_head()
        except:
            return super().send_head()

def start_server(port=8000):
    """Start UTF-8 HTTP server"""
    try:
        # Try to find an available port if the default is in use
        max_port = port + 10
        current_port = port
        server = None
        
        while current_port <= max_port:
            try:
                server = socketserver.TCPServer(("", current_port), UTF8HTTPRequestHandler)
                break
            except OSError:
                print(f"Port {current_port} is in use, trying next port...")
                current_port += 1
        
        if server is None:
            print(f"❌ Could not find an available port between {port} and {max_port}")
            return
        
        print(f"✓ Enhanced UTF-8 HTTP server started successfully")
        print(f"✓ Access address: http://localhost:{current_port}")
        print(f"✓ UTF-8 encoding fully supported")
        print("Press Ctrl+C to stop server")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Server stopped")
    except Exception as e:
        print(f"❌ Server start failed: {e}")

if __name__ == "__main__":
    start_server()
