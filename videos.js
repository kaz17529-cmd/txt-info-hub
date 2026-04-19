const videoGrid = document.getElementById('video-grid');

const renderVideos = (videos) => {
    videoGrid.innerHTML = '';
    
    if (videos.length === 0) {
        videoGrid.innerHTML = '<p style="color:var(--text-muted); grid-column: 1 / -1; text-align: center;">動画が見つかりませんでした。</p>';
        return;
    }
    
    videos.forEach((video, index) => {
        const card = document.createElement('a');
        card.href = video.url;
        card.target = '_blank';
        card.rel = 'noopener noreferrer';
        card.className = 'video-card';
        card.style.textDecoration = 'none';
        card.style.color = 'inherit';
        
        // 少しずつアニメーション遅延をつける (最初の20個くらいに絞るか、modを使う)
        const delay = (index % 20) * 0.05;
        card.style.animation = `fadeIn 0.5s ease forwards ${delay}s`;
        card.style.opacity = '0';

        card.innerHTML = `
            <div class="video-thumbnail">
                <img src="${video.thumbnail}" alt="${video.title} thumbnail" loading="lazy">
                <i class="fa-solid fa-circle-play play-icon"></i>
            </div>
            <div class="video-info">
                <h2 class="video-title">${video.title}</h2>
                <div class="video-meta">
                    <span class="channel-name"><i class="fa-solid fa-user"></i> ${video.channel}</span>
                    <span class="published-time">${video.published_time}</span>
                </div>
            </div>
        `;
        
        videoGrid.appendChild(card);
    });
}

const fetchVideos = async () => {
    try {
        const response = await fetch('videos.json');
        if (!response.ok) {
            throw new Error('ネットワークエラー');
        }
        const data = await response.json();
        // 念のため逆順ソートはスクレイパー側で保証されているはずですが、ここではそのまま出力します
        renderVideos(data);
    } catch (error) {
        console.error('動画取得エラー:', error);
        videoGrid.innerHTML = '<p style="color:#ff003c; grid-column: 1 / -1; text-align: center;">データの読み込みに失敗しました。ローカル環境の場合はローカルサーバー（Live Server等）経由で開いてください。</p>';
    }
};

document.addEventListener('DOMContentLoaded', () => {
    fetchVideos();
});
