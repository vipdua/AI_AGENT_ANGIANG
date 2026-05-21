import os
import requests

# Lấy URL từ biến môi trường, nếu không có thì mặc định là localhost
API_URL = os.environ.get("API_URL", "http://localhost:8000")

# ===================================================
# ⏱️ TIMEOUT CONFIG (giây)
# ===================================================
CHAT_TIMEOUT = 180    # AI có thể cần nhiều thời gian
SCAN_TIMEOUT = 300    # Quét thư mục có thể tốn rất nhiều thời gian
DEFAULT_TIMEOUT = 10  # Các API khác

# ===================================================
# 🔒 HANDLE API RESPONSE
# ===================================================
def handle_response(response):
    try:
        data = response.json()
    except Exception:
        return {
            "success": False,
            "message": "Lỗi parse response từ API"
        }
    return data

# ===================================================
# 🔐 AUTH HEADERS
# ===================================================
def get_headers(token):
    return {
        "Authorization": f"Bearer {token}"
    }

# ===================================================
# 🔐 LOGIN API
# ===================================================
def api_login(username, password):
    try:
        response = requests.post(
            f"{API_URL}/login",
            json={
                "username": username,
                "password": password
            },
            timeout=DEFAULT_TIMEOUT
        )
        return handle_response(response)
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "❌ Không thể kết nối đến API Server. Hãy kiểm tra FastAPI có đang chạy không."
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "⏱️ API Server phản hồi quá chậm (timeout)."
        }

# ===================================================
# 💬 CHAT API
# ===================================================
def api_chat(token, username, user_role, message):
    try:
        response = requests.post(
            f"{API_URL}/chat",
            headers=get_headers(token),
            json={
                "username": username,
                "user_role": user_role,
                "message": message
            },
            timeout=CHAT_TIMEOUT
        )
        return handle_response(response)
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "❌ Không thể kết nối đến API Server. Hãy kiểm tra FastAPI có đang chạy không."
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "⏱️ AI phản hồi quá chậm (timeout 3 phút). Hãy thử lại hoặc kiểm tra Ollama."
        }

# ===================================================
# 📊 SYSTEM STATS API
# ===================================================
def api_stats(token):
    try:
        response = requests.get(
            f"{API_URL}/stats",
            headers=get_headers(token),
            timeout=DEFAULT_TIMEOUT
        )
        return handle_response(response)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return {
            "success": False,
            "message": "❌ Không thể kết nối đến API Server."
        }

# ===================================================
# 🧹 CLEAR MEMORY API
# ===================================================
def api_clear_memory(token, username):
    try:
        response = requests.post(
            f"{API_URL}/memory/clear",
            headers=get_headers(token),
            json={"username": username},
            timeout=DEFAULT_TIMEOUT
        )
        return handle_response(response)
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "❌ Không thể kết nối đến API Server."
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "⏱️ API Server phản hồi quá chậm (timeout)."
        }

# ===================================================
# 📂 SCAN DIRECTORY API
# ===================================================
def api_scan_directory(token, directory_path):
    try:
        response = requests.post(
            f"{API_URL}/documents/scan",
            headers=get_headers(token),
            json={"directory_path": directory_path},
            timeout=SCAN_TIMEOUT
        )
        return handle_response(response)
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "❌ Không thể kết nối đến API Server."
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "⏱️ Quét thư mục quá chậm (timeout 5 phút)."
        }

# ===================================================
# 👥 GET USERS
# ===================================================
def api_get_users(token):
    response = requests.get(
        f"{API_URL}/users",
        headers=get_headers(token)
    )
    return handle_response(response)

# ===================================================
# 👤 CREATE USER
# ===================================================
def api_create_user(token, username, password, role):
    response = requests.post(
        f"{API_URL}/users/create",
        headers=get_headers(token),
        json={
            "username": username,
            "password": password,
            "role": role
        }
    )
    return handle_response(response)

# ===================================================
# 📜 GET AUDIT LOGS
# ===================================================
def api_get_audit_logs(token):
    response = requests.get(
        f"{API_URL}/audit-logs",
        headers=get_headers(token)
    )
    return handle_response(response)