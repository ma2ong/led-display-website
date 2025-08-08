/**
 * 统一API连接器 - 支持Flask后端和Supabase后端切换
 * Unified API Connector - Supports switching between Flask backend and Supabase backend
 */

import supabase from '../lib/supabase.js';

class UnifiedAPI {
    constructor() {
        // 配置选项
        this.config = {
            useFlaskBackend: true, // 设置为true使用Flask后端，false使用Supabase
            flaskBaseURL: 'http://localhost:5003',
            retryAttempts: 3,
            retryDelay: 1000
        };
        
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5分钟缓存
    }

    /**
     * 检测Flask后端是否可用
     */
    async checkFlaskBackend() {
        try {
            const response = await fetch(`${this.config.flaskBaseURL}/api/settings`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });
            return response.ok;
        } catch (error) {
            console.warn('Flask后端不可用，切换到Supabase:', error);
            return false;
        }
    }

    /**
     * 自动选择后端
     */
    async autoSelectBackend() {
        if (this.config.useFlaskBackend) {
            const flaskAvailable = await this.checkFlaskBackend();
            if (!flaskAvailable) {
                console.log('自动切换到Supabase后端');
                this.config.useFlaskBackend = false;
            }
        }
    }

    /**
     * 通用请求方法
     */
    async request(endpoint, options = {}) {
        await this.autoSelectBackend();

        if (this.config.useFlaskBackend) {
            return this.flaskRequest(endpoint, options);
        } else {
            return this.supabaseRequest(endpoint, options);
        }
    }

    /**
     * Flask请求方法
     */
    async flaskRequest(endpoint, options = {}) {
        const url = `${this.config.flaskBaseURL}/api${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include'
        };

        const finalOptions = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, finalOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Flask API请求失败:', error);
            // 如果Flask失败，尝试切换到Supabase
            this.config.useFlaskBackend = false;
            return this.supabaseRequest(endpoint, options);
        }
    }

    /**
     * Supabase请求方法（备用）
     */
    async supabaseRequest(endpoint, options = {}) {
        try {
            // 根据endpoint路由到对应的Supabase操作
            switch (endpoint) {
                case '/products':
                    const { data: products, error: productsError } = await supabase
                        .from('products')
                        .select('*')
                        .eq('status', 'active')
                        .order('created_at', { ascending: false });
                    
                    if (productsError) throw productsError;
                    return { status: 'success', products: products || [] };

                case '/news':
                    const { data: news, error: newsError } = await supabase
                        .from('news')
                        .select('*')
                        .eq('status', 'published')
                        .order('created_at', { ascending: false });
                    
                    if (newsError) throw newsError;
                    return { status: 'success', news: news || [] };

                case '/contact':
                    if (options.method === 'POST') {
                        const formData = JSON.parse(options.body);
                        const { data, error } = await supabase
                            .from('inquiries')
                            .insert([formData])
                            .select();
                        
                        if (error) throw error;
                        return { status: 'success', message: '联系表单提交成功' };
                    }
                    break;

                default:
                    throw new Error(`Supabase不支持的端点: ${endpoint}`);
            }
        } catch (error) {
            console.error('Supabase API请求失败:', error);
            throw error;
        }
    }

    /**
     * 获取前端页面内容
     */
    async getFrontendContent(pageName) {
        const cacheKey = `frontend_${pageName}`;
        const cached = this.cache.get(cacheKey);
        
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.data;
        }

        try {
            const data = await this.request(`/frontend/${pageName}`);
            const contents = data.contents || [];
            
            // 更新缓存
            this.cache.set(cacheKey, {
                data: contents,
                timestamp: Date.now()
            });
            
            return contents;
        } catch (error) {
            console.error(`获取${pageName}页面内容失败:`, error);
            return [];
        }
    }

    /**
     * 获取产品列表
     */
    async getProducts() {
        try {
            const data = await this.request('/products');
            return data.products || [];
        } catch (error) {
            console.error('获取产品列表失败:', error);
            return [];
        }
    }

    /**
     * 获取新闻列表
     */
    async getNews() {
        try {
            const data = await this.request('/news');
            return data.news || [];
        } catch (error) {
            console.error('获取新闻列表失败:', error);
            return [];
        }
    }

    /**
     * 获取案例列表
     */
    async getCases() {
        try {
            const data = await this.request('/cases');
            return data.cases || [];
        } catch (error) {
            console.error('获取案例列表失败:', error);
            return [];
        }
    }

    /**
     * 获取解决方案列表
     */
    async getSolutions() {
        try {
            const data = await this.request('/solutions');
            return data.solutions || [];
        } catch (error) {
            console.error('获取解决方案列表失败:', error);
            return [];
        }
    }

    /**
     * 提交联系表单
     */
    async submitContact(formData) {
        try {
            const data = await this.request('/contact', {
                method: 'POST',
                body: JSON.stringify(formData)
            });
            return data;
        } catch (error) {
            console.error('提交联系表单失败:', error);
            throw error;
        }
    }

    /**
     * 获取系统设置
     */
    async getSettings() {
        try {
            const data = await this.request('/settings');
            return data.settings || {};
        } catch (error) {
            console.error('获取系统设置失败:', error);
            return {};
        }
    }

    /**
     * 清除缓存
     */
    clearCache() {
        this.cache.clear();
    }

    /**
     * 强制使用Flask后端
     */
    forceFlaskBackend() {
        this.config.useFlaskBackend = true;
    }

    /**
     * 强制使用Supabase后端
     */
    forceSupabaseBackend() {
        this.config.useFlaskBackend = false;
    }
}

// 创建全局统一API实例
window.unifiedAPI = new UnifiedAPI();

/**
 * 实时内容更新器
 */
class RealTimeContentUpdater {
    constructor() {
        this.api = window.unifiedAPI;
        this.updateInterval = 30000; // 30秒检查一次更新
        this.isUpdating = false;
    }

    /**
     * 开始实时更新
     */
    startRealTimeUpdates() {
        if (this.isUpdating) return;
        
        this.isUpdating = true;
        console.log('开始实时内容更新');
        
        // 立即执行一次更新
        this.updatePageContent();
        
        // 设置定时更新
        this.updateTimer = setInterval(() => {
            this.updatePageContent();
        }, this.updateInterval);
    }

    /**
     * 停止实时更新
     */
    stopRealTimeUpdates() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
        this.isUpdating = false;
        console.log('停止实时内容更新');
    }

    /**
     * 更新页面内容
     */
    async updatePageContent() {
        try {
            // 获取当前页面名称
            const pageName = this.getCurrentPageName();
            
            // 清除缓存以获取最新内容
            this.api.clearCache();
            
            // 获取最新内容
            const contents = await this.api.getFrontendContent(pageName);
            
            // 更新页面显示
            this.renderUpdatedContent(contents);
            
            console.log(`页面${pageName}内容已更新`);
        } catch (error) {
            console.error('更新页面内容失败:', error);
        }
    }

    /**
     * 获取当前页面名称
     */
    getCurrentPageName() {
        const path = window.location.pathname;
        let pageName = 'home';
        
        if (path.includes('about')) pageName = 'about';
        else if (path.includes('products')) pageName = 'products';
        else if (path.includes('solutions')) pageName = 'solutions';
        else if (path.includes('cases')) pageName = 'cases';
        else if (path.includes('news')) pageName = 'news';
        else if (path.includes('support')) pageName = 'support';
        else if (path.includes('contact')) pageName = 'contact';
        
        return pageName;
    }

    /**
     * 渲染更新的内容
     */
    renderUpdatedContent(contents) {
        contents.forEach(content => {
            const { section_name, title_zh, subtitle_zh, content_zh } = content;
            
            // 查找对应的DOM元素
            const targetElement = document.querySelector(`[data-section="${section_name}"]`) ||
                                 document.querySelector(`#${section_name}`) ||
                                 document.querySelector(`.${section_name}`);

            if (targetElement) {
                // 更新标题
                const titleElement = targetElement.querySelector('h1, h2, h3, .title');
                if (titleElement && title_zh) {
                    titleElement.textContent = title_zh;
                }

                // 更新副标题
                const subtitleElement = targetElement.querySelector('.subtitle, .lead');
                if (subtitleElement && subtitle_zh) {
                    subtitleElement.textContent = subtitle_zh;
                }

                // 更新内容
                const contentElement = targetElement.querySelector('p, .content');
                if (contentElement && content_zh) {
                    contentElement.textContent = content_zh;
                }
            }
        });
    }
}

// 创建全局实时更新器实例
window.realTimeUpdater = new RealTimeContentUpdater();

// 页面加载完成后自动开始实时更新
document.addEventListener('DOMContentLoaded', function() {
    // 延迟3秒后开始实时更新，避免与初始加载冲突
    setTimeout(() => {
        window.realTimeUpdater.startRealTimeUpdates();
    }, 3000);
});

// 页面卸载时停止实时更新
window.addEventListener('beforeunload', function() {
    if (window.realTimeUpdater) {
        window.realTimeUpdater.stopRealTimeUpdates();
    }
});

// 导出API类
export { UnifiedAPI, RealTimeContentUpdater };