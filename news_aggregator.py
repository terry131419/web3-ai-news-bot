bash

cat /mnt/user-data/outputs/news_aggregator_GNEWS_FIXED.py
Output

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

def send_to_telegram(bot_token, chat_id, message):
    """发送消息到 Telegram，处理分割"""
    tg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    MAX_LEN = 4090
    
    # 确保 chat_id 是字符串
    chat_id_str = str(chat_id)
    
    # 分割消息
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
    
    # 发送每个部分
    success_count = 0
    for i, part in enumerate(parts, 1):
        try:
            payload = {
                'chat_id': chat_id_str,
                'text': part,
                'parse_mode': 'HTML'
            }
            r = requests.post(tg_url, json=payload, timeout=10)
            result = r.json()
            
            if result.get('ok'):
                print(f"✅ Part {i}/{len(parts)} sent successfully")
                success_count += 1
            else:
                print(f"❌ Part {i} failed: {result.get('description')}")
                print(f"   Chat ID: {chat_id_str}")
                print(f"   Error: {result}")
        except Exception as e:
            print(f"❌ Part {i} error: {e}")
    
    return success_count == len(parts)

def main():
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
    web3_chat_id = os.getenv('TELEGRAM_WEB3_CHAT_ID', '').strip()
    ai_chat_id = os.getenv('TELEGRAM_AI_CHAT_ID', '').strip()
    economy_chat_id = os.getenv('TELEGRAM_ECONOMY_CHAT_ID', '').strip()
    gnews_api_key = os.getenv('GNEWS_API_KEY', '').strip()
    
    if not all([bot_token, web3_chat_id, ai_chat_id, economy_chat_id, gnews_api_key]):
        print("ERROR: Missing required credentials")
        print(f"bot_token: {'✓' if bot_token else '✗'}")
        print(f"web3_chat_id: {'✓' if web3_chat_id else '✗'}")
        print(f"ai_chat_id: {'✓' if ai_chat_id else '✗'}")
        print(f"economy_chat_id: {'✓' if economy_chat_id else '✗'}")
        print(f"gnews_api_key: {'✓' if gnews_api_key else '✗'}")
        return 1
    
    try:
        tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(tz)
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        
        print(f"[START] {date_str} {time_str} UTC+8")
        print(f"Chat IDs: Web3={web3_chat_id}, AI={ai_chat_id}, Economy={economy_chat_id}")
        print("[1/4] Fetching Web3 news from GNews...")
        
        web3_queries = [
            'bitcoin OR ethereum OR blockchain OR crypto OR Web3 OR NFT OR DeFi',
            'cryptocurrency market OR crypto trading OR blockchain technology',
            'Bitcoin OR Ethereum OR altcoin'
        ]
        
        web3_articles = []
        for query in web3_queries:
            web3_articles.extend(get_gnews_news(query, gnews_api_key, 10))
            time.sleep(0.5)
        
        web3_news = deduplicate_articles(web3_articles, limit=10)
        print(f"✓ Fetched {len(web3_news)} Web3 articles")
        
        print("[2/4] Fetching AI news from GNews...")
        
        ai_queries = [
            'artificial intelligence OR AI OR machine learning OR deep learning',
            'ChatGPT OR language model OR neural network OR LLM',
            'AI technology OR AI news OR artificial intelligence'
        ]
        
        ai_articles = []
        for query in ai_queries:
            ai_articles.extend(get_gnews_news(query, gnews_api_key, 10))
            time.sleep(0.5)
        
        ai_news = deduplicate_articles(ai_articles, limit=10)
        print(f"✓ Fetched {len(ai_news)} AI articles")
        
        print("[3/4] Fetching Economy news from GNews...")
        
        economy_queries = [
            'economy OR finance OR stock market OR economic news',
            'war OR conflict OR geopolitics OR international tension',
            'global market OR sanctions OR inflation OR interest rate OR recession'
        ]
        
        economy_articles = []
        for query in economy_queries:
            economy_articles.extend(get_gnews_news(query, gnews_api_key, 10))
            time.sleep(0.5)
        
        economy_news = deduplicate_articles(economy_articles, limit=10)
        print(f"✓ Fetched {len(economy_news)} Economy articles")
        
        print("[4/4] Translating and sending...")
        
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
        
        # 发送 Web3
        web3_msg = f"📱 WEB3 & BLOCKCHAIN NEWS (Top 10)\n📅 {date_str} | ⏰ {time_str} (UTC+8)\n" + "=" * 50 + "\n\n"
        for i, n in enumerate(web3_data, 1):
            web3_msg += f"[{i}] {n['title_en']}\n    {n['title_cn']}\n    Source: {n['source']}\n    Link: {n['url']}\n    摘要: {n['summary_cn']}\n\n"
        
        print("Sending Web3...")
        send_to_telegram(bot_token, web3_chat_id, web3_msg)
        
        # 发送 AI
        ai_msg = f"🤖 AI & TECHNOLOGY NEWS (Top 10)\n📅 {date_str} | ⏰ {time_str} (UTC+8)\n" + "=" * 50 + "\n\n"
        for i, n in enumerate(ai_data, 1):
            ai_msg += f"[{i}] {n['title_en']}\n    {n['title_cn']}\n    Source: {n['source']}\n    Link: {n['url']}\n    摘要: {n['summary_cn']}\n\n"
        
        print("Sending AI...")
        send_to_telegram(bot_token, ai_chat_id, ai_msg)
        
        # 发送经济
        econ_msg = f"💰 GLOBAL ECONOMY & FINANCE NEWS (Top 10)\n📅 {date_str} | ⏰ {time_str} (UTC+8)\n" + "=" * 50 + "\n\n"
        for i, n in enumerate(economy_data, 1):
            econ_msg += f"[{i}] {n['title_en']}\n    {n['title_cn']}\n    Source: {n['source']}\n    Link: {n['url']}\n    摘要: {n['summary_cn']}\n\n"
        
        print("Sending Economy...")
        send_to_telegram(bot_token, economy_chat_id, econ_msg)
        
        print(f"\n✅ SUCCESS! All news sent at {time_str} UTC+8")
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
