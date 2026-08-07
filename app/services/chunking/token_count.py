import tiktoken
ENCODING = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    """Count the number of tokens in a text using tiktoken."""
    return len(ENCODING.encode(text))
