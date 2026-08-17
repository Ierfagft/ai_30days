import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# =============================================
# SimpleAgent 类：封装了 LLM 调用 + 工具执行
# =============================================
class SimpleAgent:
    def __init__(self, api_key=None, base_url="https://api.deepseek.com", model="deepseek-chat"):
        """
        初始化 Agent。
        如果不传 api_key，则从 .env 中读取 DEEPSEEK_API_KEY。
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("❌ 未找到 API Key，请配置 .env 或传入 api_key")

        self.client = OpenAI(api_key=self.api_key, base_url=base_url)
        self.model = model
        self.tools = []  # 后续可以通过 register_tool 添加工具
        self.messages = []  # 对话历史

    def register_tool(self, name, description, parameters):
        """
        注册工具（把工具说明书加到 self.tools 列表中）
        """
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
        """
        添加一条消息到对话历史
        """
        self.messages.append({"role": role, "content": content})

    def call_llm(self, user_input, stream=False):
        """
        核心方法：调用大模型，支持工具调用
        返回：AI 的回复内容（或 tool_calls）
        """
        # 先把用户输入加入消息列表
        self.add_message("user", user_input)

        # 调用 API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tools if self.tools else None,  # 如果有注册工具才传
            tool_choice="auto" if self.tools else None
        )

        message = response.choices[0].message

        # 如果是流式输出，这里暂不处理（保持简洁）
        # 实际项目中可以扩展

        # 把 AI 的回复加入消息列表（如果是 tool_calls，也一并保留）
        self.messages.append(message.model_dump())

        # 如果 AI 决定调用工具，返回 tool_calls；否则返回文字内容
        if message.tool_calls:
            return {"type": "tool_calls", "data": message.tool_calls}
        else:
            return {"type": "text", "data": message.content}

    def execute_tool(self, tool_call):
        """
        执行工具调用（根据 tool_call 中的函数名，路由到对应的本地函数）
        """
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        print(f"🔧 执行工具：{function_name}({arguments})")

        # 路由表：根据函数名执行不同的本地函数
        if function_name == "get_weather":
            city = arguments.get("city")
            result = self._get_weather(city)
        elif function_name == "calculator":
            expression = arguments.get("expression")
            result = self._calculator(expression)
        else:
            result = f"未知工具：{function_name}"

        # 把工具执行结果以 role="tool" 的形式加入消息列表
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(result)
        })

        return result

    def run(self, user_input):
        """
        对外暴露的入口：输入用户问题，返回最终答案（自动完成工具调用循环）
        """
        # 第一次调用 LLM
        result = self.call_llm(user_input)

        # 如果 AI 调用了工具，执行工具并再次调用 LLM 生成最终回复
        if result["type"] == "tool_calls":
            # 取第一个工具调用（当前只支持单工具）
            tool_call = result["data"][0]
            tool_result = self.execute_tool(tool_call)
            print(f"📦 工具返回：{tool_result}")

            # 第二次调用 LLM，让 AI 根据工具结果生成最终回复
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages
            )
            final_reply = final_response.choices[0].message.content

            # 把最终回复也加入历史（可选）
            self.messages.append({"role": "assistant", "content": final_reply})
            return final_reply
        else:
            return result["data"]

    # ========== 本地工具函数 ==========
    def _get_weather(self, city):
        """模拟天气查询"""
        if city == "北京":
            return "晴，25°C"
        elif city == "上海":
            return "多云，28°C"
        else:
            return f"未知城市：{city}"

    def _calculator(self, expression):
        """简易计算器（仅支持加减乘除）"""
        try:
            # 安全起见，只允许数字和运算符
            allowed = set("0123456789+-*/(). ")
            if not all(c in allowed for c in expression):
                return "表达式包含非法字符"
            return eval(expression)
        except Exception as e:
            return f"计算错误：{e}"

# =============================================
# 测试代码
# =============================================
if __name__ == "__main__":
    # 1. 创建 Agent
    agent = SimpleAgent()
    print("🤖 Agent 初始化完成\n")

    # 2. 注册工具
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

    # 3. 使用 Agent
    user_input = "北京今天天气怎么样？"
    print(f"🧑 用户：{user_input}")
    reply = agent.run(user_input)
    print(f"🤖 Agent：{reply}")