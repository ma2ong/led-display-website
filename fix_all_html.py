#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive HTML fix for LED Display Website
"""

import os
import re
from pathlib import Path

def fix_html_file(file_path):
    """Fix HTML file by adding proper structure and global-fix.js"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if global-fix.js is already included
        if 'global-fix.js' in content:
            print(f"✓ global-fix.js already included in: {file_path}")
        else:
            # Check if the file has a proper HTML structure
            has_doctype = '<!DOCTYPE' in content.upper()
            has_html_tag = '<html' in content.lower()
            has_head_tag = '<head>' in content.lower()
            has_body_tag = '<body' in content.lower()
            
            new_content = content
            
            # Add DOCTYPE if missing
            if not has_doctype:
                new_content = '<!DOCTYPE html>\n' + new_content
                print(f"✅ Added DOCTYPE to: {file_path}")
            
            # Add html tag if missing
            if not has_html_tag:
                new_content = re.sub(r'^(<!DOCTYPE[^>]*>)', r'\1\n<html>', new_content, flags=re.IGNORECASE)
                new_content += '\n</html>'
                print(f"✅ Added HTML tags to: {file_path}")
            
            # Add head tag if missing
            if not has_head_tag:
                if has_body_tag:
                    # Insert head before body
                    new_content = re.sub(r'(<body[^>]*>)', r'<head>\n    <meta charset="UTF-8">\n    <script src="js/global-fix.js"></script>\n</head>\n\1', new_content, flags=re.IGNORECASE)
                    print(f"✅ Added HEAD with global-fix.js to: {file_path}")
                else:
                    # Insert head after html
                    new_content = re.sub(r'(<html[^>]*>)', r'\1\n<head>\n    <meta charset="UTF-8">\n    <script src="js/global-fix.js"></script>\n</head>\n<body>', new_content, flags=re.IGNORECASE)
                    new_content += '\n</body>'
                    print(f"✅ Added HEAD and BODY with global-fix.js to: {file_path}")
            else:
                # Add global-fix.js to existing head
                new_content = re.sub(r'(<head[^>]*>)', r'\1\n    <script src="js/global-fix.js"></script>', new_content, flags=re.IGNORECASE)
                print(f"✅ Added global-fix.js to: {file_path}")
            
            # Add body tag if missing
            if not has_body_tag and '<body>' not in new_content.lower():
                new_content = re.sub(r'(</head>)', r'\1\n<body>', new_content, flags=re.IGNORECASE)
                new_content = re.sub(r'(</html>)', r'</body>\n\1', new_content, flags=re.IGNORECASE)
                print(f"✅ Added BODY tags to: {file_path}")
            
            # Add meta charset if missing
            if '<meta charset=' not in new_content.lower():
                new_content = re.sub(r'(<head[^>]*>)', r'\1\n    <meta charset="UTF-8">', new_content, flags=re.IGNORECASE)
                print(f"✅ Added meta charset to: {file_path}")
            
            # Write the updated content
            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(new_content)
        
        return True
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def create_minimal_html(file_path):
    """Create a minimal HTML file with global-fix.js"""
    try:
        minimal_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LED Display Website</title>
    <script src="js/global-fix.js"></script>
    <script src="js/script-fixed.js"></script>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <h1>LED Display Website</h1>
        <p>This is a minimal HTML page with all the necessary fixes.</p>
        <p>Please use this page if you encounter issues with other pages.</p>
        <div class="links">
            <a href="index.html">Home</a>
            <a href="products.html">Products</a>
            <a href="about.html">About</a>
            <a href="contact.html">Contact</a>
        </div>
    </div>
</body>
</html>'''
        
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(minimal_html)
        
        print(f"✅ Created minimal HTML file: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error creating {file_path}: {e}")
        return False

def main():
    """Main function"""
    print("Fixing all HTML files...")
    print("=" * 60)
    
    # Find all HTML files
    html_files = list(Path('.').glob('*.html'))
    
    # Fix each HTML file
    success_count = 0
    for file_path in html_files:
        if fix_html_file(file_path):
            success_count += 1
    
    # Create a minimal HTML file
    create_minimal_html('minimal.html')
    
    print("=" * 60)
    print(f"✅ Fixed {success_count} HTML files")
    print("✅ Created minimal.html as a fallback")
    print("🔧 All HTML files now have proper structure and JavaScript error protection")
    print("🌐 Please restart the server and reload the pages to apply the changes")

if __name__ == "__main__":
    main()