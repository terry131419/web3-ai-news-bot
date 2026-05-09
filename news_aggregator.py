#!/usr/bin/env python3
"""
完整诊断版本 - 显示每一步的详细信息
"""
import os
import sys
 
print("=" * 60)
print("🔍 开始诊断...")
print("=" * 60)
 
# 1. 检查环境变量
print("\n1️⃣ 检查环境变量...")
api_key = os.getenv('ANTHROPIC_API_KEY')
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')
 
print(f"   ANTHROPIC_API_KEY: {'✅ 存在' if api_key else '❌ 缺失'}")
print(f"   TELEGRAM_BOT_TOKEN: {'✅ 存在' if bot_token else '❌ 缺失'}")
print(f"   TELEGRAM_CHAT_ID: {'✅ 存在' if chat_id else '❌ 缺失'}")
 
if not all([api_key, bot_token, chat_id]):
    print("\n❌ 错误：Secrets 没有配置！")
    print("\n请检查 GitHub Secrets:")
    print("Settings → Secrets and variables → Actions")
    print("\n需要配置这 3 个：")
    print("1. ANTHROPIC_API_KEY")
    print("2. TELEGRAM_BOT_TOKEN")
    print("3. TELEGRAM_CHAT_ID")
    sys.exit(1)
 
# 2. 检查导入
print("\n2️⃣ 检查依赖...")
try:
    import requests
    print("   ✅ requests 导入成功")
except ImportError as e:
    print(f"   ❌ requests 导入失败: {e}")
    sys.exit(1)
 
try:
    from anthropic import Anthropic
    print("   ✅ Anthropic 导入成功")
except ImportError as e:
    print(f"   ❌ Anthropic 导入失败: {e}")
    print("   请确保执行了: pip install anthropic requests")
    sys.exit(1)
 
# 3. 连接 Claude
print("\n3️⃣ 连接 Claude API...")
try:
    client = Anthropic(api_key=api_key)
    print("   ✅ Anthropic 客户端初始化成功")
except Exception as e:
    print(f"   ❌ 初始化失败: {e}")
    sys.exit(1)
 
# 4. 调用 API
print("\n4️⃣ 调用 Claude API...")
try:
    print("   正在发送请求...")
    message = client.messages.create(
        model="claude-opus-4-20250805",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": "列出5条最新的Web3新闻标题即可。格式简洁。"
        }]
    )
    print("   ✅ API 调用成功")
    news = message.content[0].text
    print(f"   获取的新闻长度: {len(news)} 字符")
except Exception as e:
    print(f"   ❌ API 调用失败: {e}")
    print("   可能的原因：")
    print("   1. API Key 无效或过期")
    print("   2. API 配额不足")
    print("   3. 网络问题")
    sys.exit(1)
 
# 5. 发送 Telegram
print("\n5️⃣ 发送到 Telegram...")
try:
    print("   正在连接 Telegram API...")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # 测试消息
    test_message = f"✅ 系统测试成功！\n\n获取到的新闻预览:\n{news[:200]}..."
    
    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": test_message
        },
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('ok'):
            print("   ✅ Telegram 消息发送成功！")
        else:
            print(f"   ❌ Telegram API 返回错误: {result.get('description')}")
            print("   可能的原因：")
            print("   1. Chat ID 无效")
            print("   2. Bot Token 无效")
            print("   3. 机器人没有权限")
            sys.exit(1)
    else:
        print(f"   ❌ HTTP 错误 {response.status_code}")
        print(f"   响应: {response.text}")
        sys.exit(1)
        
except requests.exceptions.RequestException as e:
    print(f"   ❌ 网络错误: {e}")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ 发送失败: {e}")
    sys.exit(1)
 
# 完成
print("\n" + "=" * 60)
print("✅ 所有检查通过！系统工作正常！")
print("=" * 60)
print("\n现在应该在 Telegram 中收到测试消息了")
sys.exit(0)
