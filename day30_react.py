import os
import json
import math
from openai import OpenAI
from dotenv import load_dotenv

# =============================================
# D30：纯手写 ReAct Agent
# =============================================

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# ========== 1. 定义工具 ==========

# 工具 1：天气
def get_weather(city):
    if city == "北京":
        return "晴，25°C"
    elif city == "上海":
        return "多云，28°C"
    else:
        return f"未知城市：{city}"

# 工具 2：开平方
def sqrt_tool(x):
    try:
        return math.sqrt(x)
    except ValueError:
        return "数值错误：不能对负数开平方"

# 工具 2：简单计算（对应开平方）
def calculator(expression):
    try:
        allowed = set("0123456789+-*/(). ")
        if not all(c in allowed for c in expression):
            return "表达式包含非法字符"
        return eval(expression)
    except Exception as e:
        return f"计算错误：{e}"

# ========== 2. 工具描述（Schema） ==========

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称，如：北京、上海"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "执行数学计算",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式，如 'sqrt(100)' 表示开平方"}
                },
                "required": ["expression"]
            }
        }
    }
]

# ========== 3. 本地工具映射 ==========
tool_map = {
    "get_weather": get_weather,
    "calculator": calculator
}

# ========== 4. ReAct 循环 ==========

def run_react(user_question):
    messages = [
        {"role": "system", "content": "你是一个智能助手，能根据用户问题调用工具。请逐步思考并执行。"},
        {"role": "user", "content": user_question}
    ]

    max_iterations = 5
    iteration = 0
    final_answer = None

    while iteration < max_iterations:
        iteration += 1
        print(f"\n🧠 第 {iteration} 轮思考...")

        # 调用 LLM
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        msg = response.choices[0].message
        messages.append(msg.model_dump())  # 记录 AI 的回复

        # 如果 AI 想调用工具
        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                print(f"🔧 调用工具：{func_name}，参数：{args}")

                # 执行对应的本地函数
                if func_name in tool_map:
                    result = tool_map[func_name](**args)
                    print(f"📦 工具返回：{result}")
                else:
                    result = f"未知工具：{func_name}"

                # 把工具结果回传给模型
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
        else:
            # 没有工具调用，说明最终答案已生成
            final_answer = msg.content
            break

    if final_answer is None:
        final_answer = "达到最大迭代次数，未能生成最终答案。"

    return final_answer

# =============================================
# 测试
# =============================================
if __name__ == "__main__":
    print("🚀 D30 ReAct Agent 启动\n")

    # 第 1 个测试：天气 + 开平方
    question_1 = "北京今天天气怎么样？顺便帮我算 100 的平方根是多少。"
    print(f"🧑 用户：{question_1}")
    answer_1 = run_react(question_1)
    print(f"\n🤖 最终回答：{answer_1}")

    print("\n" + "=" * 60)

    # 第 2 个测试：单工具
    question_2 = "上海天气怎么样？"
    print(f"\n🧑 用户：{question_2}")
    answer_2 = run_react(question_2)
    print(f"\n🤖 最终回答：{answer_2}")