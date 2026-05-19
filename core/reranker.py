from sentence_transformers import (
    CrossEncoder
)

from utils.logger import logger

# ===================================================
# 🧠 RERANK MODEL
# ===================================================
rerank_model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

logger.info(
    "✅ Reranker model loaded"
)

# ===================================================
# 🧠 RERANK DOCUMENTS
# ===================================================
def rerank_documents(query, documents, top_k=5):

    if not documents:

        return []

    # ===================================================
    # 📄 QUERY-DOCUMENT PAIRS
    # ===================================================
    pairs = []

    for doc in documents:

        pairs.append(
            [
                query,
                doc.page_content
            ]
        )

    # ===================================================
    # 📊 PREDICT SCORES
    # ===================================================
    scores = rerank_model.predict(
        pairs
    )

    # ===================================================
    # 🔄 SORT
    # ===================================================
    ranked_results = sorted(

        zip(documents, scores),

        key=lambda x: x[1],

        reverse=True
    )

    # ===================================================
    # 📦 TOP RESULTS
    # ===================================================
    top_documents = [

        item[0]

        for item in ranked_results[:top_k]
    ]

    logger.info(
        f"🧠 Reranked top documents: {len(top_documents)}"
    )

    return top_documents