import shutil
import streamlit as st

from core.system_stats import (
    format_system_info
)

from core.memory import (
    user_memories
)

from core.config import (
    CHROMA_DB_DIR
)

from api.client import (

    api_get_users,

    api_create_user
)

from api.client import (
    api_get_audit_logs
)

from core.backup import (

    create_backup,

    get_backups
)

from utils.logger import logger

# ===================================================
# 📊 ADMIN PANEL
# ===================================================
def render_admin_panel():

    st.markdown("---")

    st.subheader("🛠️ Admin Panel")

    # ===================================================
    # 📊 SYSTEM STATS
    # ===================================================
    with st.expander(
        "📊 Thống kê hệ thống",
        expanded=False
    ):

        system_info = format_system_info()

        st.text(system_info)

    # ===================================================
    # 🧠 MEMORY MANAGEMENT
    # ===================================================
    with st.expander(
        "🧠 User Memories",
        expanded=False
    ):

        st.write(
            f"👥 Active memories: "
            f"{len(user_memories)}"
        )

        if len(user_memories) > 0:

            for username in user_memories:

                st.caption(
                    f"🧠 {username}"
                )

        else:

            st.info(
                "Chưa có memory user nào"
            )

    # ===================================================
    # 💾 DATABASE MANAGEMENT
    # ===================================================
    with st.expander(
        "💾 Vector Database",
        expanded=False
    ):

        st.warning(
            "⚠️ Hành động này không thể hoàn tác"
        )

        if st.button(
            "🔥 Xóa Chroma Database",
            use_container_width=True
        ):

            try:

                if CHROMA_DB_DIR.exists():

                    shutil.rmtree(
                        CHROMA_DB_DIR
                    )

                    st.success(
                        "✅ Đã xóa database"
                    )

                    logger.info(
                        "🔥 Chroma DB deleted"
                    )

                else:

                    st.info(
                        "Database không tồn tại"
                    )

            except Exception as e:

                st.error(
                    f"Lỗi: {e}"
                )

    # ===================================================
    # 📜 LOG VIEWER
    # ===================================================
    with st.expander(
        "📜 System Logs",
        expanded=False
    ):

        try:

            with open(

                "logs/ai_agent.log",

                "r",

                encoding="utf-8"

            ) as f:

                logs = f.read()

            st.text_area(

                "Logs",

                logs[-5000:],

                height=300
            )

        except Exception as e:

            st.error(
                f"Không đọc được logs: {e}"
            )

    # ===================================================
    # 📜 AUDIT LOGS
    # ===================================================
    with st.expander(
        "📜 Audit Logs",
        expanded=False
    ):

        result = api_get_audit_logs(

            st.session_state.token
        )

        if result["success"]:

            logs = result["logs"]

            if len(logs) == 0:

                st.info(
                    "Chưa có audit logs"
                )

            else:

                for log in logs:

                    st.markdown(
                        f"""
    ### 👤 {log['username']}

    - 📌 Action:
    {log['action']}

    - 📝 Details:
    {log['details']}

    - 🕒 Time:
    {log['created_at']}
    """
                    )

    # ===================================================
    # 💾 BACKUP SYSTEM
    # ===================================================
    with st.expander(
        "💾 Backup System",
        expanded=False
    ):

        # ===================================================
        # 🚀 CREATE BACKUP
        # ===================================================
        if st.button(
            "💾 Tạo Backup",
            use_container_width=True
        ):

            backup_path = create_backup()

            st.success(
                f"✅ Backup thành công:\n{backup_path}"
            )

        st.markdown("---")

        # ===================================================
        # 📋 BACKUP LIST
        # ===================================================
        backups = get_backups()

        if len(backups) == 0:

            st.info(
                "Chưa có backup"
            )

        else:

            st.subheader(
                "📦 Danh sách backup"
            )

            for backup in backups:

                st.caption(
                    f"📁 {backup}"
                )

    # ===================================================
    # 👥 USER MANAGEMENT
    # ===================================================
    with st.expander(
        "👥 User Management",
        expanded=False
    ):

        # ===================================================
        # 📋 USER LIST
        # ===================================================
        result = api_get_users(

            st.session_state.token
        )

        if result["success"]:

            users = result["users"]

            for user in users:

                st.caption(
                    f"""
    👤 {user['username']}
    ({user['role']})
    """
                )

        st.markdown("---")

        # ===================================================
        # ➕ CREATE USER
        # ===================================================
        st.subheader("➕ Tạo User")

        new_username = st.text_input(
            "Username"
        )

        new_password = st.text_input(
            "Password",
            type="password"
        )

        new_role = st.selectbox(

            "Role",

            [

                "admin",

                "nhan_vien",

                "tai_chinh",

                "nhan_su"
            ]
        )

        if st.button(
            "👤 Tạo User",
            use_container_width=True
        ):

            create_result = api_create_user(
                st.session_state.token,

                new_username,

                new_password,

                new_role
            )

            if create_result["success"]:

                st.success(
                    "✅ Tạo user thành công"
                )

                st.rerun()

            else:

                st.error(
                    create_result["message"]
                )