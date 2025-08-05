/**
 * Contact Form API Integration
 * 联系表单API集成
 */

class ContactAPI {
    constructor() {
        this.apiBaseUrl = 'http://localhost:5000/api';
        this.init();
    }

    init() {
        // 绑定联系表单提交事件
        const contactForms = document.querySelectorAll('form[data-contact-form]');
        contactForms.forEach(form => {
            form.addEventListener('submit', (e) => this.handleContactSubmit(e));
        });

        // 绑定报价表单提交事件
        const quoteForms = document.querySelectorAll('form[data-quote-form]');
        quoteForms.forEach(form => {
            form.addEventListener('submit', (e) => this.handleQuoteSubmit(e));
        });
    }

    async handleContactSubmit(event) {
        event.preventDefault();
        
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        
        try {
            // 显示加载状态
            submitBtn.disabled = true;
            submitBtn.textContent = 'Sending...';
            
            // 收集表单数据
            const formData = new FormData(form);
            const data = {
                name: formData.get('name'),
                email: formData.get('email'),
                company: formData.get('company') || '',
                phone: formData.get('phone') || '',
                product: formData.get('product') || '',
                message: formData.get('message')
            };
            
            // 验证必填字段
            if (!data.name || !data.email || !data.message) {
                throw new Error('Please fill in all required fields');
            }
            
            // 发送API请求
            const response = await fetch(`${this.apiBaseUrl}/contact`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.showSuccess(result.message || 'Thank you for your inquiry! We will contact you soon.');
                form.reset();
            } else {
                throw new Error(result.message || 'Failed to submit inquiry');
            }
            
        } catch (error) {
            console.error('Contact form error:', error);
            this.showError(error.message || 'Failed to submit inquiry. Please try again.');
        } finally {
            // 恢复按钮状态
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }

    async handleQuoteSubmit(event) {
        event.preventDefault();
        
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        
        try {
            // 显示加载状态
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';
            
            // 收集表单数据
            const formData = new FormData(form);
            const data = {
                name: formData.get('name'),
                email: formData.get('email'),
                company: formData.get('company'),
                product_type: formData.get('product_type') || '',
                display_size: formData.get('display_size') || '',
                quantity: formData.get('quantity') || '',
                requirements: formData.get('requirements') || '',
                timeline: formData.get('timeline') || '',
                budget: formData.get('budget') || ''
            };
            
            // 验证必填字段
            if (!data.name || !data.email || !data.company) {
                throw new Error('Please fill in all required fields');
            }
            
            // 发送API请求
            const response = await fetch(`${this.apiBaseUrl}/quote`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.showSuccess(result.message || 'Thank you for your quote request! We will prepare a customized quote for you.');
                form.reset();
            } else {
                throw new Error(result.message || 'Failed to submit quote request');
            }
            
        } catch (error) {
            console.error('Quote form error:', error);
            this.showError(error.message || 'Failed to submit quote request. Please try again.');
        } finally {
            // 恢复按钮状态
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }

    showSuccess(message) {
        // 创建成功提示
        const alert = this.createAlert(message, 'success');
        this.showAlert(alert);
    }

    showError(message) {
        // 创建错误提示
        const alert = this.createAlert(message, 'error');
        this.showAlert(alert);
    }

    createAlert(message, type) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
        alert.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        
        alert.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
                <span>${message}</span>
                <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        return alert;
    }

    showAlert(alert) {
        document.body.appendChild(alert);
        
        // 自动隐藏
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    // 获取产品数据
    async getProducts() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/products`);
            const result = await response.json();
            
            if (result.status === 'success') {
                return result.products;
            } else {
                throw new Error(result.message || 'Failed to fetch products');
            }
        } catch (error) {
            console.error('Failed to fetch products:', error);
            return [];
        }
    }

    // 获取统计数据
    async getStats() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/stats`);
            const result = await response.json();
            
            if (result.status === 'success') {
                return result.stats;
            } else {
                throw new Error(result.message || 'Failed to fetch stats');
            }
        } catch (error) {
            console.error('Failed to fetch stats:', error);
            return null;
        }
    }
}

// 初始化API
document.addEventListener('DOMContentLoaded', () => {
    window.contactAPI = new ContactAPI();
    
    // 全局错误处理
    window.addEventListener('error', (e) => {
        console.warn('Global error caught:', e.message);
        e.preventDefault();
        return true;
    });
    
    // 防止未处理的Promise rejection
    window.addEventListener('unhandledrejection', (e) => {
        console.warn('Unhandled promise rejection:', e.reason);
        e.preventDefault();
    });
});

// 导出API类供其他脚本使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ContactAPI;
}