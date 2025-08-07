/**
 * Supabase Authentication Component
 * Handles user authentication and session management
 */

class SupabaseAuth {
  constructor() {
    this.supabase = window.SupabaseFrontend?.client
    this.currentUser = null
    this.currentSession = null
    this.authCallbacks = []
    
    // Initialize auth state
    this.init()
  }

  async init() {
    if (!this.supabase) {
      console.warn('Supabase not available for authentication')
      return
    }

    // Get initial session
    try {
      const { data: { session }, error } = await this.supabase.auth.getSession()
      if (error) throw error
      
      this.currentSession = session
      this.currentUser = session?.user || null
      
      // Set up auth state listener
      this.supabase.auth.onAuthStateChange((event, session) => {
        console.log('Auth state changed:', event, session)
        
        this.currentSession = session
        this.currentUser = session?.user || null
        
        // Notify callbacks
        this.authCallbacks.forEach(callback => {
          try {
            callback(event, session, this.currentUser)
          } catch (error) {
            console.error('Auth callback error:', error)
          }
        })
        
        // Handle specific events
        this.handleAuthEvent(event, session)
      })
      
    } catch (error) {
      console.error('Auth initialization error:', error)
    }
  }

  // Handle auth events
  handleAuthEvent(event, session) {
    switch (event) {
      case 'SIGNED_IN':
        this.onSignedIn(session)
        break
      case 'SIGNED_OUT':
        this.onSignedOut()
        break
      case 'TOKEN_REFRESHED':
        console.log('Token refreshed')
        break
      case 'USER_UPDATED':
        console.log('User updated')
        break
    }
  }

  onSignedIn(session) {
    console.log('User signed in:', session.user.email)
    
    // Store user info in localStorage for fallback
    localStorage.setItem('auth_user', JSON.stringify({
      id: session.user.id,
      email: session.user.email,
      role: session.user.user_metadata?.role || 'user'
    }))
    
    // Redirect to admin dashboard if on login page
    if (window.location.pathname.includes('admin') && 
        window.location.pathname.includes('login')) {
      window.location.href = '/admin/dashboard'
    }
  }

  onSignedOut() {
    console.log('User signed out')
    
    // Clear localStorage
    localStorage.removeItem('auth_user')
    localStorage.removeItem('auth_session')
    
    // Redirect to login if on admin pages
    if (window.location.pathname.includes('admin') && 
        !window.location.pathname.includes('login')) {
      window.location.href = '/admin/login'
    }
  }

  // Authentication methods
  async signIn(email, password) {
    if (!this.supabase) {
      return this.fallbackSignIn(email, password)
    }

    try {
      const { data, error } = await this.supabase.auth.signInWithPassword({
        email,
        password
      })
      
      if (error) throw error
      
      return {
        success: true,
        user: data.user,
        session: data.session
      }
    } catch (error) {
      console.error('Sign in error:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  async signUp(email, password, metadata = {}) {
    if (!this.supabase) {
      return { success: false, error: 'Supabase not available' }
    }

    try {
      const { data, error } = await this.supabase.auth.signUp({
        email,
        password,
        options: {
          data: metadata
        }
      })
      
      if (error) throw error
      
      return {
        success: true,
        user: data.user,
        session: data.session
      }
    } catch (error) {
      console.error('Sign up error:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  async signOut() {
    if (!this.supabase) {
      return this.fallbackSignOut()
    }

    try {
      const { error } = await this.supabase.auth.signOut()
      if (error) throw error
      
      return { success: true }
    } catch (error) {
      console.error('Sign out error:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  async resetPassword(email) {
    if (!this.supabase) {
      return { success: false, error: 'Supabase not available' }
    }

    try {
      const { error } = await this.supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/admin/reset-password`
      })
      
      if (error) throw error
      
      return { success: true }
    } catch (error) {
      console.error('Reset password error:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  async updatePassword(newPassword) {
    if (!this.supabase) {
      return { success: false, error: 'Supabase not available' }
    }

    try {
      const { error } = await this.supabase.auth.updateUser({
        password: newPassword
      })
      
      if (error) throw error
      
      return { success: true }
    } catch (error) {
      console.error('Update password error:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  // Utility methods
  isAuthenticated() {
    return !!this.currentUser || !!localStorage.getItem('auth_user')
  }

  getCurrentUser() {
    if (this.currentUser) {
      return this.currentUser
    }
    
    // Fallback to localStorage
    const storedUser = localStorage.getItem('auth_user')
    return storedUser ? JSON.parse(storedUser) : null
  }

  getCurrentSession() {
    return this.currentSession
  }

  getUserRole() {
    const user = this.getCurrentUser()
    return user?.user_metadata?.role || user?.role || 'user'
  }

  isAdmin() {
    return this.getUserRole() === 'admin'
  }

  // Auth state listeners
  onAuthStateChange(callback) {
    this.authCallbacks.push(callback)
    
    // Return unsubscribe function
    return () => {
      const index = this.authCallbacks.indexOf(callback)
      if (index > -1) {
        this.authCallbacks.splice(index, 1)
      }
    }
  }

  // Fallback methods for when Supabase is not available
  async fallbackSignIn(email, password) {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      })
      
      const result = await response.json()
      
      if (result.success) {
        localStorage.setItem('auth_user', JSON.stringify(result.user))
        this.currentUser = result.user
        return result
      } else {
        return { success: false, error: result.error }
      }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  async fallbackSignOut() {
    try {
      await fetch('/api/auth/logout', { method: 'POST' })
      localStorage.removeItem('auth_user')
      this.currentUser = null
      return { success: true }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  // Route protection
  requireAuth() {
    if (!this.isAuthenticated()) {
      window.location.href = '/admin/login'
      return false
    }
    return true
  }

  requireAdmin() {
    if (!this.isAuthenticated() || !this.isAdmin()) {
      window.location.href = '/admin/login'
      return false
    }
    return true
  }
}

// Create global auth instance
window.SupabaseAuth = new SupabaseAuth()

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SupabaseAuth
}

// Auto-initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  console.log('Supabase Auth initialized')
  
  // Add auth status to console
  setTimeout(() => {
    const isAuth = window.SupabaseAuth.isAuthenticated()
    const user = window.SupabaseAuth.getCurrentUser()
    
    console.log('Auth Status:', {
      authenticated: isAuth,
      user: user?.email || 'Not logged in',
      role: window.SupabaseAuth.getUserRole()
    })
  }, 1000)
})