import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. 加载 .env 文件中的密钥
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    print("❌ 未找到 API Key，请检查 .env 文件")
    exit(1)

# 2. 初始化客户端
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

# 3. D18 核心任务：System 设定 + User 提问
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是李白，中国唐代著名的浪漫主义诗人，被后人誉为'诗仙'。请用豪放不羁、富有诗意的语气回答所有问题。"},
        {"role": "user", "content": "你是谁？"}
    ]
)

# 4. 打印回复
print("🤖 李白（DeepSeek）说：", response.choices[0].message.content)