import os

import logging

# ===================================================
# 🔇 SUPPRESS VERBOSE WARNINGS
# (transformers __path__ warnings không ảnh hưởng chức năng)
# ===================================================
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("huggingface_hub").setLevel(logging.WARNING)

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

import time

from fastapi import UploadFile, File

from core.config import (
    DOCUMENTS_DIR
)

from utils.logger import logger

from core.loaders import (
    load_single_file
)

from core.rag import (
    ingest_documents
)

import warnings

from threading import Thread

from core.folder_watcher import (
    start_folder_watcher
)

from core.ingestion_worker import (
    start_workers
)

from pathlib import Path

warnings.filterwarnings("ignore")

# ===================================================
# 🚀 FASTAPI APP
# ===================================================
app = FastAPI(

    title="AI Nội Bộ API",

    version="1.0.0"
)

# ===================================================
# 🚀 START BACKGROUND SERVICES
# ===================================================
@app.on_event("startup")
async def startup_event():

    # ===================================================
    # 👷 START WORKERS
    # ===================================================
    start_workers(4)

    # ===================================================
    # 👀 START FOLDER WATCHER
    # ===================================================
    watch_folder = str(DOCUMENTS_DIR)

    Path(watch_folder).mkdir(
        exist_ok=True
    )

    watcher_thread = Thread(

        target=start_folder_watcher,

        args=(watch_folder,),

        daemon=True
    )

    watcher_thread.start()

    logger.info(
        f"👀 Folder watcher started: "
        f"{watch_folder}"
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
# 💬 CHAT API
# ===================================================
@app.post("/chat")
@limiter.limit("20/minute")
def chat( request: Request, data: ChatRequest, current_user=Depends( get_current_user ) ):

    # ===================================================
    # 🔒 AUTHENTICATION CHECK
    # ===================================================
    if not current_user:

        return {

            "success": False,

            "message":
            "Unauthorized"
        }

    # ===================================================
    # ✅ ALL AUTHENTICATED USERS CAN CHAT
    # (admin, nhan_vien, hr, finance, etc.)
    # ===================================================
    try:

        response = ask_ai(

            user_question=data.message,

            username=data.username,

            user_role=data.user_role
        )

        return {

            "success": True,

            "response": response
        }

    except Exception as e:

        logger.error(f"❌ Chat error: {e}")

        return {

            "success": False,

            "message": str(e)
        }

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

    try:

        # ===================================================
        # 📂 CREATE DIRECTORY
        # ===================================================
        os.makedirs(
            DOCUMENTS_DIR,
            exist_ok=True
        )

        save_path = (
            DOCUMENTS_DIR / file.filename
        )

        # ===================================================
        # 💾 SAVE FILE
        # ===================================================
        with open(save_path, "wb") as f:

            content = await file.read()

            f.write(content)

        logger.info(
            f"📤 Uploaded: {file.filename}"
        )

        # ===================================================
        # 📄 LOAD DOCUMENT
        # ===================================================
        docs = load_single_file(
            save_path
        )

        logger.info(
            f"📄 Loaded docs: {len(docs)}"
        )

        # ===================================================
        # 🚫 NO DOCS
        # ===================================================
        if not docs:

            return {

                "success": False,

                "message":
                "Không đọc được nội dung file"
            }

        # ===================================================
        # 🧠 INGEST
        # ===================================================
        ingest_documents(docs)

        logger.info(
            f"✅ Ingested: {file.filename}"
        )

        return {

            "success": True,

            "filename": file.filename
        }

    except Exception as e:

        logger.error(
            f"❌ Upload ingest error: {e}"
        )

        return {

            "success": False,

            "message": str(e)
        }