import { createClient } from '@supabase/supabase-js'

// 从环境变量获取配置
const supabaseUrl = process.env.SUPABASE_URL || 'https://jirudzbqcxviytcmxegf.supabase.co'
const supabaseAnonKey = process.env.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y214ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4'

// 创建Supabase客户端
export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// API功能封装
export const SupabaseAPI = {
  // 产品相关
  async getProducts() {
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .order('created_at', { ascending: false })
    
    if (error) throw error
    return data
  },

  async getFeaturedProducts() {
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .eq('is_featured', true)
      .order('created_at', { ascending: false })
      .limit(6)
    
    if (error) throw error
    return data
  },

  async getProductsByCategory(category) {
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .eq('category', category)
      .order('created_at', { ascending: false })
    
    if (error) throw error
    return data
  },

  async createProduct(product) {
    const { data, error } = await supabase
      .from('products')
      .insert([product])
      .select()
    
    if (error) throw error
    return data[0]
  },

  async updateProduct(id, updates) {
    const { data, error } = await supabase
      .from('products')
      .update(updates)
      .eq('id', id)
      .select()
    
    if (error) throw error
    return data[0]
  },

  async deleteProduct(id) {
    const { error } = await supabase
      .from('products')
      .delete()
      .eq('id', id)
    
    if (error) throw error
    return true
  },

  // 新闻相关
  async getPublishedNews(limit = 10) {
    const { data, error } = await supabase
      .from('news')
      .select('*')
      .eq('status', 'published')
      .order('created_at', { ascending: false })
      .limit(limit)
    
    if (error) throw error
    return data
  },

  async createNews(news) {
    const { data, error } = await supabase
      .from('news')
      .insert([news])
      .select()
    
    if (error) throw error
    return data[0]
  },

  async updateNews(id, updates) {
    const { data, error } = await supabase
      .from('news')
      .update(updates)
      .eq('id', id)
      .select()
    
    if (error) throw error
    return data[0]
  },

  async deleteNews(id) {
    const { error } = await supabase
      .from('news')
      .delete()
      .eq('id', id)
    
    if (error) throw error
    return true
  },

  // 询盘相关
  async createInquiry(inquiry) {
    const { data, error } = await supabase
      .from('inquiries')
      .insert([{
        ...inquiry,
        status: 'pending',
        created_at: new Date().toISOString()
      }])
      .select()
    
    if (error) throw error
    return data[0]
  },

  async getInquiries() {
    const { data, error } = await supabase
      .from('inquiries')
      .select('*')
      .order('created_at', { ascending: false })
    
    if (error) throw error
    return data
  },

  async updateInquiryStatus(id, status) {
    const { data, error } = await supabase
      .from('inquiries')
      .update({ status })
      .eq('id', id)
      .select()
    
    if (error) throw error
    return data[0]
  },

  // 统计数据
  async getStats() {
    const [products, news, inquiries] = await Promise.all([
      supabase.from('products').select('count'),
      supabase.from('news').select('count'),
      supabase.from('inquiries').select('count')
    ])

    return {
      products_count: products.count || 0,
      news_count: news.count || 0,
      inquiries_count: inquiries.count || 0,
      projects_completed: 15000, // 这些可以从设置表读取
      countries_served: 120,
      years_experience: 25,
      expert_engineers: 500
    }
  }
}
