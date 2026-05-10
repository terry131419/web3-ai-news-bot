#!/usr/bin/env python3
"""
Web3 & AI News Aggregator - 改进版本
更稳定，更好的错误处理
"""
import os
import sys
import json

def main():
    # 1. 获取配置
    api_key = os.getenv('ANTHROPIC_API_KEY', '').strip()
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '').strip()
    
    # 验证配置
    if not all([api_key, bot_token, chat_id]):
        print("ERROR: Missing environment variables")
        print(f"ANTHROPIC_API_KEY: {'✓' if api_key else '✗'}")
        print(f"TELEGRAM_BOT_TOKEN: {'✓' if bot_token else '✗'}")
        print(f"TELEGRAM_CHAT_ID: {'✓' if chat_id else '✗'}")
        return 1
    
    try:
        # 2. 导入库（分开导入，便于定位问题）
        print("[1/4] 导入依赖...")
        import requests
        print("      ✓ requests 已加载")
        
        from anthropic import Anthropic
        print("      ✓ anthropic 已加载")
        
        # 3. 调用 Claude API
        print("[2/4] 调用 Claude API...")
        client = Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model="claude-opus-4-20250805",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": "请简要列出最近最重要的5条Web3和AI新闻，每条一行，包括标题和来源"
            }]
        )
        
        news = response.content[0].text
        print(f"      ✓ 获取新闻成功 ({len(news)} 字符)")
        
        # 4. 发送到 Telegram
        print("[3/4] 发送到 Telegram...")
        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        # 准备消息
        message_text = f"🚀 Web3 & AI 新闻\n\n{news}"
        
        # 发送请求
        response = requests.post(
            telegram_url,
            json={
                "chat_id": chat_id,
                "text": message_text,
                "parse_mode": "HTML"
            },
            timeout=10
        )
        
        result = response.json()
        
        if result.get('ok'):
            print("      ✓ Telegram 消息发送成功")
        else:
            error = result.get('description', '未知错误')
            print(f"      ✗ Telegram API 错误: {error}")
            return 1
        
        # 5. 完成
        print("[4/4] 完成")
        print("\n✅ 所有步骤都成功了！")
        return 0
        
    except ImportError as e:
        print(f"ERROR: 导入失败 - {str(e)}")
        print("解决方案: 检查 workflow 的 pip install 步骤")
        return 1
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
