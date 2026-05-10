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
        params = {
            'q': query,
            'sortBy': 'relevancy',
            'language': 'en',
            'apiKey': api_key,
            'pageSize': page_size
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get('articles', [])
        return []
    except Exception as e:
        print(f"NewsAPI error: {e}")
        return []

def get_gnews_news(query, api_key, page_size=20):
    try:
        url = "https://gnews.io/api/v4/search"
        params = {
            'q': query,
            'lang': 'en',
            'sortby': 'relevancy',
            'max': page_size,
            'apikey': api_key
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            articles = response.json().get('articles', [])
            converted = []
            for article in articles:
                converted.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'source': {'name': article.get('source', {}).get('name', 'GNews')}
                })
            return converted
        return []
    except Exception as e:
        print(f"GNews error: {e}")
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
    gnews_api_key = os.getenv('GNEWS_API_KEY', '').strip()
    
    if not all([bot_token, web3_chat_id, ai_chat_id, economy_chat_id, news_api_key]):
        print("ERROR: Missing required credentials")
        return 1
    
    try:
        tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(tz)
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        
        print(f"[START] {date_str} {time_str} UTC+8")
        print("[1/5] Fetching Web3 news...")
        
        web3_queries = [
            'bitcoin OR ethereum OR blockchain OR crypto OR Web3 OR NFT OR DeFi',
            'cryptocurrency market OR crypto trading OR blockchain technology',
            'Bitcoin OR Ethereum OR altcoin news'
        ]
        
        web3_articles = []
        for query in web3_queries:
            web3_articles.extend(get_newsapi_news(query, news_api_key, 10))
            time.sleep(0.5)
            if gnews_api_key:
                web3_articles.extend(get_gnews_news(query, gnews_api_key, 5))
                time.sleep(0.5)
        
        web3_news = deduplicate_articles(web3_articles, limit=10)
        print(f"✓ Fetched {len(web3_news)} Web3 articles")
        
        print("[2/5] Fetching AI news...")
        
        ai_queries = [
            'artificial intelligence OR AI OR machine learning OR deep learning',
            'ChatGPT OR language model OR neural network OR LLM',
            'AI technology OR AI news OR artificial intelligence breakthrough'
        ]
        
        ai_articles = []
        for query in ai_queries:
            ai_articles.extend(get_newsapi_news(query, news_api_key, 10))
            time.sleep(0.5)
            if gnews_api_key:
                ai_articles.extend(get_gnews_news(query, gnews_api_key, 5))
                time.sleep(0.5)
        
        ai_news = deduplicate_articles(ai_articles, limit=10)
        print(f"✓ Fetched {len(ai_news)} AI articles")
        
        print("[3/5] Fetching Economy news...")
        
        economy_queries = [
            'economy OR finance OR stock market OR economic news',
            'war OR conflict OR geopolitics OR international tension',
            'global market OR sanctions OR inflation OR interest rate OR recession'
        ]
        
        economy_articles = []
        for query in economy_queries:
            economy_articles.extend(get_newsapi_news(query, news_api_key, 10))
            time.sleep(0.5)
            if gnews_api_key:
                economy_articles.extend(get_gnews_news(query, gnews_api_key, 5))
                time.sleep(0.5)
        
        economy_news = deduplicate_articles(economy_articles, limit=10)
        print(f"✓ Fetched {len(economy_news)} Economy articles")
        
        print("[4/5] Translating...")
        
        # 翻译代码（省略，与之前相同）
        web3_data = []
        for article in web3_news:
            print(".", end="", flush=True)
            title_cn = translate_text(article['title'])
            time.sleep(0.15)
            summary = article.get('description', 'N/A')[:150]
            summary_cn = translate_text(summary) if summary != 'N/A' else 'N/A'
            time.sleep(0.15)
            web3_data.append({
                'title_en': article['title'],
                'title_cn': title_cn,
                'source': article['source']['name'],
                'url': article['url'],
                'summary_en': summary,
                'summary_cn': summary_cn
            })
        
        # AI 和经济的翻译代码相同...
        ai_data = []
        for article in ai_news:
            print(".", end="", flush=True)
            title_cn = translate_text(article['title'])
            time.sleep(0.15)
            summary = article.get('description', 'N/A')[:150]
            summary_cn = translate_text(summary) if summary != 'N/A' else 'N/A'
            time.sleep(0.15)
            ai_data.append({
                'title_en': article['title'],
                'title_cn': title_cn,
                'source': article['source']['name'],
                'url': article['url'],
                'summary_en': summary,
                'summary_cn': summary_cn
            })
        
        economy_data = []
        for article in economy_news:
            print(".", end="", flush=True)
            title_cn = translate_text(article['title'])
            time.sleep(0.15)
            summary = article.get('description', 'N/A')[:150]
            summary_cn = translate_text(summary) if summary != 'N/A' else 'N/A'
            time.sleep(0.15)
            economy_data.append({
                'title_en': article['title'],
                'title_cn': title_cn,
                'source': article['source']['name'],
                'url': article['url'],
                'summary_en': summary,
                'summary_cn': summary_cn
            })
        
        print("\n✓ All translated")
        print("[5/5] Sending to channels...")
        
        tg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        # 发送逻辑（分别发送到 3 个频道）
        # Web3
        web3_message = f"📱 WEB3 & BLOCKCHAIN NEWS (Top 10)\n📅 {date_str} | ⏰ {time_str} (UTC+8)\n" + "=" * 50 + "\n\n"
        for i, n in enumerate(web3_data, 1):
            web3_message += f"[{i}] {n['title_en']}\n    {n['title_cn']}\n    Source: {n['source']}\n    Link: {n['url']}\n    摘要: {n['summary_cn']}\n\n"
        
        MAX_LENGTH = 4090
        web3_parts = []
        current = ""
        for line in web3_message.split('\n'):
            if len(current) + len(line) + 1 > MAX_LENGTH:
                if current:
                    web3_parts.append(current)
                current = line
            else:
                current += line + '\n'
        if current:
            web3_parts.append(current)
        
        for i, part in enumerate(web3_parts):
            data = {'chat_id': web3_chat_id, 'text': part}
            r = requests.post(tg_url, json=data, timeout=10)
            if r.json().get('ok'):
                print(f"✅ Web3 {i+1}/{len(web3_parts)} sent")
        
        # AI（代码相同，改 ai_chat_id）
        ai_message = f"🤖 AI & TECHNOLOGY NEWS (Top 10)\n📅 {date_str} | ⏰ {time_str} (UTC+8)\n" + "=" * 50 + "\n\n"
        for i, n in enumerate(ai_data, 1):
            ai_message += f"[{i}] {n['title_en']}\n    {n['title_cn']}\n    Source: {n['source']}\n    Link: {n['url']}\n    摘要: {n['summary_cn']}\n\n"
        
        ai_parts = []
        current = ""
        for line in ai_message.split('\n'):
            if len(current) + len(line) + 1 > MAX_LENGTH:
                if current:
                    ai_parts.append(current)
                current = line
            else:
                current += line + '\n'
        if current:
            ai_parts.append(current)
        
        for i, part in enumerate(ai_parts):
            data = {'chat_id': ai_chat_id, 'text': part}
            r = requests.post(tg_url, json=data, timeout=10)
            if r.json().get('ok'):
                print(f"✅ AI {i+1}/{len(ai_parts)} sent")
        
        # Economy（代码相同，改 economy_chat_id）
        economy_message = f"💰 GLOBAL ECONOMY & FINANCE NEWS (Top 10)\n📅 {date_str} | ⏰ {time_str} (UTC+8)\n" + "=" * 50 + "\n\n"
        for i, n in enumerate(economy_data, 1):
            economy_message += f"[{i}] {n['title_en']}\n    {n['title_cn']}\n    Source: {n['source']}\n    Link: {n['url']}\n    摘要: {n['summary_cn']}\n\n"
        
        economy_parts = []
        current = ""
        for line in economy_message.split('\n'):
            if len(current) + len(line) + 1 > MAX_LENGTH:
                if current:
                    economy_parts.append(current)
                current = line
            else:
                current += line + '\n'
        if current:
            economy_parts.append(current)
        
        for i, part in enumerate(economy_parts):
            data = {'chat_id': economy_chat_id, 'text': part}
            r = requests.post(tg_url, json=data, timeout=10)
            if r.json().get('ok'):
                print(f"✅ Economy {i+1}/{len(economy_parts)} sent")
        
        print(f"\n✅ SUCCESS! All news sent at {time_str} UTC+8")
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
