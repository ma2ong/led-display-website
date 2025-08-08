// 终极Hero区域修复JavaScript - 最高优先级
(function() {
    'use strict';
    
    console.log('🚀 启动终极Hero修复...');
    
    // 强制修复Hero区域的函数
    function forceFixHeroSections() {
        // 查找所有可能的Hero区域
        const heroSelectors = [
            '.hero-section',
            '.product-hero-section', 
            'section[class*="hero"]',
            '.cta-section',
            '#hero',
            '.hero'
        ];
        
        let fixedCount = 0;
        
        heroSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                // 强制设置样式
                el.style.setProperty('min-height', '600px', 'important');
                el.style.setProperty('max-height', '600px', 'important');
                el.style.setProperty('height', '600px', 'important');
                el.style.setProperty('padding', '120px 0 80px', 'important');
                el.style.setProperty('display', 'flex', 'important');
                el.style.setProperty('align-items', 'center', 'important');
                el.style.setProperty('justify-content', 'center', 'important');
                el.style.setProperty('position', 'relative', 'important');
                el.style.setProperty('overflow', 'hidden', 'important');
                el.style.setProperty('box-sizing', 'border-box', 'important');
                
                // 修复容器
                const container = el.querySelector('.container');
                if (container) {
                    container.style.setProperty('position', 'relative', 'important');
                    container.style.setProperty('z-index', '10', 'important');
                    container.style.setProperty('height', 'auto', 'important');
                    container.style.setProperty('max-height', 'none', 'important');
                    container.style.setProperty('display', 'flex', 'important');
                    container.style.setProperty('align-items', 'center', 'important');
                    container.style.setProperty('justify-content', 'center', 'important');
                    container.style.setProperty('width', '100%', 'important');
                    container.style.setProperty('padding', '0 15px', 'important');
                }
                
                // 修复行
                const rows = el.querySelectorAll('.row');
                rows.forEach(row => {
                    row.style.setProperty('align-items', 'center', 'important');
                    row.style.setProperty('height', 'auto', 'important');
                    row.style.setProperty('width', '100%', 'important');
                    row.style.setProperty('margin', '0', 'important');
                });
                
                // 修复列
                const cols = el.querySelectorAll('[class*="col-"]');
                cols.forEach(col => {
                    col.style.setProperty('display', 'flex', 'important');
                    col.style.setProperty('flex-direction', 'column', 'important');
                    col.style.setProperty('justify-content', 'center', 'important');
                    col.style.setProperty('height', 'auto', 'important');
                    col.style.setProperty('padding', '20px', 'important');
                });
                
                fixedCount++;
            });
        });
        
        console.log(`✅ 已修复 ${fixedCount} 个Hero区域`);
        return fixedCount;
    }
    
    // 响应式修复
    function applyResponsiveFix() {
        const heroElements = document.querySelectorAll('.hero-section, .product-hero-section, section[class*="hero"], .cta-section, #hero, .hero');
        
        heroElements.forEach(el => {
            if (window.innerWidth <= 768) {
                // 移动端
                el.style.setProperty('min-height', '500px', 'important');
                el.style.setProperty('max-height', '500px', 'important');
                el.style.setProperty('height', '500px', 'important');
                el.style.setProperty('padding', '100px 0 60px', 'important');
            } else if (window.innerWidth <= 576) {
                // 超小屏幕
                el.style.setProperty('min-height', '450px', 'important');
                el.style.setProperty('max-height', '450px', 'important');
                el.style.setProperty('height', '450px', 'important');
                el.style.setProperty('padding', '80px 0 50px', 'important');
            } else {
                // 桌面端
                el.style.setProperty('min-height', '600px', 'important');
                el.style.setProperty('max-height', '600px', 'important');
                el.style.setProperty('height', '600px', 'important');
                el.style.setProperty('padding', '120px 0 80px', 'important');
            }
        });
    }
    
    // 监听窗口大小变化
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            applyResponsiveFix();
            forceFixHeroSections();
        }, 100);
    });
    
    // 监听DOM变化
    const observer = new MutationObserver(function(mutations) {
        let shouldFix = false;
        mutations.forEach(mutation => {
            if (mutation.type === 'childList' || mutation.type === 'attributes') {
                shouldFix = true;
            }
        });
        
        if (shouldFix) {
            setTimeout(forceFixHeroSections, 50);
        }
    });
    
    // 多次执行修复，确保生效
    function executeMultipleFixes() {
        forceFixHeroSections();
        applyResponsiveFix();
        
        // 延迟执行
        setTimeout(() => {
            forceFixHeroSections();
            applyResponsiveFix();
        }, 100);
        
        setTimeout(() => {
            forceFixHeroSections();
            applyResponsiveFix();
        }, 500);
        
        setTimeout(() => {
            forceFixHeroSections();
            applyResponsiveFix();
        }, 1000);
    }
    
    // DOM加载完成后执行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', executeMultipleFixes);
    } else {
        executeMultipleFixes();
    }
    
    // 页面完全加载后再次执行
    window.addEventListener('load', executeMultipleFixes);
    
    // 开始监听DOM变化
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['style', 'class']
    });
    
    console.log('🎉 终极Hero修复已激活！');
})();