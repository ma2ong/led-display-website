/**
 * Supabase Integration API
 * Handles all database operations using Supabase
 */

import { supabase } from '../lib/supabase.js'

// Products API
export const ProductsAPI = {
  // Get all products
  async getAll() {
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .order('created_at', { ascending: false })
    
    if (error) throw error
    return data
  },

  // Get products by category
  async getByCategory(category) {
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .eq('category', category)
      .order('created_at', { ascending: false })
    
    if (error) throw error
    return data
  },

  // Get single product
  async getById(id) {
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .eq('id', id)
      .single()
    
    if (error) throw error
    return data
  },

  // Create new product
  async create(productData) {
    const { data, error } = await supabase
      .from('products')
      .insert([productData])
      .select()
    
    if (error) throw error
    return data[0]
  },

  // Update product
  async update(id, productData) {
    const { data, error } = await supabase
      .from('products')
      .update(productData)
      .eq('id', id)
      .select()
    
    if (error) throw error
    return data[0]
  },

  // Delete product
  async delete(id) {
    const { error } = await supabase
      .from('products')
      .delete()
      .eq('id', id)
    
    if (error) throw error
    return true
  }
}

// Inquiries API
export const InquiriesAPI = {
  // Get all inquiries
  async getAll() {
    const { data, error } = await supabase
      .from('inquiries')
      .select('*')
      .order('created_at', { ascending: false })
    
    if (error) throw error
    return data
  },

  // Create new inquiry
  async create(inquiryData) {
    const { data, error } = await supabase
      .from('inquiries')
      .insert([inquiryData])
      .select()
    
    if (error) throw error
    return data[0]
  },

  // Update inquiry status
  async updateStatus(id, status) {
    const { data, error } = await supabase
      .from('inquiries')
      .update({ status, updated_at: new Date().toISOString() })
      .eq('id', id)
      .select()
    
    if (error) throw error
    return data[0]
  },

  // Delete inquiry
  async delete(id) {
    const { error } = await supabase
      .from('inquiries')
      .delete()
      .eq('id', id)
    
    if (error) throw error
    return true
  }
}

// News API
export const NewsAPI = {
  // Get all published news
  async getPublished() {
    const { data, error } = await supabase
      .from('news')
      .select('*')
      .eq('status', 'published')
      .order('created_at', { ascending: false })
    
    if (error) throw error
    return data
  },

  // Get all news (admin)
  async getAll() {
    const { data, error } = await supabase
      .from('news')
      .select('*')
      .order('created_at', { ascending: false })
    
    if (error) throw error
    return data
  },

  // Get single news article
  async getById(id) {
    const { data, error } = await supabase
      .from('news')
      .select('*')
      .eq('id', id)
      .single()
    
    if (error) throw error
    return data
  },

  // Create new news article
  async create(newsData) {
    const { data, error } = await supabase
      .from('news')
      .insert([newsData])
      .select()
    
    if (error) throw error
    return data[0]
  },

  // Update news article
  async update(id, newsData) {
    const { data, error } = await supabase
      .from('news')
      .update({ ...newsData, updated_at: new Date().toISOString() })
      .eq('id', id)
      .select()
    
    if (error) throw error
    return data[0]
  },

  // Delete news article
  async delete(id) {
    const { error } = await supabase
      .from('news')
      .delete()
      .eq('id', id)
    
    if (error) throw error
    return true
  }
}

// Users API (for admin management)
export const UsersAPI = {
  // Get all users
  async getAll() {
    const { data, error } = await supabase
      .from('users')
      .select('id, username, email, role, created_at, updated_at')
      .order('created_at', { ascending: false })
    
    if (error) throw error
    return data
  },

  // Create new user
  async create(userData) {
    const { data, error } = await supabase
      .from('users')
      .insert([userData])
      .select('id, username, email, role, created_at, updated_at')
    
    if (error) throw error
    return data[0]
  },

  // Update user
  async update(id, userData) {
    const { data, error } = await supabase
      .from('users')
      .update({ ...userData, updated_at: new Date().toISOString() })
      .eq('id', id)
      .select('id, username, email, role, created_at, updated_at')
    
    if (error) throw error
    return data[0]
  },

  // Delete user
  async delete(id) {
    const { error } = await supabase
      .from('users')
      .delete()
      .eq('id', id)
    
    if (error) throw error
    return true
  }
}

// Auth API helpers
export const AuthAPI = {
  // Sign up new user
  async signUp(email, password, metadata = {}) {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: metadata
      }
    })
    
    if (error) throw error
    return data
  },

  // Sign in user
  async signIn(email, password) {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    })
    
    if (error) throw error
    return data
  },

  // Sign out user
  async signOut() {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
    return true
  },

  // Get current user
  async getCurrentUser() {
    const { data: { user }, error } = await supabase.auth.getUser()
    if (error) throw error
    return user
  },

  // Get current session
  async getSession() {
    const { data: { session }, error } = await supabase.auth.getSession()
    if (error) throw error
    return session
  },

  // Listen to auth changes
  onAuthStateChange(callback) {
    return supabase.auth.onAuthStateChange(callback)
  }
}

// Statistics API
export const StatsAPI = {
  async getDashboardStats() {
    try {
      // Get products count
      const { count: productsCount } = await supabase
        .from('products')
        .select('*', { count: 'exact', head: true })

      // Get inquiries count
      const { count: inquiriesCount } = await supabase
        .from('inquiries')
        .select('*', { count: 'exact', head: true })

      // Get pending inquiries count
      const { count: pendingInquiries } = await supabase
        .from('inquiries')
        .select('*', { count: 'exact', head: true })
        .eq('status', 'pending')

      // Get published news count
      const { count: newsCount } = await supabase
        .from('news')
        .select('*', { count: 'exact', head: true })
        .eq('status', 'published')

      // Get users count
      const { count: usersCount } = await supabase
        .from('users')
        .select('*', { count: 'exact', head: true })

      return {
        products: productsCount || 0,
        inquiries: inquiriesCount || 0,
        pendingInquiries: pendingInquiries || 0,
        news: newsCount || 0,
        users: usersCount || 0
      }
    } catch (error) {
      console.error('Error fetching dashboard stats:', error)
      return {
        products: 0,
        inquiries: 0,
        pendingInquiries: 0,
        news: 0,
        users: 0
      }
    }
  }
}

// Real-time subscriptions
export const RealtimeAPI = {
  // Subscribe to table changes
  subscribeToTable(table, callback) {
    return supabase
      .channel(`public:${table}`)
      .on('postgres_changes', 
        { event: '*', schema: 'public', table: table }, 
        callback
      )
      .subscribe()
  },

  // Subscribe to inquiries changes
  subscribeToInquiries(callback) {
    return this.subscribeToTable('inquiries', callback)
  },

  // Subscribe to products changes
  subscribeToProducts(callback) {
    return this.subscribeToTable('products', callback)
  },

  // Subscribe to news changes
  subscribeToNews(callback) {
    return this.subscribeToTable('news', callback)
  }
}

// Export all APIs
export {
  supabase,
  ProductsAPI,
  InquiriesAPI,
  NewsAPI,
  UsersAPI,
  AuthAPI,
  StatsAPI,
  RealtimeAPI
}