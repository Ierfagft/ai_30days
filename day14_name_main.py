# ========== day14_name_main.py ==========
# 这是一个用来演示 __name__ 工作原理的脚本

def main():
    """程序的主入口函数"""
    print("🚀 程序正在运行...")
    print("   (这段代码只在直接运行脚本时执行)")

# 这是一个测试函数（模拟导入时的行为）
def helper():
    print("🛠️  helper 函数被调用了")

# ========== 核心知识点：if __name__ == "__main__" ==========
# 当你在终端执行 python day14_name_main.py 时，Python 会把 __name__ 设为 "__main__"
# 当你在其他文件里 import day14_name_main 时，Python 会把 __name__ 设为 "day14_name_main"
if __name__ == "__main__":
    # 只有直接运行脚本时，才会进入这个 if 块
    main()
else:
    # 如果这个文件被 import 到别的文件里，会执行这里（通常留空或写一些初始化）
    print(f"📦 模块被导入，__name__ = {__name__}")