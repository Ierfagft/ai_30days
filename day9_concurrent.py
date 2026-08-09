import asyncio
import aiohttp
import time

# ========== 1. 定义异步请求函数（复用 D8 的 async def） ==========
async def fetch_zen(session, request_id):
    """
    异步获取 GitHub 格言。
    request_id: 用来区分是第几次请求。
    """
    url = "https://api.github.com/zen"
    print(f"   [请求 {request_id}] 开始发送...")
    
    # 记录每个请求的单独耗时
    start = time.time()
    async with session.get(url) as response:
        text = await response.text()  # 异步等待返回结果
        end = time.time()
        
    print(f"   [请求 {request_id}] 完成，状态码 {response.status}，耗时 {end - start:.2f} 秒")
    return text.strip()

# ========== 2. 主函数：对比顺序 vs 并发 ==========
async def main():
    # 创建一个共享的 ClientSession（相当于异步版的 requests.Session）
    async with aiohttp.ClientSession() as session:
        
        # ----- 2.1 先做顺序执行（作为对比基准） -----
        print("\n🧪 实验1：顺序执行（依次请求3次）")
        start_seq = time.time()
        results_seq = []
        for i in range(3):
            result = await fetch_zen(session, i)
            results_seq.append(result)
        end_seq = time.time()
        total_seq = end_seq - start_seq
        print(f"⏱️  顺序总耗时: {total_seq:.2f} 秒\n")
        
        # ----- 2.2 再做并发执行（核心任务） -----
        print("🚀 实验2：并发执行（asyncio.gather 同时发起3次请求）")
        start_con = time.time()
        
        # 创建3个任务（此时还没真正执行，只是准备好）
        tasks = [fetch_zen(session, i) for i in range(3)]
        
        # asyncio.gather 会同时执行所有任务，并等待全部完成
        results_con = await asyncio.gather(*tasks)
        
        end_con = time.time()
        total_con = end_con - start_con
        print(f"⏱️  并发总耗时: {total_con:.2f} 秒")
        
        # ----- 2.3 打印结果对比，验收检测标准 -----
        print("\n📊 耗时对比：")
        print(f"   顺序执行: {total_seq:.2f} 秒")
        print(f"   并发执行: {total_con:.2f} 秒")
        print(f"   🎉 速度提升: {total_seq / total_con:.1f} 倍")
        
        # 打印获取到的格言（验证内容没问题）
        print("\n📖 获取到的格言：")
        for i, text in enumerate(results_con):
            print(f"   第{i+1}条: {text}")

# ========== 3. 启动异步程序 ==========
if __name__ == "__main__":
    asyncio.run(main())