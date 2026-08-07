import enum
import uuid

from sqlalchemy import Column, String, DateTime, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.shared.database import Base


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    __table_args__ = (
        Index("idx_documents_status", "status"),
        Index("idx_documents_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title}, status={self.status})>"
