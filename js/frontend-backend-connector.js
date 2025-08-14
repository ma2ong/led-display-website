/**
 * 前后端连接器 - 简化版本
 * Frontend-Backend Connector - Simplified Version
 */

class FrontendBackendConnector {
    constructor() {
        // 使用相对路径，自动适配部署环境
        this.apiURL = window.location.origin;
        this.isBackendAvailable = false;
        this.checkInterval = 30000; // 30秒检查一次
        this.init();
    }

    /**
     * 初始化连接器
     */
    async init() {
        await this.checkBackendConnection();
        this.startPeriodicCheck();
        this.setupPageContentLoader();
    }

    /**
     * 检查后端连接
     */
    async checkBackendConnection() {
        try {
            const response = await fetch(`${this.apiURL}/api/health`, {
                method: 'GET',
                headers: { 'Accept': 'application/json' }
            });
            this.isBackendAvailable = response.ok;
            
            if (this.isBackendAvailable) {
                console.log('✅ 后端连接成功');
                this.showConnectionStatus('connected');
            } else {
                console.log('❌ 后端连接失败');
                this.showConnectionStatus('disconnected');
            }
        } catch (error) {
            this.isBackendAvailable = false;
            console.log('❌ 后端不可用:', error.message);
            this.showConnectionStatus('disconnected');
        }
    }

    /**
     * 显示连接状态
     */
    showConnectionStatus(status) {
        // 创建状态指示器
        let statusIndicator = document.getElementById('backend-status');
        if (!statusIndicator) {
            statusIndicator = document.createElement('div');
            statusIndicator.id = 'backend-status';
            statusIndicator.style.cssText = `
                position: fixed;
                top: 10px;
                right: 10px;
                padding: 8px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
                z-index: 9999;
                transition: all 0.3s ease;
            `;
            document.body.appendChild(statusIndicator);
        }

        if (status === 'connected') {
            statusIndicator.innerHTML = '🟢 后端已连接';
            statusIndicator.style.backgroundColor = '#d4edda';
            statusIndicator.style.color = '#155724';
            statusIndicator.style.border = '1px solid #c3e6cb';
        } else {
            statusIndicator.innerHTML = '🔴 后端断开';
            statusIndicator.style.backgroundColor = '#f8d7da';
            statusIndicator.style.color = '#721c24';
            statusIndicator.style.border = '1px solid #f5c6cb';
        }
    }

    /**
     * 开始定期检查
     */
    startPeriodicCheck() {
        setInterval(() => {
            this.checkBackendConnection();
        }, this.checkInterval);
    }

    /**
     * 设置页面内容加载器
     */
    setupPageContentLoader() {
        // 为每个页面设置内容加载
        this.loadPageContent();
        
        // 设置产品加载器
        if (document.getElementById('products-grid')) {
            this.setupProductLoader();
        }

        // 设置新闻加载器
        if (document.querySelector('.news-container')) {
            this.setupNewsLoader();
        }

        // 设置联系表单
        if (document.getElementById('contact-form')) {
            this.setupContactForm();
        }
    }

    /**
     * 加载页面内容
     */
    async loadPageContent() {
        if (!this.isBackendAvailable) return;

        const pageName = this.getCurrentPageName();
        
        try {
            const response = await fetch(`${this.apiURL}/api/frontend/${pageName}`);
            const data = await response.json();
            
            if (data.status === 'success' && data.contents) {
                this.updatePageContent(data.contents);
                console.log(`✅ ${pageName}页面内容已更新`);
            }
        } catch (error) {
            console.error('加载页面内容失败:', error);
        }
    }

    /**
     * 更新页面内容
     */
    updatePageContent(contents) {
        contents.forEach(content => {
            const { section_name, title_zh, subtitle_zh, content_zh } = content;
            
            // 查找目标元素
            const selectors = [
                `[data-section="${section_name}"]`,
                `#${section_name}`,
                `.${section_name}`,
                `[data-content="${section_name}"]`
            ];
            
            let targetElement = null;
            for (const selector of selectors) {
                targetElement = document.querySelector(selector);
                if (targetElement) break;
            }

            if (targetElement) {
                // 更新标题
                const titleEl = targetElement.querySelector('h1, h2, h3, .title, .hero-title');
                if (titleEl && title_zh) {
                    titleEl.textContent = title_zh;
                }

                // 更新副标题
                const subtitleEl = targetElement.querySelector('.subtitle, .lead, .hero-subtitle');
                if (subtitleEl && subtitle_zh) {
                    subtitleEl.textContent = subtitle_zh;
                }

                // 更新内容
                const contentEl = targetElement.querySelector('p, .content, .description');
                if (contentEl && content_zh) {
                    contentEl.textContent = content_zh;
                }
            }
        });
    }

    /**
     * 设置产品加载器
     */
    async setupProductLoader() {
        if (!this.isBackendAvailable) return;

        try {
            const response = await fetch(`${this.apiURL}/api/products`);
            const data = await response.json();
            
            if (data.status === 'success' && data.products) {
                this.renderProducts(data.products);
                console.log(`✅ 加载了${data.products.length}个产品`);
            }
        } catch (error) {
            console.error('加载产品失败:', error);
        }
    }

    /**
     * 渲染产品
     */
    renderProducts(products) {
        const container = document.getElementById('products-grid');
        if (!container) return;

        const row = container.querySelector('.row') || container;
        row.innerHTML = '';

        products.forEach((product, index) => {
            const productCard = this.createProductCard(product, index);
            row.appendChild(productCard);
        });
    }

    /**
     * 创建产品卡片
     */
    createProductCard(product, index) {
        const col = document.createElement('div');
        col.className = 'col-lg-4 col-md-6 mb-4';
        
        col.innerHTML = `
            <div class="card h-100 product-card">
                <div class="card-body">
                    <h5 class="card-title">${product.name}</h5>
                    <p class="card-text">${product.description || '暂无描述'}</p>
                    <small class="text-muted">类别: ${product.category || '未分类'}</small>
                </div>
                <div class="card-footer">
                    <a href="contact.html?product=${product.id}" class="btn btn-primary btn-sm">
                        <i class="fas fa-phone me-1"></i>获取报价
                    </a>
                </div>
            </div>
        `;
        
        return col;
    }

    /**
     * 设置新闻加载器
     */
    async setupNewsLoader() {
        if (!this.isBackendAvailable) return;

        try {
            const response = await fetch(`${this.apiURL}/api/news`);
            const data = await response.json();
            
            if (data.status === 'success' && data.news) {
                this.renderNews(data.news);
                console.log(`✅ 加载了${data.news.length}条新闻`);
            }
        } catch (error) {
            console.error('加载新闻失败:', error);
        }
    }

    /**
     * 渲染新闻
     */
    renderNews(newsList) {
        const container = document.querySelector('.news-container, #news-list');
        if (!container) return;

        container.innerHTML = '';

        newsList.forEach(news => {
            const newsCard = document.createElement('div');
            newsCard.className = 'col-md-6 col-lg-4 mb-4';
            
            newsCard.innerHTML = `
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">${news.title}</h5>
                        <p class="card-text">${news.content ? news.content.substring(0, 100) + '...' : '暂无内容'}</p>
                        <small class="text-muted">作者: ${news.author || '未知'}</small>
                    </div>
                </div>
            `;
            
            container.appendChild(newsCard);
        });
    }

    /**
     * 设置联系表单
     */
    setupContactForm() {
        const form = document.getElementById('contact-form');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (!this.isBackendAvailable) {
                alert('后端服务不可用，请稍后再试');
                return;
            }

            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            try {
                const response = await fetch(`${this.apiURL}/api/contact`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                
                if (result.status === 'success') {
                    alert('联系表单提交成功！我们会尽快回复您。');
                    form.reset();
                } else {
                    alert('提交失败，请稍后再试。');
                }
            } catch (error) {
                console.error('提交联系表单失败:', error);
                alert('提交失败，请检查网络连接。');
            }
        });
    }

    /**
     * 获取当前页面名称
     */
    getCurrentPageName() {
        const path = window.location.pathname;
        const filename = path.split('/').pop() || 'index.html';
        
        if (filename === 'index.html' || filename === '') return 'home';
        if (filename.includes('about')) return 'about';
        if (filename.includes('products')) return 'products';
        if (filename.includes('solutions')) return 'solutions';
        if (filename.includes('cases')) return 'cases';
        if (filename.includes('news')) return 'news';
        if (filename.includes('support')) return 'support';
        if (filename.includes('contact')) return 'contact';
        
        return 'home';
    }

    /**
     * 手动刷新内容
     */
    async refreshContent() {
        await this.checkBackendConnection();
        if (this.isBackendAvailable) {
            await this.loadPageContent();
            console.log('✅ 内容已刷新');
        }
    }
}

// 页面加载完成后自动初始化
document.addEventListener('DOMContentLoaded', () => {
    window.frontendBackendConnector = new FrontendBackendConnector();
    
    // 添加手动刷新按钮（可选）
    const refreshBtn = document.createElement('button');
    refreshBtn.innerHTML = '🔄';
    refreshBtn.title = '刷新后端内容';
    refreshBtn.style.cssText = `
        position: fixed;
        top: 50px;
        right: 10px;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        border: none;
        background: #007bff;
        color: white;
        cursor: pointer;
        z-index: 9998;
        font-size: 16px;
    `;
    
    refreshBtn.addEventListener('click', () => {
        window.frontendBackendConnector.refreshContent();
    });
    
    document.body.appendChild(refreshBtn);
});
