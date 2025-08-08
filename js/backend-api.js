/**
 * 后端API连接模块
 * Backend API Connection Module
 */

class BackendAPI {
    constructor() {
        // Flask后端地址
        this.baseURL = 'http://localhost:5003';
        this.apiURL = `${this.baseURL}/api`;
    }

    /**
     * 通用API请求方法
     */
    async request(endpoint, options = {}) {
        const url = endpoint.startsWith('/api') ? `${this.baseURL}${endpoint}` : `${this.apiURL}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include' // 包含session cookies
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
            console.error('API请求失败:', error);
            throw error;
        }
    }

    /**
     * 获取前端页面内容
     */
    async getFrontendContent(pageName) {
        try {
            const data = await this.request(`/frontend/${pageName}`);
            return data.contents || [];
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
}

// 创建全局API实例
window.backendAPI = new BackendAPI();

/**
 * 页面内容加载器
 */
class PageContentLoader {
    constructor() {
        this.api = window.backendAPI;
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5分钟缓存
    }

    /**
     * 加载页面内容并渲染
     */
    async loadPageContent(pageName) {
        try {
            // 检查缓存
            const cacheKey = `page_${pageName}`;
            const cached = this.cache.get(cacheKey);
            
            if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
                this.renderContent(cached.data);
                return;
            }

            // 从后端获取内容
            const contents = await this.api.getFrontendContent(pageName);
            
            // 更新缓存
            this.cache.set(cacheKey, {
                data: contents,
                timestamp: Date.now()
            });

            // 渲染内容
            this.renderContent(contents);
            
        } catch (error) {
            console.error(`加载${pageName}页面内容失败:`, error);
            this.renderFallbackContent();
        }
    }

    /**
     * 渲染内容到页面
     */
    renderContent(contents) {
        contents.forEach(content => {
            this.renderContentItem(content);
        });
    }

    /**
     * 渲染单个内容项
     */
    renderContentItem(content) {
        const { section_name, content_type, title_zh, subtitle_zh, content_zh, image_url } = content;
        
        // 根据section_name查找对应的DOM元素
        const targetElement = document.querySelector(`[data-section="${section_name}"]`) ||
                             document.querySelector(`#${section_name}`) ||
                             document.querySelector(`.${section_name}`);

        if (!targetElement) {
            console.warn(`未找到section: ${section_name}的目标元素`);
            return;
        }

        // 根据content_type渲染不同类型的内容
        switch (content_type) {
            case 'hero_section':
                this.renderHeroSection(targetElement, content);
                break;
            case 'text_content':
                this.renderTextContent(targetElement, content);
                break;
            case 'feature_list':
                this.renderFeatureList(targetElement, content);
                break;
            case 'product_categories':
                this.renderProductCategories(targetElement, content);
                break;
            default:
                this.renderGenericContent(targetElement, content);
        }
    }

    /**
     * 渲染Hero区域
     */
    renderHeroSection(element, content) {
        const titleElement = element.querySelector('h1, .hero-title');
        const subtitleElement = element.querySelector('h2, .hero-subtitle, .lead');
        const contentElement = element.querySelector('p, .hero-content');
        const imageElement = element.querySelector('img, .hero-image');

        if (titleElement && content.title_zh) {
            titleElement.textContent = content.title_zh;
        }
        if (subtitleElement && content.subtitle_zh) {
            subtitleElement.textContent = content.subtitle_zh;
        }
        if (contentElement && content.content_zh) {
            contentElement.textContent = content.content_zh;
        }
        if (imageElement && content.image_url) {
            imageElement.src = content.image_url;
        }
    }

    /**
     * 渲染文本内容
     */
    renderTextContent(element, content) {
        const titleElement = element.querySelector('h1, h2, h3, .title');
        const contentElement = element.querySelector('p, .content');

        if (titleElement && content.title_zh) {
            titleElement.textContent = content.title_zh;
        }
        if (contentElement && content.content_zh) {
            contentElement.textContent = content.content_zh;
        }
    }

    /**
     * 渲染特性列表
     */
    renderFeatureList(element, content) {
        // 实现特性列表渲染逻辑
        this.renderGenericContent(element, content);
    }

    /**
     * 渲染产品分类
     */
    renderProductCategories(element, content) {
        // 实现产品分类渲染逻辑
        this.renderGenericContent(element, content);
    }

    /**
     * 渲染通用内容
     */
    renderGenericContent(element, content) {
        if (content.title_zh) {
            const titleElement = element.querySelector('h1, h2, h3, .title') || element;
            titleElement.textContent = content.title_zh;
        }
    }

    /**
     * 渲染备用内容
     */
    renderFallbackContent() {
        console.log('使用备用内容渲染');
        // 可以在这里设置默认内容
    }

    /**
     * 清除缓存
     */
    clearCache() {
        this.cache.clear();
    }

    /**
     * 强制刷新页面内容
     */
    async refreshPageContent(pageName) {
        this.cache.delete(`page_${pageName}`);
        await this.loadPageContent(pageName);
    }
}

// 创建全局页面内容加载器实例
window.pageContentLoader = new PageContentLoader();

/**
 * 页面初始化时自动加载内容
 */
document.addEventListener('DOMContentLoaded', function() {
    // 根据当前页面URL确定页面名称
    const path = window.location.pathname;
    let pageName = 'home';
    
    if (path.includes('about')) pageName = 'about';
    else if (path.includes('products')) pageName = 'products';
    else if (path.includes('solutions')) pageName = 'solutions';
    else if (path.includes('cases')) pageName = 'cases';
    else if (path.includes('news')) pageName = 'news';
    else if (path.includes('support')) pageName = 'support';
    else if (path.includes('contact')) pageName = 'contact';
    
    // 加载页面内容
    window.pageContentLoader.loadPageContent(pageName);
});

// 导出API和加载器
export { BackendAPI, PageContentLoader };