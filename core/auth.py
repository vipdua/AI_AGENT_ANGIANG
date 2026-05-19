import bcrypt

from database.db import (
    get_connection
)

from core.audit import (
    write_audit_log
)

from utils.logger import logger

# ===================================================
# 🔐 HASH PASSWORD
# ===================================================
def hash_password(password):

    hashed = bcrypt.hashpw(

        password.encode(),

        bcrypt.gensalt()
    )

    return hashed.decode()

# ===================================================
# 🔑 VERIFY PASSWORD
# ===================================================
def verify_password(

    password,

    hashed_password
):

    return bcrypt.checkpw(

        password.encode(),

        hashed_password.encode()
    )

# ===================================================
# 🔐 AUTHENTICATE USER
# ===================================================
def authenticate_user(

    username,

    password
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
SELECT *
FROM users
WHERE username = ?
"""
        ,
        (username,)
    )

    user = cursor.fetchone()

    conn.close()

    # ===================================================
    # ❌ USER NOT FOUND
    # ===================================================
    if not user:

        logger.warning(
            f"❌ Login failed: {username}"
        )

        write_audit_log(

            username,

            "LOGIN_FAILED"
        )

        return None

    # ===================================================
    # ❌ WRONG PASSWORD
    # ===================================================
    if not verify_password(

        password,

        user["password"]
    ):

        logger.warning(
            f"❌ Wrong password: {username}"
        )

        return None

    # ===================================================
    # ✅ LOGIN SUCCESS
    # ===================================================
    logger.info(
        f"✅ Login success: {username}"
    )

    write_audit_log(

        username,

        "LOGIN_SUCCESS"
    )

    return {

        "id": user["id"],

        "username": user["username"],

        "role": user["role"]
    }

# ===================================================
# 👤 CREATE USER
# ===================================================
def create_user(

    username,

    password,

    role
):

    conn = get_connection()

    cursor = conn.cursor()

    hashed_password = (
        hash_password(password)
    )

    try:

        cursor.execute(
            """
INSERT INTO users (
    username,
    password,
    role
)
VALUES (?, ?, ?)
"""
            ,
            (
                username,
                hashed_password,
                role
            )
        )

        conn.commit()

        logger.info(
            f"👤 Created user: {username}"
        )

        return True

    except Exception as e:

        logger.error(
            f"❌ Create user failed: {e}"
        )

        return False

    finally:

        conn.close()

# ===================================================
# 👥 GET ALL USERS
# ===================================================
def get_all_users():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
SELECT id, username, role
FROM users
ORDER BY id ASC
"""
    )

    users = cursor.fetchall()

    conn.close()

    results = []

    for user in users:

        results.append({

            "id": user["id"],

            "username": user["username"],

            "role": user["role"]
        })

    return results