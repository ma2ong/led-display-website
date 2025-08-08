#!/usr/bin/env python3
"""
Script to add hero-fix.css to all HTML files
"""

import os
import re

def update_html_file(filepath):
    """Add hero-fix.css to an HTML file if not already present"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if hero-fix.css is already included
        if 'hero-fix.css' in content:
            print(f"✓ {filepath} already has hero-fix.css")
            return True
        
        # Find the position to insert the CSS link
        # Look for the line with css/style.css
        pattern = r'(\s*<link href="css/style\.css" rel="stylesheet">)'
        match = re.search(pattern, content)
        
        if match:
            # Insert hero-fix.css after style.css
            replacement = match.group(1) + '\n    <link href="css/hero-fix.css" rel="stylesheet">'
            new_content = content.replace(match.group(1), replacement)
            
            # Write the updated content back
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Updated {filepath} - Added hero-fix.css")
            return True
        else:
            print(f"⚠️  Could not find css/style.css in {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {filepath}: {e}")
        return False

def main():
    """Update all HTML files in the current directory"""
    print("🔧 Adding hero-fix.css to all HTML files...")
    print("=" * 50)
    
    # Get all HTML files in current directory
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    
    if not html_files:
        print("No HTML files found in current directory")
        return
    
    updated_count = 0
    total_count = len(html_files)
    
    for html_file in sorted(html_files):
        if update_html_file(html_file):
            updated_count += 1
    
    print("=" * 50)
    print(f"📊 Summary: {updated_count}/{total_count} files processed successfully")
    
    if updated_count == total_count:
        print("🎉 All HTML files have been updated with hero-fix.css!")
    else:
        print(f"⚠️  {total_count - updated_count} files could not be updated")

if __name__ == "__main__":
    main()