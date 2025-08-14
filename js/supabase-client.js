/**
 * Supabase Client for Frontend
 * 用于前端直接连接Supabase的客户端
 */

// Supabase配置
const SUPABASE_URL = 'https://jirudzbqcxviytcmxegf.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y214ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4';

class SupabaseClient {
    constructor() {
        this.initialized = false;
        this.supabase = null;
        this.init();
    }

    async init() {
        try {
            // 检查是否已加载Supabase库
            if (typeof window.supabase !== 'undefined') {
                const { createClient } = window.supabase;
                this.supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
                this.initialized = true;
                console.log('✅ Supabase客户端初始化成功');
            } else {
                console.warn('⚠️ Supabase库未加载，使用API端点');
            }
        } catch (error) {
            console.error('❌ Supabase初始化失败:', error);
        }
    }

    // 获取产品列表
    async getProducts() {
        if (this.supabase) {
            try {
                const { data, error } = await this.supabase
                    .from('products')
                    .select('*')
                    .order('created_at', { ascending: false });
                
                if (error) throw error;
                return { status: 'success', products: data };
            } catch (error) {
                console.error('Supabase查询失败:', error);
                return this.getProductsViaAPI();
            }
        } else {
            return this.getProductsViaAPI();
        }
    }

    // 通过API获取产品
    async getProductsViaAPI() {
        try {
            const response = await fetch('/api/products');
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API请求失败:', error);
            return { status: 'error', message: error.message };
        }
    }

    // 获取特色产品
    async getFeaturedProducts() {
        if (this.supabase) {
            try {
                const { data, error } = await this.supabase
                    .from('products')
                    .select('*')
                    .eq('is_featured', true)
                    .limit(6)
                    .order('created_at', { ascending: false });
                
                if (error) throw error;
                return { status: 'success', products: data };
            } catch (error) {
                console.error('Supabase查询失败:', error);
                return { status: 'error', message: error.message };
            }
        }
        return { status: 'error', message: 'Supabase未初始化' };
    }

    // 获取新闻列表
    async getNews(limit = 10) {
        if (this.supabase) {
            try {
                const { data, error } = await this.supabase
                    .from('news')
                    .select('*')
                    .eq('status', 'published')
                    .limit(limit)
                    .order('created_at', { ascending: false });
                
                if (error) throw error;
                return { status: 'success', news: data };
            } catch (error) {
                console.error('Supabase查询失败:', error);
                return { status: 'error', message: error.message };
            }
        }
        return { status: 'error', message: 'Supabase未初始化' };
    }

    // 提交询盘
    async submitInquiry(inquiryData) {
        // 优先使用API端点，确保服务器端验证
        try {
            const response = await fetch('/api/contact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(inquiryData)
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('提交询盘失败:', error);
            
            // 如果API失败，尝试直接写入Supabase
            if (this.supabase) {
                try {
                    const { data, error } = await this.supabase
                        .from('inquiries')
                        .insert([{
                            ...inquiryData,
                            status: 'pending',
                            created_at: new Date().toISOString()
                        }])
                        .select();
                    
                    if (error) throw error;
                    return { status: 'success', message: '询盘提交成功' };
                } catch (supabaseError) {
                    return { status: 'error', message: supabaseError.message };
                }
            }
            
            return { status: 'error', message: error.message };
        }
    }

    // 健康检查
    async healthCheck() {
        const results = {
            api: false,
            supabase: false
        };

        // 检查API
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            results.api = data.status === 'ok';
        } catch (error) {
            console.log('API不可用:', error.message);
        }

        // 检查Supabase
        if (this.supabase) {
            try {
                const { error } = await this.supabase
                    .from('products')
                    .select('count')
                    .limit(1)
                    .single();
                
                results.supabase = !error;
            } catch (error) {
                console.log('Supabase不可用:', error.message);
            }
        }

        return results;
    }

    // 实时订阅（可选功能）
    subscribeToProducts(callback) {
        if (!this.supabase) return null;
        
        return this.supabase
            .channel('products-changes')
            .on('postgres_changes', 
                { event: '*', schema: 'public', table: 'products' },
                callback
            )
            .subscribe();
    }
}

// 创建全局实例
window.supabaseClient = new SupabaseClient();

// 导出给其他脚本使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SupabaseClient;
}
