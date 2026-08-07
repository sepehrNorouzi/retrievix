import uuid

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.shared.database import Base


class Chunk(Base):
    __tablename__ = "chunk"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(String, nullable=False)
    token_count = Column(Integer, nullable=False)
    qdrant_point_id = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_chunks_document_id", "document_id"),
        Index("idx_chunks_document_chunk_index", "document_id", "chunk_index", unique=True),
    )

    def __repr__(self):
        return f"<Chunk(id={self.id}, doc={self.document_id}, index={self.chunk_index})>"
