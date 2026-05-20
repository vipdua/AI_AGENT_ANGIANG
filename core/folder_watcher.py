from watchdog.observers import Observer

from watchdog.events import (
    FileSystemEventHandler
)

from pathlib import Path

import time

from utils.logger import logger

from core.loaders import (
    load_single_file
)

from core.file_registry import (
    is_file_indexed,
    register_file
)

from core.rag import (
    ingest_documents,
    delete_document_by_source
)

from core.file_registry import (
    is_file_indexed,
    register_file,
    remove_file_from_registry
)

from core.persistent_queue import (
    add_task
)

# ===================================================
# 📂 WATCHER HANDLER
# ===================================================
class DocumentHandler(
    FileSystemEventHandler
):

    # ===================================================
    # 📄 NEW FILE
    # ===================================================
    def on_created(self, event):

        if event.is_directory:

            return

        file_path = Path(
            event.src_path
        )

        logger.info(
            f"📄 New file: {file_path.name}"
        )

        supported = [
            ".pdf",
            ".docx",
            ".txt"
        ]

        if (
            file_path.suffix.lower()
            not in supported
        ):

            return

        try:

            # ===================================================
            # ⏭️ SKIP EXISTING FILE
            # ===================================================
            if is_file_indexed(file_path):

                logger.info(
                    f"⏭️ Skipped existing: "
                    f"{file_path.name}"
                )

                return

            # ===================================================
            # 📥 ADD TO QUEUE
            # ===================================================
            add_task(

                "created",

                str(file_path)
            )

            logger.info(
                f"📥 Queued: "
                f"{file_path.name}"
            )

        except Exception as e:

            logger.error(
                f"❌ Watcher error: {e}"
            )

    # ===================================================
    # ✏️ FILE MODIFIED
    # ===================================================
    def on_modified(self, event):

        if event.is_directory:

            return

        file_path = Path(
            event.src_path
        )

        supported = [
            ".pdf",
            ".docx",
            ".txt"
        ]

        if (
            file_path.suffix.lower()
            not in supported
        ):

            return

        try:

            # ===================================================
            # ⏭️ SKIP IF NOT CHANGED
            # ===================================================
            if is_file_indexed(file_path):

                return

            logger.info(
                f"✏️ File modified: "
                f"{file_path.name}"
            )

            # ===================================================
            # 📥 ADD TO QUEUE
            # ===================================================
            add_task(

                "modified",

                str(file_path)
            )

            logger.info(
                f"📥 Modify queued: "
                f"{file_path.name}"
            )

        except Exception as e:

            logger.error(
                f"❌ Modify error: {e}"
            )

    # ===================================================
    # 🗑️ FILE DELETED
    # ===================================================
    def on_deleted(self, event):

        if event.is_directory:

            return

        file_path = Path(
            event.src_path
        )

        supported = [
            ".pdf",
            ".docx",
            ".txt"
        ]

        if (
            file_path.suffix.lower()
            not in supported
        ):

            return

        try:

            logger.info(
                f"🗑️ File deleted: "
                f"{file_path.name}"
            )

            # ===================================================
            # 📥 ADD TO QUEUE
            # ===================================================
            add_task(

                "deleted",

                str(file_path)
            )

            logger.info(
                f"📥 Delete queued: "
                f"{file_path.name}"
            )

        except Exception as e:

            logger.error(
                f"❌ Delete error: {e}"
            )

# ===================================================
# 🚀 START WATCHER
# ===================================================
def start_folder_watcher(

    folder_path
):

    observer = Observer()

    handler = DocumentHandler()

    observer.schedule(

        handler,

        folder_path,

        recursive=True
    )

    observer.start()

    logger.info(
        f"👀 Watching: {folder_path}"
    )

    try:

        while True:

            time.sleep(1)

    except KeyboardInterrupt:

        observer.stop()

    observer.join()