from pathlib import Path

# ===================================================
# 📁 BASE DIRECTORY
# ===================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ===================================================
# 📂 DATA DIRECTORIES
# ===================================================
DATA_DIR = BASE_DIR / "data"

DOCUMENTS_DIR = DATA_DIR / "documents"

PROCESSED_DIR = DATA_DIR / "processed"

UPLOAD_DIR = DATA_DIR / "uploads"

# ===================================================
# 💾 VECTOR DATABASE
# ===================================================
CHROMA_DB_DIR = BASE_DIR / "chroma_db"

# ===================================================
# 🧠 LLM MODEL
# ===================================================
LLM_MODEL = "ollama/qwen2.5:7b"

# ===================================================
# 🧠 EMBEDDING MODEL
# ===================================================
EMBEDDING_MODEL = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

# ===================================================
# ✂️ CHUNKING CONFIG
# ===================================================
CHUNK_SIZE = 1000

CHUNK_OVERLAP = 200

# ===================================================
# 🔍 RETRIEVAL CONFIG
# ===================================================
RETRIEVAL_K = 5

# ===================================================
# 📄 SUPPORTED FILE TYPES
# ===================================================
SUPPORTED_FILE_TYPES = [
    ".txt",
    ".pdf",
    ".docx"
]

# ===================================================
# 📋 LOGGING
# ===================================================
LOG_DIR = BASE_DIR / "logs"

# ===================================================
# ⚡ CREATE DIRECTORIES
# ===================================================
def create_directories():

    directories = [

        DATA_DIR,

        DOCUMENTS_DIR,

        PROCESSED_DIR,

        UPLOAD_DIR,

        CHROMA_DB_DIR,

        LOG_DIR
    ]

    for directory in directories:

        directory.mkdir(
            parents=True,
            exist_ok=True
        )