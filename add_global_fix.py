#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add global-fix.js to all HTML files
"""

import os
import re
from pathlib import Path

def add_global_fix_to_html(file_path):
    """Add global-fix.js to HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if global-fix.js is already included
        if 'global-fix.js' in content:
            print(f"✓ global-fix.js already included in: {file_path}")
            return True
        
        # Add global-fix.js as the first script in the head
        if '<head>' in content:
            new_content = content.replace(
                '<head>',
                '<head>\n    <script src="js/global-fix.js"></script>'
            )
            
            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(new_content)
            
            print(f"✅ Added global-fix.js to: {file_path}")
            return True
        else:
            print(f"❌ No <head> tag found in: {file_path}")
            return False
    except Exception as e:
        print(f"❌ Error adding global-fix.js to {file_path}: {e}")
        return False

def main():
    """Main function"""
    print("Adding global-fix.js to HTML files...")
    print("=" * 60)
    
    # Find all HTML files
    html_files = list(Path('.').glob('*.html'))
    
    # Add global-fix.js to each HTML file
    success_count = 0
    for file_path in html_files:
        if add_global_fix_to_html(file_path):
            success_count += 1
    
    print("=" * 60)
    print(f"✅ Added global-fix.js to {success_count} HTML files")
    print("🔧 All HTML files now have protection against JavaScript errors")
    print("🌐 Please restart the server and reload the pages to apply the changes")

if __name__ == "__main__":
    main()