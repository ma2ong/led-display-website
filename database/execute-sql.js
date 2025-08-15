// 简化的Supabase SQL执行器
import { createClient } from '@supabase/supabase-js'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// 配置
const supabaseUrl = 'https://jirudzbqcxviytcmxegf.supabase.co'
let supabaseKey = process.env.SUPABASE_SERVICE_KEY

// 如果没有环境变量，尝试从命令行参数获取
if (!supabaseKey && process.argv.length > 2) {
  supabaseKey = process.argv[2]
}

// 如果仍然没有key，提供指导
if (!supabaseKey) {
  console.log('\n🔑 需要Supabase Service Role Key来执行SQL脚本')
  console.log('\n📋 获取Service Role Key的步骤：')
  console.log('1. 打开 https://supabase.com/dashboard/projects')
  console.log('2. 选择你的项目')
  console.log('3. 进入 Settings → API')
  console.log('4. 复制 "Service Role Key" (service_role)')
  console.log('\n💡 运行方式：')
  console.log('方式1: 设置环境变量')
  console.log('  $env:SUPABASE_SERVICE_KEY="your_service_key_here"')
  console.log('  node database/execute-sql.js')
  console.log('\n方式2: 直接传参')
  console.log('  node database/execute-sql.js "your_service_key_here"')
  console.log('\n方式3: 手动复制SQL到Supabase控制台')
  console.log('  复制 database/create_tables.sql 的内容')
  console.log('  粘贴到 Supabase Dashboard → SQL Editor → 执行')
  process.exit(0)
}

const supabase = createClient(supabaseUrl, supabaseKey)

async function executeSQLScript() {
  try {
    console.log('🚀 开始执行Supabase数据库初始化...')
    
    // 读取SQL文件
    const sqlPath = path.join(__dirname, 'create_tables.sql')
    const sqlContent = fs.readFileSync(sqlPath, 'utf8')
    
    console.log('📖 读取SQL文件成功')
    console.log('📊 正在执行数据库脚本...')
    
    // 直接执行整个SQL脚本
    const { data, error } = await supabase.rpc('exec', {
      sql: sqlContent
    })
    
    if (error) {
      console.error('❌ 执行SQL脚本出错：', error)
      
      // 尝试分段执行
      console.log('🔄 尝试分段执行SQL语句...')
      await executeSQLByParts(sqlContent)
    } else {
      console.log('✅ SQL脚本执行成功！')
    }
    
    // 验证表创建
    await verifyTables()
    
  } catch (error) {
    console.error('💥 脚本执行失败：', error.message)
    console.log('\n💡 建议：')
    console.log('1. 检查Service Role Key是否正确')
    console.log('2. 确认Supabase项目URL是否正确')
    console.log('3. 或者手动在Supabase SQL编辑器中执行SQL')
  }
}

async function executeSQLByParts(sqlContent) {
  // 分割SQL语句
  const statements = sqlContent
    .replace(/\r\n/g, '\n')
    .split(';')
    .map(stmt => stmt.trim())
    .filter(stmt => stmt.length > 0 && !stmt.startsWith('--'))
  
  console.log(`📝 分割为 ${statements.length} 个SQL语句`)
  
  let successCount = 0
  let errorCount = 0
  
  for (let i = 0; i < statements.length; i++) {
    const statement = statements[i]
    if (statement.trim()) {
      try {
        // 使用不同的方法执行SQL
        const { error } = await supabase.rpc('exec', { sql: statement + ';' })
        
        if (error) {
          console.warn(`⚠️  语句 ${i + 1} 警告:`, error.message.substring(0, 100))
          errorCount++
        } else {
          successCount++
          if (i % 10 === 0) {
            console.log(`✅ 已执行 ${i + 1}/${statements.length} 个语句`)
          }
        }
      } catch (err) {
        console.warn(`❌ 语句 ${i + 1} 错误:`, err.message.substring(0, 100))
        errorCount++
      }
    }
  }
  
  console.log(`\n📈 执行结果：`)
  console.log(`✅ 成功: ${successCount} 个语句`)
  console.log(`⚠️  警告/错误: ${errorCount} 个语句`)
}

async function verifyTables() {
  console.log('\n🔍 验证数据库表创建状态...')
  
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
        console.log(`❌ ${tableName}: ${error.message}`)
      } else {
        console.log(`✅ ${tableName}: 创建成功 (${count} 条记录)`)
      }
    } catch (err) {
      console.log(`❌ ${tableName}: ${err.message}`)
    }
  }
  
  console.log('\n🎉 数据库初始化完成！')
  console.log('📝 你现在可以使用内容管理系统功能了')
}

// 执行脚本
executeSQLScript()
