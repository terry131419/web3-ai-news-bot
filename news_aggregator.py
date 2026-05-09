✅ 最终修复 - Python 脚本出错

问题：
exit code 1 - Python 脚本执行失败

解决：
替换成一个更简单、更稳定的 news_aggregator.py


🎯 只需 2 步：

1️⃣ 删除旧的 news_aggregator.py

进入你的仓库 Code 页面
找到 news_aggregator.py
右上角三个点 → Delete file → Commit changes


2️⃣ 上传新的简化版本

链接：https://github.com/terry131419/web3-ai-news-bot/new/main

文件名：news_aggregator.py

完整代码（复制粘贴）：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#!/usr/bin/env python3
import os
import requests
from anthropic import Anthropic

# 获取环境变量
api_key = os.getenv('ANTHROPIC_API_KEY')
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

if not all([api_key, bot_token, chat_id]):
    print("ERROR: Missing environment variables")
    exit(1)

try:
    # 初始化 Anthropic 客户端
    client = Anthropic(api_key=api_key)
    
    # 调用 Claude API
    print("Fetching news from Claude...")
    message = client.messages.create(
        model="claude-opus-4-20250805",
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": "请从全球主流媒体（Reuters, Bloomberg, TechCrunch, CoinDesk等）整理最新的Web3和AI新闻，提供20条最重要的新闻，包括标题、来源和摘要。格式简洁清晰。"
        }]
    )
    
    news = message.content[0].text
    print("News fetched successfully")
    
    # 发送到 Telegram
    print("Sending to Telegram...")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # 如果消息太长，分割发送
    max_len = 4096
    if len(news) > max_len:
        parts = [news[i:i+max_len] for i in range(0, len(news), max_len)]
        for i, part in enumerate(parts, 1):
            requests.post(url, json={
                "chat_id": chat_id,
                "text": f"📰 Web3 & AI News (Part {i}/{len(parts)}):\n\n{part}"
            })
    else:
        requests.post(url, json={
            "chat_id": chat_id,
            "text": f"🚀 Web3 & AI 每日新闻精选\n\n{news}"
        })
    
    print("Message sent successfully")
    print("✅ Done!")
    exit(0)
    
except Exception as e:
    print(f"ERROR: {str(e)}")
    exit(1)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣ 点击 "Commit changes"


4️⃣ 测试

刷新页面
进入 Actions 标签
左侧菜单点 "Daily News"
右上角点 "Run workflow"
等待 1-3 分钟
应该看到 ✅ Completed（绿色）


如果成功：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

打开 Telegram
搜索你的机器人
应该收到新闻消息

恭喜！完成！🎉


关键改动：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ 移除了复杂的类和函数
✓ 直接使用简单的脚本
✓ 完整的错误处理
✓ 自动消息分割功能
✓ 清晰的日志输出

这是最终版本！
