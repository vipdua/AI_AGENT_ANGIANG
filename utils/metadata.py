from pathlib import Path

from datetime import datetime

# ===================================================
# 🏢 DETECT DEPARTMENT
# ===================================================
def detect_department(file_path):

    path_str = str(file_path).lower()

    department_keywords = {

        "nhân sự": [
            "nhansu",
            "nhan_su",
            "hr"
        ],

        "tài chính": [
            "taichinh",
            "tai_chinh",
            "finance"
        ],

        "hành chính": [
            "hanhchinh",
            "hanh_chinh",
            "admin"
        ],

        "pháp chế": [
            "phapche",
            "phap_che",
            "legal"
        ]
    }

    for department, keywords in department_keywords.items():

        for keyword in keywords:

            if keyword in path_str:

                return department

    return "chung"

# ===================================================
# 📄 DETECT DOCUMENT CATEGORY
# ===================================================
def detect_document_category(file_name):

    file_name = file_name.lower()

    category_keywords = {

        "quy định": [
            "quydinh",
            "quy_dinh"
        ],

        "quyết định": [
            "quyetdinh",
            "quyet_dinh"
        ],

        "thông báo": [
            "thongbao",
            "thong_bao"
        ],

        "công văn": [
            "congvan",
            "cong_van"
        ],

        "biên bản": [
            "bienban",
            "bien_ban"
        ]
    }

    for category, keywords in category_keywords.items():

        for keyword in keywords:

            if keyword in file_name:

                return category

    return "tài liệu"

# ===================================================
# 🔒 SECURITY LEVEL
# ===================================================
def detect_security_level(file_name):

    file_name = file_name.lower()

    if "mat" in file_name:

        return "mật"

    if "noi_bo" in file_name:

        return "nội bộ"

    return "thường"

# ===================================================
# 🏷️ GENERATE TAGS
# ===================================================
def generate_tags(file_name):

    file_name = file_name.lower()

    words = file_name.replace(
        "_",
        " "
    ).split()

    tags = []

    for word in words:

        if len(word) >= 3:

            tags.append(word)

    return tags

# ===================================================
# 📋 CREATE DOCUMENT METADATA
# ===================================================
def create_document_metadata(file_path):

    file_path = Path(file_path)

    file_name = file_path.name

    metadata = {

        # ===================================================
        # 📄 BASIC
        # ===================================================
        "source": str(file_path),

        "file_name": file_name,

        "file_type": file_path.suffix.lower(),

        # ===================================================
        # 🏢 BUSINESS
        # ===================================================
        "department": detect_department(
            file_path
        ),

        "document_category": (
            detect_document_category(
                file_name
            )
        ),

        "security_level": (
            detect_security_level(
                file_name
            )
        ),

        # ===================================================
        # 🕒 TIME
        # ===================================================
        "indexed_at": str(
            datetime.now()
        ),

        # ===================================================
        # 🏷️ TAGS
        # ===================================================
        "tags": ", ".join(
            generate_tags(file_name)
        )
    }

    return metadata