// 导入Supabase客户端
import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm'

// Supabase配置
const supabaseUrl = 'https://jirudzbqcxviytcmxegf.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y218ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4'

// 创建Supabase客户端
const supabase = createClient(supabaseUrl, supabaseAnonKey)

// 登录函数
async function login(username, password) {
    try {
        // 显示加载中
        document.getElementById('loadingOverlay').style.display = 'flex'
        
        // 使用Supabase进行身份验证
        const { data, error } = await supabase.auth.signInWithPassword({
            email: `${username}@admin.com`, // 使用用户名作为邮箱前缀
            password: password
        })
        
        if (error) {
            throw error
        }
        
        // 登录成功，获取用户信息
        const { data: userData, error: userError } = await supabase
            .from('admin_users')
            .select('*')
            .eq('username', username)
            .single()
            
        if (userError) {
            throw userError
        }
        
        // 保存用户信息到本地存储
        localStorage.setItem('adminUser', JSON.stringify(userData))
        localStorage.setItem('adminToken', data.session.access_token)
        
        // 隐藏登录部分，显示管理面板
        document.getElementById('loginSection').style.display = 'none'
        document.getElementById('adminPanel').style.display = 'block'
        
        // 加载初始数据
        loadDashboardData()
        
        return { success: true }
    } catch (error) {
        console.error('登录失败:', error)
        return { success: false, message: error.message || '登录失败，请检查用户名和密码' }
    } finally {
        // 隐藏加载中
        document.getElementById('loadingOverlay').style.display = 'none'
    }
}

// 退出登录
function logout() {
    // 清除本地存储的用户信息
    localStorage.removeItem('adminUser')
    localStorage.removeItem('adminToken')
    
    // 调用Supabase退出登录
    supabase.auth.signOut()
    
    // 显示登录部分，隐藏管理面板
    document.getElementById('loginSection').style.display = 'block'
    document.getElementById('adminPanel').style.display = 'none'
}

// 检查是否已登录
function checkLogin() {
    const token = localStorage.getItem('adminToken')
    if (token) {
        // 验证token是否有效
        supabase.auth.getSession().then(({ data, error }) => {
            if (data.session) {
                // Token有效，显示管理面板
                document.getElementById('loginSection').style.display = 'none'
                document.getElementById('adminPanel').style.display = 'block'
                loadDashboardData()
            } else {
                // Token无效，显示登录部分
                logout()
            }
        })
    }
}

// 加载仪表盘数据
async function loadDashboardData() {
    try {
        // 获取产品数量
        const { count: productCount, error: productError } = await supabase
            .from('products')
            .select('*', { count: 'exact', head: true })
            
        if (!productError) {
            document.getElementById('productCount').textContent = productCount
        }
        
        // 获取询盘数量
        const { count: inquiryCount, error: inquiryError } = await supabase
            .from('inquiries')
            .select('*', { count: 'exact', head: true })
            
        if (!inquiryError) {
            document.getElementById('inquiryCount').textContent = inquiryCount
        }
        
        // 获取新闻数量
        const { count: newsCount, error: newsError } = await supabase
            .from('news')
            .select('*', { count: 'exact', head: true })
            
        if (!newsError) {
            document.getElementById('newsCount').textContent = newsCount
        }
        
        // 获取用户数量
        const { count: userCount, error: userError } = await supabase
            .from('admin_users')
            .select('*', { count: 'exact', head: true })
            
        if (!userError) {
            document.getElementById('totalUsers').textContent = userCount
        }
        
        // 获取最新询盘
        const { data: latestInquiries, error: latestInquiryError } = await supabase
            .from('inquiries')
            .select('*')
            .order('created_at', { ascending: false })
            .limit(5)
            
        if (!latestInquiryError && latestInquiries.length > 0) {
            const tableBody = document.getElementById('latestInquiriesTable')
            tableBody.innerHTML = ''
            
            latestInquiries.forEach(inquiry => {
                const row = document.createElement('tr')
                row.innerHTML = `
                    <td>${inquiry.name}</td>
                    <td>${inquiry.company}</td>
                    <td><span class="status-badge ${inquiry.status === 'pending' ? 'status-pending' : 'status-active'}">${inquiry.status === 'pending' ? '待处理' : '已处理'}</span></td>
                    <td>${new Date(inquiry.created_at).toLocaleDateString()}</td>
                `
                tableBody.appendChild(row)
            })
        }
        
        // 初始化访问统计图表
        initVisitsChart()
        
    } catch (error) {
        console.error('加载仪表盘数据失败:', error)
    }
}

// 初始化访问统计图表
function initVisitsChart() {
    const ctx = document.getElementById('visitsChart').getContext('2d')
    
    // 模拟数据
    const labels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    const data = {
        labels: labels,
        datasets: [{
            label: '网站访问量',
            data: [65, 59, 80, 81, 56, 55, 40],
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        }]
    }
    
    const config = {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    }
    
    new Chart(ctx, config)
}

// 产品管理相关函数
let currentProductPage = 1
const productsPerPage = 10
let totalProducts = 0

// 加载产品列表
async function loadProducts(page = 1) {
    try {
        document.getElementById('loadingOverlay').style.display = 'flex'
        
        // 计算分页
        const from = (page - 1) * productsPerPage
        const to = from + productsPerPage - 1
        
        // 获取产品总数
        const { count, error: countError } = await supabase
            .from('products')
            .select('*', { count: 'exact', head: true })
            
        if (countError) throw countError
        
        totalProducts = count
        
        // 更新分页信息
        document.getElementById('productTotalCount').textContent = totalProducts
        document.getElementById('productStartRange').textContent = from + 1
        document.getElementById('productEndRange').textContent = Math.min(to + 1, totalProducts)
        
        // 禁用/启用分页按钮
        document.getElementById('productPrevBtn').disabled = page === 1
        document.getElementById('productNextBtn').disabled = to + 1 >= totalProducts
        
        // 获取产品列表
        const { data: products, error } = await supabase
            .from('products')
            .select('*')
            .range(from, to)
            .order('created_at', { ascending: false })
            
        if (error) throw error
        
        // 更新产品表格
        const tableBody = document.getElementById('productsTable')
        tableBody.innerHTML = ''
        
        if (products.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center">暂无产品数据</td></tr>'
            return
        }
        
        products.forEach(product => {
            const row = document.createElement('tr')
            row.innerHTML = `
                <td>${product.name}</td>
                <td>${product.category}</td>
                <td>${product.price ? '¥' + product.price : '面议'}</td>
                <td><span class="status-badge ${product.status === 'active' ? 'status-active' : 'status-inactive'}">${product.status === 'active' ? '上架' : '下架'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editProduct(${product.id})">编辑</button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteProduct(${product.id})">删除</button>
                </td>
            `
            tableBody.appendChild(row)
        })
    } catch (error) {
        console.error('加载产品列表失败:', error)
        alert('加载产品列表失败: ' + error.message)
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none'
    }
}

// 上一页产品
function prevProductPage() {
    if (currentProductPage > 1) {
        currentProductPage--
        loadProducts(currentProductPage)
    }
}

// 下一页产品
function nextProductPage() {
    if ((currentProductPage * productsPerPage) < totalProducts) {
        currentProductPage++
        loadProducts(currentProductPage)
    }
}

// 搜索产品
async function searchProducts() {
    const searchTerm = document.getElementById('productSearchInput').value.trim()
    
    if (!searchTerm) {
        loadProducts(1)
        return
    }
    
    try {
        document.getElementById('loadingOverlay').style.display = 'flex'
        
        const { data: products, error } = await supabase
            .from('products')
            .select('*')
            .ilike('name', `%${searchTerm}%`)
            .order('created_at', { ascending: false })
            
        if (error) throw error
        
        // 更新产品表格
        const tableBody = document.getElementById('productsTable')
        tableBody.innerHTML = ''
        
        if (products.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center">未找到匹配的产品</td></tr>'
            return
        }
        
        products.forEach(product => {
            const row = document.createElement('tr')
            row.innerHTML = `
                <td>${product.name}</td>
                <td>${product.category}</td>
                <td>${product.price ? '¥' + product.price : '面议'}</td>
                <td><span class="status-badge ${product.status === 'active' ? 'status-active' : 'status-inactive'}">${product.status === 'active' ? '上架' : '下架'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editProduct(${product.id})">编辑</button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteProduct(${product.id})">删除</button>
                </td>
            `
            tableBody.appendChild(row)
        })
        
        // 更新分页信息
        document.getElementById('productTotalCount').textContent = products.length
        document.getElementById('productStartRange').textContent = '1'
        document.getElementById('productEndRange').textContent = products.length
        
        // 禁用分页按钮
        document.getElementById('productPrevBtn').disabled = true
        document.getElementById('productNextBtn').disabled = true
    } catch (error) {
        console.error('搜索产品失败:', error)
        alert('搜索产品失败: ' + error.message)
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none'
    }
}

// 导出函数
window.login = async function() {
    const username = document.getElementById('username').value
    const password = document.getElementById('password').value
    
    if (!username || !password) {
        alert('请输入用户名和密码')
        return
    }
    
    const result = await login(username, password)
    
    if (!result.success) {
        alert(result.message)
    }
}

window.logout = logout
window.checkLogin = checkLogin
window.loadProducts = loadProducts
window.prevProductPage = prevProductPage
window.nextProductPage = nextProductPage
window.searchProducts = searchProducts

// 页面加载完成后检查登录状态
document.addEventListener('DOMContentLoaded', checkLogin)

// 导出Supabase客户端，以便其他模块使用
export { supabase }