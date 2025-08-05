/**
 * Frontend-Backend Data Synchronization
 * 前后端数据同步系统
 */

class FrontendSync {
    constructor() {
        this.apiBase = window.location.origin;
        this.syncInterval = 30000; // 30秒同步一次
        this.lastSync = 0;
        this.cache = new Map();
        this.init();
    }

    init() {
        console.log('🔄 Frontend-Backend Sync initialized');
        this.startAutoSync();
        this.bindEvents();
    }

    // 开始自动同步
    startAutoSync() {
        // 立即同步一次
        this.syncAllData();
        
        // 设置定时同步
        setInterval(() => {
            this.syncAllData();
        }, this.syncInterval);
    }

    // 同步所有数据
    async syncAllData() {
        try {
            console.log('🔄 Syncing data from backend...');
            
            // 同步产品数据
            await this.syncProducts();
            
            // 同步内容数据
            await this.syncContent();
            
            // 更新最后同步时间
            this.lastSync = Date.now();
            
            console.log('✅ Data sync completed');
        } catch (error) {
            console.warn('⚠️ Sync error:', error);
        }
    }

    // 同步产品数据
    async syncProducts() {
        try {
            const response = await fetch(`${this.apiBase}/api/products`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.cache.set('products', data.products);
                this.updateProductsDisplay(data.products);
            }
        } catch (error) {
            console.warn('Products sync error:', error);
        }
    }

    // 同步内容数据
    async syncContent() {
        try {
            const response = await fetch(`${this.apiBase}/api/content`);
            if (response.ok) {
                const data = await response.json();
                if (data.status === 'success') {
                    this.cache.set('content', data.content);
                    this.updateContentDisplay(data.content);
                }
            }
        } catch (error) {
            console.warn('Content sync error:', error);
        }
    }

    // 更新产品显示
    updateProductsDisplay(products) {
        // 更新首页产品展示
        this.updateHomepageProducts(products);
        
        // 更新产品页面
        this.updateProductsPage(products);
        
        // 更新各个产品分类页面
        this.updateCategoryPages(products);
    }

    // 更新首页产品展示
    updateHomepageProducts(products) {
        const productGrid = document.querySelector('.products-grid');
        const productCards = document.querySelector('.product-cards');
        const featuredProducts = document.querySelector('.featured-products');
        
        if (productGrid || productCards || featuredProducts) {
            const container = productGrid || productCards || featuredProducts;
            if (container && products.length > 0) {
                container.innerHTML = this.generateProductCards(products.slice(0, 6));
            }
        }
    }

    // 更新产品页面
    updateProductsPage(products) {
        if (window.location.pathname.includes('products.html')) {
            const productList = document.querySelector('.product-list');
            const productGrid = document.querySelector('.products-grid');
            
            if (productList || productGrid) {
                const container = productList || productGrid;
                container.innerHTML = this.generateProductList(products);
            }
        }
    }

    // 更新分类页面
    updateCategoryPages(products) {
        const categoryMap = {
            'fine-pitch.html': 'fine-pitch',
            'outdoor.html': 'outdoor',
            'rental.html': 'rental',
            'creative.html': 'creative',
            'transparent.html': 'transparent'
        };

        const currentPage = window.location.pathname.split('/').pop();
        const category = categoryMap[currentPage];

        if (category) {
            const categoryProducts = products.filter(p => p.category === category);
            const productContainer = document.querySelector('.category-products');
            const productGrid = document.querySelector('.products-grid');
            
            if (productContainer || productGrid) {
                const container = productContainer || productGrid;
                container.innerHTML = this.generateProductList(categoryProducts);
            }
        }
    }

    // 生成产品卡片HTML
    generateProductCards(products) {
        return products.map(product => `
            <div class="col-md-4 mb-4">
                <div class="card product-card h-100">
                    <img src="${product.images || 'assets/products/default.jpg'}" 
                         class="card-img-top" alt="${product.name_zh}" 
                         style="height: 200px; object-fit: cover;">
                    <div class="card-body">
                        <h5 class="card-title">${product.name_zh}</h5>
                        <p class="card-text">${product.description_zh || product.description_en || ''}</p>
                        <div class="product-features">
                            ${product.features ? product.features.split(',').map(f => 
                                `<span class="badge bg-primary me-1">${f.trim()}</span>`
                            ).join('') : ''}
                        </div>
                    </div>
                    <div class="card-footer">
                        <button class="btn btn-primary btn-sm" onclick="showProductDetails('${product.id}')">
                            查看详情
                        </button>
                        <button class="btn btn-outline-success btn-sm" onclick="requestQuote('${product.id}')">
                            询价
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // 生成产品列表HTML
    generateProductList(products) {
        return products.map(product => `
            <div class="row product-item mb-4 p-3 border rounded">
                <div class="col-md-3">
                    <img src="${product.images || 'assets/products/default.jpg'}" 
                         class="img-fluid rounded" alt="${product.name_zh}"
                         style="height: 150px; width: 100%; object-fit: cover;">
                </div>
                <div class="col-md-9">
                    <h4>${product.name_zh}</h4>
                    <h6 class="text-muted">${product.name_en}</h6>
                    <p class="text-muted">${product.description_zh || product.description_en || ''}</p>
                    
                    ${product.specifications ? `
                        <div class="specifications mb-2">
                            <strong>技术规格：</strong>
                            <span class="text-info">${product.specifications}</span>
                        </div>
                    ` : ''}
                    
                    ${product.features ? `
                        <div class="features mb-3">
                            ${product.features.split(',').map(f => 
                                `<span class="badge bg-success me-1">${f.trim()}</span>`
                            ).join('')}
                        </div>
                    ` : ''}
                    
                    <div class="product-actions">
                        <button class="btn btn-primary me-2" onclick="showProductDetails('${product.id}')">
                            <i class="fas fa-eye"></i> 查看详情
                        </button>
                        <button class="btn btn-success me-2" onclick="requestQuote('${product.id}')">
                            <i class="fas fa-quote-right"></i> 立即询价
                        </button>
                        <button class="btn btn-outline-info" onclick="downloadBrochure('${product.id}')">
                            <i class="fas fa-download"></i> 下载资料
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // 更新内容显示
    updateContentDisplay(content) {
        if (!content) return;

        // 更新公司信息
        if (content.company) {
            this.updateCompanyInfo(content.company);
        }

        // 更新新闻资讯
        if (content.news) {
            this.updateNewsDisplay(content.news);
        }

        // 更新案例展示
        if (content.cases) {
            this.updateCasesDisplay(content.cases);
        }
    }

    // 更新公司信息
    updateCompanyInfo(company) {
        const elements = {
            '.company-name': company.name,
            '.company-description': company.description,
            '.company-address': company.address,
            '.company-phone': company.phone,
            '.company-email': company.email
        };

        Object.entries(elements).forEach(([selector, value]) => {
            const element = document.querySelector(selector);
            if (element && value) {
                element.textContent = value;
            }
        });
    }

    // 绑定事件
    bindEvents() {
        // 监听页面可见性变化，页面重新可见时同步数据
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && Date.now() - this.lastSync > 60000) {
                this.syncAllData();
            }
        });

        // 监听网络状态变化
        window.addEventListener('online', () => {
            console.log('🌐 Network restored, syncing data...');
            this.syncAllData();
        });
    }

    // 获取缓存数据
    getCachedData(key) {
        return this.cache.get(key);
    }

    // 手动触发同步
    forcSync() {
        return this.syncAllData();
    }
}

// 产品详情显示
window.showProductDetails = function(productId) {
    const products = window.frontendSync?.getCachedData('products') || [];
    const product = products.find(p => p.id == productId);
    
    if (product) {
        // 创建模态框显示产品详情
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${product.name_zh}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <img src="${product.images || 'assets/products/default.jpg'}" 
                                     class="img-fluid rounded" alt="${product.name_zh}">
                            </div>
                            <div class="col-md-6">
                                <h6>${product.name_en}</h6>
                                <p>${product.description_zh || product.description_en || ''}</p>
                                
                                ${product.specifications ? `
                                    <div class="mb-3">
                                        <strong>技术规格：</strong><br>
                                        <span class="text-info">${product.specifications}</span>
                                    </div>
                                ` : ''}
                                
                                ${product.features ? `
                                    <div class="mb-3">
                                        <strong>产品特点：</strong><br>
                                        ${product.features.split(',').map(f => 
                                            `<span class="badge bg-success me-1 mb-1">${f.trim()}</span>`
                                        ).join('')}
                                    </div>
                                ` : ''}
                                
                                ${product.price ? `
                                    <div class="mb-3">
                                        <strong>参考价格：</strong>
                                        <span class="text-primary fs-5">¥${product.price}</span>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                        <button type="button" class="btn btn-success" onclick="requestQuote('${product.id}')">立即询价</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // 模态框关闭后移除元素
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }
};

// 询价功能
window.requestQuote = function(productId) {
    const products = window.frontendSync?.getCachedData('products') || [];
    const product = products.find(p => p.id == productId);
    
    if (product) {
        // 跳转到联系页面并预填产品信息
        const contactUrl = `contact.html?product=${encodeURIComponent(product.name_zh)}&id=${productId}`;
        window.location.href = contactUrl;
    }
};

// 下载资料功能
window.downloadBrochure = function(productId) {
    alert('产品资料下载功能开发中，请联系我们获取详细资料。');
};

// 初始化同步系统
document.addEventListener('DOMContentLoaded', function() {
    try {
        window.frontendSync = new FrontendSync();
        
        // 添加同步状态指示器
        const syncIndicator = document.createElement('div');
        syncIndicator.id = 'sync-indicator';
        syncIndicator.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: #28a745;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 12px;
            z-index: 9999;
            display: none;
        `;
        syncIndicator.innerHTML = '<i class="fas fa-sync-alt"></i> 数据已同步';
        document.body.appendChild(syncIndicator);
        
        // 显示同步指示器
        window.showSyncIndicator = function() {
            syncIndicator.style.display = 'block';
            setTimeout(() => {
                syncIndicator.style.display = 'none';
            }, 2000);
        };
        
    } catch (error) {
        console.warn('Frontend sync initialization error:', error);
    }
});

// 导出同步对象供其他脚本使用
window.FrontendSync = FrontendSync;