// Authentication System for LED Display Website
// Handles user authentication with Supabase Auth

import { supabase, auth } from '../lib/supabase-client.js'

class AuthSystem {
  constructor() {
    this.currentUser = null
    this.isAuthenticated = false
    this.init()
  }

  async init() {
    // Check for existing session
    const session = await auth.getSession()
    if (session?.user) {
      this.currentUser = session.user
      this.isAuthenticated = true
      this.updateUI()
    }

    // Listen for auth state changes
    auth.onAuthStateChange((event, session) => {
      console.log('Auth state changed:', event, session)
      
      if (event === 'SIGNED_IN') {
        this.currentUser = session.user
        this.isAuthenticated = true
        this.updateUI()
        this.showMessage('Successfully signed in!', 'success')
      } else if (event === 'SIGNED_OUT') {
        this.currentUser = null
        this.isAuthenticated = false
        this.updateUI()
        this.showMessage('Successfully signed out!', 'info')
      } else if (event === 'PASSWORD_RECOVERY') {
        this.showPasswordResetForm()
      }
    })
  }

  // Sign up new user
  async signUp(email, password, userData = {}) {
    try {
      const result = await auth.signUp(email, password, userData)
      
      if (result.user && !result.user.email_confirmed_at) {
        this.showMessage('Please check your email to confirm your account!', 'info')
      }
      
      return result
    } catch (error) {
      this.showMessage(error.message, 'error')
      throw error
    }
  }

  // Sign in existing user
  async signIn(email, password) {
    try {
      const result = await auth.signIn(email, password)
      return result
    } catch (error) {
      this.showMessage(error.message, 'error')
      throw error
    }
  }

  // Sign out user
  async signOut() {
    try {
      await auth.signOut()
    } catch (error) {
      this.showMessage(error.message, 'error')
      throw error
    }
  }

  // Reset password
  async resetPassword(email) {
    try {
      await auth.resetPassword(email)
      this.showMessage('Password reset email sent! Check your inbox.', 'success')
    } catch (error) {
      this.showMessage(error.message, 'error')
      throw error
    }
  }

  // Update user profile
  async updateProfile(updates) {
    try {
      const result = await auth.updateUser(updates)
      this.showMessage('Profile updated successfully!', 'success')
      return result
    } catch (error) {
      this.showMessage(error.message, 'error')
      throw error
    }
  }

  // Update UI based on auth state
  updateUI() {
    const authButtons = document.querySelector('.auth-buttons')
    const userProfile = document.querySelector('.user-profile')
    const adminLinks = document.querySelectorAll('.admin-only')

    if (this.isAuthenticated) {
      // Show user profile, hide auth buttons
      if (authButtons) authButtons.style.display = 'none'
      if (userProfile) {
        userProfile.style.display = 'block'
        userProfile.querySelector('.user-email').textContent = this.currentUser.email
      }
      
      // Show admin links if user has admin role
      adminLinks.forEach(link => {
        link.style.display = this.hasRole('admin') ? 'block' : 'none'
      })
    } else {
      // Show auth buttons, hide user profile
      if (authButtons) authButtons.style.display = 'block'
      if (userProfile) userProfile.style.display = 'none'
      
      // Hide admin links
      adminLinks.forEach(link => {
        link.style.display = 'none'
      })
    }
  }

  // Check if user has specific role
  hasRole(role) {
    return this.currentUser?.user_metadata?.role === role
  }

  // Show message to user
  showMessage(message, type = 'info') {
    // Create message element
    const messageEl = document.createElement('div')
    messageEl.className = `auth-message auth-message-${type}`
    messageEl.textContent = message
    
    // Style the message
    messageEl.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 12px 20px;
      border-radius: 6px;
      color: white;
      font-weight: 500;
      z-index: 10000;
      max-width: 300px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      ${type === 'success' ? 'background: #10b981;' : ''}
      ${type === 'error' ? 'background: #ef4444;' : ''}
      ${type === 'info' ? 'background: #3b82f6;' : ''}
    `
    
    // Add to page
    document.body.appendChild(messageEl)
    
    // Remove after 5 seconds
    setTimeout(() => {
      if (messageEl.parentNode) {
        messageEl.parentNode.removeChild(messageEl)
      }
    }, 5000)
  }

  // Show password reset form
  showPasswordResetForm() {
    const modal = document.createElement('div')
    modal.innerHTML = `
      <div class="auth-modal-overlay" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 10000; display: flex; align-items: center; justify-content: center;">
        <div class="auth-modal" style="background: white; padding: 30px; border-radius: 8px; max-width: 400px; width: 90%;">
          <h3>Reset Your Password</h3>
          <form id="password-reset-form">
            <div style="margin-bottom: 15px;">
              <label for="new-password">New Password:</label>
              <input type="password" id="new-password" required style="width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            <div style="margin-bottom: 15px;">
              <label for="confirm-password">Confirm Password:</label>
              <input type="password" id="confirm-password" required style="width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            <div style="display: flex; gap: 10px; justify-content: flex-end;">
              <button type="button" class="cancel-btn" style="padding: 8px 16px; border: 1px solid #ddd; background: white; border-radius: 4px; cursor: pointer;">Cancel</button>
              <button type="submit" style="padding: 8px 16px; background: #3b82f6; color: white; border: none; border-radius: 4px; cursor: pointer;">Update Password</button>
            </div>
          </form>
        </div>
      </div>
    `
    
    document.body.appendChild(modal)
    
    // Handle form submission
    modal.querySelector('#password-reset-form').addEventListener('submit', async (e) => {
      e.preventDefault()
      
      const newPassword = modal.querySelector('#new-password').value
      const confirmPassword = modal.querySelector('#confirm-password').value
      
      if (newPassword !== confirmPassword) {
        this.showMessage('Passwords do not match!', 'error')
        return
      }
      
      try {
        await this.updateProfile({ password: newPassword })
        document.body.removeChild(modal)
      } catch (error) {
        console.error('Password update failed:', error)
      }
    })
    
    // Handle cancel
    modal.querySelector('.cancel-btn').addEventListener('click', () => {
      document.body.removeChild(modal)
    })
    
    // Handle overlay click
    modal.querySelector('.auth-modal-overlay').addEventListener('click', (e) => {
      if (e.target === modal.querySelector('.auth-modal-overlay')) {
        document.body.removeChild(modal)
      }
    })
  }

  // Create auth forms
  createAuthForms() {
    return `
      <div class="auth-container" style="max-width: 400px; margin: 0 auto; padding: 20px;">
        <!-- Sign In Form -->
        <div id="signin-form" class="auth-form">
          <h3>Sign In</h3>
          <form>
            <div class="form-group">
              <label for="signin-email">Email:</label>
              <input type="email" id="signin-email" required>
            </div>
            <div class="form-group">
              <label for="signin-password">Password:</label>
              <input type="password" id="signin-password" required>
            </div>
            <button type="submit" class="auth-btn">Sign In</button>
            <p><a href="#" id="show-signup">Don't have an account? Sign up</a></p>
            <p><a href="#" id="forgot-password">Forgot password?</a></p>
          </form>
        </div>

        <!-- Sign Up Form -->
        <div id="signup-form" class="auth-form" style="display: none;">
          <h3>Sign Up</h3>
          <form>
            <div class="form-group">
              <label for="signup-email">Email:</label>
              <input type="email" id="signup-email" required>
            </div>
            <div class="form-group">
              <label for="signup-password">Password:</label>
              <input type="password" id="signup-password" required>
            </div>
            <div class="form-group">
              <label for="signup-name">Full Name:</label>
              <input type="text" id="signup-name" required>
            </div>
            <button type="submit" class="auth-btn">Sign Up</button>
            <p><a href="#" id="show-signin">Already have an account? Sign in</a></p>
          </form>
        </div>
      </div>
    `
  }
}

// Initialize auth system when DOM is loaded
let authSystem = null

document.addEventListener('DOMContentLoaded', () => {
  authSystem = new AuthSystem()
  
  // Add auth forms to page if auth container exists
  const authContainer = document.querySelector('#auth-container')
  if (authContainer) {
    authContainer.innerHTML = authSystem.createAuthForms()
    
    // Bind form events
    bindAuthFormEvents()
  }
})

// Bind auth form events
function bindAuthFormEvents() {
  const signinForm = document.querySelector('#signin-form form')
  const signupForm = document.querySelector('#signup-form form')
  
  // Sign in form
  if (signinForm) {
    signinForm.addEventListener('submit', async (e) => {
      e.preventDefault()
      const email = document.querySelector('#signin-email').value
      const password = document.querySelector('#signin-password').value
      
      try {
        await authSystem.signIn(email, password)
      } catch (error) {
        console.error('Sign in failed:', error)
      }
    })
  }
  
  // Sign up form
  if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
      e.preventDefault()
      const email = document.querySelector('#signup-email').value
      const password = document.querySelector('#signup-password').value
      const name = document.querySelector('#signup-name').value
      
      try {
        await authSystem.signUp(email, password, { full_name: name })
      } catch (error) {
        console.error('Sign up failed:', error)
      }
    })
  }
  
  // Form toggle links
  document.querySelector('#show-signup')?.addEventListener('click', (e) => {
    e.preventDefault()
    document.querySelector('#signin-form').style.display = 'none'
    document.querySelector('#signup-form').style.display = 'block'
  })
  
  document.querySelector('#show-signin')?.addEventListener('click', (e) => {
    e.preventDefault()
    document.querySelector('#signup-form').style.display = 'none'
    document.querySelector('#signin-form').style.display = 'block'
  })
  
  // Forgot password
  document.querySelector('#forgot-password')?.addEventListener('click', async (e) => {
    e.preventDefault()
    const email = document.querySelector('#signin-email').value
    
    if (!email) {
      authSystem.showMessage('Please enter your email first', 'error')
      return
    }
    
    try {
      await authSystem.resetPassword(email)
    } catch (error) {
      console.error('Password reset failed:', error)
    }
  })
}

// Export auth system
export default AuthSystem
export { authSystem }