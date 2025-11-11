/**
 * 后台管理系统 JavaScript
 * 处理页面切换、数据加载、认证等功能
 */

// 初始化
document.addEventListener('DOMContentLoaded', async function() {
    console.log('📊 管理后台初始化中...')

    // 检查认证
    await checkAuth()

    // 加载统计数据
    await loadDashboardStats()

    // 设置事件监听器
    setupEventListeners()

    console.log('✅ 管理后台初始化完成')
})

/**
 * 检查用户认证状态
 */
async function checkAuth() {
    try {
        // 检查是否有 Supabase 客户端
        if (typeof supabase === 'undefined') {
            console.warn('⚠️ Supabase 客户端未加载')
            return
        }

        // 获取当前会话
        const { data: { session }, error } = await supabase.auth.getSession()

        if (error) {
            console.error('认证检查错误:', error)
            redirectToLogin()
            return
        }

        if (!session) {
            console.warn('⚠️ 未登录，跳转到登录页')
            redirectToLogin()
            return
        }

        // 验证是否是管理员
        const { data: adminUser, error: adminError } = await supabase
            .from('admin_users')
            .select('username, role')
            .eq('user_id', session.user.id)
            .eq('is_active', true)
            .single()

        if (adminError || !adminUser) {
            console.error('❌ 非管理员用户')
            alert('您没有访问管理后台的权限')
            redirectToLogin()
            return
        }

        // 显示用户信息
        const welcomeEl = document.getElementById('userWelcome')
        if (welcomeEl) {
            welcomeEl.textContent = `欢迎，${adminUser.username} (${getRoleName(adminUser.role)})`
        }

        console.log('✅ 认证成功:', adminUser.username)

    } catch (error) {
        console.error('认证检查异常:', error)
        redirectToLogin()
    }
}

/**
 * 跳转到登录页
 */
function redirectToLogin() {
    window.location.href = '/admin/login.html'
}

/**
 * 获取角色名称
 */
function getRoleName(role) {
    const roleNames = {
        'super_admin': '超级管理员',
        'admin': '管理员',
        'editor': '编辑',
        'viewer': '查看者'
    }
    return roleNames[role] || role
}

/**
 * 登出功能
 */
async function logout() {
    try {
        if (typeof supabase !== 'undefined') {
            const { error } = await supabase.auth.signOut()
            if (error) {
                console.error('登出错误:', error)
            }
        }

        // 清除本地存储
        localStorage.clear()
        sessionStorage.clear()

        // 跳转到登录页
        window.location.href = '/admin/login.html'

    } catch (error) {
        console.error('登出异常:', error)
        window.location.href = '/admin/login.html'
    }
}

/**
 * 显示指定的内容区域
 */
function showSection(sectionId) {
    console.log('📄 切换到:', sectionId)

    // 隐藏所有内容区域
    const sections = document.querySelectorAll('.content-section')
    sections.forEach(section => {
        section.classList.remove('active')
    })

    // 显示目标区域
    const targetSection = document.getElementById(sectionId)
    if (targetSection) {
        targetSection.classList.add('active')
    }

    // 更新导航高亮
    const navLinks = document.querySelectorAll('.nav-link')
    navLinks.forEach(link => {
        link.classList.remove('active')
    })

    const activeLink = document.querySelector(`a[onclick*="${sectionId}"]`)
    if (activeLink) {
        activeLink.classList.add('active')
    }

    // 根据不同部分加载数据
    switch(sectionId) {
        case 'products':
            loadProducts()
            break
        case 'news':
            loadNews()
            break
        case 'inquiries':
            loadInquiries()
            break
        case 'users':
            loadUsers()
            break
    }
}

/**
 * 加载仪表板统计数据
 */
async function loadDashboardStats() {
    try {
        console.log('📊 加载统计数据...')

        // 检查 API 是否可用
        if (typeof window.dataAPI === 'undefined' && typeof supabase === 'undefined') {
            console.warn('⚠️ 数据API不可用，显示占位数据')
            setStatPlaceholders()
            return
        }

        // 使用统一数据API或直接查询
        const api = window.dataAPI || supabase

        // 加载产品数量
        loadProductCount(api)

        // 加载新闻数量
        loadNewsCount(api)

        // 加载询问数量
        loadInquiryCount(api)

        // 加载用户数量
        loadUserCount(api)

    } catch (error) {
        console.error('加载统计数据错误:', error)
        setStatPlaceholders()
    }
}

/**
 * 设置统计数据占位符
 */
function setStatPlaceholders() {
    document.getElementById('totalProducts').textContent = '0'
    document.getElementById('totalNews').textContent = '0'
    document.getElementById('totalInquiries').textContent = '0'
    document.getElementById('totalUsers').textContent = '0'
}

/**
 * 加载产品数量
 */
async function loadProductCount(api) {
    try {
        if (window.dataAPI && window.dataAPI.products) {
            const products = await window.dataAPI.products.getAll()
            document.getElementById('totalProducts').textContent = products.length
        } else if (supabase) {
            const { count, error } = await supabase
                .from('products')
                .select('*', { count: 'exact', head: true })

            if (!error) {
                document.getElementById('totalProducts').textContent = count || 0
            }
        }
    } catch (error) {
        console.error('加载产品数量错误:', error)
        document.getElementById('totalProducts').textContent = '-'
    }
}

/**
 * 加载新闻数量
 */
async function loadNewsCount(api) {
    try {
        if (window.dataAPI && window.dataAPI.news) {
            const news = await window.dataAPI.news.getAll()
            document.getElementById('totalNews').textContent = news.length
        } else if (supabase) {
            const { count, error } = await supabase
                .from('news')
                .select('*', { count: 'exact', head: true })

            if (!error) {
                document.getElementById('totalNews').textContent = count || 0
            }
        }
    } catch (error) {
        console.error('加载新闻数量错误:', error)
        document.getElementById('totalNews').textContent = '-'
    }
}

/**
 * 加载询问数量
 */
async function loadInquiryCount(api) {
    try {
        if (window.dataAPI && window.dataAPI.inquiries) {
            const inquiries = await window.dataAPI.inquiries.getAll()
            document.getElementById('totalInquiries').textContent = inquiries.length
        } else if (supabase) {
            const { count, error } = await supabase
                .from('inquiries')
                .select('*', { count: 'exact', head: true })

            if (!error) {
                document.getElementById('totalInquiries').textContent = count || 0
            }
        }
    } catch (error) {
        console.error('加载询问数量错误:', error)
        document.getElementById('totalInquiries').textContent = '-'
    }
}

/**
 * 加载用户数量
 */
async function loadUserCount(api) {
    try {
        if (supabase) {
            const { count, error } = await supabase
                .from('admin_users')
                .select('*', { count: 'exact', head: true })

            if (!error) {
                document.getElementById('totalUsers').textContent = count || 0
            }
        }
    } catch (error) {
        console.error('加载用户数量错误:', error)
        document.getElementById('totalUsers').textContent = '-'
    }
}

/**
 * 加载产品列表
 */
async function loadProducts() {
    console.log('📦 加载产品列表...')

    const loading = document.getElementById('productsLoading')
    const table = document.getElementById('productsTable')
    const tbody = document.getElementById('productsTableBody')

    try {
        loading.style.display = 'block'
        table.style.display = 'none'

        let products = []

        if (window.dataAPI && window.dataAPI.products) {
            products = await window.dataAPI.products.getAll()
        } else if (supabase) {
            const { data, error } = await supabase
                .from('products')
                .select('*')
                .order('created_at', { ascending: false })

            if (!error) {
                products = data || []
            }
        }

        // 渲染产品列表
        tbody.innerHTML = products.map(product => `
            <tr>
                <td>${product.id}</td>
                <td>${product.name || '-'}</td>
                <td>${product.category || '-'}</td>
                <td>${product.price ? '¥' + product.price : '-'}</td>
                <td>${formatDate(product.created_at)}</td>
                <td>
                    <button class="btn btn-sm" onclick="editProduct('${product.id}')">编辑</button>
                    <button class="btn btn-sm" onclick="deleteProduct('${product.id}')">删除</button>
                </td>
            </tr>
        `).join('')

        loading.style.display = 'none'
        table.style.display = 'table'

    } catch (error) {
        console.error('加载产品列表错误:', error)
        loading.innerHTML = '<p style="color: red;">加载失败: ' + error.message + '</p>'
    }
}

/**
 * 加载新闻列表
 */
async function loadNews() {
    console.log('📰 加载新闻列表...')

    const loading = document.getElementById('newsLoading')
    const table = document.getElementById('newsTable')
    const tbody = document.getElementById('newsTableBody')

    try {
        loading.style.display = 'block'
        table.style.display = 'none'

        let news = []

        if (window.dataAPI && window.dataAPI.news) {
            news = await window.dataAPI.news.getAll()
        } else if (supabase) {
            const { data, error } = await supabase
                .from('news')
                .select('*')
                .order('created_at', { ascending: false })

            if (!error) {
                news = data || []
            }
        }

        // 渲染新闻列表
        tbody.innerHTML = news.map(item => `
            <tr>
                <td>${item.id}</td>
                <td>${item.title || '-'}</td>
                <td>${item.author || '-'}</td>
                <td>${item.status || '-'}</td>
                <td>${formatDate(item.created_at)}</td>
                <td>
                    <button class="btn btn-sm" onclick="editNews('${item.id}')">编辑</button>
                    <button class="btn btn-sm" onclick="deleteNews('${item.id}')">删除</button>
                </td>
            </tr>
        `).join('')

        loading.style.display = 'none'
        table.style.display = 'table'

    } catch (error) {
        console.error('加载新闻列表错误:', error)
        loading.innerHTML = '<p style="color: red;">加载失败: ' + error.message + '</p>'
    }
}

/**
 * 加载客户询问列表
 */
async function loadInquiries() {
    console.log('📧 加载客户询问列表...')

    const loading = document.getElementById('inquiriesLoading')
    const table = document.getElementById('inquiriesTable')
    const tbody = document.getElementById('inquiriesTableBody')

    try {
        loading.style.display = 'block'
        table.style.display = 'none'

        let inquiries = []

        if (window.dataAPI && window.dataAPI.inquiries) {
            inquiries = await window.dataAPI.inquiries.getAll()
        } else if (supabase) {
            const { data, error } = await supabase
                .from('inquiries')
                .select('*')
                .order('created_at', { ascending: false })

            if (!error) {
                inquiries = data || []
            }
        }

        // 渲染询问列表
        tbody.innerHTML = inquiries.map(inquiry => `
            <tr>
                <td>${inquiry.id}</td>
                <td>${inquiry.name || '-'}</td>
                <td>${inquiry.email || '-'}</td>
                <td>${inquiry.company || '-'}</td>
                <td>${inquiry.status || 'pending'}</td>
                <td>${formatDate(inquiry.created_at)}</td>
                <td>
                    <button class="btn btn-sm" onclick="viewInquiry('${inquiry.id}')">查看</button>
                    <button class="btn btn-sm" onclick="deleteInquiry('${inquiry.id}')">删除</button>
                </td>
            </tr>
        `).join('')

        loading.style.display = 'none'
        table.style.display = 'table'

    } catch (error) {
        console.error('加载询问列表错误:', error)
        loading.innerHTML = '<p style="color: red;">加载失败: ' + error.message + '</p>'
    }
}

/**
 * 加载用户列表
 */
async function loadUsers() {
    console.log('👥 加载用户列表...')

    const loading = document.getElementById('usersLoading')
    const table = document.getElementById('usersTable')
    const tbody = document.getElementById('usersTableBody')

    try {
        loading.style.display = 'block'
        table.style.display = 'none'

        let users = []

        if (supabase) {
            const { data, error } = await supabase
                .from('admin_users')
                .select('*')
                .order('created_at', { ascending: false })

            if (!error) {
                users = data || []
            }
        }

        // 渲染用户列表
        tbody.innerHTML = users.map(user => `
            <tr>
                <td>${user.id}</td>
                <td>${user.username || '-'}</td>
                <td>${getRoleName(user.role)}</td>
                <td>${formatDate(user.created_at)}</td>
                <td>
                    <button class="btn btn-sm" onclick="editUser('${user.id}')">编辑</button>
                    <button class="btn btn-sm" onclick="deleteUser('${user.id}')">删除</button>
                </td>
            </tr>
        `).join('')

        loading.style.display = 'none'
        table.style.display = 'table'

    } catch (error) {
        console.error('加载用户列表错误:', error)
        loading.innerHTML = '<p style="color: red;">加载失败: ' + error.message + '</p>'
    }
}

/**
 * 格式化日期
 */
function formatDate(dateString) {
    if (!dateString) return '-'

    try {
        const date = new Date(dateString)
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        })
    } catch (error) {
        return dateString
    }
}

/**
 * 设置事件监听器
 */
function setupEventListeners() {
    // 可以在这里添加全局事件监听器
    console.log('📡 事件监听器已设置')
}

// ========== 占位函数（未来实现） ==========

function addProduct() {
    alert('添加产品功能开发中...')
}

function editProduct(id) {
    alert('编辑产品功能开发中: ' + id)
}

function deleteProduct(id) {
    if (confirm('确定要删除这个产品吗？')) {
        alert('删除产品功能开发中: ' + id)
    }
}

function addNews() {
    alert('添加新闻功能开发中...')
}

function editNews(id) {
    alert('编辑新闻功能开发中: ' + id)
}

function deleteNews(id) {
    if (confirm('确定要删除这条新闻吗？')) {
        alert('删除新闻功能开发中: ' + id)
    }
}

function viewInquiry(id) {
    alert('查看询问功能开发中: ' + id)
}

function deleteInquiry(id) {
    if (confirm('确定要删除这个询问吗？')) {
        alert('删除询问功能开发中: ' + id)
    }
}

function addUser() {
    alert('添加用户功能开发中...')
}

function editUser(id) {
    alert('编辑用户功能开发中: ' + id)
}

function deleteUser(id) {
    if (confirm('确定要删除这个用户吗？')) {
        alert('删除用户功能开发中: ' + id)
    }
}

// 导出函数供全局使用
window.showSection = showSection
window.logout = logout
