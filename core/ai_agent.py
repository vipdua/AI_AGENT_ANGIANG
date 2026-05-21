from langchain_ollama import OllamaLLM

from utils.logger import logger

from core.memory import (
    get_user_memory
)

from core.audit import (
    write_audit_log
)

from core.retrieval import (
    hybrid_search
)

from core.prompts import (
    GREETING_RESPONSE,
    NO_DATA_RESPONSE,
    create_error_response
)

from utils.source_formatter import (
    format_sources
)

from core.config import (
    LLM_MODEL,
    OLLAMA_BASE_URL
)

# ===================================================
# 🧠 LLM MODEL (Ollama trực tiếp — nhanh hơn CrewAI)
# ===================================================
def get_llm():

    # Lấy tên model, bỏ prefix "ollama/"
    model_name = LLM_MODEL.replace(
        "ollama/", ""
    )

    # ⚠️ QUAN TRỌNG: Trong Docker container, "localhost" = container
    # Ollama chạy trên host Windows → phải dùng host.docker.internal
    # OLLAMA_BASE_URL trong config.py đã được set đúng
    return OllamaLLM(
        model=model_name,
        base_url=OLLAMA_BASE_URL,
        temperature=0.3,
    )

# ===================================================
# 💬 SIMPLE CHAT (chào hỏi không cần RAG)
# ===================================================
def handle_simple_chat(user_message):

    greetings = [
        "xin chào",
        "hello",
        "hi",
        "alo",
        "hey",
        "chào"
    ]

    if user_message.lower().strip() in greetings:

        return GREETING_RESPONSE

    return None

# ===================================================
# 📄 BUILD CONTEXT FROM DOCS
# ===================================================
def build_context_from_docs(docs):

    if not docs:
        return ""

    context_parts = []

    for index, doc in enumerate(docs, start=1):

        source = doc.metadata.get(
            "filename",
            "Không rõ nguồn"
        )

        department = doc.metadata.get(
            "department",
            "unknown"
        )

        content = doc.page_content.strip()

        # ===================================================
        # 🚫 SKIP EMPTY
        # ===================================================
        if not content:
            continue

        context_parts.append(
            f"""
==============================
TÀI LIỆU {index}
==============================

NGUỒN:
{source}

PHÒNG BAN:
{department}

NỘI DUNG:
{content}
"""
        )

    return "\n\n".join(context_parts)

# ===================================================
# 🚀 MAIN AI FUNCTION (1 agent — nhanh hơn CrewAI)
# ===================================================
def ask_ai(
    user_question,
    username,
    user_role="nhan_vien"
):

    logger.info(f"📩 User question: {user_question}")

    write_audit_log(
        username,
        "CHAT",
        user_question[:200]
    )

    # ===================================================
    # 💬 SIMPLE CHAT — không cần RAG
    # ===================================================
    simple_response = handle_simple_chat(
        user_question
    )

    if simple_response:

        return simple_response

    # ===================================================
    # 🧠 USER MEMORY
    # ===================================================
    memory = get_user_memory(username)

    conversation_history = memory.get_history()

    # ===================================================
    # 🔍 HYBRID SEARCH
    # ===================================================
    try:

        docs = hybrid_search(
            query=user_question,
            user_role=user_role
        )

    except Exception as e:

        logger.error(f"❌ Search error: {e}")

        docs = []

    # ===================================================
    # 📄 BUILD CONTEXT
    # ===================================================
    context = build_context_from_docs(docs)

    sources_text = format_sources(docs) if docs else ""

    # ===================================================
    # 🚀 DIRECT DOCUMENT RETURN
    # ===================================================
    simple_queries = [

        "nội dung gì",

        "có gì",

        "nội dung là gì",

        "ghi gì",

        "viết gì"
    ]

    question_lower = user_question.lower()

    if docs and any(

        q in question_lower

        for q in simple_queries
    ):

        logger.info(
            "⚡ Direct document response"
        )

        # ===================================================
        # 🎯 FIND BEST FILE MATCH
        # ===================================================
        best_doc = docs[0]

        question_tokens = (
            question_lower
            .replace("?", "")
            .split()
        )

        for doc in docs:

            filename = (
                doc.metadata.get(
                    "filename",
                    ""
                )
                .lower()
                .replace(".txt", "")
                .replace("_", " ")
            )

            # ===================================================
            # 🎯 TOKEN MATCH SCORE
            # ===================================================
            score = sum(

                1

                for token in question_tokens

                if token in filename
            )

            logger.info(
                f"""
    FILENAME SCORE: {score}

    FILE:
    {filename}
    """
            )

            # ===================================================
            # 🚀 PRIORITY MATCH
            # ===================================================
            if score >= 2:

                best_doc = doc

                logger.info(
                    f"🎯 Best doc matched: {filename}"
                )

                break

        direct_answer = (
            best_doc.page_content.strip()
        )

        if sources_text:

            direct_answer += sources_text

        return direct_answer

    # ===================================================
    # 🤖 BUILD PROMPT
    # ===================================================
    if context:

        prompt = f"""
    Bạn là trợ lý AI nội bộ cơ quan Việt Nam.

    QUY TẮC BẮT BUỘC:

    - Chỉ trả lời bằng tiếng Việt
    - Không dùng tiếng Anh
    - Không dùng tiếng Trung
    - Không tự bịa thông tin
    - Không suy diễn ngoài CONTEXT
    - Chỉ dùng dữ liệu trong CONTEXT

    - Nếu CONTEXT chứa:
        + bảng dữ liệu
        + danh sách
        + mã tài liệu
        + cấp độ bảo mật
    thì phải liệt kê đầy đủ

    - Không trả lời chung chung
    - Ưu tiên trích nguyên văn dữ liệu quan trọng
    - Nếu có nhiều tài liệu:
        + hãy tổng hợp rõ ràng
        + dễ đọc

    - Nếu tài liệu có cấu trúc bảng:
        + giữ nguyên nội dung quan trọng
        + không được bỏ sót dữ liệu

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

        prompt = f"""
    Bạn là trợ lý AI nội bộ cơ quan Việt Nam.

    QUY TẮC BẮT BUỘC:

    - Chỉ trả lời bằng tiếng Việt
    - Không dùng tiếng Trung
    - Không dùng tiếng Anh
    - Không tự bịa thông tin nếu không có trong tài liệu

    ==============================
    LỊCH SỬ HỘI THOẠI
    ==============================

    {conversation_history if conversation_history else "(Chưa có lịch sử)"}

    ==============================
    THÔNG BÁO
    ==============================

    Không tìm thấy tài liệu phù hợp trong kho dữ liệu.

    ==============================
    CÂU HỎI
    ==============================

    {user_question}

    ==============================
    YÊU CẦU
    ==============================

    Hãy thông báo rằng:
    - không tìm thấy thông tin phù hợp
    - và gợi ý người dùng:
        + nạp thêm tài liệu
        + hoặc đặt lại câu hỏi rõ hơn

    - KHÔNG được diễn giải dữ liệu
    - KHÔNG được nhận xét dữ liệu
    - KHÔNG được đánh giá dữ liệu
    - KHÔNG được thêm giải thích cá nhân
    - Nếu dữ liệu chỉ có 1 dòng:
        hãy trả nguyên văn dòng đó
    - Nếu dữ liệu là bảng:
        hãy giữ nguyên cấu trúc quan trọng
    - Ưu tiên trích nguyên văn thay vì tóm tắt    
    
    ==============================
    TRẢ LỜI
    ==============================
    """

    # ===================================================
    # 🚀 CALL LLM
    # ===================================================
    try:

        llm = get_llm()

        response = llm.invoke(prompt)

        answer = str(response).strip()

        # ===================================================
        # 🚫 REMOVE HALLUCINATION PHRASES
        # ===================================================
        bad_phrases = [

            "mang tính chất",

            "được cấp độ",

            "thông tin nội bộ",

            "rõ ràng là",

            "có vẻ như"
        ]

        for phrase in bad_phrases:

            answer = answer.replace(
                phrase,
                ""
            )

        # ===================================================
        # 🚫 FALLBACK BAD ANSWERS
        # ===================================================
        bad_patterns = [

            "không tìm thấy",

            "không có thông tin",

            "vui lòng cung cấp thêm",

            "hãy nạp thêm tài liệu"
        ]

        if context:

            lower_answer = answer.lower()

            if any(
                pattern in lower_answer
                for pattern in bad_patterns
            ):

                logger.warning(
                    "⚠️ AI trả lời sai dù có context"
                )

                # ===================================================
                # 🚀 RETURN BEST MATCH ONLY
                # ===================================================
                best_doc = docs[0]

                answer = (
                    best_doc.page_content[:1500]
                )

        # Thêm nguồn tài liệu nếu có
        if sources_text:
            answer += sources_text

        # ===================================================
        # 🧠 LƯU VÀO MEMORY
        # ===================================================
        memory.add_message("user", user_question)

        memory.add_message("assistant", answer)

        logger.info("✅ AI trả lời thành công")

        return answer

    except Exception as e:

        logger.error(f"❌ AI Error: {e}")

        return create_error_response(e)