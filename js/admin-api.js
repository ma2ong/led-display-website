/**
 * Admin API Integration for Frontend
 * 前端与后台API集成
 */

// API基础URL
const API_BASE_URL = 'http://localhost:5000/api';

// 产品数据缓存
let productsCache = null;

/**
 * 从后台API获取产品数据
 */
async function fetchProductsFromAdmin() {
    try {
        const response = await fetch(`${API_BASE_URL}/products`);
        const data = await response.json();
        
        if (data.status === 'success') {
            productsCache = data.products;
            return data.products;
        } else {
            console.warn('Failed to fetch products from admin API');
            return null;
        }
    } catch (error) {
        console.warn('Admin API not available, using static content:', error);
        return null;
    }
}

/**
 * 根据分类获取产品
 */
async function fetchProductsByCategory(category) {
    try {
        const response = await fetch(`${API_BASE_URL}/products/${category}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            return data.products;
        } else {
            console.warn(`Failed to fetch ${category} products from admin API`);
            return null;
        }
    } catch (error) {
        console.warn('Admin API not available, using static content:', error);
        return null;
    }
}

/**
 * 更新产品展示区域
 */
function updateProductDisplay(products) {
    if (!products || products.length === 0) return;
    
    const productGrid = document.querySelector('.products-grid');
    if (!productGrid) return;
    
    // 清空现有产品卡片
    productGrid.innerHTML = '';
    
    products.forEach((product, index) => {
        const productCard = createProductCard(product, index);
        productGrid.appendChild(productCard);
    });
}

/**
 * 创建产品卡片元素
 */
function createProductCard(product, index) {
    const card = document.createElement('div');
    card.className = 'product-card';
    card.setAttribute('data-aos', 'fade-up');
    card.setAttribute('data-aos-delay', (index * 100 + 100).toString());
    
    // 处理图片路径
    let imagePath = product.images;
    let imageHtml = '';
    
    if (imagePath) {
        if (imagePath.startsWith('assets/')) {
            imageHtml = `<img src="${imagePath}" alt="${product.name_en}" onerror="this.style.display='none'; this.parentNode.querySelector('.image-placeholder').style.display='flex';">
                        <div class="image-placeholder" style="display:none; width:100%; height:200px; background:#f8f9fa; align-items:center; justify-content:center; flex-direction:column;">
                            <i class="fas fa-image fa-2x text-muted mb-2"></i>
                            <span class="text-muted">${product.name_en}</span>
                        </div>`;
        } else {
            imageHtml = `<img src="${imagePath}" alt="${product.name_en}" onerror="this.style.display='none'; this.parentNode.querySelector('.image-placeholder').style.display='flex';">
                        <div class="image-placeholder" style="display:none; width:100%; height:200px; background:#f8f9fa; align-items:center; justify-content:center; flex-direction:column;">
                            <i class="fas fa-image fa-2x text-muted mb-2"></i>
                            <span class="text-muted">${product.name_en}</span>
                        </div>`;
        }
    } else {
        imageHtml = `<div class="image-placeholder" style="display:flex; width:100%; height:200px; background:#f8f9fa; align-items:center; justify-content:center; flex-direction:column;">
                        <i class="fas fa-image fa-2x text-muted mb-2"></i>
                        <span class="text-muted">${product.name_en}</span>
                    </div>`;
    }
    
    // 处理产品特点
    const features = product.features ? product.features.split('\n').filter(f => f.trim()) : [];
    const featuresHtml = features.slice(0, 3).map(feature => 
        `<li data-en="${feature}" data-zh="${feature}">${feature}</li>`
    ).join('');
    
    card.innerHTML = `
        <div class="product-image">
            ${imageHtml}
            <div class="product-overlay">
                <a href="#${product.category}" class="product-link">
                    <i class="fas fa-arrow-right"></i>
                </a>
            </div>
        </div>
        <div class="product-content">
            <h3 class="product-title" data-en="${product.name_en}" data-zh="${product.name_zh}">${product.name_en}</h3>
            <p class="product-description" data-en="${product.description_en}" data-zh="${product.description_zh}">
                ${product.description_en}
            </p>
            <ul class="product-features">
                ${featuresHtml}
            </ul>
            <a href="#${product.category}" class="btn btn-outline btn-sm" data-en="Learn More" data-zh="了解更多">Learn More</a>
        </div>
    `;
    
    return card;
}

/**
 * 初始化产品数据
 */
async function initializeProducts() {
    // 尝试从后台API获取产品数据
    const products = await fetchProductsFromAdmin();
    
    if (products && products.length > 0) {
        console.log('Loaded products from admin API:', products.length);
        updateProductDisplay(products);
        
        // 重新初始化AOS动画
        if (typeof AOS !== 'undefined') {
            AOS.refresh();
        }
    } else {
        console.log('Using static product content');
    }
}

/**
 * 页面加载完成后初始化
 */
document.addEventListener('DOMContentLoaded', function() {
    // 延迟初始化，确保其他脚本已加载
    setTimeout(initializeProducts, 1000);
});

/**
 * 导出函数供其他脚本使用
 */
window.AdminAPI = {
    fetchProducts: fetchProductsFromAdmin,
    fetchProductsByCategory: fetchProductsByCategory,
    updateProductDisplay: updateProductDisplay
};