import shutil

from pathlib import Path

from datetime import datetime

from core.config import (
    CHROMA_DB_DIR
)

from utils.logger import logger

# ===================================================
# 📁 PATHS
# ===================================================
DATABASE_FILE = Path(
    "database/ai_agent.db"
)

BACKUP_DIR = Path(
    "backups"
)

# ===================================================
# 💾 CREATE BACKUP
# ===================================================
def create_backup():

    # ===================================================
    # 📂 CREATE BACKUP FOLDER
    # ===================================================
    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    backup_path = (
        BACKUP_DIR / timestamp
    )

    backup_path.mkdir(

        parents=True,

        exist_ok=True
    )

    # ===================================================
    # 💾 BACKUP SQLITE
    # ===================================================
    if DATABASE_FILE.exists():

        shutil.copy2(

            DATABASE_FILE,

            backup_path / "ai_agent.db"
        )

    # ===================================================
    # 🧠 BACKUP CHROMA DB
    # ===================================================
    if CHROMA_DB_DIR.exists():

        shutil.copytree(

            CHROMA_DB_DIR,

            backup_path / "chroma_db",

            dirs_exist_ok=True
        )

    logger.info(
        f"💾 Backup created: {backup_path}"
    )

    return str(backup_path)

# ===================================================
# 📋 GET BACKUPS
# ===================================================
def get_backups():

    if not BACKUP_DIR.exists():

        return []

    backups = []

    for folder in BACKUP_DIR.iterdir():

        if folder.is_dir():

            backups.append(folder.name)

    backups.sort(reverse=True)

    return backups