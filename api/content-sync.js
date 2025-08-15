/**
 * 内容同步API
 * 实现前后端内容的实时同步和WebSocket推送
 */

class ContentSyncAPI {
    constructor() {
        this.supabaseUrl = 'https://jirudzbqcxviytcmxegf.supabase.co';
        this.supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y218ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4';
        this.supabase = null;
        this.channels = new Map();
        this.syncCallbacks = new Map();
        this.isInitialized = false;
    }

    /**
     * 初始化API
     */
    async init() {
        try {
            console.log('🔄 初始化内容同步API...');
            
            // 初始化Supabase客户端
            if (typeof window !== 'undefined' && window.supabase) {
                this.supabase = window.supabase.createClient(this.supabaseUrl, this.supabaseKey);
            } else if (typeof global !== 'undefined' && global.supabase) {
                this.supabase = global.supabase.createClient(this.supabaseUrl, this.supabaseKey);
            } else {
                console.warn('⚠️ Supabase客户端未找到');
                return false;
            }

            // 设置实时监听
            this.setupRealtimeSync();
            
            this.isInitialized = true;
            console.log('✅ 内容同步API初始化完成');
            return true;
        } catch (error) {
            console.error('❌ 内容同步API初始化失败:', error);
            return false;
        }
    }

    /**
     * 设置实时同步
     */
    setupRealtimeSync() {
        // 监听页面内容变化
        const contentChannel = this.supabase
            .channel('content-sync')
            .on('postgres_changes', 
                { event: '*', schema: 'public', table: 'page_contents' }, 
                (payload) => {
                    this.handleContentChange(payload);
                }
            )
            .on('postgres_changes', 
                { event: '*', schema: 'public', table: 'site_settings' }, 
                (payload) => {
                    this.handleSettingChange(payload);
                }
            )
            .on('postgres_changes', 
                { event: '*', schema: 'public', table: 'page_sections' }, 
                (payload) => {
                    this.handleSectionChange(payload);
                }
            )
            .subscribe();

        this.channels.set('content-sync', contentChannel);
        console.log('📡 实时同步通道已建立');
    }

    /**
     * 处理内容变化
     */
    handleContentChange(payload) {
        console.log('📝 内容变化:', payload);
        
        const { eventType, new: newRecord, old: oldRecord } = payload;
        
        // 触发同步回调
        this.triggerSyncCallbacks('content', {
            type: eventType,
            data: newRecord || oldRecord,
            timestamp: new Date().toISOString()
        });

        // 广播变化事件
        this.broadcastChange('content', payload);
    }

    /**
     * 处理设置变化
     */
    handleSettingChange(payload) {
        console.log('⚙️ 设置变化:', payload);
        
        const { eventType, new: newRecord, old: oldRecord } = payload;
        
        // 触发同步回调
        this.triggerSyncCallbacks('setting', {
            type: eventType,
            data: newRecord || oldRecord,
            timestamp: new Date().toISOString()
        });

        // 广播变化事件
        this.broadcastChange('setting', payload);
    }

    /**
     * 处理区块变化
     */
    handleSectionChange(payload) {
        console.log('📦 区块变化:', payload);
        
        const { eventType, new: newRecord, old: oldRecord } = payload;
        
        // 触发同步回调
        this.triggerSyncCallbacks('section', {
            type: eventType,
            data: newRecord || oldRecord,
            timestamp: new Date().toISOString()
        });

        // 广播变化事件
        this.broadcastChange('section', payload);
    }

    /**
     * 保存页面内容
     */
    async savePageContent(pageName, contentKey, contentValue, contentType = 'text') {
        if (!this.supabase) {
            throw new Error('Supabase客户端未初始化');
        }

        try {
            // 先检查是否存在
            const { data: existing } = await this.supabase
                .from('page_contents')
                .select('id')
                .eq('page_name', pageName)
                .eq('content_key', contentKey)
                .single();

            let result;
            
            if (existing) {
                // 更新现有记录
                result = await this.supabase
                    .from('page_contents')
                    .update({
                        content_value: contentValue,
                        content_type: contentType,
                        updated_at: new Date().toISOString()
                    })
                    .eq('id', existing.id)
                    .select();
            } else {
                // 插入新记录
                result = await this.supabase
                    .from('page_contents')
                    .insert({
                        page_name: pageName,
                        content_key: contentKey,
                        content_value: contentValue,
                        content_type: contentType,
                        is_active: true
                    })
                    .select();
            }

            if (result.error) throw result.error;

            console.log('✅ 内容保存成功');
            return { success: true, data: result.data };
        } catch (error) {
            console.error('❌ 保存内容失败:', error);
            throw error;
        }
    }

    /**
     * 批量保存页面内容
     */
    async savePageContentBatch(pageName, contents) {
        if (!this.supabase) {
            throw new Error('Supabase客户端未初始化');
        }

        try {
            const updates = [];
            const inserts = [];

            for (const [key, value] of Object.entries(contents)) {
                // 检查是否存在
                const { data: existing } = await this.supabase
                    .from('page_contents')
                    .select('id')
                    .eq('page_name', pageName)
                    .eq('content_key', key)
                    .single();

                if (existing) {
                    updates.push({
                        id: existing.id,
                        content_value: value.value || value,
                        content_type: value.type || 'text',
                        updated_at: new Date().toISOString()
                    });
                } else {
                    inserts.push({
                        page_name: pageName,
                        content_key: key,
                        content_value: value.value || value,
                        content_type: value.type || 'text',
                        is_active: true
                    });
                }
            }

            // 执行批量更新
            if (updates.length > 0) {
                for (const update of updates) {
                    await this.supabase
                        .from('page_contents')
                        .update(update)
                        .eq('id', update.id);
                }
            }

            // 执行批量插入
            if (inserts.length > 0) {
                await this.supabase
                    .from('page_contents')
                    .insert(inserts);
            }

            console.log(`✅ 批量保存成功: ${updates.length}个更新, ${inserts.length}个新增`);
            return { success: true, updates: updates.length, inserts: inserts.length };
        } catch (error) {
            console.error('❌ 批量保存失败:', error);
            throw error;
        }
    }

    /**
     * 获取页面内容
     */
    async getPageContent(pageName) {
        if (!this.supabase) {
            throw new Error('Supabase客户端未初始化');
        }

        try {
            const { data, error } = await this.supabase
                .from('page_contents')
                .select('*')
                .eq('page_name', pageName)
                .eq('is_active', true);

            if (error) throw error;

            // 转换为键值对象
            const contents = {};
            data.forEach(item => {
                contents[item.content_key] = {
                    value: item.content_value,
                    type: item.content_type,
                    id: item.id
                };
            });

            return contents;
        } catch (error) {
            console.error('获取页面内容失败:', error);
            throw error;
        }
    }

    /**
     * 保存网站设置
     */
    async saveSiteSetting(key, value, type = 'text') {
        if (!this.supabase) {
            throw new Error('Supabase客户端未初始化');
        }

        try {
            const { data: existing } = await this.supabase
                .from('site_settings')
                .select('id')
                .eq('setting_key', key)
                .single();

            let result;
            
            if (existing) {
                result = await this.supabase
                    .from('site_settings')
                    .update({
                        setting_value: value,
                        setting_type: type,
                        updated_at: new Date().toISOString()
                    })
                    .eq('id', existing.id)
                    .select();
            } else {
                result = await this.supabase
                    .from('site_settings')
                    .insert({
                        setting_key: key,
                        setting_value: value,
                        setting_type: type,
                        is_public: true
                    })
                    .select();
            }

            if (result.error) throw result.error;

            console.log('✅ 设置保存成功');
            return { success: true, data: result.data };
        } catch (error) {
            console.error('❌ 保存设置失败:', error);
            throw error;
        }
    }

    /**
     * 注册同步回调
     */
    onSync(type, callback) {
        if (!this.syncCallbacks.has(type)) {
            this.syncCallbacks.set(type, []);
        }
        this.syncCallbacks.get(type).push(callback);
        
        console.log(`📌 注册了${type}类型的同步回调`);
    }

    /**
     * 触发同步回调
     */
    triggerSyncCallbacks(type, data) {
        const callbacks = this.syncCallbacks.get(type) || [];
        callbacks.forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error('执行同步回调失败:', error);
            }
        });
    }

    /**
     * 广播变化事件
     */
    broadcastChange(type, payload) {
        // 创建自定义事件
        if (typeof window !== 'undefined') {
            const event = new CustomEvent('content-sync', {
                detail: {
                    type: type,
                    payload: payload,
                    timestamp: new Date().toISOString()
                }
            });
            window.dispatchEvent(event);
        }
    }

    /**
     * 强制同步所有内容
     */
    async forceSync(pageName) {
        try {
            console.log('🔄 强制同步页面内容:', pageName);
            
            // 获取最新内容
            const contents = await this.getPageContent(pageName);
            
            // 触发同步事件
            this.broadcastChange('force-sync', {
                page: pageName,
                contents: contents
            });
            
            console.log('✅ 强制同步完成');
            return { success: true, contents };
        } catch (error) {
            console.error('❌ 强制同步失败:', error);
            throw error;
        }
    }

    /**
     * 清理资源
     */
    cleanup() {
        // 取消所有订阅
        this.channels.forEach((channel, name) => {
            channel.unsubscribe();
            console.log(`📴 取消订阅通道: ${name}`);
        });
        
        this.channels.clear();
        this.syncCallbacks.clear();
        this.isInitialized = false;
    }
}

// 创建单例实例
const contentSyncAPI = new ContentSyncAPI();

// 自动初始化
if (typeof window !== 'undefined') {
    window.addEventListener('DOMContentLoaded', () => {
        contentSyncAPI.init();
    });
    
    // 导出到全局
    window.contentSyncAPI = contentSyncAPI;
} else if (typeof module !== 'undefined' && module.exports) {
    // Node.js环境
    module.exports = contentSyncAPI;
}

console.log('📡 内容同步API模块已加载');
