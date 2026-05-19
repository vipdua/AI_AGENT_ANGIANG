from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from utils.logger import logger

from core.memory import (
    get_user_memory
)

from core.prompts import (
    create_memory_prompt
)

from utils.source_formatter import (
    format_sources
)

from core.audit import (
    write_audit_log
)

from core.retrieval import (
    hybrid_search
)

from core.prompts import (
    RESEARCH_AGENT_PROMPT,
    WRITING_AGENT_PROMPT,
    WRITING_TASK_PROMPT,
    GREETING_RESPONSE,
    NO_DATA_RESPONSE,
    create_research_task_prompt,
    create_error_response
)

# ===================================================
# 🧠 LLM MODEL
# ===================================================
LLM_MODEL = "ollama/qwen2.5:7b"

# ===================================================
# 💬 SIMPLE CHAT
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
# 🔍 CREATE SEARCH TOOL
# ===================================================
def create_search_tool( user_role):

    @tool("Tra cứu Văn bản Nội bộ")
    def tra_cuu_van_ban(query: str) -> str:
        """
        Công cụ dùng để tra cứu thông tin
        trong kho tài liệu nội bộ.
        """

        # ===================================================
        # 🔍 HYBRID SEARCH
        # ===================================================
        docs = hybrid_search( query=query, user_role=user_role )

        # ===================================================
        # 🚫 NO DATA
        # ===================================================
        if not docs:

            return NO_DATA_RESPONSE

        results = []

        # ===================================================
        # 📄 DOCUMENT RESULTS
        # ===================================================
        for doc in docs:

            source = doc.metadata.get(
                "file_name",
                "Không rõ nguồn"
            )

            content = doc.page_content

            results.append(
                f"""
Nguồn: {source}

Nội dung:
{content}
"""
            )

        # ===================================================
        # 📄 FORMAT SOURCES
        # ===================================================
        sources_text = format_sources(
            docs
        )

        # ===================================================
        # 🧠 FINAL RESULT
        # ===================================================
        final_result = "\n\n".join(results)

        final_result += sources_text

        return final_result

    return tra_cuu_van_ban

# ===================================================
# 👨‍💼 CREATE RESEARCH AGENT
# ===================================================
def create_research_agent(search_tool):

    return Agent(

        role="Chuyên viên Tra cứu",

        goal="Tìm kiếm thông tin chính xác.",

        backstory=RESEARCH_AGENT_PROMPT,

        tools=[search_tool],

        llm=LLM_MODEL,

        verbose=True
    )

# ===================================================
# 📝 CREATE WRITING AGENT
# ===================================================
def create_writing_agent():

    return Agent(

        role="Chuyên viên Soạn thảo",

        goal="Soạn phản hồi chuyên nghiệp.",

        backstory=WRITING_AGENT_PROMPT,

        tools=[],

        llm=LLM_MODEL,

        verbose=True,

        max_iter=1,

        memory=False
    )

# ===================================================
# 📌 CREATE TASKS
# ===================================================
def create_tasks(
    user_question,
    research_agent,
    writing_agent
):

    # ===================================================
    # 📌 TASK 1
    # ===================================================
    task_1 = Task(

        description=create_research_task_prompt(
            user_question
        ),

        expected_output="""
Thông tin chính xác từ tài liệu nội bộ.
""",

        agent=research_agent
    )

    # ===================================================
    # 📌 TASK 2
    # ===================================================
    task_2 = Task(

        description=WRITING_TASK_PROMPT,

        expected_output="""
Một câu trả lời hoàn chỉnh bằng tiếng Việt.
""",

        agent=writing_agent
    )

    return [task_1, task_2]

# ===================================================
# 🚀 MAIN AI FUNCTION
# ===================================================
def ask_ai( user_question, username, user_role="nhan_vien" ):

    logger.info( f"📩 User question: {user_question}" )

    write_audit_log(

        username,

        "CHAT",

        user_question[:200]
    )

    # ===================================================
    # 🧠 USER MEMORY
    # ===================================================
    memory = get_user_memory(
        username
    )

    conversation_history = (
        memory.get_history()
    )

    enhanced_question = create_memory_prompt(

        conversation_history,

        user_question
    )

    # ===================================================
    # 💬 SIMPLE CHAT
    # ===================================================
    simple_response = handle_simple_chat(
        user_question
    )

    if simple_response:

        return simple_response

    # ===================================================
    # 🔍 SEARCH TOOL
    # ===================================================
    search_tool = create_search_tool( user_role )

    # ===================================================
    # 👨‍💼 CREATE AGENTS
    # ===================================================
    research_agent = create_research_agent(
        search_tool
    )

    writing_agent = create_writing_agent()

    # ===================================================
    # 📌 CREATE TASKS
    # ===================================================
    tasks = create_tasks(
        enhanced_question,
        research_agent,
        writing_agent
    )

    # ===================================================
    # 👥 CREATE CREW
    # ===================================================
    crew = Crew(

        agents=[
            research_agent,
            writing_agent
        ],

        tasks=tasks,

        process=Process.sequential
    )

    # ===================================================
    # 🚀 RUN AI
    # ===================================================
    try:

        result = crew.kickoff()

        memory.add_message(
            "user",
            user_question
        )

        memory.add_message(
            "assistant",
            str(result)
        )

        logger.info("✅ AI trả lời thành công")

        return str(result)

    except Exception as e:

        logger.error(f"❌ AI Error: {e}")

        return create_error_response(e)