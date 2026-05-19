from database.db import (
    get_connection
)

from utils.logger import logger

# ===================================================
# 📜 WRITE AUDIT LOG
# ===================================================
def write_audit_log(

    username,

    action,

    details=""
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
INSERT INTO audit_logs (

    username,

    action,

    details
)
VALUES (?, ?, ?)
"""
        ,
        (
            username,

            action,

            details
        )
    )

    conn.commit()

    conn.close()

    logger.info(
        f"📜 Audit: {username} - {action}"
    )

# ===================================================
# 📋 GET AUDIT LOGS
# ===================================================
def get_audit_logs(

    limit=100
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        f"""
SELECT *
FROM audit_logs
ORDER BY id DESC
LIMIT {limit}
"""
    )

    logs = cursor.fetchall()

    conn.close()

    results = []

    for log in logs:

        results.append({

            "id": log["id"],

            "username": log["username"],

            "action": log["action"],

            "details": log["details"],

            "created_at": log["created_at"]
        })

    return results