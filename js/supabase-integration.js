// Supabase Integration for LED Display Website
import { createClient } from '@supabase/supabase-js'

// Supabase configuration
const supabaseUrl = 'https://jirudzbqcxviytcmxegf.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y214ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// API Integration Class
class LEDWebsiteAPI {
  constructor() {
    this.useSupabase = true // Set to false to use local API
    this.localApiUrl = 'http://127.0.0.1:5001'
  }

  // Products API
  async getProducts() {
    if (this.useSupabase) {
      try {
        const { data, error } = await supabase
          .from('products')
          .select('*')
          .order('created_at', { ascending: false })
        
        if (error) throw error
        return { status: 'success', data }
      } catch (error) {
        console.error('Supabase error, falling back to local API:', error)
        return this.getProductsLocal()
      }
    } else {
      return this.getProductsLocal()
    }
  }

  async getProductsLocal() {
    try {
      const response = await fetch(`${this.localApiUrl}/api/products`)
      const data = await response.json()
      return { status: 'success', data }
    } catch (error) {
      console.error('Local API error:', error)
      return { status: 'error', message: error.message }
    }
  }

  async getProductsByCategory(category) {
    if (this.useSupabase) {
      try {
        const { data, error } = await supabase
          .from('products')
          .select('*')
          .eq('category', category)
          .order('created_at', { ascending: false })
        
        if (error) throw error
        return { status: 'success', data }
      } catch (error) {
        console.error('Supabase error:', error)
        return { status: 'error', message: error.message }
      }
    } else {
      try {
        const response = await fetch(`${this.localApiUrl}/api/products/category/${category}`)
        const result = await response.json()
        return result
      } catch (error) {
        return { status: 'error', message: error.message }
      }
    }
  }

  // Contact/Inquiry API
  async submitInquiry(inquiryData) {
    if (this.useSupabase) {
      try {
        const { data, error } = await supabase
          .from('inquiries')
          .insert([{
            name: inquiryData.name,
            email: inquiryData.email,
            phone: inquiryData.phone,
            company: inquiryData.company,
            message: inquiryData.message,
            product_interest: inquiryData.product || null,
            status: 'pending'
          }])
          .select()
        
        if (error) throw error
        return { status: 'success', message: '询盘提交成功', data }
      } catch (error) {
        console.error('Supabase error, falling back to local API:', error)
        return this.submitInquiryLocal(inquiryData)
      }
    } else {
      return this.submitInquiryLocal(inquiryData)
    }
  }

  async submitInquiryLocal(inquiryData) {
    try {
      const response = await fetch(`${this.localApiUrl}/api/contact`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(inquiryData)
      })
      const result = await response.json()
      return result
    } catch (error) {
      return { status: 'error', message: error.message }
    }
  }

  // News API
  async getNews(limit = 10) {
    if (this.useSupabase) {
      try {
        const { data, error } = await supabase
          .from('news')
          .select('*')
          .eq('status', 'published')
          .order('created_at', { ascending: false })
          .limit(limit)
        
        if (error) throw error
        return { status: 'success', data }
      } catch (error) {
        console.error('Supabase error:', error)
        return this.getNewsLocal(limit)
      }
    } else {
      return this.getNewsLocal(limit)
    }
  }

  async getNewsLocal(limit) {
    try {
      const response = await fetch(`${this.localApiUrl}/api/news`)
      const result = await response.json()
      if (result.status === 'success') {
        result.data = result.news.slice(0, limit)
      }
      return result
    } catch (error) {
      return { status: 'error', message: error.message }
    }
  }

  // Real-time subscriptions (Supabase only)
  subscribeToProducts(callback) {
    if (!this.useSupabase) return null
    
    return supabase
      .channel('products')
      .on('postgres_changes', { 
        event: '*', 
        schema: 'public', 
        table: 'products' 
      }, callback)
      .subscribe()
  }

  subscribeToInquiries(callback) {
    if (!this.useSupabase) return null
    
    return supabase
      .channel('inquiries')
      .on('postgres_changes', { 
        event: '*', 
        schema: 'public', 
        table: 'inquiries' 
      }, callback)
      .subscribe()
  }

  // Health check
  async healthCheck() {
    const results = {
      supabase: false,
      local: false
    }

    // Check Supabase
    try {
      const { data, error } = await supabase
        .from('products')
        .select('count')
        .limit(1)
      
      if (!error) results.supabase = true
    } catch (error) {
      console.log('Supabase not available:', error.message)
    }

    // Check Local API
    try {
      const response = await fetch(`${this.localApiUrl}/api/health`)
      if (response.ok) results.local = true
    } catch (error) {
      console.log('Local API not available:', error.message)
    }

    return results
  }
}

// Create global API instance
window.ledAPI = new LEDWebsiteAPI()

// Export for module usage
export default LEDWebsiteAPI
export { LEDWebsiteAPI }

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
  console.log('🚀 LED Website API initialized')
  
  // Health check
  const health = await window.ledAPI.healthCheck()
  console.log('📊 API Health Status:', health)
  
  // Auto-switch to local if Supabase is not available
  if (!health.supabase && health.local) {
    window.ledAPI.useSupabase = false
    console.log('🔄 Switched to local API mode')
  }
})