from utils.logger import logger

# ===================================================
# 🔐 ROLE PERMISSIONS
# ===================================================
ROLE_PERMISSIONS = {

    "admin": [
        "thường",
        "nội bộ",
        "mật"
    ],

    "nhan_su": [
        "thường",
        "nội bộ"
    ],

    "tai_chinh": [
        "thường",
        "nội bộ"
    ],

    "nhan_vien": [
        "thường"
    ]
}

# ===================================================
# 🔍 CHECK DOCUMENT ACCESS
# ===================================================
def can_access_document(

    user_role,

    document
):

    security_level = document.metadata.get(

        "security_level",

        "thường"
    )

    allowed_levels = ROLE_PERMISSIONS.get(

        user_role,

        []
    )

    return security_level in allowed_levels

# ===================================================
# 📄 FILTER DOCUMENTS
# ===================================================
def filter_accessible_documents(

    user_role,

    documents
):

    filtered_documents = []

    for document in documents:

        if can_access_document(

            user_role,

            document
        ):

            filtered_documents.append(
                document
            )

    logger.info(
        f"🔐 Accessible documents: {len(filtered_documents)}"
    )

    return filtered_documents