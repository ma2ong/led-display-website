import os
import re
from bs4 import BeautifulSoup

# Define the inline style to be injected directly into hero sections
HERO_INLINE_STYLE = """
    min-height: 600px !important; 
    max-height: 600px !important; 
    height: 600px !important; 
    padding: 120px 0 80px !important;
    display: flex !important;
    align-items: center !important;
"""

# Define the style for containers within hero sections
CONTAINER_INLINE_STYLE = """
    position: relative !important;
    z-index: 10 !important;
    height: auto !important;
    display: flex !important;
    align-items: center !important;
"""

def fix_html_file(file_path):
    print(f"Processing {file_path}...")
    
    try:
        # 首先尝试 UTF-8 编码
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        try:
            # 如果 UTF-8 失败，尝试 latin-1 编码
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()
            print(f"  Note: Used latin-1 encoding for {file_path}")
        except Exception as e:
            print(f"  Error reading {file_path}: {e}")
            return False
    
    # Parse HTML
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find all hero sections
    hero_sections = soup.select('.hero-section, .product-hero-section, section[class*="hero"], .cta-section')
    
    if not hero_sections:
        print(f"  No hero sections found in {file_path}")
        return False
    
    changes_made = False
    
    # Apply inline styles to hero sections
    for section in hero_sections:
        # Get existing style
        existing_style = section.get('style', '')
        
        # Remove any height or min-height settings
        existing_style = re.sub(r'(min-height|max-height|height):[^;]+;', '', existing_style)
        
        # Add our forced styles
        new_style = existing_style + HERO_INLINE_STYLE
        section['style'] = new_style
        changes_made = True
        print(f"  Applied hero fix to {section.get('class', ['unknown'])}")
        
        # Find container within hero section and apply styles
        containers = section.select('.container, .container-fluid')
        for container in containers:
            container_style = container.get('style', '')
            container['style'] = container_style + CONTAINER_INLINE_STYLE
            print(f"  Applied container fix within hero section")
    
    # Add a script to ensure the fix is applied even after DOM loads
    if changes_made:
        script_tag = soup.new_tag('script')
        script_content = """
        document.addEventListener('DOMContentLoaded', function() {
            // Force hero sections to correct height
            document.querySelectorAll('.hero-section, .product-hero-section, section[class*="hero"], .cta-section').forEach(function(el) {
                el.style.minHeight = '600px';
                el.style.maxHeight = '600px';
                el.style.height = '600px';
                el.style.padding = '120px 0 80px';
                el.style.display = 'flex';
                el.style.alignItems = 'center';
            });
            
            // Force containers within hero sections
            document.querySelectorAll('.hero-section .container, .product-hero-section .container, .cta-section .container').forEach(function(el) {
                el.style.position = 'relative';
                el.style.zIndex = '10';
                el.style.height = 'auto';
                el.style.display = 'flex';
                el.style.alignItems = 'center';
            });
            
            console.log('✅ Emergency hero fix applied via JavaScript');
        });
        """
        script_tag.string = script_content
        soup.body.append(script_tag)
    
    # Write the modified HTML back to the file
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(str(soup))
    except UnicodeEncodeError:
        # 如果 UTF-8 写入失败，尝试使用 latin-1
        with open(file_path, 'w', encoding='latin-1') as file:
            file.write(str(soup))
        print(f"  Note: Used latin-1 encoding for writing {file_path}")
    
    return changes_made

def main():
    # Get all HTML files in the current directory
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    
    fixed_count = 0
    error_count = 0
    
    for html_file in html_files:
        try:
            if fix_html_file(html_file):
                fixed_count += 1
        except Exception as e:
            print(f"  Error processing {html_file}: {e}")
            error_count += 1
    
    print(f"\nCompleted! Fixed {fixed_count} files. Encountered errors in {error_count} files.")

if __name__ == "__main__":
    main()