import os
from openai import OpenAI
from dotenv import load_dotenv

# ========== 1. 加载环境变量 ==========
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("❌ 未找到 DEEPSEEK_API_KEY，请检查 .env 文件")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# ========== 2. 初始化对话历史（这就是记忆） ==========
messages = [
    {"role": "system", "content": "你是一个友好的助手，会记住用户之前说过的话。"}
]

def ask(question):
    """发送问题并更新记忆"""
    # 把用户的问题加入历史
    messages.append({"role": "user", "content": question})

    # 调用大模型
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,  # 把整个历史发过去
        temperature=0.7,
        max_tokens=200
    )

    # 提取回复
    reply = response.choices[0].message.content

    # 把助手的回复也加入历史（关键！）
    messages.append({"role": "assistant", "content": reply})

    return reply

# ========== 3. 测试记忆 ==========
print("🤖 启动带记忆的对话...\n")

# 第一轮：告诉模型名字
q1 = "我叫小王"
print(f"🧑 用户：{q1}")
a1 = ask(q1)
print(f"🤖 助手：{a1}\n")

# 第二轮：问模型自己叫什么（检测是否记住）
q2 = "我叫什么名字？"
print(f"🧑 用户：{q2}")
a2 = ask(q2)
print(f"🤖 助手：{a2}\n")

# ========== 4. 检测 ==========
# 如果回答里包含"小王"或"王"，就认为记住了
if "小王" in a2 or "王" in a2:
    print("✅ D38 检测通过！模型记住了用户的名字。")
else:
    print("⚠️ 模型似乎没记住名字，请检查对话历史是否正确追加。")

print("\n📝 完整对话历史：")
for msg in messages:
    print(f"{msg['role']}: {msg['content'][:80]}...")