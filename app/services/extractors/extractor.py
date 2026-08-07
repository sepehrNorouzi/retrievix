from fastapi import UploadFile

from app.services.extractors.base import TextExtractorBase
from app.services.extractors.docx_extractor import DocxTextExtractor
from app.services.extractors.html_extractor import HTMLTextExtractor
from app.services.extractors.markdown_extractor import MarkdownTextExtractor
from app.services.extractors.pdf_extractor import PDFTextExtractor
from app.services.extractors.text_extractor import TxtTextExtractor


class TextExtractor:
    def __init__(self, file: UploadFile):
        self.file = file
        self.mime_type = file.content_type or ""

    async def extract(self) -> str:
        extractor = self.get_extractor()
        content = await self.file.read()
        return await extractor.extract(content=content)

    def get_extractor(self) -> TextExtractorBase:
        match self.mime_type:
            case "application/pdf":
                return PDFTextExtractor()
            case "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return DocxTextExtractor()
            case "text/plain":
                return TxtTextExtractor()
            case "text/markdown":
                return MarkdownTextExtractor()
            case "text/html":
                return HTMLTextExtractor()
            case _:
                raise ValueError(f"Unknown mime type: {self.mime_type}")
