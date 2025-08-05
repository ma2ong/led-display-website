#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final comprehensive encoding fix for LED Display Website
"""

import os
import json
import codecs
import re
import sys
import shutil
import time
from pathlib import Path
from bs4 import BeautifulSoup

# Ensure the script itself uses UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    elif hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def backup_file(file_path):
    """Create a backup of the file before modifying it"""
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    # Create a backup with timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = Path(file_path).name
    backup_path = backup_dir / f"{filename}.{timestamp}.bak"
    
    try:
        shutil.copy2(file_path, backup_path)
        return True
    except Exception as e:
        print(f"⚠️ Backup failed for {file_path}: {e}")
        return False

def detect_and_fix_encoding(file_path):
    """Detect and fix file encoding with improved handling"""
    try:
        # Create backup
        backup_file(file_path)
        
        # Try different encoding methods to read files
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'big5', 'latin-1', 'cp1252', 'iso-8859-1']
        content = None
        original_encoding = None
        
        # First try to read as binary
        with open(file_path, 'rb') as f:
            raw_content = f.read()
            
            # Check for BOM
            if raw_content.startswith(b'\xef\xbb\xbf'):
                content = raw_content[3:].decode('utf-8')
                original_encoding = 'utf-8-sig'
            else:
                # Try different encodings
                for encoding in encodings:
                    try:
                        content = raw_content.decode(encoding)
                        original_encoding = encoding
                        break
                    except UnicodeDecodeError:
                        continue
        
        if content is None:
            print(f"❌ Cannot read file: {file_path}")
            return False
        
        # Save as UTF-8 encoding without BOM
        with open(file_path, 'wb') as f:
            f.write(content.encode('utf-8'))
        
        print(f"✓ File encoding fixed: {file_path} ({original_encoding} -> utf-8)")
        return True
    except Exception as e:
        print(f"❌ File encoding fix failed {file_path}: {e}")
        return False

def fix_html_meta_charset(file_path):
    """Fix HTML file meta charset tag using BeautifulSoup for better parsing"""
    try:
        # Create backup
        backup_file(file_path)
        
        with open(file_path, 'rb') as f:
            content = f.read().decode('utf-8', errors='replace')
        
        # Use BeautifulSoup for more reliable HTML parsing
        try:
            # Try to parse with html.parser first
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove existing charset meta tags
            for meta in soup.find_all('meta'):
                if meta.get('charset') or (meta.get('http-equiv') and meta.get('http-equiv').lower() == 'content-type'):
                    meta.decompose()
            
            # Add new UTF-8 charset meta tag
            head = soup.find('head')
            if head:
                new_meta = soup.new_tag('meta')
                new_meta['charset'] = 'UTF-8'
                head.insert(0, new_meta)
            else:
                # Create head if it doesn't exist
                html = soup.find('html')
                if html:
                    head = soup.new_tag('head')
                    new_meta = soup.new_tag('meta')
                    new_meta['charset'] = 'UTF-8'
                    head.append(new_meta)
                    if html.contents:
                        html.insert(0, head)
                    else:
                        html.append(head)
                else:
                    # If no html tag, just use regex as fallback
                    content = re.sub(r'<meta\s+charset=["\'][^"\']*["\'][^>]*>', '', content, flags=re.IGNORECASE)
                    content = re.sub(r'<meta\s+http-equiv=["\']Content-Type["\'][^>]*>', '', content, flags=re.IGNORECASE)
                    
                    if '<head>' in content:
                        content = content.replace('<head>', '<head>\n    <meta charset="UTF-8">')
                    elif '<html>' in content and '<head>' not in content:
                        content = content.replace('<html>', '<html>\n<head>\n    <meta charset="UTF-8">\n</head>')
                    
                    # Ensure DOCTYPE declaration exists
                    if not content.strip().startswith('<!DOCTYPE'):
                        content = '<!DOCTYPE html>\n' + content
                    
                    with open(file_path, 'wb') as f:
                        f.write(content.encode('utf-8'))
                    
                    print(f"✓ HTML meta charset fixed (regex): {file_path}")
                    return True
            
            # Ensure DOCTYPE declaration exists
            if not str(soup).strip().startswith('<!DOCTYPE'):
                with open(file_path, 'wb') as f:
                    f.write(('<!DOCTYPE html>\n' + str(soup)).encode('utf-8'))
            else:
                with open(file_path, 'wb') as f:
                    f.write(str(soup).encode('utf-8'))
            
            print(f"✓ HTML meta charset fixed (BeautifulSoup): {file_path}")
            return True
            
        except Exception as bs_error:
            # Fallback to regex if BeautifulSoup fails
            print(f"⚠️ BeautifulSoup failed for {file_path}, using regex fallback: {bs_error}")
            content = re.sub(r'<meta\s+charset=["\'][^"\']*["\'][^>]*>', '', content, flags=re.IGNORECASE)
            content = re.sub(r'<meta\s+http-equiv=["\']Content-Type["\'][^>]*>', '', content, flags=re.IGNORECASE)
            
            if '<head>' in content:
                content = content.replace('<head>', '<head>\n    <meta charset="UTF-8">')
            elif '<html>' in content and '<head>' not in content:
                content = content.replace('<html>', '<html>\n<head>\n    <meta charset="UTF-8">\n</head>')
            
            # Ensure DOCTYPE declaration exists
            if not content.strip().startswith('<!DOCTYPE'):
                content = '<!DOCTYPE html>\n' + content
            
            with open(file_path, 'wb') as f:
                f.write(content.encode('utf-8'))
            
            print(f"✓ HTML meta charset fixed (regex fallback): {file_path}")
            return True
            
    except Exception as e:
        print(f"❌ HTML meta charset fix failed {file_path}: {e}")
        return False

def fix_json_encoding(file_path):
    """Fix JSON file encoding with special handling"""
    try:
        # Create backup
        backup_file(file_path)
        
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
            # Try a more lenient approach - just decode without JSON validation
            for encoding in encodings:
                try:
                    content = raw_content.decode(encoding)
                    break
                except UnicodeDecodeError:
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
            
            print(f"✓ JSON file encoding fixed and formatted: {file_path}")
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

def fix_css_encoding(file_path):
    """Fix CSS file encoding with special handling for @charset rules"""
    try:
        # Create backup
        backup_file(file_path)
        
        # Detect and fix basic encoding
        if not detect_and_fix_encoding(file_path):
            return False
        
        # Now handle CSS-specific issues
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove existing @charset rules
        content = re.sub(r'@charset\s+["\'][^"\']*["\'];', '', content)
        
        # Add UTF-8 @charset rule at the beginning
        content = '@charset "UTF-8";\n' + content
        
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        
        print(f"✓ CSS @charset rule added: {file_path}")
        return True
    except Exception as e:
        print(f"❌ CSS encoding fix failed {file_path}: {e}")
        return False

def create_utf8_server():
    """Create UTF-8 supporting HTTP server with improved handling"""
    server_code = '''#!/usr/bin/env python3
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
        print("\\n✓ Server stopped")
    except Exception as e:
        print(f"❌ Server start failed: {e}")

if __name__ == "__main__":
    start_server()
'''
    
    with open('utf8_server.py', 'wb') as f:
        f.write(server_code.encode('utf-8'))
    
    print("✓ Enhanced UTF-8 HTTP server created: utf8_server.py")

def fix_python_encoding(file_path):
    """Fix Python file encoding with special handling"""
    try:
        # Create backup
        backup_file(file_path)
        
        # First detect and fix basic encoding
        if not detect_and_fix_encoding(file_path):
            return False
        
        # Now handle Python-specific issues
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if encoding declaration exists
        has_encoding = re.search(r'^#.*coding[:=]\s*([-\w.]+)', content, re.MULTILINE) is not None
        
        if not has_encoding:
            # Add encoding declaration after shebang if it exists
            if content.startswith('#!'):
                shebang_end = content.find('\n')
                if shebang_end != -1:
                    content = content[:shebang_end+1] + '# -*- coding: utf-8 -*-\n' + content[shebang_end+1:]
            else:
                content = '# -*- coding: utf-8 -*-\n' + content
        
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        
        print(f"✓ Python encoding declaration added: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Python encoding fix failed {file_path}: {e}")
        return False

def check_dependencies():
    """Check and install required dependencies"""
    try:
        import bs4
        print("✓ BeautifulSoup is already installed")
    except ImportError:
        print("⚠️ BeautifulSoup not found, attempting to install...")
        try:
            import pip
            pip.main(['install', 'beautifulsoup4'])
            print("✓ BeautifulSoup installed successfully")
        except Exception as e:
            print(f"❌ Failed to install BeautifulSoup: {e}")
            print("Please install manually with: pip install beautifulsoup4")

def main():
    """Main function with improved handling"""
    print("✓ Starting final comprehensive encoding fix...")
    print("=" * 60)
    
    # Check dependencies
    check_dependencies()
    
    # Create backup directory
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    print(f"✓ Backup directory created: {backup_dir}")
    
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
    
    # 3. Fix CSS files with special handling
    css_files = ["css/style.css"]
    print("\n✓ Fixing CSS file encoding...")
    for file_path in css_files:
        if Path(file_path).exists():
            fix_css_encoding(file_path)
    
    # 4. Fix JS files
    js_files = ["js/script.js", "js/admin-sync.js", "js/admin-api.js"]
    print("\n✓ Fixing JS file encoding...")
    for file_path in js_files:
        if Path(file_path).exists():
            detect_and_fix_encoding(file_path)
    
    # 5. Fix admin backend template files
    admin_templates = Path("admin/templates")
    if admin_templates.exists():
        print("\n✓ Fixing admin backend template files...")
        for template_file in admin_templates.glob("*.html"):
            detect_and_fix_encoding(template_file)
            fix_html_meta_charset(template_file)
    
    # 6. Fix Python files with special handling
    python_files = ["deploy.py", "server.py", "admin/app.py", "admin/api.py", "admin/start_admin.py", "update_database.py"]
    print("\n✓ Fixing Python file encoding...")
    for file_path in python_files:
        if Path(file_path).exists():
            fix_python_encoding(file_path)
    
    # 7. Create enhanced UTF-8 HTTP server
    print("\n✓ Creating enhanced UTF-8 HTTP server...")
    create_utf8_server()
    
    print("\n" + "=" * 60)
    print("✓ Final comprehensive encoding fix completed!")
    print("✓ Fixed content:")
    print("  • Created backups of all modified files")
    print("  • Detected and fixed original encoding issues for all files")
    print("  • Ensured all HTML files contain correct <meta charset='UTF-8'>")
    print("  • Added @charset rules to CSS files")
    print("  • Added encoding declarations to Python files")
    print("  • Removed conflicting encoding declarations")
    print("  • Created enhanced UTF-8 supporting HTTP server")
    print("  • All text files unified to UTF-8 encoding")
    print("  • Special handling for JSON, CSS, and Python files")
    print("\n✓ Launch methods:")
    print("  Method 1: python utf8_server.py (recommended)")
    print("  Method 2: python deploy.py")
    print("\n✓ Access address: http://localhost:8000")

if __name__ == "__main__":
    main()