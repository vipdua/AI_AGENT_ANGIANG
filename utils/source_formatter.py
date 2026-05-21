# ===================================================
# 📄 FORMAT SOURCES
# ===================================================
def format_sources(documents):

    if not documents:
        return ""

    sources = set()

    for doc in documents:

        # Hỗ trợ cả hai key "filename" và "file_name"
        file_name = (
            doc.metadata.get("filename")
            or doc.metadata.get("file_name")
            or doc.metadata.get("source")
            or "Không rõ nguồn"
        )

        sources.add(file_name)

    if not sources:

        return ""

    result = "\n\n📄 **Nguồn tham khảo:**\n"

    for source in sorted(sources):

        result += f"- {source}\n"

    return result