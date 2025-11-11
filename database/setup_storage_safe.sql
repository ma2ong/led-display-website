-- ============================================
-- Supabase Storage 配置（安全版 - 可重复执行）
-- 图片管理系统 - 存储桶和权限设置
-- ============================================

-- 步骤 1: 创建存储桶 (Buckets)
-- ============================================

-- 注意：存储桶需要在 Supabase Dashboard 中手动创建
-- 路径：Storage → New Bucket
--
-- 创建以下存储桶：
-- 1. 名称：led-images
--    Public: ✅ 勾选（公开访问）
--    File size limit: 5 MB
--    Allowed MIME types: image/jpeg, image/png, image/webp, image/gif

-- 步骤 2: 清理旧的存储桶策略（如果存在）
-- ============================================

DROP POLICY IF EXISTS "Public Access" ON storage.objects;
DROP POLICY IF EXISTS "Authenticated users can upload images" ON storage.objects;
DROP POLICY IF EXISTS "Authenticated users can update images" ON storage.objects;
DROP POLICY IF EXISTS "Admins can delete images" ON storage.objects;

-- 步骤 3: 创建存储桶策略 (RLS Policies)
-- ============================================

-- 3.1 允许所有人查看图片（公开读取）
CREATE POLICY "Public Access"
ON storage.objects FOR SELECT
USING ( bucket_id = 'led-images' );

-- 3.2 允许已认证用户上传图片
CREATE POLICY "Authenticated users can upload images"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK ( bucket_id = 'led-images' );

-- 3.3 允许已认证用户更新图片
CREATE POLICY "Authenticated users can update images"
ON storage.objects FOR UPDATE
TO authenticated
USING ( bucket_id = 'led-images' );

-- 3.4 允许管理员删除图片
CREATE POLICY "Admins can delete images"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'led-images' AND
  EXISTS (
    SELECT 1 FROM admin_users
    WHERE user_id = auth.uid()
    AND is_active = true
    AND role IN ('super_admin', 'admin')
  )
);

-- 步骤 4: 创建图片元数据表
-- ============================================

CREATE TABLE IF NOT EXISTS image_metadata (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,

  -- 基本信息
  filename VARCHAR(255) NOT NULL,              -- 文件名
  original_filename VARCHAR(255) NOT NULL,     -- 原始文件名
  storage_path TEXT NOT NULL,                  -- 存储路径
  public_url TEXT NOT NULL,                    -- 公开访问 URL

  -- 分类信息
  category VARCHAR(50) NOT NULL,               -- 分类：products, cases, certificates, etc.
  subcategory VARCHAR(50),                     -- 子分类：outdoor, indoor, etc.
  tags TEXT[],                                 -- 标签数组

  -- 图片信息
  file_size INTEGER,                           -- 文件大小（字节）
  mime_type VARCHAR(50),                       -- MIME 类型
  width INTEGER,                               -- 宽度（像素）
  height INTEGER,                              -- 高度（像素）

  -- 元数据
  title VARCHAR(255),                          -- 标题
  description TEXT,                            -- 描述
  alt_text VARCHAR(255),                       -- Alt 文本（SEO）

  -- 上传信息
  uploaded_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  uploaded_at TIMESTAMPTZ DEFAULT NOW(),

  -- 使用信息
  usage_count INTEGER DEFAULT 0,              -- 使用次数
  last_used_at TIMESTAMPTZ,                   -- 最后使用时间

  -- 状态
  is_active BOOLEAN DEFAULT true,             -- 是否激活

  -- 时间戳
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 步骤 5: 创建索引（安全方式）
-- ============================================

DROP INDEX IF EXISTS idx_image_metadata_category;
DROP INDEX IF EXISTS idx_image_metadata_subcategory;
DROP INDEX IF EXISTS idx_image_metadata_uploaded_by;
DROP INDEX IF EXISTS idx_image_metadata_created_at;

CREATE INDEX idx_image_metadata_category ON image_metadata(category);
CREATE INDEX idx_image_metadata_subcategory ON image_metadata(subcategory);
CREATE INDEX idx_image_metadata_uploaded_by ON image_metadata(uploaded_by);
CREATE INDEX idx_image_metadata_created_at ON image_metadata(created_at DESC);

-- 步骤 6: 创建更新时间触发器
-- ============================================

CREATE OR REPLACE FUNCTION update_image_metadata_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS image_metadata_updated_at ON image_metadata;

CREATE TRIGGER image_metadata_updated_at
  BEFORE UPDATE ON image_metadata
  FOR EACH ROW
  EXECUTE FUNCTION update_image_metadata_updated_at();

-- 步骤 7: 设置表 RLS 策略
-- ============================================

ALTER TABLE image_metadata ENABLE ROW LEVEL SECURITY;

-- 清理旧策略
DROP POLICY IF EXISTS "Anyone can view active images" ON image_metadata;
DROP POLICY IF EXISTS "Authenticated users can insert image metadata" ON image_metadata;
DROP POLICY IF EXISTS "Users can update their own image metadata" ON image_metadata;
DROP POLICY IF EXISTS "Admins can delete image metadata" ON image_metadata;

-- 创建新策略
-- 允许所有人查看激活的图片元数据
CREATE POLICY "Anyone can view active images"
ON image_metadata FOR SELECT
USING (is_active = true);

-- 允许已认证用户插入图片元数据
CREATE POLICY "Authenticated users can insert image metadata"
ON image_metadata FOR INSERT
TO authenticated
WITH CHECK (uploaded_by = auth.uid());

-- 允许上传者更新自己的图片元数据
CREATE POLICY "Users can update their own image metadata"
ON image_metadata FOR UPDATE
TO authenticated
USING (uploaded_by = auth.uid());

-- 允许管理员删除图片元数据
CREATE POLICY "Admins can delete image metadata"
ON image_metadata FOR DELETE
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM admin_users
    WHERE user_id = auth.uid()
    AND is_active = true
    AND role IN ('super_admin', 'admin')
  )
);

-- 步骤 8: 创建辅助函数
-- ============================================

-- 获取图片统计信息
CREATE OR REPLACE FUNCTION get_image_stats()
RETURNS TABLE (
  total_images BIGINT,
  total_size BIGINT,
  categories JSON
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    COUNT(*)::BIGINT as total_images,
    COALESCE(SUM(file_size), 0)::BIGINT as total_size,
    json_agg(
      json_build_object(
        'category', category,
        'count', count
      )
    ) as categories
  FROM (
    SELECT
      category,
      COUNT(*) as count
    FROM image_metadata
    WHERE is_active = true
    GROUP BY category
  ) cat_counts;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 增加图片使用计数
CREATE OR REPLACE FUNCTION increment_image_usage(image_id UUID)
RETURNS VOID AS $$
BEGIN
  UPDATE image_metadata
  SET
    usage_count = usage_count + 1,
    last_used_at = NOW()
  WHERE id = image_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 步骤 9: 预定义分类
-- ============================================

-- 创建分类配置表
CREATE TABLE IF NOT EXISTS image_categories (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL,
  display_name VARCHAR(100) NOT NULL,
  description TEXT,
  icon VARCHAR(50),
  sort_order INTEGER DEFAULT 0,
  is_active BOOLEAN DEFAULT true
);

-- 插入预定义分类
INSERT INTO image_categories (name, display_name, description, icon, sort_order) VALUES
('products', '产品图片', 'LED 显示屏产品照片', 'box', 1),
('cases', '案例图片', '项目案例和应用场景', 'briefcase', 2),
('certificates', '证书资质', '公司证书和资质文件', 'award', 3),
('about', '关于我们', '公司照片、团队合影等', 'building', 4),
('solutions', '解决方案', '行业解决方案配图', 'lightbulb', 5),
('news', '新闻资讯', '新闻配图', 'newspaper', 6),
('support', '技术支持', '技术文档配图', 'tool', 7),
('backgrounds', '背景图片', '页面背景和 Banner', 'image', 8),
('logos', 'Logo 图标', '公司 Logo 和图标', 'star', 9),
('other', '其他', '其他类型图片', 'folder', 10)
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- 完成提示
-- ============================================

-- 验证配置
SELECT
  'Storage Buckets' as component,
  COUNT(*) as count
FROM storage.buckets
WHERE name = 'led-images'

UNION ALL

SELECT
  'Storage Policies' as component,
  COUNT(*) as count
FROM pg_policies
WHERE tablename = 'objects' AND schemaname = 'storage'
AND policyname IN ('Public Access', 'Authenticated users can upload images',
                   'Authenticated users can update images', 'Admins can delete images')

UNION ALL

SELECT
  'Image Metadata Table' as component,
  COUNT(*) as count
FROM information_schema.tables
WHERE table_name = 'image_metadata'

UNION ALL

SELECT
  'Image Metadata Policies' as component,
  COUNT(*) as count
FROM pg_policies
WHERE tablename = 'image_metadata'

UNION ALL

SELECT
  'Image Categories' as component,
  COUNT(*) as count
FROM image_categories;

-- ============================================
-- 使用说明
-- ============================================

/*
✅ 配置完成！

此脚本已安全执行，可以重复运行而不会报错。

验证结果应该显示：
- Storage Buckets: 1
- Storage Policies: 4
- Image Metadata Table: 1
- Image Metadata Policies: 4
- Image Categories: 10

下一步：
1. ✅ 确认 'led-images' 存储桶已在 Dashboard 创建
2. ✅ 访问媒体管理器开始上传图片
3. ✅ 图片会自动保存到 Supabase Storage

图片 URL 格式：
https://jirudzbqcxviytcmxegf.supabase.co/storage/v1/object/public/led-images/products/xxx.jpg

如有问题，请检查：
1. led-images bucket 是否标记为 Public
2. 管理员账号是否已登录
3. admin_users 表中是否有您的用户记录
*/
