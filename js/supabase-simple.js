// 简化的浏览器 Supabase 客户端
// 专门为浏览器环境设计，避免 Node.js 依赖问题

// 直接配置 Supabase（公开的 anon key 可以安全地放在前端代码中）
const supabaseUrl = 'https://jirudzbqcxviytcmxegf.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y218ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4'

// 创建 Supabase 客户端
let supabaseClient = null

// 初始化函数
function initSupabase() {
  try {
    if (typeof window.supabase !== 'undefined') {
      supabaseClient = window.supabase.createClient(supabaseUrl, supabaseKey)
      console.log('✅ Supabase 客户端初始化成功')
      return true
    } else {
      console.error('❌ Supabase 库未加载')
      return false
    }
  } catch (error) {
    console.error('❌ Supabase 初始化失败:', error)
    return false
  }
}

// 数据库操作函数
const db = {
  // 产品操作
  async getProducts() {
    try {
      const { data, error } = await supabaseClient
        .from('products')
        .select('*')
        .order('created_at', { ascending: false })
      
      if (error) throw error
      return data
    } catch (error) {
      console.error('获取产品失败:', error)
      return []
    }
  },

  // 新闻操作
  async getNews() {
    try {
      const { data, error } = await supabaseClient
        .from('news')
        .select('*')
        .eq('status', 'published')
        .order('created_at', { ascending: false })
      
      if (error) throw error
      return data
    } catch (error) {
      console.error('获取新闻失败:', error)
      return []
    }
  },

  // 提交询价
  async submitInquiry(inquiryData) {
    try {
      const { data, error } = await supabaseClient
        .from('inquiries')
        .insert([{
          ...inquiryData,
          status: 'new',
          created_at: new Date().toISOString()
        }])
        .select()
      
      if (error) throw error
      console.log('✅ 询价提交成功:', data)
      return { success: true, data: data[0] }
    } catch (error) {
      console.error('❌ 询价提交失败:', error)
      return { success: false, error: error.message }
    }
  },

  // 用户认证
  async authenticateUser(username, password) {
    try {
      const { data, error } = await supabaseClient
        .from('users')
        .select('*')
        .eq('username', username)
        .eq('password', password)
        .single()
      
      if (error) throw error
      return { success: true, user: data }
    } catch (error) {
      console.error('用户认证失败:', error)
      return { success: false, error: error.message }
    }
  }
}

// 认证操作
const auth = {
  // 用户注册
  async signUp(email, password, userData = {}) {
    try {
      const { data, error } = await supabaseClient.auth.signUp({
        email,
        password,
        options: {
          data: userData
        }
      })
      
      if (error) throw error
      return { success: true, data }
    } catch (error) {
      console.error('注册失败:', error)
      return { success: false, error: error.message }
    }
  },

  // 用户登录
  async signIn(email, password) {
    try {
      const { data, error } = await supabaseClient.auth.signInWithPassword({
        email,
        password
      })
      
      if (error) throw error
      return { success: true, data }
    } catch (error) {
      console.error('登录失败:', error)
      return { success: false, error: error.message }
    }
  },

  // 用户登出
  async signOut() {
    try {
      const { error } = await supabaseClient.auth.signOut()
      if (error) throw error
      return { success: true }
    } catch (error) {
      console.error('登出失败:', error)
      return { success: false, error: error.message }
    }
  },

  // 获取当前用户
  async getCurrentUser() {
    try {
      const { data: { user } } = await supabaseClient.auth.getUser()
      return user
    } catch (error) {
      console.error('获取用户信息失败:', error)
      return null
    }
  },

  // 监听认证状态变化
  onAuthStateChange(callback) {
    return supabaseClient.auth.onAuthStateChange(callback)
  }
}

// 连接测试
async function testConnection() {
  try {
    if (!supabaseClient) {
      throw new Error('Supabase 客户端未初始化')
    }

    const { data, error } = await supabaseClient
      .from('products')
      .select('count')
      .limit(1)
    
    if (error) throw error
    
    console.log('✅ Supabase 连接测试成功')
    return { success: true, message: '连接成功' }
  } catch (error) {
    console.error('❌ Supabase 连接测试失败:', error)
    return { success: false, error: error.message }
  }
}

// 显示连接状态
function showConnectionStatus(connected) {
  const indicator = document.createElement('div')
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
    ${connected ? 'background: #10b981;' : 'background: #ef4444;'}
  `
  
  indicator.textContent = connected ? '🟢 后端已连接' : '🔴 后端离线'
  document.body.appendChild(indicator)
  
  // 3秒后自动隐藏
  setTimeout(() => {
    if (indicator.parentNode) {
      indicator.parentNode.removeChild(indicator)
    }
  }, 3000)
}

// 页面加载时自动初始化
document.addEventListener('DOMContentLoaded', async function() {
  console.log('🚀 开始初始化 Supabase...')
  
  // 等待 Supabase 库加载
  let attempts = 0
  const maxAttempts = 10
  
  const waitForSupabase = () => {
    return new Promise((resolve) => {
      const checkSupabase = () => {
        if (typeof window.supabase !== 'undefined') {
          resolve(true)
        } else if (attempts < maxAttempts) {
          attempts++
          setTimeout(checkSupabase, 500)
        } else {
          resolve(false)
        }
      }
      checkSupabase()
    })
  }
  
  const supabaseLoaded = await waitForSupabase()
  
  if (supabaseLoaded) {
    const initialized = initSupabase()
    if (initialized) {
      // 测试连接
      const connectionResult = await testConnection()
      showConnectionStatus(connectionResult.success)
      
      if (connectionResult.success) {
        console.log('🎉 Supabase 集成完成！')
        
        // 绑定联系表单
        bindContactForms()
        
        // 加载动态内容
        loadDynamicContent()
      }
    }
  } else {
    console.warn('⚠️ Supabase 库加载失败，使用离线模式')
    showConnectionStatus(false)
  }
})

// 绑定联系表单
function bindContactForms() {
  const forms = document.querySelectorAll('form')
  
  forms.forEach(form => {
    const hasContactFields = form.querySelector('input[name="email"], input[name="name"], textarea[name="message"]')
    
    if (hasContactFields) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault()
        
        const formData = new FormData(form)
        const inquiryData = {
          name: formData.get('name') || formData.get('fullname'),
          email: formData.get('email'),
          phone: formData.get('phone'),
          company: formData.get('company'),
          message: formData.get('message') || formData.get('inquiry')
        }
        
        // 验证必填字段
        if (!inquiryData.name || !inquiryData.email || !inquiryData.message) {
          alert('请填写所有必填字段')
          return
        }
        
        // 提交到数据库
        const result = await db.submitInquiry(inquiryData)
        
        if (result.success) {
          alert('感谢您的询价！我们会尽快回复您。')
          form.reset()
        } else {
          alert('提交失败，请稍后重试。')
        }
      })
    }
  })
}

// 加载动态内容
async function loadDynamicContent() {
  try {
    // 加载产品
    const products = await db.getProducts()
    if (products.length > 0) {
      console.log(`📦 加载了 ${products.length} 个产品`)
    }
    
    // 加载新闻
    const news = await db.getNews()
    if (news.length > 0) {
      console.log(`📰 加载了 ${news.length} 条新闻`)
    }
    
  } catch (error) {
    console.error('加载动态内容失败:', error)
  }
}

// 导出给全局使用
window.SupabaseSimple = {
  client: () => supabaseClient,
  db,
  auth,
  testConnection,
  initSupabase
}

console.log('📚 Supabase 简化客户端已加载')