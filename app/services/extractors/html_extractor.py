from bs4 import BeautifulSoup

from app.services.extractors.base import TextExtractorBase


class HTMLTextExtractor(TextExtractorBase):

    async def extract(self, content: bytes) -> str:
        soup = BeautifulSoup(content.decode("utf-8"), "html.parser")
        text = soup.get_text(separator="\n")
        return self.clean_text(text)
