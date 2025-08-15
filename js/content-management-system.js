/**
 * 完整的页面内容管理系统
 * 解决静态HTML内容无法通过后台修改的问题
 */

class ContentManagementSystem {
    constructor() {
        this.isInitialized = false;
        this.contentElements = new Map();
        this.defaultContent = {};
        this.currentContent = {};
        this.init();
    }

    /**
     * 初始化内容管理系统
     */
    async init() {
        console.log('🚀 内容管理系统初始化中...');
        
        // 等待DOM加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupSystem());
        } else {
            this.setupSystem();
        }
    }

    /**
     * 设置系统
     */
    async setupSystem() {
        try {
            // 1. 记录所有可编辑元素的默认值
            this.recordDefaultContent();
            
            // 2. 加载保存的内容
            await this.loadSavedContent();
            
            // 3. 应用内容到页面
            this.applyContentToPage();
            
            // 4. 监听内容变更
            this.setupContentListener();
            
            this.isInitialized = true;
            console.log('✅ 内容管理系统初始化完成');
            
        } catch (error) {
            console.error('❌ 内容管理系统初始化失败:', error);
        }
    }

    /**
     * 记录页面默认内容
     */
    recordDefaultContent() {
        const pageName = this.getCurrentPageName();
        
        // 定义可编辑的内容区域选择器
        const editableSelectors = {
            // Hero区域
            hero_title: 'h1.hero-title, .hero-title',
            hero_subtitle: 'p.hero-subtitle, .hero-subtitle',
            hero_description: '.hero-content p:not(.hero-subtitle)',
            
            // 页面标题和副标题
            page_title: 'h1.page-title, .page-title',
            section_title: 'h2.section-title, .section-title',
            section_subtitle: 'p.section-subtitle, .section-subtitle',
            
            // 导航品牌
            brand_name: '.navbar-brand span',
            
            // 页面特定内容
            page_description: '.page-description, .lead',
            
            // Footer内容
            footer_description: 'footer p',
            
            // 公司信息
            company_name: '.company-name',
            company_description: '.company-description'
        };

        // 记录每个可编辑元素的默认值
        Object.entries(editableSelectors).forEach(([key, selector]) => {
            const element = document.querySelector(selector);
            if (element) {
                const defaultValue = element.textContent.trim();
                if (defaultValue) {
                    this.contentElements.set(key, { selector, element, defaultValue });
                    
                    // 初始化默认内容
                    if (!this.defaultContent[pageName]) {
                        this.defaultContent[pageName] = {};
                    }
                    this.defaultContent[pageName][key] = defaultValue;
                }
            }
        });

        console.log(`📋 记录了${pageName}页面的${this.contentElements.size}个可编辑元素`);
    }

    /**
     * 加载保存的内容
     */
    async loadSavedContent() {
        const pageName = this.getCurrentPageName();
        
        try {
            // 优先从统一API获取
            if (window.unifiedDataAPI) {
                const savedContent = await window.unifiedDataAPI.getPageContent(pageName);
                if (savedContent && savedContent.elements) {
                    this.currentContent[pageName] = savedContent.elements;
                    console.log(`📥 从统一API加载了${pageName}页面内容`);
                    return;
                }
            }
            
            // 从localStorage获取
            const savedPages = JSON.parse(localStorage.getItem('cms_content') || '{}');
            if (savedPages[pageName]) {
                this.currentContent[pageName] = savedPages[pageName];
                console.log(`📥 从localStorage加载了${pageName}页面内容`);
                return;
            }
            
            // 使用默认内容
            this.currentContent[pageName] = this.defaultContent[pageName] || {};
            console.log(`📄 使用${pageName}页面的默认内容`);
            
        } catch (error) {
            console.error('加载保存内容失败:', error);
            this.currentContent[pageName] = this.defaultContent[pageName] || {};
        }
    }

    /**
     * 应用内容到页面
     */
    applyContentToPage() {
        const pageName = this.getCurrentPageName();
        const pageContent = this.currentContent[pageName] || {};
        
        let updatedCount = 0;
        
        this.contentElements.forEach((elementInfo, key) => {
            const { element, defaultValue } = elementInfo;
            const savedValue = pageContent[key];
            
            if (savedValue && savedValue !== defaultValue) {
                element.textContent = savedValue;
                element.setAttribute('data-cms-modified', 'true');
                updatedCount++;
            }
        });

        if (updatedCount > 0) {
            console.log(`✨ 更新了${updatedCount}个页面元素的内容`);
            this.showUpdateNotification(updatedCount);
        }
    }

    /**
     * 保存页面内容
     */
    async savePageContent(contentData) {
        const pageName = this.getCurrentPageName();
        
        try {
            // 更新当前内容
            if (!this.currentContent[pageName]) {
                this.currentContent[pageName] = {};
            }
            
            Object.assign(this.currentContent[pageName], contentData);
            
            // 保存到统一API
            if (window.unifiedDataAPI) {
                const success = await window.unifiedDataAPI.savePageContent(pageName, {
                    elements: this.currentContent[pageName],
                    updated_at: new Date().toISOString()
                });
                
                if (success) {
                    console.log('✅ 内容保存到统一API成功');
                } else {
                    throw new Error('统一API保存失败');
                }
            } else {
                // 保存到localStorage
                const allContent = JSON.parse(localStorage.getItem('cms_content') || '{}');
                allContent[pageName] = this.currentContent[pageName];
                localStorage.setItem('cms_content', JSON.stringify(allContent));
                console.log('✅ 内容保存到localStorage成功');
            }
            
            // 立即应用到页面
            this.applyContentToPage();
            
            return true;
        } catch (error) {
            console.error('❌ 保存页面内容失败:', error);
            return false;
        }
    }

    /**
     * 获取页面所有可编辑内容
     */
    getEditableContent() {
        const pageName = this.getCurrentPageName();
        const result = {};
        
        this.contentElements.forEach((elementInfo, key) => {
            const { element, defaultValue } = elementInfo;
            result[key] = {
                current: element.textContent.trim(),
                default: defaultValue,
                modified: element.hasAttribute('data-cms-modified')
            };
        });
        
        return {
            pageName,
            elements: result,
            totalElements: this.contentElements.size
        };
    }

    /**
     * 重置页面内容到默认值
     */
    resetToDefault() {
        const pageName = this.getCurrentPageName();
        let resetCount = 0;
        
        this.contentElements.forEach((elementInfo, key) => {
            const { element, defaultValue } = elementInfo;
            if (element.hasAttribute('data-cms-modified')) {
                element.textContent = defaultValue;
                element.removeAttribute('data-cms-modified');
                resetCount++;
            }
        });
        
        // 清除保存的内容
        if (this.currentContent[pageName]) {
            this.currentContent[pageName] = {};
        }
        
        console.log(`🔄 重置了${resetCount}个元素到默认值`);
        return resetCount;
    }

    /**
     * 设置内容变更监听器
     */
    setupContentListener() {
        // 监听数据更新事件
        window.addEventListener('dataUpdated', (event) => {
            if (event.detail.type === 'page_content') {
                console.log('📢 收到页面内容更新通知');
                setTimeout(() => {
                    this.loadSavedContent().then(() => {
                        this.applyContentToPage();
                    });
                }, 100);
            }
        });

        // 监听localStorage变更
        window.addEventListener('storage', (event) => {
            if (event.key === 'cms_content') {
                console.log('📢 检测到CMS内容变更');
                setTimeout(() => {
                    this.loadSavedContent().then(() => {
                        this.applyContentToPage();
                    });
                }, 100);
            }
        });
    }

    /**
     * 获取当前页面名称
     */
    getCurrentPageName() {
        const path = window.location.pathname;
        const filename = path.split('/').pop() || 'index.html';
        
        if (filename === 'index.html' || filename === '') return 'home';
        if (filename.includes('about')) return 'about';
        if (filename.includes('products')) return 'products';
        if (filename.includes('solutions')) return 'solutions';
        if (filename.includes('cases')) return 'cases';
        if (filename.includes('news')) return 'news';
        if (filename.includes('support')) return 'support';
        if (filename.includes('contact')) return 'contact';
        if (filename.includes('fine-pitch')) return 'fine-pitch';
        if (filename.includes('outdoor')) return 'outdoor';
        if (filename.includes('rental')) return 'rental';
        if (filename.includes('creative')) return 'creative';
        if (filename.includes('transparent')) return 'transparent';
        
        return filename.replace('.html', '') || 'home';
    }

    /**
     * 显示更新通知
     */
    showUpdateNotification(count) {
        const notification = document.createElement('div');
        notification.className = 'cms-update-notification';
        notification.innerHTML = `✨ 已更新 ${count} 处页面内容`;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            font-size: 14px;
            font-weight: bold;
            z-index: 10001;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        `;

        document.body.appendChild(notification);

        // 显示动画
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 100);

        // 隐藏动画
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    /**
     * 创建管理界面按钮
     */
    createManagementButton() {
        const button = document.createElement('button');
        button.innerHTML = '📝';
        button.title = '页面内容管理';
        button.style.cssText = `
            position: fixed;
            top: 80px;
            left: 20px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            border: none;
            background: #28a745;
            color: white;
            cursor: pointer;
            z-index: 10000;
            font-size: 18px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        `;
        
        button.addEventListener('click', () => {
            this.showContentManagementModal();
        });
        
        button.addEventListener('mouseenter', () => {
            button.style.transform = 'scale(1.1)';
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.transform = 'scale(1)';
        });
        
        document.body.appendChild(button);
    }

    /**
     * 显示内容管理模态框
     */
    showContentManagementModal() {
        const content = this.getEditableContent();
        
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 10002;
            display: flex;
            justify-content: center;
            align-items: center;
        `;
        
        const modalContent = document.createElement('div');
        modalContent.style.cssText = `
            background: white;
            padding: 20px;
            border-radius: 10px;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        `;
        
        let elementsHtml = '';
        Object.entries(content.elements).forEach(([key, info]) => {
            elementsHtml += `
                <div style="margin-bottom: 15px;">
                    <label style="font-weight: bold; display: block; margin-bottom: 5px;">
                        ${key.replace(/_/g, ' ').toUpperCase()}
                        ${info.modified ? '<span style="color: #28a745;">(已修改)</span>' : ''}
                    </label>
                    <textarea 
                        id="cms-${key}" 
                        style="width: 100%; min-height: 60px; padding: 8px; border: 1px solid #ddd; border-radius: 4px;"
                    >${info.current}</textarea>
                    <small style="color: #666;">默认: ${info.default}</small>
                </div>
            `;
        });
        
        modalContent.innerHTML = `
            <h3>页面内容管理 - ${content.pageName}</h3>
            <p>共 ${content.totalElements} 个可编辑元素</p>
            <hr>
            ${elementsHtml}
            <div style="margin-top: 20px; display: flex; gap: 10px;">
                <button id="cms-save" style="padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px;">保存</button>
                <button id="cms-reset" style="padding: 8px 16px; background: #dc3545; color: white; border: none; border-radius: 4px;">重置</button>
                <button id="cms-close" style="padding: 8px 16px; background: #6c757d; color: white; border: none; border-radius: 4px;">关闭</button>
            </div>
        `;
        
        modal.appendChild(modalContent);
        document.body.appendChild(modal);
        
        // 绑定事件
        modal.querySelector('#cms-save').addEventListener('click', () => {
            const newContent = {};
            Object.keys(content.elements).forEach(key => {
                const textarea = modal.querySelector(`#cms-${key}`);
                if (textarea) {
                    newContent[key] = textarea.value.trim();
                }
            });
            
            this.savePageContent(newContent).then(success => {
                if (success) {
                    alert('内容保存成功！');
                    modal.remove();
                } else {
                    alert('保存失败，请重试！');
                }
            });
        });
        
        modal.querySelector('#cms-reset').addEventListener('click', () => {
            if (confirm('确定要重置所有内容到默认值吗？')) {
                const resetCount = this.resetToDefault();
                alert(`已重置 ${resetCount} 个元素到默认值`);
                modal.remove();
            }
        });
        
        modal.querySelector('#cms-close').addEventListener('click', () => {
            modal.remove();
        });
        
        // 点击背景关闭
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }
}

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    // 延迟初始化，确保其他脚本都已加载
    setTimeout(() => {
        window.contentManagementSystem = new ContentManagementSystem();
        
        // 在开发环境添加管理按钮
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            window.contentManagementSystem.createManagementButton();
        }
    }, 1500);
});

console.log('📦 内容管理系统已加载');
