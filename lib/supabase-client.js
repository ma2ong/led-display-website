// Supabase Client Configuration for LED Display Website
// This file creates a singleton Supabase client following best practices

import { createClient } from '@supabase/supabase-js'

// Supabase configuration - 在浏览器环境中直接使用配置
const supabaseUrl = 'https://jirudzbqcxviytcmxegf.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y218ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4'

// 检查环境变量（如果在支持的环境中）
const getSupabaseConfig = () => {
  // 尝试从环境变量获取（Vercel 部署时）
  if (typeof window !== 'undefined' && window.location.hostname.includes('vercel.app')) {
    // 在 Vercel 部署环境中，环境变量会被注入到构建过程中
    return {
      url: supabaseUrl,
      key: supabaseAnonKey
    }
  }
  
  // 本地开发或其他环境
  return {
    url: supabaseUrl,
    key: supabaseAnonKey
  }
}

const config = getSupabaseConfig()

// Create Supabase client (singleton pattern)
export const supabase = createClient(config.url, config.key, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  }
})

// Database helper functions
export const db = {
  // Products operations
  products: {
    async getAll() {
      const { data, error } = await supabase
        .from('products')
        .select('*')
        .order('created_at', { ascending: false })
      
      if (error) throw error
      return data
    },

    async getById(id) {
      const { data, error } = await supabase
        .from('products')
        .select('*')
        .eq('id', id)
        .single()
      
      if (error) throw error
      return data
    },

    async getByCategory(category) {
      const { data, error } = await supabase
        .from('products')
        .select('*')
        .eq('category', category)
        .order('created_at', { ascending: false })
      
      if (error) throw error
      return data
    },

    async create(product) {
      const { data, error } = await supabase
        .from('products')
        .insert([product])
        .select()
      
      if (error) throw error
      return data[0]
    },

    async update(id, updates) {
      const { data, error } = await supabase
        .from('products')
        .update(updates)
        .eq('id', id)
        .select()
      
      if (error) throw error
      return data[0]
    },

    async delete(id) {
      const { error } = await supabase
        .from('products')
        .delete()
        .eq('id', id)
      
      if (error) throw error
    }
  },

  // News operations
  news: {
    async getAll() {
      const { data, error } = await supabase
        .from('news')
        .select('*')
        .eq('status', 'published')
        .order('created_at', { ascending: false })
      
      if (error) throw error
      return data
    },

    async getById(id) {
      const { data, error } = await supabase
        .from('news')
        .select('*')
        .eq('id', id)
        .single()
      
      if (error) throw error
      return data
    },

    async create(article) {
      const { data, error } = await supabase
        .from('news')
        .insert([article])
        .select()
      
      if (error) throw error
      return data[0]
    },

    async update(id, updates) {
      const { data, error } = await supabase
        .from('news')
        .update(updates)
        .eq('id', id)
        .select()
      
      if (error) throw error
      return data[0]
    },

    async delete(id) {
      const { error } = await supabase
        .from('news')
        .delete()
        .eq('id', id)
      
      if (error) throw error
    }
  },

  // Inquiries operations
  inquiries: {
    async getAll() {
      const { data, error } = await supabase
        .from('inquiries')
        .select('*')
        .order('created_at', { ascending: false })
      
      if (error) throw error
      return data
    },

    async create(inquiry) {
      const { data, error } = await supabase
        .from('inquiries')
        .insert([{
          ...inquiry,
          status: 'new',
          created_at: new Date().toISOString()
        }])
        .select()
      
      if (error) throw error
      return data[0]
    },

    async updateStatus(id, status) {
      const { data, error } = await supabase
        .from('inquiries')
        .update({ status })
        .eq('id', id)
        .select()
      
      if (error) throw error
      return data[0]
    },

    async delete(id) {
      const { error } = await supabase
        .from('inquiries')
        .delete()
        .eq('id', id)
      
      if (error) throw error
    }
  },

  // Users operations (for admin authentication)
  users: {
    async authenticate(username, password) {
      const { data, error } = await supabase
        .from('users')
        .select('*')
        .eq('username', username)
        .eq('password', password)
        .single()
      
      if (error) throw error
      return data
    },

    async create(user) {
      const { data, error } = await supabase
        .from('users')
        .insert([user])
        .select()
      
      if (error) throw error
      return data[0]
    }
  }
}

// Auth helper functions
export const auth = {
  // Sign up with email and password
  async signUp(email, password, userData = {}) {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: userData
      }
    })
    
    if (error) throw error
    return data
  },

  // Sign in with email and password
  async signIn(email, password) {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    })
    
    if (error) throw error
    return data
  },

  // Sign out
  async signOut() {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
  },

  // Get current user
  async getCurrentUser() {
    const { data: { user } } = await supabase.auth.getUser()
    return user
  },

  // Get current session
  async getSession() {
    const { data: { session } } = await supabase.auth.getSession()
    return session
  },

  // Listen to auth state changes
  onAuthStateChange(callback) {
    return supabase.auth.onAuthStateChange(callback)
  },

  // Reset password
  async resetPassword(email) {
    const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/reset-password`
    })
    
    if (error) throw error
    return data
  },

  // Update user
  async updateUser(updates) {
    const { data, error } = await supabase.auth.updateUser(updates)
    if (error) throw error
    return data
  }
}

// Connection test function
export async function testConnection() {
  try {
    const { data, error } = await supabase
      .from('products')
      .select('count')
      .limit(1)
    
    if (error) throw error
    
    console.log('✅ Supabase connection successful')
    return { success: true, message: 'Connected to Supabase' }
  } catch (error) {
    console.error('❌ Supabase connection failed:', error)
    return { success: false, error: error.message }
  }
}

// Export default client
export default supabase