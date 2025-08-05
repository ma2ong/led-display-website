#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to update all HTML files to use the fixed JavaScript file
"""

import os
import re
from pathlib import Path

def update_script_references(file_path):
    """Update script references from script.js to script-fixed.js"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace script.js references with script-fixed.js
        updated_content = re.sub(
            r'<script\s+src=["\'](?:\.\/)?js\/script\.js["\']',
            '<script src="js/script-fixed.js"',
            content
        )
        
        # Write the updated content back to the file
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(updated_content)
        
        print(f"✅ Updated script references in: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error updating script references in {file_path}: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Updating script references in HTML files...")
    print("=" * 60)
    
    # List of HTML files to update
    html_files = [
        "index.html", "homepage.html", "about.html", "products.html", 
        "contact.html", "fine-pitch.html", "outdoor.html", "rental.html",
        "creative.html", "transparent.html", "solutions.html", "cases.html",
        "news.html", "support.html"
    ]
    
    updated_count = 0
    for file_path in html_files:
        if Path(file_path).exists():
            if update_script_references(file_path):
                updated_count += 1
    
    print("=" * 60)
    print(f"✅ Updated {updated_count} HTML files to use script-fixed.js")
    print("🔧 All HTML files now use the fixed JavaScript file with proper error handling")

if __name__ == "__main__":
    main()