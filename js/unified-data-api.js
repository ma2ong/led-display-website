/**
 * 统一数据API管理器
 * 负责前后端数据的统一管理和同步
 */

class UnifiedDataAPI {
    constructor() {
        this.isSupabaseAvailable = false;
        this.dataVersion = Date.now(); // 数据版本控制
        this.eventListeners = new Map(); // 事件监听器
        this.cache = new Map(); // 本地缓存
        this.init();
    }

    /**
     * 初始化API
     */
    async init() {
        console.log('🚀 统一数据API初始化中...');
        
        // 检查Supabase可用性
        await this.checkSupabaseConnection();
        
        // 设置数据变更监听
        this.setupDataChangeListener();
        
        // 初始化数据同步
        this.syncInitialData();
        
        console.log('✅ 统一数据API初始化完成');
    }

    /**
     * 检查Supabase连接
     */
    async checkSupabaseConnection() {
        try {
            if (typeof supabase !== 'undefined') {
                // 测试连接
                const { data, error } = await supabase.from('products').select('count');
                this.isSupabaseAvailable = !error;
                console.log(this.isSupabaseAvailable ? '✅ Supabase连接正常' : '❌ Supabase连接失败');
            } else {
                this.isSupabaseAvailable = false;
                console.log('⚠️ Supabase客户端未加载，使用本地存储');
            }
        } catch (error) {
            this.isSupabaseAvailable = false;
            console.log('⚠️ Supabase不可用，使用本地存储模式');
        }
    }

    /**
     * 设置数据变更监听
     */
    setupDataChangeListener() {
        // 监听localStorage变更
        window.addEventListener('storage', (event) => {
            if (event.key && (event.key.includes('products') || event.key.includes('news') || event.key.includes('page_contents'))) {
                console.log('📢 检测到数据变更:', event.key);
                this.dataVersion = Date.now();
                this.clearCache();
                this.notifyDataChange(event.key);
            }
        });

        // 监听自定义数据更新事件
        window.addEventListener('dataUpdated', (event) => {
            console.log('📢 收到数据更新通知:', event.detail);
            this.dataVersion = Date.now();
            this.clearCache();
            this.notifyDataChange(event.detail.type);
        });
    }

    /**
     * 同步初始数据
     */
    async syncInitialData() {
        try {
            // 如果Supabase可用，同步本地数据到Supabase
            if (this.isSupabaseAvailable) {
                await this.syncLocalDataToSupabase();
            }
        } catch (error) {
            console.error('初始数据同步失败:', error);
        }
    }

    /**
     * 同步本地数据到Supabase
     */
    async syncLocalDataToSupabase() {
        console.log('🔄 开始同步本地数据到Supabase...');
        
        try {
            // 从content.json读取产品数据
            const response = await fetch('./data/content.json');
            const contentData = await response.json();
            
            if (contentData.products && contentData.products.length > 0) {
                // 检查Supabase中是否已有数据
                const { data: existingProducts } = await supabase.from('products').select('id');
                
                if (!existingProducts || existingProducts.length === 0) {
                    // 将产品数据同步到Supabase
                    const { error } = await supabase.from('products').insert(contentData.products);
                    if (error) {
                        console.error('同步产品数据失败:', error);
                    } else {
                        console.log('✅ 产品数据同步成功');
                    }
                }
            }
        } catch (error) {
            console.error('同步数据失败:', error);
        }
    }

    /**
     * 获取产品数据
     */
    async getProducts() {
        const cacheKey = 'products';
        
        // 检查缓存
        if (this.cache.has(cacheKey)) {
            console.log('📋 从缓存加载产品数据');
            return this.cache.get(cacheKey);
        }

        try {
            let products = [];

            // 优先使用Supabase数据
            if (this.isSupabaseAvailable) {
                console.log('🔗 从Supabase获取产品数据');
                const { data, error } = await supabase
                    .from('products')
                    .select('*')
                    .order('created_at', { ascending: false });
                
                if (!error && data) {
                    products = data;
                }
            }

            // 如果Supabase没有数据或不可用，从本地获取
            if (products.length === 0) {
                console.log('📁 从本地存储获取产品数据');
                
                // 先检查localStorage
                const localProducts = localStorage.getItem('admin_products');
                if (localProducts) {
                    products = JSON.parse(localProducts);
                } else {
                    // 从content.json获取
                    const response = await fetch('./data/content.json');
                    const contentData = await response.json();
                    products = contentData.products || [];
                }
            }

            // 缓存数据
            this.cache.set(cacheKey, products);
            console.log(`✅ 加载了${products.length}个产品`);
            
            return products;
        } catch (error) {
            console.error('获取产品数据失败:', error);
            return [];
        }
    }

    /**
     * 保存产品数据
     */
    async saveProducts(products) {
        try {
            // 保存到Supabase
            if (this.isSupabaseAvailable) {
                console.log('💾 保存产品数据到Supabase');
                // 这里需要根据实际情况决定是更新还是插入
                // 简化处理：先删除所有，再插入
                const { error: deleteError } = await supabase.from('products').delete().gte('id', 0);
                if (!deleteError) {
                    const { error: insertError } = await supabase.from('products').insert(products);
                    if (insertError) {
                        console.error('保存到Supabase失败:', insertError);
                    }
                }
            }

            // 保存到本地存储
            localStorage.setItem('admin_products', JSON.stringify(products));
            
            // 更新数据版本
            this.dataVersion = Date.now();
            this.cache.delete('products');
            
            // 通知数据变更
            this.triggerDataUpdate('products');
            
            console.log('✅ 产品数据保存成功');
            return true;
        } catch (error) {
            console.error('保存产品数据失败:', error);
            return false;
        }
    }

    /**
     * 获取新闻数据
     */
    async getNews() {
        const cacheKey = 'news';
        
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }

        try {
            let news = [];

            if (this.isSupabaseAvailable) {
                const { data, error } = await supabase
                    .from('news')
                    .select('*')
                    .order('created_at', { ascending: false });
                
                if (!error && data) {
                    news = data;
                }
            }

            if (news.length === 0) {
                const localNews = localStorage.getItem('admin_news');
                if (localNews) {
                    news = JSON.parse(localNews);
                }
            }

            this.cache.set(cacheKey, news);
            return news;
        } catch (error) {
            console.error('获取新闻数据失败:', error);
            return [];
        }
    }

    /**
     * 保存新闻数据
     */
    async saveNews(news) {
        try {
            if (this.isSupabaseAvailable) {
                const { error: deleteError } = await supabase.from('news').delete().gte('id', 0);
                if (!deleteError) {
                    const { error: insertError } = await supabase.from('news').insert(news);
                    if (insertError) {
                        console.error('保存新闻到Supabase失败:', insertError);
                    }
                }
            }

            localStorage.setItem('admin_news', JSON.stringify(news));
            this.dataVersion = Date.now();
            this.cache.delete('news');
            this.triggerDataUpdate('news');
            
            return true;
        } catch (error) {
            console.error('保存新闻数据失败:', error);
            return false;
        }
    }

    /**
     * 获取页面内容
     */
    async getPageContent(pageName) {
        const cacheKey = `page_${pageName}`;
        
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }

        try {
            const savedPages = JSON.parse(localStorage.getItem('page_contents') || '{}');
            const content = savedPages[pageName];
            
            if (content) {
                this.cache.set(cacheKey, content);
            }
            
            return content;
        } catch (error) {
            console.error('获取页面内容失败:', error);
            return null;
        }
    }

    /**
     * 保存页面内容
     */
    async savePageContent(pageName, content) {
        try {
            const savedPages = JSON.parse(localStorage.getItem('page_contents') || '{}');
            savedPages[pageName] = {
                ...content,
                updated_at: new Date().toISOString()
            };
            
            localStorage.setItem('page_contents', JSON.stringify(savedPages));
            
            this.dataVersion = Date.now();
            this.cache.delete(`page_${pageName}`);
            this.triggerDataUpdate('page_content');
            
            return true;
        } catch (error) {
            console.error('保存页面内容失败:', error);
            return false;
        }
    }

    /**
     * 触发数据更新事件
     */
    triggerDataUpdate(type) {
        const event = new CustomEvent('dataUpdated', {
            detail: { type, version: this.dataVersion }
        });
        window.dispatchEvent(event);
        console.log(`📡 触发数据更新事件: ${type}`);
    }

    /**
     * 通知数据变更
     */
    notifyDataChange(key) {
        if (this.eventListeners.has(key)) {
            const listeners = this.eventListeners.get(key);
            listeners.forEach(callback => {
                try {
                    callback();
                } catch (error) {
                    console.error('执行数据变更回调失败:', error);
                }
            });
        }
    }

    /**
     * 添加数据变更监听器
     */
    onDataChange(key, callback) {
        if (!this.eventListeners.has(key)) {
            this.eventListeners.set(key, []);
        }
        this.eventListeners.get(key).push(callback);
    }

    /**
     * 清除缓存
     */
    clearCache() {
        this.cache.clear();
        console.log('🧹 缓存已清除');
    }

    /**
     * 强制刷新数据
     */
    async forceRefresh() {
        this.clearCache();
        this.dataVersion = Date.now();
        console.log('🔄 强制刷新数据');
        
        // 通知所有监听器
        this.eventListeners.forEach((listeners, key) => {
            this.notifyDataChange(key);
        });
    }

    /**
     * 获取数据版本
     */
    getDataVersion() {
        return this.dataVersion;
    }
}

// 创建全局实例
window.unifiedDataAPI = new UnifiedDataAPI();

// 暴露给全局使用
window.UnifiedDataAPI = UnifiedDataAPI;

console.log('📦 统一数据API已加载');
