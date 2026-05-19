from datetime import (
    datetime,
    timedelta
)

from fastapi import (
    Header
)

from jose import jwt

# ===================================================
# 🔐 JWT CONFIG
# ===================================================
SECRET_KEY = (
    "AI_AGENT_SECRET_KEY"
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_HOURS = 12

# ===================================================
# 🎟️ CREATE TOKEN
# ===================================================
def create_access_token(

    data: dict
):

    to_encode = data.copy()

    expire = (
        datetime.utcnow()

        + timedelta(
            hours=
            ACCESS_TOKEN_EXPIRE_HOURS
        )
    )

    to_encode.update({

        "exp": expire
    })

    encoded_jwt = jwt.encode(

        to_encode,

        SECRET_KEY,

        algorithm=ALGORITHM
    )

    return encoded_jwt

# ===================================================
# 🔍 VERIFY TOKEN
# ===================================================
def verify_access_token(

    token: str
):

    try:

        payload = jwt.decode(

            token,

            SECRET_KEY,

            algorithms=[ALGORITHM]
        )

        return payload

    except:

        return None
    
# ===================================================
# 🔒 GET CURRENT USER
# ===================================================
def get_current_user(

    authorization: str = Header(None)
):

    if not authorization:

        return None

    try:

        token = authorization.replace(

            "Bearer ",

            ""
        )

        payload = verify_access_token(
            token
        )

        return payload

    except:

        return None
    
# ===================================================
# 🛡️ REQUIRE ROLE
# ===================================================
def require_role(

    current_user,

    allowed_roles
):

    if not current_user:

        return False

    user_role = current_user.get(
        "role"
    )

    return user_role in allowed_roles