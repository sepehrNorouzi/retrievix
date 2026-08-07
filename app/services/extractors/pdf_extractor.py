import io

import pdfplumber

from app.services.extractors.base import TextExtractorBase


class PDFTextExtractor(TextExtractorBase):

    async def extract(self, content: bytes) -> str:
        text = ""
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return self.clean_text(text)