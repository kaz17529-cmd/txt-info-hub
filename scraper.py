import urllib.request
import xml.etree.ElementTree as ET
import json
import datetime
from urllib.parse import quote
import re

def get_official_news():
    results = []
    try:
        url = "https://txt-official.jp/news"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        pattern = r'href=\"(/news/[\w-]+)\".*?text-accentFirst[^>]*>\s*\[\s*([^\]]*?)\s*\].*?text-main[^>]*>([\d\.]+).*?text-font[^>]*>([^<]*?)</p>'
        matches = re.finditer(pattern, html, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            link_path = match.group(1).strip()
            category_raw = match.group(2).strip().replace("&amp;", "&")
            date_str = match.group(3).strip()
            title = match.group(4).strip().replace("&amp;", "&").replace('\n', '').strip()
            
            cat_lower = category_raw.lower()
            if "event" in cat_lower or "live" in cat_lower:
                category = "Live"
                importance = "high"
            elif "release" in cat_lower:
                category = "Comeback"
                importance = "high"
            else:
                category = "News"
                importance = "medium"
                
            formatted_date = date_str.replace('.', '-')
            
            results.append({
                "title": f"【公式】{title}",
                "date": formatted_date,
                "category": category,
                "desc": f"公式カテゴリ: [{category_raw}]",
                "importance": importance,
                "url": f"https://txt-official.jp{link_path}",
                "badge": "OFFICIAL"
            })
    except Exception as e:
        print(f"Error fetching official news: {e}")
        
    return results

def main():
    news_items = []
    
    # 1. 各国のGoogle News RSSからの取得
    locales = [
        # 日本
        {"hl": "ja", "gl": "JP", "ceid": "JP:ja", "query": '"Tomorrow X Together" OR "TOMORROW X TOGETHER" OR TXT OR "トゥモローバイトゥゲザー"'},
        # 韓国
        {"hl": "ko", "gl": "KR", "ceid": "KR:ko", "query": '"Tomorrow X Together" OR "투모로우바이투게더" OR TXT'},
        # グローバル (英語)
        {"hl": "en-US", "gl": "US", "ceid": "US:en", "query": '"Tomorrow X Together" OR TXT OR "Tomorrow by Together"'}
    ]
    
    for loc in locales:
        print(f"Fetching news from {loc['gl']}...")
        query = quote(loc["query"])
        url = f"https://news.google.com/rss/search?q={query}&hl={loc['hl']}&gl={loc['gl']}&ceid={loc['ceid']}"
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                xml_data = response.read()
            
            root = ET.fromstring(xml_data)
            
            # 各言語最大15個程度取得
            for idx, item in enumerate(root.findall('.//item')):
                if idx >= 15:
                    break
                    
                title = item.find('title').text
                pubDate_str = item.find('pubDate').text
                source = item.find('source').text if item.find('source') is not None else ""
                link = item.find('link').text
                
                # 日付パース
                try:
                    pubDate_obj = datetime.datetime.strptime(pubDate_str, "%a, %d %b %Y %H:%M:%S %Z")
                    date_str = pubDate_obj.strftime("%Y-%m-%d")
                except:
                    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
                    
                desc = f"メディア({loc['gl']}): {source}"
                
                category = "News"
                importance = "medium"
                title_lower = title.lower()
                
                # 言語横断のキーワードで判定
                if any(word in title_lower for word in ["カムバック", "comeback", "アルバム", "mv", "リリース", "컴백", "앨범", "뮤직비디오"]):
                    category = "Comeback"
                    importance = "high"
                elif any(word in title_lower for word in ["ライブ", "ツアー", "コンサート", "公演", "ドーム", "live", "tour", "concert", "라이브", "투어", "콘서트", "공연", "콘서트"]):
                    category = "Live"
                elif any(word in title_lower for word in ["噂", "rumor", "話題", "考察", "sns", "루머", "이슈", "비하인드"]):
                    category = "Rumor"
                    importance = "low"
                    
                news_items.append({
                    "title": title,
                    "date": date_str,
                    "category": category,
                    "desc": desc,
                    "importance": importance,
                    "url": link
                })
        except Exception as e:
            print(f"Error fetching data from {loc['gl']}: {e}")

    # 2. 公式サイトからの取得を追加
    print("Fetching news from Official Site...")
    official_items = get_official_news()
    news_items.extend(official_items)
    
    # URLの重複排除
    seen_urls = set()
    unique_news = []
    for item in news_items:
        if item["url"] not in seen_urls:
            seen_urls.add(item["url"])
            unique_news.append(item)
    
    # 日付で降順にソート (新しい順)
    unique_news.sort(key=lambda x: x["date"], reverse=True)
    
    # IDを振り直す
    for idx, item in enumerate(unique_news):
        item["id"] = idx + 1

    # JSONに出力
    output_file = 'data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_news, f, ensure_ascii=False, indent=4)
        
    print(f"Successfully scraped {len(unique_news)} items and updated {output_file}.")

if __name__ == "__main__":
    main()
