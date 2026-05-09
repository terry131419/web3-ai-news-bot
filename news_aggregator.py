✨ 最终解决方案 - 超级简化版本

Secrets 都配置正确了 ✅
但脚本可能太复杂了

现在上传一个超级简化的版本（只有 30 行代码）


🎯 3 步完成：

1️⃣ 删除旧脚本

Code 页面
找 news_aggregator.py
右上角三个点 → Delete file → Commit changes


2️⃣ 上传新脚本

链接：https://github.com/terry131419/web3-ai-news-bot/new/main

文件名：news_aggregator.py

代码（复制粘贴）：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#!/usr/bin/env python3
import os
import sys

try:
    # 导入库
    import requests
    from anthropic import Anthropic
    
    # 获取环境变量
    api_key = os.getenv('ANTHROPIC_API_KEY')
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    # 调用 API
    client = Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-opus-4-20250805",
        max_tokens=800,
        messages=[{"role": "user", "content": "请列出最近5条重要的Web3和AI新闻"}]
    )
    
    news = message.content[0].text
    
    # 发送到 Telegram
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": f"🚀 Web3 & AI News\n\n{news}"})
    
    print("✅ Success!")
    exit(0)
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    exit(1)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣ 点击 "Commit changes"


4️⃣ 测试

刷新页面
进入 Actions
点击 "Daily News"
右上角点 "Run workflow"
等待 1-3 分钟
应该看到 ✅ Completed


为什么这个版本更好？
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ 只有 30 行代码（之前是 100+ 行）
✓ 没有复杂的函数
✓ 没有多余的处理
✓ 直接做 3 件事：
  1. 调用 Claude API
  2. 获取新闻
  3. 发送到 Telegram

就这么简单！
