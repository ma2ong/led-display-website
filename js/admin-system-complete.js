// 完整功能的管理系统脚本
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 完整管理系统已加载');
    
    // 全局变量
    let currentAdmin = null;
    let currentEditingPage = null;
    let currentEditingItem = null;
    let currentData = {
        products: [],
        inquiries: [],
        news: [],
        users: []
    };
    
    // 初始化前后端API连接
    let api = null;
    if (window.frontendBackendAPI) {
        api = window.frontendBackendAPI;
        console.log('✅ API连接器已就绪');
    } else {
        console.log('⚠️ API连接器未加载，使用本地模拟数据');
    }
    
    // 检查是否已登录
    function checkLoginStatus() {
        const adminUser = localStorage.getItem('admin_user');
        if (adminUser) {
            try {
                currentAdmin = JSON.parse(adminUser);
                console.log('✅ 登录状态检查成功:', currentAdmin);
                
                // 更新用户名显示
                const usernameElement = document.getElementById('admin-username');
                if (usernameElement) {
                    usernameElement.textContent = currentAdmin.username || 'admin';
                }
                
                // 显示管理界面
                showAdminInterface();
                loadDashboard();
                return true;
            } catch (e) {
                console.error('❌ 解析登录信息失败:', e);
                localStorage.removeItem('admin_user');
            }
        }
        return false;
    }
    
    // 显示管理界面
    function showAdminInterface() {
        const loginSection = document.getElementById('login-section');
        const adminSection = document.getElementById('admin-section');
        
        if (loginSection) loginSection.style.display = 'none';
        if (adminSection) adminSection.style.display = 'block';
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
            const pageTitle = document.getElementById('page-title');
            if (pageTitle) {
                pageTitle.textContent = getPageTitle(section);
            }
        });
    });
    
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
    
    // 加载仪表盘数据
    window.loadDashboard = async function() {
        try {
            console.log('📊 加载仪表盘数据...');
            
            // 更新统计数据
            const stats = {
                pages: 8,
                products: currentData.products.length,
                inquiries: currentData.inquiries.length,
                news: currentData.news.length
            };
            
            const elements = {
                'stat-pages': stats.pages,
                'stat-products': stats.products,
                'stat-inquiries': stats.inquiries,
                'stat-news': stats.news
            };
            
            Object.entries(elements).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) {
                    element.textContent = value.toString();
                }
            });
            
            // 加载最近询盘
            await loadRecentInquiries();
            
            console.log('✅ 仪表盘数据加载完成');
        } catch (error) {
            console.error('❌ 加载仪表盘失败:', error);
        }
    };
    
    // 加载最近询盘
    async function loadRecentInquiries() {
        const tbody = document.getElementById('recent-inquiries');
        if (!tbody) return;
        
        try {
            // 尝试从API获取数据
            if (api) {
                // API数据获取功能待实现
            }
            
            // 使用示例数据
            const recentInquiries = [
                {
                    id: 1,
                    name: '张先生',
                    email: 'zhang@example.com',
                    phone: '+86 138 0013 8000',
                    company: '科技有限公司',
                    subject: 'LED显示屏咨询',
                    status: 'new',
                    created_at: new Date().toISOString()
                }
            ];
            
            if (recentInquiries.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">暂无最近询盘</td></tr>';
                return;
            }
            
            tbody.innerHTML = recentInquiries.map(inquiry => `
                <tr>
                    <td>${inquiry.id}</td>
                    <td>${inquiry.name}</td>
                    <td>${inquiry.email}</td>
                    <td>${inquiry.company || '-'}</td>
                    <td><span class="badge bg-warning">新询盘</span></td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="viewInquiry(${inquiry.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success" onclick="handleInquiry(${inquiry.id})">
                            <i class="fas fa-check"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger py-4">加载失败</td></tr>';
        }
    }
    
    // 产品管理功能
    window.loadProducts = async function() {
        try {
            console.log('📦 加载产品数据...');
            
            const tbody = document.getElementById('products-table');
            if (!tbody) return;
            
            // 尝试从API获取产品数据
            if (api) {
                try {
                    const products = await api.getProducts();
                    currentData.products = products;
                } catch (error) {
                    console.log('使用备用产品数据');
                }
            }
            
            if (currentData.products.length === 0) {
                // 使用示例数据
                currentData.products = [
                    {
                        id: 1,
                        name: 'Indoor LED Display P2.5',
                        category: 'indoor',
                        price: 8500.00,
                        status: 'active',
                        created_at: '2024-01-15T10:00:00Z'
                    },
                    {
                        id: 2,
                        name: 'Outdoor LED Display P10',
                        category: 'outdoor',
                        price: 12000.00,
                        status: 'active',
                        created_at: '2024-01-10T14:30:00Z'
                    }
                ];
            }
            
            tbody.innerHTML = currentData.products.map(product => `
                <tr>
                    <td>${product.id}</td>
                    <td>${product.name}</td>
                    <td><span class="badge bg-info">${product.category}</span></td>
                    <td>¥${product.price ? product.price.toLocaleString() : '-'}</td>
                    <td><span class="badge bg-success">${product.status === 'active' ? '启用' : '禁用'}</span></td>
                    <td>${new Date(product.created_at).toLocaleDateString()}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="editProduct(${product.id})" title="编辑">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteProduct(${product.id})" title="删除">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
            
            console.log('✅ 产品数据加载完成');
        } catch (error) {
            console.error('❌ 加载产品失败:', error);
            const tbody = document.getElementById('products-table');
            if (tbody) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center text-danger py-4">加载产品数据失败</td></tr>';
            }
        }
    };
    
    // 询盘管理功能
    window.loadInquiries = async function() {
        try {
            console.log('📧 加载询盘数据...');
            
            const tbody = document.getElementById('inquiries-table');
            if (!tbody) return;
            
            // 使用示例数据
            if (currentData.inquiries.length === 0) {
                currentData.inquiries = [
                    {
                        id: 1,
                        name: '张先生',
                        email: 'zhang@example.com',
                        company: '科技有限公司',
                        phone: '+86 138 0013 8000',
                        status: 'new',
                        created_at: new Date().toISOString()
                    }
                ];
            }
            
            tbody.innerHTML = currentData.inquiries.map(inquiry => `
                <tr>
                    <td>${inquiry.id}</td>
                    <td>${inquiry.name}</td>
                    <td>${inquiry.email}</td>
                    <td>${inquiry.company || '-'}</td>
                    <td>${inquiry.phone || '-'}</td>
                    <td><span class="badge bg-warning">新询盘</span></td>
                    <td>${new Date(inquiry.created_at).toLocaleDateString()}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="viewInquiry(${inquiry.id})" title="查看">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success" onclick="handleInquiry(${inquiry.id})" title="处理">
                            <i class="fas fa-check"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
            
            console.log('✅ 询盘数据加载完成');
        } catch (error) {
            console.error('❌ 加载询盘失败:', error);
        }
    };
    
    // 新闻管理功能
    window.loadNews = async function() {
        try {
            console.log('📰 加载新闻数据...');
            
            const tbody = document.getElementById('news-table');
            if (!tbody) return;
            
            // 使用示例数据
            if (currentData.news.length === 0) {
                currentData.news = [
                    {
                        id: 1,
                        title: 'LED显示技术的最新发展趋势',
                        author: 'Admin',
                        status: 'published',
                        created_at: '2024-01-15T10:00:00Z'
                    }
                ];
            }
            
            tbody.innerHTML = currentData.news.map(news => `
                <tr>
                    <td>${news.id}</td>
                    <td>${news.title}</td>
                    <td>${news.author}</td>
                    <td><span class="badge bg-success">已发布</span></td>
                    <td>${new Date(news.created_at).toLocaleDateString()}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="editNews(${news.id})" title="编辑">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteNews(${news.id})" title="删除">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
            
            console.log('✅ 新闻数据加载完成');
        } catch (error) {
            console.error('❌ 加载新闻失败:', error);
        }
    };
    
    // 用户管理功能
    window.loadUsers = function() {
        try {
            console.log('👥 加载用户数据...');
            
            const tbody = document.getElementById('users-table');
            if (!tbody) return;
            
            tbody.innerHTML = `
                <tr>
                    <td>1</td>
                    <td>admin</td>
                    <td>admin@lianjinled.com</td>
                    <td><span class="badge bg-danger">超级管理员</span></td>
                    <td><span class="badge bg-success">活跃</span></td>
                    <td>${new Date().toLocaleDateString()}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="editUser(1)" title="编辑">
                            <i class="fas fa-edit"></i>
                        </button>
                    </td>
                </tr>
            `;
            
            console.log('✅ 用户数据加载完成');
        } catch (error) {
            console.error('❌ 加载用户失败:', error);
        }
    };
    
    // 统计数据
    window.loadStatistics = function() {
        try {
            console.log('📈 加载统计数据...');
            
            const elements = {
                'total-inquiries': currentData.inquiries.length,
                'total-products': currentData.products.length,
                'total-news': currentData.news.length,
                'total-users': 1
            };
            
            Object.entries(elements).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) {
                    element.textContent = value.toString();
                }
            });
            
            console.log('✅ 统计数据加载完成');
        } catch (error) {
            console.error('❌ 加载统计失败:', error);
        }
    };
    
    // 编辑页面内容
    window.editPage = function(pageName) {
        console.log(`📝 编辑页面: ${pageName}`);
        
        currentEditingPage = pageName;
        
        // 创建高级页面内容编辑界面
        showAdvancedPageEditor(pageName);
    };

    // 显示高级页面编辑器
    function showAdvancedPageEditor(pageName) {
        // 获取页面默认内容模板
        const contentTemplate = getPageContentTemplate(pageName);
        
        // 创建编辑器HTML
        const editorHTML = `
            <div class="modal fade" id="advancedPageModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">页面内容管理 - ${getPageDisplayName(pageName)}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body" style="max-height: 70vh; overflow-y: auto;">
                            <div class="alert alert-info">
                                <i class="fas fa-info-circle me-2"></i>
                                此功能允许你修改页面中的所有静态文字内容，修改后将实时更新到前端页面。
                            </div>
                            <form id="advancedPageForm">
                                ${generateContentFields(contentTemplate)}
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-warning" onclick="resetPageContent()">重置默认</button>
                            <button type="button" class="btn btn-primary" onclick="saveAdvancedPageContent()">保存并同步</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // 移除已存在的模态框
        const existingModal = document.getElementById('advancedPageModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // 添加新模态框
        document.body.insertAdjacentHTML('beforeend', editorHTML);
        
        // 加载现有内容
        loadExistingPageContent(pageName);
        
        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('advancedPageModal'));
        modal.show();
    }
    
    // 获取页面数据
    function getPageData(pageName) {
        const pageDefaults = {
            'home': {
                title: '首页 - 专业LED显示解决方案',
                subtitle: '联锦LED显示屏',
                content: '我们是专业的LED显示屏制造商，提供高质量的显示解决方案',
                image: '/assets/hero/hero-bg.jpg'
            },
            'products': {
                title: '产品中心 - LED显示屏系列',
                subtitle: '全系列LED显示产品',
                content: '涵盖室内、户外、租赁、透明、创意等各类LED显示屏产品',
                image: '/assets/products/products-banner.jpg'
            },
            'about': {
                title: '关于我们 - 专业LED显示厂商',
                subtitle: '17年专业经验',
                content: '联锦LED是专业的显示屏制造商，拥有17年行业经验',
                image: '/assets/about/company-bg.jpg'
            }
        };
        
        return pageDefaults[pageName] || {
            title: `${pageName}页面标题`,
            subtitle: `${pageName}页面副标题`,
            content: `${pageName}页面内容描述`,
            image: '/assets/default-bg.jpg'
        };
    }
    
    // 获取页面显示名称
    function getPageDisplayName(pageName) {
        const names = {
            'home': '首页',
            'about': '关于我们',
            'products': '产品中心',
            'solutions': '解决方案',
            'cases': '成功案例',
            'news': '新闻资讯',
            'support': '技术支持',
            'contact': '联系我们'
        };
        return names[pageName] || pageName;
    }
    
    // 保存页面内容
    window.savePageContent = async function() {
        if (!currentEditingPage) return;
        
        const data = {
            page: currentEditingPage,
            title: document.getElementById('page-title-input').value,
            subtitle: document.getElementById('page-subtitle-input').value,
            content: document.getElementById('page-content-input').value,
            image: document.getElementById('page-image-input').value
        };
        
        // 使用统一API保存
        if (window.unifiedDataAPI) {
            const success = await window.unifiedDataAPI.savePageContent(currentEditingPage, data);
            if (success) {
                console.log('✅ 页面内容保存成功:', data);
                alert(`${getPageDisplayName(currentEditingPage)}内容保存成功！`);
            } else {
                alert('保存失败，请重试！');
                return;
            }
        } else {
            // 降级到原来的方式
            const savedPages = JSON.parse(localStorage.getItem('page_contents') || '{}');
            savedPages[currentEditingPage] = { ...data, updated_at: new Date().toISOString() };
            localStorage.setItem('page_contents', JSON.stringify(savedPages));
            alert(`${getPageDisplayName(currentEditingPage)}内容保存成功！`);
        }
        
        const editPageModal = bootstrap.Modal.getInstance(document.getElementById('editPageModal'));
        if (editPageModal) {
            editPageModal.hide();
        }
    };
    
    // 产品管理功能
    window.addProduct = function() {
        console.log('➕ 添加新产品');
        currentEditingItem = null;
        showProductModal('添加产品');
    };
    
    window.editProduct = function(id) {
        console.log(`✏️ 编辑产品: ${id}`);
        const product = currentData.products.find(p => p.id === id);
        if (product) {
            currentEditingItem = product;
            showProductModal('编辑产品', product);
        }
    };
    
    window.deleteProduct = function(id) {
        if (confirm('确定要删除这个产品吗？')) {
            console.log(`🗑️ 删除产品: ${id}`);
            currentData.products = currentData.products.filter(p => p.id !== id);
            loadProducts();
            alert('产品删除成功！');
        }
    };
    
    // 显示产品编辑模态框
    function showProductModal(title, product = null) {
        // 创建简化的产品编辑界面
        const modalHTML = `
            <div class="modal fade" id="productModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="productForm">
                                <div class="mb-3">
                                    <label class="form-label">产品名称</label>
                                    <input type="text" class="form-control" id="productName" value="${product?.name || ''}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">产品分类</label>
                                    <select class="form-control" id="productCategory" required>
                                        <option value="indoor" ${product?.category === 'indoor' ? 'selected' : ''}>室内显示屏</option>
                                        <option value="outdoor" ${product?.category === 'outdoor' ? 'selected' : ''}>户外显示屏</option>
                                        <option value="rental" ${product?.category === 'rental' ? 'selected' : ''}>租赁显示屏</option>
                                        <option value="transparent" ${product?.category === 'transparent' ? 'selected' : ''}>透明显示屏</option>
                                        <option value="creative" ${product?.category === 'creative' ? 'selected' : ''}>创意显示屏</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">产品价格</label>
                                    <input type="number" class="form-control" id="productPrice" value="${product?.price || ''}" step="0.01">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">产品描述</label>
                                    <textarea class="form-control" id="productDescription" rows="3">${product?.description || ''}</textarea>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-primary" onclick="saveProduct()">保存</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // 移除已存在的模态框
        const existingModal = document.getElementById('productModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // 添加新模态框
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('productModal'));
        modal.show();
    }
    
    // 保存产品
    window.saveProduct = function() {
        const form = document.getElementById('productForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        const productData = {
            name: document.getElementById('productName').value,
            category: document.getElementById('productCategory').value,
            price: parseFloat(document.getElementById('productPrice').value) || 0,
            description: document.getElementById('productDescription').value,
            status: 'active',
            updated_at: new Date().toISOString()
        };
        
        if (currentEditingItem) {
            // 编辑现有产品
            const index = currentData.products.findIndex(p => p.id === currentEditingItem.id);
            if (index !== -1) {
                currentData.products[index] = { ...currentEditingItem, ...productData };
            }
        } else {
            // 添加新产品
            const newId = Math.max(...currentData.products.map(p => p.id), 0) + 1;
            currentData.products.push({
                id: newId,
                ...productData,
                created_at: new Date().toISOString()
            });
        }
        
        // 关闭模态框
        const modal = bootstrap.Modal.getInstance(document.getElementById('productModal'));
        if (modal) {
            modal.hide();
        }
        
        // 重新加载产品列表
        loadProducts();
        alert('产品保存成功！');
    };
    
    // 询盘管理功能
    window.viewInquiry = function(id) {
        const inquiry = currentData.inquiries.find(i => i.id === id);
        if (inquiry) {
            alert(`询盘详情:\n\n姓名: ${inquiry.name}\n邮箱: ${inquiry.email}\n公司: ${inquiry.company || '未填写'}\n电话: ${inquiry.phone || '未填写'}\n时间: ${new Date(inquiry.created_at).toLocaleString()}`);
        }
    };
    
    window.handleInquiry = function(id) {
        if (confirm(`确定将询盘 ${id} 标记为已处理吗？`)) {
            console.log(`✅ 处理询盘: ${id}`);
            const inquiry = currentData.inquiries.find(i => i.id === id);
            if (inquiry) {
                inquiry.status = 'handled';
                inquiry.handled_at = new Date().toISOString();
                loadInquiries();
                alert('询盘已标记为已处理！');
            }
        }
    };
    
    // 新闻管理功能
    window.addNews = function() {
        console.log('➕ 添加新闻');
        currentEditingItem = null;
        showNewsModal('添加新闻');
    };
    
    window.editNews = function(id) {
        console.log(`✏️ 编辑新闻: ${id}`);
        const news = currentData.news.find(n => n.id === id);
        if (news) {
            currentEditingItem = news;
            showNewsModal('编辑新闻', news);
        }
    };
    
    window.deleteNews = function(id) {
        if (confirm('确定要删除这条新闻吗？')) {
            console.log(`🗑️ 删除新闻: ${id}`);
            currentData.news = currentData.news.filter(n => n.id !== id);
            loadNews();
            alert('新闻删除成功！');
        }
    };
    
    // 显示新闻编辑模态框
    function showNewsModal(title, news = null) {
        const modalHTML = `
            <div class="modal fade" id="newsModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="newsForm">
                                <div class="mb-3">
                                    <label class="form-label">新闻标题</label>
                                    <input type="text" class="form-control" id="newsTitle" value="${news?.title || ''}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">作者</label>
                                    <input type="text" class="form-control" id="newsAuthor" value="${news?.author || 'Admin'}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">新闻内容</label>
                                    <textarea class="form-control" id="newsContent" rows="8">${news?.content || ''}</textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">新闻摘要</label>
                                    <textarea class="form-control" id="newsSummary" rows="3">${news?.summary || ''}</textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">封面图片URL</label>
                                    <input type="url" class="form-control" id="newsImage" value="${news?.image_url || ''}">
                                </div>
                                <div class="mb-3">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="newsPublished" ${news?.published ? 'checked' : ''}>
                                        <label class="form-check-label" for="newsPublished">
                                            立即发布
                                        </label>
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-primary" onclick="saveNews()">保存</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // 移除已存在的模态框
        const existingModal = document.getElementById('newsModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // 添加新模态框
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('newsModal'));
        modal.show();
    }
    
    // 保存新闻
    window.saveNews = function() {
        const form = document.getElementById('newsForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        const newsData = {
            title: document.getElementById('newsTitle').value,
            author: document.getElementById('newsAuthor').value,
            content: document.getElementById('newsContent').value,
            summary: document.getElementById('newsSummary').value,
            image_url: document.getElementById('newsImage').value,
            published: document.getElementById('newsPublished').checked,
            updated_at: new Date().toISOString()
        };
        
        if (currentEditingItem) {
            // 编辑现有新闻
            const index = currentData.news.findIndex(n => n.id === currentEditingItem.id);
            if (index !== -1) {
                currentData.news[index] = { ...currentEditingItem, ...newsData };
            }
        } else {
            // 添加新新闻
            const newId = Math.max(...currentData.news.map(n => n.id), 0) + 1;
            currentData.news.push({
                id: newId,
                ...newsData,
                created_at: new Date().toISOString()
            });
        }
        
        // 关闭模态框
        const modal = bootstrap.Modal.getInstance(document.getElementById('newsModal'));
        if (modal) {
            modal.hide();
        }
        
        // 重新加载新闻列表
        loadNews();
        alert('新闻保存成功！');
    };
    
    // 用户管理功能
    window.addUser = function() {
        alert('添加用户功能：\n\n为了系统安全，新用户添加需要超级管理员权限。\n请联系系统管理员进行用户管理。');
    };
    
    window.editUser = function(id) {
        alert('编辑用户功能：\n\n当前用户信息:\n- 用户名: admin\n- 角色: 超级管理员\n- 状态: 活跃\n\n密码修改请联系系统管理员。');
    };
    
    // 系统设置保存
    const settingsForm = document.getElementById('settings-form');
    if (settingsForm) {
        settingsForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const settings = {
                site_name: document.getElementById('site_name').value,
                contact_email: document.getElementById('contact_email').value,
                contact_phone: document.getElementById('contact_phone').value,
                company_address: document.getElementById('company_address').value,
                site_description: document.getElementById('site_description').value,
                updated_at: new Date().toISOString()
            };
            
            // 保存设置到localStorage
            localStorage.setItem('system_settings', JSON.stringify(settings));
            
            console.log('✅ 系统设置保存成功:', settings);
            alert('系统设置保存成功！');
        });
    }
    
    // 退出登录
    window.logout = function() {
        if (confirm('确定要退出登录吗？')) {
            console.log('👋 用户退出登录');
            
            currentAdmin = null;
            localStorage.removeItem('admin_user');

            // 跳转到登录页面
            window.location.href = 'admin/login.html';
        }
    };
    
    // 获取页面内容模板
    function getPageContentTemplate(pageName) {
        const templates = {
            'home': {
                hero_title: { label: '首页主标题', default: 'Professional LED Display Solutions' },
                hero_subtitle: { label: '首页副标题', default: 'Leading provider of high-quality LED displays for indoor, outdoor, and rental applications worldwide.' },
                section_title: { label: '产品区域标题', default: 'Our LED Display Solutions' },
                section_subtitle: { label: '产品区域副标题', default: 'Comprehensive range of professional LED displays for every application' },
                brand_name: { label: '品牌名称', default: 'Lianjin LED' }
            },
            'about': {
                hero_title: { label: '关于我们标题', default: 'About Lianjin LED Display Technology' },
                hero_subtitle: { label: '关于我们副标题', default: '17 Years of Excellence in LED Display Innovation' },
                company_description: { label: '公司介绍', default: 'Leading manufacturer of professional LED display solutions' }
            },
            'products': {
                hero_title: { label: '产品页标题', default: 'Professional LED Display Products' },
                hero_subtitle: { label: '产品页副标题', default: 'Complete Range of High-Quality LED Display Solutions' },
                section_title: { label: '产品列表标题', default: 'All Products' }
            },
            'contact': {
                hero_title: { label: '联系我们标题', default: 'Contact Us' },
                hero_subtitle: { label: '联系我们副标题', default: 'Get in Touch for Professional LED Display Solutions' }
            }
        };
        
        return templates[pageName] || {
            hero_title: { label: '页面主标题', default: `${pageName} Page Title` },
            hero_subtitle: { label: '页面副标题', default: `${pageName} Page Subtitle` }
        };
    }

    // 生成内容编辑字段
    function generateContentFields(template) {
        let html = '';
        Object.entries(template).forEach(([key, config]) => {
            html += `
                <div class="mb-4">
                    <label for="content-${key}" class="form-label fw-bold">
                        ${config.label}
                        <span class="text-muted">(语义标识: ${key})</span>
                    </label>
                    <textarea 
                        class="form-control" 
                        id="content-${key}" 
                        name="${key}"
                        rows="2" 
                        placeholder="默认值: ${config.default}"
                    ></textarea>
                    <small class="text-muted">默认内容: ${config.default}</small>
                </div>
            `;
        });
        return html;
    }

    // 加载现有页面内容
    async function loadExistingPageContent(pageName) {
        try {
            let savedContent = {};
            
            // 从统一API获取
            if (window.unifiedDataAPI) {
                const content = await window.unifiedDataAPI.getPageContent(pageName);
                if (content && content.elements) {
                    savedContent = content.elements;
                }
            } else {
                // 从 localStorage 获取
                const allContent = JSON.parse(localStorage.getItem('cms_content') || '{}');
                savedContent = allContent[pageName] || {};
            }
            
            // 填充表单字段
            Object.entries(savedContent).forEach(([key, value]) => {
                const field = document.getElementById(`content-${key}`);
                if (field && value) {
                    field.value = value;
                    field.style.backgroundColor = '#e8f5e8'; // 标记已修改
                }
            });
            
            console.log(`📄 加载了${pageName}页面的已保存内容`);
        } catch (error) {
            console.error('加载现有内容失败:', error);
        }
    }

    // 保存高级页面内容
    window.saveAdvancedPageContent = async function() {
        if (!currentEditingPage) return;
        
        const form = document.getElementById('advancedPageForm');
        const formData = new FormData(form);
        const contentData = {};
        
        // 收集表单数据
        for (let [key, value] of formData.entries()) {
            if (value.trim()) {
                contentData[key] = value.trim();
            }
        }
        
        try {
            let success = false;
            
            // 使用统一API保存
            if (window.unifiedDataAPI) {
                success = await window.unifiedDataAPI.savePageContent(currentEditingPage, {
                    elements: contentData,
                    updated_at: new Date().toISOString()
                });
            } else {
                // 使用localStorage保存
                const allContent = JSON.parse(localStorage.getItem('cms_content') || '{}');
                allContent[currentEditingPage] = contentData;
                localStorage.setItem('cms_content', JSON.stringify(allContent));
                success = true;
            }
            
            if (success) {
                // 触发同步事件
                const syncEvent = new CustomEvent('dataUpdated', {
                    detail: { type: 'page_content', version: Date.now() }
                });
                window.dispatchEvent(syncEvent);
                
                alert(`✅ ${getPageDisplayName(currentEditingPage)}页面内容保存成功！\n\n修改将在几秒内同步到前端页面。`);
                
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('advancedPageModal'));
                if (modal) {
                    modal.hide();
                }
            } else {
                throw new Error('保存失败');
            }
        } catch (error) {
            console.error('保存高级页面内容失败:', error);
            alert('❗ 保存失败，请重试！');
        }
    };

    // 重置页面内容
    window.resetPageContent = function() {
        if (!currentEditingPage) return;
        
        if (confirm(`确定要重置 ${getPageDisplayName(currentEditingPage)} 页面内容到默认值吗？`)) {
            // 清除表单字段
            const form = document.getElementById('advancedPageForm');
            if (form) {
                const textareas = form.querySelectorAll('textarea');
                textareas.forEach(textarea => {
                    textarea.value = '';
                    textarea.style.backgroundColor = '';
                });
            }
            
            // 清除保存的数据
            try {
                if (window.unifiedDataAPI) {
                    window.unifiedDataAPI.savePageContent(currentEditingPage, {
                        elements: {},
                        updated_at: new Date().toISOString()
                    });
                } else {
                    const allContent = JSON.parse(localStorage.getItem('cms_content') || '{}');
                    delete allContent[currentEditingPage];
                    localStorage.setItem('cms_content', JSON.stringify(allContent));
                }
                
                // 触发同步事件
                const syncEvent = new CustomEvent('dataUpdated', {
                    detail: { type: 'page_content', version: Date.now() }
                });
                window.dispatchEvent(syncEvent);
                
                alert('✅ 页面内容已重置到默认值！');
            } catch (error) {
                console.error('重置页面内容失败:', error);
                alert('❗ 重置失败，请重试！');
            }
        }
    };

    // 页面加载完成后的初始化
    console.log('🎉 联锦LED管理系统完整版已就绪');
    
    // 检查是否已登录
    if (checkLoginStatus()) {
        // 已登录，显示管理界面
        showAdminInterface();
        
        // 初始化显示仪表盘
        setTimeout(() => {
            document.querySelector('[data-section="dashboard"]')?.click();
        }, 100);
    } else {
        // 未登录，跳转到登录页面
        console.log('🔐 未登录，跳转到登录页面');
        window.location.href = 'admin/login.html';
    }
});
