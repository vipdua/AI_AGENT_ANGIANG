from core.chunking import smart_chunk_documents
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from utils.logger import logger
from core.config import (
    CHROMA_DB_DIR,
    EMBEDDING_MODEL
)

# ===================================================
# ✂️ TEXT SPLITTER
# ===================================================
def split_documents(documents):
    chunks = smart_chunk_documents(documents)
    return chunks

# ===================================================
# 🧠 EMBEDDING MODEL
# ===================================================
def get_embedding_model():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return embeddings

# ===================================================
# 💾 CREATE VECTOR DATABASE
# ===================================================
def create_vector_database(documents):
    embeddings = get_embedding_model()
    vectorstore = Chroma(
        persist_directory=str(CHROMA_DB_DIR),
        embedding_function=embeddings
    )
    vectorstore.add_documents(documents)
    return vectorstore

# ===================================================
# 📂 LOAD VECTOR DATABASE
# ===================================================
def load_vector_database():
    embeddings = get_embedding_model()
    vectorstore = Chroma(
        persist_directory=str(CHROMA_DB_DIR),
        embedding_function=embeddings
    )
    return vectorstore

# ===================================================
# 🔍 CREATE RETRIEVER
# ===================================================
def create_retriever():
    vectorstore = load_vector_database()
    # 🚀 TỐI ƯU: Tăng k lên 15 để lấy lưới rộng hơn, 
    # nhường việc lọc từ khóa chính xác cho BM25 ở file hybrid_search.py
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 15}
    )
    return retriever

# ===================================================
# 🚀 INGEST DOCUMENTS
# ===================================================
def ingest_documents(documents):
    # ===================================================
    # ✂️ SPLIT DOCUMENTS
    # ===================================================
    chunks = split_documents(documents)

    for i, chunk in enumerate(chunks):
        logger.info(
            f"""
    CHUNK {i}

    CONTENT:
    {chunk.page_content[:300]}

    METADATA:
    {chunk.metadata}
    """
        )

    logger.info(f"📦 Tổng chunk cần nạp: {len(chunks)}")

    # ===================================================
    # 💾 VECTOR DATABASE
    # ===================================================
    create_vector_database(chunks)
    logger.info("✅ Đã nạp dữ liệu vào Vector Database thành công!")

# ===================================================
# 🗑️ DELETE DOCUMENTS BY SOURCE
# ===================================================
def delete_document_by_source(source):
    try:
        vectorstore = load_vector_database()
        vectorstore.delete(where={"source": source})
        logger.info(f"🗑️ Deleted old vectors: {source}")
    except Exception as e:
        logger.error(f"Delete vector error: {e}")