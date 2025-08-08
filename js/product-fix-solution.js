// 产品表写入修复方案
// 解决HTTP 400错误问题

import supabase from '../lib/supabase.js';

/**
 * 产品数据验证器
 * 确保数据符合表结构要求
 */
class ProductValidator {
  /**
   * 验证产品数据
   * @param {Object} data - 产品数据
   * @returns {Object} 验证结果 {valid: boolean, errors: Array}
   */
  static validate(data) {
    const errors = [];
    
    // 检查必填字段
    if (!data.name || data.name.trim() === '') {
      errors.push('产品名称(name)不能为空');
    }
    
    if (!data.category || data.category.trim() === '') {
      errors.push('产品分类(category)不能为空');
    }
    
    // 检查数据类型
    if (data.price !== undefined && data.price !== null) {
      if (isNaN(Number(data.price))) {
        errors.push('价格(price)必须是数字类型');
      }
    }
    
    // 检查规格字段格式
    if (data.specifications !== undefined && data.specifications !== null) {
      if (typeof data.specifications === 'object' && !Array.isArray(data.specifications)) {
        errors.push('规格(specifications)必须是数组或JSON字符串');
      } else if (typeof data.specifications !== 'string' && !Array.isArray(data.specifications)) {
        errors.push('规格(specifications)格式无效');
      }
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }
  
  /**
   * 清理和格式化产品数据
   * @param {Object} data - 原始产品数据
   * @returns {Object} 清理后的数据
   */
  static sanitize(data) {
    const cleaned = { ...data };
    
    // 处理字符串字段
    ['name', 'category', 'description', 'image_url'].forEach(field => {
      if (cleaned[field]) {
        cleaned[field] = String(cleaned[field]).trim();
      }
    });
    
    // 处理数字字段
    if (cleaned.price !== undefined && cleaned.price !== null) {
      cleaned.price = Number(cleaned.price);
    }
    
    // 处理规格字段
    if (cleaned.specifications) {
      if (Array.isArray(cleaned.specifications)) {
        cleaned.specifications = JSON.stringify(cleaned.specifications);
      } else if (typeof cleaned.specifications === 'object') {
        cleaned.specifications = JSON.stringify(Object.values(cleaned.specifications));
      } else if (typeof cleaned.specifications === 'string') {
        try {
          // 验证是否为有效的JSON
          JSON.parse(cleaned.specifications);
        } catch (e) {
          // 如果不是有效的JSON，则转换为数组
          cleaned.specifications = JSON.stringify([cleaned.specifications]);
        }
      }
    }
    
    return cleaned;
  }
}

/**
 * 产品表修复工具
 * 解决HTTP 400错误问题
 */
class ProductTableFix {
  /**
   * 安全插入产品数据
   * @param {Object} productData - 产品数据
   * @returns {Promise} 包含结果的Promise
   */
  static async insertProduct(productData) {
    try {
      console.log('开始安全插入产品数据:', productData);
      
      // 1. 验证数据
      const validation = ProductValidator.validate(productData);
      if (!validation.valid) {
        return {
          success: false,
          error: `数据验证失败: ${validation.errors.join(', ')}`
        };
      }
      
      // 2. 清理和格式化数据
      const cleanedData = ProductValidator.sanitize(productData);
      console.log('清理后的数据:', cleanedData);
      
      // 3. 插入数据
      const { data, error } = await supabase
        .from('products')
        .insert(cleanedData)
        .select();
        
      if (error) {
        console.error('插入失败:', error);
        return {
          success: false,
          error: error.message,
          details: error
        };
      }
      
      console.log('插入成功:', data);
      return {
        success: true,
        data: data[0]
      };
      
    } catch (err) {
      console.error('插入产品异常:', err);
      return {
        success: false,
        error: err.message
      };
    }
  }
  
  /**
   * 批量插入产品数据
   * @param {Array} productsArray - 产品数据数组
   * @returns {Promise} 包含结果的Promise
   */
  static async insertMultipleProducts(productsArray) {
    const results = [];
    let successCount = 0;
    let failCount = 0;
    
    for (let i = 0; i < productsArray.length; i++) {
      const product = productsArray[i];
      console.log(`插入第 ${i + 1}/${productsArray.length} 个产品...`);
      
      const result = await this.insertProduct(product);
      
      if (result.success) {
        successCount++;
      } else {
        failCount++;
      }
      
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
    
    return {
      total: productsArray.length,
      success: successCount,
      fail: failCount,
      results
    };
  }
  
  /**
   * 测试数据库连接
   * @returns {Promise<boolean>} 连接是否成功
   */
  static async testDatabaseConnection() {
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
  
  /**
   * 检查表权限
   * @returns {Promise<Object>} 权限检查结果
   */
  static async checkTablePermissions() {
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
  
  /**
   * 诊断产品表问题
   * @returns {Promise<Object>} 诊断结果
   */
  static async diagnoseProductTableIssues() {
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
      diagnosis.connection = await this.testDatabaseConnection();
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
      diagnosis.permissions = await this.checkTablePermissions();
      
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
  
  /**
   * 获取修复建议
   * @returns {Promise<Array>} 修复建议
   */
  static async getFixRecommendations() {
    const diagnosis = await this.diagnoseProductTableIssues();
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
  
  /**
   * 应用修复 - 禁用RLS
   * @returns {Promise<Object>} 修复结果
   */
  static async applyFix_DisableRLS() {
    try {
      console.log('正在应用修复: 禁用RLS...');
      
      const { data, error } = await supabase.rpc('admin_disable_rls', { table_name: 'products' });
      
      if (error) {
        console.error('禁用RLS失败:', error);
        return {
          success: false,
          error: error.message
        };
      }
      
      console.log('禁用RLS成功');
      return {
        success: true,
        message: 'RLS已成功禁用'
      };
    } catch (err) {
      console.error('应用修复异常:', err);
      return {
        success: false,
        error: err.message
      };
    }
  }
}

// 导出修复工具
export default ProductTableFix;

// 全局对象，方便在控制台调试
window.ProductTableFix = ProductTableFix;

console.log('产品表修复方案已加载');