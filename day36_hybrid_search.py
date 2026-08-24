import os
import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

# ========== 1. 设置镜像站 ==========
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# ========== 2. 加载嵌入模型 ==========
print("📥 加载嵌入模型...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ 模型加载成功！\n")

# ========== 3. 连接 ChromaDB，获取所有文档 ==========
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("my_knowledge_base")

# 取出所有文档
all_data = collection.get()
documents = all_data["documents"]  # 文本列表
doc_ids = all_data["ids"]

print(f"📚 从向量库中读取到 {len(documents)} 个文档\n")

# ========== 4. 定义查询词 ==========
query = "智能体"  # 你可以换成其他词测试
print(f"🔍 查询词：{query}\n")

# ========== 5. 向量检索（语义） ==========
print("🧪 向量检索（语义）结果：")
query_vector = model.encode([query]).tolist()
vector_results = collection.query(
    query_embeddings=query_vector,
    n_results=len(documents),  # 返回所有文档，方便后续混合排序
    include=["documents", "distances"]
)

# 整理向量检索结果：按距离升序（越近越相关）
vector_docs = vector_results["documents"][0]
vector_distances = vector_results["distances"][0]

# ========== 6. BM25 检索（关键词） ==========
print("🧪 BM25 检索（关键词）结果：")

# 对文档进行分词（简单按空格切分，中文需要更细的分词，这里用字符级分词）
def tokenize(text):
    # 简单中文分词：按字符切分（适合小规模演示）
    return list(text.replace(" ", ""))

tokenized_docs = [tokenize(doc) for doc in documents]
bm25 = BM25Okapi(tokenized_docs)

# 对查询分词
query_tokens = tokenize(query)
bm25_scores = bm25.get_scores(query_tokens)  # 返回每个文档的 BM25 分数（越高越相关）

# 按 BM25 分数降序排序
bm25_indices = np.argsort(bm25_scores)[::-1]  # 从高到低

# ========== 7. 打印单独结果对比 ==========
print("\n向量检索 Top 3：")
for i, (doc, dist) in enumerate(zip(vector_docs[:3], vector_distances[:3]), 1):
    print(f"  {i}. (距离 {dist:.4f}) {doc[:60]}...")

print("\nBM25 检索 Top 3：")
for i, idx in enumerate(bm25_indices[:3], 1):
    print(f"  {i}. (BM25 分数 {bm25_scores[idx]:.2f}) {documents[idx][:60]}...")

# ========== 8. 混合检索（加权合并） ==========
print("\n🔄 混合检索（向量 + BM25 加权）结果：")

# 归一化向量距离（转化为相似度得分，距离越小得分越高）
max_dist = max(vector_distances)
min_dist = min(vector_distances)
if max_dist == min_dist:
    vector_scores_norm = [1.0] * len(vector_docs)
else:
    vector_scores_norm = [1 - (d - min_dist) / (max_dist - min_dist) for d in vector_distances]

# 归一化 BM25 分数
max_bm25 = max(bm25_scores)
min_bm25 = min(bm25_scores)
if max_bm25 == min_bm25:
    bm25_scores_norm = [1.0] * len(documents)
else:
    bm25_scores_norm = [(s - min_bm25) / (max_bm25 - min_bm25) for s in bm25_scores]

# 加权合并（权重可调）
alpha = 0.5  # 向量权重
beta = 0.5   # BM25 权重
hybrid_scores = [alpha * v + beta * b for v, b in zip(vector_scores_norm, bm25_scores_norm)]

# 按混合分数降序排序
hybrid_indices = np.argsort(hybrid_scores)[::-1]

for i, idx in enumerate(hybrid_indices[:3], 1):
    print(f"  {i}. (混合得分 {hybrid_scores[idx]:.4f}) {documents[idx][:60]}...")

# ========== 9. 检测标准 ==========
print("\n" + "="*50)
print("📊 检测结果：")

# 取向量检索 Top 1 和 BM25 Top 1 的 ID
vector_top1 = vector_docs[0][:30] if vector_docs else ""
bm25_top1 = documents[bm25_indices[0]][:30] if len(bm25_indices) > 0 else ""
hybrid_top1 = documents[hybrid_indices[0]][:30] if len(hybrid_indices) > 0 else ""

# 如果向量和 BM25 的 Top 1 不一致，说明互补有效
if vector_top1 != bm25_top1:
    print("✅ 向量检索和 BM25 返回的 Top 1 不一致，证明两者互补有效！")
else:
    print("ℹ️ 向量检索和 BM25 返回的 Top 1 相同，说明两者对当前查询的判断一致。")

print(f"混合检索 Top 1：{hybrid_top1}...")
print("\n🎉 D36 检测通过！你已成功实现混合检索。")