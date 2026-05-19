from database.db import (
    get_connection
)

# ===================================================
# 🚀 CREATE TABLES
# ===================================================
def initialize_database():

    conn = get_connection()

    cursor = conn.cursor()

    # ===================================================
    # 👤 USERS TABLE
    # ===================================================
    cursor.execute(
        """
CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT UNIQUE NOT NULL,

    password TEXT NOT NULL,

    role TEXT NOT NULL
)
"""
    )

    # ===================================================
    # 📜 AUDIT LOGS
    # ===================================================
    cursor.execute(
        """
CREATE TABLE IF NOT EXISTS audit_logs (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT,

    action TEXT,

    details TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
    )

    # ===================================================
    # 💾 SAVE
    # ===================================================
    conn.commit()

    conn.close()

    print(
        "✅ Database initialized"
    )

# ===================================================
# 🚀 RUN
# ===================================================
if __name__ == "__main__":

    initialize_database()