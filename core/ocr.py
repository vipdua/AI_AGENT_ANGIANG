import pytesseract

from PIL import Image

from pdf2image import convert_from_path

from pathlib import Path

from utils.logger import logger

# ===================================================
# ⚙️ TESSERACT PATH
# ===================================================
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# ===================================================
# 🖼️ OCR IMAGE
# ===================================================
def extract_text_from_image(image_path):

    try:

        image = Image.open(image_path)

        text = pytesseract.image_to_string(
            image,
            lang="vie"
        )

        return text

    except Exception as e:

        logger.error(
            f"OCR image error: {e}"
        )

        return ""

# ===================================================
# 📄 OCR PDF
# ===================================================
def extract_text_from_pdf(pdf_path):

    try:

        pages = convert_from_path(pdf_path)

        all_text = []

        for page in pages:

            text = pytesseract.image_to_string(
                page,
                lang="vie"
            )

            all_text.append(text)

        return "\n".join(all_text)

    except Exception as e:

        logger.error(
            f"OCR PDF error: {e}"
        )

        return ""

# ===================================================
# 🔍 CHECK SCAN PDF
# ===================================================
def is_scanned_pdf(text):

    cleaned = text.strip()

    return len(cleaned) < 30