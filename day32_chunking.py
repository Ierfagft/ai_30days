import os
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ========== 1. 从外部文件读取文本 ==========
text_file = os.path.join(os.path.dirname(__file__), "sample_text.txt")
if not os.path.exists(text_file):
    print(f"❌ 找不到文本文件：{text_file}")
    exit(1)

with open(text_file, "r", encoding="utf-8") as f:
    text = f.read().strip()

if not text:
    print("❌ 文本文件为空，请先写入内容。")
    exit(1)

print(f"📄 成功读取文本，共 {len(text)} 字符\n")

# ========== 2. 文本分块 ==========
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "，", " ", ""]
)

chunks = splitter.split_text(text)

print(f"✂️  文本被切分成 {len(chunks)} 个块：\n")
for i, chunk in enumerate(chunks):
    print(f"块 {i+1}（长度：{len(chunk)} 字符）：")
    print(chunk[:150] + ("..." if len(chunk) > 150 else ""))
    print("-" * 40)

# ========== 3. 检测标准 ==========
assert len(chunks) > 1, "❌ 分块数量应大于1，说明文本太短或分块参数不合适"
assert all(len(c) <= 500 for c in chunks), "❌ 存在超过500字符的块"
print("\n✅ D32 检测通过！文本分块成功，每块 ≤ 500 字符。")