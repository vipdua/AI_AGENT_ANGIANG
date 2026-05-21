import os

# ===================================================
# 📄 FORMAT SOURCES
# ===================================================
def format_sources(documents):
    if not documents:
        return ""

    sources = set()

    for doc in documents:
        # Hỗ trợ cả hai key "filename" và "file_name" hoặc "source" gốc của Langchain
        raw_source = (
            doc.metadata.get("filename")
            or doc.metadata.get("file_name")
            or doc.metadata.get("source")
            or "Không rõ nguồn"
        )

        # Nếu source là một đường dẫn dài (C:\...\file.txt), chỉ trích xuất tên file
        if raw_source != "Không rõ nguồn" and ("/" in raw_source or "\\" in raw_source):
            file_name = os.path.basename(raw_source)
        else:
            file_name = raw_source

        # Bỏ qua các file rỗng
        if file_name.strip():
            sources.add(file_name)

    # Nếu set chỉ chứa mỗi chữ "Không rõ nguồn" thì không cần hiển thị
    if not sources or sources == {"Không rõ nguồn"}:
        return ""

    result = "\n\n📄 **Nguồn tham khảo:**\n"

    for source in sorted(sources):
        result += f"- {source}\n"

    return result