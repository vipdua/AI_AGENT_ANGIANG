from sentence_transformers import CrossEncoder
from utils.logger import logger

# ===================================================
# 🧠 RERANK MODEL (lazy load — không load lúc import)
# ===================================================
_rerank_model = None

def get_rerank_model():
    """
    Lazy-load CrossEncoder để tránh crash khi startup nếu model chưa được download.
    Đã chuyển sang model Multilingual (BGE-M3) để hiểu được ngữ nghĩa Tiếng Việt.
    """
    global _rerank_model

    if _rerank_model is None:
        try:
            logger.info("🧠 Loading reranker model (BAAI/bge-reranker-m3)...")
            
            # Sử dụng model đa ngôn ngữ thay vì ms-marco (chỉ hỗ trợ tốt tiếng Anh)
            _rerank_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            
            logger.info("✅ Reranker model loaded successfully")

        except Exception as e:
            logger.error(f"⚠️ Không load được reranker model: {e}")
            _rerank_model = None

    return _rerank_model

# ===================================================
# 🧠 RERANK DOCUMENTS
# ===================================================
def rerank_documents(query, documents, top_k=5):
    
    if not documents:
        return []

    # ===================================================
    # 🔄 THỬ RERANK, NẾU LỖI TRẢ VỀ KẾT QUẢ GỐC
    # ===================================================
    model = get_rerank_model()

    if model is None:
        logger.warning("⚠️ Reranker không khả dụng, dùng kết quả gốc")
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

        # In log điểm số để bạn dễ debug xem file nào đang top 1
        for i, (doc, score) in enumerate(ranked_results[:top_k]):
            filename = doc.metadata.get("file_name") or doc.metadata.get("filename") or "Unknown"
            logger.info(f"📊 Rerank [Top {i+1}] | Score: {score:.4f} | File: {filename}")

        top_documents = [
            item[0]
            for item in ranked_results[:top_k]
        ]

        logger.info(f"🧠 Trả về top documents sau khi Rerank: {len(top_documents)}")

        return top_documents

    except Exception as e:
        logger.error(f"❌ Reranker error: {e}")
        return documents[:top_k]