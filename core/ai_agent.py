import unicodedata
import re
from langchain_ollama import OllamaLLM
from utils.logger import logger
from core.memory import get_user_memory
from core.audit import write_audit_log
from core.retrieval import hybrid_search
from core.prompts import GREETING_RESPONSE, NO_DATA_RESPONSE, create_error_response
from utils.source_formatter import format_sources
from core.config import LLM_MODEL, OLLAMA_BASE_URL

# ===================================================
# 🔤 TIỆN ÍCH XỬ LÝ TIẾNG VIỆT & TÊN FILE
# ===================================================
def remove_vietnamese_accents(s):
    """Xóa dấu tiếng Việt để so khớp tên file chính xác"""
    if not s:
        return ""
    s = unicodedata.normalize('NFKD', s)
    s = "".join([c for c in s if not unicodedata.combining(c)])
    return s.replace('đ', 'd').replace('Đ', 'D')

def normalize_filename_for_matching(filename):
    """Xử lý tên file dính chữ (CamelCase) và các ký tự đặc biệt"""
    if not filename:
        return ""
    # 1. Tách chữ hoa/chữ thường (VD: VanBan -> Van Ban)
    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', filename)
    # 2. Xóa đuôi mở rộng và thay ký tự đặc biệt thành khoảng trắng
    s = s.replace(".txt", "").replace(".pdf", "").replace(".docx", "").replace("_", " ").replace("-", " ")
    # 3. Xóa dấu tiếng Việt và in thường
    return remove_vietnamese_accents(s).lower()

# ===================================================
# 🧠 LLM MODEL
# ===================================================
def get_llm():
    model_name = LLM_MODEL.replace("ollama/", "")
    return OllamaLLM(
        model=model_name,
        base_url=OLLAMA_BASE_URL,
        temperature=0.3,
    )

def handle_simple_chat(user_message):
    greetings = ["xin chào", "hello", "hi", "alo", "hey", "chào"]
    if user_message.lower().strip() in greetings:
        return GREETING_RESPONSE
    return None

def build_context_from_docs(docs):
    if not docs:
        return ""
    context_parts = []
    
    for index, doc in enumerate(docs, start=1):
        source = doc.metadata.get("file_name") or doc.metadata.get("filename") or "Không rõ nguồn"
        department = doc.metadata.get("department", "unknown")
        content = doc.page_content.strip()

        if not content:
            continue

        context_parts.append(
            f"==============================\n"
            f"TÀI LIỆU {index}\n"
            f"NGUỒN: {source}\n"
            f"PHÒNG BAN: {department}\n"
            f"NỘI DUNG:\n{content}\n"
        )
    return "\n\n".join(context_parts)

# ===================================================
# 🚀 MAIN AI FUNCTION
# ===================================================
def ask_ai(user_question, username, user_role="nhan_vien"):
    logger.info(f"📩 User question: {user_question}")
    write_audit_log(username, "CHAT", user_question[:200])

    simple_response = handle_simple_chat(user_question)
    if simple_response:
        return simple_response

    memory = get_user_memory(username)
    conversation_history = memory.get_history()

    try:
        docs = hybrid_search(query=user_question, user_role=user_role)
    except Exception as e:
        logger.error(f"❌ Search error: {e}")
        docs = []

    context = build_context_from_docs(docs)

    # ===================================================
    # 🎯 DIRECT DOCUMENT RETURN (EXACT MATCH)
    # ===================================================
    # Mở rộng bộ từ khóa để bao quát các câu hỏi rà soát, kiểm tra văn bản
    direct_match_triggers = [
        "nội dung", "có gì", "ghi gì", "viết gì", 
        "tài liệu", "văn bản", "báo cáo", "quy định", 
        "hồ sơ", "rà soát", "kiểm tra", "cho xem"
    ]
    
    question_lower = user_question.lower()

    if docs and any(trigger in question_lower for trigger in direct_match_triggers):
        logger.info("⚡ Direct document response (Exact Match Flow Triggered)")
        
        question_clean = remove_vietnamese_accents(question_lower).replace("?", "")
        question_tokens = set(question_clean.split())
        
        best_doc = docs[0]
        max_score = -1

        for doc in docs:
            filename_raw = doc.metadata.get("file_name") or doc.metadata.get("filename") or ""
            
            # Chuẩn hóa tên file thông minh (tách CamelCase)
            filename_clean = normalize_filename_for_matching(filename_raw)
            filename_tokens = set(filename_clean.split())

            # Tính điểm dựa trên số từ giao nhau
            score = len(filename_tokens.intersection(question_tokens))
            
            logger.info(f"🔍 Checking file: '{filename_raw}' -> Clean: '{filename_clean}' | Score: {score}")

            if score > max_score:
                max_score = score
                best_doc = doc

        # NẾU ĐIỂM SỐ >= 2 (khớp ít nhất 2 từ khóa), trả thẳng file đó
        if max_score >= 2:
            logger.info(f"🎯 Matched file directly based on filename score: {max_score}")
            direct_answer = best_doc.page_content.strip()
            
            single_source_text = format_sources([best_doc])
            if single_source_text:
                direct_answer += f"\n{single_source_text}"
                
            memory.add_message("user", user_question)
            memory.add_message("assistant", direct_answer)
            return direct_answer
        else:
            logger.info("📉 Score too low for Exact Match. Falling back to LLM RAG.")

    # ===================================================
    # 🤖 BUILD PROMPT CHO LLM TỔNG HỢP
    # ===================================================
    if context:
        prompt = f"""Bạn là trợ lý AI nội bộ cơ quan Việt Nam.

QUY TẮC BẮT BUỘC:
- Chỉ trả lời bằng tiếng Việt.
- Không tự bịa thông tin, không suy diễn ngoài CONTEXT. Chỉ dùng dữ liệu trong CONTEXT.
- Nếu người dùng hỏi về một TÊN TÀI LIỆU CỤ THỂ, hãy đọc NỘI DUNG của tài liệu đó trong CONTEXT và trích xuất nguyên văn.
- Nếu tài liệu có lỗi (sai chính tả, sai thể thức), hãy BÁO CÁO LẠI các lỗi đó một cách rõ ràng.

==============================
LỊCH SỬ HỘI THOẠI
==============================
{conversation_history if conversation_history else "(Chưa có lịch sử)"}

==============================
CONTEXT
==============================
{context}

==============================
CÂU HỎI
==============================
{user_question}

==============================
TRẢ LỜI
==============================
"""
    else:
        prompt = f"""Bạn là trợ lý AI nội bộ cơ quan Việt Nam.
==============================
THÔNG BÁO
==============================
Không tìm thấy tài liệu phù hợp trong kho dữ liệu.
==============================
CÂU HỎI
==============================
{user_question}
==============================
TRẢ LỜI
==============================
Hãy thông báo rằng không tìm thấy thông tin phù hợp và gợi ý người dùng nạp thêm tài liệu.
"""

    # ===================================================
    # 🚀 CALL LLM
    # ===================================================
    try:
        llm = get_llm()
        response = llm.invoke(prompt)
        answer = str(response).strip()

        bad_phrases = ["mang tính chất", "được cấp độ", "thông tin nội bộ", "rõ ràng là", "có vẻ như"]
        for phrase in bad_phrases:
            answer = answer.replace(phrase, "")

        bad_patterns = ["không tìm thấy", "không có thông tin", "vui lòng cung cấp thêm", "hãy nạp thêm tài liệu"]
        if context and any(pattern in answer.lower() for pattern in bad_patterns):
            logger.warning("⚠️ AI trả lời sai dù có context -> Lấy nội dung thô.")
            answer = docs[0].page_content[:1500]

        sources_text = format_sources(docs)
        if sources_text:
            answer += f"\n{sources_text}"

        memory.add_message("user", user_question)
        memory.add_message("assistant", answer)

        logger.info("✅ AI trả lời thành công")
        return answer

    except Exception as e:
        logger.error(f"❌ AI Error: {e}")
        return create_error_response(e)