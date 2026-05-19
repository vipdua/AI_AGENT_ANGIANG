import logging

from pathlib import Path

from core.config import LOG_DIR

# ===================================================
# 📁 CREATE LOG DIRECTORY
# ===================================================
LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# ===================================================
# 📄 LOG FILE
# ===================================================
LOG_FILE = LOG_DIR / "ai_agent.log"

# ===================================================
# ⚙️ LOGGER CONFIG
# ===================================================
logging.basicConfig(

    level=logging.INFO,

    format="""
%(asctime)s
[%(levelname)s]
%(message)s
""",

    handlers=[

        logging.FileHandler(
            LOG_FILE,
            encoding="utf-8"
        ),

        logging.StreamHandler()
    ]
)

# ===================================================
# 🚀 LOGGER
# ===================================================
logger = logging.getLogger("AI_AGENT")