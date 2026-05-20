import sqlite3

# ===================================================
# 📦 CREATE QUEUE TABLE
# ===================================================
def init_queue_db():

    conn = sqlite3.connect(
        "queue.db"
    )

    cursor = conn.cursor()

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS ingestion_queue (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        action TEXT,

        file_path TEXT,

        status TEXT DEFAULT 'pending',

        created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP
    )

    """)

    conn.commit()

    conn.close()