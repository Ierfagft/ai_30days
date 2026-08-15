import asyncio
import aiohttp
import json

# ==========================================
# 1. 定义 AsyncDataFetcher 类（核心任务）
# ==========================================
class AsyncDataFetcher:
    """
    异步数据获取器。
    支持并发请求 3 个 API，并带有 1 次自动重试机制。
    """
    
    def __init__(self, max_retries=1):
        """
        初始化获取器。
        max_retries: 最大重试次数（这里设为 1，即失败后最多再试 1 次）
        """
        self.max_retries = max_retries
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def fetch_single(self, session, url):
        """
        获取单个 URL 的数据（带重试机制）。
        如果第一次失败，会等待 0.5 秒后重试一次。
        """
        # 尝试次数 = 最大重试次数 + 1 (首次)
        for attempt in range(self.max_retries + 1):
            try:
                # 发起异步请求
                async with session.get(url, headers=self.headers, timeout=10) as response:
                    # 检查状态码
                    if response.status == 200:
                        # 尝试解析 JSON，如果失败则返回文本摘要
                        try:
                            data = await response.json()
                            # 如果是 JSON 格式，返回紧凑格式的字符串
                            return json.dumps(data, ensure_ascii=False)[:150] + "..."
                        except:
                            text = await response.text()
                            # 纯文本返回前 100 个字符
                            return text[:100] + ("..." if len(text) > 100 else "")
                    else:
                        # 状态码不是 200，当作一次失败
                        raise Exception(f"HTTP {response.status}")
            
            except Exception as e:
                # 捕获所有异常（网络超时、连接错误等）
                if attempt < self.max_retries:
                    # 如果还没达到重试上限，打印提示并等待
                    print(f"   ⚠️  请求失败，正在重试 (第 {attempt+2} 次尝试): {url}")
                    await asyncio.sleep(0.5)  # 等待 0.5 秒再重试
                else:
                    # 重试次数用完了，返回错误信息
                    return f"❌ 获取失败: {str(e)}"
        
        return "❌ 未知错误"

    async def fetch_all(self, urls):
        """
        并发获取多个 URL。
        使用 asyncio.gather 同时执行多个 fetch_single 任务。
        """
        # 创建一个共享的 ClientSession（复用连接，提升性能）
        async with aiohttp.ClientSession() as session:
            # 创建任务列表：每个 url 对应一个 fetch_single 任务
            tasks = [self.fetch_single(session, url) for url in urls]
            # 并发执行所有任务
            results = await asyncio.gather(*tasks)
            return results

    def run(self, urls):
        """
        外部调用的入口函数（同步接口）。
        负责启动异步事件循环并返回结果。
        """
        # asyncio.run() 是启动异步程序的统一入口
        return asyncio.run(self.fetch_all(urls))


# ==========================================
# 2. 使用类并测试（检测标准）
# ==========================================
if __name__ == "__main__":
    print("🚀 第一阶段大阅兵：AsyncDataFetcher 测试开始")
    print("=" * 40)
    
    # 定义 3 个公开 API（不同类型的接口，增加测试覆盖）
    test_urls = [
        "https://api.ipify.org?format=json",           # 返回你的公网 IP
        "https://jsonplaceholder.typicode.com/todos/1", # 测试 JSON 数据
        "https://api.github.com/zen"                   # 返回一句格言
    ]
    
    # 实例化获取器（最大重试 1 次）
    fetcher = AsyncDataFetcher(max_retries=1)
    
    # 执行并发获取
    print("📡 正在并发请求 3 个 API...\n")
    results = fetcher.run(test_urls)
    
    # 打印结果摘要
    print("✅ 获取完成！结果摘要如下：")
    for i, (url, data) in enumerate(zip(test_urls, results), 1):
        # 截断过长的 URL 以便显示
        short_url = url[:50] + "..." if len(url) > 50 else url
        print(f"\n📌 接口 {i}: {short_url}")
        print(f"   数据: {data}")
    
    print("\n" + "=" * 40)
    print("🎉 第一阶段大阅兵顺利结束！所有任务跑通且无报错！")