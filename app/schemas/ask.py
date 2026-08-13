from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class AskRequest(BaseModel):
    question: str
    top_k: int = 5
    include_sources: bool = True

class SourceChunk(BaseModel):
    chunk_id: UUID
    document_id: UUID
    text: str
    chunk_index: int
    score: float

class AskResponse(BaseModel):
    answer: str
    sources: Optional[List[SourceChunk]] = None
    model: str
