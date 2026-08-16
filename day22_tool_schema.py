import json

# ========== 核心任务：定义 get_weather 的工具 Schema ==========
get_weather_schema = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "获取指定城市的当前天气信息",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，例如：北京、上海"
                }
            },
            "required": ["city"]
        }
    }
}

# 打印出来验证（检测标准：能看到 properties 字段）
print("📦 工具 Schema（格式化输出）：")
print(json.dumps(get_weather_schema, indent=2, ensure_ascii=False))

# ========== 检测 ==========
assert "properties" in get_weather_schema["function"]["parameters"], "❌ 缺少 properties 字段！"
print("\n✅ D22 检测通过！你已成功定义了一个包含 properties 字段的工具 Schema。")