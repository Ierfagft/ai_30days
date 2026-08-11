# ========== test_import.py ==========
# 这个文件用来导入 day14_name_main，验证它的代码不会自动执行

import day14_name_main

print("✅ 导入成功！day14_name_main 中的 main() 没有自动运行。")
print("   （因为 main() 被保护在 if __name__ == '__main__': 内部了）")

# 如果你想调用它的函数，必须显式调用
day14_name_main.helper()