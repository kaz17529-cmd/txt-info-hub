const gridContainer = document.getElementById('info-grid');
const filterBtns = document.querySelectorAll('.filter-btn');

let currentData = [];

// カテゴリーラベルの変換ヘルパー
const getCategoryLabel = (cat) => {
    switch(cat) {
        case 'comeback': return 'Comeback';
        case 'live': return 'Live';
        case 'news': return 'News';
        case 'rumor': return 'Rumor';
        default: return cat;
    }
}

// カードの描画関数
const renderCards = (data) => {
    gridContainer.innerHTML = '';
    
    if (data.length === 0) {
        gridContainer.innerHTML = '<p style="color:var(--text-muted); grid-column: 1 / -1; text-align: center;">データが見つかりませんでした。</p>';
        return;
    }
    
    data.forEach((item, index) => {
        const card = document.createElement('article');
        card.className = 'info-card';
        card.setAttribute('data-category', item.category);
        
        // 少しずつアニメーション遅延をつける
        card.style.animationDelay = `${index * 0.1}s`;

        // HIGH重要度のバッジ
        const importanceBadge = item.importance === 'high' 
            ? `<div class="card-importance">HOT</div>` 
            : '';

        card.innerHTML = `
            ${importanceBadge}
            <div class="card-meta">
                <span class="badge ${item.category}">${getCategoryLabel(item.category)}</span>
                <span class="card-date">${item.date}</span>
            </div>
            <h2 class="card-title">${item.title}</h2>
            <p class="card-desc">${item.desc}</p>
            <a href="${item.url || '#'}" target="_blank" rel="noopener noreferrer" class="read-more-btn">
                記事を読む <i class="fa-solid fa-arrow-up-right-from-square"></i>
            </a>
        `;
        
        gridContainer.appendChild(card);
    });
}

// データ取得と初期描画
const fetchData = async () => {
    try {
        const response = await fetch('data.json');
        if (!response.ok) {
            throw new Error('ネットワークエラーが発生しました');
        }
        currentData = await response.json();
        // 日付が新しい順（降順）にソート
        currentData.sort((a, b) => new Date(b.date) - new Date(a.date));
        renderCards(currentData);
    } catch (error) {
        console.error('データの取得に失敗しました:', error);
        gridContainer.innerHTML = '<p style="color:#ff003c; grid-column: 1 / -1; text-align: center;">データの読み込みに失敗しました。ローカル環境の場合はローカルサーバー（Live Server等）経由で開いてください。</p>';
    }
};

// フィルター機能
filterBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
        // Activeクラスの切り替え
        filterBtns.forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');

        // データのフィルタリング
        const filterValue = e.target.getAttribute('data-filter');
        
        if(filterValue === 'all') {
            renderCards(currentData);
        } else {
            const filteredData = currentData.filter(item => item.category === filterValue);
            renderCards(filteredData);
        }
    });
});

// 初期起動
document.addEventListener('DOMContentLoaded', () => {
    fetchData();
});
