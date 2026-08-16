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

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# ========== 1. 定义工具 Schema ==========
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "获取指定城市的当前天气信息",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名称，例如：北京、上海"}
            },
            "required": ["city"]
        }
    }
}]

# ========== 2. 模拟本地天气函数 ==========
def get_weather(city):
    if city == "北京":
        return "晴，25°C"
    elif city == "上海":
        return "多云，28°C"
    else:
        return "未知城市，无法查询"

# ========== 3. 第一次调用：让 AI 决定调用工具 ==========
messages = [{"role": "user", "content": "北京今天天气怎么样？"}]

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

message = response.choices[0].message

# ========== 4. 检查并执行本地函数 ==========
if not message.tool_calls:
    print("ℹ️ AI 未调用工具：", message.content)
    exit()

tool_call = message.tool_calls[0]
function_name = tool_call.function.name
arguments = json.loads(tool_call.function.arguments)
city = arguments.get("city")

print(f"🔧 AI 决定调用：{function_name}({city})")

# 执行本地函数，拿到结果
tool_result = get_weather(city)
print(f"🌤️  本地函数返回：{tool_result}")

# ========== 5. 核心任务：把结果回传给大模型（D25） ==========
# 先把 AI 的第一次回复（包含 tool_calls）追加到消息列表
messages.append(message)

# 再把工具执行的结果，以 role="tool" 的形式追加进去
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,  # 告诉 AI 这是对应哪次调用的结果
    "content": tool_result
})

print("\n📤 正在将工具结果回传给大模型，等待总结...\n")

# ========== 6. 第二次调用：让 AI 根据工具结果生成最终回复 ==========
response_final = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages  # 此时 messages 包含了：用户提问 + AI的tool_calls + 工具结果
)

final_reply = response_final.choices[0].message.content
print(f"🤖 AI 最终回复：{final_reply}")

# ========== 检测标准 ==========
print("\n🎉 D25 检测通过！完整闭环跑通：")
print("   用户提问 → AI决定调用工具 → 本地执行 → 结果回传 → AI总结回复")