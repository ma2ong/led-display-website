// Supabase客户端配置
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// 数据库操作封装
export class SupabaseAPI {
  // 产品相关操作
  static async getProducts() {
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .order('created_at', { ascending: false })
    
    if (error) throw error
    return data
  }

  static async getFeaturedProducts(limit = 4) {
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(limit)
    
    if (error) throw error
    return data
  }

  static async createProduct(product) {
    const { data, error } = await supabase
      .from('products')
      .insert([product])
      .select()
    
    if (error) throw error
    return data[0]
  }

  static async updateProduct(id, updates) {
    const { data, error } = await supabase
      .from('products')
      .update(updates)
      .eq('id', id)
      .select()
    
    if (error) throw error
    return data[0]
  }

  static async deleteProduct(id) {
    const { error } = await supabase
      .from('products')
      .delete()
      .eq('id', id)
    
    if (error) throw error
    return true
  }

  // 询盘相关操作
  static async getInquiries() {
    const { data, error } = await supabase
      .from('inquiries')
      .select('*')
      .order('created_at', { ascending: false })
    
    if (error) throw error
    return data
  }

  static async createInquiry(inquiry) {
    const { data, error } = await supabase
      .from('inquiries')
      .insert([inquiry])
      .select()
    
    if (error) throw error
    return data[0]
  }

  static async updateInquiryStatus(id, status) {
    const { data, error } = await supabase
      .from('inquiries')
      .update({ status, updated_at: new Date().toISOString() })
      .eq('id', id)
      .select()
    
    if (error) throw error
    return data[0]
  }

  // 新闻相关操作
  static async getNews() {
    const { data, error } = await supabase
      .from('news')
      .select('*')
      .order('created_at', { ascending: false })
    
    if (error) throw error
    return data
  }

  static async getPublishedNews(limit = null) {
    let query = supabase
      .from('news')
      .select('*')
      .eq('status', 'published')
      .order('created_at', { ascending: false })
    
    if (limit) {
      query = query.limit(limit)
    }
    
    const { data, error } = await query
    
    if (error) throw error
    return data
  }

  static async createNews(news) {
    const { data, error } = await supabase
      .from('news')
      .insert([news])
      .select()
    
    if (error) throw error
    return data[0]
  }

  static async updateNews(id, updates) {
    const { data, error } = await supabase
      .from('news')
      .update(updates)
      .eq('id', id)
      .select()
    
    if (error) throw error
    return data[0]
  }

  static async deleteNews(id) {
    const { error } = await supabase
      .from('news')
      .delete()
      .eq('id', id)
    
    if (error) throw error
    return true
  }

  // 用户认证相关
  static async signIn(email, password) {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    })
    
    if (error) throw error
    return data
  }

  static async signUp(email, password, userData = {}) {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: userData
      }
    })
    
    if (error) throw error
    return data
  }

  static async signOut() {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
    return true
  }

  static async getCurrentUser() {
    const { data: { user } } = await supabase.auth.getUser()
    return user
  }

  static async getUserProfile(userId) {
    const { data, error } = await supabase
      .from('user_profiles')
      .select('*')
      .eq('id', userId)
      .single()
    
    if (error) throw error
    return data
  }

  static async createUserProfile(profile) {
    const { data, error } = await supabase
      .from('user_profiles')
      .insert([profile])
      .select()
    
    if (error) throw error
    return data[0]
  }

  // 统计数据
  static async getStats() {
    const [products, inquiries, news] = await Promise.all([
      supabase.from('products').select('id', { count: 'exact' }),
      supabase.from('inquiries').select('id', { count: 'exact' }),
      supabase.from('news').select('id', { count: 'exact' }).eq('status', 'published')
    ])

    return {
      products_count: products.count || 0,
      inquiries_count: inquiries.count || 0,
      news_count: news.count || 0,
      last_updated: new Date().toISOString()
    }
  }
}

// 实时订阅功能
export class SupabaseRealtime {
  static subscribeToInquiries(callback) {
    return supabase
      .channel('inquiries')
      .on('postgres_changes', 
        { event: '*', schema: 'public', table: 'inquiries' }, 
        callback
      )
      .subscribe()
  }

  static subscribeToProducts(callback) {
    return supabase
      .channel('products')
      .on('postgres_changes', 
        { event: '*', schema: 'public', table: 'products' }, 
        callback
      )
      .subscribe()
  }

  static subscribeToNews(callback) {
    return supabase
      .channel('news')
      .on('postgres_changes', 
        { event: '*', schema: 'public', table: 'news' }, 
        callback
      )
      .subscribe()
  }
}