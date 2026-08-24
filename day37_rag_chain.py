import os
import chromadb
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# ========== 1. 加载环境变量与模型 ==========
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("❌ 未找到 DEEPSEEK_API_KEY，请检查 .env 文件")

# 设置镜像站
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

print("📥 加载嵌入模型...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ 嵌入模型加载成功！\n")

# ========== 2. 连接向量库 ==========
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("my_knowledge_base")

print(f"📚 向量库文档数：{collection.count()}\n")

# ========== 3. 定义检索函数 ==========
def retrieve(query, top_k=3):
    """将查询转为向量，从向量库检索 top_k 个最相似的文档"""
    query_vector = embedding_model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_vector,
        n_results=top_k,
        include=["documents", "distances"]
    )
    return results["documents"][0]

# ========== 4. RAG 问答函数 ==========
def rag_qa(query):
    """
    完整的 RAG 链路：
    1. 检索相关文档
    2. 拼入 System Prompt
    3. 调用大模型生成回答
    """
    # Step 1: 检索
    retrieved_docs = retrieve(query)
    context = "\n\n".join(retrieved_docs)  # 用换行合并多个文档

    print(f"🔍 检索到的相关上下文：\n{context}\n")
    print("-" * 50)

    # Step 2: 构建 System Prompt（把检索到的知识嵌入）
    system_prompt = f"""
你是一个企业知识库助手。请严格基于以下提供的内部文档片段来回答用户的问题。
如果文档中没有相关信息，请直接说“根据现有文档无法回答此问题”，不要编造。

内部文档片段：
{context}
"""

    # Step 3: 调用大模型
    client_openai = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    response = client_openai.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        temperature=0.3,
        max_tokens=300
    )

    return response.choices[0].message.content

# ========== 5. 测试 ==========
if __name__ == "__main__":
    # 先测试一个与知识库相关的问题
    question = "什么是Agent？"
    print(f"🧑 用户问：{question}\n")
    answer = rag_qa(question)
    print(f"🤖 RAG Agent 回答：\n{answer}\n")

    print("=" * 50)

    # 再测试一个知识库中没有的问题（检测是否会乱编）
    question2 = "公司年假有多少天？"
    print(f"🧑 用户问：{question2}\n")
    answer2 = rag_qa(question2)
    print(f"🤖 RAG Agent 回答：\n{answer2}")