// 导入Supabase客户端
import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm'
import { supabase } from './supabase-admin.js'

// 全局变量
let currentProductPage = 1;
let currentInquiryPage = 1;
let currentNewsPage = 1;
const itemsPerPage = 10;

// 加载仪表盘数据
export async function loadDashboardData() {
    try {
        document.getElementById('loadingOverlay').style.display = 'flex';
        
        // 获取产品数量
        const { count: productCount, error: productError } = await supabase
            .from('products')
            .select('*', { count: 'exact', head: true });
            
        if (!productError) {
            document.getElementById('productCount').textContent = productCount;
        }
        
        // 获取询盘数量
        const { count: inquiryCount, error: inquiryError } = await supabase
            .from('inquiries')
            .select('*', { count: 'exact', head: true });
            
        if (!inquiryError) {
            document.getElementById('inquiryCount').textContent = inquiryCount;
        }
        
        // 获取新闻数量
        const { count: newsCount, error: newsError } = await supabase
            .from('news')
            .select('*', { count: 'exact', head: true });
            
        if (!newsError) {
            document.getElementById('newsCount').textContent = newsCount;
        }
        
        // 获取用户数量
        const { count: userCount, error: userError } = await supabase
            .from('admin_users')
            .select('*', { count: 'exact', head: true });
            
        if (!userError) {
            document.getElementById('totalUsers').textContent = userCount;
        }
        
        // 获取最新询盘
        const { data: latestInquiries, error: latestInquiryError } = await supabase
            .from('inquiries')
            .select('*')
            .order('created_at', { ascending: false })
            .limit(5);
            
        if (!latestInquiryError && latestInquiries.length > 0) {
            const tableBody = document.getElementById('latestInquiriesTable');
            tableBody.innerHTML = '';
            
            latestInquiries.forEach(inquiry => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${inquiry.name}</td>
                    <td>${inquiry.company}</td>
                    <td><span class="status-badge ${inquiry.status === 'pending' ? 'status-pending' : 'status-active'}">${inquiry.status === 'pending' ? '待处理' : '已处理'}</span></td>
                    <td>${new Date(inquiry.created_at).toLocaleDateString()}</td>
                `;
                tableBody.appendChild(row);
            });
        } else {
            document.getElementById('latestInquiriesTable').innerHTML = '<tr><td colspan="4" class="text-center">暂无询盘数据</td></tr>';
        }
        
        // 初始化访问统计图表
        initVisitsChart();
        
    } catch (error) {
        console.error('加载仪表盘数据失败:', error);
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

// 初始化访问统计图表
function initVisitsChart() {
    const ctx = document.getElementById('visitsChart').getContext('2d');
    
    // 模拟数据
    const labels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
    const data = {
        labels: labels,
        datasets: [{
            label: '网站访问量',
            data: [65, 59, 80, 81, 56, 55, 40],
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        }]
    };
    
    const config = {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    };
    
    new Chart(ctx, config);
}

// 加载产品列表
export async function loadProducts(page = 1) {
    try {
        document.getElementById('loadingOverlay').style.display = 'flex';
        
        // 计算分页
        const from = (page - 1) * itemsPerPage;
        const to = from + itemsPerPage - 1;
        
        // 获取产品总数
        const { count, error: countError } = await supabase
            .from('products')
            .select('*', { count: 'exact', head: true });
            
        if (countError) throw countError;
        
        const totalProducts = count;
        
        // 更新分页信息
        document.getElementById('productTotalCount').textContent = totalProducts;
        document.getElementById('productStartRange').textContent = from + 1;
        document.getElementById('productEndRange').textContent = Math.min(to + 1, totalProducts);
        
        // 禁用/启用分页按钮
        document.getElementById('productPrevBtn').disabled = page === 1;
        document.getElementById('productNextBtn').disabled = to + 1 >= totalProducts;
        
        // 获取产品列表
        const { data: products, error } = await supabase
            .from('products')
            .select('*')
            .range(from, to)
            .order('created_at', { ascending: false });
            
        if (error) throw error;
        
        // 更新产品表格
        const tableBody = document.getElementById('productsTable');
        tableBody.innerHTML = '';
        
        if (products.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center">暂无产品数据</td></tr>';
            return;
        }
        
        products.forEach(product => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${product.name}</td>
                <td>${product.category}</td>
                <td>${product.price ? '¥' + product.price : '面议'}</td>
                <td><span class="status-badge ${product.status === 'active' ? 'status-active' : 'status-inactive'}">${product.status === 'active' ? '上架' : '下架'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editProduct(${product.id})">编辑</button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteProduct(${product.id})">删除</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
        
        // 更新当前页码
        currentProductPage = page;
    } catch (error) {
        console.error('加载产品列表失败:', error);
        alert('加载产品列表失败: ' + error.message);
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

// 上一页产品
export function prevProductPage() {
    if (currentProductPage > 1) {
        loadProducts(currentProductPage - 1);
    }
}

// 下一页产品
export function nextProductPage() {
    loadProducts(currentProductPage + 1);
}

// 搜索产品
export async function searchProducts() {
    const searchTerm = document.getElementById('productSearchInput').value.trim();
    
    if (!searchTerm) {
        loadProducts(1);
        return;
    }
    
    try {
        document.getElementById('loadingOverlay').style.display = 'flex';
        
        const { data: products, error } = await supabase
            .from('products')
            .select('*')
            .ilike('name', `%${searchTerm}%`)
            .order('created_at', { ascending: false });
            
        if (error) throw error;
        
        // 更新产品表格
        const tableBody = document.getElementById('productsTable');
        tableBody.innerHTML = '';
        
        if (products.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center">未找到匹配的产品</td></tr>';
            return;
        }
        
        products.forEach(product => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${product.name}</td>
                <td>${product.category}</td>
                <td>${product.price ? '¥' + product.price : '面议'}</td>
                <td><span class="status-badge ${product.status === 'active' ? 'status-active' : 'status-inactive'}">${product.status === 'active' ? '上架' : '下架'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editProduct(${product.id})">编辑</button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteProduct(${product.id})">删除</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
        
        // 更新分页信息
        document.getElementById('productTotalCount').textContent = products.length;
        document.getElementById('productStartRange').textContent = '1';
        document.getElementById('productEndRange').textContent = products.length;
        
        // 禁用分页按钮
        document.getElementById('productPrevBtn').disabled = true;
        document.getElementById('productNextBtn').disabled = true;
    } catch (error) {
        console.error('搜索产品失败:', error);
        alert('搜索产品失败: ' + error.message);
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

// 显示产品编辑模态框
export function showProductModal(productId = null) {
    // 重置表单
    document.getElementById('productForm').reset();
    document.getElementById('productId').value = '';
    document.getElementById('productImagePreview').innerHTML = '';
    
    if (productId) {
        // 编辑现有产品
        document.getElementById('productModalTitle').textContent = '编辑产品';
        
        // 获取产品数据
        supabase
            .from('products')
            .select('*')
            .eq('id', productId)
            .single()
            .then(({ data, error }) => {
                if (error) {
                    console.error('获取产品数据失败:', error);
                    return;
                }
                
                // 填充表单
                document.getElementById('productId').value = data.id;
                document.getElementById('productName').value = data.name;
                document.getElementById('productCategory').value = data.category;
                document.getElementById('productPrice').value = data.price || '';
                document.getElementById('productStatus').value = data.status;
                document.getElementById('productDescription').value = data.description || '';
                
                // 显示产品图片预览
                if (data.image_url) {
                    const imgPreview = document.createElement('img');
                    imgPreview.src = data.image_url;
                    imgPreview.className = 'preview-image';
                    document.getElementById('productImagePreview').appendChild(imgPreview);
                }
            });
    } else {
        // 添加新产品
        document.getElementById('productModalTitle').textContent = '添加产品';
    }
    
    // 显示模态框
    const productModal = new bootstrap.Modal(document.getElementById('productModal'));
    productModal.show();
}

// 保存产品
export async function saveProduct() {
    try {
        document.getElementById('loadingOverlay').style.display = 'flex';
        
        const productId = document.getElementById('productId').value;
        const productName = document.getElementById('productName').value;
        const productCategory = document.getElementById('productCategory').value;
        const productPrice = document.getElementById('productPrice').value;
        const productStatus = document.getElementById('productStatus').value;
        const productDescription = document.getElementById('productDescription').value;
        const productImage = document.getElementById('productImage').files[0];
        
        if (!productName) {
            alert('请输入产品名称');
            return;
        }
        
        // 准备产品数据
        const productData = {
            name: productName,
            category: productCategory,
            price: productPrice ? parseFloat(productPrice) : null,
            status: productStatus,
            description: productDescription,
            updated_at: new Date().toISOString()
        };
        
        // 如果有新图片，先上传图片
        if (productImage) {
            const fileExt = productImage.name.split('.').pop();
            const fileName = `${Date.now()}.${fileExt}`;
            const filePath = `products/${fileName}`;
            
            const { data: uploadData, error: uploadError } = await supabase.storage
                .from('images')
                .upload(filePath, productImage);
                
            if (uploadError) {
                throw uploadError;
            }
            
            // 获取图片URL
            const { data: { publicUrl } } = supabase.storage
                .from('images')
                .getPublicUrl(filePath);
                
            productData.image_url = publicUrl;
        }
        
        let result;
        
        if (productId) {
            // 更新现有产品
            result = await supabase
                .from('products')
                .update(productData)
                .eq('id', productId);
        } else {
            // 添加新产品
            productData.created_at = new Date().toISOString();
            result = await supabase
                .from('products')
                .insert([productData]);
        }
        
        if (result.error) {
            throw result.error;
        }
        
        // 关闭模态框
        const productModal = bootstrap.Modal.getInstance(document.getElementById('productModal'));
        productModal.hide();
        
        // 重新加载产品列表
        loadProducts(currentProductPage);
        
        alert(productId ? '产品更新成功' : '产品添加成功');
    } catch (error) {
        console.error('保存产品失败:', error);
        alert('保存产品失败: ' + error.message);
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

// 删除产品
export async function deleteProduct(productId) {
    if (!confirm('确定要删除这个产品吗？')) {
        return;
    }
    
    try {
        document.getElementById('loadingOverlay').style.display = 'flex';
        
        const { error } = await supabase
            .from('products')
            .delete()
            .eq('id', productId);
            
        if (error) {
            throw error;
        }
        
        // 重新加载产品列表
        loadProducts(currentProductPage);
        
        alert('产品删除成功');
    } catch (error) {
        console.error('删除产品失败:', error);
        alert('删除产品失败: ' + error.message);
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

// 加载询盘列表
export async function loadInquiries(page = 1) {
    try {
        document.getElementById('loadingOverlay').style.display = 'flex';
        
        // 计算分页
        const from = (page - 1) * itemsPerPage;
        const to = from + itemsPerPage - 1;
        
        // 获取询盘总数
        const { count, error: countError } = await supabase
            .from('inquiries')
            .select('*', { count: 'exact', head: true });
            
        if (countError) throw countError;
        
        const totalInquiries = count;
        
        // 更新分页信息
        document.getElementById('inquiryTotalCount').textContent = totalInquiries;
        document.getElementById('inquiryStartRange').textContent = from + 1;
        document.getElementById('inquiryEndRange').textContent = Math.min(to + 1, totalInquiries);
        
        // 禁用/启用分页按钮
        document.getElementById('inquiryPrevBtn').disabled = page === 1;
        document.getElementById('inquiryNextBtn').disabled = to + 1 >= totalInquiries;
        
        // 获取询盘列表
        const { data: inquiries, error } = await supabase
            .from('inquiries')
            .select('*')
            .range(from, to)
            .order('created_at', { ascending: false });
            
        if (error) throw error;
        
        // 更新询盘表格
        const tableBody = document.getElementById('inquiriesTable');
        tableBody.innerHTML = '';
        
        if (inquiries.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7" class="text-center">暂无询盘数据</td></tr>';
            return;
        }
        
        inquiries.forEach(inquiry => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${inquiry.name}</td>
                <td>${inquiry.company}</td>
                <td>${inquiry.phone}</td>
                <td>${inquiry.email}</td>
                <td><span class="status-badge ${inquiry.status === 'pending' ? 'status-pending' : 'status-active'}">${inquiry.status === 'pending' ? '待处理' : '已处理'}</span></td>
                <td>${new Date(inquiry.created_at).toLocaleDateString()}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="viewInquiry('${inquiry.id}')">查看</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
        
        // 更新当前页码
        currentInquiryPage = page;
    } catch (error) {
        console.error('加载询盘列表失败:', error);
        alert('加载询盘列表失败: ' + error.message);
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

// 上一页询盘
export function prevInquiryPage() {
    if (currentInquiryPage > 1) {
        loadInquiries(currentInquiryPage - 1);
    }
}

// 下一页询盘
export function nextInquiryPage() {
    loadInquiries(currentInquiryPage + 1);
}

// 搜索询盘
export async function searchInquiries() {
    const searchTerm = document.getElementById('inquirySearchInput').value.trim();
    
    if (!searchTerm) {
        loadInquiries(1);
        return;
    }
    
    try {
        document.getElementById('loadingOverlay').style.display = 'flex';
        
        const { data: inquiries, error } = await supabase
            .from('inquiries')
            .select('*')
            .or(`name.ilike.%${searchTerm}%,company.ilike.%${searchTerm}%,email.ilike.%${searchTerm}%`)
            .order('created_at', { ascending: false });
            
        if (error) throw error;
        
        // 更新询盘表格
        const tableBody = document.getElementById('inquiriesTable');
        tableBody.innerHTML = '';
        
        if (inquiries.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7" class="text-center">未找到匹配的询盘</td></tr>';
            return;
        }
        
        inquiries.forEach(inquiry => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${inquiry.name}</td>
                <td>${inquiry.company}</td>
                <td>${inquiry.phone}</td>
                <td>${inquiry.email}</td>
                <td><span class="status-badge ${inquiry.status === 'pending' ? 'status-pending' : 'status-active'}">${inquiry.status === 'pending' ? '待处理' : '已处理'}</span></td>
                <td>${new Date(inquiry.created_at).toLocaleDateString()}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="viewInquiry('${inquiry.id}')">查看</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
        
        // 更新分页信息
        document.getElementById('inquiryTotalCount').textContent = inquiries.length;
        document.getElementById('inquiryStartRange').textContent = '1';
        document.getElementById('inquiryEndRange').textContent = inquiries.length;
        
        // 禁用分页按钮
        document.getElementById('inquiryPrevBtn').disabled = true;
        document.getElementById('inquiryNextBtn').disabled = true;
    } catch (error) {
        console.error('搜索询盘失败:', error);
        alert('搜索询盘失败: ' + error.message);
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

// 筛选询盘
export async function filterInquiries(status) {
    try {
        document.getElementById('loadingOverlay').style.display = 'flex';
        
        // 更新按钮状态
        document.querySelectorAll('#inquiries .btn-group .btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`#inquiries .btn-group .btn[onclick="filterInquiries('${status}')"]`).classList.add('active');
        
        let query = supabase
            .from('inquiries')
            .select('*')
            .order('created_at', { ascending: false });
            
        if (status !== 'all') {
            query = query.eq('status', status);
        }
        
        const { data: inquiries, error } = await query;
        
        if (error) throw error;
        
        // 更新询盘表格
        const tableBody = document.getElementById('inquiriesTable');
        tableBody.innerHTML = '';
        
        if (inquiries.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7" class="text-center">暂无询盘数据</td></tr>';
            return;
        }
        
        inquiries.forEach(inquiry => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${inquiry.name}</td>
                <td>${inquiry.company}</td>
                <td>${inquiry.phone}</td>
                <td>${inquiry.email}</td>
                <td><span class="status-badge ${inquiry.status === 'pending' ? 'status-pending' : 'status-active'}">${inquiry.status === 'pending' ? '待处理' : '已处理'}</span></td>
                <td>${new Date(inquiry.created_at).toLocaleDateString()}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="viewInquiry('${inquiry.id}')">查看</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
        
        // 更新分页信息
        document.getElementById('inquiryTotalCount').textContent = inquiries.length;
        document.getElementById('inquiryStartRange').textContent = '1';
        document.getElementById('inquiryEndRange').textContent = inquiries.length;
        
        // 禁用分页按钮
        document.getElementById('inquiryPrevBtn').disabled = true;
        document.getElementById('inquiryNextBtn').disabled = true;
    } catch (error) {
        console.error('筛选询盘失败:', error);
        alert('筛选询盘失败: ' + error.message);
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

// 查看询盘详情
export async function viewInquiry(inquiryId) {
    try {
        document.getElementById('loadingOverlay').style.display = 'flex';
        
        const { data: inquiry, error } = await supabase
            .from('inquiries')
            .select('*')
            .eq('id', inquiryId)
            .single();
            
        if (error) throw error;
        
        // 填充询盘详情
        document.getElementById('inquiryName').textContent = inquiry.name;
        document.getElementById('inquiryCompany').textContent = inquiry.company;
        document.getElementById('inquiryPhone').textContent = inquiry.phone;
        document.getElementById('inquiryEmail').textContent = inquiry.email;
        document.getElementById('inquiryTime').textContent = new Date(inquiry.created_at).toLocaleString();
        document.getElementById('inquiryStatus').textContent = inquiry.status === 'pending' ? '待处理' : '已处理';
        document.getElementById('inquiryMessage').textContent = inquiry.message;
        document.getElementById('inquiryNotes').value = inquiry.notes || '';
        document.getElementById('inquiryStatusUpdate').value = inquiry.status;
        
        // 存储询盘ID
        document.getElementById('inquiryModal').dataset.inquiryId = inquiryId;
        
        // 显示模态框
        const inquiryModal = new bootstrap.Modal(document.getElementById('inquiryModal'));
        inquiryModal.show();
    } catch (error) {
        console.error('获取询盘详情失败:', error);
        alert('获取询盘详情失败: ' + error.message);
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

// 更新询盘状态
export async function updateInquiry() {
    try {
        document.getElementById('loadingOverlay').style.display = 'flex';
        
        const inquiryId = document.getElementById('inquiryModal').dataset.inquiryId;
        const status = document.getElementById('inquiryStatusUpdate').value;
        const notes = document.getElementById('inquiryNotes').value;
        
        const { error } = await supabase
            .from('inquiries')
            .update({ status, notes, updated_at: new Date().toISOString() })
            .eq('id', inquiryId);
            
        if (error) throw error;
        
        // 关闭模态框
        const inquiryModal = bootstrap.Modal.getInstance(document.getElementById('inquiryModal'));
        inquiryModal.hide();
        
        // 重新加载询盘列表
        loadInquiries(currentInquiryPage);
        
        alert('询盘状态更新成功');
    } catch (error) {
        console.error('更新询盘状态失败:', error);
        alert('更新询盘状态失败: ' + error.message);
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

// 加载新闻列表
export async function loadNews(page = 1) {
    try {
        document.getElementById('loadingOverlay').style.display = 'flex';
        
        // 计算分页
        const from = (page - 1) * itemsPerPage;
        const to = from + itemsPerPage - 1;
        
        // 获取新闻总数
        const { count, error: countError } = await supabase
            .from('news')
            .select('*', { count: 'exact', head: true });
            
        if (countError) throw countError;
        
        const totalNews = count;
        
        // 更新分页信息
        document.getElementById('newsTotalCount').textContent = totalNews;
        document.getElementById('newsStartRange').textContent = from + 1;
        document.getElementById('newsEndRange').textContent = Math.min(to + 1, totalNews);
        
        // 禁用/启用分页按钮
        document.getElementById('newsPrevBtn').disabled = page === 1;
        document.getElementById('newsNextBtn').disabled = to + 1 >= totalNews;
        
        // 获取新闻列表
        const { data: news, error } = await supabase
            .from('news')
            .select('*')
            .range(from, to)
            .order('created_at', { ascending: false });
            
        if (error) throw error;
        
        // 更新新闻表格
        const tableBody = document.getElementById('newsTable');
        tableBody.innerHTML = '';
        
        if (news.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="6" class="text-center">暂无新闻数据</td></tr>';
            return;
        }
        
        news.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.title}</td>
                <td>${item.category}</td>
                <td>${item.author}</td>
                <td><span class="status-badge ${item.status === 'published' ? 'status-published' : 'status-draft'}">${item.status === 'published' ? '已发布' : '草稿'}</span></td>
                <td>${new Date(item.created_at).toLocaleDateString()}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editNews('${item.id}')">编辑</button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteNews('${item.id}')">删除</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
        
        // 更新当前页码
        currentNewsPage = page;
    } catch (error) {
        console.error('加载新闻列表失败:', error);
        alert('加载新闻列表失败: ' + error.message);
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

// 上一页新闻
export function prevNewsPage() {
    if (currentNewsPage > 1) {
        loadNews(currentNewsPage - 1);
    }
}