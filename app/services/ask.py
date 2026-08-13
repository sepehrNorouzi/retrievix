from typing import Optional

from qdrant_client import AsyncQdrantClient

from app.schemas.ask import AskResponse, SourceChunk
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embedding.base import EmbeddingProvider
from app.ai.llm.base import LLMClient
from app.ai.llm.llm import get_llm_client
from app.repositories.chunk import ChunkRepository
from app.settings import settings


class AskService:
    def __init__(
            self,
            embedding_provider: EmbeddingProvider,
            qdrant_client,
            db: AsyncSession,
            llm_client: Optional[LLMClient] = None,
    ):
        self.embedder = embedding_provider
        self.qdrant: AsyncQdrantClient = qdrant_client
        self.db = db
        self.llm = llm_client or get_llm_client()

    async def ask(self, question: str, top_k: int = 5, include_sources: bool = False) -> AskResponse:
        query_vector = await self.embedder.embed(question)

        search_response = await self.qdrant.query_points(
            collection_name=settings.qdrant_collection,
            query=query_vector,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )

        search_results = search_response.points

        chunk_ids = [hit.id for hit in search_results]
        scores = {hit.id: hit.score for hit in search_results}

        chunk_repo = ChunkRepository(self.db)
        chunks = await chunk_repo.get_by_ids(chunk_ids)

        chunk_map = {str(c.id): c for c in chunks}

        context_parts = []
        sources = []

        for hit in search_results:
            chunk_id = hit.id
            chunk = chunk_map.get(str(chunk_id))

            if not chunk:
                continue

            context_parts.append(
                f"[Document {chunk.document_id}, Chunk {chunk.chunk_index}]\n"
                f"{chunk.text}"
            )

            sources.append(
                SourceChunk(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    text=chunk.text,
                    chunk_index=chunk.chunk_index,
                    score=scores.get(chunk_id, 0.0),
                )
            )

        context = "\n\n".join(context_parts)

        system_prompt = """You are a helpful assistant that answers questions based solely on the provided context.
    If the context does not contain enough information to answer, say so clearly.
    Always cite the source document IDs when referencing information.
    """

        user_prompt = f"""Context:
    {context}

    Question: {question}

    Answer:"""

        answer = await self.llm.generate(
            prompt=user_prompt,
            system=system_prompt,
            options={
                "temperature": 0.3,
                "max_tokens": 512,
            },
        )

        return AskResponse(
            answer=answer,
            sources=sources if include_sources else [],
            model=self.llm.model,
        )
