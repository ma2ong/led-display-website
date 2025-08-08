// 应用数据库迁移脚本
// 解决产品表写入失败问题 (HTTP 400)

import supabase from './lib/supabase.js';
import fs from 'fs';
import path from 'path';

// 读取迁移文件
const migrationPath = path.join(process.cwd(), 'supabase/migrations/20250808_fix_products_table.sql');
const migrationSQL = fs.readFileSync(migrationPath, 'utf8');

// 分割SQL语句
const sqlStatements = migrationSQL
  .split(';')
  .map(stmt => stmt.trim())
  .filter(stmt => stmt.length > 0);

// 执行迁移
async function applyMigration() {
  console.log('开始应用数据库迁移...');
  console.log(`共 ${sqlStatements.length} 条SQL语句需要执行`);
  
  let successCount = 0;
  let errorCount = 0;
  
  for (let i = 0; i < sqlStatements.length; i++) {
    const sql = sqlStatements[i] + ';';
    console.log(`执行第 ${i + 1}/${sqlStatements.length} 条SQL语句...`);
    
    try {
      const { data, error } = await supabase.rpc('exec_sql', { sql });
      
      if (error) {
        console.error(`SQL执行失败:`, error);
        errorCount++;
      } else {
        console.log(`SQL执行成功`);
        successCount++;
      }
    } catch (err) {
      console.error(`SQL执行异常:`, err);
      errorCount++;
    }
    
    // 添加延迟避免频率限制
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  
  console.log('迁移完成');
  console.log(`成功: ${successCount}, 失败: ${errorCount}`);
  
  return {
    total: sqlStatements.length,
    success: successCount,
    error: errorCount
  };
}

// 执行迁移
applyMigration()
  .then(result => {
    console.log('迁移结果:', result);
    process.exit(0);
  })
  .catch(err => {
    console.error('迁移过程出错:', err);
    process.exit(1);
  });