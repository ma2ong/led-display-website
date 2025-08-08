// 检查登录状态
function checkAuth() {
    const adminUser = localStorage.getItem('adminUser');
    if (!adminUser) {
        window.location.href = 'login.html';
        return null;
    }
    
    const user = JSON.parse(adminUser);
    document.getElementById('userWelcome').textContent = `欢迎，${user.username}`;
    return user;
}

// 退出登录
function logout() {
    localStorage.removeItem('adminUser');
    window.location.href = 'login.html';
}

// 显示指定部分
function showSection(sectionId) {
    // 隐藏所有部分
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // 移除所有导航链接的active类
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // 显示指定部分
    document.getElementById(sectionId).classList.add('active');
    
    // 添加active类到对应的导航链接
    document.querySelector(`[onclick="showSection('${sectionId}')"]`).classList.add('active');
    
    // 根据部分加载数据
    switch(sectionId) {
        case 'dashboard':
            loadDashboardStats();
            break;
        case 'products':
            loadProducts();
            break;
        case 'news':
            loadNews();
            break;
        case 'inquiries':
            loadInquiries();
            break;
        case 'users':
            loadUsers();
            break;
    }
}

// 加载仪表板统计数据
async function loadDashboardStats() {
    try {
        const supabase = getSupabaseClient();
        
        // 获取产品数量
        const { count: productsCount } = await supabase
            .from('products')
            .select('*', { count: 'exact', head: true });
        
        // 获取新闻数量
        const { count: newsCount } = await supabase
            .from('news')
            .select('*', { count: 'exact', head: true });
        
        // 获取询问数量
        const { count: inquiriesCount } = await supabase
            .from('inquiries')
            .select('*', { count: 'exact', head: true });
        
        // 获取用户数量
        const { count: usersCount } = await supabase
            .from('users')
            .select('*', { count: 'exact', head: true });
        
        // 更新统计数据
        document.getElementById('totalProducts').textContent = productsCount || 0;
        document.getElementById('totalNews').textContent = newsCount || 0;
        document.getElementById('totalInquiries').textContent = inquiriesCount || 0;
        document.getElementById('totalUsers').textContent = usersCount || 0;
        
    } catch (error) {
        console.error('加载统计数据失败:', error);
    }
}

// 加载产品列表
async function loadProducts() {
    const loading = document.getElementById('productsLoading');
    const table = document.getElementById('productsTable');
    const tbody = document.getElementById('productsTableBody');
    
    loading.style.display = 'block';
    table.style.display = 'none';
    
    try {
        const supabase = getSupabaseClient();
        const { data: products, error } = await supabase
            .from('products')
            .select('*')
            .order('id');
        
        if (error) throw error;
        
        tbody.innerHTML = '';
        products.forEach(product => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${product.id}</td>
                <td>${product.name}</td>
                <td>${product.category}</td>
                <td>${product.price ? '¥' + product.price : '未设置'}</td>
                <td>${new Date(product.created_at).toLocaleDateString()}</td>
                <td>
                    <button class="btn" onclick="editProduct(${product.id})">编辑</button>
                    <button class="btn" style="background: #e74c3c;" onclick="deleteProduct(${product.id})">删除</button>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        loading.style.display = 'none';
        table.style.display = 'table';
        
    } catch (error) {
        console.error('加载产品列表失败:', error);
        loading.textContent = '加载失败';
    }
}

// 加载新闻列表
async function loadNews() {
    const loading = document.getElementById('newsLoading');
    const table = document.getElementById('newsTable');
    const tbody = document.getElementById('newsTableBody');
    
    loading.style.display = 'block';
    table.style.display = 'none';
    
    try {
        const supabase = getSupabaseClient();
        const { data: news, error } = await supabase
            .from('news')
            .select('*')
            .order('created_at', { ascending: false });
        
        if (error) throw error;
        
        tbody.innerHTML = '';
        news.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.id}</td>
                <td>${item.title}</td>
                <td>${item.author || '未设置'}</td>
                <td>${item.status}</td>
                <td>${new Date(item.created_at).toLocaleDateString()}</td>
                <td>
                    <button class="btn" onclick="editNews(${item.id})">编辑</button>
                    <button class="btn" style="background: #e74c3c;" onclick="deleteNews(${item.id})">删除</button>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        loading.style.display = 'none';
        table.style.display = 'table';
        
    } catch (error) {
        console.error('加载新闻列表失败:', error);
        loading.textContent = '加载失败';
    }
}

// 加载客户询问列表
async function loadInquiries() {
    const loading = document.getElementById('inquiriesLoading');
    const table = document.getElementById('inquiriesTable');
    const tbody = document.getElementById('inquiriesTableBody');
    
    loading.style.display = 'block';
    table.style.display = 'none';
    
    try {
        const supabase = getSupabaseClient();
        const { data: inquiries, error } = await supabase
            .from('inquiries')
            .select('*')
            .order('created_at', { ascending: false });
        
        if (error) throw error;
        
        tbody.innerHTML = '';
        inquiries.forEach(inquiry => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${inquiry.id}</td>
                <td>${inquiry.name}</td>
                <td>${inquiry.email}</td>
                <td>${inquiry.company || '未填写'}</td>
                <td>${inquiry.status}</td>
                <td>${new Date(inquiry.created_at).toLocaleDateString()}</td>
                <td>
                    <button class="btn" onclick="viewInquiry(${inquiry.id})">查看</button>
                    <button class="btn" onclick="updateInquiryStatus(${inquiry.id})">更新状态</button>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        loading.style.display = 'none';
        table.style.display = 'table';
        
    } catch (error) {
        console.error('加载客户询问失败:', error);
        loading.textContent = '加载失败';
    }
}

// 加载用户列表
async function loadUsers() {
    const loading = document.getElementById('usersLoading');
    const table = document.getElementById('usersTable');
    const tbody = document.getElementById('usersTableBody');
    
    loading.style.display = 'block';
    table.style.display = 'none';
    
    try {
        const supabase = getSupabaseClient();
        const { data: users, error } = await supabase
            .from('users')
            .select('*')
            .order('created_at', { ascending: false });
        
        if (error) throw error;
        
        tbody.innerHTML = '';
        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.id}</td>
                <td>${user.username}</td>
                <td>${user.role}</td>
                <td>${new Date(user.created_at).toLocaleDateString()}</td>
                <td>
                    <button class="btn" onclick="editUser(${user.id})">编辑</button>
                    <button class="btn" style="background: #e74c3c;" onclick="deleteUser(${user.id})">删除</button>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        loading.style.display = 'none';
        table.style.display = 'table';
        
    } catch (error) {
        console.error('加载用户列表失败:', error);
        loading.textContent = '加载失败';
    }
}

// 占位符函数 - 这些可以根据需要进一步实现
function addProduct() {
    alert('添加产品功能待实现');
}

function editProduct(id) {
    alert(`编辑产品 ID: ${id}`);
}

function deleteProduct(id) {
    if (confirm('确定要删除这个产品吗？')) {
        // 实现删除逻辑
        alert(`删除产品 ID: ${id}`);
    }
}

function addNews() {
    alert('添加新闻功能待实现');
}

function editNews(id) {
    alert(`编辑新闻 ID: ${id}`);
}

function deleteNews(id) {
    if (confirm('确定要删除这条新闻吗？')) {
        alert(`删除新闻 ID: ${id}`);
    }
}

function viewInquiry(id) {
    alert(`查看询问 ID: ${id}`);
}

function updateInquiryStatus(id) {
    alert(`更新询问状态 ID: ${id}`);
}

function addUser() {
    alert('添加用户功能待实现');
}

function editUser(id) {
    alert(`编辑用户 ID: ${id}`);
}

function deleteUser(id) {
    if (confirm('确定要删除这个用户吗？')) {
        alert(`删除用户 ID: ${id}`);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 检查登录状态
    const user = checkAuth();
    if (user) {
        // 加载仪表板数据
        loadDashboardStats();
    }
});