import urllib.request
import re
import json
import urllib.parse
import sys

def get_youtube_results(query, max_results=100):
    # sp=CAI%253D はYouTube検索の「アップロード日順（新着順）」のパラメータ
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}&sp=CAI%253D"
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    )
    
    videos = []
    print(f"Fetching YouTube search results for: {query}")
    try:
        response = urllib.request.urlopen(req)
        html = response.read().decode('utf-8')
        
        # HTML内に埋め込まれた ytInitialData を抽出する
        match = re.search(r'var ytInitialData = (.*?);</script>', html)
        if not match:
            print("Could not find ytInitialData. Possible YouTube layout change or anti-bot challenge.")
            return videos
            
        data = json.loads(match.group(1))
        
        # 検索結果のJSONツリーを辿る
        # 変更に弱い箇所ですが、APIキーなしで取得するためのハックです
        contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [])
        
        for section in contents:
            item_section = section.get('itemSectionRenderer', {}).get('contents', [])
            for item in item_section:
                video_renderer = item.get('videoRenderer')
                if video_renderer:
                    vid_id = video_renderer.get('videoId')
                    title_runs = video_renderer.get('title', {}).get('runs', [{}])
                    title = title_runs[0].get('text', '') if title_runs else ''
                    
                    channel_runs = video_renderer.get('ownerText', {}).get('runs', [{}])
                    channel = channel_runs[0].get('text', '') if channel_runs else ''
                    
                    published = video_renderer.get('publishedTimeText', {}).get('simpleText', '')
                    
                    if vid_id and title:
                        videos.append({
                            'id': vid_id,
                            'title': title,
                            'channel': channel,
                            'published_time': published,
                            'url': f"https://www.youtube.com/watch?v={vid_id}",
                            'thumbnail': f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg"
                        })
                        
                if len(videos) >= max_results:
                    return videos
                    
    except Exception as e:
        print(f"Error fetching YouTube: {e}")
        
    return videos

if __name__ == "__main__":
    search_keywords = "TXT OR Tomorrow X Together OR トゥモローバイトゥゲザー"
    # 動画を最大100件取得
    videos = get_youtube_results(search_keywords, 100)
    
    with open("videos.json", "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=4)
        
    print(f"Scraped {len(videos)} videos and saved to videos.json.")
