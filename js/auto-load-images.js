/**
 * 自动加载上传的图片到前端页面
 * 从 localStorage 读取图片位置映射，并替换对应位置的图片
 */

(function() {
    'use strict';

    console.log('🖼️ 图片自动加载器已启动');

    // 从 localStorage 读取图片映射
    function loadImageMappings() {
        try {
            const mappings = localStorage.getItem('image_location_mappings');
            if (!mappings) {
                console.log('📭 暂无图片映射数据');
                return {};
            }
            const parsed = JSON.parse(mappings);
            console.log(`✅ 加载了 ${Object.keys(parsed).length} 个图片映射`, parsed);
            return parsed;
        } catch (error) {
            console.error('❌ 读取图片映射失败:', error);
            return {};
        }
    }

    // 应用图片到页面元素
    function applyImageToElement(mapping) {
        try {
            const elements = document.querySelectorAll(mapping.element);

            if (!elements || elements.length === 0) {
                console.warn(`⚠️ 未找到元素: ${mapping.element} (${mapping.locationName})`);
                return false;
            }

            let appliedCount = 0;
            elements.forEach((element) => {
                if (element.tagName === 'IMG') {
                    // 直接是 img 元素
                    element.src = mapping.publicUrl;
                    element.alt = mapping.locationName;
                    element.dataset.uploadedImage = mapping.locationId;
                    appliedCount++;
                    console.log(`✅ 应用图片: ${mapping.locationName} → ${element.tagName}`);
                } else {
                    // 可能是背景图
                    element.style.backgroundImage = `url('${mapping.publicUrl}')`;
                    element.dataset.uploadedImage = mapping.locationId;
                    appliedCount++;
                    console.log(`✅ 应用背景图: ${mapping.locationName} → ${element.tagName}`);
                }
            });

            return appliedCount > 0;
        } catch (error) {
            console.error(`❌ 应用图片失败 (${mapping.locationName}):`, error);
            return false;
        }
    }

    // 主函数：加载所有图片
    function loadAllImages() {
        const mappings = loadImageMappings();

        if (Object.keys(mappings).length === 0) {
            console.log('📭 没有需要加载的图片');
            return;
        }

        let successCount = 0;
        let failCount = 0;

        for (const [locationId, mapping] of Object.entries(mappings)) {
            if (applyImageToElement(mapping)) {
                successCount++;
            } else {
                failCount++;
            }
        }

        console.log(`🎉 图片加载完成: 成功 ${successCount} 个, 失败 ${failCount} 个`);

        // 在控制台显示加载的图片信息
        if (successCount > 0) {
            console.table(Object.values(mappings).map(m => ({
                '位置': m.locationName,
                '页面': m.page,
                '文件': m.fileName,
                '大小': `${(m.size / 1024).toFixed(2)} KB`,
                '上传时间': new Date(m.uploadedAt).toLocaleString('zh-CN')
            })));
        }
    }

    // 页面加载完成后执行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadAllImages);
    } else {
        // DOM已经加载完成
        loadAllImages();
    }

    // 导出到全局，方便手动调用
    window.reloadUploadedImages = loadAllImages;

    console.log('💡 提示: 可以在控制台运行 reloadUploadedImages() 手动重新加载图片');

})();
