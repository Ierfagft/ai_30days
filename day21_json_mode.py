import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    print("❌ 未找到 API Key")
    exit(1)

# 初始化客户端
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

# ==================== D21 核心任务：JSON 模式 ====================
print("📡 正在请求 AI 返回 JSON 数据...\n")

# 注意：使用 JSON 模式时，通常建议关闭流式（stream=False）以获得完整 JSON
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个数据提取助手。请只返回 JSON 格式的数据，不要包含其他文字。"},
        {"role": "user", "content": "请提取这句话中的城市名：'我最喜欢上海和北京，但更喜欢北京。' 以 JSON 格式返回，key 为 'city'。"}
    ],
    temperature=0.3,  # 低温提高准确性
    response_format={"type": "json_object"}  # 👈 今天的核心参数！
)

# 1. 拿到返回的字符串
content = response.choices[0].message.content
print(f"📄 原始返回字符串：\n{content}\n")

# 2. 解析为 Python 字典（检测标准）
try:
    data = json.loads(content)  # 将 JSON 字符串转为字典
    print(f"✅ 解析成功！类型：{type(data)}")
    print(f"🏙️  提取到的城市：{data.get('city', '未找到 city 键')}")
    
    # 3. 断言检测
    assert isinstance(data, dict), "❌ 返回的不是字典！"
    assert "city" in data, "❌ 字典中没有 'city' 键！"
    print("\n🎉 D21 检测通过！你成功让 AI 返回了可解析的 JSON 数据！")
    
except json.JSONDecodeError as e:
    print(f"❌ JSON 解析失败：{e}")
    print("提示：请检查 AI 是否返回了纯 JSON（没有 Markdown 代码块包裹）。")