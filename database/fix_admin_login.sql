-- ============================================
-- 管理员登录问题修复脚本
-- ============================================
-- ⚠️ 重要：请先运行 diagnose_login.sql 诊断问题
-- 然后根据诊断结果，取消注释并修改相应的修复代码

-- ============================================
-- 修复 1: 添加用户到 admin_users 表
-- ============================================
-- 如果用户存在于 auth.users 但不在 admin_users 中

-- 🔧 将你的邮箱添加到管理员表
INSERT INTO admin_users (user_id, email, role, is_active)
SELECT
  id,
  email,
  'super_admin',  -- 可选: super_admin, admin, editor, viewer
  true
FROM auth.users
WHERE email = 'YOUR_EMAIL@example.com'  -- ⚠️ 替换为你的实际邮箱
ON CONFLICT (user_id) DO UPDATE
SET
  is_active = true,
  role = 'super_admin',
  updated_at = NOW();

-- ============================================
-- 修复 2: 激活被禁用的管理员账号
-- ============================================
/*
UPDATE admin_users
SET
  is_active = true,
  updated_at = NOW()
WHERE email = 'YOUR_EMAIL@example.com';  -- ⚠️ 替换为你的实际邮箱
*/

-- ============================================
-- 修复 3: 更新管理员角色
-- ============================================
/*
UPDATE admin_users
SET
  role = 'super_admin',  -- 可选: super_admin, admin, editor, viewer
  updated_at = NOW()
WHERE email = 'YOUR_EMAIL@example.com';  -- ⚠️ 替换为你的实际邮箱
*/

-- ============================================
-- 修复 4: 确认邮箱（如果邮箱未确认）
-- ============================================
-- ⚠️ 需要 service_role 权限，或在 Supabase Dashboard 手动确认
/*
UPDATE auth.users
SET
  confirmed_at = NOW(),
  email_confirmed_at = NOW()
WHERE email = 'YOUR_EMAIL@example.com';  -- ⚠️ 替换为你的实际邮箱
*/

-- ============================================
-- 修复 5: 批量添加多个管理员
-- ============================================
/*
INSERT INTO admin_users (user_id, email, role, is_active)
VALUES
  -- 从 auth.users 获取 user_id，然后手动添加
  ('user-id-1', 'admin1@example.com', 'super_admin', true),
  ('user-id-2', 'admin2@example.com', 'admin', true),
  ('user-id-3', 'editor@example.com', 'editor', true)
ON CONFLICT (user_id) DO UPDATE
SET
  is_active = EXCLUDED.is_active,
  role = EXCLUDED.role,
  updated_at = NOW();
*/

-- ============================================
-- 验证修复结果
-- ============================================
-- 运行此查询验证修复是否成功

SELECT
  au.email,
  au.role,
  au.is_active,
  u.confirmed_at,
  CASE
    WHEN au.is_active AND u.confirmed_at IS NOT NULL
    THEN '✅ 可以登录'
    WHEN NOT au.is_active
    THEN '❌ 账号被禁用'
    WHEN u.confirmed_at IS NULL
    THEN '❌ 邮箱未确认'
    ELSE '⚠️ 未知问题'
  END as login_status
FROM admin_users au
JOIN auth.users u ON u.id = au.user_id
WHERE au.email = 'YOUR_EMAIL@example.com';  -- ⚠️ 替换为你的实际邮箱

-- ============================================
-- 完整的创建新管理员流程（推荐）
-- ============================================
-- 如果你想从头创建一个新管理员账号，按以下步骤操作：

/*
步骤 1: 在 Supabase Dashboard → Authentication → Users 中创建新用户
- 点击 "Add user" → "Create new user"
- 输入 Email 和 Password
- ✅ 勾选 "Auto Confirm User" (自动确认用户)

步骤 2: 复制新用户的 ID，运行以下 SQL

INSERT INTO admin_users (user_id, email, role, is_active)
VALUES (
  'PASTE_USER_ID_HERE',  -- 从步骤 1 复制的用户 ID
  'your-email@example.com',  -- 你的邮箱
  'super_admin',  -- 角色
  true  -- 激活状态
)
ON CONFLICT (user_id) DO UPDATE
SET
  is_active = true,
  role = 'super_admin',
  updated_at = NOW();

步骤 3: 验证
运行上面的 "验证修复结果" 查询
*/

-- ============================================
-- 角色说明
-- ============================================
/*
super_admin: 超级管理员 - 拥有所有权限
admin: 管理员 - 可以管理内容和用户
editor: 编辑 - 可以编辑内容
viewer: 查看者 - 只能查看（不能登录后台）
*/
