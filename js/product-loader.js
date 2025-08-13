/**
 * 产品加载器 - 从Flask后端或Supabase数据库加载产品数据并显示在页面上
 */
import supabase from '../lib/supabase.js';

class ProductLoader {
  constructor() {
    this.productsContainer = document.getElementById('products-grid');
    this.loadingIndicator = document.createElement('div');
    this.loadingIndicator.className = 'text-center py-5';
    this.loadingIndicator.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">加载中...</span></div>';
    this.errorMessage = document.createElement('div');
    this.errorMessage.className = 'alert alert-danger';
    // 使用统一API
    this.api = window.unifiedAPI || this.createFallbackAPI();
  }

  /**
   * 创建备用API（如果统一API未加载）
   */
  createFallbackAPI() {
    return {
      getProducts: async () => {
        try {
          const response = await fetch('http://localhost:5003/api/products');
          const data = await response.json();
          return data.products || [];
        } catch (error) {
          console.error('备用API获取产品失败:', error);
          return [];
        }
      }
    };
  }

  /**
   * 初始化产品加载器
   */
  init() {
    this.loadProducts();
    this.setupCategoryFilters();
  }

  /**
   * 加载所有产品
   */
  async loadProducts() {
    try {
      // 显示加载指示器
      if (this.productsContainer) {
        this.productsContainer.querySelector('.row').innerHTML = '';
        this.productsContainer.querySelector('.row').appendChild(this.loadingIndicator);
      }

      // 尝试使用统一API获取产品
      let products = [];
      if (this.api && typeof this.api.getProducts === 'function') {
        products = await this.api.getProducts();
      } else {
        // 从Supabase数据库加载产品数据
        const { data, error } = await supabase
          .from('products')
          .select('*')
          .eq('status', 'active')
          .order('created_at', { ascending: false });
        
        if (error) {
          throw new Error(error.message);
        }
        
        products = data || [];
      }
      
      // 移除加载指示器
      if (this.loadingIndicator.parentNode) {
        this.loadingIndicator.parentNode.removeChild(this.loadingIndicator);
      }

      // 渲染产品
      this.renderProducts(products);
    } catch (error) {
      console.error('加载产品失败:', error);
      this.showError('加载产品数据时出错，请稍后再试。');
    }
  }

  /**
   * 按类别加载产品
   * @param {string} category - 产品类别
   */
  async loadProductsByCategory(category) {
    try {
      // 显示加载指示器
      if (this.productsContainer) {
        this.productsContainer.querySelector('.row').innerHTML = '';
        this.productsContainer.querySelector('.row').appendChild(this.loadingIndicator);
      }

      let products = [];
      
      // 尝试使用统一API获取产品
      if (this.api && typeof this.api.getProducts === 'function') {
        const allProducts = await this.api.getProducts();
        products = allProducts.filter(p => p.category === category);
      } else {
        // 从Supabase数据库按类别加载产品数据
        const { data, error } = await supabase
          .from('products')
          .select('*')
          .eq('status', 'active')
          .eq('category', category)
          .order('created_at', { ascending: false });
        
        if (error) {
          throw new Error(error.message);
        }
        
        products = data || [];
      }
      
      // 移除加载指示器
      if (this.loadingIndicator.parentNode) {
        this.loadingIndicator.parentNode.removeChild(this.loadingIndicator);
      }
        
      // 渲染产品
      this.renderProducts(products);
    } catch (error) {
      console.error(`加载${category}类别产品失败:`, error);
      this.showError(`加载${category}类别产品数据时出错，请稍后再试。`);
    }
  }

  /**
   * 渲染产品列表
   * @param {Array} products - 产品数据数组
   */
  renderProducts(products) {
    if (!this.productsContainer) return;
    
    const productsRow = this.productsContainer.querySelector('.row');
    productsRow.innerHTML = '';

    if (!products || products.length === 0) {
      const noProductsMessage = document.createElement('div');
      noProductsMessage.className = 'col-12 text-center py-5';
      noProductsMessage.innerHTML = '<p class="text-muted">没有找到产品。</p>';
      productsRow.appendChild(noProductsMessage);
      return;
    }

    // 渲染每个产品卡片
    products.forEach((product, index) => {
      const productCard = this.createProductCard(product, index);
      productsRow.appendChild(productCard);
    });

    // 初始化AOS动画
    if (window.AOS) {
      window.AOS.refresh();
    }
  }

  /**
   * 创建产品卡片元素
   * @param {Object} product - 产品数据
   * @param {number} index - 产品索引
   * @returns {HTMLElement} 产品卡片元素
   */
  createProductCard(product, index) {
    const delay = (index % 3) * 100;
    
    const productCol = document.createElement('div');
    productCol.className = 'col-lg-4 col-md-6';
    productCol.setAttribute('data-aos', 'fade-up');
    productCol.setAttribute('data-aos-delay', delay.toString());

    // 获取产品图标
    const iconClass = this.getCategoryIcon(product.category);
    
    // 创建产品卡片HTML
    productCol.innerHTML = `
      <div class="card product-card h-100">
        <div class="card-img-container">
          <div class="product-image bg-light d-flex align-items-center justify-content-center">
            ${product.image_url ? 
              `<img src="${product.image_url}" alt="${product.name}" class="img-fluid">` : 
              `<i class="${iconClass} display-4"></i>`
            }
          </div>
          <div class="card-overlay">
            <a class="btn btn-primary" href="contact.html?product=${product.id}">
              <i class="fas fa-phone me-2"></i>获取报价
            </a>
          </div>
        </div>
        <div class="card-body">
          <h5 class="card-title">${product.name}</h5>
          <p class="card-text">${product.description || '暂无描述'}</p>
          ${this.renderProductSpecifications(product.specifications)}
        </div>
        <div class="card-footer">
          <small class="text-muted">类别: ${product.category}</small>
        </div>
      </div>
    `;

    return productCol;
  }

  /**
   * 渲染产品规格
   * @param {string} specifications - 产品规格JSON字符串
   * @returns {string} 产品规格HTML
   */
  renderProductSpecifications(specifications) {
    if (!specifications) return '';

    try {
      let specs;
      if (typeof specifications === 'string') {
        specs = JSON.parse(specifications);
      } else {
        specs = specifications;
      }

      if (!specs || !Array.isArray(specs)) return '';

      let specsHtml = '<ul class="list-unstyled small">';
      specs.forEach(spec => {
        specsHtml += `<li><i class="fas fa-check text-success me-2"></i>${spec}</li>`;
      });
      specsHtml += '</ul>';
      return specsHtml;
    } catch (error) {
      console.error('解析产品规格失败:', error);
      return '';
    }
  }

  /**
   * 根据产品类别获取图标
   * @param {string} category - 产品类别
   * @returns {string} 图标类名
   */
  getCategoryIcon(category) {
    const categoryIcons = {
      'Indoor': 'fas fa-building text-primary',
      'Outdoor': 'fas fa-sun text-warning',
      'Rental': 'fas fa-magic text-purple',
      'Transparent': 'fas fa-eye text-info',
      'Creative': 'fas fa-palette text-danger',
      'Industrial': 'fas fa-industry text-secondary',
      'Fine Pitch': 'fas fa-microscope text-dark',
      'Broadcast': 'fas fa-video text-success'
    };

    return categoryIcons[category] || 'fas fa-tv text-primary';
  }

  /**
   * 设置类别筛选器
   */
  setupCategoryFilters() {
    const filterContainer = document.getElementById('category-filters');
    if (!filterContainer) return;

    // 获取所有类别按钮
    const filterButtons = filterContainer.querySelectorAll('.category-filter');
    
    // 为每个按钮添加点击事件
    filterButtons.forEach(button => {
      button.addEventListener('click', (event) => {
        event.preventDefault();
        
        // 移除所有按钮的active类
        filterButtons.forEach(btn => btn.classList.remove('active'));
        
        // 为当前按钮添加active类
        button.classList.add('active');
        
        // 获取类别值
        const category = button.getAttribute('data-category');
        
        // 加载对应类别的产品
        if (category === 'all') {
          this.loadProducts();
        } else {
          this.loadProductsByCategory(category);
        }
      });
    });
  }

  /**
   * 显示错误消息
   * @param {string} message - 错误消息
   */
  showError(message) {
    if (!this.productsContainer) return;
    
    // 移除加载指示器
    if (this.loadingIndicator.parentNode) {
      this.loadingIndicator.parentNode.removeChild(this.loadingIndicator);
    }

    // 显示错误消息
    this.errorMessage.textContent = message;
    this.productsContainer.querySelector('.row').innerHTML = '';
    this.productsContainer.querySelector('.row').appendChild(this.errorMessage);
  }
}

// 当DOM加载完成后初始化产品加载器
document.addEventListener('DOMContentLoaded', () => {
  const productLoader = new ProductLoader();
  productLoader.init();
});