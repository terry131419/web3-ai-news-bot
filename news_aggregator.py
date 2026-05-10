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

def deduplicate_articles(articles, limit=5):
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

def send_to_telegram(bot_token, chat_id, message):
    tg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    MAX_LEN = 4090
    chat_id_str = str(chat_id)
    
    parts = []
    current = ""
    for line in message.split('\n'):
        if len(current) + len(line) + 1 > MAX_LEN:
            if current:
                parts.append(current)
            current = line
        else:
            current += line + '\n'
    if current:
        parts.append(current)
    
    success_count = 0
    for i, part in enumerate(parts, 1):
        try:
            payload = {'chat_id': chat_id_str, 'text': part}
            r = requests.post(tg_url, json=payload, timeout=10)
            result = r.json()
            if result.get('ok'):
                print(f"✅ Part {i}/{len(parts)} sent")
                success_count += 1
            else:
                print(f"❌ Part {i} failed: {result.get('description')}")
        except Exception as e:
            print(f"❌ Part {i} error: {e}")
    return success_count == len(parts)

def main():
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
    web3_chat_id = os.getenv('TELEGRAM_WEB3_CHAT_ID', '').strip()
    ai_chat_id = os.getenv('TELEGRAM_AI_CHAT_ID', '').strip()
    economy_chat_id = os.getenv('TELEGRAM_ECONOMY_CHAT_ID', '').strip()
    news_api_key = os.getenv('NEWS_API_KEY', '').strip()
    
    if not all([bot_token, web3_chat_id, ai_chat_id, economy_chat_id, news_api_key]):
        print("ERROR: Missing credentials")
        return 1
    
    try:
        tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(tz)
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        
        print(f"[START] {date_str} {time_str} UTC+8")
        print("[1/3] Fetching Web3 news...")
        
        web3_articles = get_newsapi_news('bitcoin OR ethereum OR blockchain OR crypto OR Web3', news_api_key, 20)
        web3_news = deduplicate_articles(web3_articles, limit=5)
        print(f"✓ Web3: {len(web3_news)} articles")
        
        print("[2/3] Fetching AI news...")
        ai_articles = get_newsapi_news('artificial intelligence OR AI OR machine learning OR ChatGPT', news_api_key, 20)
        ai_news = deduplicate_articles(ai_articles, limit=5)
        print(f"✓ AI: {len(ai_news)} articles")
        
        print("[3/3] Fetching Economy news...")
        economy_articles = get_newsapi_news('economy OR finance OR stock market OR war OR conflict OR geopolitics', news_api_key, 20)
        economy_news = deduplicate_articles(economy_articles, limit=5)
        print(f"✓ Economy: {len(economy_news)} articles")
        
        print("[4/4] Translating...")
        
        web3_data = []
        for article in web3_news:
            title_cn = translate_text(article['title'])
            time.sleep(0.1)
            summary_cn = translate_text(article.get('description', '')[:150])
            time.sleep(0.1)
            web3_data.append({'title_en': article['title'], 'title_cn': title_cn, 'source': article['source']['name'], 'url': article['url'], 'summary_cn': summary_cn})
        
        ai_data = []
        for article in ai_news:
            title_cn = translate_text(article['title'])
            time.sleep(0.1)
            summary_cn = translate_text(article.get('description', '')[:150])
            time.sleep(0.1)
            ai_data.append({'title_en': article['title'], 'title_cn': title_cn, 'source': article['source']['name'], 'url': article['url'], 'summary_cn': summary_cn})
        
        economy_data = []
        for article in economy_news:
            title_cn = translate_text(article['title'])
            time.sleep(0.1)
            summary_cn = translate_text(article.get('description', '')[:150])
            time.sleep(0.1)
            economy_data.append({'title_en': article['title'], 'title_cn': title_cn, 'source': article['source']['name'], 'url': article['url'], 'summary_cn': summary_cn})
        
        web3_msg = f"📱 WEB3 & BLOCKCHAIN NEWS (Top 5)\n📅 {date_str} | ⏰ {time_str} (UTC+8)\n{'='*50}\n\n"
        for i, n in enumerate(web3_data, 1):
            web3_msg += f"[{i}] {n['title_en']}\n{n['title_cn']}\nSource: {n['source']}\nLink: {n['url']}\n摘要: {n['summary_cn']}\n\n"
        send_to_telegram(bot_token, web3_chat_id, web3_msg)
        
        ai_msg = f"🤖 AI & TECHNOLOGY NEWS (Top 5)\n📅 {date_str} | ⏰ {time_str} (UTC+8)\n{'='*50}\n\n"
        for i, n in enumerate(ai_data, 1):
            ai_msg += f"[{i}] {n['title_en']}\n{n['title_cn']}\nSource: {n['source']}\nLink: {n['url']}\n摘要: {n['summary_cn']}\n\n"
        send_to_telegram(bot_token, ai_chat_id, ai_msg)
        
        econ_msg = f"💰 GLOBAL ECONOMY & FINANCE NEWS (Top 5)\n📅 {date_str} | ⏰ {time_str} (UTC+8)\n{'='*50}\n\n"
        for i, n in enumerate(economy_data, 1):
            econ_msg += f"[{i}] {n['title_en']}\n{n['title_cn']}\nSource: {n['source']}\nLink: {n['url']}\n摘要: {n['summary_cn']}\n\n"
        send_to_telegram(bot_token, economy_chat_id, econ_msg)
        
        print(f"✅ SUCCESS at {time_str} UTC+8")
        return 0
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
