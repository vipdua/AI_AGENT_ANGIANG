import threading

from pathlib import Path

from utils.logger import logger

import time

from core.failed_queue import (
    failed_files
)

from core.loaders import (
    load_single_file
)

from core.rag import (
    ingest_documents,
    delete_document_by_source
)

from core.file_registry import (
    register_file
)

from core.processing_state import (
    processing_files,
    processing_lock
)

from core.persistent_queue import (

    get_next_task,

    complete_task
)

# ===================================================
# 🚀 PROCESS FILE
# ===================================================
def process_file(

    action,

    file_path,

    retry_count=3
):

    file_path = Path(file_path)

    # ===================================================
    # 🔒 CHECK PROCESSING
    # ===================================================
    with processing_lock:

        if str(file_path) in processing_files:

            logger.warning(
                f"⏳ Already processing: "
                f"{file_path.name}"
            )

            return

        processing_files.add(
            str(file_path)
        )

    try:

        # ===================================================
        # ➕ CREATE / MODIFY
        # ===================================================
        if action in [

            "created",
            "modified"
        ]:

            if action == "modified":

                delete_document_by_source(
                    str(file_path)
                )

            docs = load_single_file(
                file_path
            )

            if docs:

                ingest_documents(docs)

                register_file(
                    file_path
                )

                logger.info(
                    f"✅ Processed: "
                    f"{file_path.name}"
                )

        # ===================================================
        # 🗑️ DELETE
        # ===================================================
        elif action == "deleted":

            delete_document_by_source(
                str(file_path)
            )

            logger.info(
                f"🗑️ Deleted vectors: "
                f"{file_path.name}"
            )

    except Exception as e:

        logger.error(
            f"❌ Worker error: {e}"
        )

        # ===================================================
        # 🔁 RETRY
        # ===================================================
        if retry_count > 0:

            logger.warning(
                f"🔁 Retrying: "
                f"{file_path.name}"
            )

            time.sleep(2)

            process_file(

                action,

                file_path,

                retry_count - 1
            )

        else:

            logger.error(
                f"💀 Failed permanently: "
                f"{file_path.name}"
            )

            failed_files.append({

                "file": str(file_path),

                "action": action,

                "error": str(e)
            })

    finally:

        # ===================================================
        # 🔓 RELEASE LOCK
        # ===================================================
        time.sleep(2)

        with processing_lock:

            processing_files.discard(
                str(file_path)
            )

# ===================================================
# 👷 WORKER LOOP
# ===================================================
def worker_loop():

    while True:

        task = get_next_task()

        # ===================================================
        # 😴 NO TASK
        # ===================================================
        if not task:

            time.sleep(1)

            continue

        task_id, action, file_path = task

        process_file(

            action,

            file_path
        )

        # ===================================================
        # ✅ COMPLETE TASK
        # ===================================================
        complete_task(task_id)

# ===================================================
# 🚀 START MULTI WORKERS
# ===================================================
def start_workers(

    num_workers=4
):

    for i in range(num_workers):

        thread = threading.Thread(

            target=worker_loop,

            daemon=True
        )

        thread.start()

        logger.info(
            f"👷 Worker {i+1} started"
        )