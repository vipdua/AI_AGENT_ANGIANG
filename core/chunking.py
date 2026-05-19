import re

from langchain_core.documents import Document

from utils.logger import logger

from core.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP
)

# ===================================================
# 📑 SPLIT BY HEADINGS
# ===================================================
def split_by_headings(text):

    pattern = r"(Điều\s+\d+|Chương\s+\w+|Mục\s+\d+)"

    parts = re.split(pattern, text)

    chunks = []

    current_chunk = ""

    for part in parts:

        if not part.strip():

            continue

        # ===================================================
        # 📑 DETECT HEADING
        # ===================================================
        if re.match(pattern, part):

            if current_chunk:

                chunks.append(current_chunk.strip())

            current_chunk = part

        else:

            current_chunk += "\n" + part

    if current_chunk:

        chunks.append(current_chunk.strip())

    return chunks

# ===================================================
# ✂️ SPLIT LARGE CHUNK
# ===================================================
def split_large_chunk(text):

    chunks = []

    start = 0

    while start < len(text):

        end = start + CHUNK_SIZE

        chunk = text[start:end]

        chunks.append(chunk)

        start += (
            CHUNK_SIZE - CHUNK_OVERLAP
        )

    return chunks

# ===================================================
# 🧠 SMART CHUNK DOCUMENT
# ===================================================
def smart_chunk_document(document):

    text = document.page_content

    metadata = document.metadata

    heading_chunks = split_by_headings(
        text
    )

    final_chunks = []

    for chunk in heading_chunks:

        # ===================================================
        # 📦 SMALL ENOUGH
        # ===================================================
        if len(chunk) <= CHUNK_SIZE:

            final_chunks.append(

                Document(
                    page_content=chunk,
                    metadata=metadata.copy()
                )
            )

        # ===================================================
        # ✂️ TOO LARGE
        # ===================================================
        else:

            smaller_chunks = split_large_chunk(
                chunk
            )

            for small_chunk in smaller_chunks:

                final_chunks.append(

                    Document(
                        page_content=small_chunk,
                        metadata=metadata.copy()
                    )
                )

    logger.info(
        f"📦 Smart chunks created: {len(final_chunks)}"
    )

    return final_chunks

# ===================================================
# 🚀 CHUNK ALL DOCUMENTS
# ===================================================
def smart_chunk_documents(documents):

    all_chunks = []

    for document in documents:

        chunks = smart_chunk_document(
            document
        )

        all_chunks.extend(chunks)

    logger.info(
        f"📚 Total smart chunks: {len(all_chunks)}"
    )

    return all_chunks