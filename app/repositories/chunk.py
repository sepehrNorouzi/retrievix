import uuid
from typing import List

from sqlalchemy import select, delete

from app.models.chunk import Chunk
from app.repositories.base import BaseRepository


class ChunkRepository(BaseRepository):
    async def create_batch(self, chunks: List[Chunk]) -> List[Chunk]:
        for chunk in chunks:
            self.db.add(chunk)
        await self.db.flush()
        return chunks

    async def get_by_document_id(
            self,
            doc_id: uuid.UUID,
            skip: int = 0,
            limit: int = 100,
    ) -> List[Chunk]:
        result = await self.db.execute(
            select(Chunk)
            .where(Chunk.document_id == doc_id)
            .order_by(Chunk.chunk_index)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def delete_by_document_id(self, doc_id: uuid.UUID) -> None:
        await self.db.execute(
            delete(Chunk).where(Chunk.document_id == doc_id)
        )
