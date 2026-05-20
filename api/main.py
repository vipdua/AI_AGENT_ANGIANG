from fastapi import FastAPI

from pydantic import BaseModel

from core.ai_agent import ask_ai

from core.auth import (
    authenticate_user
)

from core.system_stats import (
    get_system_info
)

from core.auth import (

    authenticate_user,

    create_user,

    get_all_users
)

from core.audit import (
    get_audit_logs
)

from core.security import (
    create_access_token
)

from fastapi import (

    FastAPI,

    Depends
)

from core.security import (
    create_access_token,
    get_current_user,
    require_role
)

from slowapi import Limiter

from slowapi.util import (
    get_remote_address
)

from slowapi.errors import (
    RateLimitExceeded
)

from slowapi.middleware import (
    SlowAPIMiddleware
)

from fastapi import Request

from fastapi.responses import (
    StreamingResponse
)

import time

from fastapi import UploadFile, File

from core.config import (
    DOCUMENTS_DIR
)

from utils.logger import logger

# ===================================================
# 🚀 FASTAPI APP
# ===================================================
app = FastAPI(

    title="AI Nội Bộ API",

    version="1.0.0"
)

# ===================================================
# ⚡ RATE LIMITER
# ===================================================
limiter = Limiter(

    key_func=get_remote_address
)

app.state.limiter = limiter

app.add_middleware(
    SlowAPIMiddleware
)

# ===================================================
# 📦 REQUEST MODELS
# ===================================================
class LoginRequest(BaseModel):

    username: str

    password: str

# ===================================================
# 💬 CHAT REQUEST
# ===================================================
class ChatRequest(BaseModel):

    username: str

    user_role: str

    message: str

# ===================================================
# 👤 CREATE USER REQUEST
# ===================================================
class CreateUserRequest(BaseModel):

    username: str

    password: str

    role: str

# ===================================================
# 🏠 ROOT
# ===================================================
@app.get("/")
def root():

    return {

        "message":
        "AI Nội Bộ API đang hoạt động"
    }

# ===================================================
# 🔐 LOGIN API
# ===================================================
@app.post("/login")
@limiter.limit("5/minute")
def login(

    request: Request,

    data: LoginRequest
):

    user = authenticate_user(

        data.username,

        data.password
    )

    if not user:

        return {

            "success": False,

            "message":
            "Sai tài khoản hoặc mật khẩu"
        }

    token = create_access_token({

        "username":
        user["username"],

        "role":
        user["role"]
    })

    return {

        "success": True,

        "user": user,

        "token": token
    }

# ===================================================
# 🌊 STREAM RESPONSE
# ===================================================
def stream_text(text):

    for word in text.split():

        yield f"data: {word} \n\n"

        time.sleep(0.03)

# ===================================================
# 💬 CHAT API
# ===================================================
@app.post("/chat")
@limiter.limit("20/minute")
def chat( request: Request, data: ChatRequest, current_user=Depends( get_current_user ) ):

    if not current_user:

        return {

            "success": False,

            "message":
            "Unauthorized"
        }

    if not require_role(

        current_user,

        ["admin"]
    ):

        return {

            "success": False,

            "message":
            "Forbidden"
        }

    response = ask_ai(

        user_question=data.message,

        username=data.username,

        user_role=data.user_role
    )

    return StreamingResponse(

        stream_text(response),

        media_type="text/event-stream"
    )

# ===================================================
# 📊 SYSTEM STATS API
# ===================================================
@app.get("/stats")
def stats():

    return get_system_info()

# ===================================================
# 👥 GET USERS
# ===================================================
@app.get("/users")
@limiter.limit("5/minute")
def users(request: Request, current_user=Depends( get_current_user ) ):

    if not current_user:

        return {

            "success": False,

            "message":
            "Unauthorized"
        }

    return {

        "success": True,

        "users": get_all_users()
    }

# ===================================================
# 📜 AUDIT LOGS
# ===================================================
@app.get("/audit-logs")
@limiter.limit("25/minute")
def audit_logs(request: Request, current_user=Depends( get_current_user ) ):

        if not current_user:

            return {

                "success": False,

                "message":
                "Unauthorized"
            }

        if not require_role(

            current_user,

            ["admin"]
        ):

            return {

                "success": False,

                "message":
                "Forbidden"
            }

        logs = get_audit_logs()

        return {

            "success": True,

            "logs": logs
        }

# ===================================================
# 👤 CREATE USER
# ===================================================
@limiter.limit("10/minute")
@app.post("/users/create")
def create_new_user(request: Request, data: CreateUserRequest, current_user=Depends( get_current_user ) ):

    if not current_user:

        return {

            "success": False,

            "message":
            "Unauthorized"
        }

    if not require_role(

        current_user,

        ["admin"]
    ):

        return {

            "success": False,

            "message":
            "Forbidden"
        }

    success = create_user(

        data.username,

        data.password,

        data.role
    )

    if not success:

        return {

            "success": False,

            "message":
            "Tạo user thất bại"
        }

    return {

        "success": True,

        "message":
        "Tạo user thành công"
    }

# ===================================================
# 📤 UPLOAD DOCUMENT
# ===================================================
@app.post("/upload")
async def upload_document(

    file: UploadFile = File(...)
):

    save_path = (
        DOCUMENTS_DIR / file.filename
    )

    with open(save_path, "wb") as f:

        content = await file.read()

        f.write(content)

    logger.info(
        f"📤 Uploaded: {file.filename}"
    )

    return {

        "success": True,

        "filename":
        file.filename
    }