# ========== 1. if/else 判断温度 ==========
temperature = 28

if temperature > 30:
    print("🔥 天气很热！")
elif temperature > 20:
    print("🌤️ 天气温和，适合出门。")
else:
    print("❄️ 天气有点冷，多穿点。")

# ========== 2. for 循环遍历列表 ==========
cities = ["北京", "上海", "广州", "深圳"]

print("\n📌 城市列表：")
for city in cities:
    print(f"  - {city}")

# ========== 3. 定义函数 check_temp(t) ==========
def check_temp(t):
    """
    根据温度返回状态字符串。
    - 温度 > 30：返回 "Hot"
    - 温度 20~30（含）：返回 "Warm"
    - 温度 < 20：返回 "Cold"
    """
    if t > 30:
        return "Hot"
    elif t >= 20:
        return "Warm"
    else:
        return "Cold"

# ========== 4. 测试函数（检测标准） ==========
print("\n🧪 函数测试：")
result = check_temp(35)
print(f"check_temp(35) 返回: {result}")

# 额外多测几个
print(f"check_temp(25) 返回: {check_temp(25)}")
print(f"check_temp(10) 返回: {check_temp(10)}")

# ========== 5. 检测断言（静默通过算过关） ==========
assert check_temp(35) == "Hot", "❌ 35度应该是 Hot！"
assert check_temp(25) == "Warm", "❌ 25度应该是 Warm！"
assert check_temp(10) == "Cold", "❌ 10度应该是 Cold！"

print("\n✅ 所有检测通过！D3 任务完成！")