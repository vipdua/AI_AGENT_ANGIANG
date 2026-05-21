import os
import logging
import time
import warnings
from threading import Thread
from pathlib import Path

# ===================================================
# 🔇 SUPPRESS VERBOSE WARNINGS
# ===================================================
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("huggingface_hub").setLevel(logging.WARNING)
warnings.filterwarnings("ignore")

from fastapi import FastAPI, Depends, Request, UploadFile, File
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

from core.ai_agent import ask_ai
from core.auth import authenticate_user, create_user, get_all_users
from core.system_stats import get_system_info
from core.audit import get_audit_logs
from core.security import create_access_token, get_current_user, require_role
from core.config import DOCUMENTS_DIR
from utils.logger import logger
from core.loaders import load_single_file, load_documents_from_directory
from core.rag import ingest_documents
from core.memory import clear_user_memory
from core.folder_watcher import start_folder_watcher
from core.ingestion_worker import start_workers

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
    Path(watch_folder).mkdir(exist_ok=True)

    watcher_thread = Thread(
        target=start_folder_watcher,
        args=(watch_folder,),
        daemon=True
    )
    watcher_thread.start()
    logger.info(f"👀 Folder watcher started: {watch_folder}")

# ===================================================
# ⚡ RATE LIMITER
# ===================================================
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# ===================================================
# 📦 REQUEST MODELS
# ===================================================
class LoginRequest(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    username: str
    user_role: str
    message: str

class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str

class ClearMemoryRequest(BaseModel):
    username: str

class ScanDirectoryRequest(BaseModel):
    directory_path: str

# ===================================================
# 🏠 ROOT
# ===================================================
@app.get("/")
def root():
    return {"message": "AI Nội Bộ API đang hoạt động"}

# ===================================================
# 🔐 LOGIN API
# ===================================================
@app.post("/login")
@limiter.limit("5/minute")
def login(request: Request, data: LoginRequest):
    user = authenticate_user(data.username, data.password)

    if not user:
        return {
            "success": False,
            "message": "Sai tài khoản hoặc mật khẩu"
        }

    token = create_access_token({
        "username": user["username"],
        "role": user["role"]
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
def chat(request: Request, data: ChatRequest, current_user=Depends(get_current_user)):
    if not current_user:
        return {"success": False, "message": "Unauthorized"}

    try:
        response = ask_ai(
            user_question=data.message,
            username=data.username,
            user_role=data.user_role
        )
        return {"success": True, "response": response}
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        return {"success": False, "message": str(e)}

# ===================================================
# 🧹 CLEAR MEMORY API
# ===================================================
@app.post("/memory/clear")
@limiter.limit("10/minute")
def clear_memory(request: Request, data: ClearMemoryRequest, current_user=Depends(get_current_user)):
    if not current_user:
        return {"success": False, "message": "Unauthorized"}
        
    # Chỉ cho phép tự xóa bộ nhớ của mình, trừ khi là admin
    if current_user["username"] != data.username and current_user["role"] != "admin":
         return {"success": False, "message": "Forbidden"}
    
    try:
        clear_user_memory(data.username)
        return {"success": True, "message": "Đã xóa bộ nhớ trò chuyện"}
    except Exception as e:
        logger.error(f"❌ Memory clear error: {e}")
        return {"success": False, "message": str(e)}

# ===================================================
# 📂 SCAN DIRECTORY API
# ===================================================
@app.post("/documents/scan")
@limiter.limit("5/minute")
def scan_directory(request: Request, data: ScanDirectoryRequest, current_user=Depends(get_current_user)):
    if not current_user:
        return {"success": False, "message": "Unauthorized"}
        
    # Chỉ admin mới có quyền quét thư mục trên server
    if not require_role(current_user, ["admin"]):
        return {"success": False, "message": "Forbidden"}
    
    path = data.directory_path
    if not os.path.exists(path):
        return {"success": False, "message": "Đường dẫn thư mục không tồn tại trên server!"}
    
    try:
        documents = load_documents_from_directory(path)
        if len(documents) > 0:
            ingest_documents(documents)
            return {"success": True, "message": f"Đã nạp {len(documents)} tài liệu thành công!"}
        else:
            return {"success": False, "message": "Không tìm thấy tài liệu hợp lệ trong thư mục."}
    except Exception as e:
        logger.error(f"❌ Scan directory error: {e}")
        return {"success": False, "message": str(e)}

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
@limiter.limit("100/minute")
def users(request: Request, current_user=Depends(get_current_user)):
    if not current_user:
        return {"success": False, "message": "Unauthorized"}
    return {"success": True, "users": get_all_users()}

# ===================================================
# 📜 AUDIT LOGS
# ===================================================
@app.get("/audit-logs")
@limiter.limit("25/minute")
def audit_logs(request: Request, current_user=Depends(get_current_user)):
    if not current_user:
        return {"success": False, "message": "Unauthorized"}

    if not require_role(current_user, ["admin"]):
        return {"success": False, "message": "Forbidden"}

    logs = get_audit_logs()
    return {"success": True, "logs": logs}

# ===================================================
# 👤 CREATE USER
# ===================================================
@app.post("/users/create")
@limiter.limit("10/minute")
def create_new_user(request: Request, data: CreateUserRequest, current_user=Depends(get_current_user)):
    if not current_user:
        return {"success": False, "message": "Unauthorized"}

    if not require_role(current_user, ["admin"]):
        return {"success": False, "message": "Forbidden"}

    success = create_user(data.username, data.password, data.role)

    if not success:
        return {"success": False, "message": "Tạo user thất bại"}

    return {"success": True, "message": "Tạo user thành công"}

# ===================================================
# 📤 UPLOAD DOCUMENT
# ===================================================
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        # ===================================================
        # 📂 CREATE DIRECTORY
        # ===================================================
        os.makedirs(DOCUMENTS_DIR, exist_ok=True)
        save_path = DOCUMENTS_DIR / file.filename

        # ===================================================
        # 💾 SAVE FILE
        # ===================================================
        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"📤 Uploaded: {file.filename}")

        # ===================================================
        # 📄 LOAD DOCUMENT
        # ===================================================
        docs = load_single_file(save_path)
        logger.info(f"📄 Loaded docs: {len(docs)}")

        if not docs:
            return {"success": False, "message": "Không đọc được nội dung file"}

        # ===================================================
        # 🧠 INGEST
        # ===================================================
        ingest_documents(docs)
        logger.info(f"✅ Ingested: {file.filename}")

        return {"success": True, "filename": file.filename}

    except Exception as e:
        logger.error(f"❌ Upload ingest error: {e}")
        return {"success": False, "message": str(e)}