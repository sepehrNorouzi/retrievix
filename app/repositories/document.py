# app/repositories/document.py
import uuid
from typing import Optional, List

from sqlalchemy import select, update, delete

from app.models.document import Document, DocumentStatus
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository):
    async def create(self, document: Document) -> Document:
        self.db.add(document)
        await self.db.flush()
        return document

    async def get_by_id(self, doc_id: uuid.UUID) -> Optional[Document]:
        result = await self.db.execute(
            select(Document).where(Document.id == doc_id)
        )
        return result.scalar_one_or_none()

    async def list(
            self,
            skip: int = 0,
            limit: int = 100,
            status: Optional[DocumentStatus] = None,
    ) -> List[Document]:
        query = select(Document)
        if status:
            query = query.where(Document.status == status)
        query = query.order_by(Document.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_status(self, doc_id: uuid.UUID, status: DocumentStatus) -> None:
        await self.db.execute(
            update(Document)
            .where(Document.id == doc_id)
            .values(status=status)
        )

    async def delete(self, doc_id: uuid.UUID) -> None:
        await self.db.execute(
            delete(Document).where(Document.id == doc_id)
        )
