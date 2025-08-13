// 简单的管理员登录处理脚本
document.addEventListener('DOMContentLoaded', function() {
    // 获取登录表单元素
    const loginForm = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const loginBtn = document.querySelector('.login-btn');
    
    // 添加回车键提交功能
    passwordInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            handleLogin();
        }
    });
    
    // 如果存在登录按钮，添加点击事件
    if (loginBtn) {
        loginBtn.addEventListener('click', handleLogin);
    }
    
    // 登录处理函数
    window.handleLogin = async function() {
        const username = usernameInput.value;
        const password = passwordInput.value;
        
        if (!username || !password) {
            alert('请输入用户名和密码');
            return;
        }
        
        // 显示加载状态
        if (loginBtn) {
            loginBtn.textContent = '登录中...';
            loginBtn.disabled = true;
        }
        
        try {
            // 本地验证 - 简化登录流程
            if (username === 'admin' && password === 'admin123') {
                // 存储登录信息
                localStorage.setItem('admin_user', JSON.stringify({ 
                    username: username,
                    loginTime: new Date().toISOString(),
                    role: 'admin'
                }));
                
                // 提示登录成功
                alert('登录成功！正在跳转到管理后台...');
                
                // 延迟跳转，确保数据保存
                setTimeout(() => {
                    window.location.href = 'admin-complete-system.html';
                }, 500);
            } else {
                throw new Error('用户名或密码错误');
            }
        } catch (error) {
            alert(error.message || '登录失败，请使用 admin/admin123');
            
            // 恢复按钮状态
            if (loginBtn) {
                loginBtn.textContent = '登录';
                loginBtn.disabled = false;
            }
        }
    };
    
    // 检查是否已登录
    function checkLoginStatus() {
        const adminUser = localStorage.getItem('admin_user');
        if (adminUser) {
            // 已登录，可以直接跳转
            // 但这里不自动跳转，让用户手动登录
            usernameInput.value = 'admin';
            passwordInput.value = 'admin123';
        }
    }
    
    // 页面加载时检查登录状态
    checkLoginStatus();
});