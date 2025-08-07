// Complete Supabase Website Integration
// This file integrates all Supabase functionality with the LED display website

import { supabase, db, auth, testConnection } from '../lib/supabase-client.js'
import { contactFormHandler } from './contact-form-supabase.js'

class SupabaseWebsiteIntegration {
  constructor() {
    this.isConnected = false
    this.products = []
    this.news = []
    this.init()
  }

  async init() {
    console.log('🚀 Initializing Supabase Website Integration...')
    
    try {
      // Test connection
      const connectionResult = await testConnection()
      this.isConnected = connectionResult.success
      
      if (this.isConnected) {
        console.log('✅ Supabase connected successfully')
        this.showConnectionStatus(true)
        
        // Load dynamic content
        await this.loadDynamicContent()
        
        // Set up real-time subscriptions
        this.setupRealTimeSubscriptions()
        
        // Initialize auth state
        this.initAuthState()
        
      } else {
        console.warn('⚠️ Supabase connection failed, using fallback mode')
        this.showConnectionStatus(false)
      }
      
    } catch (error) {
      console.error('❌ Supabase initialization failed:', error)
      this.showConnectionStatus(false)
    }
  }

  showConnectionStatus(connected) {
    // Create or update connection indicator
    let indicator = document.querySelector('#supabase-status-indicator')
    
    if (!indicator) {
      indicator = document.createElement('div')
      indicator.id = 'supabase-status-indicator'
      document.body.appendChild(indicator)
    }
    
    indicator.style.cssText = `
      position: fixed;
      top: 10px;
      right: 10px;
      padding: 8px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 500;
      z-index: 9999;
      color: white;
      box-shadow: 0 2px 8px rgba(0,0,0,0.15);
      transition: all 0.3s ease;
      ${connected ? 'background: linear-gradient(135deg, #10b981, #059669);' : 'background: linear-gradient(135deg, #ef4444, #dc2626);'}
    `
    
    indicator.innerHTML = connected ? 
      '🟢 Backend Online' : 
      '🔴 Backend Offline'
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
      if (indicator) {
        indicator.style.opacity = '0'
        setTimeout(() => {
          if (indicator && indicator.parentNode) {
            indicator.parentNode.removeChild(indicator)
          }
        }, 300)
      }
    }, 3000)
  }

  async loadDynamicContent() {
    if (!this.isConnected) return
    
    try {
      // Load products for product pages
      await this.loadProducts()
      
      // Load news for news sections
      await this.loadNews()
      
      // Update statistics
      await this.updateStatistics()
      
      console.log('✅ Dynamic content loaded successfully')
      
    } catch (error) {
      console.error('❌ Failed to load dynamic content:', error)
    }
  }

  async loadProducts() {
    try {
      this.products = await db.products.getAll()
      console.log(`📦 Loaded ${this.products.length} products`)
      
      // Update product displays on the page
      this.updateProductDisplays()
      
    } catch (error) {
      console.error('Error loading products:', error)
    }
  }

  async loadNews() {
    try {
      this.news = await db.news.getAll()
      console.log(`📰 Loaded ${this.news.length} news articles`)
      
      // Update news displays on the page
      this.updateNewsDisplays()
      
    } catch (error) {
      console.error('Error loading news:', error)
    }
  }

  updateProductDisplays() {
    // Update product cards if they exist
    const productContainers = document.querySelectorAll('.products-grid, .product-showcase, .featured-products')
    
    productContainers.forEach(container => {
      if (this.products.length > 0) {
        // Create product cards
        const productHTML = this.products.slice(0, 6).map(product => `
          <div class="product-card" data-product-id="${product.id}">
            <div class="product-image">
              <img src="${product.image_url || 'assets/images/placeholder-product.jpg'}" 
                   alt="${product.name}" 
                   onerror="this.src='assets/images/placeholder-product.jpg'">
            </div>
            <div class="product-info">
              <h3>${product.name}</h3>
              <p class="product-category">${product.category}</p>
              <p class="product-description">${product.description || ''}</p>
              ${product.price ? `<p class="product-price">$${product.price}</p>` : ''}
            </div>
          </div>
        `).join('')
        
        container.innerHTML = productHTML
      }
    })
  }

  updateNewsDisplays() {
    // Update news sections if they exist
    const newsContainers = document.querySelectorAll('.news-grid, .latest-news, .news-showcase')
    
    newsContainers.forEach(container => {
      if (this.news.length > 0) {
        // Create news cards
        const newsHTML = this.news.slice(0, 3).map(article => `
          <div class="news-card" data-news-id="${article.id}">
            <div class="news-content">
              <h3>${article.title}</h3>
              <p class="news-meta">
                ${article.author ? `By ${article.author} • ` : ''}
                ${new Date(article.created_at).toLocaleDateString()}
              </p>
              <p class="news-excerpt">${this.truncateText(article.content, 150)}</p>
              <a href="news.html#article-${article.id}" class="read-more">Read More</a>
            </div>
          </div>
        `).join('')
        
        container.innerHTML = newsHTML
      }
    })
  }

  async updateStatistics() {
    try {
      // Get counts from database
      const [productsResult, inquiriesResult, newsResult] = await Promise.all([
        supabase.from('products').select('*', { count: 'exact', head: true }),
        supabase.from('inquiries').select('*', { count: 'exact', head: true }),
        supabase.from('news').select('*', { count: 'exact', head: true })
      ])
      
      const stats = {
        products: productsResult.count || 0,
        inquiries: inquiriesResult.count || 0,
        news: newsResult.count || 0
      }
      
      console.log('📊 Statistics updated:', stats)
      
      // Update stats displays on page
      this.updateStatsDisplays(stats)
      
    } catch (error) {
      console.error('Error updating statistics:', error)
    }
  }

  updateStatsDisplays(stats) {
    // Update any statistics displays
    const statElements = {
      products: document.querySelectorAll('[data-stat="products"], .stat-products'),
      inquiries: document.querySelectorAll('[data-stat="inquiries"], .stat-inquiries'),
      news: document.querySelectorAll('[data-stat="news"], .stat-news')
    }
    
    Object.keys(statElements).forEach(key => {
      statElements[key].forEach(element => {
        element.textContent = stats[key]
      })
    })
  }

  setupRealTimeSubscriptions() {
    if (!this.isConnected) return
    
    // Subscribe to product changes
    supabase
      .channel('products-changes')
      .on('postgres_changes', 
          { event: '*', schema: 'public', table: 'products' }, 
          (payload) => {
            console.log('Products updated:', payload)
            this.loadProducts()
          }
      )
      .subscribe()
    
    // Subscribe to news changes
    supabase
      .channel('news-changes')
      .on('postgres_changes', 
          { event: '*', schema: 'public', table: 'news' }, 
          (payload) => {
            console.log('News updated:', payload)
            this.loadNews()
          }
      )
      .subscribe()
    
    console.log('🔄 Real-time subscriptions active')
  }

  initAuthState() {
    // Initialize authentication state
    auth.onAuthStateChange((event, session) => {
      console.log('Auth state changed:', event)
      
      if (event === 'SIGNED_IN') {
        this.handleUserSignIn(session.user)
      } else if (event === 'SIGNED_OUT') {
        this.handleUserSignOut()
      }
    })
  }

  handleUserSignIn(user) {
    console.log('User signed in:', user.email)
    
    // Update UI for authenticated user
    const authElements = document.querySelectorAll('.auth-required')
    authElements.forEach(el => el.style.display = 'block')
    
    const guestElements = document.querySelectorAll('.guest-only')
    guestElements.forEach(el => el.style.display = 'none')
  }

  handleUserSignOut() {
    console.log('User signed out')
    
    // Update UI for guest user
    const authElements = document.querySelectorAll('.auth-required')
    authElements.forEach(el => el.style.display = 'none')
    
    const guestElements = document.querySelectorAll('.guest-only')
    guestElements.forEach(el => el.style.display = 'block')
  }

  // Utility methods
  truncateText(text, maxLength) {
    if (!text) return ''
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength).trim() + '...'
  }

  // Public API methods
  async getProducts(category = null) {
    if (category) {
      return await db.products.getByCategory(category)
    }
    return await db.products.getAll()
  }

  async getNews() {
    return await db.news.getAll()
  }

  async submitInquiry(inquiryData) {
    return await db.inquiries.create(inquiryData)
  }

  // Connection status
  isSupabaseConnected() {
    return this.isConnected
  }
}

// Initialize the integration when DOM is ready
let websiteIntegration = null

document.addEventListener('DOMContentLoaded', () => {
  websiteIntegration = new SupabaseWebsiteIntegration()
})

// Export for global access
window.SupabaseWebsiteIntegration = SupabaseWebsiteIntegration
window.websiteIntegration = websiteIntegration

export default SupabaseWebsiteIntegration
export { websiteIntegration }