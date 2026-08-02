name = input("Li Hua")
age = 23

print(f"\n你好{name}，我们来数数:")
for i in range(5):
    print(f"这是{i + 1}次循环")

def greet(user):
    return f"你好，{user}你的 Python 环境已就绪，准备迎接明天的 API 调用吧！"    

print(greet(name))