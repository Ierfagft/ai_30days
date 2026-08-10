# ========== 1. 传统 for 循环写法（你早就熟练了） ==========
print("--- 传统 for 循环（3行代码） ---")
result = []
for x in range(5):
    result.append(x * 2)
print(f"结果: {result}")  # [0, 2, 4, 6, 8]

# ========== 2. 列表推导式写法（核心任务：一行搞定） ==========
print("\n--- 列表推导式（1行代码） ---")
result_comp = [x * 2 for x in range(5)]
print(f"结果: {result_comp}")  # [0, 2, 4, 6, 8]

# ========== 3. 进阶：带过滤条件的推导式（顺便扩充技能） ==========
print("\n--- 进阶：只取偶数 ---")
# 传统写法
evens = []
for x in range(10):
    if x % 2 == 0:
        evens.append(x)
print(f"传统循环取偶数: {evens}")

# 推导式写法（加了 if 过滤）
evens_comp = [x for x in range(10) if x % 2 == 0]
print(f"推导式取偶数: {evens_comp}")

# ========== 4. 终极检测（官方标准） ==========
# 这就是文档要求的检测命令
assert [x * 2 for x in range(5)] == [0, 2, 4, 6, 8], "❌ 推导式结果错误！"
print("\n🎉 检测通过！[x*2 for x in range(5)] 正确输出了 [0, 2, 4, 6, 8]")
print("✅ D11 任务完成！")