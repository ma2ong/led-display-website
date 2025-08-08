// Product Table Test Script
// 用于诊断产品表写入失败问题 (HTTP 错误: 400)

import supabase from '../lib/supabase.js';

// 测试产品数据
const testProducts = [
  {
    name: "测试产品1",
    category: "Indoor",
    description: "这是一个测试产品",
    price: 1999.99,
    image_url: "assets/products/test1.jpg",
    specifications: JSON.stringify(["规格1", "规格2", "规格3"])
  },
  {
    name: "测试产品2",
    category: "Outdoor",
    description: "这是另一个测试产品",
    price: 2999.99,
    specifications: JSON.stringify(["规格A", "规格B"])
  }
];

// 测试函数
async function testProductInsert() {
  console.log('开始测试产品表插入...');
  
  try {
    // 1. 测试数据库连接
    console.log('1. 测试数据库连接...');
    const { data: connectionTest, error: connectionError } = await supabase
      .from('products')
      .select('count')
      .limit(1);
      
    if (connectionError) {
      console.error('数据库连接失败:', connectionError);
      return {
        success: false,
        stage: 'connection',
        error: connectionError
      };
    }
    
    console.log('数据库连接成功');
    
    // 2. 测试表结构
    console.log('2. 测试表结构...');
    const { data: structureTest, error: structureError } = await supabase
      .rpc('get_table_structure', { table_name: 'products' })
      .single();
      
    if (structureError) {
      console.log('无法获取表结构，尝试简单查询...');
      // 尝试简单查询
      const { data: simpleQuery, error: simpleQueryError } = await supabase
        .from('products')
        .select('id, name, category')
        .limit(1);
        
      if (simpleQueryError) {
        console.error('表结构测试失败:', simpleQueryError);
        return {
          success: false,
          stage: 'structure',
          error: simpleQueryError
        };
      }
      
      console.log('表可以查询，结构似乎正常');
    } else {
      console.log('表结构:', structureTest);
    }
    
    // 3. 测试插入最小数据
    console.log('3. 测试插入最小必填数据...');
    const minimalProduct = {
      name: "最小测试产品",
      category: "Test"
    };
    
    const { data: minimalInsert, error: minimalError } = await supabase
      .from('products')
      .insert(minimalProduct)
      .select();
      
    if (minimalError) {
      console.error('最小数据插入失败:', minimalError);
      return {
        success: false,
        stage: 'minimal_insert',
        error: minimalError,
        data: minimalProduct
      };
    }
    
    console.log('最小数据插入成功:', minimalInsert);
    
    // 4. 测试插入完整数据
    console.log('4. 测试插入完整数据...');
    const { data: fullInsert, error: fullError } = await supabase
      .from('products')
      .insert(testProducts[0])
      .select();
      
    if (fullError) {
      console.error('完整数据插入失败:', fullError);
      return {
        success: false,
        stage: 'full_insert',
        error: fullError,
        data: testProducts[0]
      };
    }
    
    console.log('完整数据插入成功:', fullInsert);
    
    // 5. 清理测试数据
    console.log('5. 清理测试数据...');
    if (minimalInsert && minimalInsert.length > 0) {
      await supabase
        .from('products')
        .delete()
        .eq('id', minimalInsert[0].id);
    }
    
    if (fullInsert && fullInsert.length > 0) {
      await supabase
        .from('products')
        .delete()
        .eq('id', fullInsert[0].id);
    }
    
    return {
      success: true,
      message: '所有测试通过，产品表可以正常写入'
    };
    
  } catch (err) {
    console.error('测试过程中发生异常:', err);
    return {
      success: false,
      stage: 'exception',
      error: err
    };
  }
}

// 检查规格字段格式
function checkSpecificationsFormat() {
  console.log('检查数据库中的规格字段格式...');
  
  return supabase
    .from('products')
    .select('id, name, specifications')
    .limit(10)
    .then(({ data, error }) => {
      if (error) {
        console.error('查询失败:', error);
        return { success: false, error };
      }
      
      if (!data || data.length === 0) {
        console.log('没有找到产品数据');
        return { success: true, data: [], message: '没有产品数据' };
      }
      
      const results = data.map(product => {
        let specFormat = 'unknown';
        let isValid = false;
        let parsed = null;
        
        if (product.specifications === null) {
          specFormat = 'null';
          isValid = true;
        } else if (typeof product.specifications === 'string') {
          specFormat = 'string';
          try {
            parsed = JSON.parse(product.specifications);
            isValid = Array.isArray(parsed);
          } catch (e) {
            isValid = false;
          }
        } else if (Array.isArray(product.specifications)) {
          specFormat = 'array';
          isValid = true;
          parsed = product.specifications;
        } else if (typeof product.specifications === 'object') {
          specFormat = 'object';
          isValid = false;
        }
        
        return {
          id: product.id,
          name: product.name,
          format: specFormat,
          isValid,
          value: product.specifications,
          parsed
        };
      });
      
      return { 
        success: true, 
        data: results,
        summary: {
          total: results.length,
          valid: results.filter(r => r.isValid).length,
          invalid: results.filter(r => !r.isValid).length,
          formats: results.reduce((acc, curr) => {
            acc[curr.format] = (acc[curr.format] || 0) + 1;
            return acc;
          }, {})
        }
      };
    });
}

// 导出测试函数
export const productTableTest = {
  testInsert: testProductInsert,
  checkSpecificationsFormat
};

// 自动运行测试
document.addEventListener('DOMContentLoaded', () => {
  // 检查是否在调试模式
  if (window.location.search.includes('test=products')) {
    console.log('产品表测试模式已激活');
    
    // 创建测试结果显示区域
    const testResultsDiv = document.createElement('div');
    testResultsDiv.className = 'container mt-5 p-4 bg-light rounded';
    testResultsDiv.innerHTML = `
      <h3>产品表测试</h3>
      <div class="alert alert-info">正在测试产品表写入功能...</div>
      <div id="test-results" class="mt-3">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">测试中...</span>
        </div>
      </div>
      <button id="run-test-btn" class="btn btn-primary mt-3">重新测试</button>
    `;
    
    // 添加到页面
    document.body.appendChild(testResultsDiv);
    
    // 运行测试
    const runTest = () => {
      const resultsDiv = document.getElementById('test-results');
      resultsDiv.innerHTML = `
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">测试中...</span>
        </div>
      `;
      
      testProductInsert().then(result => {
        let html = '';
        
        if (result.success) {
          html = `
            <div class="alert alert-success">
              <h5>测试成功!</h5>
              <p>${result.message}</p>
            </div>
          `;
        } else {
          html = `
            <div class="alert alert-danger">
              <h5>测试失败 (阶段: ${result.stage})</h5>
              <p>错误信息: ${result.error?.message || '未知错误'}</p>
              ${result.data ? `<pre>${JSON.stringify(result.data, null, 2)}</pre>` : ''}
            </div>
          `;
        }
        
        resultsDiv.innerHTML = html;
      });
      
      // 同时检查规格字段格式
      checkSpecificationsFormat().then(result => {
        if (result.success && result.data.length > 0) {
          const formatDiv = document.createElement('div');
          formatDiv.className = 'mt-4';
          formatDiv.innerHTML = `
            <h5>规格字段格式检查</h5>
            <div class="card">
              <div class="card-body">
                <p>总计: ${result.summary.total} 条记录</p>
                <p>有效格式: ${result.summary.valid} 条</p>
                <p>无效格式: ${result.summary.invalid} 条</p>
                <p>格式分布: ${JSON.stringify(result.summary.formats)}</p>
              </div>
            </div>
          `;
          
          document.getElementById('test-results').appendChild(formatDiv);
        }
      });
    };
    
    // 绑定按钮事件
    document.getElementById('run-test-btn').addEventListener('click', runTest);
    
    // 自动运行
    runTest();
  }
});

// 导出为全局对象，方便控制台调试
window.ProductTest = {
  run: testProductInsert,
  checkSpecs: checkSpecificationsFormat
};

console.log('产品表测试脚本已加载');