# ===================================================
# 📄 FORMAT SOURCES
# ===================================================
def format_sources(documents):

    sources = set()

    for doc in documents:

        file_name = doc.metadata.get(
            "file_name",
            "Không rõ nguồn"
        )

        sources.add(file_name)

    if not sources:

        return ""

    result = "\n\n📄 Nguồn tham khảo:\n"

    for source in sorted(sources):

        result += f"- {source}\n"

    return result