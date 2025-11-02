from pydantic import BaseModel, field_validator
from typing import Literal


class FileRequest(BaseModel):
    """
    Model for receiving a base64 encoded file payload from the frontend.
    """

    filename: str
    filetype: Literal["pdf", "docx", "doc", "txt"]  # Only allow 'pdf' or 'docx'
    base64_content: str  # The raw base64 string of the file

    @field_validator("base64_content")
    @classmethod
    def validate_base64(cls, v: str) -> str:
        """
        Ensures the base64 string is not empty.
        We'll handle decoding errors in the endpoint function.
        """
        if not v:
            raise ValueError("Base64 content cannot be empty.")
        return v
