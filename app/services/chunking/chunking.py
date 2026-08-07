from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text_into_chunks(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    separators: List[str] = None,
) -> List[str]:
    """
    Split text into overlapping chunks using LangChain's recursive splitter.
    This respects paragraph, sentence, and word boundaries.
    """
    if separators is None:
        separators = ["\n\n", "\n", ". ", " ", ""]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
        length_function=len,
    )
    chunks = splitter.split_text(text)
    return chunks
