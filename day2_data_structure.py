# ========== 1. 变量（字符串 / 整数 / 布尔） ==========
name = "AI_Agent"          # 字符串
version = 1                # 整数
is_ready = True            # 布尔

print(f"初始化: {name}, 版本: {version}, 就绪: {is_ready}")

# ========== 2. 列表（增删改查 + len()） ==========
tools = ["Python", "Git"]   # 初始列表

# 增 ( Append / Insert )
tools.append("Docker")      # 尾部追加
tools.insert(1, "VS Code")  # 索引1插入
print("增之后:", tools)      # 预期: ['Python', 'VS Code', 'Git', 'Docker']

# 查 ( Index )
first_tool = tools[0]       # 查第一个
print("第一个工具:", first_tool)

# 改 ( Assign )
tools[2] = "GitHub"         # 把索引2的 Git 改成 GitHub
print("改之后:", tools)      # 预期: ['Python', 'VS Code', 'GitHub', 'Docker']

# 删 ( Remove / Pop )
tools.remove("Docker")      # 删除指定值
popped = tools.pop()        # 删除最后一个元素（此时是 GitHub，因为上一步改了顺序？等一下注意顺序）
# 注：上面 pop() 删掉了最后的 "GitHub"，但原逻辑是为了演示，我们重新整理一下
# 为了让代码逻辑更清晰，把上面几行重新规整（避免干扰），我把下面写成完全正确的演示：

# 重新演示删除（重置列表）
tools = ["Python", "VS Code", "Git", "Docker"]
tools.remove("Git")          # 删除指定值
last = tools.pop()          # 删除最后一个（Docker），并保存到变量
print("删之后:", tools)      # 预期: ['Python', 'VS Code']

# len() 测试
tool_count = len(tools)
print(f"当前工具数量: {tool_count}")  # 预期: 2

# ========== 3. 字典（增删改查 + .get() 安全取值） ==========
config = {
    "model": "deepseek",
    "temperature": 0.7,
    "max_tokens": 100
}

# 查 ( 直接索引 )
model_name = config["model"]
print(f"模型: {model_name}")

# 改 ( 赋值 )
config["temperature"] = 0.9
print("改之后:", config)

# 增 ( 赋值新键 )
config["top_p"] = 0.95
print("增之后:", config)

# 删 ( Del )
del config["max_tokens"]
print("删之后:", config)

# .get() 安全取值（重点）
unknown = config.get("unknown_key", "默认值")  # 不会报错，返回默认值
print("不存在的键取值:", unknown)

existing = config.get("model", "没有该键")
print("存在的键取值:", existing)

# ========== 4. 嵌套结构（列表套字典） ==========
# 场景：一个工具列表，每个工具是一个字典
tool_list = [
    {"name": "Python", "type": "语言", "score": 95},
    {"name": "VS Code", "type": "编辑器", "score": 90},
    {"name": "Git", "type": "版本控制", "score": 85}
]

# 嵌套索引：取第二个元素的 type
second_type = tool_list[1]["type"]
print(f"第二个工具的类型: {second_type}")  # 预期: 编辑器

# 遍历嵌套修改
for tool in tool_list:
    if tool["name"] == "Python":
        tool["score"] = 100  # 改分
print("嵌套修改后:", tool_list)

# ========== 5. 终极检测：断言（全部通过才算过关） ==========
# 断言通过则静默无输出，如果出错程序会直接报 AssertionError 并中断

# 测试 len()
assert len(tools) == 2, "❌ 列表长度不是2"

# 测试 .get()
assert config.get("temperature") == 0.9, "❌ 字典值不对"
assert config.get("xxx", "fallback") == "fallback", "❌ get默认值失效"

# 测试嵌套索引
assert tool_list[1]["type"] == "编辑器", "❌ 嵌套索引取值错误"
assert tool_list[0]["score"] == 100, "❌ 嵌套修改赋值错误"

# 测试变量类型
assert isinstance(name, str), "❌ name不是字符串"
assert isinstance(version, int), "❌ version不是整数"
assert isinstance(is_ready, bool), "❌ is_ready不是布尔"

print("\n🎉 完美！所有断言全部通过，数据结构基础已掌握！")