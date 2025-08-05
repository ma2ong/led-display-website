#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED网站Vercel部署脚本
自动化部署LED显示屏网站到Vercel平台
"""

import os
import subprocess
import sys
import json

def check_vercel_cli():
    """检查Vercel CLI是否已安装"""
    try:
        result = subprocess.run(['vercel', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Vercel CLI已安装: {result.stdout.strip()}")
            return True
        else:
            print("❌ Vercel CLI未安装")
            return False
    except FileNotFoundError:
        print("❌ Vercel CLI未找到")
        return False

def install_vercel_cli():
    """安装Vercel CLI"""
    print("🔧 正在安装Vercel CLI...")
    try:
        subprocess.run(['npm', 'install', '-g', 'vercel'], check=True)
        print("✅ Vercel CLI安装成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ Vercel CLI安装失败")
        return False
    except FileNotFoundError:
        print("❌ 未找到npm，请先安装Node.js")
        return False

def verify_files():
    """验证部署所需文件"""
    required_files = [
        'vercel.json',
        'requirements.txt',
        'api/index.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        return False
    else:
        print("✅ 所有必要文件已准备就绪")
        return True

def deploy_to_vercel():
    """部署到Vercel"""
    print("🚀 开始部署到Vercel...")
    try:
        # 首先尝试登录检查
        login_result = subprocess.run(['vercel', 'whoami'], capture_output=True, text=True)
        if login_result.returncode != 0:
            print("🔐 请先登录Vercel账户...")
            subprocess.run(['vercel', 'login'], check=True)
        
        # 执行部署
        print("📦 正在部署项目...")
        result = subprocess.run(['vercel', '--prod', '--yes'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 部署成功！")
            print("\n" + "="*50)
            print("🎉 LED网站已成功部署到Vercel！")
            print("="*50)
            
            # 提取部署URL
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'https://' in line and 'vercel.app' in line:
                    url = line.strip()
                    print(f"🌐 网站地址: {url}")
                    print(f"🔧 管理后台: {url}/admin")
                    print(f"🔑 登录信息: admin / admin123")
                    break
            
            print("\n📋 功能说明:")
            print("- 前端: 专业LED显示屏展示网站")
            print("- 后台: 完整中文管理系统")
            print("- 功能: 产品管理、询盘处理、新闻发布等")
            
            return True
        else:
            print(f"❌ 部署失败: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 部署过程中出错: {e}")
        return False

def main():
    """主函数"""
    print("🚀 LED网站Vercel部署工具")
    print("="*40)
    
    # 检查当前目录
    if not os.path.exists('index.html'):
        print("❌ 请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 验证文件
    if not verify_files():
        print("❌ 请确保所有必要文件存在")
        sys.exit(1)
    
    # 检查Vercel CLI
    if not check_vercel_cli():
        if not install_vercel_cli():
            print("❌ 无法安装Vercel CLI，请手动安装")
            sys.exit(1)
    
    # 部署
    if deploy_to_vercel():
        print("\n🎉 部署完成！您的LED网站现已在线运行。")
    else:
        print("\n❌ 部署失败，请检查错误信息并重试。")
        sys.exit(1)

if __name__ == "__main__":
    main()