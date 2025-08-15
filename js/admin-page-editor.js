/**
 * 管理后台页面内容编辑器
 * 提供页面内容的可视化编辑功能
 */

class AdminPageEditor {
    constructor() {
        this.supabase = null;
        this.currentPage = 'index';
        this.pages = [];
        this.pageContents = {};
        this.siteSettings = {};
        this.unsavedChanges = false;
        this.autoSaveTimer = null;
        this.init();
    }

    /**
     * 初始化编辑器
     */
    async init() {
        console.log('🎨 初始化页面内容编辑器...');
        
        // 初始化Supabase
        if (window.supabase) {
            const SUPABASE_URL = 'https://jirudzbqcxviytcmxegf.supabase.co';
            const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y218ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4';
            this.supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
        }

        // 定义所有页面
        this.pages = [
            { name: 'index', title: '首页', icon: 'fa-home' },
            { name: 'about', title: '关于我们', icon: 'fa-info-circle' },
            { name: 'products', title: '产品页', icon: 'fa-box' },
            { name: 'solutions', title: '解决方案', icon: 'fa-lightbulb' },
            { name: 'cases', title: '案例展示', icon: 'fa-briefcase' },
            { name: 'news', title: '新闻动态', icon: 'fa-newspaper' },
            { name: 'contact', title: '联系我们', icon: 'fa-envelope' },
            { name: 'support', title: '技术支持', icon: 'fa-headset' }
        ];

        // 加载初始数据
        await this.loadAllPageContents();
        await this.loadSiteSettings();
        
        console.log('✅ 页面内容编辑器初始化完成');
    }

    /**
     * 创建编辑器界面
     */
    createEditorUI() {
        const editorHTML = `
            <!-- 页面内容编辑器 -->
            <div class="page-editor-container">
                <div class="editor-header">
                    <h4><i class="fas fa-edit"></i> 页面内容编辑器</h4>
                    <div class="editor-actions">
                        <button class="btn btn-sm btn-outline-success" onclick="pageEditor.saveAllChanges()">
                            <i class="fas fa-save"></i> 保存所有
                        </button>
                        <button class="btn btn-sm btn-outline-info" onclick="pageEditor.previewChanges()">
                            <i class="fas fa-eye"></i> 预览
                        </button>
                        <button class="btn btn-sm btn-outline-warning" onclick="pageEditor.resetChanges()">
                            <i class="fas fa-undo"></i> 重置
                        </button>
                    </div>
                </div>

                <!-- 页面选择器 -->
                <div class="page-selector-wrapper">
                    <label class="form-label">选择要编辑的页面：</label>
                    <div class="page-selector-grid">
                        ${this.pages.map(page => `
                            <div class="page-selector-item ${page.name === this.currentPage ? 'active' : ''}" 
                                 data-page="${page.name}" 
                                 onclick="pageEditor.switchPage('${page.name}')">
                                <i class="fas ${page.icon}"></i>
                                <span>${page.title}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- 内容编辑区 -->
                <div class="content-editor-area">
                    <div class="row">
                        <!-- 左侧：编辑表单 -->
                        <div class="col-lg-6">
                            <div class="editor-form-section">
                                <h5 class="section-title">
                                    <i class="fas fa-file-alt"></i> 
                                    <span id="current-page-title">首页</span> 内容编辑
                                </h5>
                                
                                <div id="content-fields-container">
                                    <!-- 动态加载内容字段 -->
                                </div>

                                <!-- SEO设置 -->
                                <div class="seo-section mt-4">
                                    <h6 class="section-subtitle">
                                        <i class="fas fa-search"></i> SEO设置
                                    </h6>
                                    <div class="form-group">
                                        <label>页面标题</label>
                                        <input type="text" class="form-control" id="seo-title" 
                                               placeholder="页面在搜索结果中显示的标题">
                                    </div>
                                    <div class="form-group">
                                        <label>元描述</label>
                                        <textarea class="form-control" id="seo-description" rows="2"
                                                  placeholder="页面在搜索结果中显示的描述"></textarea>
                                    </div>
                                    <div class="form-group">
                                        <label>关键词</label>
                                        <input type="text" class="form-control" id="seo-keywords" 
                                               placeholder="用逗号分隔的关键词">
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 右侧：实时预览 -->
                        <div class="col-lg-6">
                            <div class="preview-section">
                                <h5 class="section-title">
                                    <i class="fas fa-desktop"></i> 实时预览
                                    <button class="btn btn-sm btn-outline-primary float-end" 
                                            onclick="pageEditor.refreshPreview()">
                                        <i class="fas fa-sync"></i>
                                    </button>
                                </h5>
                                
                                <div class="preview-container">
                                    <iframe id="preview-iframe" 
                                            src="about:blank" 
                                            frameborder="0"></iframe>
                                </div>
                                
                                <div class="preview-controls">
                                    <button class="btn btn-sm btn-outline-secondary" 
                                            onclick="pageEditor.setPreviewDevice('desktop')">
                                        <i class="fas fa-desktop"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-secondary" 
                                            onclick="pageEditor.setPreviewDevice('tablet')">
                                        <i class="fas fa-tablet-alt"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-secondary" 
                                            onclick="pageEditor.setPreviewDevice('mobile')">
                                        <i class="fas fa-mobile-alt"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 全局设置 -->
                <div class="global-settings-section mt-4">
                    <h5 class="section-title">
                        <i class="fas fa-cog"></i> 全局网站设置
                    </h5>
                    <div class="row" id="global-settings-container">
                        <!-- 动态加载全局设置 -->
                    </div>
                </div>
            </div>
        `;

        return editorHTML;
    }

    /**
     * 加载所有页面内容
     */
    async loadAllPageContents() {
        if (!this.supabase) return;

        try {
            const { data, error } = await this.supabase
                .from('page_contents')
                .select('*')
                .eq('is_active', true);

            if (error) throw error;

            // 按页面组织内容
            this.pageContents = {};
            data.forEach(item => {
                if (!this.pageContents[item.page_name]) {
                    this.pageContents[item.page_name] = {};
                }
                this.pageContents[item.page_name][item.content_key] = {
                    id: item.id,
                    value: item.content_value,
                    type: item.content_type
                };
            });

            console.log('✅ 加载页面内容成功');
        } catch (error) {
            console.error('加载页面内容失败:', error);
            // 使用默认内容
            this.pageContents = this.getDefaultPageContents();
        }
    }

    /**
     * 加载网站设置
     */
    async loadSiteSettings() {
        if (!this.supabase) return;

        try {
            const { data, error } = await this.supabase
                .from('site_settings')
                .select('*');

            if (error) throw error;

            this.siteSettings = {};
            data.forEach(setting => {
                this.siteSettings[setting.setting_key] = {
                    id: setting.id,
                    value: setting.setting_value,
                    type: setting.setting_type,
                    category: setting.category,
                    description: setting.description
                };
            });

            console.log('✅ 加载网站设置成功');
        } catch (error) {
            console.error('加载网站设置失败:', error);
        }
    }

    /**
     * 切换页面
     */
    switchPage(pageName) {
        this.currentPage = pageName;
        
        // 更新UI
        document.querySelectorAll('.page-selector-item').forEach(item => {
            item.classList.toggle('active', item.dataset.page === pageName);
        });

        // 更新标题
        const pageInfo = this.pages.find(p => p.name === pageName);
        if (pageInfo) {
            document.getElementById('current-page-title').textContent = pageInfo.title;
        }

        // 加载页面内容字段
        this.loadContentFields();
        
        // 刷新预览
        this.refreshPreview();
    }

    /**
     * 加载内容字段
     */
    loadContentFields() {
        const container = document.getElementById('content-fields-container');
        if (!container) return;

        const pageContent = this.pageContents[this.currentPage] || {};
        
        // 定义字段配置
        const fieldConfigs = this.getFieldConfigs();
        
        let html = '';
        fieldConfigs.forEach(config => {
            const content = pageContent[config.key] || { value: '', type: 'text' };
            html += this.createFieldHTML(config, content);
        });

        container.innerHTML = html;

        // 绑定输入事件
        container.querySelectorAll('input, textarea').forEach(field => {
            field.addEventListener('input', (e) => this.handleFieldChange(e));
        });
    }

    /**
     * 获取字段配置
     */
    getFieldConfigs() {
        const configs = {
            'index': [
                { key: 'hero_title', label: 'Hero标题', type: 'text', icon: 'fa-heading' },
                { key: 'hero_subtitle', label: 'Hero副标题', type: 'textarea', icon: 'fa-text-height' },
                { key: 'hero_button_text', label: 'Hero按钮文字', type: 'text', icon: 'fa-mouse-pointer' },
                { key: 'section_title', label: '区块标题', type: 'text', icon: 'fa-h-square' },
                { key: 'section_subtitle', label: '区块副标题', type: 'textarea', icon: 'fa-paragraph' }
            ],
            'about': [
                { key: 'page_title', label: '页面标题', type: 'text', icon: 'fa-heading' },
                { key: 'page_description', label: '页面描述', type: 'textarea', icon: 'fa-file-alt' },
                { key: 'mission_title', label: '使命标题', type: 'text', icon: 'fa-bullseye' },
                { key: 'mission_content', label: '使命内容', type: 'textarea', icon: 'fa-align-left' },
                { key: 'vision_title', label: '愿景标题', type: 'text', icon: 'fa-eye' },
                { key: 'vision_content', label: '愿景内容', type: 'textarea', icon: 'fa-align-left' }
            ],
            'products': [
                { key: 'page_title', label: '页面标题', type: 'text', icon: 'fa-heading' },
                { key: 'page_description', label: '页面描述', type: 'textarea', icon: 'fa-file-alt' },
                { key: 'category_title', label: '分类标题', type: 'text', icon: 'fa-tags' }
            ],
            'contact': [
                { key: 'page_title', label: '页面标题', type: 'text', icon: 'fa-heading' },
                { key: 'page_description', label: '页面描述', type: 'textarea', icon: 'fa-file-alt' },
                { key: 'form_title', label: '表单标题', type: 'text', icon: 'fa-wpforms' },
                { key: 'form_subtitle', label: '表单说明', type: 'textarea', icon: 'fa-info-circle' }
            ]
        };

        // 通用字段（所有页面都有）
        const commonFields = [
            { key: 'breadcrumb_text', label: '面包屑文字', type: 'text', icon: 'fa-chevron-right' }
        ];

        const pageFields = configs[this.currentPage] || [];
        return [...pageFields, ...commonFields];
    }

    /**
     * 创建字段HTML
     */
    createFieldHTML(config, content) {
        const fieldId = `field-${this.currentPage}-${config.key}`;
        
        if (config.type === 'textarea') {
            return `
                <div class="form-group content-field">
                    <label for="${fieldId}">
                        <i class="fas ${config.icon}"></i> ${config.label}
                    </label>
                    <textarea class="form-control" 
                              id="${fieldId}" 
                              data-key="${config.key}"
                              rows="3"
                              placeholder="输入${config.label}...">${content.value || ''}</textarea>
                    <small class="text-muted">字符数: <span class="char-count">${(content.value || '').length}</span></small>
                </div>
            `;
        } else {
            return `
                <div class="form-group content-field">
                    <label for="${fieldId}">
                        <i class="fas ${config.icon}"></i> ${config.label}
                    </label>
                    <input type="text" 
                           class="form-control" 
                           id="${fieldId}" 
                           data-key="${config.key}"
                           value="${content.value || ''}"
                           placeholder="输入${config.label}...">
                </div>
            `;
        }
    }

    /**
     * 处理字段变化
     */
    handleFieldChange(event) {
        const field = event.target;
        const key = field.dataset.key;
        const value = field.value;

        // 更新内存中的数据
        if (!this.pageContents[this.currentPage]) {
            this.pageContents[this.currentPage] = {};
        }
        
        if (!this.pageContents[this.currentPage][key]) {
            this.pageContents[this.currentPage][key] = { type: 'text' };
        }
        
        this.pageContents[this.currentPage][key].value = value;
        this.pageContents[this.currentPage][key].modified = true;

        // 更新字符计数
        if (field.tagName === 'TEXTAREA') {
            const charCount = field.parentElement.querySelector('.char-count');
            if (charCount) {
                charCount.textContent = value.length;
            }
        }

        // 标记有未保存的更改
        this.unsavedChanges = true;
        
        // 自动保存（延迟2秒）
        this.scheduleAutoSave();
        
        // 实时更新预览
        this.updatePreviewContent(key, value);
    }

    /**
     * 保存所有更改
     */
    async saveAllChanges() {
        if (!this.supabase || !this.unsavedChanges) {
            this.showNotification('没有需要保存的更改', 'info');
            return;
        }

        try {
            // 显示保存中状态
            this.showNotification('正在保存...', 'info');

            // 收集所有修改的内容
            const updates = [];
            const inserts = [];

            for (const [pageName, contents] of Object.entries(this.pageContents)) {
                for (const [key, content] of Object.entries(contents)) {
                    if (content.modified) {
                        if (content.id) {
                            // 更新现有记录
                            updates.push({
                                id: content.id,
                                content_value: content.value,
                                updated_at: new Date().toISOString()
                            });
                        } else {
                            // 插入新记录
                            inserts.push({
                                page_name: pageName,
                                content_key: key,
                                content_value: content.value,
                                content_type: content.type || 'text',
                                is_active: true
                            });
                        }
                    }
                }
            }

            // 执行更新
            if (updates.length > 0) {
                for (const update of updates) {
                    const { error } = await this.supabase
                        .from('page_contents')
                        .update(update)
                        .eq('id', update.id);
                    
                    if (error) throw error;
                }
            }

            // 执行插入
            if (inserts.length > 0) {
                const { data, error } = await this.supabase
                    .from('page_contents')
                    .insert(inserts)
                    .select();
                
                if (error) throw error;

                // 更新本地数据的ID
                data.forEach(item => {
                    if (this.pageContents[item.page_name] && 
                        this.pageContents[item.page_name][item.content_key]) {
                        this.pageContents[item.page_name][item.content_key].id = item.id;
                    }
                });
            }

            // 清除修改标记
            for (const contents of Object.values(this.pageContents)) {
                for (const content of Object.values(contents)) {
                    content.modified = false;
                }
            }

            this.unsavedChanges = false;
            this.showNotification('✅ 所有更改已保存成功！', 'success');
            
        } catch (error) {
            console.error('保存失败:', error);
            this.showNotification('❌ 保存失败: ' + error.message, 'error');
        }
    }

    /**
     * 自动保存调度
     */
    scheduleAutoSave() {
        // 清除之前的定时器
        if (this.autoSaveTimer) {
            clearTimeout(this.autoSaveTimer);
        }

        // 设置新的定时器（2秒后自动保存）
        this.autoSaveTimer = setTimeout(() => {
            this.saveAllChanges();
        }, 2000);
    }

    /**
     * 刷新预览
     */
    refreshPreview() {
        const iframe = document.getElementById('preview-iframe');
        if (!iframe) return;

        // 加载当前页面
        const pageUrl = `/${this.currentPage === 'index' ? '' : this.currentPage + '.html'}`;
        iframe.src = pageUrl;

        // 等待iframe加载完成后更新内容
        iframe.onload = () => {
            this.updateAllPreviewContent();
        };
    }

    /**
     * 更新预览内容
     */
    updatePreviewContent(key, value) {
        const iframe = document.getElementById('preview-iframe');
        if (!iframe || !iframe.contentDocument) return;

        const doc = iframe.contentDocument;
        
        // 查找并更新对应的元素
        const elements = doc.querySelectorAll(`[data-content="${key}"]`);
        elements.forEach(el => {
            el.textContent = value;
        });

        // 智能查找其他可能的元素
        const selectors = this.getPreviewSelectors(key);
        selectors.forEach(selector => {
            try {
                const els = doc.querySelectorAll(selector);
                els.forEach(el => {
                    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                        el.value = value;
                    } else {
                        el.textContent = value;
                    }
                });
            } catch (e) {
                // 忽略无效选择器
            }
        });
    }

    /**
     * 更新所有预览内容
     */
    updateAllPreviewContent() {
        const pageContent = this.pageContents[this.currentPage] || {};
        
        for (const [key, content] of Object.entries(pageContent)) {
            if (content.value) {
                this.updatePreviewContent(key, content.value);
            }
        }
    }

    /**
     * 获取预览选择器
     */
    getPreviewSelectors(key) {
        const selectors = {
            'hero_title': ['.hero-title', 'h1.hero-title'],
            'hero_subtitle': ['.hero-subtitle', 'p.hero-subtitle'],
            'section_title': ['.section-title', 'h2.section-title'],
            'section_subtitle': ['.section-subtitle', 'p.section-subtitle'],
            'page_title': ['h1.page-title', '.page-header h1']
        };
        
        return selectors[key] || [];
    }

    /**
     * 设置预览设备
     */
    setPreviewDevice(device) {
        const container = document.querySelector('.preview-container');
        if (!container) return;

        // 移除所有设备类
        container.classList.remove('preview-desktop', 'preview-tablet', 'preview-mobile');
        
        // 添加新的设备类
        container.classList.add(`preview-${device}`);
    }

    /**
     * 重置更改
     */
    resetChanges() {
        if (!confirm('确定要重置所有未保存的更改吗？')) return;

        // 重新加载数据
        this.loadAllPageContents().then(() => {
            this.loadContentFields();
            this.refreshPreview();
            this.unsavedChanges = false;
            this.showNotification('已重置所有更改', 'info');
        });
    }

    /**
     * 显示通知
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification-toast`;
        notification.innerHTML = message;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 10000;
            min-width: 250px;
            animation: slideInRight 0.3s ease;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    /**
     * 获取默认页面内容
     */
    getDefaultPageContents() {
        return {
            'index': {
                'hero_title': { value: 'Professional LED Display Solutions', type: 'text' },
                'hero_subtitle': { value: 'Leading provider of high-quality LED displays', type: 'text' },
                'section_title': { value: 'Our Products', type: 'text' }
            },
            'about': {
                'page_title': { value: 'About Us', type: 'text' },
                'page_description': { value: 'Learn about our company', type: 'text' }
            }
        };
    }
}

// 添加样式
const editorStyles = `
<style>
.page-editor-container {
    padding: 20px;
    background: #f8f9fa;
    border-radius: 10px;
}

.editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    padding-bottom: 15px;
    border-bottom: 2px solid #dee2e6;
}

.page-selector-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 15px;
    margin-top: 15px;
}

.page-selector-item {
    text-align: center;
    padding: 15px;
    background: white;
    border: 2px solid #dee2e6;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.page-selector-item:hover {
    border-color: #667eea;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.page-selector-item.active {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border-color: #667eea;
}

.page-selector-item i {
    display: block;
    font-size: 24px;
    margin-bottom: 8px;
}

.editor-form-section,
.preview-section {
    background: white;
    padding: 25px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

.section-title {
    color: #495057;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #e9ecef;
}

.section-subtitle {
    color: #6c757d;
    font-size: 16px;
    font-weight: 500;
    margin-bottom: 15px;
}

.content-field {
    margin-bottom: 20px;
}

.content-field label {
    color: #495057;
    font-weight: 500;
    margin-bottom: 8px;
    display: block;
}

.content-field label i {
    color: #667eea;
    margin-right: 5px;
}

.preview-container {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.3s ease;
}

.preview-container iframe {
    width: 100%;
    height: 500px;
    background: white;
}

.preview-container.preview-tablet {
    max-width: 768px;
    margin: 0 auto;
}

.preview-container.preview-mobile {
    max-width: 375px;
    margin: 0 auto;
}

.preview-controls {
    margin-top: 15px;
    text-align: center;
}

.preview-controls .btn {
    margin: 0 5px;
}

.global-settings-section {
    background: white;
    padding: 25px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

.char-count {
    font-weight: 600;
    color: #667eea;
}

.notification-toast {
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.seo-section {
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
}

@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes slideOutRight {
    from {
        transform: translateX(0);
        opacity: 1;
    }
    to {
        transform: translateX(100%);
        opacity: 0;
    }
}
</style>
`;

// 添加样式到页面
if (!document.getElementById('page-editor-styles')) {
    const styleElement = document.createElement('div');
    styleElement.id = 'page-editor-styles';
    styleElement.innerHTML = editorStyles;
    document.head.appendChild(styleElement);
}

// 创建全局实例
window.pageEditor = new AdminPageEditor();

console.log('📝 管理后台页面编辑器已加载');
