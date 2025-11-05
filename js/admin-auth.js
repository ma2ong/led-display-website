/**
 * 安全的管理员认证系统
 * 使用 Supabase Auth 进行真实认证
 */

import { auth, handleSupabaseError } from '../lib/supabase-client.js'

// ============================================
// 登录处理
// ============================================

/**
 * 处理管理员登录
 */
export async function handleLogin(email, password) {
  try {
    // 1. 使用 Supabase Auth 登录
    const { user, session } = await auth.login(email, password)

    if (!user || !session) {
      throw new Error('登录失败')
    }

    // 2. 验证管理员权限
    const isAdmin = await auth.isAdmin()
    if (!isAdmin) {
      // 如果不是管理员，立即登出
      await auth.logout()
      throw new Error('您没有管理员权限，请联系系统管理员')
    }

    // 3. 获取管理员角色
    const role = await auth.getAdminRole()

    // 4. 存储用户信息到 localStorage（用于快速访问）
    const adminUser = {
      userId: user.id,
      email: user.email,
      role: role,
      loginTime: new Date().toISOString()
    }
    localStorage.setItem('admin_user', JSON.stringify(adminUser))

    return {
      success: true,
      user: adminUser,
      message: '登录成功！'
    }

  } catch (error) {
    console.error('Login error:', error)

    // 记录失败的登录尝试
    try {
      await auth.logLogin(null, email, 'failed', error.message)
    } catch (logError) {
      console.error('Error logging failed login:', logError)
    }

    return {
      success: false,
      message: handleSupabaseError(error, 'login')
    }
  }
}

/**
 * 处理管理员登出
 */
export async function handleLogout() {
  try {
    await auth.logout()
    localStorage.removeItem('admin_user')
    return { success: true }
  } catch (error) {
    console.error('Logout error:', error)
    return {
      success: false,
      message: handleSupabaseError(error, 'logout')
    }
  }
}

// ============================================
// 会话验证
// ============================================

/**
 * 验证管理员会话
 */
export async function validateAdminSession() {
  try {
    // 1. 检查 Supabase 会话
    const session = await auth.getSession()
    if (!session) {
      return { valid: false, reason: 'no_session' }
    }

    // 2. 检查用户是否为管理员
    const isAdmin = await auth.isAdmin()
    if (!isAdmin) {
      return { valid: false, reason: 'not_admin' }
    }

    // 3. 获取用户信息
    const user = await auth.getCurrentUser()
    const role = await auth.getAdminRole()

    // 4. 更新 localStorage
    const adminUser = {
      userId: user.id,
      email: user.email,
      role: role,
      loginTime: new Date().toISOString()
    }
    localStorage.setItem('admin_user', JSON.stringify(adminUser))

    return {
      valid: true,
      user: adminUser
    }

  } catch (error) {
    console.error('Session validation error:', error)
    return { valid: false, reason: 'error', error }
  }
}

/**
 * 检查管理员权限（用于页面加载时）
 */
export async function checkAdminAccess() {
  const validation = await validateAdminSession()

  if (!validation.valid) {
    // 清除本地存储
    localStorage.removeItem('admin_user')

    // 重定向到登录页
    const currentPath = window.location.pathname
    if (!currentPath.includes('login.html')) {
      window.location.href = '/admin/login.html'
    }

    return false
  }

  return true
}

/**
 * 获取当前管理员信息
 */
export function getCurrentAdmin() {
  const adminData = localStorage.getItem('admin_user')
  if (!adminData) return null

  try {
    return JSON.parse(adminData)
  } catch (error) {
    console.error('Error parsing admin data:', error)
    return null
  }
}

// ============================================
// 权限检查
// ============================================

/**
 * 检查是否有特定权限
 */
export function hasPermission(requiredRole) {
  const admin = getCurrentAdmin()
  if (!admin) return false

  const roleHierarchy = {
    'super_admin': 4,
    'admin': 3,
    'editor': 2,
    'viewer': 1
  }

  const userLevel = roleHierarchy[admin.role] || 0
  const requiredLevel = roleHierarchy[requiredRole] || 0

  return userLevel >= requiredLevel
}

/**
 * 检查是否为超级管理员
 */
export function isSuperAdmin() {
  return hasPermission('super_admin')
}

/**
 * 检查是否可以编辑
 */
export function canEdit() {
  return hasPermission('editor')
}

/**
 * 检查是否可以查看
 */
export function canView() {
  return hasPermission('viewer')
}

// ============================================
// UI 辅助函数
// ============================================

/**
 * 显示加载状态
 */
export function showLoading(button, loadingText = '处理中...') {
  if (!button) return

  button.dataset.originalText = button.textContent
  button.textContent = loadingText
  button.disabled = true
}

/**
 * 隐藏加载状态
 */
export function hideLoading(button) {
  if (!button) return

  button.textContent = button.dataset.originalText || '登录'
  button.disabled = false
}

/**
 * 显示错误消息
 */
export function showError(message, container = null) {
  if (container) {
    container.innerHTML = `
      <div class="alert alert-danger alert-dismissible fade show" role="alert">
        <i class="fas fa-exclamation-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
      </div>
    `
  } else {
    alert(message)
  }
}

/**
 * 显示成功消息
 */
export function showSuccess(message, container = null) {
  if (container) {
    container.innerHTML = `
      <div class="alert alert-success alert-dismissible fade show" role="alert">
        <i class="fas fa-check-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
      </div>
    `
  } else {
    alert(message)
  }
}

// ============================================
// 监听认证状态变化
// ============================================

/**
 * 设置认证状态监听
 */
export function setupAuthListener(onSignIn, onSignOut) {
  auth.onAuthStateChange((event, session) => {
    console.log('Auth state changed:', event)

    if (event === 'SIGNED_IN' && session) {
      if (onSignIn) onSignIn(session)
    } else if (event === 'SIGNED_OUT') {
      localStorage.removeItem('admin_user')
      if (onSignOut) onSignOut()
    }
  })
}

// 导出默认对象
export default {
  handleLogin,
  handleLogout,
  validateAdminSession,
  checkAdminAccess,
  getCurrentAdmin,
  hasPermission,
  isSuperAdmin,
  canEdit,
  canView,
  showLoading,
  hideLoading,
  showError,
  showSuccess,
  setupAuthListener
}
