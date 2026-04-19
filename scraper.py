import urllib.request
import xml.etree.ElementTree as ET
import json
import datetime
from urllib.parse import quote

def main():
    # Google News RSS Search Query for TXT
    # "Tomorrow X Together", "TXT", およびカタカナ名を含める
    query = quote('"Tomorrow X Together" OR "TOMORROW X TOGETHER" OR TXT OR "トゥモローバイトゥゲザー"')
    url = f"https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"
    
    print(f"Fetching news from Google News RSS...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    root = ET.fromstring(xml_data)
    news_items = []
    
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
            
        desc = f"提供元: {source}"
        
        # カテゴリと重要度の判定
        category = "news"
        importance = "medium"
        
        title_lower = title.lower()
        if any(word in title_lower for word in ["カムバック", "comeback", "アルバム", "mv", "リリース"]):
            category = "comeback"
            importance = "high"
        elif any(word in title_lower for word in ["ライブ", "ツアー", "コンサート", "公演", "ライブ", "ドーム"]):
            category = "live"
        elif any(word in title_lower for word in ["噂", "rumor", "話題", "考察", "sns"]):
            category = "rumor"
            importance = "low"
            
        news_items.append({
            "id": idx + 1,
            "title": title,
            "date": date_str,
            "category": category,
            "desc": desc,
            "importance": importance,
            "url": link
        })

    # JSONファイルに出力
    output_file = 'data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(news_items, f, ensure_ascii=False, indent=4)
        
    print(f"Successfully scraped {len(news_items)} items and updated {output_file}.")

if __name__ == "__main__":
    main()
