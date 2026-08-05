import requests

# ========== 1. 定义目标 URL ==========
url = "https://api.github.com/zen"

# ========== 2. 发送请求并处理异常（复用 D4 的 try/except 技能） ==========
try:
    print("🌐 正在请求 GitHub 格言...")
    response = requests.get(url, timeout=5)  # timeout=5 表示最多等待5秒
    
    # ========== 3. 检查状态码并打印内容（检测标准） ==========
    if response.status_code == 200:
        print(f"✅ 请求成功！状态码：{response.status_code}")
        print(f"📖 GitHub 格言：{response.text}")
    else:
        print(f"⚠️ 请求返回了非200状态码：{response.status_code}")

except requests.exceptions.ConnectionError:
    print("❌ 网络连接失败，请检查你的网络或代理设置。")
except requests.exceptions.Timeout:
    print("❌ 请求超时，服务器响应太慢。")
except Exception as e:
    print(f"❌ 发生了未知错误：{e}")