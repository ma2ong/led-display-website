/**
 * 前后端联动同步系统
 * 实现前端与后端API的完整集成
 */

class FrontendBackendSync {
    constructor() {
        this.apiBaseUrl = this.detectApiUrl();
        this.init();
    }

    // 自动检测API URL
    detectApiUrl() {
        const hostname = window.location.hostname;
        const protocol = window.location.protocol;
        
        // 如果是Vercel部署环境
        if (hostname.includes('vercel.app')) {
            return `${protocol}//${hostname}`;
        }
        
        // 如果是本地开发环境
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://localhost:8080';
        }
        
        // 默认使用当前域名
        return `${protocol}//${hostname}`;
    }

    // 初始化系统
    init() {
        this.setupContactForm();
        this.setupProductInquiry();
        this.setupNewsletterSubscription();
        this.loadDynamicContent();
        console.log('✓ Frontend-Backend sync initialized');
    }

    // 设置联系表单
    setupContactForm() {
        const contactForms = document.querySelectorAll('[data-contact-form]');
        contactForms.forEach(form => {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleContactSubmission(form);
            });
        });
    }

    // 处理联系表单提交
    async handleContactSubmission(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        
        try {
            // 显示加载状态
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Sending...';
            
            // 收集表单数据
            const formData = new FormData(form);
            const data = this.formatContactData(formData);
            
            // 发送到后端API
            const response = await this.apiRequest('/api/contact', 'POST', data);
            
            if (response.status === 'success') {
                this.showNotification('Thank you! We will contact you within 24 hours.', 'success');
                form.reset();
                form.classList.remove('was-validated');
            } else {
                throw new Error(response.message || 'Submission failed');
            }
            
        } catch (error) {
            console.error('Contact form error:', error);
            this.showNotification(error.message || 'Failed to submit. Please try again.', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    }

    // 格式化联系数据
    formatContactData(formData) {
        const firstName = formData.get('first_name') || '';
        const lastName = formData.get('last_name') || '';
        const fullName = `${firstName} ${lastName}`.trim();
        
        return {
            name: fullName || formData.get('name') || '',
            email: formData.get('email') || '',
            company: formData.get('company') || '',
            phone: formData.get('phone') || '',
            product: formData.get('product') || formData.get('productInterest') || '',
            subject: formData.get('subject') || 'General Inquiry',
            message: formData.get('message') || '',
            source: window.location.pathname,
            timestamp: new Date().toISOString()
        };
    }

    // 设置产品询盘功能
    setupProductInquiry() {
        // 处理产品页面的询盘按钮
        const inquiryButtons = document.querySelectorAll('[data-product-inquiry]');
        inquiryButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const productName = button.dataset.productName || 'Unknown Product';
                this.openInquiryModal(productName);
            });
        });

        // 检查URL参数中的产品信息
        this.checkProductParams();
    }

    // 检查URL参数中的产品信息
    checkProductParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const product = urlParams.get('product');
        const inquiry = urlParams.get('inquiry');
        
        if (product && inquiry === 'true') {
            // 自动填充产品信息到联系表单
            this.prefillProductInfo(product);
        }
    }

    // 预填充产品信息
    prefillProductInfo(productName) {
        const productSelect = document.getElementById('productInterest');
        const subjectField = document.getElementById('subject');
        const messageField = document.getElementById('message');
        
        if (productSelect) {
            // 尝试匹配产品类型
            const productMap = {
                'fine-pitch': 'fine-pitch',
                'outdoor': 'outdoor',
                'rental': 'rental',
                'creative': 'creative',
                'transparent': 'transparent',
                'indoor': 'indoor'
            };
            
            const productType = Object.keys(productMap).find(key => 
                productName.toLowerCase().includes(key)
            );
            
            if (productType) {
                productSelect.value = productMap[productType];
            }
        }
        
        if (subjectField && !subjectField.value) {
            subjectField.value = `Inquiry about ${productName}`;
        }
        
        if (messageField && !messageField.value) {
            messageField.value = `I am interested in learning more about ${productName}. Please provide detailed information including specifications, pricing, and availability.`;
        }
    }

    // 打开询盘模态框
    openInquiryModal(productName) {
        // 如果在联系页面，直接滚动到表单
        if (window.location.pathname.includes('contact.html')) {
            this.prefillProductInfo(productName);
            document.getElementById('contact-form').scrollIntoView({ behavior: 'smooth' });
            return;
        }
        
        // 否则跳转到联系页面
        window.location.href = `contact.html?product=${encodeURIComponent(productName)}&inquiry=true`;
    }

    // 设置新闻订阅
    setupNewsletterSubscription() {
        const newsletterForms = document.querySelectorAll('[data-newsletter-form]');
        newsletterForms.forEach(form => {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleNewsletterSubscription(form);
            });
        });
    }

    // 处理新闻订阅
    async handleNewsletterSubscription(form) {
        const emailInput = form.querySelector('input[type="email"]');
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (!emailInput.value) {
            this.showNotification('Please enter your email address', 'error');
            return;
        }
        
        try {
            submitBtn.disabled = true;
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Subscribing...';
            
            const response = await this.apiRequest('/api/newsletter', 'POST', {
                email: emailInput.value,
                source: window.location.pathname
            });
            
            if (response.status === 'success') {
                this.showNotification('Successfully subscribed to newsletter!', 'success');
                emailInput.value = '';
            } else {
                throw new Error(response.message || 'Subscription failed');
            }
            
        } catch (error) {
            console.error('Newsletter subscription error:', error);
            this.showNotification(error.message || 'Subscription failed', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Subscribe';
        }
    }

    // 加载动态内容
    async loadDynamicContent() {
        try {
            // 加载最新新闻
            await this.loadLatestNews();
            
            // 加载产品信息
            await this.loadProductInfo();
            
            // 加载公司统计
            await this.loadCompanyStats();
            
        } catch (error) {
            console.error('Failed to load dynamic content:', error);
        }
    }

    // 加载最新新闻
    async loadLatestNews() {
        try {
            const response = await this.apiRequest('/api/news/latest', 'GET');
            if (response.status === 'success' && response.data) {
                this.updateNewsSection(response.data);
            }
        } catch (error) {
            console.error('Failed to load latest news:', error);
        }
    }

    // 更新新闻区域
    updateNewsSection(newsData) {
        const newsContainer = document.querySelector('[data-latest-news]');
        if (!newsContainer || !newsData.length) return;
        
        const newsHTML = newsData.slice(0, 3).map(news => `
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    <img src="${news.image || 'assets/news/news-thumb-1.jpg'}" class="card-img-top" alt="${news.title}">
                    <div class="card-body">
                        <h6 class="card-title">${news.title}</h6>
                        <p class="card-text text-muted small">${news.summary || news.content.substring(0, 100)}...</p>
                        <small class="text-muted">${new Date(news.created_at).toLocaleDateString()}</small>
                    </div>
                </div>
            </div>
        `).join('');
        
        newsContainer.innerHTML = newsHTML;
    }

    // 加载产品信息
    async loadProductInfo() {
        try {
            const response = await this.apiRequest('/api/products/featured', 'GET');
            if (response.status === 'success' && response.data) {
                this.updateProductSection(response.data);
            }
        } catch (error) {
            console.error('Failed to load product info:', error);
        }
    }

    // 更新产品区域
    updateProductSection(productData) {
        const productContainer = document.querySelector('[data-featured-products]');
        if (!productContainer || !productData.length) return;
        
        const productHTML = productData.slice(0, 4).map(product => `
            <div class="col-lg-3 col-md-6 mb-4">
                <div class="card product-card h-100">
                    <img src="${product.image || 'assets/products/product-detail-1.jpg'}" class="card-img-top" alt="${product.name}">
                    <div class="card-body">
                        <h6 class="card-title">${product.name}</h6>
                        <p class="card-text text-muted small">${product.description}</p>
                        <button class="btn btn-primary btn-sm" data-product-inquiry data-product-name="${product.name}">
                            <i class="fas fa-envelope me-1"></i>Inquire
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
        
        productContainer.innerHTML = productHTML;
        
        // 重新绑定询盘按钮事件
        this.setupProductInquiry();
    }

    // 加载公司统计
    async loadCompanyStats() {
        try {
            const response = await this.apiRequest('/api/stats/company', 'GET');
            if (response.status === 'success' && response.data) {
                this.updateStatsSection(response.data);
            }
        } catch (error) {
            console.error('Failed to load company stats:', error);
        }
    }

    // 更新统计区域
    updateStatsSection(statsData) {
        const statsContainer = document.querySelector('[data-company-stats]');
        if (!statsContainer) return;
        
        const stats = {
            projects: statsData.total_projects || 1000,
            clients: statsData.total_clients || 500,
            countries: statsData.countries_served || 50,
            experience: statsData.years_experience || 17
        };
        
        // 更新统计数字
        Object.keys(stats).forEach(key => {
            const element = document.querySelector(`[data-stat="${key}"]`);
            if (element) {
                this.animateCounter(element, stats[key]);
            }
        });
    }

    // 数字动画效果
    animateCounter(element, target) {
        const duration = 2000;
        const start = 0;
        const increment = target / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current).toLocaleString();
        }, 16);
    }

    // API请求封装
    async apiRequest(endpoint, method = 'GET', data = null) {
        const url = `${this.apiBaseUrl}${endpoint}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(url, options);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${method} ${endpoint}`, error);
            throw error;
        }
    }

    // 显示通知
    showNotification(message, type = 'info') {
        // 移除现有通知
        const existingNotifications = document.querySelectorAll('.sync-notification');
        existingNotifications.forEach(notification => notification.remove());
        
        // 创建新通知
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} alert-dismissible fade show sync-notification`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        
        const icon = type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle';
        
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-${icon} me-2"></i>
                <span>${message}</span>
                <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // 自动移除
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    window.frontendBackendSync = new FrontendBackendSync();
});

// 导出供其他脚本使用
window.FrontendBackendSync = FrontendBackendSync;