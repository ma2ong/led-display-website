// 导入Supabase客户端
import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm'

// Supabase配置
const supabaseUrl = 'https://jirudzbqcxviytcmxegf.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y218ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4'

// 创建Supabase客户端
const supabase = createClient(supabaseUrl, supabaseAnonKey)

// 初始化Supabase数据库
async function initSupabase() {
    console.log('开始初始化Supabase...')
    
    try {
        // 检查是否已经初始化过
        const initialized = localStorage.getItem('supabaseInitialized')
        
        if (initialized) {
            console.log('Supabase已经初始化过，跳过初始化过程')
            return
        }
        
        // 创建默认管理员用户
        const { data: authUser, error: authError } = await supabase.auth.signUp({
            email: 'admin@admin.com',
            password: 'admin123'
        })
        
        if (authError) {
            // 如果用户已存在，尝试登录
            if (authError.message.includes('already registered')) {
                console.log('默认管理员用户已存在，尝试登录')
                
                const { data: signInData, error: signInError } = await supabase.auth.signInWithPassword({
                    email: 'admin@admin.com',
                    password: 'admin123'
                })
                
                if (signInError) {
                    console.error('登录失败:', signInError)
                    return
                }
                
                console.log('登录成功')
            } else {
                console.error('创建默认管理员用户失败:', authError)
                return
            }
        } else {
            console.log('默认管理员用户创建成功')
        }
        
        // 标记为已初始化
        localStorage.setItem('supabaseInitialized', 'true')
        console.log('Supabase初始化完成')
        
    } catch (error) {
        console.error('初始化Supabase失败:', error)
    }
}

// 导出初始化函数
export { initSupabase, supabase }

// 自动执行初始化
document.addEventListener('DOMContentLoaded', initSupabase)