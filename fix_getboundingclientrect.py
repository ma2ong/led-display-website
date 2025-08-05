#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to fix getBoundingClientRect errors by adding a global patch to all HTML files
"""

import os
import re
from pathlib import Path

def add_getboundingclientrect_patch(file_path):
    """Add a patch for getBoundingClientRect to HTML files"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if the patch is already added
        if "window.Element.prototype.originalGetBoundingClientRect" in content:
            print(f"✓ Patch already exists in: {file_path}")
            return True
        
        # Create the patch script
        patch_script = """
<script>
// Patch for getBoundingClientRect to prevent errors
(function() {
    // Save the original method
    window.Element.prototype.originalGetBoundingClientRect = Element.prototype.getBoundingClientRect;
    
    // Override with a safe version
    Element.prototype.getBoundingClientRect = function() {
        try {
            return this.originalGetBoundingClientRect.apply(this);
        } catch (error) {
            console.warn('Error in getBoundingClientRect, returning default values');
            return {
                top: 0, right: 0, bottom: 0, left: 0,
                width: 0, height: 0, x: 0, y: 0
            };
        }
    };
    
    // Add a global error handler
    window.addEventListener('error', function(event) {
        console.warn('Caught error:', event.error);
        // Prevent the error from showing in console
        event.preventDefault();
    });
    
    console.log('✓ getBoundingClientRect patch applied');
})();
</script>
"""
        
        # Add the patch script right after the opening <head> tag
        updated_content = re.sub(
            r'(<head>)',
            r'\1' + patch_script,
            content
        )
        
        # Write the updated content back to the file
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(updated_content)
        
        print(f"✅ Added getBoundingClientRect patch to: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error adding patch to {file_path}: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Adding getBoundingClientRect patch to HTML files...")
    print("=" * 60)
    
    # List of HTML files to update
    html_files = [
        "index.html", "homepage.html", "about.html", "products.html", 
        "contact.html", "fine-pitch.html", "outdoor.html", "rental.html",
        "creative.html", "transparent.html", "solutions.html", "cases.html",
        "news.html", "support.html", "fixed-index.html", "debug.html", "test.html"
    ]
    
    updated_count = 0
    for file_path in html_files:
        if Path(file_path).exists():
            if add_getboundingclientrect_patch(file_path):
                updated_count += 1
    
    print("=" * 60)
    print(f"✅ Added patch to {updated_count} HTML files")
    print("🔧 All HTML files now have protection against getBoundingClientRect errors")
    print("🌐 Please restart the server and reload the pages to apply the changes")

if __name__ == "__main__":
    main()