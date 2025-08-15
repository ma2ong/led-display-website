// 验证Supabase数据库表是否创建成功
import { createClient } from '@supabase/supabase-js'

// 使用项目中的公开配置（仅用于读取验证）
const supabaseUrl = 'https://jirudzbqcxviytcmxegf.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y214ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4'

const supabase = createClient(supabaseUrl, supabaseAnonKey)

async function verifyTables() {
  console.log('🔍 正在验证Supabase数据库表创建状态...\n')
  
  const tables = [
    { name: 'page_contents', description: '页面内容表' },
    { name: 'page_sections', description: '页面区块表' },
    { name: 'site_settings', description: '网站设置表' },
    { name: 'content_history', description: '内容历史表' },
    { name: 'page_metadata', description: '页面元数据表' }
  ]
  
  let successCount = 0
  let errorCount = 0
  
  for (const table of tables) {
    try {
      const { count, error } = await supabase
        .from(table.name)
        .select('*', { count: 'exact', head: true })
      
      if (error) {
        console.log(`❌ ${table.name} (${table.description}): ${error.message}`)
        errorCount++
      } else {
        console.log(`✅ ${table.name} (${table.description}): 创建成功，包含 ${count} 条记录`)
        successCount++
      }
    } catch (err) {
      console.log(`❌ ${table.name} (${table.description}): ${err.message}`)
      errorCount++
    }
  }
  
  console.log('\n' + '='.repeat(60))
  console.log(`📊 验证结果：`)
  console.log(`✅ 成功创建: ${successCount} 个表`)
  console.log(`❌ 失败/未创建: ${errorCount} 个表`)
  
  if (errorCount === 0) {
    console.log('\n🎉 恭喜！所有数据库表都已成功创建！')
    console.log('📝 你现在可以使用内容管理系统的所有功能了')
    console.log('\n🚀 下一步：')
    console.log('• 访问 /admin.html 进入管理后台')
    console.log('• 开始编辑网站内容')
    console.log('• 体验实时内容同步功能')
  } else if (errorCount === tables.length) {
    console.log('\n⚠️  看起来数据库表还没有创建')
    console.log('💡 请按照以下步骤执行SQL：')
    console.log('1. 运行: node database/show-sql.js')
    console.log('2. 复制输出的SQL代码')
    console.log('3. 在Supabase控制台的SQL Editor中执行')
  } else {
    console.log('\n⚠️  部分表创建失败，建议重新执行完整的SQL脚本')
  }
}

// 执行验证
verifyTables().catch(error => {
  console.error('💥 验证过程出错：', error.message)
  console.log('\n💡 可能的原因：')
  console.log('• 网络连接问题')
  console.log('• Supabase项目配置问题') 
  console.log('• 数据库表尚未创建')
})
