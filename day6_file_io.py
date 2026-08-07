import requests

# ========== 1. 复用 D5 的逻辑：获取 GitHub 格言 ==========
def fetch_zen():
    url = "https://api.github.com/zen"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text.strip()  # strip() 去掉首尾换行符
        else:
            return f"请求失败，状态码：{response.status_code}"
    except Exception as e:
        return f"网络错误：{e}"

# ========== 2. 获取格言 ==========
zen_quote = fetch_zen()
print(f"📖 获取到的格言：{zen_quote}")

# ========== 3. 核心任务：用 with open 写入 result.txt ==========
# 'w' 表示写入模式，如果文件不存在会自动创建，存在则会覆盖原内容
# encoding='utf-8' 保证中文不会乱码
with open("result.txt", "w", encoding="utf-8") as file:
    file.write(zen_quote)

print("✅ 格言已成功写入 result.txt 文件！")

# ========== 4. 额外验证（可选）：读取刚写入的内容 ==========
with open("result.txt", "r", encoding="utf-8") as file:
    saved_content = file.read()

print(f"🔍 验证读取结果：{saved_content}")

# ========== 5. 检测断言（自动验证文件内容） ==========
assert saved_content == zen_quote, "❌ 写入和读取的内容不一致！"
assert len(saved_content) > 0, "❌ 文件内容为空！"
print("\n🎉 D6 任务完成！你已成功将数据持久化到了硬盘上。")
