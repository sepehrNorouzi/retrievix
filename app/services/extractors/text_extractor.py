from app.services.extractors.base import TextExtractorBase


class TxtTextExtractor(TextExtractorBase):

    async def extract(self, content: bytes) -> str:
        try:
            return self.clean_text(content.decode("utf-8"))
        except UnicodeDecodeError:
            # Try other encodings
            return self.clean_text(content.decode("uft-32"))
