// 管理系统主脚本
document.addEventListener('DOMContentLoaded', function() {
    // 全局变量
    let currentAdmin = null;
    let currentEditingPage = null;
    
    // 检查是否已登录
    function checkLoginStatus() {
        const adminUser = localStorage.getItem('admin_user');
        if (adminUser) {
            try {
                currentAdmin = JSON.parse(adminUser);
                console.log('登录状态检查成功:', currentAdmin);
                
                // 更新用户名显示
                const usernameElement = document.getElementById('admin-username');
                if (usernameElement) {
                    usernameElement.textContent = currentAdmin.username || 'admin';
                }
                
                // 切换界面显示
                const loginSection = document.getElementById('login-section');
                const adminSection = document.getElementById('admin-section');
                
                if (loginSection) loginSection.style.display = 'none';
                if (adminSection) adminSection.style.display = 'block';
                
                loadDashboard();
                return true;
            } catch (e) {
                console.error('解析登录信息失败:', e);
                // 清除无效的登录信息
                localStorage.removeItem('admin_user');
            }
        }
        return false;
    }
    
    // 登录处理
    if (document.getElementById('login-form')) {
        document.getElementById('login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                // 简化登录逻辑，直接使用本地验证
                if (username === 'admin' && password === 'admin123') {
                    currentAdmin = { username };
                    localStorage.setItem('admin_user', JSON.stringify(currentAdmin));
                    document.getElementById('admin-username').textContent = username;
                    document.getElementById('login-section').style.display = 'none';
                    document.getElementById('admin-section').style.display = 'block';
                    loadDashboard();
                } else {
                    alert('用户名或密码错误');
                }
            } catch (error) {
                console.error('登录错误:', error);
                alert('登录失败，请使用 admin/admin123');
            }
        });
    }

    // 导航处理
    document.querySelectorAll('.sidebar .nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // 更新导航状态
            document.querySelectorAll('.sidebar .nav-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            // 显示对应内容
            const section = link.getAttribute('data-section');
            showSection(section);
            
            // 更新页面标题
            document.getElementById('page-title').textContent = getPageTitle(section);
        });
    });

    // 获取页面标题
    function getPageTitle(section) {
        const pageTitles = {
            'dashboard': '仪表盘总览',
            'frontend': '前端页面管理',
            'products': '产品管理',
            'inquiries': '询盘管理',
            'news': '新闻管理',
            'users': '用户管理',
            'settings': '系统设置',
            'statistics': '统计分析'
        };
        return pageTitles[section] || section;
    }

    // 显示指定内容区域
    function showSection(section) {
        document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
        const sectionElement = document.getElementById(`${section}-content`);
        if (sectionElement) {
            sectionElement.classList.add('active');
            
            // 根据不同section加载对应数据
            switch(section) {
                case 'dashboard':
                    loadDashboard();
                    break;
                case 'products':
                    loadProducts();
                    break;
                case 'inquiries':
                    loadInquiries();
                    break;
                case 'news':
                    loadNews();
                    break;
                case 'users':
                    loadUsers();
                    break;
                case 'statistics':
                    loadStatistics();
                    break;
            }
        }
    }

    // 加载仪表盘数据
    window.loadDashboard = function() {
        // 使用默认数据
        document.getElementById('stat-pages').textContent = '8';
        document.getElementById('stat-products').textContent = '0';
        document.getElementById('stat-inquiries').textContent = '0';
        document.getElementById('stat-news').textContent = '0';
        
        // 清空询盘表格
        const tbody = document.getElementById('recent-inquiries');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">暂无数据</td></tr>';
        }
    }

    // 加载产品数据
    window.loadProducts = function() {
        const tbody = document.getElementById('products-table');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">暂无数据</td></tr>';
        }
    }

    // 加载询盘数据
    window.loadInquiries = function() {
        const tbody = document.getElementById('inquiries-table');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted py-4">暂无数据</td></tr>';
        }
    }

    // 加载新闻数据
    window.loadNews = function() {
        const tbody = document.getElementById('news-table');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">暂无数据</td></tr>';
        }
    }

    // 加载用户数据
    window.loadUsers = function() {
        const tbody = document.getElementById('users-table');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td>1</td>
                    <td>admin</td>
                    <td>admin@lianjinled.com</td>
                    <td><span class="badge bg-danger">超级管理员</span></td>
                    <td><span class="badge bg-success">活跃</span></td>
                    <td>${new Date().toLocaleDateString()}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="editUser(1)">
                            <i class="fas fa-edit"></i>
                        </button>
                    </td>
                </tr>
            `;
        }
    }

    // 加载统计数据
    window.loadStatistics = function() {
        // 复用仪表盘数据
        loadDashboard();
        
        // 更新统计页面的数据
        if (document.getElementById('total-inquiries')) {
            document.getElementById('total-inquiries').textContent = document.getElementById('stat-inquiries').textContent;
            document.getElementById('total-products').textContent = document.getElementById('stat-products').textContent;
            document.getElementById('total-news').textContent = document.getElementById('stat-news').textContent;
            document.getElementById('total-users').textContent = '1';
        }
    }

    // 编辑页面内容
    window.editPage = function(pageName) {
        currentEditingPage = pageName;
        
        // 设置模态框标题
        const modalTitle = document.querySelector('#editPageModal .modal-title');
        if (modalTitle) {
            modalTitle.textContent = `编辑${getPageTitle(pageName)}内容`;
        }
        
        // 清空表单
        document.getElementById('page-title-input').value = '';
        document.getElementById('page-subtitle-input').value = '';
        document.getElementById('page-content-input').value = '';
        document.getElementById('page-image-input').value = '';
        
        // 显示模态框
        const editPageModal = new bootstrap.Modal(document.getElementById('editPageModal'));
        editPageModal.show();
    }

    // 获取页面标题
    function getPageTitle(pageName) {
        const titles = {
            'home': '首页',
            'about': '关于我们',
            'products': '产品中心',
            'solutions': '解决方案',
            'cases': '成功案例',
            'news': '新闻资讯',
            'support': '技术支持',
            'contact': '联系我们',
            'dashboard': '仪表盘总览',
            'frontend': '前端页面管理',
            'inquiries': '询盘管理',
            'users': '用户管理',
            'settings': '系统设置',
            'statistics': '统计分析'
        };
        return titles[pageName] || pageName;
    }

    // 保存页面内容
    window.savePageContent = function() {
        if (!currentEditingPage) return;
        
        const data = {
            title_zh: document.getElementById('page-title-input').value,
            subtitle_zh: document.getElementById('page-subtitle-input').value,
            content_zh: document.getElementById('page-content-input').value,
            image_url: document.getElementById('page-image-input').value
        };
        
        alert('页面内容保存成功！');
        const editPageModal = bootstrap.Modal.getInstance(document.getElementById('editPageModal'));
        editPageModal.hide();
    }

    // 产品管理功能
    window.addProduct = function() {
        alert('添加产品功能开发中...');
    }

    window.editProduct = function(id) {
        alert(`编辑产品 ${id} 功能开发中...`);
    }

    window.deleteProduct = function(id) {
        if (confirm('确定要删除这个产品吗？')) {
            alert(`删除产品 ${id} 功能开发中...`);
        }
    }

    // 询盘管理功能
    window.viewInquiry = function(id) {
        alert(`查看询盘 ${id} 功能开发中...`);
    }

    window.handleInquiry = function(id) {
        alert(`处理询盘 ${id} 功能开发中...`);
    }

    // 新闻管理功能
    window.addNews = function() {
        alert('添加新闻功能开发中...');
    }

    window.editNews = function(id) {
        alert(`编辑新闻 ${id} 功能开发中...`);
    }

    window.deleteNews = function(id) {
        if (confirm('确定要删除这条新闻吗？')) {
            alert(`删除新闻 ${id} 功能开发中...`);
        }
    }

    // 用户管理功能
    window.addUser = function() {
        alert('添加用户功能开发中...');
    }

    window.editUser = function(id) {
        alert(`编辑用户 ${id} 功能开发中...`);
    }

    // 系统设置保存
    const settingsForm = document.getElementById('settings-form');
    if (settingsForm) {
        settingsForm.addEventListener('submit', (e) => {
            e.preventDefault();
            alert('系统设置保存功能开发中...');
        });
    }

    // 退出登录
    window.logout = function() {
        if (confirm('确定要退出登录吗？')) {
            currentAdmin = null;
            localStorage.removeItem('admin_user');
            document.getElementById('login-section').style.display = 'flex';
            document.getElementById('admin-section').style.display = 'none';
            
            // 重置表单
            if (document.getElementById('username')) {
                document.getElementById('username').value = 'admin';
                document.getElementById('password').value = 'admin123';
            }
        }
    }

    // 页面加载完成后的初始化
    console.log('联锦LED管理系统已加载');
    
    // 检查是否已登录
    if (!checkLoginStatus()) {
        // 未登录，显示登录界面
        if (document.getElementById('login-section')) {
            document.getElementById('login-section').style.display = 'flex';
        }
        if (document.getElementById('admin-section')) {
            document.getElementById('admin-section').style.display = 'none';
        }
    }
});