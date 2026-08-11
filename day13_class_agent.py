# ========== 1. 定义 Agent 类（核心任务） ==========
class Agent:
    """
    这是一个简单的 Agent 类。
    __init__ 方法会在创建实例时自动调用，用来初始化名字。
    run 方法是 Agent 的核心行为。
    """
    
    # 初始化方法（构造函数）
    def __init__(self, name):
        # self.name 是实例变量，把传入的 name 存起来
        self.name = name
        print(f"✅ Agent '{self.name}' 已创建！")
    
    # Agent 的运行方法
    def run(self):
        # 通过 self.name 访问实例的名字
        print(f"🤖 Agent '{self.name}' 正在运行...")
        # 可以在这里加具体任务，我们先打印一句话作为演示
        return f"任务执行完成（来自 {self.name}）"

# ========== 2. 使用 Agent 类（检测标准） ==========
if __name__ == "__main__":
    # 实例化：创建具体的 Agent 对象，名字叫 "助手"
    a = Agent("助手")      # 这行会自动调用 __init__ 方法
    
    # 调用 run 方法（必须能打印出名字）
    result = a.run()
    print(result)

    # 再建一个试试，加深印象
    b = Agent("管家")
    b.run()