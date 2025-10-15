import base64
import io
from fastapi import HTTPException, status

try:
    from pypdf import PdfReader  # For PDF extraction
    from docx import Document  # For DOCX extraction
except ImportError:
    # This warning indicates the required libraries are missing.
    print(
        "⚠️ WARNING: 'pypdf' or 'python-docx' library not found. Install them with 'pip install pypdf python-docx'."
    )

from schema.file import FileRequest


class FileController:
    @staticmethod
    def decode_base64_file(base64_string: str, filetype: str):
        """
        Decodes a base64 string into bytes and returns a BytesIO object.

        Args:
            base64_string: The base64 encoded file data.
            filetype: The expected file type ('pdf' or 'docx').

        Returns:
            io.BytesIO: An in-memory file handle containing the decoded bytes.
        """
        try:
            # 1. Decode the base64 string
            # Strip common MIME type prefixes (e.g., "data:application/pdf;base64,...")
            if "," in base64_string:
                _, base64_data = base64_string.split(",", 1)
            else:
                base64_data = base64_string

            decoded_bytes = base64.b64decode(base64_data)

            # 2. Wrap bytes in an in-memory file handle
            file_buffer = io.BytesIO(decoded_bytes)

            # 3. Basic integrity check: size
            if len(decoded_bytes) < 100:
                raise ValueError("Decoded file size is too small or file is empty.")

            print(
                f"Successfully decoded file of type {filetype}. Size: {len(decoded_bytes)} bytes."
            )

            return file_buffer

        except base64.binascii.Error:
            # Handle cases where the base64 string is malformed
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid base64 encoding for the file.",
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            # Catch any other unexpected decoding issues
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during decoding: {e}",
            )

    @staticmethod
    def extract_text(request: FileRequest):
        # Decode the file data into an in-memory buffer (io.BytesIO)
        file_buffer = FileController.decode_base64_file(
            request.base64_content, request.filetype
        )
        extracted_text = ""

        try:
            # 1. PDF Processing: Extract text using pypdf
            if request.filetype == "pdf":
                # The PdfReader takes the BytesIO buffer directly
                reader = PdfReader(file_buffer)
                # Iterate through all pages and extract text
                text_pages = [page.extract_text() for page in reader.pages]
                extracted_text = "\n".join(text_pages)

                if not extracted_text.strip():
                    raise ValueError(
                        "Could not extract any meaningful text from the PDF. It might be image-based or corrupted."
                    )

            # 2. DOCX Processing: Extract text using python-docx
            elif request.filetype in ["docx", "doc"]:
                # The Document class takes the BytesIO buffer directly
                document = Document(file_buffer)
                # Iterate through all paragraphs and join the text
                text_paragraphs = [paragraph.text for paragraph in document.paragraphs]
                extracted_text = "\n".join(text_paragraphs)

                if not extracted_text.strip():
                    raise ValueError(
                        "Could not extract any meaningful text from the DOCX file."
                    )

            # This safeguard is technically redundant due to Pydantic Literal, but good practice
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unsupported filetype specified for extraction.",
                )

        except Exception as e:
            # Handle exceptions during the file parsing (e.g., corrupted file structure, missing library)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to parse and extract text from the file. Ensure the file is valid and dependencies are installed: {e}",
            )

        # --- Response: Return the extracted text ---

        return {
            "filename": request.filename,
            "filetype": request.filetype,
            "extracted_text": extracted_text,
            "status": "Text extraction successful.",
        }
