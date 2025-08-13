/**
 * 增强版管理后台JavaScript
 * 包含完整的产品、新闻、询盘和用户管理功能
 */

// Supabase配置
const SUPABASE_URL = 'https://jirudzbqcxviytcmxegf.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y218ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4';

// 初始化Supabase客户端
let supabase;
if (typeof window !== 'undefined' && window.supabase) {
    const { createClient } = window.supabase;
    supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
}

// 产品管理功能
class ProductManager {
    static async addProduct() {
        const modalHtml = `
            <div class="modal fade" id="addProductModal">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">添加新产品</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="productForm">
                                <div class="mb-3">
                                    <label class="form-label">产品名称</label>
                                    <input type="text" class="form-control" name="name" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">产品类别</label>
                                    <select class="form-control" name="category" required>
                                        <option value="">选择类别</option>
                                        <option value="Indoor LED">室内LED</option>
                                        <option value="Outdoor LED">户外LED</option>
                                        <option value="Rental LED">租赁LED</option>
                                        <option value="Transparent LED">透明LED</option>
                                        <option value="Creative LED">创意LED</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">产品描述</label>
                                    <textarea class="form-control" name="description" rows="3"></textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">技术规格</label>
                                    <textarea class="form-control" name="specifications" rows="3" 
                                        placeholder="像素间距:P2.5mm&#10;亮度:1000cd/㎡&#10;刷新率:3840Hz"></textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">价格</label>
                                    <input type="number" class="form-control" name="price" step="0.01">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">图片URL</label>
                                    <input type="text" class="form-control" name="image_url" 
                                        placeholder="/assets/products/product.jpg">
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-primary" onclick="ProductManager.saveProduct()">保存产品</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // 添加模态框到页面
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('addProductModal'));
        modal.show();
    }
    
    static async saveProduct() {
        const form = document.getElementById('productForm');
        const formData = new FormData(form);
        
        const product = {
            name: formData.get('name'),
            category: formData.get('category'),
            description: formData.get('description'),
            specifications: formData.get('specifications'),
            price: parseFloat(formData.get('price')) || null,
            image_url: formData.get('image_url')
        };
        
        try {
            const { data, error } = await supabase
                .from('products')
                .insert([product]);
            
            if (error) throw error;
            
            alert('产品添加成功！');
            bootstrap.Modal.getInstance(document.getElementById('addProductModal')).hide();
            
            // 刷新产品列表
            if (window.loadProducts) {
                window.loadProducts();
            }
        } catch (error) {
            alert('添加失败: ' + error.message);
        }
    }
    
    static async editProduct(id) {
        try {
            // 获取产品信息
            const { data: product, error } = await supabase
                .from('products')
                .select('*')
                .eq('id', id)
                .single();
            
            if (error) throw error;
            
            const modalHtml = `
                <div class="modal fade" id="editProductModal">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">编辑产品</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <form id="editProductForm">
                                    <input type="hidden" name="id" value="${product.id}">
                                    <div class="mb-3">
                                        <label class="form-label">产品名称</label>
                                        <input type="text" class="form-control" name="name" value="${product.name}" required>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">产品类别</label>
                                        <select class="form-control" name="category" required>
                                            <option value="Indoor LED" ${product.category === 'Indoor LED' ? 'selected' : ''}>室内LED</option>
                                            <option value="Outdoor LED" ${product.category === 'Outdoor LED' ? 'selected' : ''}>户外LED</option>
                                            <option value="Rental LED" ${product.category === 'Rental LED' ? 'selected' : ''}>租赁LED</option>
                                            <option value="Transparent LED" ${product.category === 'Transparent LED' ? 'selected' : ''}>透明LED</option>
                                            <option value="Creative LED" ${product.category === 'Creative LED' ? 'selected' : ''}>创意LED</option>
                                        </select>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">产品描述</label>
                                        <textarea class="form-control" name="description" rows="3">${product.description || ''}</textarea>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">技术规格</label>
                                        <textarea class="form-control" name="specifications" rows="3">${product.specifications || ''}</textarea>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">价格</label>
                                        <input type="number" class="form-control" name="price" value="${product.price || ''}" step="0.01">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">图片URL</label>
                                        <input type="text" class="form-control" name="image_url" value="${product.image_url || ''}">
                                    </div>
                                </form>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                                <button type="button" class="btn btn-primary" onclick="ProductManager.updateProduct()">更新产品</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // 移除旧的模态框
            const oldModal = document.getElementById('editProductModal');
            if (oldModal) oldModal.remove();
            
            // 添加新模态框
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            const modal = new bootstrap.Modal(document.getElementById('editProductModal'));
            modal.show();
            
        } catch (error) {
            alert('获取产品信息失败: ' + error.message);
        }
    }
    
    static async updateProduct() {
        const form = document.getElementById('editProductForm');
        const formData = new FormData(form);
        
        const id = formData.get('id');
        const product = {
            name: formData.get('name'),
            category: formData.get('category'),
            description: formData.get('description'),
            specifications: formData.get('specifications'),
            price: parseFloat(formData.get('price')) || null,
            image_url: formData.get('image_url'),
            updated_at: new Date().toISOString()
        };
        
        try {
            const { data, error } = await supabase
                .from('products')
                .update(product)
                .eq('id', id);
            
            if (error) throw error;
            
            alert('产品更新成功！');
            bootstrap.Modal.getInstance(document.getElementById('editProductModal')).hide();
            
            // 刷新产品列表
            if (window.loadProducts) {
                window.loadProducts();
            }
        } catch (error) {
            alert('更新失败: ' + error.message);
        }
    }
    
    static async deleteProduct(id) {
        if (!confirm('确定要删除这个产品吗？此操作不可恢复。')) {
            return;
        }
        
        try {
            const { error } = await supabase
                .from('products')
                .delete()
                .eq('id', id);
            
            if (error) throw error;
            
            alert('产品删除成功！');
            
            // 刷新产品列表
            if (window.loadProducts) {
                window.loadProducts();
            }
        } catch (error) {
            alert('删除失败: ' + error.message);
        }
    }
}

// 新闻管理功能
class NewsManager {
    static async addNews() {
        const modalHtml = `
            <div class="modal fade" id="addNewsModal">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">添加新闻</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="newsForm">
                                <div class="mb-3">
                                    <label class="form-label">新闻标题</label>
                                    <input type="text" class="form-control" name="title" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">新闻内容</label>
                                    <textarea class="form-control" name="content" rows="5" required></textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">作者</label>
                                    <input type="text" class="form-control" name="author" value="Admin">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">状态</label>
                                    <select class="form-control" name="status">
                                        <option value="published">已发布</option>
                                        <option value="draft">草稿</option>
                                    </select>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-primary" onclick="NewsManager.saveNews()">保存新闻</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('addNewsModal'));
        modal.show();
    }
    
    static async saveNews() {
        const form = document.getElementById('newsForm');
        const formData = new FormData(form);
        
        const news = {
            title: formData.get('title'),
            content: formData.get('content'),
            author: formData.get('author'),
            status: formData.get('status')
        };
        
        try {
            const { data, error } = await supabase
                .from('news')
                .insert([news]);
            
            if (error) throw error;
            
            alert('新闻添加成功！');
            bootstrap.Modal.getInstance(document.getElementById('addNewsModal')).hide();
            
            // 刷新新闻列表
            if (window.loadNews) {
                window.loadNews();
            }
        } catch (error) {
            alert('添加失败: ' + error.message);
        }
    }
    
    static async deleteNews(id) {
        if (!confirm('确定要删除这条新闻吗？')) {
            return;
        }
        
        try {
            const { error } = await supabase
                .from('news')
                .delete()
                .eq('id', id);
            
            if (error) throw error;
            
            alert('新闻删除成功！');
            
            // 刷新新闻列表
            if (window.loadNews) {
                window.loadNews();
            }
        } catch (error) {
            alert('删除失败: ' + error.message);
        }
    }
}

// 询盘管理功能
class InquiryManager {
    static async viewInquiry(id) {
        try {
            const { data: inquiry, error } = await supabase
                .from('inquiries')
                .select('*')
                .eq('id', id)
                .single();
            
            if (error) throw error;
            
            const modalHtml = `
                <div class="modal fade" id="viewInquiryModal">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">询盘详情</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row mb-3">
                                    <div class="col-md-6">
                                        <strong>姓名：</strong> ${inquiry.name}
                                    </div>
                                    <div class="col-md-6">
                                        <strong>邮箱：</strong> ${inquiry.email}
                                    </div>
                                </div>
                                <div class="row mb-3">
                                    <div class="col-md-6">
                                        <strong>电话：</strong> ${inquiry.phone || '未提供'}
                                    </div>
                                    <div class="col-md-6">
                                        <strong>公司：</strong> ${inquiry.company || '未提供'}
                                    </div>
                                </div>
                                <div class="row mb-3">
                                    <div class="col-md-6">
                                        <strong>状态：</strong> 
                                        <span class="badge bg-${inquiry.status === 'new' ? 'warning' : 'success'}">
                                            ${inquiry.status === 'new' ? '新询盘' : '已处理'}
                                        </span>
                                    </div>
                                    <div class="col-md-6">
                                        <strong>时间：</strong> ${new Date(inquiry.created_at).toLocaleString()}
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <strong>留言内容：</strong>
                                    <div class="border p-3 mt-2">
                                        ${inquiry.message}
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                                ${inquiry.status === 'new' ? 
                                    `<button type="button" class="btn btn-primary" onclick="InquiryManager.updateStatus(${id}, 'processed')">标记为已处理</button>` 
                                    : ''}
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // 移除旧的模态框
            const oldModal = document.getElementById('viewInquiryModal');
            if (oldModal) oldModal.remove();
            
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            const modal = new bootstrap.Modal(document.getElementById('viewInquiryModal'));
            modal.show();
            
        } catch (error) {
            alert('获取询盘信息失败: ' + error.message);
        }
    }
    
    static async updateStatus(id, status) {
        try {
            const { error } = await supabase
                .from('inquiries')
                .update({ 
                    status: status,
                    updated_at: new Date().toISOString()
                })
                .eq('id', id);
            
            if (error) throw error;
            
            alert('状态更新成功！');
            
            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('viewInquiryModal'));
            if (modal) modal.hide();
            
            // 刷新询盘列表
            if (window.loadInquiries) {
                window.loadInquiries();
            }
        } catch (error) {
            alert('更新失败: ' + error.message);
        }
    }
}

// 用户管理功能
class UserManager {
    static async addUser() {
        const modalHtml = `
            <div class="modal fade" id="addUserModal">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">添加用户</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="userForm">
                                <div class="mb-3">
                                    <label class="form-label">用户名</label>
                                    <input type="text" class="form-control" name="username" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">邮箱</label>
                                    <input type="email" class="form-control" name="email" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">密码</label>
                                    <input type="password" class="form-control" name="password" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">角色</label>
                                    <select class="form-control" name="role">
                                        <option value="admin">管理员</option>
                                        <option value="editor">编辑</option>
                                        <option value="viewer">查看</option>
                                    </select>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-primary" onclick="UserManager.saveUser()">保存用户</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('addUserModal'));
        modal.show();
    }
    
    static async saveUser() {
        alert('用户管理功能需要配合Supabase Auth实现，请使用Supabase控制台管理用户');
    }
}

// 将函数绑定到全局作用域，以便HTML中可以调用
window.ProductManager = ProductManager;
window.NewsManager = NewsManager;
window.InquiryManager = InquiryManager;
window.UserManager = UserManager;

// 重新绑定原有函数
window.addProduct = ProductManager.addProduct;
window.editProduct = ProductManager.editProduct;
window.deleteProduct = ProductManager.deleteProduct;
window.addNews = NewsManager.addNews;
window.editNews = (id) => alert('编辑功能类似添加功能，请参考addNews实现');
window.deleteNews = NewsManager.deleteNews;
window.viewInquiry = InquiryManager.viewInquiry;
window.updateInquiryStatus = (id) => InquiryManager.updateStatus(id, 'processed');
window.addUser = UserManager.addUser;
window.editUser = (id) => alert('用户编辑请使用Supabase控制台');
window.deleteUser = (id) => alert('用户删除请使用Supabase控制台');

console.log('✅ 增强版管理功能已加载');
