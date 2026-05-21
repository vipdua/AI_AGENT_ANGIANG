from core.rag import (
    create_retriever
)

from core.reranker import (
    rerank_documents
)

from utils.logger import logger

# ===================================================
# 🔍 HYBRID SEARCH
# ===================================================
def hybrid_search(

    query,

    user_role
):

    retriever = create_retriever()

    docs = retriever.invoke(query)

    logger.info(
        f"📄 Retrieved docs: {len(docs)}"
    )

    # ===================================================
    # 🚀 DEBUG DOCS
    # ===================================================
    for i, doc in enumerate(docs):

        logger.info(
            f"""
DOC {i}

CONTENT:
{doc.page_content[:300]}

METADATA:
{doc.metadata}
"""
        )

    # ===================================================
    # 🚀 TEMP: SKIP RBAC FILTER
    # ===================================================
    filtered_docs = docs

    logger.info(
        f"🔐 Accessible docs: "
        f"{len(filtered_docs)}"
    )

    # ===================================================
    # 🚫 NO ACCESSIBLE DOCS
    # ===================================================
    if len(filtered_docs) == 0:

        return []

    # ===================================================
    # 🧠 RERANK
    # ===================================================
    reranked_docs = rerank_documents(

        query,

        filtered_docs
    )

    return reranked_docs