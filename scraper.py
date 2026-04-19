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
    # 1. Google News RSSからの取得
    query = quote('"Tomorrow X Together" OR "TOMORROW X TOGETHER" OR TXT OR "トゥモローバイトゥゲザー"')
    url = f"https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"
    
    print(f"Fetching news from Google News RSS...")
    news_items = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
        
        root = ET.fromstring(xml_data)
        
        # ニュースアイテムの解析 (最大10個)
        for idx, item in enumerate(root.findall('.//item')):
            if idx >= 10:
                break
                
            title = item.find('title').text
            pubDate_str = item.find('pubDate').text
            source = item.find('source').text if item.find('source') is not None else ""
            link = item.find('link').text
            
            # 日付文字列のパース (例: Thu, 19 Apr 2026 12:00:00 GMT)
            try:
                pubDate_obj = datetime.datetime.strptime(pubDate_str, "%a, %d %b %Y %H:%M:%S %Z")
                date_str = pubDate_obj.strftime("%Y-%m-%d")
            except:
                date_str = datetime.datetime.now().strftime("%Y-%m-%d")
                
            desc = f"メディア: {source}"
            
            # カテゴリと重要度の判定
            category = "News"
            importance = "medium"
            
            title_lower = title.lower()
            if any(word in title_lower for word in ["カムバック", "comeback", "アルバム", "mv", "リリース"]):
                category = "Comeback"
                importance = "high"
            elif any(word in title_lower for word in ["ライブ", "ツアー", "コンサート", "公演", "ライブ", "ドーム"]):
                category = "Live"
            elif any(word in title_lower for word in ["噂", "rumor", "話題", "考察", "sns"]):
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
        print(f"Error fetching data: {e}")

    # 2. 公式サイトからの取得を追加
    print("Fetching news from Official Site...")
    official_items = get_official_news()
    news_items.extend(official_items)
    
    # 日付で降順にソート (新しい順)
    news_items.sort(key=lambda x: x["date"], reverse=True)
    
    # IDを振り直す
    for idx, item in enumerate(news_items):
        item["id"] = idx + 1

    # JSONファイルに出力
    output_file = 'data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(news_items, f, ensure_ascii=False, indent=4)
        
    print(f"Successfully scraped {len(news_items)} items and updated {output_file}.")

if __name__ == "__main__":
    main()
