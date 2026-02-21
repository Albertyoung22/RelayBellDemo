/* auth.js - 為雲端展示模式強行解除登入檢查 */

(function() {
    console.log("[AUTH] 已啟動展示廳專用免登入模式");
    
    // 1. 強行在本地端設置一個虛假的登入 ID
    localStorage.setItem('X_TOKEN', 'demo-mode-unlocked');

    // 2. 劫持原本的 token 檢查邏輯
    window.getToken = function() { return 'demo-mode-unlocked'; };

    // 3. 停用 logout 登出功能，避免誤點
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.onclick = function() { 
            alert("展示模式下已停用登出功能");
        };
        logoutBtn.style.opacity = "0.5";
    }

    // 4. 重寫 checkAuth (如果有的話)，讓它永遠回傳成功
    window.checkAuth = async function() { return true; };

    console.log("[AUTH] 解鎖成功：index.html 現在可以自由存取");
})();
