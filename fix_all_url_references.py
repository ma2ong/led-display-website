#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面修复所有模板文件中的URL引用问题
"""

import os
import re

def fix_all_url_references():
    """修复所有模板文件中的URL引用"""
    template_dir = 'admin/templates'
    
    # URL映射表 - 将错误的URL引用映射到正确的
    url_mappings = {
        "url_for('dashboard')": "url_for('admin_dashboard')",
        "url_for('frontend_pages')": "url_for('admin_frontend_pages')",
        "url_for('products')": "url_for('admin_products')",
        "url_for('inquiries')": "url_for('admin_inquiries')",
        "url_for('news')": "url_for('admin_news')",
        "url_for('users')": "url_for('admin_users')",
        "url_for('statistics')": "url_for('admin_statistics')",
        "url_for('settings')": "url_for('admin_settings')",
        "url_for('logout')": "url_for('admin_logout')",
        "url_for('page_list')": "url_for('admin_frontend_pages')",
        "url_for('admin_solutions')": "url_for('admin_frontend_pages')",
        "url_for('admin_cases')": "url_for('admin_frontend_pages')",
        "url_for('admin_support')": "url_for('admin_frontend_pages')",
        "url_for('admin_quotes')": "url_for('admin_inquiries')",
        "url_for('admin_media')": "url_for('admin_frontend_pages')"
    }
    
    # 获取所有HTML文件
    html_files = []
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    fixed_count = 0
    
    for filepath in html_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 应用所有URL映射
            for old_url, new_url in url_mappings.items():
                content = content.replace(old_url, new_url)
            
            # 如果内容有变化，写回文件
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                filename = os.path.basename(filepath)
                print(f"✅ 修复完成: {filename}")
                fixed_count += 1
            
        except Exception as e:
            filename = os.path.basename(filepath)
            print(f"❌ 修复失败: {filename} - {e}")
    
    print(f"\n🎉 修复完成！共修复了 {fixed_count} 个文件")

if __name__ == "__main__":
    print("🔧 开始全面修复URL引用...")
    fix_all_url_references()
    print("✅ 全面修复完成！")