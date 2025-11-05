-- ============================================
-- 修复 admin_users 表的 RLS 策略
-- ============================================

-- 🧹 第一步：彻底清理所有 admin_users 表的 RLS 策略
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT policyname FROM pg_policies WHERE tablename = 'admin_users') LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON admin_users', r.policyname);
    END LOOP;
END $$;

-- 验证清理结果（应该返回 0 行）
SELECT policyname FROM pg_policies WHERE tablename = 'admin_users';

-- 🔒 第二步：重新启用 RLS
ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;

-- 🔒 第三步：创建正确的策略

-- 策略 1: 允许已认证用户查看自己的管理员记录
CREATE POLICY "allow_users_view_own_record"
ON admin_users
FOR SELECT
TO authenticated
USING (user_id = auth.uid());

-- 策略 2: 允许活跃管理员查看所有管理员记录
CREATE POLICY "allow_admins_view_all_records"
ON admin_users
FOR SELECT
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM admin_users
    WHERE user_id = auth.uid()
    AND is_active = true
    AND role IN ('super_admin', 'admin')
  )
);

-- 策略 3: 允许超级管理员完全管理所有记录
CREATE POLICY "allow_superadmin_full_access"
ON admin_users
FOR ALL
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM admin_users
    WHERE user_id = auth.uid()
    AND is_active = true
    AND role = 'super_admin'
  )
)
WITH CHECK (
  EXISTS (
    SELECT 1 FROM admin_users
    WHERE user_id = auth.uid()
    AND is_active = true
    AND role = 'super_admin'
  )
);

-- ✅ 验证策略已创建
SELECT
  policyname as policy_name,
  cmd as command_type,
  CASE
    WHEN cmd = 'SELECT' THEN 'Query'
    WHEN cmd = 'ALL' THEN 'All Operations'
    ELSE cmd
  END as description
FROM pg_policies
WHERE tablename = 'admin_users'
ORDER BY policyname;
