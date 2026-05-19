import requests

API_URL = "http://127.0.0.1:8000"

# ===================================================
# 🔒 HANDLE API RESPONSE
# ===================================================
def handle_response(response):

    try:

        data = response.json()

    except:

        return {

            "success": False,

            "message":
            "API Error"
        }

    return data

# ===================================================
# 🔐 AUTH HEADERS
# ===================================================
def get_headers(token):

    return {

        "Authorization":
        f"Bearer {token}"
    }

# ===================================================
# 🔐 LOGIN API
# ===================================================
def api_login(

    username,

    password
):

    response = requests.post(

        f"{API_URL}/login",

        json={

            "username": username,

            "password": password
        }
    )

    return handle_response( response )

# ===================================================
# 💬 CHAT API
# ===================================================
def api_chat(

    token,

    username,

    user_role,

    message
):

    response = requests.post(

        f"{API_URL}/chat",

        headers=get_headers(token),

        json={

            "username": username,

            "user_role": user_role,

            "message": message
        }
    )

    return handle_response( response )

# ===================================================
# 📊 SYSTEM STATS API
# ===================================================
def api_stats(token):

    response = requests.get(

        f"{API_URL}/stats",

        headers=get_headers(token)
    )

    return handle_response( response )

# ===================================================
# 👥 GET USERS
# ===================================================
def api_get_users(token):

    response = requests.get(

        f"{API_URL}/users",

        headers=get_headers(token)
    )

    return handle_response( response )

# ===================================================
# 👤 CREATE USER
# ===================================================
def api_create_user(

    token,

    username,

    password,

    role
):

    response = requests.post(

        f"{API_URL}/users/create",

        headers=get_headers(token),

        json={

            "username": username,

            "password": password,

            "role": role
        }
    )

    return handle_response( response )

# ===================================================
# 📜 GET AUDIT LOGS
# ===================================================
def api_get_audit_logs(token):

    response = requests.get(

        f"{API_URL}/audit-logs",

        headers=get_headers(token)
    )

    return handle_response( response )