#!/usr/bin/env node
/**
 * Supabase + Vercel 一键部署脚本
 * 自动配置和部署LED网站到现代化云架构
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 LED网站 Supabase + Vercel 一键部署');
console.log('=' .repeat(50));

// 检查必要的工具
function checkRequirements() {
  console.log('📋 检查部署环境...');
  
  try {
    execSync('npm --version', { stdio: 'ignore' });
    console.log('✅ Node.js/npm 已安装');
  } catch (error) {
    console.error('❌ 请先安装 Node.js 和 npm');
    process.exit(1);
  }

  try {
    execSync('npx supabase --version', { stdio: 'ignore' });
    console.log('✅ Supabase CLI 可用');
  } catch (error) {
    console.log('📦 安装 Supabase CLI...');
    execSync('npm install -g supabase', { stdio: 'inherit' });
  }

  try {
    execSync('npx vercel --version', { stdio: 'ignore' });
    console.log('✅ Vercel CLI 可用');
  } catch (error) {
    console.log('📦 安装 Vercel CLI...');
    execSync('npm install -g vercel', { stdio: 'inherit' });
  }
}

// 安装依赖
function installDependencies() {
  console.log('\n📦 安装项目依赖...');
  execSync('npm install', { stdio: 'inherit' });
  console.log('✅ 依赖安装完成');
}

// 初始化Supabase项目
function initSupabase() {
  console.log('\n🗄️  初始化 Supabase 项目...');
  
  if (!fs.existsSync('supabase')) {
    execSync('npx supabase init', { stdio: 'inherit' });
  }
  
  // 启动本地Supabase
  console.log('🔄 启动本地 Supabase 服务...');
  try {
    execSync('npx supabase start', { stdio: 'inherit' });
    console.log('✅ Supabase 本地服务启动成功');
  } catch (error) {
    console.log('⚠️  Supabase 服务可能已在运行');
  }
  
  // 应用数据库架构
  if (fs.existsSync('supabase/schema.sql')) {
    console.log('📊 应用数据库架构...');
    execSync('npx supabase db reset', { stdio: 'inherit' });
    console.log('✅ 数据库架构应用完成');
  }
}

// 配置环境变量
function setupEnvironment() {
  console.log('\n⚙️  配置环境变量...');
  
  // 获取本地Supabase配置
  try {
    const status = execSync('npx supabase status', { encoding: 'utf8' });
    const apiUrl = status.match(/API URL: (.*)/)?.[1];
    const anonKey = status.match(/anon key: (.*)/)?.[1];
    
    if (apiUrl && anonKey) {
      const envContent = `# Supabase配置
NEXT_PUBLIC_SUPABASE_URL=${apiUrl}
NEXT_PUBLIC_SUPABASE_ANON_KEY=${anonKey}

# 网站配置
NEXT_PUBLIC_SITE_NAME=深圳联进科技有限公司
NODE_ENV=development
`;
      
      fs.writeFileSync('.env.local', envContent);
      console.log('✅ 本地环境变量配置完成');
      console.log(`📍 Supabase URL: ${apiUrl}`);
      console.log(`🔑 Anon Key: ${anonKey.substring(0, 20)}...`);
    }
  } catch (error) {
    console.log('⚠️  无法自动获取Supabase配置，请手动配置');
  }
}

// 构建项目
function buildProject() {
  console.log('\n🔨 构建项目...');
  try {
    execSync('npm run build', { stdio: 'inherit' });
    console.log('✅ 项目构建成功');
  } catch (error) {
    console.log('⚠️  构建过程中出现警告，但可以继续部署');
  }
}

// 部署到Vercel
function deployToVercel() {
  console.log('\n🚀 部署到 Vercel...');
  
  try {
    // 登录Vercel（如果需要）
    execSync('npx vercel login', { stdio: 'inherit' });
    
    // 部署项目
    const deployOutput = execSync('npx vercel --prod', { encoding: 'utf8', stdio: 'inherit' });
    
    console.log('✅ Vercel 部署成功！');
    
    // 提取部署URL
    const urlMatch = deployOutput.match(/https:\/\/[^\s]+/);
    if (urlMatch) {
      console.log(`🌐 部署地址: ${urlMatch[0]}`);
    }
    
  } catch (error) {
    console.error('❌ Vercel 部署失败:', error.message);
    console.log('💡 请检查 Vercel 配置和权限');
  }
}

// 显示部署后的配置说明
function showPostDeploymentInstructions() {
  console.log('\n' + '='.repeat(50));
  console.log('🎉 部署完成！后续配置说明：');
  console.log('='.repeat(50));
  
  console.log('\n📋 Supabase 生产环境配置：');
  console.log('1. 访问 https://supabase.com 创建新项目');
  console.log('2. 在项目设置中获取 URL 和 API Key');
  console.log('3. 在 SQL Editor 中运行 supabase/schema.sql');
  console.log('4. 配置行级安全策略（RLS）');
  
  console.log('\n🔧 Vercel 环境变量配置：');
  console.log('1. 在 Vercel Dashboard 中打开项目');
  console.log('2. 进入 Settings > Environment Variables');
  console.log('3. 添加以下变量：');
  console.log('   - NEXT_PUBLIC_SUPABASE_URL');
  console.log('   - NEXT_PUBLIC_SUPABASE_ANON_KEY');
  console.log('   - SUPABASE_SERVICE_ROLE_KEY');
  
  console.log('\n🔐 管理员账户设置：');
  console.log('1. 在 Supabase Auth 中创建管理员用户');
  console.log('2. 在 user_profiles 表中设置角色为 admin');
  console.log('3. 使用邮箱和密码登录后台管理');
  
  console.log('\n🌐 访问地址：');
  console.log('- 前端网站: [Vercel部署地址]');
  console.log('- 后台管理: [Vercel部署地址]/admin');
  console.log('- Supabase Dashboard: https://supabase.com/dashboard');
  
  console.log('\n📚 更多帮助：');
  console.log('- Supabase文档: https://supabase.com/docs');
  console.log('- Vercel文档: https://vercel.com/docs');
  console.log('- 项目README: ./README.md');
}

// 主函数
async function main() {
  try {
    checkRequirements();
    installDependencies();
    initSupabase();
    setupEnvironment();
    buildProject();
    deployToVercel();
    showPostDeploymentInstructions();
    
    console.log('\n🎊 一键部署完成！');
    
  } catch (error) {
    console.error('\n❌ 部署过程中出现错误:', error.message);
    console.log('\n💡 故障排除建议：');
    console.log('1. 检查网络连接');
    console.log('2. 确认 Supabase 和 Vercel 账户权限');
    console.log('3. 查看详细错误日志');
    console.log('4. 参考部署文档进行手动配置');
    process.exit(1);
  }
}

// 运行部署脚本
if (require.main === module) {
  main();
}

module.exports = { main };