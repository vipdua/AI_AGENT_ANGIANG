import sqlite3

from pathlib import Path

# ===================================================
# 📁 DATABASE PATH
# ===================================================
DATABASE_DIR = Path("database")

DATABASE_DIR.mkdir(
    exist_ok=True
)

DATABASE_PATH = (
    DATABASE_DIR / "ai_agent.db"
)

# ===================================================
# 🔌 GET CONNECTION
# ===================================================
def get_connection():

    conn = sqlite3.connect(
        DATABASE_PATH
    )

    conn.row_factory = (
        sqlite3.Row
    )

    return conn