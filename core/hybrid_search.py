from rank_bm25 import BM25Okapi
from utils.logger import logger
from core.reranker import rerank_documents

# ===================================================
# 🧠 BM25 INDEX CLASS
# ===================================================
class BM25Search:
    def __init__(self, documents):
        self.documents = documents
        self.texts = [doc.page_content for doc in documents]
        self.tokenized_texts = [text.lower().split() for text in self.texts]
        self.bm25 = BM25Okapi(self.tokenized_texts)
        logger.info("✅ BM25 index created for retrieved docs")

    # ===================================================
    # 🔍 SEARCH
    # ===================================================
    def search(self, query, top_k=5, department=None):
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)

        ranked_results = sorted(
            zip(self.documents, scores),
            key=lambda x: x[1],
            reverse=True
        )

        results = []
        # ===================================================
        # 🔒 FILTER RESULTS
        # ===================================================
        for doc, score in ranked_results:
            # ===================================================
            # 🏢 DEPARTMENT FILTER
            # ===================================================
            if department:
                if doc.metadata.get("department") != department:
                    continue

            results.append(doc)
            if len(results) >= top_k:
                break

        return results

# ===================================================
# 🔍 HYBRID SEARCH (Vector + BM25 + Rerank)
# ===================================================
def hybrid_search(query, user_role):
    from core.rag import create_retriever

    # 1. VECTOR SEARCH (Tìm kiếm theo ngữ nghĩa)
    retriever = create_retriever()
    vector_docs = retriever.invoke(query)
    logger.info(f"📄 Retrieved docs via Vector: {len(vector_docs)}")

    if not vector_docs:
        return []

    # 2. LOCAL BM25 ON RETRIEVED DOCS (Tìm kiếm chính xác từ khóa)
    # Dùng class BM25Search của bạn để lọc và sắp xếp lại tập kết quả từ Vector
    try:
        bm25_engine = BM25Search(vector_docs)
        # Giữ nguyên số lượng doc để không làm rớt tài liệu trước khi Rerank
        filtered_docs = bm25_engine.search(query, top_k=len(vector_docs))
        logger.info("✅ BM25 Keyword Filter applied successfully")
    except Exception as e:
        logger.error(f"⚠️ BM25 local fallback error: {e}")
        filtered_docs = vector_docs

    # ===================================================
    # 🚀 TEMP: SKIP RBAC FILTER (Chờ triển khai sau)
    # ===================================================
    logger.info(f"🔐 Accessible docs ready for Rerank: {len(filtered_docs)}")
    
    # Debug hiển thị các file trước khi Rerank
    for i, doc in enumerate(filtered_docs):
        filename = doc.metadata.get("filename", "Unknown")
        logger.info(f"   + Doc {i}: {filename}")

    if len(filtered_docs) == 0:
        return []

    # 3. RERANK BẰNG CROSS-ENCODER
    reranked_docs = rerank_documents(query, filtered_docs)

    return reranked_docs