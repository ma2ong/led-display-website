// Contact Form Integration with Supabase
// Handles contact form submissions to Supabase database

import { db } from '../lib/supabase-client.js'

class ContactFormHandler {
  constructor() {
    this.init()
  }

  init() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.bindEvents())
    } else {
      this.bindEvents()
    }
  }

  bindEvents() {
    // Find all contact forms
    const contactForms = document.querySelectorAll('form[data-contact-form], .contact-form form, #contact-form')
    
    contactForms.forEach(form => {
      form.addEventListener('submit', (e) => this.handleSubmit(e))
    })

    // Also bind to any form with contact-related fields
    const forms = document.querySelectorAll('form')
    forms.forEach(form => {
      const hasContactFields = form.querySelector('input[name="email"], input[name="name"], textarea[name="message"]')
      if (hasContactFields && !form.dataset.bound) {
        form.dataset.bound = 'true'
        form.addEventListener('submit', (e) => this.handleSubmit(e))
      }
    })
  }

  async handleSubmit(event) {
    event.preventDefault()
    
    const form = event.target
    const submitButton = form.querySelector('button[type="submit"], input[type="submit"]')
    const originalText = submitButton ? submitButton.textContent || submitButton.value : ''
    
    try {
      // Show loading state
      if (submitButton) {
        submitButton.disabled = true
        submitButton.textContent = 'Sending...'
        submitButton.style.opacity = '0.7'
      }

      // Extract form data
      const formData = new FormData(form)
      const contactData = this.extractContactData(formData)

      // Validate required fields
      if (!this.validateContactData(contactData)) {
        throw new Error('Please fill in all required fields')
      }

      // Submit to Supabase
      const result = await db.inquiries.create(contactData)
      
      console.log('✅ Contact form submitted successfully:', result)
      
      // Show success message
      this.showMessage('Thank you! Your message has been sent successfully.', 'success')
      
      // Reset form
      form.reset()
      
      // Optional: Redirect or show confirmation
      this.handleSuccess(result)

    } catch (error) {
      console.error('❌ Contact form submission failed:', error)
      this.showMessage(error.message || 'Failed to send message. Please try again.', 'error')
    } finally {
      // Restore button state
      if (submitButton) {
        submitButton.disabled = false
        submitButton.textContent = originalText
        submitButton.style.opacity = '1'
      }
    }
  }

  extractContactData(formData) {
    // Extract data from form, handling various field name variations
    const data = {
      name: this.getFieldValue(formData, ['name', 'fullname', 'full_name', 'contact_name']),
      email: this.getFieldValue(formData, ['email', 'email_address', 'contact_email']),
      phone: this.getFieldValue(formData, ['phone', 'telephone', 'mobile', 'contact_phone']),
      company: this.getFieldValue(formData, ['company', 'organization', 'business']),
      message: this.getFieldValue(formData, ['message', 'inquiry', 'comments', 'details']),
      subject: this.getFieldValue(formData, ['subject', 'topic', 'regarding'])
    }

    // Combine subject and message if both exist
    if (data.subject && data.message) {
      data.message = `Subject: ${data.subject}\n\n${data.message}`
    } else if (data.subject && !data.message) {
      data.message = data.subject
    }

    // Remove empty fields
    Object.keys(data).forEach(key => {
      if (!data[key] || data[key].trim() === '') {
        delete data[key]
      }
    })

    return data
  }

  getFieldValue(formData, fieldNames) {
    for (const name of fieldNames) {
      const value = formData.get(name)
      if (value && value.trim()) {
        return value.trim()
      }
    }
    return null
  }

  validateContactData(data) {
    // Check required fields
    if (!data.name || !data.email || !data.message) {
      return false
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(data.email)) {
      throw new Error('Please enter a valid email address')
    }

    return true
  }

  showMessage(message, type = 'info') {
    // Remove any existing messages
    const existingMessages = document.querySelectorAll('.contact-form-message')
    existingMessages.forEach(msg => msg.remove())

    // Create message element
    const messageEl = document.createElement('div')
    messageEl.className = `contact-form-message contact-form-message-${type}`
    messageEl.textContent = message
    
    // Style the message
    const styles = {
      position: 'fixed',
      top: '20px',
      right: '20px',
      padding: '15px 20px',
      borderRadius: '6px',
      color: 'white',
      fontWeight: '500',
      zIndex: '10000',
      maxWidth: '400px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
      fontSize: '14px',
      lineHeight: '1.4'
    }

    // Type-specific styles
    if (type === 'success') {
      styles.background = '#10b981'
      styles.border = '1px solid #059669'
    } else if (type === 'error') {
      styles.background = '#ef4444'
      styles.border = '1px solid #dc2626'
    } else {
      styles.background = '#3b82f6'
      styles.border = '1px solid #2563eb'
    }

    // Apply styles
    Object.assign(messageEl.style, styles)
    
    // Add to page
    document.body.appendChild(messageEl)
    
    // Animate in
    messageEl.style.transform = 'translateX(100%)'
    messageEl.style.transition = 'transform 0.3s ease-out'
    
    setTimeout(() => {
      messageEl.style.transform = 'translateX(0)'
    }, 10)
    
    // Remove after 5 seconds
    setTimeout(() => {
      if (messageEl.parentNode) {
        messageEl.style.transform = 'translateX(100%)'
        setTimeout(() => {
          if (messageEl.parentNode) {
            messageEl.parentNode.removeChild(messageEl)
          }
        }, 300)
      }
    }, 5000)

    // Allow manual dismissal
    messageEl.addEventListener('click', () => {
      if (messageEl.parentNode) {
        messageEl.style.transform = 'translateX(100%)'
        setTimeout(() => {
          if (messageEl.parentNode) {
            messageEl.parentNode.removeChild(messageEl)
          }
        }, 300)
      }
    })
  }

  handleSuccess(result) {
    // Optional: Add custom success handling
    // Could redirect to thank you page, show modal, etc.
    
    // Example: Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' })
    
    // Example: Track analytics
    if (typeof gtag !== 'undefined') {
      gtag('event', 'contact_form_submit', {
        event_category: 'engagement',
        event_label: 'contact_form'
      })
    }
  }

  // Method to manually submit contact data (for API use)
  async submitContact(contactData) {
    try {
      if (!this.validateContactData(contactData)) {
        throw new Error('Invalid contact data')
      }

      const result = await db.inquiries.create(contactData)
      return { success: true, data: result }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }
}

// Initialize contact form handler
const contactFormHandler = new ContactFormHandler()

// Export for external use
window.ContactFormHandler = ContactFormHandler
window.contactFormHandler = contactFormHandler

export default ContactFormHandler
export { contactFormHandler }