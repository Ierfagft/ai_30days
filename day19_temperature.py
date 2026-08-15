import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    print("❌ 未找到 API Key")
    exit(1)

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# ==================== 同一个问题 ====================
question = "1 + 1 等于几？请用一句话回答。"

# ==================== 实验 1：低温（极度确定） ====================
print("\n🧊 实验 1：Temperature = 0（极度确定，几乎每次都一样）")
response_low = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": question}],
    temperature=0.0,  # 最低温度，追求确定性
    max_tokens=50
)
print("🤖 低温回答：", response_low.choices[0].message.content)

# ==================== 实验 2：高温（极度发散） ====================
print("\n🔥 实验 2：Temperature = 1.2（高度随机，每次都不一样）")
response_high = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": question}],
    temperature=1.2,  # 最高建议值，追求创造性
    max_tokens=50
)
print("🤖 高温回答：", response_high.choices[0].message.content)

# ==================== 检测结论 ====================
print("\n" + "="*40)
print("🎯 D19 检测标准：肉眼可见两次回复的确定性/发散性明显不同。")
print("如果两个回答风格差异很大，说明 Temperature 参数生效了！")