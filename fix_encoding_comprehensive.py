#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive encoding fix for LED Display Website
"""

import os
import json
import codecs
import re
import sys
from pathlib import Path

# Ensure the script itself uses UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    elif hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def detect_and_fix_encoding(file_path):
    """Detect and fix file encoding"""
    try:
        # Try different encoding methods to read files
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'big5', 'latin-1', 'cp1252']
        content = None
        original_encoding = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'rb') as f:
                    raw_content = f.read()
                    # Try to decode with the current encoding
                    content = raw_content.decode(encoding)
                    original_encoding = encoding
                    break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print(f"❌ Cannot read file: {file_path}")
            return False
        
        # Remove BOM if present
        if content.startswith('\ufeff'):
            content = content[1:]
        
        # Save as UTF-8 encoding without BOM
        with open(file_path, 'wb') as f:
            f.write(content.encode('utf-8'))
        
        print(f"✓ File encoding fixed: {file_path} ({original_encoding} -> utf-8)")
        return True
    except Exception as e:
        print(f"❌ File encoding fix failed {file_path}: {e}")
        return False

def fix_html_meta_charset(file_path):
    """Fix HTML file meta charset tag"""
    try:
        with open(file_path, 'rb') as f:
            content = f.read().decode('utf-8', errors='replace')
        
        # Remove all existing charset declarations
        content = re.sub(r'<meta\s+charset=["\'][^"\']*["\'][^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'<meta\s+http-equiv=["\']Content-Type["\'][^>]*>', '', content, flags=re.IGNORECASE)
        
        # Add UTF-8 charset declaration immediately after the <head> tag
        if '<head>' in content:
            content = content.replace('<head>', '<head>\n    <meta charset="UTF-8">')
        elif '<html>' in content and '<head>' not in content:
            content = content.replace('<html>', '<html>\n<head>\n    <meta charset="UTF-8">\n</head>')
        
        # Ensure DOCTYPE declaration exists
        if not content.strip().startswith('<!DOCTYPE'):
            content = '<!DOCTYPE html>\n' + content
        
        with open(file_path, 'wb') as f:
            f.write(content.encode('utf-8'))
        
        print(f"✓ HTML meta charset fixed: {file_path}")
        return True
    except Exception as e:
        print(f"❌ HTML meta charset fix failed {file_path}: {e}")
        return False

def create_utf8_server():
    """Create UTF-8 supporting HTTP server"""
    server_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UTF-8 HTTP Server for LED Display Website
"""

import http.server
import socketserver
import os
import sys
import codecs
import mimetypes
from pathlib import Path

# Ensure the server uses UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    elif hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

class UTF8HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """UTF-8 encoding HTTP request handler"""
    
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

def start_server(port=8000):
    """Start UTF-8 HTTP server"""
    try:
        with socketserver.TCPServer(("", port), UTF8HTTPRequestHandler) as httpd:
            print(f"✓ UTF-8 HTTP server started successfully")
            print(f"✓ Access address: http://localhost:{port}")
            print(f"✓ UTF-8 encoding supported")
            print("Press Ctrl+C to stop server")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\\n✓ Server stopped")
    except Exception as e:
        print(f"❌ Server start failed: {e}")

if __name__ == "__main__":
    start_server()
'''
    
    with open('utf8_server.py', 'wb') as f:
        f.write(server_code.encode('utf-8'))
    
    print("✓ UTF-8 HTTP server created: utf8_server.py")

def fix_json_encoding(file_path):
    """Fix JSON file encoding with special handling"""
    try:
        # First try to read as binary
        with open(file_path, 'rb') as f:
            raw_content = f.read()
        
        # Try different encodings
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin-1', 'cp1252']
        content = None
        
        for encoding in encodings:
            try:
                content = raw_content.decode(encoding)
                # Try to parse as JSON to validate
                json.loads(content)
                break
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
        
        if content is None:
            print(f"❌ Cannot read JSON file: {file_path}")
            return False
        
        # Remove BOM if present
        if content.startswith('\ufeff'):
            content = content[1:]
        
        # Format JSON properly
        try:
            json_obj = json.loads(content)
            formatted_content = json.dumps(json_obj, ensure_ascii=False, indent=2)
            
            # Save as UTF-8
            with open(file_path, 'wb') as f:
                f.write(formatted_content.encode('utf-8'))
            
            print(f"✓ JSON file encoding fixed: {file_path}")
            return True
        except json.JSONDecodeError:
            # If JSON parsing fails, just save the raw content as UTF-8
            with open(file_path, 'wb') as f:
                f.write(content.encode('utf-8'))
            print(f"✓ JSON file encoding fixed (raw): {file_path}")
            return True
    except Exception as e:
        print(f"❌ JSON file encoding fix failed {file_path}: {e}")
        return False

def main():
    """Main function"""
    print("✓ Starting comprehensive encoding fix...")
    print("=" * 60)
    
    # 1. Detect and fix encoding for all HTML files
    html_files = [
        "index.html", "homepage.html", "about.html", "products.html", 
        "contact.html", "fine-pitch.html", "outdoor.html", "rental.html",
        "creative.html", "transparent.html", "solutions.html", "cases.html",
        "news.html", "support.html"
    ]
    
    print("✓ Fixing HTML file encoding...")
    for file_path in html_files:
        if Path(file_path).exists():
            detect_and_fix_encoding(file_path)
            fix_html_meta_charset(file_path)
    
    # 2. Fix JSON files with special handling
    json_files = ["data/content.json"]
    print("\n✓ Fixing JSON file encoding...")
    for file_path in json_files:
        if Path(file_path).exists():
            fix_json_encoding(file_path)
    
    # 3. Fix CSS and JS files
    css_js_files = ["css/style.css", "js/script.js", "js/admin-sync.js", "js/admin-api.js"]
    print("\n✓ Fixing CSS/JS file encoding...")
    for file_path in css_js_files:
        if Path(file_path).exists():
            detect_and_fix_encoding(file_path)
    
    # 4. Fix admin backend template files
    admin_templates = Path("admin/templates")
    if admin_templates.exists():
        print("\n✓ Fixing admin backend template files...")
        for template_file in admin_templates.glob("*.html"):
            detect_and_fix_encoding(template_file)
            fix_html_meta_charset(template_file)
    
    # 5. Fix Python files
    python_files = ["deploy.py", "server.py", "admin/app.py", "admin/api.py", "admin/start_admin.py", "update_database.py"]
    print("\n✓ Fixing Python file encoding...")
    for file_path in python_files:
        if Path(file_path).exists():
            detect_and_fix_encoding(file_path)
    
    # 6. Create UTF-8 HTTP server
    print("\n✓ Creating UTF-8 HTTP server...")
    create_utf8_server()
    
    print("\n" + "=" * 60)
    print("✓ Comprehensive encoding fix completed!")
    print("✓ Fixed content:")
    print("  • Detected and fixed original encoding issues for all files")
    print("  • Ensured all HTML files contain correct <meta charset='UTF-8'>")
    print("  • Removed conflicting encoding declarations")
    print("  • Created UTF-8 supporting HTTP server")
    print("  • All text files unified to UTF-8 encoding")
    print("  • Special handling for JSON files")
    print("\n✓ Launch methods:")
    print("  Method 1: python utf8_server.py (recommended)")
    print("  Method 2: python deploy.py")
    print("\n✓ Access address: http://localhost:8000")

if __name__ == "__main__":
    main()