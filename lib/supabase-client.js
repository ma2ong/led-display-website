/**
 * 统一的 Supabase 客户端
 * 整合了所有 Supabase 相关功能
 */
import { createClient } from '@supabase/supabase-js'

// 从环境变量获取配置
const supabaseUrl = import.meta?.env?.VITE_SUPABASE_URL ||
                    process.env.VITE_SUPABASE_URL ||
                    process.env.SUPABASE_URL ||
                    'https://jirudzbqcxviytcmxegf.supabase.co'

const supabaseAnonKey = import.meta?.env?.VITE_SUPABASE_ANON_KEY ||
                        process.env.VITE_SUPABASE_ANON_KEY ||
                        process.env.SUPABASE_ANON_KEY ||
                        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y214ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4'

// 创建 Supabase 客户端
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true
  }
})

// ============================================
// 认证 API
// ============================================
export const auth = {
  /**
   * 用户登录
   */
  async login(email, password) {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })

    if (error) throw error

    // 记录登录日志
    await this.logLogin(data.user.id, email, 'success')

    return data
  },

  /**
   * 用户登出
   */
  async logout() {
    const { error } = await supabase.auth.signOut()
    if (error) throw error

    // 清除本地存储
    localStorage.removeItem('admin_user')
  },

  /**
   * 获取当前用户
   */
  async getCurrentUser() {
    const { data: { user }, error } = await supabase.auth.getUser()
    if (error) throw error
    return user
  },

  /**
   * 获取当前会话
   */
  async getSession() {
    const { data: { session }, error } = await supabase.auth.getSession()
    if (error) throw error
    return session
  },

  /**
   * 检查是否为管理员
   */
  async isAdmin() {
    try {
      const user = await this.getCurrentUser()
      if (!user) return false

      const { data, error } = await supabase
        .from('admin_users')
        .select('role, is_active')
        .eq('user_id', user.id)
        .single()

      if (error) {
        console.error('Error checking admin status:', error)
        return false
      }

      return data?.is_active && ['super_admin', 'admin', 'editor'].includes(data?.role)
    } catch (error) {
      console.error('Error in isAdmin:', error)
      return false
    }
  },

  /**
   * 获取管理员角色
   */
  async getAdminRole() {
    try {
      const user = await this.getCurrentUser()
      if (!user) return null

      const { data, error } = await supabase
        .from('admin_users')
        .select('role, is_active')
        .eq('user_id', user.id)
        .single()

      if (error) return null
      return data?.is_active ? data.role : null
    } catch (error) {
      console.error('Error getting admin role:', error)
      return null
    }
  },

  /**
   * 记录登录日志
   */
  async logLogin(userId, email, status = 'success', failureReason = null) {
    try {
      // 获取 IP 地址（通过第三方服务）
      let ipAddress = null
      try {
        const ipResponse = await fetch('https://api.ipify.org?format=json')
        const ipData = await ipResponse.json()
        ipAddress = ipData.ip
      } catch (e) {
        console.warn('Could not get IP address')
      }

      const { error } = await supabase.rpc('log_admin_login', {
        p_user_id: userId,
        p_email: email,
        p_ip_address: ipAddress,
        p_user_agent: navigator.userAgent,
        p_login_status: status,
        p_failure_reason: failureReason
      })

      if (error) console.error('Error logging login:', error)
    } catch (error) {
      console.error('Error in logLogin:', error)
    }
  },

  /**
   * 监听认证状态变化
   */
  onAuthStateChange(callback) {
    return supabase.auth.onAuthStateChange(callback)
  }
}

// ============================================
// 产品 API
// ============================================
export const productsAPI = {
  /**
   * 获取所有产品
   */
  async getAll() {
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .order('created_at', { ascending: false })

    if (error) throw error
    return data || []
  },

  /**
   * 根据 ID 获取产品
   */
  async getById(id) {
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .eq('id', id)
      .single()

    if (error) throw error
    return data
  },

  /**
   * 根据分类获取产品
   */
  async getByCategory(category) {
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .eq('category', category)
      .order('created_at', { ascending: false })

    if (error) throw error
    return data || []
  },

  /**
   * 获取特色产品
   */
  async getFeatured(limit = 6) {
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .eq('is_featured', true)
      .order('created_at', { ascending: false })
      .limit(limit)

    if (error) throw error
    return data || []
  },

  /**
   * 创建产品
   */
  async create(product) {
    const { data, error } = await supabase
      .from('products')
      .insert([product])
      .select()
      .single()

    if (error) throw error
    return data
  },

  /**
   * 更新产品
   */
  async update(id, updates) {
    const { data, error } = await supabase
      .from('products')
      .update(updates)
      .eq('id', id)
      .select()
      .single()

    if (error) throw error
    return data
  },

  /**
   * 删除产品
   */
  async delete(id) {
    const { error } = await supabase
      .from('products')
      .delete()
      .eq('id', id)

    if (error) throw error
    return true
  },

  /**
   * 搜索产品
   */
  async search(query) {
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .or(`name_en.ilike.%${query}%,name_zh.ilike.%${query}%,description_en.ilike.%${query}%,description_zh.ilike.%${query}%`)

    if (error) throw error
    return data || []
  }
}

// ============================================
// 内容管理 API
// ============================================
export const contentAPI = {
  /**
   * 获取页面内容
   */
  async getPageContent(pageName, language = 'en') {
    const { data, error } = await supabase
      .from('page_contents')
      .select('*')
      .eq('page_name', pageName)
      .eq('language', language)
      .eq('is_active', true)

    if (error) throw error
    return data || []
  },

  /**
   * 获取所有页面内容（用于管理后台）
   */
  async getAllPageContent() {
    const { data, error } = await supabase
      .from('page_contents')
      .select('*')
      .order('page_name', { ascending: true })
      .order('content_key', { ascending: true })

    if (error) throw error
    return data || []
  },

  /**
   * 更新内容
   */
  async updateContent(id, value) {
    const { data, error } = await supabase
      .from('page_contents')
      .update({ content_value: value })
      .eq('id', id)
      .select()
      .single()

    if (error) throw error
    return data
  },

  /**
   * 创建内容
   */
  async createContent(content) {
    const { data, error } = await supabase
      .from('page_contents')
      .insert([content])
      .select()
      .single()

    if (error) throw error
    return data
  },

  /**
   * 获取页面区块
   */
  async getPageSections(pageName) {
    const { data, error } = await supabase
      .from('page_sections')
      .select('*')
      .eq('page_name', pageName)
      .eq('is_visible', true)
      .order('section_order', { ascending: true })

    if (error) throw error
    return data || []
  },

  /**
   * 更新页面区块
   */
  async updateSection(id, updates) {
    const { data, error } = await supabase
      .from('page_sections')
      .update(updates)
      .eq('id', id)
      .select()
      .single()

    if (error) throw error
    return data
  }
}

// ============================================
// 新闻 API
// ============================================
export const newsAPI = {
  /**
   * 获取已发布的新闻
   */
  async getPublished(limit = 10) {
    const { data, error } = await supabase
      .from('news')
      .select('*')
      .eq('status', 'published')
      .order('created_at', { ascending: false })
      .limit(limit)

    if (error) throw error
    return data || []
  },

  /**
   * 获取所有新闻（管理员）
   */
  async getAll() {
    const { data, error } = await supabase
      .from('news')
      .select('*')
      .order('created_at', { ascending: false })

    if (error) throw error
    return data || []
  },

  /**
   * 根据 ID 获取新闻
   */
  async getById(id) {
    const { data, error } = await supabase
      .from('news')
      .select('*')
      .eq('id', id)
      .single()

    if (error) throw error
    return data
  },

  /**
   * 创建新闻
   */
  async create(news) {
    const { data, error } = await supabase
      .from('news')
      .insert([news])
      .select()
      .single()

    if (error) throw error
    return data
  },

  /**
   * 更新新闻
   */
  async update(id, updates) {
    const { data, error } = await supabase
      .from('news')
      .update(updates)
      .eq('id', id)
      .select()
      .single()

    if (error) throw error
    return data
  },

  /**
   * 删除新闻
   */
  async delete(id) {
    const { error } = await supabase
      .from('news')
      .delete()
      .eq('id', id)

    if (error) throw error
    return true
  }
}

// ============================================
// 询盘/联系表单 API
// ============================================
export const inquiriesAPI = {
  /**
   * 创建询盘
   */
  async create(inquiry) {
    const { data, error } = await supabase
      .from('inquiries')
      .insert([inquiry])
      .select()
      .single()

    if (error) throw error
    return data
  },

  /**
   * 获取所有询盘（管理员）
   */
  async getAll() {
    const { data, error } = await supabase
      .from('inquiries')
      .select('*')
      .order('created_at', { ascending: false })

    if (error) throw error
    return data || []
  },

  /**
   * 更新询盘状态
   */
  async updateStatus(id, status) {
    const { data, error } = await supabase
      .from('inquiries')
      .update({ status })
      .eq('id', id)
      .select()
      .single()

    if (error) throw error
    return data
  },

  /**
   * 删除询盘
   */
  async delete(id) {
    const { error } = await supabase
      .from('inquiries')
      .delete()
      .eq('id', id)

    if (error) throw error
    return true
  }
}

// ============================================
// 网站设置 API
// ============================================
export const settingsAPI = {
  /**
   * 获取所有公开设置
   */
  async getPublic() {
    const { data, error } = await supabase
      .from('site_settings')
      .select('*')
      .eq('is_public', true)

    if (error) throw error
    return data || []
  },

  /**
   * 获取所有设置（管理员）
   */
  async getAll() {
    const { data, error } = await supabase
      .from('site_settings')
      .select('*')
      .order('category', { ascending: true })

    if (error) throw error
    return data || []
  },

  /**
   * 根据 key 获取设置
   */
  async get(key) {
    const { data, error } = await supabase
      .from('site_settings')
      .select('*')
      .eq('setting_key', key)
      .single()

    if (error) throw error
    return data
  },

  /**
   * 更新设置
   */
  async update(key, value) {
    const { data, error } = await supabase
      .from('site_settings')
      .update({ setting_value: value })
      .eq('setting_key', key)
      .select()
      .single()

    if (error) throw error
    return data
  }
}

// ============================================
// 统计数据 API
// ============================================
export const statsAPI = {
  /**
   * 获取统计数据
   */
  async get() {
    try {
      const [products, news, inquiries] = await Promise.all([
        supabase.from('products').select('id', { count: 'exact', head: true }),
        supabase.from('news').select('id', { count: 'exact', head: true }),
        supabase.from('inquiries').select('id', { count: 'exact', head: true })
      ])

      return {
        products: products.count || 0,
        news: news.count || 0,
        inquiries: inquiries.count || 0
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
      return { products: 0, news: 0, inquiries: 0 }
    }
  }
}

// ============================================
// 实时订阅 API
// ============================================
export const realtimeAPI = {
  /**
   * 订阅表变化
   */
  subscribe(table, callback, event = '*') {
    return supabase
      .channel(`${table}_changes`)
      .on('postgres_changes',
        { event, schema: 'public', table },
        callback
      )
      .subscribe()
  },

  /**
   * 取消订阅
   */
  unsubscribe(subscription) {
    if (subscription) {
      supabase.removeChannel(subscription)
    }
  }
}

// ============================================
// 错误处理辅助函数
// ============================================
export class SupabaseError extends Error {
  constructor(message, originalError) {
    super(message)
    this.name = 'SupabaseError'
    this.originalError = originalError
  }
}

export function handleSupabaseError(error, context = '') {
  console.error(`Supabase Error${context ? ` (${context})` : ''}:`, error)

  // 根据错误类型返回用户友好的消息
  if (error.code === 'PGRST116') {
    return '未找到请求的数据'
  } else if (error.code === '23505') {
    return '数据已存在，无法重复创建'
  } else if (error.code === '23503') {
    return '关联数据不存在'
  } else if (error.message?.includes('JWT')) {
    return '登录已过期，请重新登录'
  } else if (error.message?.includes('permission')) {
    return '您没有权限执行此操作'
  }

  return error.message || '操作失败，请稍后重试'
}

// 导出默认对象
export default {
  supabase,
  auth,
  productsAPI,
  contentAPI,
  newsAPI,
  inquiriesAPI,
  settingsAPI,
  statsAPI,
  realtimeAPI,
  handleSupabaseError,
  SupabaseError
}
