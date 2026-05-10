#!/usr/bin/env python3
import os, sys, io, requests, time

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
        print("[1/4] Fetching news from NewsAPI...")
        
        web3_url = "https://newsapi.org/v2/everything"
        web3_params = {'q': 'bitcoin OR ethereum OR blockchain OR crypto OR Web3', 'sortBy': 'relevancy', 'language': 'en', 'apiKey': news_api_key, 'pageSize': 10}
        web3_response = requests.get(web3_url, params=web3_params, timeout=10)
        web3_news = web3_response.json().get('articles', []) if web3_response.status_code == 200 else []
        
        ai_params = {'q': 'artificial intelligence OR AI OR machine learning OR ChatGPT', 'sortBy': 'relevancy', 'language': 'en', 'apiKey': news_api_key, 'pageSize': 10}
        ai_response = requests.get(web3_url, params=ai_params, timeout=10)
        ai_news = ai_response.json().get('articles', []) if ai_response.status_code == 200 else []
        
        world_params = {'q': 'world news OR breaking news OR international', 'sortBy': 'publishedAt', 'language': 'en', 'apiKey': news_api_key, 'pageSize': 10}
        world_response = requests.get(web3_url, params=world_params, timeout=10)
        world_news = world_response.json().get('articles', []) if world_response.status_code == 200 else []
        
        print(f"OK - Fetched {len(web3_news)} Web3, {len(ai_news)} AI, {len(world_news)} world news")
        
        print("[2/4] Translating titles and summaries...")
        
        news_data = {'web3': [], 'ai': [], 'world': []}
        
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
        
        for article in world_news[:5]:
            print(".", end="", flush=True)
            title_cn = translate_text(article['title'])
            time.sleep(0.2)
            summary = article.get('description', 'N/A')[:150]
            summary_cn = translate_text(summary)
            time.sleep(0.2)
            news_data['world'].append({
                'title_en': article['title'], 'title_cn': title_cn,
                'source': article['source']['name'], 'url': article['url'],
                'summary_en': summary, 'summary_cn': summary_cn
            })
        
        print("\nOK - All translated")
        
        print("[3/4] Formatting news...")
        
        final_news = "📰 Daily Web3, AI & International News\n" + "=" * 50 + "\n\n"
        
        final_news += "📱 WEB3 & BLOCKCHAIN NEWS (Top 5)\n\n"
        for i, n in enumerate(news_data['web3'], 1):
            final_news += f"[{i}] {n['title_en']}\n    {n['title_cn']}\n    Source: {n['source']}\n    Link: {n['url']}\n    Summary: {n['summary_en']}\n    摘要: {n['summary_cn']}\n\n"
        
        final_news += "\n🤖 AI & TECHNOLOGY NEWS (Top 5)\n\n"
        for i, n in enumerate(news_data['ai'], 1):
            final_news += f"[{i}] {n['title_en']}\n    {n['title_cn']}\n    Source: {n['source']}\n    Link: {n['url']}\n    Summary: {n['summary_en']}\n    摘要: {n['summary_cn']}\n\n"
        
        final_news += "\n🌍 INTERNATIONAL NEWS (Top 5)\n\n"
        for i, n in enumerate(news_data['world'], 1):
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
        
        print("\n✅ SUCCESS! Complete bilingual news sent to Telegram!")
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
