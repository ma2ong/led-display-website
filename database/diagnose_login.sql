-- ============================================
-- 登录问题诊断脚本
-- ============================================
-- 此脚本帮助诊断管理员登录失败的原因

-- 步骤 1: 检查 admin_users 表是否存在
SELECT
  'admin_users 表检查' as check_type,
  CASE
    WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'admin_users')
    THEN '✅ 表存在'
    ELSE '❌ 表不存在 - 请先运行数据库迁移脚本'
  END as status;

-- 步骤 2: 检查 admin_login_logs 表是否存在
SELECT
  'admin_login_logs 表检查' as check_type,
  CASE
    WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'admin_login_logs')
    THEN '✅ 表存在'
    ELSE '❌ 表不存在 - 请先运行数据库迁移脚本'
  END as status;

-- 步骤 3: 查看所有认证用户（auth.users）
SELECT
  '认证用户列表' as info,
  id as user_id,
  email,
  created_at,
  confirmed_at,
  CASE
    WHEN confirmed_at IS NOT NULL THEN '✅ 已确认'
    ELSE '⚠️ 未确认邮箱'
  END as email_status
FROM auth.users
ORDER BY created_at DESC;

-- 步骤 4: 查看所有管理员用户（admin_users）
SELECT
  '管理员用户列表' as info,
  id,
  user_id,
  email,
  role,
  is_active,
  created_at,
  CASE
    WHEN is_active THEN '✅ 活跃'
    ELSE '❌ 已禁用'
  END as status
FROM admin_users
ORDER BY created_at DESC;

-- 步骤 5: 检查孤立的认证用户（在 auth.users 中但不在 admin_users 中）
SELECT
  '孤立用户检查' as check_type,
  u.id as user_id,
  u.email,
  '⚠️ 用户存在于 auth.users 但不在 admin_users 中' as issue,
  '需要手动添加到 admin_users 表' as solution
FROM auth.users u
LEFT JOIN admin_users au ON u.id = au.user_id
WHERE au.user_id IS NULL;

-- 步骤 6: 检查 RLS 策略
SELECT
  'RLS 策略检查' as check_type,
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd as command,
  qual as using_expression
FROM pg_policies
WHERE tablename IN ('admin_users', 'admin_login_logs')
ORDER BY tablename, policyname;

-- 步骤 7: 检查最近的登录尝试
SELECT
  '最近登录记录' as info,
  email,
  status,
  error_message,
  ip_address,
  created_at
FROM admin_login_logs
ORDER BY created_at DESC
LIMIT 10;

-- ============================================
-- 常见问题和解决方案
-- ============================================
/*
问题 1: 用户只在 auth.users 中，不在 admin_users 中
解决: 运行以下 SQL 添加用户到 admin_users 表

INSERT INTO admin_users (user_id, email, role, is_active)
SELECT
  id,
  email,
  'super_admin',
  true
FROM auth.users
WHERE email = 'your-email@example.com'  -- 替换为你的邮箱
ON CONFLICT (user_id) DO NOTHING;


问题 2: 用户的 is_active 为 false
解决: 激活用户

UPDATE admin_users
SET is_active = true
WHERE email = 'your-email@example.com';  -- 替换为你的邮箱


问题 3: 用户的 role 不正确
解决: 更新角色

UPDATE admin_users
SET role = 'super_admin'
WHERE email = 'your-email@example.com';  -- 替换为你的邮箱


问题 4: 邮箱未确认
解决: 在 Supabase Dashboard 中手动确认邮箱
或运行以下 SQL (需要 service_role 权限):

UPDATE auth.users
SET confirmed_at = NOW(),
    email_confirmed_at = NOW()
WHERE email = 'your-email@example.com';  -- 替换为你的邮箱
*/
