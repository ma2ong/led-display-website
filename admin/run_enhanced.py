#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动增强版LED显示屏管理后台
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_init import init_enhanced_db
from enhanced_admin import app

def main():
    """启动增强版管理后台"""
    print("=" * 60)
    print("🚀 启动增强版LED显示屏管理后台")
    print("=" * 60)
    
    # 初始化数据库
    print("📊 初始化数据库...")
    init_enhanced_db()
    
    print("✅ 数据库初始化完成")
    print("🌐 管理后台地址: http://localhost:5001")
    print("👤 默认登录账号: admin")
    print("🔑 默认登录密码: admin123")
    print("=" * 60)
    print("📋 功能特色:")
    print("   • 完整的8个前端页面内容管理")
    print("   • 标题、副标题、正文、图片、视频编辑")
    print("   • 中英文双语内容支持")
    print("   • 拖拽排序和状态管理")
    print("   • 实时预览和API接口")
    print("=" * 60)
    
    try:
        # 启动Flask应用
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5001,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 管理后台已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == '__main__':
    main()