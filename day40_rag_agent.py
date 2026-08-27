# =============================================
# 强制设置 Hugging Face 镜像站（必须放在最顶部！）
# =============================================
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# =============================================
# 其他导入
# =============================================
import chromadb
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from dotenv import load_dotenv

# =============================================
# 手写文本分块器（无 LangChain）
# =============================================
class SimpleTextSplitter:
    def __init__(self, chunk_size=500, chunk_overlap=50, separators=None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap 必须小于 chunk_size")
        self.separators = separators or ["\n\n", "\n", "。", "，", " ", ""]

    def split_text(self, text):
        if not text:
            return []
        chunks = []
        start = 0
        text_len = len(text)
        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            if end < text_len:
                for sep in self.separators:
                    last_sep = text.rfind(sep, start, end)
                    if last_sep > start:
                        end = last_sep + len(sep)
                        break
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= text_len:
                break
            start = end - self.chunk_overlap
            if start >= end:
                start = end
        return chunks

# =============================================
# RAGAgent 类（纯基础版，无答案溯源）
# =============================================
class RAGAgent:
    def __init__(self, pdf_path=None, api_key=None, model_name="deepseek-chat", embedding_model="all-MiniLM-L6-v2"):
        """
        初始化 RAG Agent。
        - pdf_path: PDF 文件路径（可选，如果已有向量库可跳过）
        - api_key: DeepSeek API Key（不传则从 .env 读取）
        """
        # 1. 加载环境变量
        load_dotenv()
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("❌ 未找到 API Key，请配置 .env 文件")

        # 2. 初始化 LLM 客户端
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
        self.model_name = model_name

        # 3. 初始化嵌入模型（镜像站已强制设置）
        self.embedding_model = SentenceTransformer(embedding_model)

        # 4. 初始化向量数据库
        self.client_db = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client_db.get_or_create_collection(
            name="my_knowledge_base",
            metadata={"description": "RAG 知识库"}
        )

        # 5. 初始化分块器
        self.splitter = SimpleTextSplitter(chunk_size=500, chunk_overlap=50)

        # 6. 初始化对话记忆（滑动窗口）
        self.messages = [
            {"role": "system", "content": "你是企业知识库助手，请根据提供的文档回答问题。如果文档中没有相关信息，请直接说无法回答。"}
        ]
        self.max_rounds = 5  # 保留最近 5 轮对话

        # 7. 如果提供了 PDF 路径，自动加载并向量化
        if pdf_path and os.path.exists(pdf_path):
            print(f"📄 正在加载 PDF: {pdf_path}")
            self.load_pdf(pdf_path)
            self._build_vector_store()
        else:
            print("ℹ️ 未提供 PDF 路径，将使用已有向量库（如有）")

    # ========== 加载 PDF ==========
    def load_pdf(self, pdf_path):
        """从 PDF 提取文本"""
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        self.raw_text = text
        print(f"✅ 成功提取 {len(text)} 字符")

    # ========== 构建向量库 ==========
    def _build_vector_store(self):
        """将文本分块并存入向量库"""
        if not self.raw_text:
            print("⚠️ 没有文本可处理")
            return

        chunks = self.splitter.split_text(self.raw_text)
        print(f"✂️  切分成 {len(chunks)} 个块")

        if not chunks:
            print("⚠️ 没有可用的文本块")
            return

        embeddings = self.embedding_model.encode(chunks).tolist()

        if self.collection.count() > 0:
            self.collection.delete(ids=self.collection.get()["ids"])

        ids = [str(i) for i in range(len(chunks))]
        self.collection.add(ids=ids, documents=chunks, embeddings=embeddings)
        print(f"💾 存入 {self.collection.count()} 个向量到 ChromaDB")

    # ========== 检索 ==========
    def _retrieve(self, query, top_k=3):
        """从向量库检索 Top-K 相关文档"""
        query_vector = self.embedding_model.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_vector,
            n_results=top_k,
            include=["documents", "distances"]
        )
        return results["documents"][0] if results["documents"] else []

    # ========== 裁剪记忆（滑动窗口） ==========
    def _trim_memory(self):
        """只保留最近的 N 轮对话"""
        system_msg = self.messages[0]
        conversation = self.messages[1:]
        max_msgs = self.max_rounds * 2
        if len(conversation) > max_msgs:
            conversation = conversation[-max_msgs:]
        self.messages = [system_msg] + conversation

    # ========== 核心方法：问答 ==========
    def query(self, question):
        """
        对外入口：输入用户问题，返回 RAG 增强的回答
        """
        # 1. 检索相关文档
        retrieved_docs = self._retrieve(question)
        context = "\n\n".join(retrieved_docs) if retrieved_docs else "未检索到相关文档。"

        # 2. 构造上下文（拼入 User 消息）
        user_content = f"""
根据以下内部文档片段回答问题：
{context}

用户问题：{question}
"""
        self.messages.append({"role": "user", "content": user_content})

        # 3. 调用 LLM
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.messages,
            temperature=0.3,
            max_tokens=500
        )

        reply = response.choices[0].message.content

        # 4. 添加助手回复
        self.messages.append({"role": "assistant", "content": reply})

        # 5. 滑动窗口裁剪
        self._trim_memory()

        return reply

    def get_history(self):
        """查看对话历史（调试用）"""
        return self.messages.copy()

# =============================================
# 测试代码
# =============================================
if __name__ == "__main__":
    print("🚀 初始化 RAGAgent（纯 D40）...\n")

    agent = RAGAgent()

    questions = [
        "什么是Agent？",
        "RAG是什么？",
        "公司年假有多少天？"
    ]

    for q in questions:
        print(f"\n🧑 用户：{q}")
        answer = agent.query(q)
        print(f"🤖 Agent：{answer}")
        print("-" * 50)