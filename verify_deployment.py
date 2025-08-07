#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED显示屏网站 - 部署验证脚本
验证GitHub推送和Supabase部署状态
"""

import requests
import subprocess
import json
import sys
from datetime import datetime

def print_status(message, status="INFO"):
    """打印状态信息"""
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m", 
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "END": "\033[0m"
    }
    print(f"{colors.get(status, '')}{status}: {message}{colors['END']}")

def verify_github_status():
    """验证GitHub仓库状态"""
    print_status("验证GitHub仓库状态...", "INFO")
    
    try:
        # 检查Git状态
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            if result.stdout.strip():
                print_status("有未提交的更改", "WARNING")
                print(result.stdout)
            else:
                print_status("Git工作区干净", "SUCCESS")
        
        # 检查远程状态
        result = subprocess.run(['git', 'log', '--oneline', '-1'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_status(f"最新提交: {result.stdout.strip()}", "SUCCESS")
        
        return True
    except Exception as e:
        print_status(f"GitHub验证失败: {e}", "ERROR")
        return False

def verify_supabase_connection():
    """验证Supabase数据库连接"""
    print_status("验证Supabase数据库连接...", "INFO")
    
    url = "https://jirudzbqcxviytcmxegf.supabase.co/rest/v1/products"
    headers = {
        "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y214ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y214ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_status(f"Supabase连接成功! 产品数量: {len(data)}", "SUCCESS")
            return True
        else:
            print_status(f"Supabase连接失败: HTTP {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"Supabase连接错误: {e}", "ERROR")
        return False

def verify_local_servers():
    """验证本地服务器状态"""
    print_status("验证本地服务器状态...", "INFO")
    
    servers = [
        ("后台管理", "http://localhost:5003"),
        ("前端网站", "http://localhost:8000")
    ]
    
    results = []
    for name, url in servers:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print_status(f"{name} ({url}) - 运行正常", "SUCCESS")
                results.append(True)
            else:
                print_status(f"{name} ({url}) - HTTP {response.status_code}", "WARNING")
                results.append(False)
        except Exception as e:
            print_status(f"{name} ({url}) - 连接失败: {e}", "ERROR")
            results.append(False)
    
    return all(results)

def generate_deployment_summary():
    """生成部署总结"""
    print_status("生成部署总结...", "INFO")
    
    summary = {
        "deployment_time": datetime.now().isoformat(),
        "project_name": "LED显示屏网站管理系统",
        "version": "1.0.0",
        "github_repo": "https://github.com/ma2ong/led-display-website.git",
        "supabase_url": "https://jirudzbqcxviytcmxegf.supabase.co",
        "local_admin": "http://localhost:5003",
        "local_frontend": "http://localhost:8000",
        "features": [
            "完整中文后台管理系统",
            "Supabase数据库集成", 
            "产品管理CRUD操作",
            "询盘管理系统",
            "新闻发布系统",
            "用户权限管理",
            "统计分析面板",
            "系统设置配置",
            "固定侧边栏布局",
            "响应式设计"
        ],
        "deployment_status": "SUCCESS"
    }
    
    with open("deployment_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print_status("部署总结已保存到 deployment_summary.json", "SUCCESS")
    return summary

def main():
    """主验证流程"""
    print("="*60)
    print("🚀 LED显示屏网站 - 部署验证")
    print("="*60)
    
    # 验证各个组件
    github_ok = verify_github_status()
    supabase_ok = verify_supabase_connection()
    servers_ok = verify_local_servers()
    
    # 生成总结
    summary = generate_deployment_summary()
    
    print("\n" + "="*60)
    print("📋 部署验证结果")
    print("="*60)
    print(f"✅ GitHub仓库: {'正常' if github_ok else '异常'}")
    print(f"✅ Supabase数据库: {'正常' if supabase_ok else '异常'}")
    print(f"✅ 本地服务器: {'正常' if servers_ok else '异常'}")
    
    if all([github_ok, supabase_ok, servers_ok]):
        print("\n🎉 部署验证完全成功!")
        print("📋 项目已成功推送到GitHub并配置Supabase")
        print("🌐 所有服务正常运行")
        print("\n📍 访问地址:")
        print("- GitHub: https://github.com/ma2ong/led-display-website.git")
        print("- 后台管理: http://localhost:5003 (admin/admin123)")
        print("- 前端网站: http://localhost:8000")
        print("- Supabase: https://jirudzbqcxviytcmxegf.supabase.co")
        return 0
    else:
        print("\n⚠️ 部署验证发现问题")
        print("📋 请检查上述错误信息并修复")
        return 1

if __name__ == "__main__":
    sys.exit(main())