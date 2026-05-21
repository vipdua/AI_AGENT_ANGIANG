from pathlib import Path

from utils.logger import logger

from utils.metadata import (
    create_document_metadata
)

from core.ocr import (
    extract_text_from_pdf,
    is_scanned_pdf
)

from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader
)

# ===================================================
# 📄 LOAD TXT
# ===================================================
def load_txt(file_path):

    loader = TextLoader(
        file_path,
        encoding="utf-8"
    )

    return loader.load()

# ===================================================
# 📘 LOAD PDF
# ===================================================
def load_pdf(file_path):

    loader = PyPDFLoader(file_path)

    docs = loader.load()

    # ===================================================
    # 🔍 CHECK SCAN PDF
    # ===================================================
    combined_text = "\n".join([
        doc.page_content
        for doc in docs
    ])

    if is_scanned_pdf(combined_text):

        logger.info(
            f"🖨️ Scan PDF detected: {file_path}"
        )

        ocr_text = extract_text_from_pdf(
            file_path
        )

        if ocr_text.strip():

            docs[0].page_content = ocr_text

    return docs

# ===================================================
# 📄 LOAD DOCX
# ===================================================
def load_docx(file_path):

    loader = Docx2txtLoader(file_path)

    return loader.load()

# ===================================================
# 📂 LOAD SINGLE FILE
# ===================================================
def load_single_file(file_path):

    file_path = Path(file_path)

    suffix = file_path.suffix.lower()

    try:

        # ===================================================
        # 📄 LOAD FILE
        # ===================================================
        # TXT
        if suffix == ".txt":

            docs = load_txt(str(file_path))

        # PDF
        elif suffix == ".pdf":

            docs = load_pdf(str(file_path))

        # DOCX
        elif suffix == ".docx":

            docs = load_docx(str(file_path))

        else:

            print(
                f"❌ Không hỗ trợ file: "
                f"{file_path.name}"
            )

            return []

        # ===================================================
        # 📋 CREATE METADATA
        # ===================================================
        metadata = create_document_metadata(
            file_path
        )

        metadata["department"] = (
            detect_department(
                file_path.name
            )
        )

        logger.info(
            f"""
        📄 FILE METADATA

        FILE:
        {file_path.name}

        METADATA:
        {metadata}
        """
        )

        # ===================================================
        # 📦 ADD METADATA
        # ===================================================
        for doc in docs:

            doc.metadata.update(metadata)

        return docs

    except Exception as e:

        logger.error(
            f"Lỗi đọc file "
            f"{file_path.name}: {e}"
        )

        return []

# ===================================================
# 📁 LOAD DIRECTORY
# ===================================================
def load_documents_from_directory(directory_path):

    directory = Path(directory_path)

    all_documents = []

    supported_extensions = [
        ".txt",
        ".pdf",
        ".docx"
    ]

    for file_path in directory.rglob("*"):

        if file_path.suffix.lower() in supported_extensions:

            logger.info(f"📄 Đang đọc: {file_path.name}")

            docs = load_single_file(file_path)

            all_documents.extend(docs)

    return all_documents

# ===================================================
# 🏢 DETECT DEPARTMENT
# ===================================================
def detect_department(

    file_name
):

    file_name = (
        file_name.lower()
    )

    if "tai_chinh" in file_name:

        return "tai_chinh"

    if "nhan_su" in file_name:

        return "nhan_su"

    if "admin" in file_name:

        return "admin"

    return "all"