import hashlib
import json

from pathlib import Path

REGISTRY_FILE = (
    Path("file_registry.json")
)

# ===================================================
# 📂 LOAD REGISTRY
# ===================================================
def load_registry():

    if not REGISTRY_FILE.exists():

        return {}

    with open(

        REGISTRY_FILE,

        "r",

        encoding="utf-8"

    ) as f:

        return json.load(f)

# ===================================================
# 💾 SAVE REGISTRY
# ===================================================
def save_registry(registry):

    with open(

        REGISTRY_FILE,

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            registry,

            f,

            indent=2,

            ensure_ascii=False
        )

# ===================================================
# 🔐 FILE HASH
# ===================================================
def calculate_file_hash(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:

        while chunk := f.read(4096):

            sha256.update(chunk)

    return sha256.hexdigest()

# ===================================================
# ✅ CHECK INDEXED
# ===================================================
def is_file_indexed(file_path):

    registry = load_registry()

    file_hash = calculate_file_hash(
        file_path
    )

    stored_hash = registry.get(
        str(file_path)
    )

    return stored_hash == file_hash

# ===================================================
# ➕ REGISTER FILE
# ===================================================
def register_file(file_path):

    registry = load_registry()

    file_hash = calculate_file_hash(
        file_path
    )

    registry[str(file_path)] = file_hash

    save_registry(registry)

# ===================================================
# 🗑️ REMOVE FILE FROM REGISTRY
# ===================================================
def remove_file_from_registry(

    file_path
):

    registry = load_registry()

    file_key = str(file_path)

    if file_key in registry:

        del registry[file_key]

        save_registry(registry)