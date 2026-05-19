from core.auth import (
    create_user
)

# ===================================================
# 🌱 SEED USERS
# ===================================================
def seed_users():

    users = [

        (
            "admin",
            "admin123",
            "admin"
        ),

        (
            "nhanvien",
            "nhanvien123",
            "nhan_vien"
        ),

        (
            "taichinh",
            "taichinh123",
            "tai_chinh"
        )
    ]

    for user in users:

        create_user(*user)

    print(
        "✅ Seed users completed"
    )

# ===================================================
# 🚀 RUN
# ===================================================
if __name__ == "__main__":

    seed_users()