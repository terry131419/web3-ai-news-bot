#!/usr/bin/env python3
import os, sys, io, requests, time
from datetime import datetime
import pytz

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def translate_text(text, target_lang='zh-CN'):
    try:
        if len(text) > 500:
            text = text[:500]
        url = "https://api.mymemory.translated.net/get"
        params = {'q': text, 'langpair': f'en|{target_lang}'}
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result.get('responseStatus') == 200:
                return result['responseData']['translatedText']
        return text
    except:
        return text

def get_newsapi_news(query, api_key, page_size=20):
    try:
        url = "https://newsapi.org/v2/everything"
        params = {'q': query, 'sortBy': 'relevancy', 'language': 'en', 'apiKey': api_key, 'pageSize': page_size}
        response = requests.get(url, params=params, timeout=10)
        return response.json().get('articles', []) if response.status_code == 200 else []
    except:
        return []

def deduplicate_articles(articles, limit=10):
    seen_titles = set()
    unique = []
    for article in articles:
        title = article.get('title', '').lower().strip()
        if title and title not in seen_titles and article.get('url'):
            seen_titles.add(title)
            unique.append(article)
            if len(unique) >= limit:
                break
    return unique[:limit]

def main():
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
    web3_chat_id = os.getenv('TELEGRAM_WEB3_CHAT_ID', '').strip()
    ai_chat_id = os.getenv('TELEGRAM_AI_CHAT_ID', '').strip()
    economy_chat_id = os.getenv('TELEGRAM_ECONOMY_CHAT_ID', '').strip()
    news_api_key = os.getenv('NEWS_API_KEY', '').strip()
    
    if not all([bot_token, web3_chat_id, ai_chat_id, economy_chat_id, news_api_key]):
        print("ERROR: Missing required credentials")
        print(f"bot_token: {'✓' if bot_token else '✗'}")
        print(f"web3_chat_id: {'✓' if web3_chat_id else '✗'}")
        print(f"ai_chat_id: {'✓' if ai_chat_id else '✗'}")
        print(f"economy_chat_id: {'✓' if economy_chat_id else '✗'}")
        print(f"news_api_key: {'✓' if news_api_key else '✗'}")
        return 1
    
    try:
        tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(tz)
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        
        print(f"[START] {date_str} {time_str} UTC+8")
        
        web3_queries = ['bitcoin OR ethereum OR blockchain OR crypto OR Web3 OR NFT OR DeFi', 'cryptocurrency market', 'Bitcoin OR Ethereum']
        web3_articles = []
        for query in web3_queries:
            web3_articles.extend(get_newsapi_news(query, news_api_key, 10))
            time.sleep(0.5)
        web3_news = deduplicate_articles(web3_articles, limit=10)
        print(f"✓ Fetched {len(web3_news)} Web3 articles")
        
        ai_queries = ['artificial intelligence OR AI OR machine learning', 'ChatGPT OR language model', 'AI technology']
        ai_articles = []
        for query in ai_queries:
            ai_articles.extend(get_newsapi_news(query, news_api_key, 10))
            time.sleep(0.5)
        ai_news = deduplicate_articles(ai_articles, limit=10)
        print(f"✓ Fetched {len(ai_news)} AI articles")
        
        economy_queries = ['economy OR finance OR stock market', 'war OR conflict OR geopolitics', 'global market OR sanctions']
        economy_articles = []
        for query in economy_queries:
            economy_articles.extend(get_newsapi_news(query, news_api_key, 10))
            time.sleep(0.5)
        economy_news = deduplicate_articles(economy_articles, limit=10)
        print(f"✓ Fetched {len(economy_news)} Economy articles")
        
        print("[TRANSLATE] Processing...")
        
        web3_data = []
        for article in web3_news:
            title_cn = translate_text(article['title'])
            time.sleep(0.15)
            summary = article.get('description', 'N/A')[:150]
            summary_cn = translate_text(summary) if summary != 'N/A' else 'N/A'
            time.sleep(0.15)
            web3_data.append({
                'title_en': article['title'], 'title_cn': title_cn,
                'source': article['source']['name'], 'url': article['url'],
                'summary_en': summary, 'summary_cn': summary_cn
            })
        
        ai_data = []
        for article in ai_news:
            title_cn = translate_text(article['title'])
            time.sleep(0.15)
            summary = article.get('description', 'N/A')[:150]
            summary_cn = translate_text(summary) if summary != 'N/A' else 'N/A'
            time.sleep(0.15)
            ai_data.append({
                'title_en': article['title'], 'title_cn': title_cn,
                'source': article['source']['name'], 'url': article['url'],
                'summary_en': summary, 'summary_cn': summary_cn
            })
        
        economy_data = []
        for article in economy_news:
            title_cn = translate_text(article['title'])
            time.sleep(0.15)
            summary = article.get('description', 'N/A')[:150]
            summary_cn = translate_text(summary) if summary != 'N/A' else 'N/A'
            time.sleep(0.15)
            economy_data.append({
                'title_en': article['title'], 'title_cn': title_cn,
                'source': article['source']['name'], 'url': article['url'],
                'summary_en': summary, 'summary_cn': summary_cn
            })
        
        print("[SEND] Sending to Telegram...")
        
        tg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        # Web3
        web3_msg = f"📱 WEB3 & BLOCKCHAIN NEWS (Top 10)\n📅 {date_str} | ⏰ {time_str} (UTC+8)\n" + "=" * 50 + "\n\n"
        for i, n in enumerate(web3_data, 1):
            web3_msg += f"[{i}] {n['title_en']}\n    {n['title_cn']}\n    Source: {n['source']}\n    Link: {n['url']}\n    摘要: {n['summary_cn']}\n\n"
        
        MAX_LEN = 4090
        parts = [web3_msg[i:i+MAX_LEN] for i in range(0, len(web3_msg), MAX_LEN)]
        for part in parts:
            r = requests.post(tg_url, json={'chat_id': web3_chat_id, 'text': part}, timeout=10)
            if r.json().get('ok'):
                print("✅ Web3 sent")
        
        # AI
        ai_msg = f"🤖 AI & TECHNOLOGY NEWS (Top 10)\n📅 {date_str} | ⏰ {time_str} (UTC+8)\n" + "=" * 50 + "\n\n"
        for i, n in enumerate(ai_data, 1):
            ai_msg += f"[{i}] {n['title_en']}\n    {n['title_cn']}\n    Source: {n['source']}\n    Link: {n['url']}\n    摘要: {n['summary_cn']}\n\n"
        
        parts = [ai_msg[i:i+MAX_LEN] for i in range(0, len(ai_msg), MAX_LEN)]
        for part in parts:
            r = requests.post(tg_url, json={'chat_id': ai_chat_id, 'text': part}, timeout=10)
            if r.json().get('ok'):
                print("✅ AI sent")
        
        # Economy
        econ_msg = f"💰 GLOBAL ECONOMY & FINANCE NEWS (Top 10)\n📅 {date_str} | ⏰ {time_str} (UTC+8)\n" + "=" * 50 + "\n\n"
        for i, n in enumerate(economy_data, 1):
            econ_msg += f"[{i}] {n['title_en']}\n    {n['title_cn']}\n    Source: {n['source']}\n    Link: {n['url']}\n    摘要: {n['summary_cn']}\n\n"
        
        parts = [econ_msg[i:i+MAX_LEN] for i in range(0, len(econ_msg), MAX_LEN)]
        for part in parts:
            r = requests.post(tg_url, json={'chat_id': economy_chat_id, 'text': part}, timeout=10)
            if r.json().get('ok'):
                print("✅ Economy sent")
        
        print(f"\n✅ SUCCESS! All news sent at {time_str} UTC+8")
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
