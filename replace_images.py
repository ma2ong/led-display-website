#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
静态网站图片替换工具
帮助用户快速替换网站中的图片
"""

import os
import shutil
from pathlib import Path

def create_image_directories():
    """创建必要的图片目录"""
    directories = [
        'assets/products',
        'assets/uploads',
        'assets/news',
        'assets/cases'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {directory}")

def list_required_images():
    """列出需要的图片文件"""
    required_images = {
        'assets/products/led-display-hero.jpg': '主页横幅图片 (1200x800px)',
        'assets/products/indoor-led.jpg': '室内LED显示屏 (800x600px)',
        'assets/products/outdoor-led.jpg': '户外LED显示屏 (800x600px)', 
        'assets/products/rental-led.jpg': '租赁LED显示屏 (800x600px)',
        'assets/products/transparent-led.jpg': '透明LED显示屏 (800x600px)',
        'assets/products/creative-led.jpg': '创意LED显示屏 (800x600px)',
        'assets/products/industrial-led.jpg': '工业LED解决方案 (800x600px)'
    }
    
    print("\n📋 需要准备的图片文件:")
    print("=" * 60)
    for filepath, description in required_images.items():
        exists = "✅" if os.path.exists(filepath) else "❌"
        print(f"{exists} {filepath}")
        print(f"   描述: {description}")
        print()

def copy_user_images(source_folder):
    """从用户指定文件夹复制图片"""
    if not os.path.exists(source_folder):
        print(f"❌ 源文件夹不存在: {source_folder}")
        return
    
    # 图片文件扩展名
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    
    # 扫描源文件夹中的图片
    source_images = []
    for file in os.listdir(source_folder):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            source_images.append(file)
    
    if not source_images:
        print(f"❌ 在 {source_folder} 中没有找到图片文件")
        return
    
    print(f"\n📁 在 {source_folder} 中找到 {len(source_images)} 张图片:")
    for i, image in enumerate(source_images, 1):
        print(f"  {i}. {image}")
    
    # 创建目标目录
    create_image_directories()
    
    # 复制图片到assets/products目录
    target_dir = 'assets/products'
    copied_count = 0
    
    for image in source_images:
        source_path = os.path.join(source_folder, image)
        target_path = os.path.join(target_dir, image)
        
        try:
            shutil.copy2(source_path, target_path)
            print(f"✅ 复制: {image} -> {target_path}")
            copied_count += 1
        except Exception as e:
            print(f"❌ 复制失败 {image}: {e}")
    
    print(f"\n🎉 成功复制 {copied_count} 张图片到 {target_dir}")

def generate_html_with_images():
    """生成包含实际图片的HTML代码片段"""
    
    # 检查哪些图片文件存在
    image_files = {
        'hero': 'assets/products/led-display-hero.jpg',
        'indoor': 'assets/products/indoor-led.jpg',
        'outdoor': 'assets/products/outdoor-led.jpg',
        'rental': 'assets/products/rental-led.jpg',
        'transparent': 'assets/products/transparent-led.jpg',
        'creative': 'assets/products/creative-led.jpg',
        'industrial': 'assets/products/industrial-led.jpg'
    }
    
    existing_images = {}
    for key, filepath in image_files.items():
        if os.path.exists(filepath):
            existing_images[key] = filepath
    
    if not existing_images:
        print("❌ 没有找到任何产品图片文件")
        return
    
    print(f"\n📝 找到 {len(existing_images)} 张图片，生成HTML代码...")
    
    # 生成HTML代码
    html_snippets = []
    
    # Hero区域图片
    if 'hero' in existing_images:
        html_snippets.append(f'''
<!-- Hero区域图片 -->
<img src="{existing_images['hero']}" alt="Professional LED Display Solutions" class="img-fluid rounded shadow-lg">
''')
    
    # 产品卡片图片
    product_cards = {
        'indoor': ('Indoor LED Displays', 'fas fa-building', 'Indoor Display'),
        'outdoor': ('Outdoor LED Displays', 'fas fa-sun', 'Outdoor Display'),
        'rental': ('Rental LED Displays', 'fas fa-magic', 'Rental Display'),
        'transparent': ('Transparent LED Displays', 'fas fa-eye', 'Transparent Display'),
        'creative': ('Creative LED Displays', 'fas fa-palette', 'Creative Display'),
        'industrial': ('Industrial Solutions', 'fas fa-industry', 'Industrial Display')
    }
    
    for key, (title, icon, category) in product_cards.items():
        if key in existing_images:
            html_snippets.append(f'''
<!-- {title} 产品卡片 -->
<div class="product-image">
    <img src="{existing_images[key]}" alt="{title}" class="img-fluid">
</div>
''')
    
    # 保存到文件
    with open('generated_html_snippets.html', 'w', encoding='utf-8') as f:
        f.write('<!-- 生成的HTML代码片段 -->\n')
        f.write('<!-- 将这些代码替换到对应的index.html位置 -->\n\n')
        f.write('\n'.join(html_snippets))
    
    print("✅ HTML代码片段已保存到: generated_html_snippets.html")

def main():
    """主函数"""
    print("🖼️  静态网站图片替换工具")
    print("=" * 50)
    
    while True:
        print("\n请选择操作:")
        print("1. 查看需要的图片文件列表")
        print("2. 从文件夹批量复制图片")
        print("3. 生成HTML代码片段")
        print("4. 创建图片目录")
        print("5. 退出")
        
        choice = input("\n请输入选项 (1-5): ").strip()
        
        if choice == '1':
            list_required_images()
            
        elif choice == '2':
            source_folder = input("请输入包含图片的文件夹路径: ").strip()
            if source_folder:
                copy_user_images(source_folder)
            else:
                print("❌ 请输入有效的文件夹路径")
                
        elif choice == '3':
            generate_html_with_images()
            
        elif choice == '4':
            create_image_directories()
            
        elif choice == '5':
            print("👋 再见!")
            break
            
        else:
            print("❌ 无效选项，请重新选择")

if __name__ == "__main__":
    main()