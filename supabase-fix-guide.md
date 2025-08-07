# Supabase产品表写入失败修复指南

## 问题分析

HTTP 400错误通常由以下原因引起：
1. 表结构与提交数据不匹配
2. 数据类型错误
3. 必填字段缺失
4. 权限配置问题

## 解决方案

### 1. 检查并修复表结构

首先在Supabase SQL Editor中执行以下SQL来检查当前表结构：

```sql
-- 检查products表结构
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'products' 
ORDER BY ordinal_position;
```

### 2. 重新创建products表（如果需要）

如果表结构有问题，执行以下SQL重新创建：

```sql
-- 删除现有products表
DROP TABLE IF EXISTS products CASCADE;

-- 重新创建products表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    specifications TEXT,
    price NUMERIC(10,2),
    image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 启用RLS
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- 创建策略
CREATE POLICY "Products are viewable by everyone" 
ON products FOR SELECT USING (true);

CREATE POLICY "Products are insertable by everyone" 
ON products FOR INSERT WITH CHECK (true);

CREATE POLICY "Products are updatable by authenticated users" 
ON products FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Products are deletable by authenticated users" 
ON products FOR DELETE USING (auth.role() = 'authenticated');
```

### 3. 插入测试数据

```sql
-- 插入测试产品数据
INSERT INTO products (name, category, description, specifications, price, image_url) VALUES
('P2.5室内LED显示屏', 'indoor', 'P2.5高清室内LED显示屏，适用于会议室、展厅等场所', '像素间距:2.5mm\n亮度:800cd/㎡\n刷新率:3840Hz', 1200.00, '/assets/products/indoor-led.jpg'),
('P10户外LED显示屏', 'outdoor', 'P10高亮度户外LED显示屏，防水防尘，适用于户外广告', '像素间距:10mm\n亮度:6500cd/㎡\n防护等级:IP65', 800.00, '/assets/products/outdoor-led.jpg'),
('租赁LED显示屏', 'rental', '轻便易装的租赁LED显示屏，适用于演出、会议等临时场合', '重量:6.5kg/㎡\n厚度:75mm\n安装:快锁设计', 1500.00, '/assets/products/rental-led.jpg'),
('透明LED显示屏', 'creative', '高透明度LED显示屏，不影响采光，适用于玻璃幕墙', '透明度:85%\n像素间距:3.9mm\n厚度:10mm', 2000.00, '/assets/products/transparent-led.jpg');
```

### 4. 验证表创建成功

```sql
-- 验证数据插入
SELECT COUNT(*) as total_products FROM products;
SELECT * FROM products LIMIT 5;
```

## 前端代码修复

确保前端提交的数据格式正确：

```javascript
// 正确的数据格式
const productData = {
    name: "产品名称",           // TEXT NOT NULL
    category: "产品分类",       // TEXT NOT NULL  
    description: "产品描述",    // TEXT (可选)
    specifications: "规格参数", // TEXT (可选)
    price: 1200.50,            // NUMERIC(10,2) (可选)
    image_url: "/path/to/image.jpg" // TEXT (可选)
};
```

## 常见错误及解决方法

### 错误1: 字段名不匹配
- 确保前端字段名与数据库字段名完全一致
- 检查是否有拼写错误

### 错误2: 数据类型错误
- price字段必须是数字类型，不能是字符串
- 日期字段使用正确的格式

### 错误3: 必填字段缺失
- name和category是必填字段，不能为空或null

### 错误4: 权限问题
- 检查RLS策略是否正确配置
- 确保匿名用户有插入权限

## 测试步骤

1. 在Supabase Dashboard中手动插入一条记录
2. 使用前端表单提交测试数据
3. 检查浏览器控制台是否有错误信息
4. 查看Supabase日志获取详细错误信息

## 联系支持

如果问题仍然存在，请提供：
1. 完整的错误信息
2. 提交的数据格式
3. Supabase项目URL
4. 浏览器控制台截图