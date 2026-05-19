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
    # 🔐 ROLE FILTER
    # ===================================================
    filtered_docs = []

    for doc in docs:

        department = doc.metadata.get(

            "department",

            "all"
        )

        # ===================================================
        # 🌍 PUBLIC DOCUMENT
        # ===================================================
        if department == "all":

            filtered_docs.append(doc)

            continue

        # ===================================================
        # 👑 ADMIN ACCESS ALL
        # ===================================================
        if user_role == "admin":

            filtered_docs.append(doc)

            continue

        # ===================================================
        # 🔐 ROLE MATCH
        # ===================================================
        if department == user_role:

            filtered_docs.append(doc)

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