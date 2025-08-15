/**
 * 内容管理器 - 前端动态内容加载和更新
 * 实现页面内容从Supabase动态加载，替换静态HTML内容
 */

class ContentManager {
    constructor() {
        this.supabaseUrl = 'https://jirudzbqcxviytcmxegf.supabase.co';
        this.supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y218ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4';
        this.supabase = null;
        this.currentPage = '';
        this.pageContents = {};
        this.siteSettings = {};
        this.isInitialized = false;
        this.contentCache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5分钟缓存
    }

    /**
     * 初始化内容管理器
     */
    async init() {
        try {
            console.log('🚀 初始化内容管理器...');
            
            // 初始化Supabase客户端
            if (typeof window.supabase !== 'undefined') {
                this.supabase = window.supabase.createClient(this.supabaseUrl, this.supabaseKey);
            } else if (window.supabaseClient) {
                this.supabase = window.supabaseClient;
            } else {
                console.warn('⚠️ Supabase客户端未找到，使用备用方案');
                return false;
            }

            // 获取当前页面名称
            this.currentPage = this.getCurrentPageName();
            
            // 加载网站设置
            await this.loadSiteSettings();
            
            // 加载页面内容
            await this.loadPageContents();
            
            // 应用内容到页面
            this.applyContentsToPage();
            
            // 设置实时监听
            this.setupRealtimeSubscription();
            
            this.isInitialized = true;
            console.log('✅ 内容管理器初始化完成');
            
            return true;
        } catch (error) {
            console.error('❌ 内容管理器初始化失败:', error);
            return false;
        }
    }

    /**
     * 获取当前页面名称
     */
    getCurrentPageName() {
        const path = window.location.pathname;
        const pageName = path.split('/').pop().replace('.html', '') || 'index';
        console.log('📄 当前页面:', pageName);
        return pageName;
    }

    /**
     * 加载网站设置
     */
    async loadSiteSettings() {
        try {
            // 检查缓存
            const cacheKey = 'site_settings';
            const cached = this.getFromCache(cacheKey);
            if (cached) {
                this.siteSettings = cached;
                return;
            }

            const { data, error } = await this.supabase
                .from('site_settings')
                .select('*')
                .eq('is_public', true);

            if (error) throw error;

            // 转换为键值对象
            this.siteSettings = {};
            data.forEach(setting => {
                this.siteSettings[setting.setting_key] = setting.setting_value;
            });

            // 保存到缓存
            this.saveToCache(cacheKey, this.siteSettings);
            
            console.log('✅ 加载了', Object.keys(this.siteSettings).length, '个网站设置');
        } catch (error) {
            console.error('加载网站设置失败:', error);
            // 使用默认设置
            this.siteSettings = this.getDefaultSettings();
        }
    }

    /**
     * 加载页面内容
     */
    async loadPageContents() {
        try {
            // 检查缓存
            const cacheKey = `page_contents_${this.currentPage}`;
            const cached = this.getFromCache(cacheKey);
            if (cached) {
                this.pageContents = cached;
                return;
            }

            const { data, error } = await this.supabase
                .from('page_contents')
                .select('*')
                .eq('page_name', this.currentPage)
                .eq('is_active', true);

            if (error) throw error;

            // 转换为键值对象
            this.pageContents = {};
            data.forEach(content => {
                this.pageContents[content.content_key] = {
                    value: content.content_value,
                    type: content.content_type
                };
            });

            // 保存到缓存
            this.saveToCache(cacheKey, this.pageContents);
            
            console.log('✅ 加载了', Object.keys(this.pageContents).length, '个页面内容项');
        } catch (error) {
            console.error('加载页面内容失败:', error);
            // 使用当前页面的默认内容
            this.pageContents = {};
        }
    }

    /**
     * 应用内容到页面
     */
    applyContentsToPage() {
        let updateCount = 0;

        // 应用页面特定内容
        Object.entries(this.pageContents).forEach(([key, content]) => {
            const elements = this.findElementsByContentKey(key);
            elements.forEach(element => {
                if (this.updateElement(element, content)) {
                    updateCount++;
                }
            });
        });

        // 应用全局设置
        Object.entries(this.siteSettings).forEach(([key, value]) => {
            const elements = this.findElementsBySettingKey(key);
            elements.forEach(element => {
                if (this.updateElement(element, { value, type: 'text' })) {
                    updateCount++;
                }
            });
        });

        if (updateCount > 0) {
            console.log('✨ 更新了', updateCount, '个页面元素');
            this.showUpdateNotification(updateCount);
        }
    }

    /**
     * 根据内容键查找元素
     */
    findElementsByContentKey(key) {
        const elements = [];
        
        // 1. 查找具有data-content属性的元素
        const dataElements = document.querySelectorAll(`[data-content="${key}"]`);
        elements.push(...dataElements);

        // 2. 根据键名智能查找元素
        const selectors = this.getSelectorsForKey(key);
        selectors.forEach(selector => {
            try {
                const found = document.querySelectorAll(selector);
                elements.push(...found);
            } catch (e) {
                // 忽略无效选择器
            }
        });

        return [...new Set(elements)]; // 去重
    }

    /**
     * 根据设置键查找元素
     */
    findElementsBySettingKey(key) {
        const elements = [];
        
        // 查找具有data-setting属性的元素
        const dataElements = document.querySelectorAll(`[data-setting="${key}"]`);
        elements.push(...dataElements);

        // 特殊处理某些设置
        if (key === 'site_name') {
            elements.push(...document.querySelectorAll('.navbar-brand span, .brand-name, .site-name'));
        } else if (key === 'footer_copyright') {
            elements.push(...document.querySelectorAll('footer .copyright, .footer-copyright'));
        }

        return [...new Set(elements)];
    }

    /**
     * 根据键名获取可能的选择器
     */
    getSelectorsForKey(key) {
        const selectors = [];
        
        // 通用映射
        const keyMappings = {
            'hero_title': ['.hero-title', 'h1.hero-title', '.hero-content h1'],
            'hero_subtitle': ['.hero-subtitle', 'p.hero-subtitle', '.hero-content p:first-of-type'],
            'hero_button_text': ['.hero-content .btn-primary', '.hero-buttons .btn:first-child'],
            'section_title': ['.section-title', 'h2.section-title'],
            'section_subtitle': ['.section-subtitle', 'p.section-subtitle'],
            'page_title': ['h1.page-title', '.page-header h1', 'main h1:first-of-type'],
            'page_description': ['.page-description', '.lead', 'main p:first-of-type']
        };

        if (keyMappings[key]) {
            selectors.push(...keyMappings[key]);
        }

        return selectors;
    }

    /**
     * 更新元素内容
     */
    updateElement(element, content) {
        if (!element || !content) return false;

        const oldContent = element.textContent || element.innerHTML;
        
        try {
            switch (content.type) {
                case 'html':
                    element.innerHTML = content.value;
                    break;
                case 'image':
                    if (element.tagName === 'IMG') {
                        element.src = content.value;
                    } else {
                        element.style.backgroundImage = `url(${content.value})`;
                    }
                    break;
                case 'url':
                    if (element.tagName === 'A') {
                        element.href = content.value;
                    }
                    break;
                default: // text
                    element.textContent = content.value;
            }

            // 标记为已更新
            element.setAttribute('data-cms-managed', 'true');
            element.setAttribute('data-cms-updated', new Date().toISOString());
            
            return oldContent !== content.value;
        } catch (error) {
            console.error('更新元素失败:', error);
            return false;
        }
    }

    /**
     * 设置实时订阅
     */
    setupRealtimeSubscription() {
        if (!this.supabase) return;

        // 订阅页面内容变化
        const contentChannel = this.supabase
            .channel('page-contents-changes')
            .on('postgres_changes', 
                { 
                    event: '*', 
                    schema: 'public', 
                    table: 'page_contents',
                    filter: `page_name=eq.${this.currentPage}`
                }, 
                (payload) => {
                    console.log('📡 收到内容更新:', payload);
                    this.handleContentUpdate(payload);
                }
            )
            .subscribe();

        // 订阅网站设置变化
        const settingsChannel = this.supabase
            .channel('site-settings-changes')
            .on('postgres_changes', 
                { 
                    event: '*', 
                    schema: 'public', 
                    table: 'site_settings'
                }, 
                (payload) => {
                    console.log('📡 收到设置更新:', payload);
                    this.handleSettingUpdate(payload);
                }
            )
            .subscribe();

        console.log('📡 实时订阅已设置');
    }

    /**
     * 处理内容更新
     */
    async handleContentUpdate(payload) {
        const { eventType, new: newRecord, old: oldRecord } = payload;

        switch (eventType) {
            case 'INSERT':
            case 'UPDATE':
                if (newRecord.is_active) {
                    this.pageContents[newRecord.content_key] = {
                        value: newRecord.content_value,
                        type: newRecord.content_type
                    };
                    
                    // 清除缓存
                    this.clearCache(`page_contents_${this.currentPage}`);
                    
                    // 更新页面
                    const elements = this.findElementsByContentKey(newRecord.content_key);
                    elements.forEach(element => {
                        this.updateElement(element, this.pageContents[newRecord.content_key]);
                    });
                    
                    this.showRealtimeUpdateNotification();
                }
                break;
            case 'DELETE':
                delete this.pageContents[oldRecord.content_key];
                this.clearCache(`page_contents_${this.currentPage}`);
                break;
        }
    }

    /**
     * 处理设置更新
     */
    handleSettingUpdate(payload) {
        const { eventType, new: newRecord, old: oldRecord } = payload;

        switch (eventType) {
            case 'INSERT':
            case 'UPDATE':
                if (newRecord.is_public) {
                    this.siteSettings[newRecord.setting_key] = newRecord.setting_value;
                    
                    // 清除缓存
                    this.clearCache('site_settings');
                    
                    // 更新页面
                    const elements = this.findElementsBySettingKey(newRecord.setting_key);
                    elements.forEach(element => {
                        this.updateElement(element, { 
                            value: newRecord.setting_value, 
                            type: newRecord.setting_type 
                        });
                    });
                    
                    this.showRealtimeUpdateNotification();
                }
                break;
            case 'DELETE':
                delete this.siteSettings[oldRecord.setting_key];
                this.clearCache('site_settings');
                break;
        }
    }

    /**
     * 缓存管理
     */
    saveToCache(key, data) {
        this.contentCache.set(key, {
            data: data,
            timestamp: Date.now()
        });
    }

    getFromCache(key) {
        const cached = this.contentCache.get(key);
        if (cached && (Date.now() - cached.timestamp < this.cacheTimeout)) {
            console.log('📦 使用缓存数据:', key);
            return cached.data;
        }
        return null;
    }

    clearCache(key) {
        if (key) {
            this.contentCache.delete(key);
        } else {
            this.contentCache.clear();
        }
    }

    /**
     * 显示更新通知
     */
    showUpdateNotification(count) {
        const notification = document.createElement('div');
        notification.className = 'cms-notification';
        notification.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>已从数据库加载 ${count} 个内容项</span>
        `;
        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            animation: slideInUp 0.3s ease;
            display: flex;
            align-items: center;
            gap: 10px;
        `;

        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutDown 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    /**
     * 显示实时更新通知
     */
    showRealtimeUpdateNotification() {
        const notification = document.createElement('div');
        notification.className = 'cms-realtime-notification';
        notification.innerHTML = `
            <i class="fas fa-sync fa-spin"></i>
            <span>内容已实时更新</span>
        `;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 10px 16px;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            z-index: 10000;
            animation: slideInRight 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        `;

        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    }

    /**
     * 获取默认设置
     */
    getDefaultSettings() {
        return {
            site_name: 'Lianjin LED',
            site_tagline: 'Professional LED Display Solutions',
            company_email: 'info@lianjinled.com',
            company_phone: '+86 123 4567 8900',
            company_address: 'Shenzhen, China',
            footer_copyright: '© 2024 Lianjin LED. All rights reserved.'
        };
    }

    /**
     * 手动刷新内容
     */
    async refresh() {
        console.log('🔄 手动刷新内容...');
        this.clearCache();
        await this.loadSiteSettings();
        await this.loadPageContents();
        this.applyContentsToPage();
    }
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInUp {
        from {
            transform: translateY(100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutDown {
        from {
            transform: translateY(0);
            opacity: 1;
        }
        to {
            transform: translateY(100%);
            opacity: 0;
        }
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    [data-cms-managed] {
        position: relative;
        transition: all 0.3s ease;
    }
    
    [data-cms-managed]:hover::after {
        content: '✏️ CMS管理';
        position: absolute;
        top: -25px;
        right: 0;
        background: rgba(0,0,0,0.8);
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        white-space: nowrap;
        pointer-events: none;
        z-index: 1000;
    }
`;
document.head.appendChild(style);

// 初始化内容管理器
const contentManager = new ContentManager();

// DOM加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        contentManager.init();
    });
} else {
    contentManager.init();
}

// 导出给全局使用
window.contentManager = contentManager;

console.log('📚 内容管理器模块已加载');
