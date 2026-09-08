from enum import Enum
from pathlib import Path
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class FileType(str, Enum):
    IMAGE = "image"
    PDF = "pdf"
    UNSUPPORTED = "unsupported"


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tiff",
    ".tif",
}


class DocumentFile(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    filename: str
    path: str
    mime_type: str | None = None
    file_type: FileType

    @classmethod
    def from_path(
        cls,
        path: str,
        mime_type: str | None = None,
    ) -> "DocumentFile":
        file_path = Path(path)

        if not file_path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        extension = file_path.suffix.lower()

        if extension in IMAGE_EXTENSIONS:
            file_type = FileType.IMAGE

        elif extension == ".pdf":
            file_type = FileType.PDF

        else:
            file_type = FileType.UNSUPPORTED

        return cls(
            filename=file_path.name,
            path=str(file_path),
            mime_type=mime_type,
            file_type=file_type,
        )

    def is_supported(self) -> bool:
        return self.file_type != FileType.UNSUPPORTED

class Document(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    file: DocumentFile
    ocr_html: str = ""
    text: str = ""