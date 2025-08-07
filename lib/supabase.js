import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://jirudzbqcxviytcmxegf.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y214ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// 导出配置信息
export const supabaseConfig = {
  url: supabaseUrl,
  anonKey: supabaseAnonKey
}

// 数据库操作辅助函数
export const dbOperations = {
  // 获取所有产品
  async getProducts() {
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .order('created_at', { ascending: false })
    
    if (error) throw error
    return data
  },

  // 根据分类获取产品
  async getProductsByCategory(category) {
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .eq('category', category)
      .order('created_at', { ascending: false })
    
    if (error) throw error
    return data
  },

  // 获取单个产品
  async getProduct(id) {
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .eq('id', id)
      .single()
    
    if (error) throw error
    return data
  },

  // 提交询盘
  async submitInquiry(inquiryData) {
    const { data, error } = await supabase
      .from('inquiries')
      .insert([inquiryData])
      .select()
    
    if (error) throw error
    return data
  },

  // 获取新闻列表
  async getNews(limit = 10) {
    const { data, error } = await supabase
      .from('news')
      .select('*')
      .eq('status', 'published')
      .order('created_at', { ascending: false })
      .limit(limit)
    
    if (error) throw error
    return data
  },

  // 获取最新新闻
  async getLatestNews(limit = 3) {
    const { data, error } = await supabase
      .from('news')
      .select('*')
      .eq('status', 'published')
      .order('created_at', { ascending: false })
      .limit(limit)
    
    if (error) throw error
    return data
  },

  // 用户认证
  async authenticateUser(username, password) {
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .eq('username', username)
      .eq('password', password)
      .single()
    
    if (error) throw error
    return data
  }
}

// 实时订阅功能
export const subscriptions = {
  // 订阅产品变化
  subscribeToProducts(callback) {
    return supabase
      .channel('products')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'products' }, callback)
      .subscribe()
  },

  // 订阅询盘变化
  subscribeToInquiries(callback) {
    return supabase
      .channel('inquiries')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'inquiries' }, callback)
      .subscribe()
  },

  // 订阅新闻变化
  subscribeToNews(callback) {
    return supabase
      .channel('news')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'news' }, callback)
      .subscribe()
  }
}

export default supabase