import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# ========== 1. 设置 Hugging Face 镜像站 ==========
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# ========== 2. 加载嵌入模型 ==========
print("📥 加载嵌入模型...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ 嵌入模型加载成功！\n")

# ========== 3. 准备示例文本块 ==========
texts = [
    "人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
    "深度学习技术的突破使得AI在图像识别、自然语言处理等领域取得了巨大进展。",
    "Agent（智能体）是指能够感知环境并采取行动以实现目标的实体。",
    "RAG（检索增强生成）是一种结合信息检索和文本生成的技术。",
    "向量检索是RAG系统的核心组件之一，它通过将文本转换为数学向量，实现高效的语义搜索。"
]

print(f"📄 准备了 {len(texts)} 个文本块\n")

# ========== 4. 生成向量 ==========
print("🔄 正在将文本块转换为向量...")
embeddings = model.encode(texts).tolist()
print(f"✅ 向量生成完成，形状：{len(embeddings)} x {len(embeddings[0])}\n")

# ========== 5. 存入 ChromaDB ==========
print("💾 正在存入 ChromaDB...")

# 创建客户端
client = chromadb.PersistentClient(path="./chroma_db")

# 获取或创建 Collection
collection = client.get_or_create_collection(
    name="my_knowledge_base",
    metadata={"description": "RAG 示例知识库"}
)

# 如果已有数据，先清空（修复了报错逻辑）
if collection.count() > 0:
    ids_to_delete = collection.get()["ids"]
    if ids_to_delete:  # 只有非空时才删除
        collection.delete(ids=ids_to_delete)

# 准备数据
ids = [str(i) for i in range(len(texts))]

# 插入数据
collection.add(
    ids=ids,
    documents=texts,
    embeddings=embeddings
)

print(f"✅ 数据存入成功！当前 Collection 中的文档数：{collection.count()}")

# ========== 6. 检测标准 ==========
assert collection.count() > 0, "❌ Collection 中没有数据！"
print("\n🎉 D34 检测通过！向量库已成功写入数据，collection.count() > 0。")