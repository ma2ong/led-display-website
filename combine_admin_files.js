const fs = require('fs');

// 读取所有部分文件
const part1 = fs.readFileSync('admin-final-supabase.html', 'utf8');
const part2 = fs.readFileSync('admin-final-supabase-part2.html', 'utf8');
const part3 = fs.readFileSync('admin-final-supabase-part3.html', 'utf8');
const part4 = fs.readFileSync('admin-final-supabase-part4.html', 'utf8');
const part5 = fs.readFileSync('admin-final-supabase-part5.html', 'utf8');
const part6 = fs.readFileSync('admin-final-supabase-part6.html', 'utf8');
const part7 = fs.readFileSync('admin-final-supabase-part7.html', 'utf8');

// 合并文件
const combinedContent = part1 + part2 + part3 + part4 + part5 + part6 + part7;

// 写入合并后的文件
fs.writeFileSync('admin-complete-supabase.html', combinedContent, 'utf8');

console.log('文件合并完成，已生成 admin-complete-supabase.html');