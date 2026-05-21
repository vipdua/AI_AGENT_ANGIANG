import os
import streamlit as st
import requests

from api.client import ( 
    api_login, 
    api_chat, 
    api_stats,
    api_clear_memory,      # Thêm mới
    api_scan_directory,    # Thêm mới
    API_URL                # Lấy API URL chung
)

# KHÔNG import thẳng từ core/ nữa để tránh lỗi khóa DB và sai kiến trúc
from core.admin_panel import render_admin_panel

# ===================================================
# ⚙️ PAGE CONFIG
# ===================================================
st.set_page_config(
    page_title="AI Agent Nội Bộ",
    page_icon="🏢",
    layout="centered"
)

# ===================================================
# 🎨 LOAD CSS
# ===================================================
def load_css(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("styles/main.css")

# ===================================================
# 🧠 SESSION STATE
# ===================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "lich_su_cuoc_tro_chuyen" not in st.session_state:
    st.session_state.lich_su_cuoc_tro_chuyen = []
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

# ===================================================
# 🔒 LOGOUT USER
# ===================================================
def logout_user():
    if st.session_state.user and st.session_state.token:
        username = st.session_state.user["username"]
        # Đã sửa: Gọi API thay vì import từ core
        api_clear_memory(st.session_state.token, username)
        
    st.session_state.user = None
    st.session_state.messages = []
    st.session_state.token = None

# ===================================================
# 🔒 HANDLE UNAUTHORIZED
# ===================================================
def handle_unauthorized(result):
    if not result.get("success"):
        message = result.get("message", "")
        if message in ["Unauthorized", "Forbidden"]:
            st.warning("🔒 Phiên đăng nhập đã hết hạn")
            logout_user()
            st.rerun()

# ===================================================
# 🔐 LOGIN PAGE
# ===================================================
if not st.session_state.user:
    st.title("🔐 AI Nội Bộ Cơ Quan")
    st.markdown("Hệ thống AI nội bộ bảo mật, hoạt động offline 100%.")

    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu", type="password")

    if st.button("Đăng nhập", use_container_width=True):
        result = api_login(username, password)
        
        if result.get("success"):
            st.session_state.user = result["user"]
            st.session_state.token = result["token"]
            st.success("✅ Đăng nhập thành công!")
            st.rerun()
        else:
            st.error("❌ Sai tài khoản hoặc mật khẩu!")
    st.stop()

# ===================================================
# 📚 SIDEBAR
# ===================================================
with st.sidebar:
    st.header("⚙️ AI Nội Bộ")
    st.success("🔒 Offline 100%")
    st.info("🧠 Qwen 2.5")
    st.markdown("---")

    # ===================================================
    # 👤 USER INFO
    # ===================================================
    st.subheader("👤 Người dùng")
    st.write(f"👤 {st.session_state.user['username']}")
    st.write(f"🔑 Role: {st.session_state.user['role']}")
    st.markdown("---")

    # ===================================================
    # 📊 SYSTEM INFO
    # ===================================================
    st.subheader("📊 Hệ thống")
    if st.button("📈 Xem thống kê", use_container_width=True):
        system_info = api_stats(st.session_state.token)
        st.text(system_info)

    # ===================================================
    # 🚪 LOGOUT
    # ===================================================
    if st.button("🚪 Đăng xuất", use_container_width=True):
        logout_user()
        st.rerun()
        
    st.markdown("---")

    # ===================================================
    # 💬 NEW CHAT
    # ===================================================
    st.subheader("📝 Tác vụ")
    if st.button("➕ Cuộc trò chuyện mới", use_container_width=True):
        username = st.session_state.user["username"]
        # Đã sửa: Gọi API để clear memory
        api_clear_memory(st.session_state.token, username)
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")

    # ===================================================
    # 💬 HISTORY
    # ===================================================
    st.subheader("💬 Lịch sử")
    if not st.session_state.lich_su_cuoc_tro_chuyen:
        st.caption("Chưa có lịch sử")
    else:
        for cau_hoi in reversed(st.session_state.lich_su_cuoc_tro_chuyen[-8:]):
            st.caption(f"📌 {cau_hoi[:35]}...")
            
    st.markdown("---")

    # ===================================================
    # 📂 DOCUMENT INGEST
    # ===================================================
    st.subheader("📂 Kho tài liệu")

    if "upload_done" not in st.session_state:
        st.session_state.upload_done = False

    uploaded_files = st.file_uploader(
        "📤 Upload tài liệu",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        key="file_uploader"
    )

    if not uploaded_files:
        st.session_state.upload_done = False

    if uploaded_files and not st.session_state.upload_done:
        progress_bar = st.progress(0)
        total_files = len(uploaded_files)
        uploaded_success = 0
        failed_uploads = 0

        for index, uploaded_file in enumerate(uploaded_files):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            with st.spinner(f"📤 Uploading: {uploaded_file.name}"):
                try:
                    # Đã sửa: Sử dụng API_URL cấu hình linh hoạt
                    response = requests.post(
                        f"{API_URL}/upload",
                        files=files,
                        timeout=300
                    )
                    result = response.json()

                    if result.get("success"):
                        uploaded_success += 1
                        st.success(f"✅ Uploaded: {uploaded_file.name}")
                    else:
                        failed_uploads += 1
                        st.error(f"❌ Failed: {uploaded_file.name}\nMessage: {result.get('message')}")
                except Exception as e:
                    failed_uploads += 1
                    st.error(f"❌ Upload Error: {uploaded_file.name}\nError: {str(e)}")

                progress_bar.progress((index + 1) / total_files)

        st.success(f"🎉 Upload hoàn tất!\n✅ Thành công: {uploaded_success}\n❌ Thất bại: {failed_uploads}")
        st.session_state.upload_done = True
        st.rerun()

    thu_muc_nhap = st.text_input("Đường dẫn thư mục", placeholder="D:\\TaiLieuCoQuan")

    if st.button("🚀 Quét & Nạp dữ liệu", use_container_width=True):
        if thu_muc_nhap:
            with st.status("Đang xử lý dữ liệu...", expanded=True):
                # Đã sửa: Sử dụng API call thay vì chạy thẳng code Core
                result = api_scan_directory(st.session_state.token, thu_muc_nhap)
                if result.get("success"):
                    st.success(f"🎉 {result.get('message')}")
                else:
                    st.error(f"❌ Lỗi: {result.get('message')}")
        else:
            st.error("❌ Vui lòng nhập đường dẫn thư mục!")

    # ===================================================
    # 🛠️ ADMIN PANEL
    # ===================================================
    if st.session_state.user["role"] == "admin":
        render_admin_panel()

# ===================================================
# 💬 EMPTY CHAT SCREEN
# ===================================================
if len(st.session_state.messages) == 0:
    st.markdown("<div class='main-title'>Xin chào!</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Tôi có thể hỗ trợ tra cứu tài liệu nội bộ cho bạn.</div>", unsafe_allow_html=True)

    with st.form("chat_form_center", clear_on_submit=True):
        st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
        col1, col2 = st.columns([15, 1])
        with col1:
            cau_hoi_dau_tien = st.text_input("Câu hỏi", placeholder="Hỏi AI nội bộ...", label_visibility="collapsed")
        with col2:
            kich_hoat_gui = st.form_submit_button("↑")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        goi_y_1 = st.button("👔 Quy định nhân sự", use_container_width=True)
    with col2:
        goi_y_2 = st.button("⏰ Giờ làm việc", use_container_width=True)
    with col3:
        goi_y_3 = st.button("📝 Soạn thông báo", use_container_width=True)

    if goi_y_1: cau_hoi_dau_tien = "Tra cứu quy định nhân sự"; kich_hoat_gui = True
    if goi_y_2: cau_hoi_dau_tien = "Tra cứu giờ làm việc"; kich_hoat_gui = True
    if goi_y_3: cau_hoi_dau_tien = "Soạn thông báo nội bộ"; kich_hoat_gui = True

    if cau_hoi_dau_tien and kich_hoat_gui:
        st.session_state.messages.append({"role": "user", "content": cau_hoi_dau_tien})
        if cau_hoi_dau_tien not in st.session_state.lich_su_cuoc_tro_chuyen:
            st.session_state.lich_su_cuoc_tro_chuyen.append(cau_hoi_dau_tien)
        st.rerun()

# ===================================================
# 💬 CHAT SCREEN
# ===================================================
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant"):
            with st.spinner("🤖 AI đang xử lý..."):
                result = api_chat(
                    token=st.session_state.token,
                    username=st.session_state.user["username"],
                    user_role=st.session_state.user["role"],
                    message=st.session_state.messages[-1]["content"]
                )

                handle_unauthorized(result)

                if not result.get("success"):
                    error_msg = result.get("message", "❌ Lỗi không xác định từ AI")
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {error_msg}"})
                else:
                    ket_qua = result["response"]
                    st.markdown(ket_qua)
                    st.session_state.messages.append({"role": "assistant", "content": ket_qua})
                st.rerun()

    cau_hoi_tiep_theo = st.chat_input("Nhập câu hỏi tiếp theo...")
    if cau_hoi_tiep_theo:
        st.session_state.messages.append({"role": "user", "content": cau_hoi_tiep_theo})
        if cau_hoi_tiep_theo not in st.session_state.lich_su_cuoc_tro_chuyen:
            st.session_state.lich_su_cuoc_tro_chuyen.append(cau_hoi_tiep_theo)
        st.rerun()