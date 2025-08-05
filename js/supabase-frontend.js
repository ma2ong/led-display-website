/**
 * Supabase前端集成
 * 支持现代化的前后端联动
 */

// Supabase客户端配置
let supabaseClient = null;

// 初始化Supabase客户端
function initSupabase() {
    const supabaseUrl = window.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseKey = window.SUPABASE_ANON_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
    
    if (supabaseUrl && supabaseKey && typeof supabase !== 'undefined') {
        supabaseClient = supabase.createClient(supabaseUrl, supabaseKey);
        console.log('✅ Supabase客户端初始化成功');
        return true;
    } else {
        console.log('⚠️ Supabase配置未找到，使用传统API');
        return false;
    }
}

// API请求封装
class ModernAPI {
    constructor() {
        this.useSupabase = initSupabase();
        this.baseUrl = this.detectEnvironment();
    }

    detectEnvironment() {
        if (typeof window !== 'undefined') {
            const hostname = window.location.hostname;
            if (hostname === 'localhost' || hostname === '127.0.0.1') {
                return 'http://localhost:8080';
            } else if (hostname.includes('vercel.app')) {
                return window.location.origin;
            }
        }
        return '';
    }

    // 产品相关API
    async getProducts() {
        if (this.useSupabase && supabaseClient) {
            try {
                const { data, error } = await supabaseClient
                    .from('products')
                    .select('*')
                    .order('created_at', { ascending: false });
                
                if (error) throw error;
                return { status: 'success', data };
            } catch (error) {
                console.error('Supabase产品获取失败:', error);
                return this.fallbackToTraditionalAPI('/api/products');
            }
        } else {
            return this.fallbackToTraditionalAPI('/api/products');
        }
    }

    async getFeaturedProducts() {
        if (this.useSupabase && supabaseClient) {
            try {
                const { data, error } = await supabaseClient
                    .from('products')
                    .select('*')
                    .order('created_at', { ascending: false })
                    .limit(4);
                
                if (error) throw error;
                return { status: 'success', data };
            } catch (error) {
                console.error('Supabase特色产品获取失败:', error);
                return this.fallbackToTraditionalAPI('/api/products/featured');
            }
        } else {
            return this.fallbackToTraditionalAPI('/api/products/featured');
        }
    }

    // 新闻相关API
    async getLatestNews() {
        if (this.useSupabase && supabaseClient) {
            try {
                const { data, error } = await supabaseClient
                    .from('news')
                    .select('*')
                    .eq('status', 'published')
                    .order('created_at', { ascending: false })
                    .limit(3);
                
                if (error) throw error;
                return { status: 'success', data };
            } catch (error) {
                console.error('Supabase新闻获取失败:', error);
                return this.fallbackToTraditionalAPI('/api/news/latest');
            }
        } else {
            return this.fallbackToTraditionalAPI('/api/news/latest');
        }
    }

    // 联系表单提交
    async submitContact(formData) {
        if (this.useSupabase && supabaseClient) {
            try {
                const { data, error } = await supabaseClient
                    .from('inquiries')
                    .insert([{
                        name: formData.name,
                        email: formData.email,
                        phone: formData.phone || '',
                        company: formData.company || '',
                        message: formData.message
                    }])
                    .select();
                
                if (error) throw error;
                return { status: 'success', message: '询盘提交成功！', data };
            } catch (error) {
                console.error('Supabase联系表单提交失败:', error);
                return this.fallbackToTraditionalAPI('/api/contact', 'POST', formData);
            }
        } else {
            return this.fallbackToTraditionalAPI('/api/contact', 'POST', formData);
        }
    }

    // 获取统计数据
    async getStats() {
        if (this.useSupabase && supabaseClient) {
            try {
                const [products, inquiries, news] = await Promise.all([
                    supabaseClient.from('products').select('id', { count: 'exact' }),
                    supabaseClient.from('inquiries').select('id', { count: 'exact' }),
                    supabaseClient.from('news').select('id', { count: 'exact' }).eq('status', 'published')
                ]);

                return {
                    status: 'success',
                    data: {
                        products_count: products.count || 0,
                        inquiries_count: inquiries.count || 0,
                        news_count: news.count || 0,
                        last_updated: new Date().toISOString()
                    }
                };
            } catch (error) {
                console.error('Supabase统计数据获取失败:', error);
                return this.fallbackToTraditionalAPI('/api/stats');
            }
        } else {
            return this.fallbackToTraditionalAPI('/api/stats');
        }
    }

    // 健康检查
    async healthCheck() {
        if (this.useSupabase && supabaseClient) {
            try {
                const { data, error } = await supabaseClient
                    .from('products')
                    .select('id')
                    .limit(1);
                
                return {
                    status: 'success',
                    message: 'Supabase连接正常',
                    timestamp: new Date().toISOString(),
                    backend: 'Supabase'
                };
            } catch (error) {
                console.error('Supabase健康检查失败:', error);
                return this.fallbackToTraditionalAPI('/api/health');
            }
        } else {
            return this.fallbackToTraditionalAPI('/api/health');
        }
    }

    // 传统API回退
    async fallbackToTraditionalAPI(endpoint, method = 'GET', data = null) {
        try {
            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json',
                }
            };

            if (data && method !== 'GET') {
                options.body = JSON.stringify(data);
            }

            const response = await fetch(`${this.baseUrl}${endpoint}`, options);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('传统API请求失败:', error);
            return {
                status: 'error',
                message: error.message,
                backend: 'Traditional'
            };
        }
    }

    // 实时订阅功能
    subscribeToInquiries(callback) {
        if (this.useSupabase && supabaseClient) {
            return supabaseClient
                .channel('inquiries')
                .on('postgres_changes', 
                    { event: '*', schema: 'public', table: 'inquiries' }, 
                    callback
                )
                .subscribe();
        }
        return null;
    }

    subscribeToProducts(callback) {
        if (this.useSupabase && supabaseClient) {
            return supabaseClient
                .channel('products')
                .on('postgres_changes', 
                    { event: '*', schema: 'public', table: 'products' }, 
                    callback
                )
                .subscribe();
        }
        return null;
    }
}

// 全局API实例
const modernAPI = new ModernAPI();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 现代化前后端联动系统启动');
    console.log(`📡 后端类型: ${modernAPI.useSupabase ? 'Supabase' : 'Traditional'}`);
    console.log(`🌐 API地址: ${modernAPI.baseUrl}`);

    // 初始化页面功能
    initializePageFeatures();
});

// 初始化页面功能
function initializePageFeatures() {
    // 联系表单处理
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', handleContactForm);
    }

    // 产品询盘按钮
    const inquiryButtons = document.querySelectorAll('.inquiry-btn, .contact-btn');
    inquiryButtons.forEach(button => {
        button.addEventListener('click', handleProductInquiry);
    });

    // 加载动态内容
    loadDynamicContent();

    // 设置实时订阅
    setupRealTimeSubscriptions();
}

// 处理联系表单
async function handleContactForm(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData);
    
    // 显示加载状态
    const submitButton = event.target.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.textContent = '提交中...';
    submitButton.disabled = true;
    
    try {
        const result = await modernAPI.submitContact(data);
        
        if (result.status === 'success') {
            showNotification('感谢您的询盘！我们会尽快与您联系。', 'success');
            event.target.reset();
        } else {
            showNotification('提交失败，请稍后重试。', 'error');
        }
    } catch (error) {
        console.error('联系表单提交错误:', error);
        showNotification('网络错误，请稍后重试。', 'error');
    } finally {
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    }
}

// 处理产品询盘
function handleProductInquiry(event) {
    const productName = event.target.dataset.product || '产品询盘';
    const contactUrl = `contact.html?product=${encodeURIComponent(productName)}`;
    window.location.href = contactUrl;
}

// 加载动态内容
async function loadDynamicContent() {
    try {
        // 加载特色产品
        const productsResult = await modernAPI.getFeaturedProducts();
        if (productsResult.status === 'success') {
            updateFeaturedProducts(productsResult.data);
        }

        // 加载最新新闻
        const newsResult = await modernAPI.getLatestNews();
        if (newsResult.status === 'success') {
            updateLatestNews(newsResult.data);
        }

        // 加载统计数据
        const statsResult = await modernAPI.getStats();
        if (statsResult.status === 'success') {
            updateCompanyStats(statsResult.data);
        }

        // 健康检查
        const healthResult = await modernAPI.healthCheck();
        console.log('🔍 系统状态:', healthResult);

    } catch (error) {
        console.error('动态内容加载失败:', error);
    }
}

// 更新特色产品
function updateFeaturedProducts(products) {
    const container = document.querySelector('.featured-products');
    if (!container || !products.length) return;

    const productsHTML = products.map(product => `
        <div class="product-card">
            <img src="${product.image_url || '/assets/products/default.jpg'}" alt="${product.name}">
            <h3>${product.name}</h3>
            <p>${product.description}</p>
            <div class="price">¥${product.price}</div>
            <button class="inquiry-btn" data-product="${product.name}">立即询盘</button>
        </div>
    `).join('');

    container.innerHTML = productsHTML;
}

// 更新最新新闻
function updateLatestNews(news) {
    const container = document.querySelector('.latest-news');
    if (!container || !news.length) return;

    const newsHTML = news.map(item => `
        <div class="news-item">
            <h4>${item.title}</h4>
            <p>${item.content.substring(0, 100)}...</p>
            <small>发布时间: ${new Date(item.created_at).toLocaleDateString()}</small>
        </div>
    `).join('');

    container.innerHTML = newsHTML;
}

// 更新公司统计
function updateCompanyStats(stats) {
    const elements = {
        '.stat-products': stats.products_count,
        '.stat-inquiries': stats.inquiries_count,
        '.stat-news': stats.news_count
    };

    Object.entries(elements).forEach(([selector, value]) => {
        const element = document.querySelector(selector);
        if (element) {
            element.textContent = value;
        }
    });
}

// 设置实时订阅
function setupRealTimeSubscriptions() {
    if (modernAPI.useSupabase) {
        // 订阅询盘更新
        modernAPI.subscribeToInquiries((payload) => {
            console.log('📨 新询盘:', payload.new);
            showNotification('收到新询盘！', 'info');
        });

        // 订阅产品更新
        modernAPI.subscribeToProducts((payload) => {
            console.log('📦 产品更新:', payload.new);
            // 重新加载产品数据
            loadDynamicContent();
        });
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// 导出API实例供其他脚本使用
window.modernAPI = modernAPI;