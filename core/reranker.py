from sentence_transformers import (
    CrossEncoder
)

from utils.logger import logger

# ===================================================
# 🧠 RERANK MODEL (lazy load — không load lúc import)
# ===================================================
_rerank_model = None

def get_rerank_model():
    """
    Lazy-load CrossEncoder để tránh crash khi startup
    nếu model chưa được download.
    """

    global _rerank_model

    if _rerank_model is None:

        try:

            logger.info("🧠 Loading reranker model...")

            _rerank_model = CrossEncoder(
                "cross-encoder/ms-marco-MiniLM-L-6-v2"
            )

            logger.info("✅ Reranker model loaded")

        except Exception as e:

            logger.error(
                f"⚠️ Không load được reranker model: {e}"
            )

            _rerank_model = None

    return _rerank_model

# ===================================================
# 🧠 RERANK DOCUMENTS
# ===================================================
def rerank_documents(
    query,
    documents,
    top_k=5
):

    if not documents:

        return []

    # ===================================================
    # 🔄 THỬ RERANK, NẾU LỖI TRẢ VỀ KẾT QUẢ GỐC
    # ===================================================
    model = get_rerank_model()

    if model is None:

        logger.warning(
            "⚠️ Reranker không khả dụng, dùng kết quả gốc"
        )

        return documents[:top_k]

    try:

        # ===================================================
        # 📄 QUERY-DOCUMENT PAIRS
        # ===================================================
        pairs = [
            [query, doc.page_content]
            for doc in documents
        ]

        # ===================================================
        # 📊 PREDICT SCORES
        # ===================================================
        scores = model.predict(pairs)

        # ===================================================
        # 🔄 SORT BY SCORE
        # ===================================================
        ranked_results = sorted(
            zip(documents, scores),
            key=lambda x: x[1],
            reverse=True
        )

        top_documents = [
            item[0]
            for item in ranked_results[:top_k]
        ]

        logger.info(
            f"🧠 Reranked top documents: {len(top_documents)}"
        )

        return top_documents

    except Exception as e:

        logger.error(f"❌ Reranker error: {e}")

        return documents[:top_k]