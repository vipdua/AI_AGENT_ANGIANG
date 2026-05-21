from langchain_huggingface import HuggingFaceEmbeddings

from core.config import EMBEDDING_MODEL

from utils.logger import logger

# ===================================================
# 🧠 EMBEDDING MODEL SINGLETON
# ===================================================
_embedding_model = None

# ===================================================
# 🧠 GET EMBEDDING MODEL
# ===================================================
def get_embedding_model():
    """
    Trả về embedding model singleton.
    Tránh load model nhiều lần.
    """

    global _embedding_model

    # ===================================================
    # 🚀 LOAD ONCE
    # ===================================================
    if _embedding_model is None:

        logger.info(
            f"🧠 Loading embedding model: "
            f"{EMBEDDING_MODEL}"
        )

        _embedding_model = HuggingFaceEmbeddings(

            model_name=EMBEDDING_MODEL,

            model_kwargs={
                "device": "cpu"
            },

            encode_kwargs={
                "normalize_embeddings": True
            }
        )

        logger.info(
            "✅ Embedding model loaded"
        )

    return _embedding_model