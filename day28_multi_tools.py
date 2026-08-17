import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# =============================================
# SimpleAgent 类（升级版：支持多工具并行）
# =============================================
class SimpleAgent:
    def __init__(self, api_key=None, base_url="https://api.deepseek.com", model="deepseek-chat"):
        load_dotenv()
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("❌ 未找到 API Key，请配置 .env 或传入 api_key")

        self.client = OpenAI(api_key=self.api_key, base_url=base_url)
        self.model = model
        self.tools = []
        self.messages = []

    def register_tool(self, name, description, parameters):
        tool_schema = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }
        self.tools.append(tool_schema)
        print(f"✅ 注册工具：{name}")

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

    def call_llm(self, user_input):
        self.add_message("user", user_input)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tools if self.tools else None,
            tool_choice="auto" if self.tools else None
        )

        message = response.choices[0].message
        self.messages.append(message.model_dump())

        if message.tool_calls:
            return {"type": "tool_calls", "data": message.tool_calls}
        else:
            return {"type": "text", "data": message.content}

    def execute_tool(self, tool_call):
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        print(f"🔧 执行工具：{function_name}({arguments})")

        if function_name == "get_weather":
            city = arguments.get("city")
            result = self._get_weather(city)
        elif function_name == "calculator":
            expression = arguments.get("expression")
            result = self._calculator(expression)
        else:
            result = f"未知工具：{function_name}"

        # 每个工具结果独立追加
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(result)
        })

        return result

    # ========== D28 核心升级：run 方法支持多个 tool_calls ==========
    def run(self, user_input):
        result = self.call_llm(user_input)

        if result["type"] == "tool_calls":
            # 👇 关键改动：遍历所有 tool_calls，而不是只取第一个
            tool_results = []
            for tool_call in result["data"]:
                tool_result = self.execute_tool(tool_call)
                tool_results.append(tool_result)
                print(f"📦 工具返回：{tool_result}")

            # 所有工具执行完毕后，统一调用 LLM 生成最终回复
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages
            )
            final_reply = final_response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": final_reply})
            return final_reply
        else:
            return result["data"]

    # ========== 本地工具函数 ==========
    def _get_weather(self, city):
        if city == "北京":
            return "晴，25°C"
        elif city == "上海":
            return "多云，28°C"
        else:
            return f"未知城市：{city}"

    def _calculator(self, expression):
        try:
            allowed = set("0123456789+-*/(). ")
            if not all(c in allowed for c in expression):
                return "表达式包含非法字符"
            result = eval(expression)
            return f"{expression} = {result}"
        except Exception as e:
            return f"计算错误：{e}"

# =============================================
# 测试代码
# =============================================
if __name__ == "__main__":
    agent = SimpleAgent()
    print("🤖 Agent 初始化完成\n")

    # 注册天气工具
    agent.register_tool(
        name="get_weather",
        description="获取指定城市的当前天气信息",
        parameters={
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名称"}
            },
            "required": ["city"]
        }
    )

    # 注册计算器工具
    agent.register_tool(
        name="calculator",
        description="执行数学计算，支持加减乘除",
        parameters={
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "数学表达式，例如 '3+5*2'"}
            },
            "required": ["expression"]
        }
    )

    # ========== D28 测试：一次提问同时触发两个工具 ==========
    user_input = "北京今天天气怎么样？顺便帮我算 3+5*2 等于多少"
    print(f"🧑 用户：{user_input}")
    reply = agent.run(user_input)
    print(f"🤖 Agent：{reply}")