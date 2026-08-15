import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. 加载 .env 文件中的密钥
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    print("❌ 未找到 API Key，请检查 .env 文件是否配置了 DEEPSEEK_API_KEY")
    exit(1)

# 2. 初始化客户端
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

# 3. D17 标准任务：发送一句 "Hi"
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "Hi"}
    ]
)

# 4. 打印回复
print("🤖 DeepSeek 说：", response.choices[0].message.content)