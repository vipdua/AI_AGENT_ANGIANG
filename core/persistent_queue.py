import sqlite3

# ===================================================
# ➕ ADD TASK
# ===================================================
def add_task(

    action,

    file_path
):

    conn = sqlite3.connect(
        "queue.db"
    )

    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO ingestion_queue (

        action,
        file_path

    )

    VALUES (?, ?)

    """, (

        action,
        file_path
    ))

    conn.commit()

    conn.close()

# ===================================================
# 📥 GET NEXT TASK
# ===================================================
def get_next_task():

    conn = sqlite3.connect(
        "queue.db"
    )

    cursor = conn.cursor()

    cursor.execute("""

    SELECT id, action, file_path

    FROM ingestion_queue

    WHERE status='pending'

    ORDER BY id ASC

    LIMIT 1

    """)

    task = cursor.fetchone()

    if task:

        cursor.execute("""

        UPDATE ingestion_queue

        SET status='processing'

        WHERE id=?

        """, (task[0],))

        conn.commit()

    conn.close()

    return task

# ===================================================
# ✅ COMPLETE TASK
# ===================================================
def complete_task(task_id):

    conn = sqlite3.connect(
        "queue.db"
    )

    cursor = conn.cursor()

    cursor.execute("""

    UPDATE ingestion_queue

    SET status='done'

    WHERE id=?

    """, (task_id,))

    conn.commit()

    conn.close()