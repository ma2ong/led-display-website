/**
 * Supabase配置文件
 * 用于Vercel + Supabase一键部署
 */

// 环境变量配置
const SUPABASE_CONFIG = {
    // 从环境变量或window对象获取配置
    url: process.env.NEXT_PUBLIC_SUPABASE_URL || window.SUPABASE_URL || '',
    anonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || window.SUPABASE_ANON_KEY || '',
    
    // 数据库表配置
    tables: {
        products: 'products',
        inquiries: 'inquiries', 
        news: 'news',
        users: 'users',
        quotes: 'quotes',
        cases: 'cases'
    },
    
    // RLS策略配置
    policies: {
        // 公开读取策略
        publicRead: ['products', 'news', 'cases'],
        // 需要认证的操作
        authRequired: ['inquiries', 'quotes'],
        // 管理员专用
        adminOnly: ['users']
    }
};

// 初始化Supabase客户端
let supabaseClient = null;

function initializeSupabase() {
    if (typeof supabase !== 'undefined' && SUPABASE_CONFIG.url && SUPABASE_CONFIG.anonKey) {
        try {
            supabaseClient = supabase.createClient(SUPABASE_CONFIG.url, SUPABASE_CONFIG.anonKey);
            console.log('✅ Supabase客户端初始化成功');
            return true;
        } catch (error) {
            console.error('❌ Supabase初始化失败:', error);
            return false;
        }
    } else {
        console.log('⚠️ Supabase配置未找到，使用传统API模式');
        return false;
    }
}

// 导出配置和客户端
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SUPABASE_CONFIG, initializeSupabase };
} else {
    window.SUPABASE_CONFIG = SUPABASE_CONFIG;
    window.initializeSupabase = initializeSupabase;
}