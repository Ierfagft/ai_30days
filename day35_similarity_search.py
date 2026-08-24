import os
import chromadb
from sentence_transformers import SentenceTransformer

# ========== 1. 设置镜像站 ==========
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# ========== 2. 加载嵌入模型（与 D34 相同） ==========
print("📥 加载嵌入模型...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ 嵌入模型加载成功！\n")

# ========== 3. 连接 ChromaDB ==========
print("🔗 连接向量数据库...")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("my_knowledge_base")  # 必须与 D34 的 Collection 名称一致

print(f"📚 当前向量库中的文档数：{collection.count()}\n")

# ========== 4. 定义查询关键词 ==========
query = "智能体"  # 你可以换成 "天气"、"数学" 等任意词

print(f"🔍 查询关键词：{query}")

# ========== 5. 将查询词转成向量 ==========
query_vector = model.encode([query]).tolist()

# ========== 6. 在向量库中搜索最相似的 Top-3 ==========
results = collection.query(
    query_embeddings=query_vector,  # 查询向量
    n_results=3,                     # 返回最相似的 3 个结果
    include=["documents", "distances"]  # 返回原文和相似度分数
)

# ========== 7. 打印结果 ==========
print("\n📄 检索结果（按相似度从高到低排列）：\n")
for i, (doc, dist) in enumerate(zip(results["documents"][0], results["distances"][0]), 1):
    print(f"排名 {i}（相似度分数：{dist:.4f}，越小越相似）：")
    print(f"   {doc}\n")

# ========== 8. 检测标准 ==========
if len(results["documents"][0]) > 0:
    print("✅ D35 检测通过！成功从向量库中检索出相关文本块。")
else:
    print("⚠️ 未检索到任何结果，请检查向量库是否有数据。")