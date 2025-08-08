#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动完整中文LED显示屏管理系统
Start Complete Chinese LED Display Admin System
"""

import os
import sys
import subprocess
import time

def check_python():
    """检查Python版本"""
    if sys.version_info < (3, 6):
        print("❌ 需要Python 3.6或更高版本")
        return False
    return True

def install_requirements():
    """安装必要的依赖包"""
    required_packages = [
        'flask',
        'flask-cors',
        'werkzeug'
    ]
    
    print("📦 检查并安装必要依赖...")
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"📥 正在安装 {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} 安装完成")

def main():
    """主启动函数"""
    print("=" * 70)
    print("🚀 启动完整中文LED显示屏管理系统")
    print("   Complete Chinese LED Display Admin System")
    print("=" * 70)
    
    # 检查Python版本
    if not check_python():
        return
    
    # 安装依赖
    try:
        install_requirements()
    except Exception as e:
        print(f"❌ 依赖安装失败: {e}")
        print("请手动运行: pip install flask flask-cors werkzeug")
        return
    
    # 切换到admin目录
    admin_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(admin_dir)
    
    print("\n📂 当前工作目录:", admin_dir)
    print("🗄️  数据库文件: complete_admin.db")
    
    # 启动系统
    print("\n" + "=" * 70)
    print("🌟 系统启动信息:")
    print("🌐 管理后台地址: http://localhost:5003")
    print("👤 默认管理员账号: admin")
    print("🔑 默认管理员密码: admin123")
    print("=" * 70)
    print("📋 完整功能模块:")
    print("   ✅ 仪表盘总览 - 实时数据统计")
    print("   ✅ 前端页面管理 - 8个页面独立编辑")
    print("   ✅ 产品管理 - 完整CRUD操作")
    print("   ✅ 询盘管理 - 客户咨询处理")
    print("   ✅ 新闻管理 - 内容发布系统")
    print("   ✅ 用户管理 - 管理员权限控制")
    print("   ✅ 系统设置 - 配置参数管理")
    print("   ✅ 统计分析 - 数据可视化")
    print("=" * 70)
    print("🎨 界面特色:")
    print("   ✅ 完整中文界面 - 专业商务风格")
    print("   ✅ 紫色渐变主题 - 固定侧边栏导航")
    print("   ✅ 响应式设计 - Bootstrap 5.3.0")
    print("   ✅ 图标支持 - Font Awesome 6.4.0")
    print("=" * 70)
    
    try:
        # 导入并运行主系统
        from complete_chinese_admin_system import main as run_admin
        run_admin()
    except ImportError:
        print("❌ 无法导入管理系统模块")
        print("请确保 complete_chinese_admin_system.py 文件存在")
    except KeyboardInterrupt:
        print("\n👋 管理系统已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == '__main__':
    main()