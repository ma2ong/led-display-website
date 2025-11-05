-- ============================================
-- 第 0 步：检查数据库当前状态
-- 运行此脚本查看哪些表已经存在
-- ============================================

-- 查看所有现有的表
SELECT
    table_name,
    table_schema
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- 查看是否有 auth.users 表（Supabase 内置）
SELECT COUNT(*) as auth_users_exists
FROM information_schema.tables
WHERE table_schema = 'auth' AND table_name = 'users';
