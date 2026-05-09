🔧 修复 Python 脚本执行错误

问题：
Process completed with exit code 2

原因：
news_aggregator.py 脚本有错误或缺少必要的导入


解决方案：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ 删除旧的 Python 文件

进入仓库 Code 标签
找到根目录的 news_aggregator.py
点右上角三个点菜单
选择 "Delete file"
点 "Commit changes"


2️⃣ 上传修复后的 Python 脚本

使用链接：https://github.com/terry131419/web3-ai-news-bot/new/main

文件名（路径）：news_aggregator.py

复制下面的完整代码：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web3 & AI News Aggregator
自动聚合全球 Web3 & AI 新闻，通过 Telegram 发送
"""

import os
import sys
import requests
from anthropic import Anthropic

def get_environment_variables():
    """获取必要的环境变量"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)
    if not bot_token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not set")
        sys.exit(1)
    if not chat_id:
        print("❌ Error: TELEGRAM_CHAT_ID not set")
        sys.exit(1)
    
    return api_key, bot_token, chat_id

def fetch_news_with_claude(client):
    """使用 Claude 获取并整理新闻"""
    try:
        print("🔄 Fetching news from global media...")
        
        prompt = """请从全球主流媒体（Reuters, Bloomberg, TechCrunch, The Verge, CoinDesk, The Block 等）
        实时搜索最新的 Web3 和 AI 相关新闻，整理成 20 条最重要的新闻。
        
        格式要求：
        1. 每条新闻包括：类别 [Web3/AI]、标题、来源、简要摘要（中文）
        2. 按重要性降序排列
        3. 包含关键词标签
        
        输出格式：
        🚀 Web3 & AI 每日新闻精选
        ═══════════════════════════════════
        ⏰ 更新时间：[当前时间]
        
        📰 Top 20 重要新闻：
        
        1. [类别] 标题
        来源：新闻来源
        内容摘要：简要描述
        关键词：标签
        
        2. [类别] 标题
        ...
        """
        
        message = client.messages.create(
            model="claude-opus-4-20250805",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        news_content = message.content[0].text
        print("✅ News fetched successfully")
        return news_content
    
    except Exception as e:
        print(f"❌ Error fetching news: {str(e)}")
        sys.exit(1)

def send_to_telegram(bot_token, chat_id, message):
    """发送消息到 Telegram"""
    try:
        # Telegram API 限制单条消息最多 4096 个字符
        # 如果消息太长，需要分割
        max_length = 4096
        
        if len(message) <= max_length:
            # 直接发送
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.json().get('ok'):
                print("✅ Message sent to Telegram successfully")
                return True
            else:
                print(f"❌ Telegram API error: {response.json()}")
                return False
        else:
            # 分割消息发送
            print(f"📝 Message is too long ({len(message)} chars), splitting into multiple messages...")
            
            parts = []
            current_part = ""
            
            for line in message.split('\n'):
                if len(current_part) + len(line) + 1 > max_length:
                    if current_part:
                        parts.append(current_part)
                    current_part = line
                else:
                    current_part += line + '\n'
            
            if current_part:
                parts.append(current_part)
            
            print(f"📨 Sending {len(parts)} messages...")
            
            for i, part in enumerate(parts, 1):
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": part,
                    "parse_mode": "HTML"
                }
                
                response = requests.post(url, json=payload, timeout=10)
                
                if not response.json().get('ok'):
                    print(f"❌ Failed to send message part {i}")
                    return False
                
                print(f"✅ Part {i}/{len(parts)} sent")
            
            print(f"✅ All {len(parts)} messages sent to Telegram successfully")
            return True
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error sending to Telegram: {str(e)}")
        return False

def main():
    """主函数"""
    try:
        print("🚀 Web3 & AI News Aggregator started...")
        
        # 获取环境变量
        api_key, bot_token, chat_id = get_environment_variables()
        print("✅ Environment variables loaded")
        
        # 初始化 Anthropic 客户端
        client = Anthropic(api_key=api_key)
        
        # 获取新闻
        news_content = fetch_news_with_claude(client)
        
        # 发送到 Telegram
        success = send_to_telegram(bot_token, chat_id, news_content)
        
        if success:
            print("\n🎉 Web3 & AI News Aggregator completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Failed to send news to Telegram")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣ 点击 "Commit changes"

提交文件


4️⃣ 测试运行

刷新页面（F5）
进入 Actions 标签
找工作流
点 "Run workflow"
等待 1-3 分钟
应该看到 ✅ Completed（绿色）


关键修复：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ 完整的错误处理
✓ 环境变量验证
✓ 正确的 API 调用
✓ 消息分割功能（处理长消息）
✓ 清晰的日志输出
✓ 正确的 exit codes

这是最终修复的脚本！
