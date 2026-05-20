from collections import deque

from utils.logger import logger

# ===================================================
# 🧠 SINGLE MEMORY
# ===================================================
class ConversationMemory:

    def __init__(self, max_messages=10):

        self.messages = deque(
            maxlen=max_messages
        )

    # ===================================================
    # ➕ ADD MESSAGE
    # ===================================================
    def add_message(

        self,

        role,

        content
    ):

        self.messages.append({

            "role": role,

            "content": content
        })

    # ===================================================
    # 📜 GET HISTORY
    # ===================================================
    def get_history(

        self,

        limit=10
    ):

        history = []

        recent_messages = list(
            self.messages
        )[-limit:]

        for msg in recent_messages:

            role = msg["role"]

            content = msg["content"]

            history.append(
                f"{role}: {content}"
            )

        return "\n".join(history)

    # ===================================================
    # 🗑️ CLEAR
    # ===================================================
    def clear(self):

        self.messages.clear()

    # ===================================================
    # 📊 MEMORY SIZE
    # ===================================================
    def size(self):

        return len(self.messages)

# ===================================================
# 👥 USER MEMORIES
# ===================================================
user_memories = {}

# ===================================================
# 🧠 GET USER MEMORY
# ===================================================
def get_user_memory(username):

    if username not in user_memories:

        user_memories[username] = (
            ConversationMemory()
        )

        logger.info(
            f"🧠 Created memory for {username}"
        )

    return user_memories[username]

# ===================================================
# 🗑️ CLEAR USER MEMORY
# ===================================================
def clear_user_memory(username):

    if username in user_memories:

        user_memories[username].clear()

        logger.info(
            f"🗑️ Cleared memory for {username}"
        )