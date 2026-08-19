import os
# 在开头强制使用 Hugging Face 镜像站（必须放在第一行！）
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 然后才是正常的 import
from sentence_transformers import SentenceTransformer

print("📥 正在加载模型 all-MiniLM-L6-v2（从镜像站下载）...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ 模型加载成功！\n")

sentences = [
    "你好，世界！",
    "今天天气真好。",
    "人工智能正在改变世界。"
]

print("📝 测试句子：")
for s in sentences:
    print(f"   - {s}")

embeddings = model.encode(sentences)

print("\n🔢 生成的向量信息：")
print(f"   - 向量形状: {embeddings.shape}")  # 应该是 (3, 384)
print(f"   - 第一个句子的向量（前10个数字）: {embeddings[0][:10]}...")
print(f"   - 向量数据类型: {embeddings.dtype}")

# 检测
assert embeddings.shape == (3, 384), "❌ 向量形状不对！"
print("\n✅ D33 检测通过！模型从镜像站加载成功。")