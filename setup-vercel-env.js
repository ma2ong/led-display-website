#!/usr/bin/env node

const { execSync } = require('child_process');

console.log('🚀 设置Vercel环境变量...');

const envVars = [
    {
        name: 'NEXT_PUBLIC_SUPABASE_URL',
        value: 'https://tfkzzgufbftlafsdyrmj.supabase.co'
    },
    {
        name: 'NEXT_PUBLIC_SUPABASE_ANON_KEY',
        value: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRma3p6Z3VmYmZ0bGFmc2R5cm1qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQzODQxOTQsImV4cCI6MjA2OTk2MDE5NH0.z5VqNaBohG-9Kwm3thBnrgAca8bePxnbBamFCBiXoLY'
    }
];

envVars.forEach((env, index) => {
    try {
        console.log(`📝 设置环境变量 ${index + 1}/${envVars.length}: ${env.name}`);
        
        // 使用echo命令传递值给vercel env add
        const command = `echo "${env.value}" | vercel env add ${env.name} production preview development`;
        execSync(command, { stdio: 'inherit' });
        
        console.log(`✅ ${env.name} 设置成功`);
    } catch (error) {
        console.error(`❌ 设置 ${env.name} 失败:`, error.message);
    }
});

console.log('🎉 环境变量设置完成！');
console.log('📋 接下来运行: vercel --prod');