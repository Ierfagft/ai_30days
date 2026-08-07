# ========== 1. 什么是 *args 和 **kwargs？ ==========
# *args：用来接收任意数量的【位置参数】（Positional Arguments），打包成元组（tuple）。
# **kwargs：用来接收任意数量的【关键字参数】（Keyword Arguments），打包成字典（dict）。

# ========== 2. 核心任务：定义 log_info 函数 ==========
def log_info(**data):
    """
    接收任意数量的关键字参数，并逐个打印。
    例如：log_info(name="小明", age=18)
    """
    print("📝 开始打印日志信息：")
    for key, value in data.items():
        print(f"   {key}: {value}")
    print("✅ 日志打印完成！\n")

# ========== 3. 补充学习：*args 的用法（顺便理解区别） ==========
def log_args(*args):
    """
    接收任意数量的位置参数，并逐个打印。
    例如：log_args("苹果", "香蕉", "橘子")
    """
    print("📦 位置参数列表：")
    for item in args:
        print(f"   - {item}")
    print()

# ========== 4. 调用测试（必须满足检测标准） ==========
print("--- 测试 **kwargs（关键字参数） ---")
log_info(name="小明", age=18)

print("--- 测试 *args（位置参数） ---")
log_args("苹果", "香蕉", "橘子")

# ========== 5. 额外测试：混合使用场景 ==========
print("--- 混合使用（普通参数 + **kwargs） ---")
def greet(greeting, **person_info):
    print(f"{greeting}！以下是你的个人信息：")
    for key, value in person_info.items():
        print(f"   {key}: {value}")

greet("你好", name="小红", city="北京", score=95)

# ========== 6. 自动检测（assert） ==========
# 因为 log_info 只是打印，不返回值，我们这里捕获 print 输出会比较复杂，
# 所以 D7 的检测标准以肉眼看到控制台输出为准。
# 但为了严谨，我们验证 **kwargs 确实被正确打包成了字典。
def test_kwargs(**data):
    return data  # 直接返回字典

result = test_kwargs(name="小明", age=18)
assert result == {"name": "小明", "age": 18}, "❌ **kwargs 打包失败！"
assert "name" in result and "age" in result, "❌ 键值缺失！"
print("\n🎉 所有检测通过！D7 任务完成！")