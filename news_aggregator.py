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

def main():
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '').strip()
    news_api_key = os.getenv('NEWS_API_KEY', '').strip()
    
    if not all([bot_token, chat_id, news_api_key]):
        print("ERROR: Missing credentials")
        return 1
    
    try:
        tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(tz)
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        
        print(f"[START] {date_str} {time_str} UTC+8")
        print("[1/4] Fetching news from NewsAPI...")
        
        web3_url = "https://newsapi.org/v2/everything"
        
        web3_params = {'q': 'bitcoin OR ethereum OR blockchain OR crypto OR Web3', 'sortBy': 'relevancy', 'language': 'en', 'apiKey': news_api_key, 'pageSize': 10}
        web3_response = requests.get(web3_url, params=web3_params, timeout=10)
        web3_news = web3_response.json().get('articles', []) if web3_response.status_code == 200 else []
        
        ai_params = {'q': 'artificial intelligence OR AI OR machine learning OR ChatGPT', 'sortBy': 'relevancy', 'language': 'en', 'apiKey': news_api_key, 'pageSize': 10}
        ai_response = requests.get(web3_url, params=ai_params, timeout=10)
        ai_news = ai_response.json().get('articles', []) if ai_response.status_code == 200 else []
        
        economy_params = {'q': 'economy OR finance OR stock market OR war OR conflict OR geopolitics OR global market OR sanctions OR inflation OR recession OR interest rate', 'sortBy': 'relevancy', 'language': 'en', 'apiKey': news_api_key, 'pageSize': 10}
        economy_response = requests.get(web3_url, params=economy_params, timeout=10)
        economy_news = economy_response.json().get('articles', []) if economy_response.status_code == 200 else []
        
        print(f"OK - Fetched {len(web3_news)} Web3, {len(ai_news)} AI, {len(economy_news)} economy news")
        
        print("[2/4] Translating titles and summaries...")
        
        news_data = {'web3': [], 'ai': [], 'economy': []}
        
        for article in web3_news[:5]:
            print(".", end="", flush=True)
            title_cn = translate_text(article['title'])
            time.sleep(0.2)
            summary = article.get('description', 'N/A')[:150]
            summary_cn = translate_text(summary)
            time.sleep(0.2)
            news_data['web3'].append({
                'title_en': article['title'], 'title_cn': title_cn,
                'source': article['source']['name'], 'url': article['url'],
                'summary_en': summary, 'summary_cn': summary_cn
            })
        
        for article in ai_news[:5]:
            print(".", end="", flush=True)
            title_cn = translate_text(article['title'])
            time.sleep(0.2)
            summary = article.get('description', 'N/A')[:150]
            summary_cn = translate_text(summary)
            time.sleep(0.2)
            news_data['ai'].append({
                'title_en': article['title'], 'title_cn': title_cn,
                'source': article['source']['name'], 'url': article['url'],
                'summary_en': summary, 'summary_cn': summary_cn
            })
        
        for article in economy_news[:5]:
            print(".", end="", flush=True)
            title_cn = translate_text(article['title'])
            time.sleep(0.2)
            summary = article.get('description', 'N/A')[:150]
            summary_cn = translate_text(summary)
            time.sleep(0.2)
            news_data['economy'].append({
                'title_en': article['title'], 'title_cn': title_cn,
                'source': article['source']['name'], 'url': article['url'],
                'summary_en': summary, 'summary_cn': summary_cn
            })
        
        print("\nOK - All translated")
        
        print("[3/4] Formatting news...")
        
        final_news = f"📰 Daily Web3, AI & Global Economy News\n"
        final_news += f"📅 {date_str} | ⏰ {time_str} (UTC+8)\n"
        final_news += "=" * 50 + "\n\n"
        
        final_news += "📱 WEB3 & BLOCKCHAIN NEWS (Top 5)\n\n"
        for i, n in enumerate(news_data['web3'], 1):
            final_news += f"[{i}] {n['title_en']}\n    {n['title_cn']}\n    Source: {n['source']}\n    Link: {n['url']}\n    Summary: {n['summary_en']}\n    摘要: {n['summary_cn']}\n\n"
        
        final_news += "\n🤖 AI & TECHNOLOGY NEWS (Top 5)\n\n"
        for i, n in enumerate(news_data['ai'], 1):
            final_news += f"[{i}] {n['title_en']}\n    {n['title_cn']}\n    Source: {n['source']}\n    Link: {n['url']}\n    Summary: {n['summary_en']}\n    摘要: {n['summary_cn']}\n\n"
        
        final_news += "\n💰 GLOBAL ECONOMY & FINANCE NEWS (Top 5)\n\n"
        for i, n in enumerate(news_data['economy'], 1):
            final_news += f"[{i}] {n['title_en']}\n    {n['title_cn']}\n    Source: {n['source']}\n    Link: {n['url']}\n    Summary: {n['summary_en']}\n    摘要: {n['summary_cn']}\n\n"
        
        print("OK - News formatted")
        print("[4/4] Sending to Telegram...")
        
        tg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        MAX_LENGTH = 4090
        parts = []
        current = ""
        
        for line in final_news.split('\n'):
            if len(current) + len(line) + 1 > MAX_LENGTH:
                if current:
                    parts.append(current)
                current = line
            else:
                current += line + '\n'
        
        if current:
            parts.append(current)
        
        print(f"Sending {len(parts)} message(s)...")
        
        for i, part in enumerate(parts):
            data = {'chat_id': chat_id, 'text': part}
            r = requests.post(tg_url, json=data, timeout=10)
            if r.json().get('ok'):
                print(f"✅ Message {i+1}/{len(parts)} sent")
            else:
                return 1
        
        print(f"\n✅ SUCCESS! News sent at {time_str} UTC+8")
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
