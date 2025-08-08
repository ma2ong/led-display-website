// Product Table Fix - 解决产品表写入失败问题
// 修复 HTTP 错误: 400 - 产品表写入失败

// Supabase 配置
const SUPABASE_URL = 'https://tfkzzgufbftlafsdyrmj.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRma3p6Z3VmYmZ0bGFmc2R5cm1qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQzODQxOTQsImV4cCI6MjA2OTk2MDE5NH0.z5VqNaBohG-9Kwm3thBnrgAca8bePxnbBamFCBiXoLY';

// 初始化 Supabase 客户端
const supabase = window.supabase?.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// 产品表结构验证
const PRODUCT_SCHEMA = {
    name: { type: 'string', required: true },
    category: { type: 'string', required: true },
    description: { type: 'string', required: false },
    price: { type: 'number', required: false },
    image_url: { type: 'string', required: false },
    specifications: { type: 'string', required: false }
};

// 验证产品数据格式
function validateProductData(productData) {
    const errors = [];
    
    for (const [field, rules] of Object.entries(PRODUCT_SCHEMA)) {
        const value = productData[field];
        
        // 检查必填字段
        if (rules.required && (!value || value.toString().trim() === '')) {
            errors.push(`${field} 是必填字段`);
            continue;
        }
        
        // 检查数据类型
        if (value !== null && value !== undefined && value !== '') {
            if (rules.type === 'string' && typeof value !== 'string') {
                errors.push(`${field} 必须是字符串类型`);
            } else if (rules.type === 'number' && isNaN(Number(value))) {
                errors.push(`${field} 必须是数字类型`);
            }
        }
    }
    
    return errors;
}

// 清理产品数据
function sanitizeProductData(productData) {
    const cleaned = {};
    
    for (const [field, rules] of Object.entries(PRODUCT_SCHEMA)) {
        let value = productData[field];
        
        if (value === null || value === undefined || value === '') {
            if (rules.required) {
                throw new Error(`必填字段 ${field} 不能为空`);
            }
            // 对于非必填字段，跳过空值
            continue;
        }
        
        // 数据类型转换
        if (rules.type === 'string') {
            cleaned[field] = String(value).trim();
        } else if (rules.type === 'number') {
            const numValue = Number(value);
            if (!isNaN(numValue)) {
                cleaned[field] = numValue;
            }
        }
    }
    
    return cleaned;
}

// 测试数据库连接
async function testDatabaseConnection() {
    try {
        console.log('测试数据库连接...');
        
        const { data, error } = await supabase
            .from('products')
            .select('count')
            .limit(1);
            
        if (error) {
            console.error('数据库连接失败:', error);
            return false;
        }
        
        console.log('数据库连接成功');
        return true;
    } catch (err) {
        console.error('数据库连接异常:', err);
        return false;
    }
}

// 检查表权限
async function checkTablePermissions() {
    try {
        console.log('检查表权限...');
        
        // 尝试读取权限
        const { data: readData, error: readError } = await supabase
            .from('products')
            .select('id')
            .limit(1);
            
        if (readError) {
            console.error('读取权限检查失败:', readError);
            return { read: false, write: false };
        }
        
        // 尝试写入权限（插入测试数据）
        const testData = {
            name: '权限测试产品',
            category: '测试分类'
        };
        
        const { data: writeData, error: writeError } = await supabase
            .from('products')
            .insert(testData)
            .select();
            
        if (writeError) {
            console.error('写入权限检查失败:', writeError);
            return { read: true, write: false, error: writeError };
        }
        
        // 删除测试数据
        if (writeData && writeData.length > 0) {
            await supabase
                .from('products')
                .delete()
                .eq('id', writeData[0].id);
        }
        
        console.log('权限检查通过');
        return { read: true, write: true };
    } catch (err) {
        console.error('权限检查异常:', err);
        return { read: false, write: false, error: err };
    }
}

// 安全插入产品数据
async function insertProduct(productData) {
    try {
        console.log('开始插入产品数据:', productData);
        
        // 1. 验证数据格式
        const validationErrors = validateProductData(productData);
        if (validationErrors.length > 0) {
            throw new Error('数据验证失败: ' + validationErrors.join(', '));
        }
        
        // 2. 清理数据
        const cleanedData = sanitizeProductData(productData);
        console.log('清理后的数据:', cleanedData);
        
        // 3. 插入数据
        const { data, error } = await supabase
            .from('products')
            .insert(cleanedData)
            .select();
            
        if (error) {
            console.error('插入失败:', error);
            throw new Error(`插入失败: ${error.message}`);
        }
        
        console.log('插入成功:', data);
        return { success: true, data: data[0] };
        
    } catch (err) {
        console.error('插入产品异常:', err);
        return { success: false, error: err.message };
    }
}

// 批量插入产品数据
async function insertMultipleProducts(productsArray) {
    const results = [];
    
    for (let i = 0; i < productsArray.length; i++) {
        const product = productsArray[i];
        console.log(`插入第 ${i + 1}/${productsArray.length} 个产品...`);
        
        const result = await insertProduct(product);
        results.push({
            index: i,
            product: product,
            result: result
        });
        
        // 添加延迟避免频率限制
        if (i < productsArray.length - 1) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
    }
    
    return results;
}

// 诊断函数 - 全面检查问题
async function diagnoseProductTableIssues() {
    console.log('=== 产品表问题诊断 ===');
    
    const diagnosis = {
        connection: false,
        permissions: { read: false, write: false },
        tableExists: false,
        rlsStatus: null,
        recommendations: []
    };
    
    try {
        // 1. 测试连接
        diagnosis.connection = await testDatabaseConnection();
        if (!diagnosis.connection) {
            diagnosis.recommendations.push('检查 Supabase URL 和 API Key 配置');
            return diagnosis;
        }
        
        // 2. 检查表是否存在
        try {
            const { data, error } = await supabase
                .from('products')
                .select('count')
                .limit(0);
                
            diagnosis.tableExists = !error;
        } catch (err) {
            diagnosis.tableExists = false;
        }
        
        if (!diagnosis.tableExists) {
            diagnosis.recommendations.push('products 表不存在，需要创建表');
            return diagnosis;
        }
        
        // 3. 检查权限
        diagnosis.permissions = await checkTablePermissions();
        
        if (!diagnosis.permissions.read) {
            diagnosis.recommendations.push('没有读取权限，检查 RLS 策略');
        }
        
        if (!diagnosis.permissions.write) {
            diagnosis.recommendations.push('没有写入权限，检查 RLS 策略或 API Key 权限');
        }
        
        // 4. 检查 RLS 状态
        try {
            const { data: rlsData } = await supabase.rpc('check_rls_status', { table_name: 'products' });
            diagnosis.rlsStatus = rlsData;
        } catch (err) {
            diagnosis.rlsStatus = 'unknown';
        }
        
    } catch (err) {
        console.error('诊断过程出错:', err);
        diagnosis.recommendations.push('诊断过程出错: ' + err.message);
    }
    
    console.log('诊断结果:', diagnosis);
    return diagnosis;
}

// 修复建议
async function getFixRecommendations() {
    const diagnosis = await diagnoseProductTableIssues();
    const fixes = [];
    
    if (!diagnosis.connection) {
        fixes.push({
            issue: '数据库连接失败',
            solution: '检查 SUPABASE_URL 和 SUPABASE_ANON_KEY 配置',
            priority: 'high'
        });
    }
    
    if (!diagnosis.tableExists) {
        fixes.push({
            issue: 'products 表不存在',
            solution: '运行 SQL 创建 products 表',
            priority: 'high'
        });
    }
    
    if (!diagnosis.permissions.write) {
        fixes.push({
            issue: '没有写入权限',
            solution: '禁用 RLS 或创建适当的 RLS 策略',
            priority: 'high'
        });
    }
    
    return fixes;
}

// 导出函数供外部使用
window.ProductTableFix = {
    insertProduct,
    insertMultipleProducts,
    validateProductData,
    sanitizeProductData,
    testDatabaseConnection,
    checkTablePermissions,
    diagnoseProductTableIssues,
    getFixRecommendations
};

// 页面加载时自动诊断
document.addEventListener('DOMContentLoaded', async function() {
    console.log('产品表修复脚本已加载');
    
    // 自动诊断（可选）
    if (window.location.search.includes('debug=true')) {
        setTimeout(async () => {
            const diagnosis = await diagnoseProductTableIssues();
            console.log('自动诊断完成:', diagnosis);
        }, 1000);
    }
});

console.log('Product Fix 脚本已加载完成');