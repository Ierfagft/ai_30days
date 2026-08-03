from openai import OpenAI

# 把你的 API Key 直接写在这里（替换 sk-... 为真实 Key）
API_KEY = "sk-e6aed07a8ef84be097863d80cc24aa36"

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)

try:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一名AI Agent架构师，回答需简洁专业。"},
            {"role": "user", "content": "请用一句话解释AI Agent与传统程序的核心区别。"}
        ],
        temperature=0.7,
        max_tokens=100
    )
    reply = response.choices[0].message.content
    print("🤖 Agent回答：", reply)
except Exception as e:
    print("❌ 调用失败：", e)