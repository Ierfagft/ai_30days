import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# =============================================
# SimpleAgent 类（升级版：增加防死循环上限）
# =============================================
class SimpleAgent:
    def __init__(self, api_key=None, base_url="https://api.deepseek.com", model="deepseek-chat", max_iterations=3):
        load_dotenv()
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("❌ 未找到 API Key，请配置 .env 或传入 api_key")

        self.client = OpenAI(api_key=self.api_key, base_url=base_url)
        self.model = model
        self.tools = []
        self.messages = []
        self.max_iterations = max_iterations  # 👈 D29 新增：安全闸门

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

    def _call_llm_once(self):
        """调用一次 LLM，并返回 message 对象"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tools if self.tools else None,
            tool_choice="auto" if self.tools else None
        )
        message = response.choices[0].message
        self.messages.append(message.model_dump())  # 记录 AI 的回复（含 tool_calls）
        return message

    def execute_tool(self, tool_call):
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        print(f"🔧 执行工具：{function_name}({arguments})")

        # 路由分发
        if function_name == "get_weather":
            city = arguments.get("city")
            result = self._get_weather(city)
        elif function_name == "calculator":
            expression = arguments.get("expression")
            result = self._calculator(expression)
        elif function_name == "echo":  # 👈 D29 新增：诱导循环的工具
            result = self._echo(arguments.get("msg", ""))
        else:
            result = f"未知工具：{function_name}"

        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(result)
        })
        return result

    # ========== D29 核心升级：带循环上限的 run 方法 ==========
    def run(self, user_input):
        self.add_message("user", user_input)

        iterations = 0
        while iterations < self.max_iterations:
            iterations += 1
            print(f"🔄 迭代 {iterations}/{self.max_iterations}")

            # 1. 调用 LLM
            message = self._call_llm_once()

            # 2. 如果 AI 想调用工具，执行它们
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    self.execute_tool(tool_call)
                # 执行完后继续循环（让 AI 看到工具结果）
            else:
                # 没有工具调用，说明 AI 已给出最终答案
                return message.content

        # 3. 超出迭代上限，强制停止
        raise RuntimeError(f"❌ 达到最大迭代次数 {self.max_iterations}，强制停止以防止死循环！")

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

    # ========== D29 新增：专用于诱导循环的 echo 工具 ==========
    def _echo(self, msg):
        """总是返回'请再调用我一次'，让 AI 不断重复调用"""
        return f"请再调用我一次。你刚说：{msg}"

# =============================================
# 测试代码
# =============================================
if __name__ == "__main__":
    print("=" * 50)
    print("🧪 测试 1：正常情况（不触发上限）")
    print("=" * 50)

    agent = SimpleAgent(max_iterations=3)

    agent.register_tool(
        name="get_weather",
        description="获取指定城市的当前天气信息",
        parameters={
            "type": "object",
            "properties": {"city": {"type": "string", "description": "城市名称"}},
            "required": ["city"]
        }
    )
    agent.register_tool(
        name="calculator",
        description="执行数学计算",
        parameters={
            "type": "object",
            "properties": {"expression": {"type": "string", "description": "数学表达式"}},
            "required": ["expression"]
        }
    )

    reply = agent.run("北京天气怎么样？顺便算 3+5*2")
    print(f"🤖 最终回复：{reply}\n")

    # ============================================
    # 诱导测试：故意让 AI 陷入循环（必须触发上限）
    # ============================================
    print("=" * 50)
    print("🧪 测试 2：诱导循环（触发最大迭代上限）")
    print("=" * 50)

    agent_trap = SimpleAgent(max_iterations=3)

    agent_trap.register_tool(
        name="echo",
        description="返回一条要求重复的消息",
        parameters={
            "type": "object",
            "properties": {"msg": {"type": "string", "description": "要回显的消息"}},
            "required": ["msg"]
        }
    )

    try:
        # 用户发起请求，AI 会不断调用 echo 工具，直到达到上限
        result = agent_trap.run("请调用 echo 工具，消息内容为 '你好'")
        print(f"🤖 最终回复：{result}")
    except RuntimeError as e:
        print(f"🛑 {e}")
        print("✅ 防死循环机制生效！程序优雅地抛出了异常，没有卡死。")