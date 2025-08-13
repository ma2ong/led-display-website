// 初始化Supabase数据库
import { supabase } from './supabase-admin.js'

async function initSupabaseDatabase() {
    try {
        console.log('开始初始化Supabase数据库...')
        
        // 1. 创建admin_users表（如果不存在）
        const { data: adminUsersExists } = await supabase
            .from('admin_users')
            .select('count')
            .limit(1)
            .single()
            
        if (!adminUsersExists) {
            // 创建默认管理员用户
            const { data: authUser, error: authError } = await supabase.auth.signUp({
                email: 'admin@admin.com',
                password: 'admin123'
            })
            
            if (authError) {
                console.error('创建默认管理员用户身份验证失败:', authError)
            } else {
                console.log('默认管理员用户身份验证已创建')
                
                // 创建admin_users表并插入默认管理员
                const { error: insertUserError } = await supabase
                    .from('admin_users')
                    .insert([
                        {
                            username: 'admin',
                            email: 'admin@admin.com',
                            role: 'admin',
                            status: 'active'
                        }
                    ])
                    
                if (insertUserError) {
                    console.error('创建默认管理员用户记录失败:', insertUserError)
                } else {
                    console.log('默认管理员用户记录已创建')
                }
            }
        } else {
            console.log('admin_users表已存在')
        }
        
        // 2. 创建products表（如果不存在）
        const { data: productsExists } = await supabase
            .from('products')
            .select('count')
            .limit(1)
            .single()
            
        if (!productsExists) {
            // 创建示例产品数据
            const sampleProducts = [
                {
                    name: 'P2.5室内全彩LED显示屏',
                    description: '高清P2.5室内全彩LED显示屏，适用于会议室、展厅等场所。',
                    category: '室内显示屏',
                    price: 1200,
                    image_url: '/assets/products/indoor-p2.5.jpg',
                    status: 'active'
                },
                {
                    name: 'P4户外防水LED显示屏',
                    description: '高亮度P4户外防水LED显示屏，适用于广告牌、体育场馆等场所。',
                    category: '户外显示屏',
                    price: 1800,
                    image_url: '/assets/products/outdoor-p4.jpg',
                    status: 'active'
                },
                {
                    name: '透明LED玻璃屏',
                    description: '创新透明LED玻璃屏，适用于商场橱窗、展览展示等场所。',
                    category: '创意显示屏',
                    price: 2500,
                    image_url: '/assets/products/transparent.jpg',
                    status: 'active'
                }
            ]
            
            const { error: insertProductsError } = await supabase
                .from('products')
                .insert(sampleProducts)
                
            if (insertProductsError) {
                console.error('创建示例产品数据失败:', insertProductsError)
            } else {
                console.log('示例产品数据已创建')
            }
        } else {
            console.log('products表已存在')
        }
        
        // 3. 创建inquiries表（如果不存在）
        const { data: inquiriesExists } = await supabase
            .from('inquiries')
            .select('count')
            .limit(1)
            .single()
            
        if (!inquiriesExists) {
            // 创建示例询盘数据
            const sampleInquiries = [
                {
                    name: '张先生',
                    company: '上海展览有限公司',
                    phone: '13812345678',
                    email: 'zhang@example.com',
                    message: '我们需要一批P3.91室内LED显示屏用于展览活动，请提供报价。',
                    status: 'pending',
                    created_at: new Date().toISOString()
                },
                {
                    name: '李女士',
                    company: '广州广告传媒有限公司',
                    phone: '13987654321',
                    email: 'li@example.com',
                    message: '咨询户外P5全彩LED显示屏的价格和安装方案。',
                    status: 'handled',
                    created_at: new Date(Date.now() - 86400000).toISOString() // 昨天
                }
            ]
            
            const { error: insertInquiriesError } = await supabase
                .from('inquiries')
                .insert(sampleInquiries)
                
            if (insertInquiriesError) {
                console.error('创建示例询盘数据失败:', insertInquiriesError)
            } else {
                console.log('示例询盘数据已创建')
            }
        } else {
            console.log('inquiries表已存在')
        }
        
        // 4. 创建news表（如果不存在）
        const { data: newsExists } = await supabase
            .from('news')
            .select('count')
            .limit(1)
            .single()
            
        if (!newsExists) {
            // 创建示例新闻数据
            const sampleNews = [
                {
                    title: '联锦LED参加2025年广州国际LED展览会',
                    content: '我司将于2025年6月参加在广州举办的国际LED展览会，展位号A123，欢迎新老客户前来参观洽谈。',
                    category: '公司新闻',
                    author: 'admin',
                    status: 'published',
                    image_url: '/assets/news/exhibition.jpg',
                    created_at: new Date().toISOString()
                },
                {
                    title: '联锦LED推出新一代透明LED显示屏',
                    content: '我司最新研发的透明LED显示屏，透光率高达85%，色彩还原度达到95%以上，是商场橱窗、展览展示的理想选择。',
                    category: '产品新闻',
                    author: 'admin',
                    status: 'published',
                    image_url: '/assets/news/new-product.jpg',
                    created_at: new Date(Date.now() - 172800000).toISOString() // 2天前
                }
            ]
            
            const { error: insertNewsError } = await supabase
                .from('news')
                .insert(sampleNews)
                
            if (insertNewsError) {
                console.error('创建示例新闻数据失败:', insertNewsError)
            } else {
                console.log('示例新闻数据已创建')
            }
        } else {
            console.log('news表已存在')
        }
        
        console.log('Supabase数据库初始化完成')
        return { success: true }
    } catch (error) {
        console.error('初始化Supabase数据库失败:', error)
        return { success: false, error }
    }
}

// 导出初始化函数
export { initSupabaseDatabase }

// 自动执行初始化
document.addEventListener('DOMContentLoaded', () => {
    // 检查是否已经初始化过
    const initialized = localStorage.getItem('supabaseInitialized')
    
    if (!initialized) {
        initSupabaseDatabase().then(result => {
            if (result.success) {
                localStorage.setItem('supabaseInitialized', 'true')
                console.log('Supabase数据库初始化成功')
            }
        })
    }
})