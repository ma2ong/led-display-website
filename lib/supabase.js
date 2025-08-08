import { createClient } from '@supabase/supabase-js'

// 创建一个Supabase客户端单例
let supabaseInstance = null

export const getSupabaseClient = () => {
  if (supabaseInstance) return supabaseInstance
  
  const supabaseUrl = 'https://jirudzbqcxviytcmxegf.supabase.co'
  const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y218ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4'
  
  supabaseInstance = createClient(supabaseUrl, supabaseAnonKey)
  return supabaseInstance
}

// 导出一个默认的Supabase客户端实例
const supabase = getSupabaseClient()
export default supabase