import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    print("❌ 未找到 API Key，请检查 .env 文件")
    exit(1)

# 初始化客户端
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

# ==================== 核心任务：开启流式输出 ====================
print("🤖 DeepSeek 正在思考（逐字输出）...\n")

# 发送请求，并开启 stream=True
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "请用 100 字以内介绍什么是人工智能，要生动有趣。"}
    ],
    temperature=0.7,
    max_tokens=200,
    stream=True  # 👈 这就是今天的核心开关
)

# 循环接收并打印增量数据块
for chunk in response:
    # 从每个 chunk 中提取增量内容
    content = chunk.choices[0].delta.content
    if content:
        # end="" 表示不换行，flush=True 强制立即输出，实现“逐字”效果
        print(content, end="", flush=True)

# 最后换行，让终端提示符整齐
print("\n\n✅ 流式输出完成！")