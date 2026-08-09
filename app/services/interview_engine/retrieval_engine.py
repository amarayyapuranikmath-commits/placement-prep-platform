"""
AIRE Retrieval Engine
======================
Implements RE (#15): retrieval of curated interview knowledge before
generation, used both to ground follow-up/feedback generation (dialogue_engine)
and to verify generated claims (quality_engine).

Fast path: knowledge attached directly to the question (O(1), no search).
Fallback: vector search over a curated knowledge base via the injected
KnowledgeBaseRepositoryProtocol + EmbeddingProviderProtocol.
"""

from __future__ import annotations

from typing import Optional

from . import EmbeddingProviderProtocol, GapType, KnowledgeBaseRepositoryProtocol, QuestionMeta, RetrievedChunk

DEFAULT_TOP_K = 10
MAX_RETURNED_CHUNKS = 3
SIMILARITY_WEIGHT = 0.6
CORE_MATCH_WEIGHT = 0.4


class RetrievalEngine:
    def __init__(
        self,
        embedding_provider: EmbeddingProviderProtocol,
        knowledge_base_repo: KnowledgeBaseRepositoryProtocol,
    ) -> None:
        self._embed = embedding_provider
        self._kb = knowledge_base_repo

    async def retrieve(
        self,
        concept: str,
        question: QuestionMeta,
        gap_type: Optional[GapType] = None,
    ) -> list[RetrievedChunk]:
        attached = question.attached_knowledge.get(concept)
        if attached:
            return [
                RetrievedChunk(
                    text=chunk,
                    source_id=f"{question.question_id}:{concept}:{i}",
                    relevance_score=1.0,
                    is_core=True,
                )
                for i, chunk in enumerate(attached[:MAX_RETURNED_CHUNKS])
            ]

        query_text = self._build_query(concept, question, gap_type)
        query_vector = await self._embed.embed(query_text)
        candidates = await self._kb.vector_search(query_vector, top_k=DEFAULT_TOP_K)

        for chunk in candidates:
            chunk.relevance_score = (
                SIMILARITY_WEIGHT * chunk.relevance_score + CORE_MATCH_WEIGHT * (1.0 if chunk.is_core else 0.0)
            )

        ranked = sorted(candidates, key=lambda c: c.relevance_score, reverse=True)
        return ranked[:MAX_RETURNED_CHUNKS]

    def _build_query(self, concept: str, question: QuestionMeta, gap_type: Optional[GapType]) -> str:
        gap_label = gap_type.value if gap_type else ""
        return f"{concept} {question.topic} {gap_label}".strip()