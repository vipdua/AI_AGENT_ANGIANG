from core.chunking import (
    smart_chunk_documents
)

from langchain_huggingface import (
    HuggingFaceEmbeddings
)

from langchain_community.vectorstores import (
    Chroma
)

from core.hybrid_search import (
    BM25Search
)

from core.reranker import (
    rerank_documents
)

from core.permissions import (
    filter_accessible_documents
)

from utils.logger import logger

from core.config import (
    CHROMA_DB_DIR,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    RETRIEVAL_K
)

bm25_search_engine = None

# ===================================================
# ✂️ TEXT SPLITTER
# ===================================================
def split_documents(documents):

    chunks = smart_chunk_documents(
        documents
    )

    return chunks

# ===================================================
# 🧠 EMBEDDING MODEL
# ===================================================
def get_embedding_model():

    embeddings = HuggingFaceEmbeddings(

        model_name=EMBEDDING_MODEL
    )

    return embeddings

# ===================================================
# 💾 CREATE VECTOR DATABASE
# ===================================================
def create_vector_database(documents):

    embeddings = get_embedding_model()

    vectorstore = Chroma.from_documents(

        documents=documents,

        embedding=embeddings,

        persist_directory=str(CHROMA_DB_DIR)
    )

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

    retriever = vectorstore.as_retriever(

        search_kwargs={
            "k": RETRIEVAL_K
        }
    )

    return retriever

# ===================================================
# 🚀 INGEST DOCUMENTS
# ===================================================
def ingest_documents(documents):

    global bm25_search_engine

    # ===================================================
    # ✂️ SPLIT DOCUMENTS
    # ===================================================
    chunks = split_documents(documents)

    logger.info(
        f"📦 Tổng chunk: {len(chunks)}"
    )

    # ===================================================
    # 💾 VECTOR DATABASE
    # ===================================================
    create_vector_database(chunks)

    logger.info(
        "✅ Đã tạo Vector Database thành công!"
    )

    # ===================================================
    # 🔍 BM25 INDEX
    # ===================================================
    bm25_search_engine = BM25Search(
        chunks
    )

    logger.info(
        "✅ BM25 Search Engine Ready"
    )

# ===================================================
# 🔍 SEARCH DOCUMENTS
# ===================================================
def search_documents(query):

    retriever = create_retriever()

    results = retriever.invoke(query)

    return results

# ===================================================
# 🔍 HYBRID SEARCH
# ===================================================
def hybrid_search(

    query,

    user_role="nhan_vien"
):

    global bm25_search_engine

    # ===================================================
    # 🧠 VECTOR SEARCH
    # ===================================================
    retriever = create_retriever()

    vector_results = retriever.invoke(
        query
    )

    # ===================================================
    # 🔍 BM25 SEARCH
    # ===================================================
    keyword_results = []

    if bm25_search_engine:

        keyword_results = (
            bm25_search_engine.search(
                query
            )
        )

    # ===================================================
    # 🔄 MERGE RESULTS
    # ===================================================
    combined_results = []

    seen_contents = set()

    all_results = (
        vector_results + keyword_results
    )

    for doc in all_results:

        content = doc.page_content

        if content not in seen_contents:

            combined_results.append(doc)

            seen_contents.add(content)

    logger.info(
        f"🔍 Hybrid search results: {len(combined_results)}"
    )

    # ===================================================
    # 🔐 FILTER PERMISSIONS
    # ===================================================
    combined_results = (
        filter_accessible_documents(

            user_role,

            combined_results
        )
    )

    # ===================================================
    # 🧠 RERANK
    # ===================================================
    reranked_results = rerank_documents(

        query=query,

        documents=combined_results,

        top_k=5
    )

    return reranked_results[:3]