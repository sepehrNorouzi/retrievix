import io

import docx
from app.services.extractors.base import TextExtractorBase


class DocxTextExtractor(TextExtractorBase):

    def extract(self, content: bytes) -> str:
        doc = docx.getdocumenttext(io.BytesIO(content))
        paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text)
        return self.clean_text("\n".join(paragraphs))
