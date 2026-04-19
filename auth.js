document.addEventListener('DOMContentLoaded', () => {
    // セッションにパスワードが保存されていれば認証スキップ（タブを切るまで有効）
    if (sessionStorage.getItem('txtHubAuth') === 'true') {
        return;
    }

    // オーバーレイの作成
    const overlay = document.createElement('div');
    overlay.id = 'auth-overlay';
    
    overlay.innerHTML = `
        <div class="auth-container">
            <h1 class="logo" style="font-size: 3rem;">TXT <span>HUB</span></h1>
            <p style="color: var(--text-muted); margin-bottom: 2rem; font-size:0.9rem;">保護された領域です。パスワードを入力してください。</p>
            <div class="auth-input-group">
                <input type="password" id="auth-password" placeholder="Password" autofocus>
                <button id="auth-submit"><i class="fa-solid fa-arrow-right"></i></button>
            </div>
            <p id="auth-error" style="color: #ff003c; margin-top: 1rem; opacity: 0; transition: opacity 0.3s; font-size: 0.85rem;">パスワードが間違っています</p>
        </div>
    `;

    document.body.appendChild(overlay);

    // スクロールを禁止して裏側を完全固定する
    document.body.classList.add('locked');

    const input = document.getElementById('auth-password');
    const submit = document.getElementById('auth-submit');
    const errorMsg = document.getElementById('auth-error');

    const checkPassword = () => {
        if (input.value === '0304') {
            // パスワード正解
            sessionStorage.setItem('txtHubAuth', 'true');
            overlay.style.opacity = '0';
            document.body.classList.remove('locked');
            
            // アニメーション完了後に要素を削除
            setTimeout(() => {
                overlay.remove();
            }, 500);
        } else {
            // パスワード不正解
            errorMsg.style.opacity = '1';
            input.value = '';
            input.focus();
            
            // 少し揺らすアニメーション
            input.parentElement.classList.add('shake');
            setTimeout(() => input.parentElement.classList.remove('shake'), 400);
        }
    };

    submit.addEventListener('click', checkPassword);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            checkPassword();
        }
    });
});
