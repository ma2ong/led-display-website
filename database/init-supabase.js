// Supabase数据库初始化脚本
import { createClient } from '@supabase/supabase-js'
import fs from 'fs'
import path from 'path'

// Supabase配置
const supabaseUrl = process.env.SUPABASE_URL || 'https://jirudzbqcxviytcmxegf.supabase.co'
const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY // 需要服务密钥来执行SQL

if (!supabaseServiceKey) {
  console.error('错误: 需要设置SUPABASE_SERVICE_KEY环境变量')
  console.log('请在Supabase控制台的Settings > API中找到Service Role Key')
  process.exit(1)
}

const supabase = createClient(supabaseUrl, supabaseServiceKey)

async function initializeDatabase() {
  try {
    console.log('开始初始化Supabase数据库...')
    
    // 读取SQL文件
    const sqlPath = path.join(process.cwd(), 'database', 'create_tables.sql')
    const sqlContent = fs.readFileSync(sqlPath, 'utf8')
    
    console.log('正在执行数据库表创建SQL...')
    
    // 分割SQL语句并逐个执行
    const statements = sqlContent
      .split(';')
      .map(stmt => stmt.trim())
      .filter(stmt => stmt.length > 0 && !stmt.startsWith('--'))
    
    let successCount = 0
    let errorCount = 0
    
    for (const statement of statements) {
      try {
        if (statement.trim()) {
          const { error } = await supabase.rpc('exec_sql', { sql: statement })
          if (error) {
            console.warn(`执行语句时出现警告: ${error.message}`)
            console.warn(`语句: ${statement.substring(0, 100)}...`)
            errorCount++
          } else {
            successCount++
          }
        }
      } catch (err) {
        console.warn(`执行语句时出现错误: ${err.message}`)
        console.warn(`语句: ${statement.substring(0, 100)}...`)
        errorCount++
      }
    }
    
    console.log(`数据库初始化完成!`)
    console.log(`成功执行: ${successCount} 个语句`)
    if (errorCount > 0) {
      console.log(`警告/错误: ${errorCount} 个语句`)
    }
    
    // 验证表是否创建成功
    console.log('\n正在验证表创建状态...')
    const tables = [
      'page_contents',
      'page_sections', 
      'site_settings',
      'content_history',
      'page_metadata'
    ]
    
    for (const tableName of tables) {
      try {
        const { count, error } = await supabase
          .from(tableName)
          .select('*', { count: 'exact', head: true })
        
        if (error) {
          console.log(`❌ 表 ${tableName}: ${error.message}`)
        } else {
          console.log(`✅ 表 ${tableName}: 已创建 (记录数: ${count})`)
        }
      } catch (err) {
        console.log(`❌ 表 ${tableName}: ${err.message}`)
      }
    }
    
  } catch (error) {
    console.error('数据库初始化失败:', error)
    process.exit(1)
  }
}

// 运行初始化
initializeDatabase()
