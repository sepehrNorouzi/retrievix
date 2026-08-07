from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, HTTPException
from qdrant_client import AsyncQdrantClient
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from app.shared.database import get_db
from app.services.document import DocumentService
from app.schemas.document import DocumentResponse, DocumentDetailResponse
from app.models.document import DocumentStatus
from app.shared.qdrant import get_qdrant

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    qdrant: AsyncQdrantClient = Depends(get_qdrant),
):
    service = DocumentService(qdrant_client=qdrant)
    doc = await service.create_document(
        file=file,
        db=db,
        title=title,
        background_tasks=background_tasks,
    )
    await db.refresh(doc)
    return DocumentResponse.model_validate(doc)

@router.get("/{doc_id}", response_model=DocumentDetailResponse)
async def get_document(
    doc_id: UUID,
    db: AsyncSession = Depends(get_db),
    qdrant: AsyncQdrantClient = Depends(get_qdrant),
):
    service = DocumentService(qdrant_client=qdrant)
    doc_detail = await service.get_document_with_chunks(doc_id, db)
    if not doc_detail:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc_detail

@router.get("/", response_model=list[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    status: Optional[DocumentStatus] = None,
    db: AsyncSession = Depends(get_db),
    qdrant: AsyncQdrantClient = Depends(get_qdrant),
):
    service = DocumentService(qdrant_client=qdrant)
    docs = await service.list_documents(db, skip=skip, limit=limit, status=status)
    return [DocumentResponse.model_validate(doc) for doc in docs]

@router.get("/{doc_id}/chunks", response_model=list[dict])
async def get_document_chunks(
    doc_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    qdrant: AsyncQdrantClient = Depends(get_qdrant),
):
    service = DocumentService(qdrant_client=qdrant)
    chunks = await service.get_chunks_for_document(doc_id, db, skip=skip, limit=limit)
    return [{"id": str(c.id), "index": c.chunk_index, "text": c.text, "token_count": c.token_count} for c in chunks]
