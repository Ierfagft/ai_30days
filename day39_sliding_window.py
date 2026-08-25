import os
from openai import OpenAI
from dotenv import load_dotenv

# ========== 1. 加载环境变量 ==========
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("❌ 未找到 DEEPSEEK_API_KEY，请检查 .env 文件")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# ========== 2. 带滑动窗口的记忆类 ==========
class SlidingWindowMemory:
    def __init__(self, max_rounds=5):
        """
        初始化记忆窗口。
        max_rounds: 保留最近 N 轮对话（每轮包含 1 条 user + 1 条 assistant）
        """
        self.max_rounds = max_rounds
        self.messages = [
            {"role": "system", "content": "你是一个友好的助手，会记住最近几轮的对话内容。"}
        ]

    def add_user_message(self, content):
        """添加用户消息"""
        self.messages.append({"role": "user", "content": content})
        self._trim()

    def add_assistant_message(self, content):
        """添加助手消息"""
        self.messages.append({"role": "assistant", "content": content})
        self._trim()

    def _trim(self):
        """
        滑动窗口核心：保留 system + 最近 N 轮对话。
        每轮 = 1 条 user + 1 条 assistant，所以 5 轮 = 10 条消息。
        """
        # 保留 system 消息（索引 0）
        system_msg = self.messages[0] if self.messages else None

        # 获取除 system 外的所有消息（即对话消息）
        conversation_msgs = self.messages[1:]

        # 如果对话消息数量超过最大轮数 * 2（因为每轮有 2 条），则截断
        max_msgs = self.max_rounds * 2
        if len(conversation_msgs) > max_msgs:
            # 只保留最近的 max_msgs 条对话消息
            conversation_msgs = conversation_msgs[-max_msgs:]

        # 重新组装消息列表
        self.messages = [system_msg] + conversation_msgs if system_msg else conversation_msgs

    def get_messages(self):
        """返回当前消息列表（只读）"""
        return self.messages.copy()

    def get_stats(self):
        """返回统计信息，方便观察窗口大小"""
        total = len(self.messages)
        rounds = (total - 1) // 2  # 减去 system
        return f"总消息数: {total}（包含 system），对话轮数: {rounds}"

# ========== 3. 对话函数 ==========
def chat(memory, user_input):
    """发送消息并更新记忆"""
    memory.add_user_message(user_input)

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=memory.get_messages(),
        temperature=0.7,
        max_tokens=150
    )

    reply = response.choices[0].message.content
    memory.add_assistant_message(reply)

    return reply

# ========== 4. 测试滑动窗口 ==========
print("🧪 开始测试滑动窗口（保留最近 3 轮）\n")

# 使用较小的窗口方便观察（3 轮）
memory = SlidingWindowMemory(max_rounds=3)

# 连续进行 6 轮对话
rounds = [
    "我叫小王。",
    "我今年 25 岁。",
    "我住在北京。",
    "我最喜欢的颜色是蓝色。",
    "我是一名程序员。",
    "我的爱好是打篮球。"
]

for i, user_input in enumerate(rounds, 1):
    print(f"第 {i} 轮")
    print(f"🧑 用户: {user_input}")
    reply = chat(memory, user_input)
    print(f"🤖 助手: {reply}")
    print(f"📊 当前状态: {memory.get_stats()}\n")

# ========== 5. 检测：第 6 轮时，最早的信息应该被遗忘 ==========
print("=" * 50)
print("🔍 检测：第 6 轮后，询问最早的信息...")

test_memory = SlidingWindowMemory(max_rounds=3)
# 模拟对话
test_memory.add_user_message("我叫小王。")
test_memory.add_assistant_message("你好小王！")
test_memory.add_user_message("我今年 25 岁。")
test_memory.add_assistant_message("25 岁正是好年纪！")
test_memory.add_user_message("我住在北京。")
test_memory.add_assistant_message("北京是个好城市！")
test_memory.add_user_message("我最喜欢的颜色是蓝色。")
test_memory.add_assistant_message("蓝色很漂亮！")
test_memory.add_user_message("我是一名程序员。")
test_memory.add_assistant_message("程序员很酷！")
test_memory.add_user_message("我的爱好是打篮球。")
test_memory.add_assistant_message("打篮球锻炼身体！")

# 现在查询名字，应该不记得了
test_memory.add_user_message("我叫什么名字？")
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=test_memory.get_messages(),
    temperature=0.7,
    max_tokens=100
)
reply = response.choices[0].message.content
print(f"🧑 问: 我叫什么名字？")
print(f"🤖 答: {reply}")

if "小王" not in reply and "王" not in reply:
    print("✅ D39 检测通过！模型已经忘记了最早的信息（滑动窗口生效）。")
else:
    print("⚠️ 模型似乎还记得最早的信息，请检查窗口大小是否正确。")