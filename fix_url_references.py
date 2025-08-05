#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复模板文件中的URL引用问题
"""

import os
import re

def fix_url_references():
    """修复所有模板文件中的URL引用"""
    template_dir = 'admin/templates'
    
    # 需要修复的文件列表
    files_to_fix = [
        'fixed_sidebar_template.html',
        'frontend_pages.html', 
        'page_content_manager.html',
        'page_list.html',
        'page_list_complete.html',
        'page_manager.html',
        'simple_dashboard.html',
        'standard_sidebar.html'
    ]
    
    for filename in files_to_fix:
        filepath = os.path.join(template_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 替换错误的URL引用
                content = content.replace("url_for('dashboard')", "url_for('admin_dashboard')")
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ 修复完成: {filename}")
            except Exception as e:
                print(f"❌ 修复失败: {filename} - {e}")
        else:
            print(f"⚠️ 文件不存在: {filename}")

if __name__ == "__main__":
    print("🔧 开始批量修复URL引用...")
    fix_url_references()
    print("✅ 批量修复完成！")