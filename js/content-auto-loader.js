/**
 * 前端内容自动加载器
 * 从 localStorage 读取后台编辑的内容并自动更新到页面
 */

(function() {
    'use strict';

    console.log('🚀 内容自动加载器已启动');

    // 获取当前页面类型
    function getCurrentPageType() {
        const path = window.location.pathname;
        if (path.includes('products.html')) return 'products';
        if (path.includes('about.html')) return 'about';
        if (path.includes('contact.html')) return 'contact';
        if (path.includes('news.html')) return 'news';
        return 'index'; // 默认首页
    }

    // 加载页面数据
    function loadPageData(pageId) {
        const key = `page_data_${pageId}`;
        const stored = localStorage.getItem(key);

        if (stored) {
            try {
                const data = JSON.parse(stored);
                console.log(`✅ 加载页面数据: ${pageId}`, data);
                return data;
            } catch (error) {
                console.error(`❌ 解析页面数据失败: ${pageId}`, error);
            }
        }

        console.log(`📭 未找到页面数据: ${pageId}，使用页面原有内容`);
        return null;
    }

    // 应用首页内容
    function applyIndexContent(data) {
        if (!data) return;

        console.log('📄 应用首页内容');

        // 1. 更新Hero轮播图
        if (data.hero && data.hero.slides) {
            data.hero.slides.forEach((slide, index) => {
                const slideElement = document.querySelector(`.carousel-item:nth-child(${index + 1})`);
                if (slideElement) {
                    // 更新图片
                    const img = slideElement.querySelector('img');
                    if (img && slide.image) {
                        img.src = slide.image;
                    }

                    // 更新标题
                    const title = slideElement.querySelector('h1, .carousel-caption h1, .hero-title');
                    if (title && slide.title) {
                        title.textContent = slide.title;
                    }

                    // 更新副标题
                    const subtitle = slideElement.querySelector('p, .carousel-caption p, .hero-subtitle');
                    if (subtitle && slide.subtitle) {
                        subtitle.textContent = slide.subtitle;
                    }

                    // 更新按钮
                    const button = slideElement.querySelector('a.btn, .hero-button');
                    if (button) {
                        if (slide.buttonText) button.textContent = slide.buttonText;
                        if (slide.buttonLink) button.href = slide.buttonLink;
                    }

                    console.log(`✅ 更新Hero轮播图 ${index + 1}`);
                }
            });
        }

        // 2. 更新产品展示区域
        if (data.products) {
            // 更新区域标题
            const sectionTitle = document.querySelector('.products-section h2, #products h2');
            if (sectionTitle && data.products.sectionTitle) {
                sectionTitle.textContent = data.products.sectionTitle;
            }

            // 更新区域副标题
            const sectionSubtitle = document.querySelector('.products-section p.lead, #products .lead');
            if (sectionSubtitle && data.products.sectionSubtitle) {
                sectionSubtitle.textContent = data.products.sectionSubtitle;
            }

            // 更新产品卡片
            if (data.products.items) {
                data.products.items.forEach((product, index) => {
                    const productCard = document.querySelector(`.product-card:nth-child(${index + 1}), .col:nth-child(${index + 1}) .product-card`);
                    if (productCard) {
                        // 更新产品图片
                        const img = productCard.querySelector('img');
                        if (img && product.image) {
                            img.src = product.image;
                            img.alt = product.name;
                        }

                        // 更新产品名称
                        const name = productCard.querySelector('h3, h4, h5, .card-title');
                        if (name && product.name) {
                            name.textContent = product.name;
                        }

                        // 更新产品描述
                        const description = productCard.querySelector('p, .card-text');
                        if (description && product.description) {
                            description.textContent = product.description;
                        }

                        // 更新链接
                        const link = productCard.querySelector('a.btn');
                        if (link && product.link) {
                            link.href = product.link;
                        }

                        console.log(`✅ 更新产品卡片: ${product.name}`);
                    }
                });
            }
        }

        // 3. 更新CTA区域
        if (data.cta) {
            const ctaSection = document.querySelector('.cta-section, #cta');
            if (ctaSection) {
                // 更新背景图
                if (data.cta.backgroundImage) {
                    ctaSection.style.backgroundImage = `url('${data.cta.backgroundImage}')`;
                }

                // 更新标题
                const title = ctaSection.querySelector('h2');
                if (title && data.cta.title) {
                    title.textContent = data.cta.title;
                }

                // 更新副标题
                const subtitle = ctaSection.querySelector('p');
                if (subtitle && data.cta.subtitle) {
                    subtitle.textContent = data.cta.subtitle;
                }

                // 更新按钮
                const button = ctaSection.querySelector('a.btn');
                if (button) {
                    if (data.cta.buttonText) button.textContent = data.cta.buttonText;
                    if (data.cta.buttonLink) button.href = data.cta.buttonLink;
                }

                console.log('✅ 更新CTA区域');
            }
        }
    }

    // 应用产品页内容
    function applyProductsContent(data) {
        if (!data) return;

        console.log('📄 应用产品页内容');

        // 1. 更新Hero区域
        if (data.hero) {
            // 更新标题
            const heroTitle = document.querySelector('.product-hero-section h1, .hero-title');
            if (heroTitle && data.hero.title) {
                heroTitle.textContent = data.hero.title;
            }

            // 更新副标题
            const heroSubtitle = document.querySelector('.product-hero-section p, .hero-subtitle');
            if (heroSubtitle && data.hero.subtitle) {
                heroSubtitle.textContent = data.hero.subtitle;
            }

            // 更新背景图（如果有）
            const heroSection = document.querySelector('.product-hero-section');
            if (heroSection && data.hero.backgroundImage) {
                heroSection.style.backgroundImage = `url('${data.hero.backgroundImage}')`;
                heroSection.style.backgroundSize = 'cover';
                heroSection.style.backgroundPosition = 'center';
            }

            console.log('✅ 更新产品页Hero区域');
        }

        // 2. 更新产品列表
        if (data.categories && data.categories.length > 0) {
            const productsContainer = document.getElementById('products-container');
            if (productsContainer) {
                // 清空现有产品（保留加载元素）
                const loadingElement = document.getElementById('products-loading');
                productsContainer.innerHTML = '';
                if (loadingElement) {
                    productsContainer.appendChild(loadingElement);
                    loadingElement.style.display = 'none';
                }

                // 渲染所有分类的产品
                data.categories.forEach(category => {
                    category.products.forEach(product => {
                        const productCard = createProductCardFromData(product, category);
                        productsContainer.appendChild(productCard);
                    });
                });

                console.log(`✅ 更新产品列表: ${data.categories.length} 个分类`);
            }
        }

        // 3. 更新分类筛选器
        if (data.categories && data.categories.length > 0) {
            const filtersContainer = document.getElementById('category-filters');
            if (filtersContainer) {
                // 保留"All"按钮
                const allButton = filtersContainer.querySelector('[data-category="all"]');
                if (allButton) {
                    filtersContainer.innerHTML = '';
                    filtersContainer.appendChild(allButton);

                    // 添加分类筛选按钮
                    data.categories.forEach(category => {
                        const button = document.createElement('button');
                        button.className = 'btn btn-outline-primary category-filter';
                        button.setAttribute('data-category', category.id);
                        button.innerHTML = `<i class="${category.icon}"></i> ${category.name}`;
                        filtersContainer.appendChild(button);
                    });

                    console.log('✅ 更新分类筛选器');
                }
            }
        }
    }

    // 从数据创建产品卡片
    function createProductCardFromData(product, category) {
        const col = document.createElement('div');
        col.className = 'col-lg-4 col-md-6';
        col.setAttribute('data-aos', 'fade-up');
        col.setAttribute('data-category', category.id);

        // 获取图标和颜色
        const iconClass = category.icon || 'fas fa-cube';
        const colorClass = getCategoryColorClass(category.id);

        col.innerHTML = `
            <div class="card product-card h-100">
                <div class="card-img-container">
                    <div class="product-image bg-light d-flex align-items-center justify-content-center">
                        ${product.mainImage ?
                            `<img src="${product.mainImage}" alt="${product.name}" class="img-fluid" style="max-height: 200px; width: 100%; object-fit: cover;">` :
                            `<i class="${iconClass} display-4 ${colorClass}"></i>`
                        }
                    </div>
                    <div class="card-overlay">
                        <a class="btn btn-primary" href="contact.html?product=${product.id}">
                            <i class="fas fa-phone me-2"></i>Get Quote
                        </a>
                    </div>
                </div>
                <div class="card-body">
                    <h5 class="card-title">${product.name}</h5>
                    <p class="card-text">${product.description || ''}</p>
                    ${renderProductFeaturesBadges(product)}
                    ${renderProductSpecsList(product)}
                </div>
                <div class="card-footer">
                    <small class="text-muted">Category: ${category.name}</small>
                </div>
            </div>
        `;

        return col;
    }

    // 渲染产品特性徽章
    function renderProductFeaturesBadges(product) {
        if (!product.features || product.features.length === 0) return '';

        const badges = product.features.slice(0, 3).map(feature =>
            `<span class="badge bg-primary me-1">${feature}</span>`
        ).join('');

        return `<div class="product-features mb-3">${badges}</div>`;
    }

    // 渲染产品规格列表
    function renderProductSpecsList(product) {
        if (!product.features || product.features.length === 0) return '';

        const specs = product.features.slice(0, 4).map(spec =>
            `<li><i class="fas fa-check text-success me-2"></i>${spec}</li>`
        ).join('');

        return `<ul class="list-unstyled small">${specs}</ul>`;
    }

    // 获取分类颜色类
    function getCategoryColorClass(categoryId) {
        const colors = {
            'indoor': 'text-primary',
            'outdoor': 'text-warning',
            'rental': 'text-success',
            'transparent': 'text-info',
            'creative': 'text-danger',
            'fine-pitch': 'text-dark'
        };
        return colors[categoryId] || 'text-primary';
    }

    // 应用关于我们内容
    function applyAboutContent(data) {
        if (!data) return;

        console.log('📄 应用关于我们内容');
        // TODO: 实现关于我们页面内容更新
    }

    // 应用联系我们内容
    function applyContactContent(data) {
        if (!data) return;

        console.log('📄 应用联系我们内容');
        // TODO: 实现联系我们页面内容更新
    }

    // 应用新闻页内容
    function applyNewsContent(data) {
        if (!data) return;

        console.log('📄 应用新闻页内容');
        // TODO: 实现新闻页内容更新
    }

    // 主函数：加载并应用内容
    function loadAndApplyContent() {
        const pageType = getCurrentPageType();
        const pageData = loadPageData(pageType);

        if (!pageData) {
            console.log('💡 提示: 在后台编辑内容后，这里会自动显示更新的内容');
            return;
        }

        console.log(`📄 当前页面: ${pageType}`);
        console.log(`🕐 最后更新: ${new Date(pageData.lastModified).toLocaleString('zh-CN')}`);

        // 根据页面类型应用内容
        switch(pageType) {
            case 'index':
                applyIndexContent(pageData);
                break;
            case 'products':
                applyProductsContent(pageData);
                break;
            case 'about':
                applyAboutContent(pageData);
                break;
            case 'contact':
                applyContactContent(pageData);
                break;
            case 'news':
                applyNewsContent(pageData);
                break;
        }

        console.log('✅ 内容加载完成');
    }

    // 页面加载完成后执行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadAndApplyContent);
    } else {
        loadAndApplyContent();
    }

    // 导出到全局，方便手动调用
    window.reloadPageContent = loadAndApplyContent;

    console.log('💡 提示: 可以在控制台运行 reloadPageContent() 手动重新加载内容');

})();
