import pytesseract
from PIL import Image
import io
import pdfplumber
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextExtractor:
    def extract_text(self, content: bytes, mime_type: str) -> str:
        pass

class TesseractTextExtractor(TextExtractor):
    def extract_text(self, content: bytes, mime_type: str) -> str:
        try:
            if mime_type in ['text/plain', 'text/csv']:
                text = content.decode('utf-8', errors='ignore')
                logger.info("Extracting text from %s: %d characters", mime_type, len(text))
                return text
            elif mime_type == 'application/pdf':
                return self._extract_from_pdf(content)
            elif mime_type == 'image/png':
                return self._extract_from_image(content)
            else:
                logger.warning("Unsupported MIME type: %s", mime_type)
                return ""
        except Exception as e:
            logger.error("Error extracting text for MIME type %s: %s", mime_type, e)
            return ""

    def _extract_from_pdf(self, content: bytes) -> str:
        try:
            pdf_file = io.BytesIO(content)
            with pdfplumber.open(pdf_file) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    text += page_text + "\n"
            if not text.strip():
                logger.warning("No text extracted from PDF")
            else:
                logger.info("Extracted %d characters from PDF", len(text))
            return text
        except Exception as e:
            logger.error("PDF extraction failed: %s", e)
            return ""

    def _extract_from_image(self, content: bytes) -> str:
        try:
            image_file = io.BytesIO(content)
            image = Image.open(image_file)
            text = pytesseract.image_to_string(image)
            if not text.strip():
                logger.warning("No text extracted from image")
            else:
                logger.info("Extracted %d characters from image", len(text))
            return text
        except Exception as e:
            logger.error("Image extraction failed: %s", e)
            return ""