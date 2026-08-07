import uuid
from typing import Optional, List
from fastapi import UploadFile, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentStatus
from app.models.chunk import Chunk
from app.schemas.document import DocumentResponse, DocumentDetailResponse, ChunkResponse
from app.services.chunking.token_count import count_tokens
from app.services.extractors import TextExtractor
from app.services.chunking import split_text_into_chunks
from app.ai.embedding.embedding import get_embedding_provider
from app.shared.database import AsyncSessionLocal
from app.shared.qdrant import get_qdrant
from app.settings import settings
from app.repositories.document import DocumentRepository
from app.repositories.chunk import ChunkRepository

class DocumentService:
    def __init__(self, qdrant_client=None, embedding_provider=None):
        self.qdrant = qdrant_client or get_qdrant()
        self.embedder = embedding_provider or get_embedding_provider()

    async def create_document(
        self,
        file: UploadFile,
        db: AsyncSession,
        title: Optional[str] = None,
        background_tasks: BackgroundTasks = None,
    ) -> Document:
        """
        Create a new document record and start background processing.
        """
        doc_repo = DocumentRepository(db)
        doc = Document(
            title=title or file.filename,
            filename=file.filename,
            mime_type=file.content_type or "application/octet-stream",
            status=DocumentStatus.PENDING,
        )
        doc = await doc_repo.create(doc)
        await db.commit()
        if background_tasks:
            background_tasks.add_task(
                self._process_document,
                doc_id=doc.id,
                file=file,
                db_factory=AsyncSessionLocal(),
            )

        return doc

    async def _process_document(
        self,
        doc_id: uuid.UUID,
        file: UploadFile,
        db_factory,
    ):
        """
        Background task: extract, chunk, embed, and store.
        Uses its own database session to avoid conflicts with the request.
        """
        async with db_factory as db:
            doc_repo = DocumentRepository(db)
            chunk_repo = ChunkRepository(db)
            try:
                await doc_repo.update_status(doc_id, DocumentStatus.PROCESSING)
                await db.commit()

                extractor = TextExtractor(file=file)
                text = await extractor.extract()
                if not text:
                    raise ValueError("Extracted text is empty")

                chunk_texts = split_text_into_chunks(text=text, chunk_size=512, chunk_overlap=50)
                embeddings = await self.embedder.embed_batch(chunk_texts)
                collection = settings.qdrant_collection
                points = []
                chunks_to_insert = []
                for idx, (chunk_text, embedding) in enumerate(zip(chunk_texts, embeddings)):
                    chunk = Chunk(
                        document_id=doc_id,
                        chunk_index=idx,
                        text=chunk_text,
                        token_count=count_tokens(text=text)
                    )
                    chunks_to_insert.append(chunk)
                chunks = await chunk_repo.create_batch(chunks_to_insert)
                for idx, chunk in enumerate(chunks):
                    point_id = str(chunk.id)
                    payload = {
                        "document_id": str(doc_id),
                        "chunk_id": point_id,
                        "chunk_index": idx,
                    }
                    points.append({
                        "id": point_id,
                        "vector": embeddings[idx],
                        "payload": payload,
                    })
                    chunk.qdrant_point_id = point_id
                if points:
                    await self.qdrant.upsert(collection_name=collection, points=points)

                await doc_repo.update_status(doc_id, DocumentStatus.COMPLETED)
                await db.commit()

            except Exception as e:
                from app.shared.logger import get_logger
                logger = get_logger()
                logger.error(f"Document {doc_id} processing failed: {e}", exc_info=True)

                await doc_repo.update_status(doc_id, DocumentStatus.FAILED)
                await db.commit()

    async def get_document_with_chunks(
        self,
        doc_id: uuid.UUID,
        db: AsyncSession,
    ) -> Optional[DocumentDetailResponse]:
        doc_repo = DocumentRepository(db)
        chunk_repo = ChunkRepository(db)

        doc = await doc_repo.get_by_id(doc_id)
        if not doc:
            return None

        chunks = await chunk_repo.get_by_document_id(doc_id)
        chunk_responses = [ChunkResponse.model_validate(chunk) for chunk in chunks]
        doc_response = DocumentResponse.model_validate(doc)
        return DocumentDetailResponse(
            **doc_response.model_dump(),
            chunks=chunk_responses,
        )

    async def list_documents(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[DocumentStatus] = None,
    ) -> List[Document]:
        doc_repo = DocumentRepository(db)
        return await doc_repo.list(skip=skip, limit=limit, status=status)

    async def get_chunks_for_document(
        self,
        doc_id: uuid.UUID,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Chunk]:
        chunk_repo = ChunkRepository(db)
        return await chunk_repo.get_by_document_id(doc_id, skip=skip, limit=limit)