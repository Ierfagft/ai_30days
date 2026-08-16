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

# ========== 1. 定义工具 Schema（从 D22 复制过来） ==========
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "获取指定城市的当前天气信息",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，例如：北京、上海"
                }
            },
            "required": ["city"]
        }
    }
}]

# ========== 2. 发送用户消息 + 工具列表 ==========
print("📡 正在向 AI 发送提问，并附上工具描述...\n")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "北京今天天气怎么样？"}
    ],
    tools=tools,  # 👈 关键：把工具说明书发给 AI
    tool_choice="auto"  # 让 AI 自行决定是否调用工具
)

# ========== 3. 解析响应，提取 tool_calls ==========
message = response.choices[0].message

# 检查 AI 是否决定调用工具
if message.tool_calls:
    tool_call = message.tool_calls[0]  # 取第一个工具调用
    function_name = tool_call.function.name
    arguments_str = tool_call.function.arguments  # 这是 JSON 字符串
    
    # 将参数解析为字典
    arguments = json.loads(arguments_str)
    
    # ========== 4. 打印结果（检测标准） ==========
    print(f"🔧 AI 决定调用工具：{function_name}")
    print(f"📦 参数：{arguments}")
    print(f"🏙️  城市：{arguments.get('city')}")
    
    # 断言检测
    assert function_name == "get_weather", "❌ 函数名不是 get_weather！"
    assert "city" in arguments, "❌ 参数中缺少 city！"
    print("\n✅ D23 检测通过！你成功解析了 tool_calls，拿到了函数名和参数。")
else:
    # 如果 AI 没有调用工具（比如问题与工具无关）
    print("ℹ️  AI 未调用任何工具，直接回复了：")
    print(message.content)