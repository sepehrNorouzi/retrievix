import markdown
from bs4 import BeautifulSoup

from app.services.extractors.base import TextExtractorBase


class MarkdownTextExtractor(TextExtractorBase):

    def extract(self, content: bytes) -> str:
        html = markdown.markdown(content.decode("utf-8"))
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n")
        return self.clean_text(text)
