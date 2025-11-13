/**
 * 页面编辑器主脚本
 * 负责加载编辑界面、处理数据保存、实时预览等功能
 */

let currentPage = 'index';
let currentPageData = {};
let hasUnsavedChanges = false;
let supabaseClient = null;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎨 页面编辑器初始化...');

    // 初始化Supabase
    initSupabase();

    // 初始化默认数据
    initializeDefaultData();

    // 加载首页编辑器
    loadPageEditor('index');

    // 监听页面关闭（提醒未保存的更改）
    window.addEventListener('beforeunload', function(e) {
        if (hasUnsavedChanges) {
            e.preventDefault();
            e.returnValue = '';
        }
    });
});

// 初始化Supabase客户端
function initSupabase() {
    if (!window.supabase) {
        console.warn('⚠️ Supabase SDK 未加载');
        return;
    }

    const { createClient } = window.supabase;
    const supabaseUrl = 'https://jirudzbqcxviytcmxegf.supabase.co';
    const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y214ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4';

    supabaseClient = createClient(supabaseUrl, supabaseKey);
    console.log('✅ Supabase 客户端初始化成功');
}

// 加载页面编辑器
function loadPageEditor(pageId) {
    console.log(`📄 加载 ${pageId} 页面编辑器`);

    // 如果有未保存的更改，提醒用户
    if (hasUnsavedChanges && currentPage !== pageId) {
        if (!confirm('您有未保存的更改，确定要离开吗？')) {
            return;
        }
    }

    currentPage = pageId;
    currentPageData = loadPageData(pageId);
    hasUnsavedChanges = false;

    // 更新菜单激活状态
    document.querySelectorAll('.page-menu-link').forEach(link => {
        link.classList.remove('active');
    });
    event.target.closest('.page-menu-link').classList.add('active');

    // 根据页面类型加载不同的编辑器
    switch(pageId) {
        case 'index':
            renderIndexEditor();
            break;
        case 'products':
            renderProductsEditor();
            break;
        case 'about':
            renderAboutEditor();
            break;
        case 'contact':
            renderContactEditor();
            break;
        case 'news':
            renderNewsEditor();
            break;
        default:
            renderDefaultEditor(pageId);
    }

    // 更新预览
    refreshPreview();
}

// 渲染首页编辑器
function renderIndexEditor() {
    const editorArea = document.getElementById('editorArea');
    const data = currentPageData;

    editorArea.innerHTML = `
        <div class="mb-4">
            <h3><i class="fas fa-home"></i> 首页内容编辑</h3>
            <p class="text-muted">编辑首页的所有内容，保存后会自动更新到前端网站</p>
        </div>

        <!-- Hero 轮播图区域 -->
        <div class="editor-section">
            <div class="section-header">
                <div class="section-title">
                    <i class="fas fa-images"></i>
                    Hero 轮播图
                </div>
                <button class="btn btn-sm btn-outline-primary" onclick="addHeroSlide()">
                    <i class="fas fa-plus"></i> 添加轮播图
                </button>
            </div>

            <div id="heroSlidesContainer">
                ${data.hero.slides.map((slide, index) => renderHeroSlideEditor(slide, index)).join('')}
            </div>
        </div>

        <!-- 产品展示区域 -->
        <div class="editor-section">
            <div class="section-header">
                <div class="section-title">
                    <i class="fas fa-cube"></i>
                    产品展示区域
                </div>
            </div>

            <div class="row mb-3">
                <div class="col-md-6">
                    <label class="form-label">区域标题</label>
                    <input type="text" class="form-control" value="${data.products.sectionTitle}"
                           onchange="updateProductsSectionTitle(this.value)">
                </div>
                <div class="col-md-6">
                    <label class="form-label">区域副标题</label>
                    <input type="text" class="form-control" value="${data.products.sectionSubtitle}"
                           onchange="updateProductsSectionSubtitle(this.value)">
                </div>
            </div>

            <div id="productsContainer">
                ${data.products.items.map((product, index) => renderProductCardEditor(product, index)).join('')}
            </div>
        </div>

        <!-- CTA 区域 -->
        <div class="editor-section">
            <div class="section-header">
                <div class="section-title">
                    <i class="fas fa-bullhorn"></i>
                    行动号召 (CTA) 区域
                </div>
            </div>

            <div class="row">
                <div class="col-md-6">
                    <label class="form-label">CTA 标题</label>
                    <input type="text" class="form-control" value="${data.cta.title}"
                           onchange="updateCTATitle(this.value)">
                </div>
                <div class="col-md-6">
                    <label class="form-label">CTA 副标题</label>
                    <input type="text" class="form-control" value="${data.cta.subtitle}"
                           onchange="updateCTASubtitle(this.value)">
                </div>
                <div class="col-md-6 mt-3">
                    <label class="form-label">按钮文字</label>
                    <input type="text" class="form-control" value="${data.cta.buttonText}"
                           onchange="updateCTAButtonText(this.value)">
                </div>
                <div class="col-md-6 mt-3">
                    <label class="form-label">按钮链接</label>
                    <input type="text" class="form-control" value="${data.cta.buttonLink}"
                           onchange="updateCTAButtonLink(this.value)">
                </div>
            </div>
        </div>
    `;
}

// 渲染Hero轮播图编辑项
function renderHeroSlideEditor(slide, index) {
    return `
        <div class="edit-item-card" data-slide-index="${index}">
            <div class="edit-item-header">
                <span class="edit-item-title">轮播图 ${index + 1}</span>
                <button class="btn btn-sm btn-danger" onclick="deleteHeroSlide(${index})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>

            <div class="row">
                <div class="col-md-4">
                    <label class="form-label">图片 (1920x800px)</label>
                    <div class="image-upload-box" onclick="uploadHeroImage(${index})">
                        ${slide.image ? `
                            <img src="${slide.image}" class="image-preview" alt="Hero ${index + 1}">
                            <div class="image-info">点击更换图片</div>
                        ` : `
                            <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-2"></i>
                            <div>点击上传图片</div>
                            <div class="image-info">建议尺寸: 1920x800px</div>
                        `}
                    </div>
                    <input type="file" id="heroImageInput${index}" accept="image/*" style="display:none"
                           onchange="handleHeroImageUpload(${index}, this)">
                </div>

                <div class="col-md-8">
                    <div class="mb-3">
                        <label class="form-label">主标题</label>
                        <input type="text" class="form-control" value="${slide.title}"
                               onchange="updateHeroSlide(${index}, 'title', this.value)">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">副标题</label>
                        <textarea class="form-control" rows="2"
                                  onchange="updateHeroSlide(${index}, 'subtitle', this.value)">${slide.subtitle}</textarea>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <label class="form-label">按钮文字</label>
                            <input type="text" class="form-control" value="${slide.buttonText}"
                                   onchange="updateHeroSlide(${index}, 'buttonText', this.value)">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">按钮链接</label>
                            <input type="text" class="form-control" value="${slide.buttonLink}"
                                   onchange="updateHeroSlide(${index}, 'buttonLink', this.value)">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 渲染产品卡片编辑项
function renderProductCardEditor(product, index) {
    return `
        <div class="edit-item-card" data-product-index="${index}">
            <div class="edit-item-header">
                <span class="edit-item-title">${product.name}</span>
            </div>

            <div class="row">
                <div class="col-md-3">
                    <label class="form-label">产品图片 (400x300px)</label>
                    <div class="image-upload-box" onclick="uploadProductImage(${index})">
                        ${product.image ? `
                            <img src="${product.image}" class="image-preview" alt="${product.name}">
                            <div class="image-info">点击更换图片</div>
                        ` : `
                            <i class="fas fa-image fa-2x text-muted mb-2"></i>
                            <div>点击上传图片</div>
                        `}
                    </div>
                    <input type="file" id="productImageInput${index}" accept="image/*" style="display:none"
                           onchange="handleProductImageUpload(${index}, this)">
                </div>

                <div class="col-md-9">
                    <div class="mb-2">
                        <label class="form-label">产品名称</label>
                        <input type="text" class="form-control" value="${product.name}"
                               onchange="updateProduct(${index}, 'name', this.value)">
                    </div>
                    <div class="mb-2">
                        <label class="form-label">产品描述</label>
                        <textarea class="form-control" rows="2"
                                  onchange="updateProduct(${index}, 'description', this.value)">${product.description}</textarea>
                    </div>
                    <div class="mb-2">
                        <label class="form-label">产品链接</label>
                        <input type="text" class="form-control" value="${product.link}"
                               onchange="updateProduct(${index}, 'link', this.value)">
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 渲染产品中心编辑器
function renderProductsEditor() {
    const editorArea = document.getElementById('editorArea');
    const data = currentPageData;

    editorArea.innerHTML = `
        <div class="mb-4">
            <h3><i class="fas fa-cube"></i> 产品中心内容编辑</h3>
            <p class="text-muted">编辑产品分类、产品详情、规格参数等信息</p>
        </div>

        <!-- Hero 区域 -->
        <div class="editor-section">
            <div class="section-header">
                <div class="section-title">
                    <i class="fas fa-image"></i>
                    产品页Hero区域
                </div>
            </div>

            <div class="row">
                <div class="col-md-4">
                    <label class="form-label">标题</label>
                    <input type="text" class="form-control" value="${data.hero.title}"
                           onchange="updateProductsHero('title', this.value)">
                </div>
                <div class="col-md-8">
                    <label class="form-label">副标题</label>
                    <input type="text" class="form-control" value="${data.hero.subtitle}"
                           onchange="updateProductsHero('subtitle', this.value)">
                </div>
            </div>
        </div>

        <!-- 产品分类列表 -->
        <div class="editor-section">
            <div class="section-header">
                <div class="section-title">
                    <i class="fas fa-folder-open"></i>
                    产品分类管理
                </div>
                <button class="btn btn-sm btn-outline-primary" onclick="addProductCategory()">
                    <i class="fas fa-plus"></i> 添加分类
                </button>
            </div>

            <div id="categoriesContainer">
                ${data.categories.map((category, catIndex) => renderCategoryEditor(category, catIndex)).join('')}
            </div>
        </div>
    `;
}

// 渲染产品分类编辑器
function renderCategoryEditor(category, catIndex) {
    return `
        <div class="edit-item-card border-primary" data-category-index="${catIndex}" style="border-width: 2px;">
            <div class="edit-item-header">
                <span class="edit-item-title">
                    <i class="${category.icon}"></i> ${category.name}
                </span>
                <div>
                    <button class="btn btn-sm btn-success me-2" onclick="addProductToCategory(${catIndex})">
                        <i class="fas fa-plus"></i> 添加产品
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteCategory(${catIndex})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>

            <div class="row mb-3">
                <div class="col-md-4">
                    <label class="form-label">分类名称</label>
                    <input type="text" class="form-control" value="${category.name}"
                           onchange="updateCategory(${catIndex}, 'name', this.value)">
                </div>
                <div class="col-md-6">
                    <label class="form-label">分类描述</label>
                    <input type="text" class="form-control" value="${category.description}"
                           onchange="updateCategory(${catIndex}, 'description', this.value)">
                </div>
                <div class="col-md-2">
                    <label class="form-label">图标类名</label>
                    <input type="text" class="form-control" value="${category.icon}"
                           onchange="updateCategory(${catIndex}, 'icon', this.value)">
                </div>
            </div>

            <!-- 该分类下的产品列表 -->
            <div class="ps-3">
                <h6 class="text-muted mb-3">
                    <i class="fas fa-boxes"></i> 分类产品 (${category.products.length})
                </h6>
                <div id="category${catIndex}Products">
                    ${category.products.map((product, prodIndex) =>
                        renderProductDetailEditor(product, catIndex, prodIndex)
                    ).join('')}
                </div>
            </div>
        </div>
    `;
}

// 渲染产品详情编辑器
function renderProductDetailEditor(product, catIndex, prodIndex) {
    return `
        <div class="edit-item-card bg-light" data-cat-index="${catIndex}" data-prod-index="${prodIndex}">
            <div class="edit-item-header">
                <span class="edit-item-title">${product.name}</span>
                <button class="btn btn-sm btn-danger" onclick="deleteProduct(${catIndex}, ${prodIndex})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>

            <div class="row">
                <!-- 左侧：图片上传 -->
                <div class="col-md-3">
                    <label class="form-label">主图片</label>
                    <div class="image-upload-box" onclick="uploadProductMainImage(${catIndex}, ${prodIndex})">
                        ${product.mainImage ? `
                            <img src="${product.mainImage}" class="image-preview" alt="${product.name}">
                            <div class="image-info">点击更换图片</div>
                        ` : `
                            <i class="fas fa-image fa-2x text-muted mb-2"></i>
                            <div>点击上传主图</div>
                        `}
                    </div>
                    <input type="file" id="productMainImg_${catIndex}_${prodIndex}" accept="image/*"
                           style="display:none" onchange="handleProductMainImageUpload(${catIndex}, ${prodIndex}, this)">
                </div>

                <!-- 右侧：产品信息 -->
                <div class="col-md-9">
                    <div class="row">
                        <div class="col-md-6 mb-2">
                            <label class="form-label">产品名称</label>
                            <input type="text" class="form-control" value="${product.name}"
                                   onchange="updateProductField(${catIndex}, ${prodIndex}, 'name', this.value)">
                        </div>
                        <div class="col-md-6 mb-2">
                            <label class="form-label">产品ID</label>
                            <input type="text" class="form-control" value="${product.id}"
                                   onchange="updateProductField(${catIndex}, ${prodIndex}, 'id', this.value)">
                        </div>
                    </div>

                    <div class="mb-2">
                        <label class="form-label">产品描述</label>
                        <textarea class="form-control" rows="2"
                                  onchange="updateProductField(${catIndex}, ${prodIndex}, 'description', this.value)">${product.description}</textarea>
                    </div>

                    <!-- 规格参数 -->
                    <div class="mb-2">
                        <label class="form-label">
                            <i class="fas fa-cog"></i> 规格参数
                        </label>
                        <div class="border rounded p-2">
                            ${renderSpecificationsEditor(product.specifications, catIndex, prodIndex)}
                        </div>
                    </div>

                    <!-- 产品特性 -->
                    <div class="mb-2">
                        <label class="form-label">
                            <i class="fas fa-star"></i> 产品特性
                        </label>
                        <div class="border rounded p-2">
                            ${renderFeaturesEditor(product.features, catIndex, prodIndex)}
                        </div>
                    </div>

                    <!-- 应用场景 -->
                    <div class="mb-2">
                        <label class="form-label">
                            <i class="fas fa-map-marker-alt"></i> 应用场景
                        </label>
                        <input type="text" class="form-control"
                               value="${product.applications.join(', ')}"
                               onchange="updateProductApplications(${catIndex}, ${prodIndex}, this.value)"
                               placeholder="用逗号分隔多个场景">
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 渲染规格参数编辑器
function renderSpecificationsEditor(specs, catIndex, prodIndex) {
    if (!specs) return '<small class="text-muted">无规格参数</small>';

    return Object.entries(specs).map(([key, value]) => `
        <div class="row mb-1">
            <div class="col-5">
                <input type="text" class="form-control form-control-sm" value="${key}"
                       onchange="updateSpecKey(${catIndex}, ${prodIndex}, '${key}', this.value)">
            </div>
            <div class="col-7">
                <input type="text" class="form-control form-control-sm" value="${value}"
                       onchange="updateSpecValue(${catIndex}, ${prodIndex}, '${key}', this.value)">
            </div>
        </div>
    `).join('');
}

// 渲染产品特性编辑器
function renderFeaturesEditor(features, catIndex, prodIndex) {
    if (!features || features.length === 0) {
        return '<small class="text-muted">无产品特性</small>';
    }

    return features.map((feature, featureIndex) => `
        <div class="input-group input-group-sm mb-1">
            <span class="input-group-text">${featureIndex + 1}</span>
            <input type="text" class="form-control" value="${feature}"
                   onchange="updateFeature(${catIndex}, ${prodIndex}, ${featureIndex}, this.value)">
            <button class="btn btn-outline-danger" type="button"
                    onclick="deleteFeature(${catIndex}, ${prodIndex}, ${featureIndex})">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `).join('');
}

function renderAboutEditor() {
    document.getElementById('editorArea').innerHTML = `
        <div class="text-center py-5">
            <i class="fas fa-building fa-4x text-muted mb-3"></i>
            <h4>关于我们编辑器</h4>
            <p class="text-muted">即将推出...</p>
        </div>
    `;
}

function renderContactEditor() {
    document.getElementById('editorArea').innerHTML = `
        <div class="text-center py-5">
            <i class="fas fa-envelope fa-4x text-muted mb-3"></i>
            <h4>联系我们编辑器</h4>
            <p class="text-muted">即将推出...</p>
        </div>
    `;
}

function renderNewsEditor() {
    document.getElementById('editorArea').innerHTML = `
        <div class="text-center py-5">
            <i class="fas fa-newspaper fa-4x text-muted mb-3"></i>
            <h4>新闻中心编辑器</h4>
            <p class="text-muted">即将推出...</p>
        </div>
    `;
}

function renderDefaultEditor(pageId) {
    document.getElementById('editorArea').innerHTML = `
        <div class="text-center py-5">
            <i class="fas fa-file fa-4x text-muted mb-3"></i>
            <h4>${pageId} 编辑器</h4>
            <p class="text-muted">正在开发中...</p>
        </div>
    `;
}

// 更新Hero轮播图数据
function updateHeroSlide(index, field, value) {
    currentPageData.hero.slides[index][field] = value;
    hasUnsavedChanges = true;
    console.log(`更新Hero轮播图 ${index + 1} - ${field}:`, value);
}

// 更新产品数据
function updateProduct(index, field, value) {
    currentPageData.products.items[index][field] = value;
    hasUnsavedChanges = true;
    console.log(`更新产品 ${index + 1} - ${field}:`, value);
}

// 上传Hero图片
function uploadHeroImage(index) {
    document.getElementById(`heroImageInput${index}`).click();
}

async function handleHeroImageUpload(index, input) {
    if (!input.files || input.files.length === 0) return;

    const file = input.files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        // 临时显示本地预览
        currentPageData.hero.slides[index].image = e.target.result;
        hasUnsavedChanges = true;
        renderIndexEditor();
    };

    reader.readAsDataURL(file);

    // TODO: 上传到Supabase Storage
    console.log('上传Hero图片:', file.name);
}

// 上传产品图片
function uploadProductImage(index) {
    document.getElementById(`productImageInput${index}`).click();
}

async function handleProductImageUpload(index, input) {
    if (!input.files || input.files.length === 0) return;

    const file = input.files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        currentPageData.products.items[index].image = e.target.result;
        hasUnsavedChanges = true;
        renderIndexEditor();
    };

    reader.readAsDataURL(file);

    console.log('上传产品图片:', file.name);
}

// 保存所有更改
function saveAllChanges() {
    if (!hasUnsavedChanges) {
        alert('没有需要保存的更改');
        return;
    }

    savePageData(currentPage, currentPageData);
    hasUnsavedChanges = false;

    // 显示成功提示
    const btn = event.target;
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-check"></i> 已保存';
    btn.disabled = true;

    setTimeout(() => {
        btn.innerHTML = originalHTML;
        btn.disabled = false;
    }, 2000);

    // 刷新预览
    refreshPreview();

    alert('✅ 保存成功！\n\n更改已保存到浏览器本地存储。\n刷新前端页面即可看到效果。');
}

// 预览更改
function previewChanges() {
    refreshPreview();
    alert('预览已刷新！\n\n您可以在右侧预览面板查看效果。\n或点击"在新标签页打开"查看完整页面。');
}

// 刷新预览
function refreshPreview() {
    const iframe = document.getElementById('previewIframe');
    if (iframe) {
        // 根据当前页面更新预览URL
        let previewUrl = '../index.html';
        switch(currentPage) {
            case 'products': previewUrl = '../products.html'; break;
            case 'about': previewUrl = '../about.html'; break;
            case 'contact': previewUrl = '../contact.html'; break;
            case 'news': previewUrl = '../news.html'; break;
        }

        // 如果URL改变了，更新iframe src
        if (!iframe.src.includes(previewUrl)) {
            iframe.src = previewUrl;
        } else {
            // 否则只是刷新
            iframe.src = iframe.src;
        }
        console.log('🔄 刷新预览:', previewUrl);
    }
}

// 在新标签页打开预览
function openPreviewInNewTab() {
    let url = '../index.html';
    switch(currentPage) {
        case 'products': url = '../products.html'; break;
        case 'about': url = '../about.html'; break;
        case 'contact': url = '../contact.html'; break;
        case 'news': url = '../news.html'; break;
    }
    window.open(url, '_blank');
}

// 返回后台
function goBackToAdmin() {
    if (hasUnsavedChanges) {
        if (!confirm('您有未保存的更改，确定要离开吗？')) {
            return;
        }
    }
    window.location.href = '../admin.html';
}

// 更新产品区域标题/副标题
function updateProductsSectionTitle(value) {
    currentPageData.products.sectionTitle = value;
    hasUnsavedChanges = true;
}

function updateProductsSectionSubtitle(value) {
    currentPageData.products.sectionSubtitle = value;
    hasUnsavedChanges = true;
}

// 更新CTA数据
function updateCTATitle(value) {
    currentPageData.cta.title = value;
    hasUnsavedChanges = true;
}

function updateCTASubtitle(value) {
    currentPageData.cta.subtitle = value;
    hasUnsavedChanges = true;
}

function updateCTAButtonText(value) {
    currentPageData.cta.buttonText = value;
    hasUnsavedChanges = true;
}

function updateCTAButtonLink(value) {
    currentPageData.cta.buttonLink = value;
    hasUnsavedChanges = true;
}

// ========== 产品页面编辑器辅助函数 ==========

// 更新产品页Hero
function updateProductsHero(field, value) {
    currentPageData.hero[field] = value;
    hasUnsavedChanges = true;
    console.log(`更新产品页Hero ${field}:`, value);
}

// 更新分类信息
function updateCategory(catIndex, field, value) {
    currentPageData.categories[catIndex][field] = value;
    hasUnsavedChanges = true;
    console.log(`更新分类 ${catIndex} - ${field}:`, value);
}

// 更新产品字段
function updateProductField(catIndex, prodIndex, field, value) {
    currentPageData.categories[catIndex].products[prodIndex][field] = value;
    hasUnsavedChanges = true;
    console.log(`更新产品 [${catIndex}][${prodIndex}] - ${field}:`, value);
}

// 更新规格参数的键
function updateSpecKey(catIndex, prodIndex, oldKey, newKey) {
    const specs = currentPageData.categories[catIndex].products[prodIndex].specifications;
    if (oldKey !== newKey) {
        specs[newKey] = specs[oldKey];
        delete specs[oldKey];
        hasUnsavedChanges = true;
        renderProductsEditor();
    }
}

// 更新规格参数的值
function updateSpecValue(catIndex, prodIndex, key, value) {
    currentPageData.categories[catIndex].products[prodIndex].specifications[key] = value;
    hasUnsavedChanges = true;
    console.log(`更新规格参数 [${catIndex}][${prodIndex}] ${key}:`, value);
}

// 更新产品特性
function updateFeature(catIndex, prodIndex, featureIndex, value) {
    currentPageData.categories[catIndex].products[prodIndex].features[featureIndex] = value;
    hasUnsavedChanges = true;
    console.log(`更新特性 [${catIndex}][${prodIndex}][${featureIndex}]:`, value);
}

// 删除产品特性
function deleteFeature(catIndex, prodIndex, featureIndex) {
    if (confirm('确定要删除这个特性吗？')) {
        currentPageData.categories[catIndex].products[prodIndex].features.splice(featureIndex, 1);
        hasUnsavedChanges = true;
        renderProductsEditor();
    }
}

// 更新应用场景
function updateProductApplications(catIndex, prodIndex, value) {
    const applications = value.split(',').map(app => app.trim()).filter(app => app);
    currentPageData.categories[catIndex].products[prodIndex].applications = applications;
    hasUnsavedChanges = true;
    console.log(`更新应用场景 [${catIndex}][${prodIndex}]:`, applications);
}

// 上传产品主图
function uploadProductMainImage(catIndex, prodIndex) {
    document.getElementById(`productMainImg_${catIndex}_${prodIndex}`).click();
}

async function handleProductMainImageUpload(catIndex, prodIndex, input) {
    if (!input.files || input.files.length === 0) return;

    const file = input.files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        currentPageData.categories[catIndex].products[prodIndex].mainImage = e.target.result;
        hasUnsavedChanges = true;
        renderProductsEditor();
    };

    reader.readAsDataURL(file);
    console.log('上传产品主图:', file.name);
}

// 添加产品分类
function addProductCategory() {
    const newCategory = {
        id: 'new-category-' + Date.now(),
        name: '新分类',
        description: '分类描述',
        icon: 'fas fa-box',
        order: currentPageData.categories.length + 1,
        products: []
    };

    currentPageData.categories.push(newCategory);
    hasUnsavedChanges = true;
    renderProductsEditor();
    console.log('添加新分类:', newCategory);
}

// 删除产品分类
function deleteCategory(catIndex) {
    const category = currentPageData.categories[catIndex];
    if (confirm(`确定要删除"${category.name}"分类吗？\n该分类下的所有产品也会被删除。`)) {
        currentPageData.categories.splice(catIndex, 1);
        hasUnsavedChanges = true;
        renderProductsEditor();
        console.log('删除分类:', category.name);
    }
}

// 添加产品到分类
function addProductToCategory(catIndex) {
    const newProduct = {
        id: 'new-product-' + Date.now(),
        name: '新产品',
        mainImage: '',
        gallery: [],
        description: '产品描述',
        specifications: {
            pixelPitch: '',
            brightness: '',
            refreshRate: ''
        },
        features: [
            '特性1',
            '特性2',
            '特性3'
        ],
        applications: ['应用场景1', '应用场景2'],
        order: currentPageData.categories[catIndex].products.length + 1
    };

    currentPageData.categories[catIndex].products.push(newProduct);
    hasUnsavedChanges = true;
    renderProductsEditor();
    console.log('添加新产品到分类', catIndex);
}

// 删除产品
function deleteProduct(catIndex, prodIndex) {
    const product = currentPageData.categories[catIndex].products[prodIndex];
    if (confirm(`确定要删除产品"${product.name}"吗？`)) {
        currentPageData.categories[catIndex].products.splice(prodIndex, 1);
        hasUnsavedChanges = true;
        renderProductsEditor();
        console.log('删除产品:', product.name);
    }
}

console.log('✅ 页面编辑器脚本加载完成');
