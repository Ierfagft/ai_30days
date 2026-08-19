import os
from pypdf import PdfReader

# ========== 1. 指定 PDF 文件路径 ==========
pdf_path = os.path.join(os.path.dirname(__file__), "sample.pdf")

# ========== 2. 检查文件是否存在 ==========
if not os.path.exists(pdf_path):
    print(f"❌ 找不到 PDF 文件：{pdf_path}")
    print("请先在项目文件夹下放置一个 sample.pdf 文件。")
    exit(1)

# ========== 3. 读取 PDF 第一页 ==========
try:
    reader = PdfReader(pdf_path)
    if len(reader.pages) == 0:
        print("⚠️ PDF 文件似乎没有页面。")
        exit(1)

    # 读取第一页
    first_page = reader.pages[0]
    text = first_page.extract_text()

    print(f"📄 成功读取 PDF 第一页，共 {len(reader.pages)} 页")
    print("-" * 40)
    print("第一页内容：")
    print(text if text.strip() else "⚠️ 该页可能没有可提取的文本（可能是扫描件或图片）。")
    print("-" * 40)

    # 检测标准：只要没有报错，就算通过
    print("\n✅ D31 检测通过！成功读取了 PDF 的第一页文本。")

except Exception as e:
    print(f"❌ 读取 PDF 时发生错误：{e}")