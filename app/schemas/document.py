from uuid import UUID
from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional, List
from app.models.document import DocumentStatus

class DocumentCreate(BaseModel):
    """Schema for creating a document (metadata only; file is separate)."""
    title: Optional[str] = None
    # file is handled separately in the API

class DocumentResponse(BaseModel):
    """Schema for document response."""
    id: UUID
    title: str
    filename: str
    mime_type: str
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime
    chunk_count: Optional[int] = None  # optionally computed

    class Config:
        from_attributes = True

class ChunkResponse(BaseModel):
    """Schema for a single chunk."""
    id: UUID
    document_id: UUID
    chunk_index: int
    text: str
    token_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentDetailResponse(DocumentResponse):
    """Full document detail with chunks."""
    chunks: List[ChunkResponse] = []