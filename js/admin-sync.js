/**
 * Admin-Frontend Synchronization Script
 * Connects frontend with backend admin system for real-time updates
 */

class AdminSync {
    constructor() {
        this.apiBase = window.location.origin;
        this.cache = new Map();
        this.retryCount = 0;
        this.maxRetries = 3;
        
        // Initialize with error protection
        this.init().catch(error => {
            console.warn('AdminSync initialization error:', error);
        });
    }

    async init() {
        try {
            // Load initial data
            await this.loadProducts();
            await this.loadContent();
            
            // Set up periodic sync
            this.startPeriodicSync();
            
            console.log('AdminSync initialized successfully');
        } catch (error) {
            console.warn('AdminSync init failed:', error);
        }
    }

    async apiCall(endpoint, options = {}) {
        try {
            const url = `${this.apiBase}${endpoint}`;
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`API call failed: ${response.status}`);
            }

            const data = await response.json();
            this.retryCount = 0; // Reset retry count on success
            return data;
        } catch (error) {
            console.warn(`API call error for ${endpoint}:`, error);
            
            // Retry logic
            if (this.retryCount < this.maxRetries) {
                this.retryCount++;
                await new Promise(resolve => setTimeout(resolve, 1000 * this.retryCount));
                return this.apiCall(endpoint, options);
            }
            
            throw error;
        }
    }

    async loadProducts() {
        try {
            const products = await this.apiCall('/api/products');
            this.cache.set('products', products);
            this.updateProductDisplay(products);
            return products;
        } catch (error) {
            console.warn('Failed to load products:', error);
            return [];
        }
    }

    async loadContent() {
        try {
            const content = await this.apiCall('/api/content');
            this.cache.set('content', content);
            this.updateContentDisplay(content);
            return content;
        } catch (error) {
            console.warn('Failed to load content:', error);
            return {};
        }
    }

    updateProductDisplay(products) {
        try {
            // Update product grids on various pages
            this.updateProductGrid(products);
            this.updateProductCards(products);
            this.updateProductDetails(products);
        } catch (error) {
            console.warn('Product display update error:', error);
        }
    }

    updateProductGrid(products) {
        const productGrids = document.querySelectorAll('.product-grid, .products-container');
        
        productGrids.forEach(grid => {
            try {
                // Clear existing content
                grid.innerHTML = '';
                
                // Add products
                products.forEach(product => {
                    if (product.status === 'active') {
                        const productCard = this.createProductCard(product);
                        grid.appendChild(productCard);
                    }
                });
            } catch (error) {
                console.warn('Product grid update error:', error);
            }
        });
    }

    createProductCard(product) {
        const card = document.createElement('div');
        card.className = 'col-lg-4 col-md-6 mb-4';
        
        const imageUrl = product.images ? 
            `${this.apiBase}/static/${product.images}` : 
            '/assets/products/default-product.jpg';
        
        const price = product.price ? 
            `$${parseFloat(product.price).toLocaleString()}` : 
            'Contact for Quote';

        card.innerHTML = `
            <div class="card product-card h-100 shadow-sm">
                <div class="card-img-wrapper">
                    <img src="${imageUrl}" class="card-img-top" alt="${product.name_en}" 
                         onerror="this.src='/assets/products/default-product.jpg'">
                    <div class="card-overlay">
                        <a href="/products/${product.category}.html" class="btn btn-primary btn-sm">
                            View Details
                        </a>
                    </div>
                </div>
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title">${product.name_en}</h5>
                    <p class="card-text flex-grow-1">${product.description_en}</p>
                    <div class="product-meta">
                        <div class="product-price">${price}</div>
                        <div class="product-category">${this.formatCategory(product.category)}</div>
                    </div>
                </div>
            </div>
        `;
        
        return card;
    }

    updateProductCards(products) {
        // Update individual product cards
        const productCards = document.querySelectorAll('[data-product-id]');
        
        productCards.forEach(card => {
            try {
                const productId = card.getAttribute('data-product-id');
                const product = products.find(p => p.id == productId);
                
                if (product) {
                    this.updateSingleProductCard(card, product);
                }
            } catch (error) {
                console.warn('Product card update error:', error);
            }
        });
    }

    updateSingleProductCard(card, product) {
        try {
            const titleElement = card.querySelector('.card-title, .product-title');
            const descElement = card.querySelector('.card-text, .product-description');
            const imageElement = card.querySelector('.card-img-top, .product-image');
            const priceElement = card.querySelector('.product-price');
            
            if (titleElement) titleElement.textContent = product.name_en;
            if (descElement) descElement.textContent = product.description_en;
            if (priceElement) {
                priceElement.textContent = product.price ? 
                    `$${parseFloat(product.price).toLocaleString()}` : 
                    'Contact for Quote';
            }
            if (imageElement && product.images) {
                imageElement.src = `${this.apiBase}/static/${product.images}`;
            }
        } catch (error) {
            console.warn('Single product card update error:', error);
        }
    }

    updateContentDisplay(content) {
        try {
            // Update dynamic content sections
            this.updateTextContent(content);
            this.updateImages(content);
            this.updateLinks(content);
        } catch (error) {
            console.warn('Content display update error:', error);
        }
    }

    updateTextContent(content) {
        // Update elements with data-content attributes
        const contentElements = document.querySelectorAll('[data-content]');
        
        contentElements.forEach(element => {
            try {
                const contentKey = element.getAttribute('data-content');
                if (content[contentKey]) {
                    element.textContent = content[contentKey];
                }
            } catch (error) {
                console.warn('Text content update error:', error);
            }
        });
    }

    updateImages(content) {
        // Update images with data-image attributes
        const imageElements = document.querySelectorAll('[data-image]');
        
        imageElements.forEach(element => {
            try {
                const imageKey = element.getAttribute('data-image');
                if (content.images && content.images[imageKey]) {
                    element.src = `${this.apiBase}/static/${content.images[imageKey]}`;
                }
            } catch (error) {
                console.warn('Image update error:', error);
            }
        });
    }

    updateLinks(content) {
        // Update links with data-link attributes
        const linkElements = document.querySelectorAll('[data-link]');
        
        linkElements.forEach(element => {
            try {
                const linkKey = element.getAttribute('data-link');
                if (content.links && content.links[linkKey]) {
                    element.href = content.links[linkKey];
                }
            } catch (error) {
                console.warn('Link update error:', error);
            }
        });
    }

    formatCategory(category) {
        const categoryMap = {
            'fine-pitch': 'Fine Pitch LED',
            'outdoor': 'Outdoor LED',
            'indoor': 'Indoor LED',
            'rental': 'Rental LED',
            'creative': 'Creative LED',
            'transparent': 'Transparent LED'
        };
        
        return categoryMap[category] || category.charAt(0).toUpperCase() + category.slice(1);
    }

    startPeriodicSync() {
        // Sync every 30 seconds
        setInterval(() => {
            this.syncData().catch(error => {
                console.warn('Periodic sync error:', error);
            });
        }, 30000);
    }

    async syncData() {
        try {
            const [products, content] = await Promise.all([
                this.loadProducts(),
                this.loadContent()
            ]);
            
            console.log('Data synced successfully');
            return { products, content };
        } catch (error) {
            console.warn('Data sync failed:', error);
            throw error;
        }
    }

    // Public methods for manual sync
    async refreshProducts() {
        return this.loadProducts();
    }

    async refreshContent() {
        return this.loadContent();
    }

    async refreshAll() {
        return this.syncData();
    }

    // Get cached data
    getProducts() {
        return this.cache.get('products') || [];
    }

    getContent() {
        return this.cache.get('content') || {};
    }
}

// Initialize AdminSync when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Only initialize if not already initialized
        if (!window.adminSync) {
            window.adminSync = new AdminSync();
        }
    } catch (error) {
        console.warn('AdminSync initialization failed:', error);
    }
});

// Global error handler
window.addEventListener('error', function(e) {
    console.warn('Global error caught by AdminSync:', e.message);
    e.preventDefault();
    return true;
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdminSync;
}