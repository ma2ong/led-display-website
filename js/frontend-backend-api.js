/**
 * 统一的前后端API连接器 v2.0
 * 支持Vercel Serverless、Supabase和本地API
 * 最新更新：2024年01月 - 增强版本
 */

class FrontendBackendAPI {
    constructor() {
        this.version = '2.0.0';
        this.apiMode = 'auto'; // auto, vercel, supabase, local
        this.baseUrls = {
            vercel: this.getVercelUrl(),
            supabase: 'https://jirudzbqcxviytcmxegf.supabase.co',
            local: window.location.origin
        };
        
        this.supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y214ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4';
        
        this.supabase = null;
        this.requestCache = new Map();
        this.retryAttempts = 3;
        this.requestTimeout = 10000; // 10秒超时
        
        this.initSupabase();
        this.setupErrorHandling();
        
        console.log(`🔗 Frontend-Backend API连接器 v${this.version} 初始化完成`);
    }

    getVercelUrl() {
        // 检测是否在Vercel环境
        if (window.location.hostname.includes('vercel.app')) {
            return window.location.origin;
        }
        // 使用最新的Vercel部署URL - 2024年更新
        return 'https://codebuddy-led-website-latest.vercel.app';
    }

    setupErrorHandling() {
        // 全局错误处理
        window.addEventListener('unhandledrejection', (event) => {
            if (event.reason && event.reason.message && event.reason.message.includes('API')) {
                console.warn('🚨 API调用失败，切换到备用模式:', event.reason.message);
                this.apiMode = 'supabase';
            }
        });
    }

    initSupabase() {
        try {
            // 检查多种可能的Supabase加载方式
            const supabaseClient = window.supabase || 
                                   (typeof supabase !== 'undefined' ? supabase : null) ||
                                   (window.createClient ? window : null);
            
            if (supabaseClient && supabaseClient.createClient) {
                this.supabase = supabaseClient.createClient(this.baseUrls.supabase, this.supabaseKey);
                console.log('✅ Supabase客户端初始化成功');
            } else {
                console.log('⚠️ Supabase库未加载，使用备用模式');
            }
        } catch (error) {
            console.warn('⚠️ Supabase初始化失败:', error.message);
        }
    }

    // 增强的API检测系统
    async detectBestAPI() {
        console.log('🔍 检测最佳API模式...');
        
        const tests = [
            { 
                name: 'vercel', 
                test: () => this.testEndpoint(`${this.baseUrls.vercel}/api/health`, 'GET'),
                priority: 1
            },
            { 
                name: 'local', 
                test: () => this.testEndpoint(`${this.baseUrls.local}/api/health`, 'GET'),
                priority: 2
            },
            { 
                name: 'supabase', 
                test: () => this.testSupabase(),
                priority: 3
            }
        ];

        // 按优先级排序测试
        tests.sort((a, b) => a.priority - b.priority);

        for (const test of tests) {
            try {
                const result = await this.withTimeout(test.test(), 5000);
                if (result) {
                    this.apiMode = test.name;
                    console.log(`✅ 使用${test.name} API模式`);
                    localStorage.setItem('preferred_api_mode', test.name);
                    return test.name;
                }
            } catch (error) {
                console.log(`❌ ${test.name} API不可用:`, error.message);
            }
        }

        // 检查上次成功的模式
        const lastMode = localStorage.getItem('preferred_api_mode');
        if (lastMode && ['vercel', 'supabase', 'local'].includes(lastMode)) {
            this.apiMode = lastMode;
            console.log(`🔄 使用上次成功的${lastMode}模式`);
            return lastMode;
        }

        this.apiMode = 'supabase'; // 最终备用
        console.log('🔄 使用默认Supabase模式');
        return 'supabase';
    }

    // 超时包装器
    withTimeout(promise, timeoutMs) {
        return Promise.race([
            promise,
            new Promise((_, reject) => 
                setTimeout(() => reject(new Error('请求超时')), timeoutMs)
            )
        ]);
    }

    // 增强的端点测试
    async testEndpoint(url, method = 'GET') {
        try {
            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json'
                },
                mode: 'cors',
                cache: 'no-cache'
            });
            return response.ok || response.status < 500;
        } catch (error) {
            return false;
        }
    }

    async testSupabase() {
        if (!this.supabase) return false;
        try {
            const { data, error } = await this.supabase
                .from('products')
                .select('count', { count: 'exact', head: true })
                .limit(1);
            return !error;
        } catch (error) {
            console.log('Supabase测试失败:', error.message);
            return false;
        }
    }

    // 带缓存和重试的请求方法
    async makeRequest(key, requestFn, useCache = true) {
        // 检查缓存
        if (useCache && this.requestCache.has(key)) {
            const cached = this.requestCache.get(key);
            if (Date.now() - cached.timestamp < 300000) { // 5分钟缓存
                console.log(`📋 使用缓存数据: ${key}`);
                return cached.data;
            }
        }

        let lastError;
        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                const result = await this.withTimeout(requestFn(), this.requestTimeout);
                
                // 缓存成功结果
                if (useCache && result) {
                    this.requestCache.set(key, {
                        data: result,
                        timestamp: Date.now()
                    });
                }
                
                return result;
            } catch (error) {
                lastError = error;
                console.warn(`❌ 请求失败 (尝试 ${attempt}/${this.retryAttempts}):`, error.message);
                
                if (attempt < this.retryAttempts) {
                    await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
                }
            }
        }
        
        throw lastError;
    }

    // 获取产品数据
    async getProducts(category = null) {
        try {
            if (this.apiMode === 'auto') {
                await this.detectBestAPI();
            }

            switch (this.apiMode) {
                case 'vercel':
                    return await this.getProductsFromVercel(category);
                case 'local':
                    return await this.getProductsFromLocal(category);
                case 'supabase':
                default:
                    return await this.getProductsFromSupabase(category);
            }
        } catch (error) {
            console.error('获取产品数据失败:', error);
            return await this.getFallbackProducts(category);
        }
    }

    async getProductsFromVercel(category) {
        const url = category 
            ? `${this.baseUrls.vercel}/api/products?category=${category}`
            : `${this.baseUrls.vercel}/api/products`;
            
        const response = await fetch(url);
        const data = await response.json();
        return data.success ? data.data : [];
    }

    async getProductsFromLocal(category) {
        const url = category 
            ? `/api/products/category/${category}`
            : `/api/products`;
            
        const response = await fetch(url);
        return await response.json();
    }

    async getProductsFromSupabase(category) {
        if (!this.supabase) {
            throw new Error('Supabase client not initialized');
        }

        let query = this.supabase
            .from('products')
            .select('*')
            .eq('status', 'active')
            .order('created_at', { ascending: false });

        if (category) {
            query = query.eq('category', category);
        }

        const { data, error } = await query;
        
        if (error) {
            throw error;
        }

        return data || [];
    }

    // 备用静态产品数据
    async getFallbackProducts(category) {
        console.log('🔄 使用备用产品数据');
        
        const fallbackProducts = [
            {
                id: 1,
                name: 'Indoor LED Display P2.5',
                category: 'indoor',
                description: 'High-resolution indoor LED displays perfect for retail stores, corporate offices, conference rooms, and entertainment venues.',
                price: 8500.00,
                image_url: '/assets/products/indoor-p2.5.jpg',
                specifications: 'Pixel Pitch: 2.5mm\nBrightness: 800cd/㎡\nRefresh Rate: 3840Hz',
                features: ['Ultra-fine pixel pitch', 'Seamless splicing technology', 'Front and rear service access', 'High refresh rate']
            },
            {
                id: 2,
                name: 'Outdoor LED Display P10',
                category: 'outdoor',
                description: 'Weather-resistant outdoor LED displays designed for advertising billboards, sports stadiums, and public information systems.',
                price: 12000.00,
                image_url: '/assets/products/outdoor-p10.jpg',
                specifications: 'Pixel Pitch: 10mm\nBrightness: 6500cd/㎡\nProtection: IP65',
                features: ['High brightness up to 10,000 nits', 'IP65/IP67 waterproof rating', 'Anti-UV and corrosion resistant', 'Temperature range: -40°C to +60°C']
            },
            {
                id: 3,
                name: 'Rental LED Display P3.91',
                category: 'rental',
                description: 'Flexible and portable rental LED displays perfect for events, concerts, conferences, and temporary installations.',
                price: 9800.00,
                image_url: '/assets/products/rental-p3.91.jpg',
                specifications: 'Pixel Pitch: 3.91mm\nWeight: 6.5kg/㎡\nInstallation: Quick lock design',
                features: ['Lightweight aluminum cabinet design', 'Quick lock system for fast setup', 'Flight case packaging included', 'Tool-free assembly']
            },
            {
                id: 4,
                name: 'Transparent LED Display',
                category: 'transparent',
                description: 'Innovative transparent LED displays that maintain visibility while displaying content, perfect for retail windows and glass facades.',
                price: 15000.00,
                image_url: '/assets/products/transparent-led.jpg',
                specifications: 'Transparency: 70-90%\nWeight: 12kg/m²\nEnergy Efficient',
                features: ['70-90% transparency rate', 'Ultra-lightweight design (12kg/m²)', 'Easy maintenance from front/back', 'Energy-efficient LED technology']
            },
            {
                id: 5,
                name: 'Creative LED Display',
                category: 'creative',
                description: 'Custom-shaped LED displays including curved, spherical, and irregular shapes for unique architectural applications.',
                price: 18000.00,
                image_url: '/assets/products/creative-led.jpg',
                specifications: 'Custom shapes\nFlexible modules\n360° display capability',
                features: ['360° cylindrical displays', 'Flexible and bendable modules', 'Custom shapes and sizes', 'Interactive touch capabilities']
            },
            {
                id: 6,
                name: 'Fine Pitch LED Display',
                category: 'fine-pitch',
                description: 'Ultra-high resolution fine pitch LED displays for close viewing applications such as broadcast studios and command centers.',
                price: 25000.00,
                image_url: '/assets/products/fine-pitch.jpg',
                specifications: 'Pixel Pitch: P0.9-P1.5\nUltra HD resolution\nSeamless splicing',
                features: ['P0.9, P1.2, P1.5 pixel pitch options', 'Ultra-high resolution and clarity', 'Flicker-free technology', 'Wide color gamut support']
            }
        ];

        return category 
            ? fallbackProducts.filter(p => p.category === category)
            : fallbackProducts;
    }

    // 提交联系表单
    async submitContactForm(formData) {
        try {
            if (this.apiMode === 'auto') {
                await this.detectBestAPI();
            }

            switch (this.apiMode) {
                case 'vercel':
                    return await this.submitToVercel(formData);
                case 'local':
                    return await this.submitToLocal(formData);
                case 'supabase':
                default:
                    return await this.submitToSupabase(formData);
            }
        } catch (error) {
            console.error('提交表单失败:', error);
            // 备用方案：至少保存到localStorage
            this.saveToLocalStorage(formData);
            return { 
                success: true, 
                message: '表单已暂存，我们会尽快联系您！',
                fallback: true 
            };
        }
    }

    async submitToVercel(formData) {
        const response = await fetch(`${this.baseUrls.vercel}/api/contact`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        return await response.json();
    }

    async submitToLocal(formData) {
        const response = await fetch('/api/contact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        return await response.json();
    }

    async submitToSupabase(formData) {
        if (!this.supabase) {
            throw new Error('Supabase client not initialized');
        }

        const inquiryData = {
            name: `${formData.first_name} ${formData.last_name}`,
            email: formData.email,
            phone: formData.phone || null,
            company: formData.company || null,
            subject: formData.subject,
            message: formData.message,
            product_interest: formData.product || null,
            country: formData.country || null,
            newsletter: formData.newsletter || false,
            status: 'new',
            created_at: new Date().toISOString()
        };

        const { data, error } = await this.supabase
            .from('inquiries')
            .insert([inquiryData])
            .select();

        if (error) {
            throw error;
        }

        return {
            success: true,
            message: '感谢您的咨询！我们会在24小时内回复您。',
            data: data
        };
    }

    saveToLocalStorage(formData) {
        try {
            const savedForms = JSON.parse(localStorage.getItem('contact_forms') || '[]');
            savedForms.push({
                ...formData,
                submitted_at: new Date().toISOString(),
                id: Date.now()
            });
            localStorage.setItem('contact_forms', JSON.stringify(savedForms));
            console.log('📝 表单已保存到本地存储');
        } catch (error) {
            console.error('保存到本地存储失败:', error);
        }
    }

    // 获取最新新闻
    async getLatestNews(limit = 3) {
        try {
            if (this.supabase) {
                const { data, error } = await this.supabase
                    .from('news')
                    .select('*')
                    .eq('published', true)
                    .order('created_at', { ascending: false })
                    .limit(limit);

                if (!error && data.length > 0) {
                    return data;
                }
            }

            // 备用新闻数据
            return this.getFallbackNews(limit);
        } catch (error) {
            console.error('获取新闻失败:', error);
            return this.getFallbackNews(limit);
        }
    }

    getFallbackNews(limit) {
        const fallbackNews = [
            {
                id: 1,
                title: 'LED显示技术的最新发展趋势',
                content: '随着技术的不断进步，LED显示屏在分辨率、亮度和能效方面都有了显著提升...',
                summary: '探索LED显示技术的最新发展和未来趋势',
                image_url: '/assets/news/news-1.jpg',
                created_at: '2024-01-15T10:00:00Z'
            },
            {
                id: 2,
                title: '户外LED显示屏在智慧城市中的应用',
                content: '智慧城市建设中，户外LED显示屏发挥着越来越重要的作用...',
                summary: '了解LED显示屏如何助力智慧城市建设',
                image_url: '/assets/news/news-2.jpg',
                created_at: '2024-01-10T14:30:00Z'
            },
            {
                id: 3,
                title: '室内小间距LED显示屏市场前景分析',
                content: '随着显示技术的发展，小间距LED显示屏在会议室、展厅等场所的应用越来越广泛...',
                summary: '分析小间距LED显示屏的市场前景和应用场景',
                image_url: '/assets/news/news-3.jpg',
                created_at: '2024-01-05T09:15:00Z'
            }
        ];

        return fallbackNews.slice(0, limit);
    }

    // 获取公司统计数据
    async getCompanyStats() {
        return {
            total_projects: 1500,
            total_clients: 800,
            countries_served: 50,
            years_experience: 17
        };
    }

    // 健康检查
    async healthCheck() {
        const results = {
            vercel: false,
            local: false,
            supabase: false
        };

        // 测试Vercel
        try {
            const response = await fetch(`${this.baseUrls.vercel}`, { 
                method: 'HEAD', 
                mode: 'no-cors' 
            });
            results.vercel = true;
        } catch (error) {
            results.vercel = false;
        }

        // 测试本地
        try {
            const response = await fetch('/api/health', { method: 'GET' });
            results.local = response.ok;
        } catch (error) {
            results.local = false;
        }

        // 测试Supabase
        results.supabase = await this.testSupabase();

        return results;
    }
}

// 创建全局API实例
window.frontendBackendAPI = new FrontendBackendAPI();

// 为了兼容性，也创建简化的全局函数
window.loadProducts = async (category = null) => {
    return await window.frontendBackendAPI.getProducts(category);
};

window.submitContactForm = async (formData) => {
    return await window.frontendBackendAPI.submitContactForm(formData);
};

window.getLatestNews = async (limit = 3) => {
    return await window.frontendBackendAPI.getLatestNews(limit);
};

console.log('🚀 前后端API连接器加载完成');

export default FrontendBackendAPI;
