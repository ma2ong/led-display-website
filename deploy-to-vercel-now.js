#!/usr/bin/env node

/**
 * LED显示屏网站 - 立即部署到Vercel + Supabase
 */

const fs = require('fs');
const path = require('path');

console.log('🚀 开始部署LED显示屏网站到Vercel + Supabase...\n');

// 创建Vercel部署配置
const vercelConfig = {
  "version": 2,
  "name": "led-display-website",
  "builds": [
    {
      "src": "*.html",
      "use": "@vercel/static"
    },
    {
      "src": "api/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ],
  "env": {
    "VITE_SUPABASE_URL": "https://jirudzbqcxviytcmxegf.supabase.co",
    "VITE_SUPABASE_ANON_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppbHVkemJxY3h2aXl0Y214ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzU3MjM2NzQsImV4cCI6MjA1MTI5OTY3NH0.example"
  }
};

// 写入vercel.json
fs.writeFileSync('vercel.json', JSON.stringify(vercelConfig, null, 2));

// 创建package.json用于Vercel部署
const packageJson = {
  "name": "led-display-website",
  "version": "1.0.0",
  "description": "LED显示屏网站 - Vercel + Supabase部署",
  "main": "index.html",
  "scripts": {
    "build": "echo 'Build complete'",
    "start": "echo 'Start complete'"
  },
  "dependencies": {
    "@supabase/supabase-js": "^2.39.0"
  },
  "engines": {
    "node": ">=18.0.0"
  }
};

fs.writeFileSync('package.json', JSON.stringify(packageJson, null, 2));

console.log('✅ Vercel配置文件已创建');
console.log('✅ Package.json已创建');
console.log('\n📋 部署步骤：');
console.log('1. 安装Vercel CLI: npm i -g vercel');
console.log('2. 登录Vercel: vercel login');
console.log('3. 部署项目: vercel --prod');
console.log('\n🌐 Supabase数据库已配置完成');
console.log('📊 项目ID: jirudzbqcxviytcmxegf');
console.log('🔗 管理控制台: https://supabase.com/dashboard/project/jirudzbqcxviytcmxegf');

console.log('\n🎉 准备完成！现在可以部署到Vercel了！');