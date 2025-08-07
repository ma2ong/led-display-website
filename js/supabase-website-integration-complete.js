// Complete Supabase Website Integration
// This file integrates all Supabase functionality with the LED display website

import { supabase, db, auth, testConnection } from '../lib/supabase-client.js'
import { contactFormHandler } from './contact-form-supabase.js'

class SupabaseWebsiteIntegration {
  constructor() {
    this.isConnected = false
    this.products = []
    this.news = []
    this.inquiries = []
    this.solutions = []
    this.cases = []
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
        
        // Initialize contact forms
        this.initContactForms()
        
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
      
      // Load solutions
      await this.loadSolutions()
      
      // Load cases
      await this.loadCases()
      
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
  
  async loadSolutions() {
    try {
      // Get solutions from Supabase
      const { data, error } = await supabase
        .from('solutions')
        .select('*')
        .eq('status', 'active')
        .order('created_at', { ascending: false })
      
      if (error) throw error
      
      this.solutions = data
      console.log(`💼 Loaded ${this.solutions.length} solutions`)
      
      // Update solution displays on the page
      this.updateSolutionDisplays()
      
    } catch (error) {
      console.error('Error loading solutions:', error)
    }
  }
  
  async loadCases() {
    try {
      // Get cases from Supabase
      const { data, error } = await supabase
        .from('cases')
        .select('*')
        .eq('status', 'published')
        .order('created_at', { ascending: false })
      
      if (error) throw error
      
      this.cases = data
      console.log(`📋 Loaded ${this.cases.length} cases`)
      
      // Update case displays on the page
      this.updateCaseDisplays()
      
    } catch (error) {
      console.error('Error loading cases:', error)
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
    
    // Update product category pages
    const categoryPages = {
      'indoor': document.querySelector('.indoor-products'),
      'outdoor': document.querySelector('.outdoor-products'),
      'rental': document.querySelector('.rental-products'),
      'creative': document.querySelector('.creative-products'),
      'transparent': document.querySelector('.transparent-products')
    }
    
    Object.keys(categoryPages).forEach(category => {
      const container = categoryPages[category]
      if (container) {
        const filteredProducts = this.products.filter(p => 
          p.category && p.category.toLowerCase().includes(category)
        )
        
        if (filteredProducts.length > 0) {
          const productHTML = filteredProducts.map(product => `
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
    
    // Update news page if it exists
    const newsPage = document.querySelector('.news-page-content')
    if (newsPage && this.news.length > 0) {
      const newsHTML = this.news.map(article => `
        <div class="news-article" id="article-${article.id}">
          <h2>${article.title}</h2>
          <div class="news-meta">
            ${article.author ? `<span class="author">By ${article.author}</span>` : ''}
            <span class="date">${new Date(article.created_at).toLocaleDateString()}</span>
            ${article.category ? `<span class="category">${article.category}</span>` : ''}
          </div>
          ${article.image ? `<img src="${article.image}" alt="${article.title}" class="news-image">` : ''}
          <div class="news-content">
            ${article.content}
          </div>
        </div>
      `).join('<hr>')
      
      newsPage.innerHTML = newsHTML
    }
  }
  
  updateSolutionDisplays() {
    // Update solution sections if they exist
    const solutionContainers = document.querySelectorAll('.solutions-grid, .solutions-showcase')
    
    solutionContainers.forEach(container => {
      if (this.solutions && this.solutions.length > 0) {
        // Create solution cards
        const solutionsHTML = this.solutions.map(solution => `
          <div class="solution-card" data-solution-id="${solution.id}">
            <div class="solution-image">
              <img src="${solution.image || 'assets/images/placeholder-solution.jpg'}" 
                   alt="${solution.title}" 
                   onerror="this.src='assets/images/placeholder-solution.jpg'">
            </div>
            <div class="solution-content">
              <h3>${solution.title}</h3>
              <p class="solution-category">${solution.category || ''}</p>
              <p class="solution-description">${this.truncateText(solution.description, 150)}</p>
              <a href="solutions.html#solution-${solution.id}" class="btn btn-outline-primary btn-sm">Learn More</a>
            </div>
          </div>
        `).join('')
        
        container.innerHTML = solutionsHTML
      }
    })
    
    // Update solutions page if it exists
    const solutionsPage = document.querySelector('.solutions-page-content')
    if (solutionsPage && this.solutions && this.solutions.length > 0) {
      const solutionsHTML = this.solutions.map(solution => `
        <div class="solution-item" id="solution-${solution.id}">
          <div class="row align-items-center">
            <div class="col-lg-5">
              <img src="${solution.image || 'assets/images/placeholder-solution.jpg'}" 
                   alt="${solution.title}" class="img-fluid rounded shadow">
            </div>
            <div class="col-lg-7">
              <h2>${solution.title}</h2>
              <p class="solution-category badge bg-primary">${solution.category || 'General'}</p>
              <div class="solution-description">
                ${solution.description || ''}
              </div>
              <div class="solution-features mt-4">
                <h5>Key Features:</h5>
                ${solution.features ? this.formatFeatures(solution.features) : ''}
              </div>
              <div class="solution-applications mt-4">
                <h5>Applications:</h5>
                ${solution.applications ? this.formatApplications(solution.applications) : ''}
              </div>
            </div>
          </div>
        </div>
      `).join('<hr class="my-5">')
      
      solutionsPage.innerHTML = solutionsHTML
    }
  }
  
  updateCaseDisplays() {
    // Update case sections if they exist
    const caseContainers = document.querySelectorAll('.cases-grid, .cases-showcase')
    
    caseContainers.forEach(container => {
      if (this.cases && this.cases.length > 0) {
        // Create case cards
        const casesHTML = this.cases.map(caseItem => `
          <div class="case-card" data-case-id="${caseItem.id}">
            <div class="case-image">
              <img src="${this.getFirstImage(caseItem.images) || 'assets/images/placeholder-case.jpg'}" 
                   alt="${caseItem.title}" 
                   onerror="this.src='assets/images/placeholder-case.jpg'">
            </div>
            <div class="case-content">
              <h3>${caseItem.title}</h3>
              <p class="case-location">${caseItem.location || ''}</p>
              <p class="case-description">${this.truncateText(caseItem.description, 120)}</p>
              <a href="cases.html#case-${caseItem.id}" class="btn btn-outline-primary btn-sm">View Case Study</a>
            </div>
          </div>
        `).join('')
        
        container.innerHTML = casesHTML
      }
    })
    
    // Update cases page if it exists
    const casesPage = document.querySelector('.cases-page-content')
    if (casesPage && this.cases && this.cases.length > 0) {
      const casesHTML = this.cases.map(caseItem => `
        <div class="case-study" id="case-${caseItem.id}">
          <h2>${caseItem.title}</h2>
          <div class="case-meta">
            ${caseItem.location ? `<span class="location"><i class="fas fa-map-marker-alt"></i> ${caseItem.location}</span>` : ''}
            ${caseItem.client ? `<span class="client"><i class="fas fa-building"></i> ${caseItem.client}</span>` : ''}
            ${caseItem.project_date ? `<span class="date"><i class="fas fa-calendar"></i> ${caseItem.project_date}</span>` : ''}
          </div>
          <div class="case-description my-4">
            ${caseItem.description || ''}
          </div>
          ${this.formatCaseImages(caseItem.images)}
        </div>
      `).join('<hr class="my-5">')
      
      casesPage.innerHTML = casesHTML
    }
  }

  async updateStatistics() {
    try {
      // Get counts from database
      const [productsResult, inquiriesResult, newsResult, casesResult] = await Promise.all([
        supabase.from('products').select('*', { count: 'exact', head: true }),
        supabase.from('inquiries').select('*', { count: 'exact', head: true }),
        supabase.from('news').select('*', { count: 'exact', head: true }),
        supabase.from('cases').select('*', { count: 'exact', head: true })
      ])
      
      const stats = {
        products: productsResult.count || 0,
        inquiries: inquiriesResult.count || 0,
        news: newsResult.count || 0,
        cases: casesResult.count || 0,
        projects: 15000, // Default value
        countries: 120,  // Default value
        experience: 25,  // Default value
        engineers: 500   // Default value
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
      news: document.querySelectorAll('[data-stat="news"], .stat-news'),
      cases: document.querySelectorAll('[data-stat="cases"], .stat-cases'),
      projects: document.querySelectorAll('[data-stat="projects"], .stat-projects'),
      countries: document.querySelectorAll('[data-stat="countries"], .stat-countries'),
      experience: document.querySelectorAll('[data-stat="experience"], .stat-experience'),
      engineers: document.querySelectorAll('[data-stat="engineers"], .stat-engineers')
    }
    
    Object.keys(statElements).forEach(key => {
      statElements[key].forEach(element => {
        if (element) {
          element.textContent = stats[key]
          
          // If this is a counter element, set the data-count attribute
          if (element.classList.contains('stat-number')) {
            element.setAttribute('data-count', stats[key])
          }
        }
      })
    })
    
    // Initialize counters if they exist
    this.initCounters()
  }
  
  initCounters() {
    const counters = document.querySelectorAll('.stat-number[data-count]')
    
    counters.forEach(counter => {
      const target = parseInt(counter.getAttribute('data-count'))
      const duration = 2000 // 2 seconds
      const startTime = performance.now()
      const startValue = 0
      
      const updateCounter = (currentTime) => {
        const elapsedTime = currentTime - startTime
        
        if (elapsedTime < duration) {
          const progress = elapsedTime / duration
          const currentValue = Math.floor(startValue + progress * (target - startValue))
          counter.textContent = currentValue.toLocaleString()
          requestAnimationFrame(updateCounter)
        } else {
          counter.textContent = target.toLocaleString()
        }
      }
      
      requestAnimationFrame(updateCounter)
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
    
    // Subscribe to solutions changes
    supabase
      .channel('solutions-changes')
      .on('postgres_changes', 
          { event: '*', schema: 'public', table: 'solutions' }, 
          (payload) => {
            console.log('Solutions updated:', payload)
            this.loadSolutions()
          }
      )
      .subscribe()
    
    // Subscribe to cases changes
    supabase
      .channel('cases-changes')
      .on('postgres_changes', 
          { event: '*', schema: 'public', table: 'cases' }, 
          (payload) => {
            console.log('Cases updated:', payload)
            this.loadCases()
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
    
    // Update user info displays
    const userNameElements = document.querySelectorAll('.user-name')
    userNameElements.forEach(el => {
      el.textContent = user.email
    })
  }

  handleUserSignOut() {
    console.log('User signed out')
    
    // Update UI for guest user
    const authElements = document.querySelectorAll('.auth-required')
    authElements.forEach(el => el.style.display = 'none')
    
    const guestElements = document.querySelectorAll('.guest-only')
    guestElements.forEach(el => el.style.display = 'block')
  }
  
  initContactForms() {
    // Contact forms are handled by contact-form-supabase.js
    // This is just a wrapper to ensure it's initialized
    if (window.contactFormHandler) {
      console.log('✅ Contact form handler already initialized')
    } else {
      console.log('⚠️ Contact form handler not found, initializing manually')
      import('./contact-form-supabase.js').then(module => {
        console.log('✅ Contact form handler initialized')
      }).catch(error => {
        console.error('❌ Failed to initialize contact form handler:', error)
      })
    }
  }

  // Utility methods
  truncateText(text, maxLength) {
    if (!text) return ''
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength).trim() + '...'
  }
  
  getFirstImage(imagesString) {
    if (!imagesString) return null
    
    try {
      // Try parsing as JSON
      const images = JSON.parse(imagesString)
      if (Array.isArray(images) && images.length > 0) {
        return images[0]
      }
      return null
    } catch (e) {
      // If not JSON, try splitting by comma
      const images = imagesString.split(',')
      return images[0] ? images[0].trim() : null
    }
  }
  
  formatFeatures(featuresString) {
    if (!featuresString) return ''
    
    try {
      // Try parsing as JSON
      const features = JSON.parse(featuresString)
      if (Array.isArray(features)) {
        return `
          <ul class="feature-list">
            ${features.map(feature => `<li>${feature}</li>`).join('')}
          </ul>
        `
      }
    } catch (e) {
      // If not JSON, try splitting by newlines or commas
      const features = featuresString.includes('\n') 
        ? featuresString.split('\n') 
        : featuresString.split(',')
      
      return `
        <ul class="feature-list">
          ${features.map(feature => `<li>${feature.trim()}</li>`).join('')}
        </ul>
      `
    }
  }
  
  formatApplications(applicationsString) {
    if (!applicationsString) return ''
    
    try {
      // Try parsing as JSON
      const applications = JSON.parse(applicationsString)
      if (Array.isArray(applications)) {
        return `
          <div class="application-badges">
            ${applications.map(app => `<span class="badge bg-secondary me-2 mb-2">${app}</span>`).join('')}
          </div>
        `
      }
    } catch (e) {
      // If not JSON, try splitting by newlines or commas
      const applications = applicationsString.includes('\n') 
        ? applicationsString.split('\n') 
        : applicationsString.split(',')
      
      return `
        <div class="application-badges">
          ${applications.map(app => `<span class="badge bg-secondary me-2 mb-2">${app.trim()}</span>`).join('')}
        </div>
      `
    }
  }
  
  formatCaseImages(imagesString) {
    if (!imagesString) return ''
    
    try {
      // Try parsing as JSON
      const images = JSON.parse(imagesString)
      if (Array.isArray(images) && images.length > 0) {
        return `
          <div class="case-images mt-4">
            <div class="row">
              ${images.map(img => `
                <div class="col-md-4 mb-4">
                  <a href="${img}" class="case-image-link" data-lightbox="case-gallery">
                    <img src="${img}" alt="Case Study Image" class="img-fluid rounded shadow">
                  </a>
                </div>
              `).join('')}
            </div>
          </div>
        `
      }
    } catch (e) {
      // If not JSON, try splitting by comma
      const images = imagesString.split(',')
      if (images.length > 0) {
        return `
          <div class="case-images mt-4">
            <div class="row">
              ${images.map(img => `
                <div class="col-md-4 mb-4">
                  <a href="${img.trim()}" class="case-image-link" data-lightbox="case-gallery">
                    <img src="${img.trim()}" alt="Case Study Image" class="img-fluid rounded shadow">
                  </a>
                </div>
              `).join('')}
            </div>
          </div>
        `
      }
    }
    
    return ''
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
  
  async getSolutions(category = null) {
    try {
      let query = supabase
        .from('solutions')
        .select('*')
        .eq('status', 'active')
      
      if (category) {
        query = query.eq('category', category)
      }
      
      const { data, error } = await query.order('created_at', { ascending: false })
      
      if (error) throw error
      return data
    } catch (error) {
      console.error('Error getting solutions:', error)
      return []
    }
  }
  
  async getCases(category = null) {
    try {
      let query = supabase
        .from('cases')
        .select('*')
        .eq('status', 'published')
      
      if (category) {
        query = query.eq('category', category)
      }
      
      const { data, error } = await query.order('created_at', { ascending: false })
      
      if (error) throw error
      return data
    } catch (error) {
      console.error('Error getting cases:', error)
      return []
    }
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