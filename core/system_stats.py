import os

from pathlib import Path

from core.config import (
    CHROMA_DB_DIR,
    DOCUMENTS_DIR,
    LLM_MODEL,
    EMBEDDING_MODEL
)

from core.ingestion_queue import (
    ingestion_queue
)

from core.failed_queue import (
    failed_files
)

from core.processing_state import (
    processing_files
)

from utils.logger import logger

# ===================================================
# 📄 COUNT DOCUMENT FILES
# ===================================================
def count_document_files():

    if not DOCUMENTS_DIR.exists():

        return 0

    total_files = 0

    for root, dirs, files in os.walk(
        DOCUMENTS_DIR
    ):

        total_files += len(files)

    return total_files

# ===================================================
# 📦 COUNT CHROMA FILES
# ===================================================
def count_chroma_files():

    if not CHROMA_DB_DIR.exists():

        return 0

    total_files = 0

    for root, dirs, files in os.walk(
        CHROMA_DB_DIR
    ):

        total_files += len(files)

    return total_files

# ===================================================
# 💾 GET DATABASE SIZE
# ===================================================
def get_database_size_mb():

    total_size = 0

    if not CHROMA_DB_DIR.exists():

        return 0

    for dirpath, dirnames, filenames in os.walk(
        CHROMA_DB_DIR
    ):

        for filename in filenames:

            file_path = Path(dirpath) / filename

            if file_path.exists():

                total_size += (
                    file_path.stat().st_size
                )

    size_mb = total_size / (1024 * 1024)

    return round(size_mb, 2)

# ===================================================
# 🧠 SYSTEM INFO
# ===================================================
def get_system_info():

    info = {

        "llm_model": LLM_MODEL,

        "embedding_model": EMBEDDING_MODEL,

        "document_files": (
            count_document_files()
        ),

        "chroma_files": (
            count_chroma_files()
        ),

        "database_size_mb": (
            get_database_size_mb()
        ),

        "queue_size":
        ingestion_queue.qsize(),

        "processing_files":
        len(processing_files),

        "failed_files":
        len(failed_files),
    }

    logger.info(
        "📊 System stats collected"
    )

    return info

# ===================================================
# 📋 FORMAT SYSTEM INFO
# ===================================================
def format_system_info():

    info = get_system_info()

    formatted = f"""
📊 THỐNG KÊ HỆ THỐNG

🧠 LLM:
{info["llm_model"]}

📦 Embedding:
{info["embedding_model"]}

📄 Tổng file tài liệu:
{info["document_files"]}

💾 File database:
{info["chroma_files"]}

🗂️ Kích thước database:
{info["database_size_mb"]} MB

📥 Queue size:
{info["queue_size"]}

⚙️ Processing files:
{info["processing_files"]}

❌ Failed files:
{info["failed_files"]}
"""

    return formatted