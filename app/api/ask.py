from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embedding.embedding import get_embedding_provider
from app.schemas.ask import AskRequest, AskResponse
from app.services.ask import AskService
from app.shared.database import get_db
from app.shared.qdrant import get_qdrant

router = APIRouter(prefix="/ask", tags=["ask"])

@router.post("/", response_model=AskResponse)
async def ask_question(
    request: AskRequest,
    db: AsyncSession = Depends(get_db),
    qdrant = Depends(get_qdrant),
    embedder = Depends(get_embedding_provider),
):
    service = AskService(
        embedding_provider=embedder,
        qdrant_client=qdrant,
        db=db,
    )
    return await service.ask(question=request.question, top_k=request.top_k, include_sources=request.include_sources)