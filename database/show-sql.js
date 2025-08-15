// SQL内容显示工具 - 方便复制到Supabase控制台
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

function showSQL() {
  try {
    // 读取SQL文件
    const sqlPath = path.join(__dirname, 'create_tables.sql')
    const sqlContent = fs.readFileSync(sqlPath, 'utf8')
    
    console.log('=' .repeat(80))
    console.log('🗄️  SUPABASE 数据库初始化 SQL')
    console.log('=' .repeat(80))
    console.log('\n📋 复制下面的SQL代码，然后：')
    console.log('1. 打开 https://supabase.com/dashboard/projects')
    console.log('2. 选择你的项目')
    console.log('3. 进入 SQL Editor')
    console.log('4. 粘贴下面的SQL代码')
    console.log('5. 点击 RUN 执行')
    console.log('\n' + '=' .repeat(80))
    console.log('📝 SQL 代码开始：')
    console.log('=' .repeat(80))
    
    // 输出SQL内容
    console.log(sqlContent)
    
    console.log('\n' + '=' .repeat(80))
    console.log('📝 SQL 代码结束')
    console.log('=' .repeat(80))
    
    console.log('\n✨ 执行完成后，你的内容管理系统将会创建以下表：')
    console.log('• page_contents - 页面内容表')
    console.log('• page_sections - 页面区块表')
    console.log('• site_settings - 网站设置表')
    console.log('• content_history - 内容历史表')
    console.log('• page_metadata - 页面元数据表')
    
  } catch (error) {
    console.error('❌ 读取SQL文件失败：', error.message)
  }
}

showSQL()
