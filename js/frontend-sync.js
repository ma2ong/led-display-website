/**
 * 前端页面实时同步组件
 * 负责监听数据变更并更新前端页面内容
 */

class FrontendSync {
    constructor() {
        this.isActive = false;
        this.syncInterval = null;
        this.lastDataVersion = 0;
        this.contentCache = new Map();
        this.init();
    }

    /**
     * 初始化同步组件
     */
    async init() {
        console.log('🔄 前端同步组件初始化中...');
        
        // 等待统一API准备就绪
        await this.waitForUnifiedAPI();
        
        // 开始监听数据变更
        this.startDataChangeListener();
        
        // 开始定期检查
        this.startPeriodicSync();
        
        // 初始加载页面内容
        await this.loadCurrentPageContent();
        
        this.isActive = true;
        console.log('✅ 前端同步组件已激活');
    }

    /**
     * 等待统一API准备就绪
     */
    async waitForUnifiedAPI() {
        return new Promise((resolve) => {
            const checkAPI = () => {
                if (window.unifiedDataAPI) {
                    resolve();
                } else {
                    setTimeout(checkAPI, 100);
                }
            };
            checkAPI();
        });
    }

    /**
     * 开始监听数据变更
     */
    startDataChangeListener() {
        // 监听自定义数据更新事件
        window.addEventListener('dataUpdated', (event) => {
            console.log('📢 前端收到数据更新通知:', event.detail);
            this.handleDataUpdate(event.detail);
        });

        // 监听localStorage变更
        window.addEventListener('storage', (event) => {
            if (event.key && event.key.includes('page_contents')) {
                console.log('📢 检测到页面内容变更:', event.key);
                this.loadCurrentPageContent();
            }
        });

        console.log('👂 数据变更监听器已启动');
    }

    /**
     * 处理数据更新
     */
    async handleDataUpdate(detail) {
        const { type, version } = detail;
        
        if (version && version > this.lastDataVersion) {
            this.lastDataVersion = version;
            
            switch (type) {
                case 'products':
                    await this.updateProductContent();
                    break;
                case 'news':
                    await this.updateNewsContent();
                    break;
                case 'page_content':
                    await this.loadCurrentPageContent();
                    break;
            }
        }
    }

    /**
     * 开始定期同步检查
     */
    startPeriodicSync() {
        // 每30秒检查一次数据版本
        this.syncInterval = setInterval(async () => {
            if (window.unifiedDataAPI) {
                const currentVersion = window.unifiedDataAPI.getDataVersion();
                if (currentVersion > this.lastDataVersion) {
                    console.log('🔄 检测到数据版本更新，开始同步...');
                    this.lastDataVersion = currentVersion;
                    await this.syncAllContent();
                }
            }
        }, 30000);
        
        console.log('⏰ 定期同步检查已启动 (30秒间隔)');
    }

    /**
     * 同步所有内容
     */
    async syncAllContent() {
        await Promise.all([
            this.loadCurrentPageContent(),
            this.updateProductContent(),
            this.updateNewsContent()
        ]);
        console.log('✅ 全部内容同步完成');
    }

    /**
     * 加载当前页面内容
     */
    async loadCurrentPageContent() {
        if (!window.unifiedDataAPI) return;

        try {
            const pageName = this.getCurrentPageName();
            const content = await window.unifiedDataAPI.getPageContent(pageName);
            
            if (content) {
                this.updatePageElements(content);
                console.log(`✅ ${pageName}页面内容已更新`);
            }
        } catch (error) {
            console.error('加载页面内容失败:', error);
        }
    }

    /**
     * 更新页面元素
     */
    updatePageElements(content) {
        const { title, subtitle, content: pageContent, image } = content;

        // 更新页面标题
        if (title) {
            // 更新document title
            document.title = title;
            
            // 更新页面中的标题元素
            const titleSelectors = [
                'h1.hero-title', 
                'h1.page-title', 
                '.hero-title', 
                '.page-title',
                'h1:first-of-type'
            ];
            
            titleSelectors.forEach(selector => {
                const element = document.querySelector(selector);
                if (element) {
                    element.textContent = title;
                }
            });
        }

        // 更新副标题
        if (subtitle) {
            const subtitleSelectors = [
                '.hero-subtitle', 
                '.page-subtitle', 
                '.lead',
                'p.hero-subtitle'
            ];
            
            subtitleSelectors.forEach(selector => {
                const element = document.querySelector(selector);
                if (element) {
                    element.textContent = subtitle;
                }
            });
        }

        // 更新页面内容
        if (pageContent) {
            const contentSelectors = [
                '.page-content', 
                '.content-text',
                '.hero-content p:not(.hero-subtitle)'
            ];
            
            contentSelectors.forEach(selector => {
                const element = document.querySelector(selector);
                if (element && !element.classList.contains('hero-subtitle')) {
                    element.textContent = pageContent;
                }
            });
        }

        // 更新背景图片
        if (image) {
            const imageSelectors = [
                '.hero-section',
                '.page-header',
                '.banner-section'
            ];
            
            imageSelectors.forEach(selector => {
                const element = document.querySelector(selector);
                if (element) {
                    element.style.backgroundImage = `url(${image})`;
                }
            });
        }

        // 添加更新动画
        this.addUpdateAnimation();
    }

    /**
     * 更新产品内容
     */
    async updateProductContent() {
        if (!window.unifiedDataAPI) return;

        try {
            const products = await window.unifiedDataAPI.getProducts();
            
            // 查找产品容器
            const productContainers = [
                '#products-grid',
                '.products-container',
                '.product-list'
            ];

            productContainers.forEach(selector => {
                const container = document.querySelector(selector);
                if (container) {
                    this.renderProductsInContainer(container, products);
                }
            });

            console.log(`✅ 产品内容已更新 (${products.length}个产品)`);
        } catch (error) {
            console.error('更新产品内容失败:', error);
        }
    }

    /**
     * 在容器中渲染产品
     */
    renderProductsInContainer(container, products) {
        const row = container.querySelector('.row') || container;
        
        if (products.length === 0) {
            row.innerHTML = '<div class="col-12 text-center py-5"><p class="text-muted">暂无产品数据</p></div>';
            return;
        }

        row.innerHTML = '';
        
        products.forEach((product, index) => {
            const productCard = this.createProductCard(product, index);
            row.appendChild(productCard);
        });

        // 重新初始化AOS动画
        if (window.AOS) {
            window.AOS.refresh();
        }
    }

    /**
     * 创建产品卡片
     */
    createProductCard(product, index) {
        const delay = (index % 3) * 100;
        
        const col = document.createElement('div');
        col.className = 'col-lg-4 col-md-6 mb-4';
        col.setAttribute('data-aos', 'fade-up');
        col.setAttribute('data-aos-delay', delay.toString());

        const categoryIcons = {
            'fine-pitch': 'fas fa-microscope text-primary',
            'outdoor': 'fas fa-sun text-warning', 
            'rental': 'fas fa-magic text-purple',
            'transparent': 'fas fa-eye text-info',
            'creative': 'fas fa-palette text-danger'
        };

        const iconClass = categoryIcons[product.category] || 'fas fa-tv text-primary';

        col.innerHTML = `
            <div class="card product-card h-100">
                <div class="card-img-container">
                    <div class="product-image bg-light d-flex align-items-center justify-content-center">
                        ${product.images ? 
                          `<img src="${product.images}" alt="${product.name_en || product.name}" class="img-fluid">` : 
                          `<i class="${iconClass} display-4"></i>`
                        }
                    </div>
                    <div class="card-overlay">
                        <a class="btn btn-primary" href="contact.html?product=${product.id}">
                            <i class="fas fa-phone me-2"></i>获取报价
                        </a>
                    </div>
                </div>
                <div class="card-body">
                    <h5 class="card-title">${product.name_en || product.name}</h5>
                    <p class="card-text">${product.description_en || product.description || '暂无描述'}</p>
                </div>
                <div class="card-footer">
                    <small class="text-muted">类别: ${product.category}</small>
                </div>
            </div>
        `;

        return col;
    }

    /**
     * 更新新闻内容
     */
    async updateNewsContent() {
        if (!window.unifiedDataAPI) return;

        try {
            const news = await window.unifiedDataAPI.getNews();
            
            const newsContainers = [
                '.news-container',
                '#news-list',
                '.news-grid'
            ];

            newsContainers.forEach(selector => {
                const container = document.querySelector(selector);
                if (container && news.length > 0) {
                    this.renderNewsInContainer(container, news.slice(0, 6)); // 最多显示6条
                }
            });

            console.log(`✅ 新闻内容已更新 (${news.length}条新闻)`);
        } catch (error) {
            console.error('更新新闻内容失败:', error);
        }
    }

    /**
     * 在容器中渲染新闻
     */
    renderNewsInContainer(container, news) {
        container.innerHTML = '';
        
        news.forEach((item, index) => {
            const newsCard = document.createElement('div');
            newsCard.className = 'col-md-6 col-lg-4 mb-4';
            newsCard.setAttribute('data-aos', 'fade-up');
            newsCard.setAttribute('data-aos-delay', (index * 100).toString());
            
            newsCard.innerHTML = `
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">${item.title}</h5>
                        <p class="card-text">${item.content ? item.content.substring(0, 100) + '...' : '暂无内容'}</p>
                        <small class="text-muted">作者: ${item.author || '未知'} | ${new Date(item.created_at).toLocaleDateString()}</small>
                    </div>
                </div>
            `;
            
            container.appendChild(newsCard);
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
     * 添加更新动画效果
     */
    addUpdateAnimation() {
        // 创建更新指示器
        const indicator = document.createElement('div');
        indicator.className = 'update-indicator';
        indicator.innerHTML = '✨ 内容已更新';
        indicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 10px 15px;
            border-radius: 25px;
            font-size: 14px;
            font-weight: bold;
            z-index: 10000;
            opacity: 0;
            transform: translateY(-20px);
            transition: all 0.3s ease;
        `;

        document.body.appendChild(indicator);

        // 显示动画
        setTimeout(() => {
            indicator.style.opacity = '1';
            indicator.style.transform = 'translateY(0)';
        }, 100);

        // 隐藏动画
        setTimeout(() => {
            indicator.style.opacity = '0';
            indicator.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                if (indicator.parentNode) {
                    indicator.parentNode.removeChild(indicator);
                }
            }, 300);
        }, 3000);
    }

    /**
     * 手动触发同步
     */
    async manualSync() {
        console.log('🔄 手动触发同步...');
        if (window.unifiedDataAPI) {
            await window.unifiedDataAPI.forceRefresh();
        }
        await this.syncAllContent();
    }

    /**
     * 销毁同步组件
     */
    destroy() {
        if (this.syncInterval) {
            clearInterval(this.syncInterval);
            this.syncInterval = null;
        }
        this.isActive = false;
        this.contentCache.clear();
        console.log('🛑 前端同步组件已停止');
    }
}

// 页面加载完成后自动初始化
document.addEventListener('DOMContentLoaded', () => {
    // 等待一段时间确保其他脚本加载完成
    setTimeout(() => {
        window.frontendSync = new FrontendSync();
        
        // 添加手动刷新按钮
        const refreshBtn = document.createElement('button');
        refreshBtn.innerHTML = '🔄';
        refreshBtn.title = '手动同步内容';
        refreshBtn.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            border: none;
            background: #007bff;
            color: white;
            cursor: pointer;
            z-index: 9999;
            font-size: 18px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        `;
        
        refreshBtn.addEventListener('click', () => {
            if (window.frontendSync) {
                window.frontendSync.manualSync();
            }
        });
        
        refreshBtn.addEventListener('mouseenter', () => {
            refreshBtn.style.transform = 'scale(1.1)';
        });
        
        refreshBtn.addEventListener('mouseleave', () => {
            refreshBtn.style.transform = 'scale(1)';
        });
        
        document.body.appendChild(refreshBtn);
    }, 1000);
});

console.log('📡 前端同步组件已加载');
