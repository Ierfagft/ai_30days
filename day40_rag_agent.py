import os
import chromadb
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from dotenv import load_dotenv

# =============================================
# 手写文本分块器（替代 LangChain 版本）
# =============================================
class SimpleTextSplitter:
    """简单文本分块器，按字符数切分，并尽量在句号处断开。"""
    def __init__(self, chunk_size=500, chunk_overlap=50, separators=None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", "。", "，", " ", ""]
    
    def split_text(self, text):
        """将文本切分成多个块"""
        if not text:
            return []
        
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            # 确定结束位置
            end = min(start + self.chunk_size, text_len)
            
            # 如果还没到末尾，尝试在合适的位置断开
            if end < text_len:
                # 从 end 往回找最近的分隔符
                for sep in self.separators:
                    last_sep = text.rfind(sep, start, end)
                    if last_sep > start:
                        end = last_sep + len(sep)
                        break
            
            # 切出一块
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # 下一个块的起始位置（考虑重叠）
            start = end - self.chunk_overlap if end < text_len else end
        
        return chunks

# =============================================
# RAGAgent 类（无 LangChain 依赖）
# =============================================
class RAGAgent:
    def __init__(self, pdf_path=None, api_key=None, model_name="deepseek-chat", embedding_model="all-MiniLM-L6-v2"):
        # 加载环境变量
        load_dotenv()
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("❌ 未找到 API Key，请配置 .env 文件")

        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
        self.model_name = model_name

        # 嵌入模型
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
        self.embedding_model = SentenceTransformer(embedding_model)

        # 向量数据库
        self.client_db = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client_db.get_or_create_collection(
            name="my_knowledge_base",
            metadata={"description": "RAG 知识库"}
        )

        # 对话记忆（滑动窗口）
        self.messages = [
            {"role": "system", "content": "你是企业知识库助手，请根据提供的文档回答问题。如果文档中没有相关信息，请直接说无法回答。"}
        ]
        self.max_rounds = 5

        # 文本分块器（手写版）
        self.splitter = SimpleTextSplitter(chunk_size=500, chunk_overlap=50)

        if pdf_path and os.path.exists(pdf_path):
            print(f"📄 正在加载 PDF: {pdf_path}")
            self.load_pdf(pdf_path)
            self._build_vector_store()
        else:
            print("ℹ️ 未提供 PDF 路径，将使用已有向量库（如有）")

    def load_pdf(self, pdf_path):
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        self.raw_text = text
        print(f"✅ 成功提取 {len(text)} 字符")

    def _build_vector_store(self):
        chunks = self.splitter.split_text(self.raw_text)
        print(f"✂️  切分成 {len(chunks)} 个块")

        if not chunks:
            print("⚠️ 没有可用的文本块，跳过构建向量库")
            return

        embeddings = self.embedding_model.encode(chunks).tolist()

        if self.collection.count() > 0:
            self.collection.delete(ids=self.collection.get()["ids"])

        ids = [str(i) for i in range(len(chunks))]
        self.collection.add(ids=ids, documents=chunks, embeddings=embeddings)
        print(f"💾 存入 {self.collection.count()} 个向量到 ChromaDB")

    def _retrieve(self, query, top_k=3):
        query_vector = self.embedding_model.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_vector,
            n_results=top_k,
            include=["documents", "distances"]
        )
        return results["documents"][0] if results["documents"] else []

    def _trim_memory(self):
        system_msg = self.messages[0]
        conversation = self.messages[1:]
        max_msgs = self.max_rounds * 2
        if len(conversation) > max_msgs:
            conversation = conversation[-max_msgs:]
        self.messages = [system_msg] + conversation

    def query(self, question):
        retrieved_docs = self._retrieve(question)
        context = "\n\n".join(retrieved_docs) if retrieved_docs else "未检索到相关文档。"

        user_content = f"""
根据以下内部文档片段回答问题：
{context}

用户问题：{question}
"""
        self.messages.append({"role": "user", "content": user_content})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.messages,
            temperature=0.3,
            max_tokens=500
        )

        reply = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": reply})
        self._trim_memory()

        return reply

    def get_history(self):
        return self.messages.copy()

# =============================================
# 测试
# =============================================
if __name__ == "__main__":
    print("🚀 初始化 RAGAgent（无 LangChain 依赖）...\n")
    agent = RAGAgent()

    for q in ["什么是Agent？", "RAG是什么？", "公司年假有多少天？"]:
        print(f"\n🧑 用户：{q}")
        print(f"🤖 Agent：{agent.query(q)}")
        print("-" * 50)