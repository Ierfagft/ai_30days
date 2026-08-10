# ========== 1. 传统取值方式（危险！） ==========
print("--- 传统 [] 取值（容易崩溃） ---")
config = {"name": "Agent", "version": 1}

# 如果键存在，一切正常
print(f"name: {config['name']}")  # 输出：Agent

# 但如果键不存在，程序会直接报错崩溃！
# print(config["timeout"])  # 这行会抛出 KeyError，我们注释掉避免程序中断

# ========== 2. 安全取值方式（核心任务：.get()） ==========
print("\n--- 安全的 .get() 取值 ---")
# .get() 语法：字典.get(键, 默认值)
# 如果键存在，返回对应的值；如果键不存在，返回默认值，绝不报错！

timeout = config.get("timeout", 30)   # "timeout" 不存在，返回 30
print(f"timeout: {timeout}")           # 输出：30

name = config.get("name", "未知")      # "name" 存在，返回 "Agent"
print(f"name: {name}")                 # 输出：Agent

# ========== 3. 检测标准（必须通过） ==========
d = {}  # 空字典，肯定没有键 "a"

# 官方检测：当字典没有键 "a" 时，返回 "默认" 而不是崩溃
result = d.get("a", "默认")
print(f"\n检测结果：d.get('a', '默认') 返回了 -> '{result}'")

# 断言检测（静默通过算过关）
assert d.get("a", "默认") == "默认", "❌ 检测失败！"
print("🎉 D12 检测通过！字典安全取值掌握成功！")

# ========== 4. 补充：.get() 在真实场景中的妙用（加深印象） ==========
print("\n--- 真实场景：用户配置合并 ---")
user_config = {"theme": "dark"}  # 用户只配置了主题
default_config = {"theme": "light", "language": "zh", "timeout": 10}

# 从用户配置中取值，如果用户没配，就用默认配置
theme = user_config.get("theme", default_config["theme"])
language = user_config.get("language", default_config["language"])
timeout = user_config.get("timeout", default_config["timeout"])

print(f"主题: {theme}")     # 输出：dark（用户配了）
print(f"语言: {language}")  # 输出：zh（用户没配，用默认）
print(f"超时: {timeout}")   # 输出：10（用户没配，用默认）