import json
import logging
import uuid
from datetime import datetime
from typing import Any, Optional

import httpx
import asyncio
import inspect
import random
import hashlib
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import get_settings
from app.models.profile import PROFILES_COLLECTION
from app.services.interview_engine import (
    AnswerLengthClass,
    CandidateProfileRepositoryProtocol,
    EmbeddingProviderProtocol,
    GroqClientProtocol,
    InterviewerPersona,
    KnowledgeBaseRepositoryProtocol,
    QuestionBankRepositoryProtocol,
    QuestionMeta,
    RetrievedChunk,
    SessionRepositoryProtocol,
    Verdict,
    utcnow,
)
from app.services.interview_engine.adaptivity_engine import AdaptivityEngine
from app.services.interview_engine.dialogue_engine import DialogueEngine
from app.services.interview_engine.groq_evaluation_engine import GroqEvaluationEngine
from app.services.interview_engine.orchestrator import InterviewOrchestrator
from app.services.interview_engine.memory_engine import MemoryEngine
from app.services.interview_engine.quality_engine import QualityEngine
from app.services.interview_engine.retrieval_engine import RetrievalEngine
from app.utils.groq_client import GROQ_CHAT_COMPLETIONS_URL, GROQ_MODEL

logger = logging.getLogger(__name__)
settings = get_settings()


class GroqClientAdapter(GroqClientProtocol):
    # instrumentation counters for analysis (engine -> count)
    ENGINE_CALL_COUNTERS: dict[str, int] = {}
    RATE_LIMIT_HIT_COUNT: int = 0

    def __init__(self) -> None:
        self._client: Optional[httpx.AsyncClient] = None
        # simple in-memory cache for deterministic responses (temperature==0.0)
        self._cache: dict[str, str] = {}

    async def complete(
        self,
        messages: list[dict[str, str]],
        *,
        max_tokens: int = 256,
        temperature: float = 0.4,
        json_mode: bool = False,
    ) -> str:
        if not settings.GROQ_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Interview AI service is temporarily unavailable.",
            )

        payload: dict[str, Any] = {
            "model": GROQ_MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}

        # Use a persistent client for connection reuse
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60.0)

        # Simple deterministic-response cache for temperature==0.0
        cache_key = None
        if temperature == 0.0:
            try:
                key_raw = json.dumps(payload, sort_keys=True)
                cache_key = hashlib.sha256(key_raw.encode("utf-8")).hexdigest()
                if cache_key in self._cache:
                    return self._cache[cache_key]
            except Exception:
                cache_key = None

        max_retries = 4
        backoff = 0.5
        data = None
        for attempt in range(1, max_retries + 1):
            try:
                response = await self._client.post(
                    GROQ_CHAT_COMPLETIONS_URL,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
                break
            except httpx.HTTPStatusError as exc:
                status_code = getattr(exc.response, "status_code", None)
                logger.warning(
                    "Groq API status error (attempt %s/%s): %s",
                    attempt,
                    max_retries,
                    status_code,
                )
                if status_code == 429:
                    GroqClientAdapter.RATE_LIMIT_HIT_COUNT += 1
                should_retry = exc.response.headers.get("x-should-retry", "true").lower() != "false"
                if (
                    status_code not in (429, 502, 503, 504)
                    or attempt == max_retries
                    or not should_retry
                ):
                    logger.exception("Interview Groq API request failed")
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Interview AI service is currently unavailable.",
                    ) from exc
                # exponential backoff with jitter
                # If Groq returned a Retry-After header, respect it exactly
                retry_after = None
                try:
                    hdr = exc.response.headers.get("retry-after")
                    if hdr is not None:
                        # usually a seconds value; fall back to float conversion
                        retry_after = float(hdr)
                except Exception:
                    retry_after = None

                jitter = random.uniform(0, backoff)
                sleep_for = backoff + jitter
                if retry_after is not None:
                    # Add a small jitter to reduce synchronized retries
                    sleep_for = max(sleep_for, retry_after + random.uniform(0, 0.5))

                await asyncio.sleep(sleep_for)
                backoff = min(backoff * 2, 30.0)
            except httpx.HTTPError as exc:
                logger.warning("Groq API network error (attempt %s/%s)", attempt, max_retries)
                if attempt == max_retries:
                    logger.exception("Interview Groq API request failed")
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Interview AI service is currently unavailable.",
                    ) from exc
                jitter = random.uniform(0, backoff)
                await asyncio.sleep(backoff + jitter)
                backoff *= 2

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            logger.exception("Interview Groq response parsing failed")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Received an invalid response from the interview AI service.",
            ) from exc

        # Instrumentation: attribute this Groq call to a calling engine by scanning the stack
        try:
            stack = inspect.stack()
            engine = "other"
            for frame_info in stack:
                fname = frame_info.filename or ""
                if "interview_engine" in fname:
                    if fname.endswith("comprehension_engine.py"):
                        engine = "Comprehension Engine"
                        break
                    if fname.endswith("retrieval_engine.py"):
                        engine = "Retrieval Engine"
                        break
                    if fname.endswith("evaluation_engine.py"):
                        engine = "Evaluation Engine"
                        break
                    if fname.endswith("dialogue_engine.py"):
                        engine = "Dialogue Engine"
                        break
                    if fname.endswith("quality_engine.py"):
                        engine = "Quality Engine"
                        break
                    # fallback: infer from filename
                    engine = fname.split("\\")[-1]
                    break
            GroqClientAdapter.ENGINE_CALL_COUNTERS[engine] = GroqClientAdapter.ENGINE_CALL_COUNTERS.get(engine, 0) + 1
        except Exception:
            pass

        if json_mode and isinstance(content, dict):
            return json.dumps(content)
        return str(content)


class SimpleEmbeddingProvider(EmbeddingProviderProtocol):
    async def embed(self, text: str) -> list[float]:
        normalized = text.lower()
        counts = {chr(ord("a") + idx): 0 for idx in range(26)}
        for ch in normalized:
            if ch in counts:
                counts[ch] += 1
        length = max(len(normalized), 1)
        return [counts[chr(ord("a") + idx)] / length for idx in range(26)]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [await self.embed(text) for text in texts]


class CandidateProfileRepository(CandidateProfileRepositoryProtocol):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db[PROFILES_COLLECTION]

    async def get_profile(self, candidate_id: str) -> dict[str, Any]:
        document = await self._collection.find_one({"user_id": candidate_id})
        if document is None:
            document = {
                "user_id": candidate_id,
                "concept_mastery": {},
                "session_count": 0,
                "last_active": utcnow().isoformat(),
                "created_at": utcnow().isoformat(),
                "updated_at": utcnow().isoformat(),
            }
            await self._collection.insert_one(document)
        return document

    async def save_profile(self, candidate_id: str, profile: dict[str, Any]) -> None:
        payload = dict(profile)
        payload.pop("_id", None)
        payload.pop("created_at", None)
        payload["user_id"] = candidate_id
        payload["updated_at"] = utcnow().isoformat()
        await self._collection.update_one(
            {"user_id": candidate_id},
            {
                "$set": payload,
                "$setOnInsert": {
                    "created_at": utcnow().isoformat(),
                },
            },
            upsert=True,
        )


class SessionRepository(SessionRepositoryProtocol):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db["interview_sessions"]
        self._archive_collection = db["interview_session_archives"]

    async def get_state(self, session_id: str) -> Optional[dict[str, Any]]:
        return await self._collection.find_one({"session_id": session_id})

    async def save_state(self, session_id: str, state: dict[str, Any]) -> None:
        payload = dict(state)
        payload.pop("_id", None)
        payload.pop("session_id", None)
        payload["updated_at"] = utcnow().isoformat()
        # Keep top-level session metadata (like question_id) in sync when present in state.
        top_level_set: dict[str, Any] = {
            "state": payload,
            "session_id": session_id,
            "updated_at": utcnow().isoformat(),
        }
        # If state includes an explicit question_id, mirror it to the document root
        if payload.get("question_id"):
            top_level_set["question_id"] = payload.get("question_id")

        await self._collection.update_one(
            {"session_id": session_id},
            {
                "$set": top_level_set,
                "$setOnInsert": {
                    "created_at": utcnow().isoformat(),
                },
            },
            upsert=True,
        )

    async def get_history(self, candidate_id: str) -> list[dict[str, Any]]:
        cursor = self._collection.find(
            {"candidate_id": candidate_id, "state.status": "completed"},
            sort=[("updated_at", -1)],
        )
        sessions: list[dict[str, Any]] = []
        async for document in cursor:
            sessions.append(document)
        return sessions

    async def archive_state(self, session_id: str, summary: dict[str, Any]) -> None:
        await self._archive_collection.insert_one(
            {
                "session_id": session_id,
                "summary": summary,
                "archived_at": utcnow().isoformat(),
            }
        )

    async def delete_state(self, session_id: str) -> None:
        await self._collection.delete_one({"session_id": session_id})

    async def create_session(
        self,
        session_id: str,
        candidate_id: str,
        question_id: str,
        persona: Optional[dict[str, Any]] = None,
        state: Optional[dict[str, Any]] = None,
    ) -> None:
        await self._collection.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "candidate_id": candidate_id,
                    "question_id": question_id,
                    "persona": persona,
                    "state": state or {},
                    "updated_at": utcnow().isoformat(),
                },
                "$setOnInsert": {
                    "session_id": session_id,
                    "created_at": utcnow().isoformat(),
                },
            },
            upsert=True,
        )


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class KnowledgeBaseRepository(KnowledgeBaseRepositoryProtocol):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db["knowledge_base"]

    async def vector_search(self, query_vector: list[float], top_k: int = 10) -> list[RetrievedChunk]:
        cursor = self._collection.find({"vector": {"$exists": True}})
        candidates: list[RetrievedChunk] = []
        async for document in cursor:
            vector = document.get("vector")
            if not isinstance(vector, list) or len(vector) != len(query_vector):
                continue
            score = _cosine_similarity(query_vector, vector)
            candidates.append(
                RetrievedChunk(
                    text=document.get("text", ""),
                    source_id=document.get("source_id", str(document.get("_id", ""))),
                    relevance_score=score,
                    is_core=document.get("is_core", False),
                )
            )
        candidates.sort(key=lambda chunk: chunk.relevance_score, reverse=True)
        return candidates[:top_k]


class QuestionBankRepository(QuestionBankRepositoryProtocol):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db["interview_questions"]

    async def get_question(self, question_id: str) -> QuestionMeta:
        query = {"question_id": question_id}
        document = await self._collection.find_one(query)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interview question not found: {question_id}",
            )

        return QuestionMeta.model_validate(document)

    async def select_question(self, config: dict[str, Any]) -> QuestionMeta:
        base_query = self._build_query(config)
        query = dict(base_query)
        exclude_ids = config.get("exclude_question_ids") or config.get("asked_question_ids") or []
        if exclude_ids:
            query["question_id"] = {"$nin": list(exclude_ids)}

        cursor = self._collection.find(query).sort([("difficulty_rating", 1)]).limit(50)
        candidates = await cursor.to_list(length=50)

        if not candidates and base_query:
            interview_type = str(config.get("interview_type") or "").strip().lower()
            if interview_type and interview_type != "mixed":
                fallback_query = self._build_broad_query(config)
                if exclude_ids:
                    fallback_query["question_id"] = {"$nin": list(exclude_ids)}
                cursor = self._collection.find(fallback_query).sort([("difficulty_rating", 1)]).limit(50)
                candidates = await cursor.to_list(length=50)
            else:
                difficulty_only_query = self._build_difficulty_only_query(config)
                if difficulty_only_query != query:
                    cursor = self._collection.find(difficulty_only_query).sort([("difficulty_rating", 1)]).limit(50)
                    candidates = await cursor.to_list(length=50)

        if not candidates:
            cursor = self._collection.find({"active": True}).sort([("difficulty_rating", 1)]).limit(50)
            candidates = await cursor.to_list(length=50)

        if not candidates:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No interview question found for the provided configuration",
            )

        # Prefer questions close to the requested difficulty and randomize among top options.
        candidates.sort(key=lambda doc: abs(doc.get("difficulty_rating", 1200.0) - self._difficulty_target(config)))
        top_choices = candidates[: min(len(candidates), 10)]
        document = random.choice(top_choices)
        return QuestionMeta.model_validate(document)

    async def select_question_strict(
        self,
        interview_type: str,
        difficulty: str,
        asked_question_ids: list[str] | None = None,
        exclude_topics: list[str] | None = None,
        role: str | None = None,
        experience_level: str | None = None,
        company_type: str | None = None,
    ) -> QuestionMeta:
        query: dict[str, Any] = {"interview_type": interview_type, "active": True}
        if difficulty in {"easy", "medium", "hard"}:
            query["difficulty_rating"] = {"$lte": self._difficulty_threshold(difficulty)}

        if asked_question_ids:
            query["question_id"] = {"$nin": asked_question_ids}

        if exclude_topics:
            query["topic"] = {"$nin": exclude_topics}

        if role and role.lower() != "any":
            query = {"$and": [query, {"$or": [{"role": role}, {"role": "Any"}]}]}

        if experience_level and experience_level.lower() != "any":
            query = {"$and": [query, {"$or": [{"experience_level": experience_level}, {"experience_level": "Any"}]}]}

        if company_type and company_type.lower() != "any":
            query = {"$and": [query, {"$or": [{"company_type": company_type}, {"company_type": "any"}]}]}

        candidates = await self._collection.find(query).sort([("difficulty_rating", 1)]).limit(50).to_list(length=50)
        if not candidates and exclude_topics:
            followup_query = dict(query)
            followup_query.pop("topic", None)
            candidates = await self._collection.find(followup_query).sort([("difficulty_rating", 1)]).limit(50).to_list(length=50)
        if not candidates and difficulty in {"easy", "medium", "hard"}:
            fallback_query = dict(query)
            fallback_query.pop("difficulty_rating", None)
            candidates = await self._collection.find(fallback_query).sort([("difficulty_rating", 1)]).limit(50).to_list(length=50)

        if not candidates:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No interview question found for mixed section: {interview_type}",
            )

        candidates.sort(key=lambda doc: abs(doc.get("difficulty_rating", 1200.0) - self._difficulty_threshold(difficulty)))
        document = random.choice(candidates[: min(len(candidates), 10)])
        return QuestionMeta.model_validate(document)

    def _build_query(self, config: dict[str, Any]) -> dict[str, Any]:
        interview_type = str(config.get("interview_type") or "").strip().lower()
        topic_candidates = self._topic_candidates_for(interview_type)

        query: dict[str, Any] = {}
        if interview_type:
            query = {
                "$or": [
                    {"interview_type": interview_type},
                    {"topic": {"$in": topic_candidates}},
                    {"topic": interview_type},
                ]
            }

        difficulty = str(config.get("difficulty") or "").strip().lower()
        if difficulty in {"easy", "medium", "hard"}:
            if query:
                query = {"$and": [query, {"difficulty_rating": {"$lte": self._difficulty_threshold(difficulty)}}]}
            else:
                query = {"difficulty_rating": {"$lte": self._difficulty_threshold(difficulty)}}

        role = str(config.get("role") or "").strip().lower()
        if role and role != "any":
            query = {"$and": [query, {"$or": [{"role": role}, {"role": "Any"}]}]} if query else {"$or": [{"role": role}, {"role": "Any"}]}

        experience_level = str(config.get("experience_level") or "").strip().lower()
        if experience_level and experience_level != "any":
            query = {"$and": [query, {"$or": [{"experience_level": experience_level}, {"experience_level": "Any"}]}]} if query else {"$or": [{"experience_level": experience_level}, {"experience_level": "Any"}]}

        company_type = str(config.get("company_type") or "").strip().lower()
        if company_type and company_type != "any":
            query = {"$and": [query, {"$or": [{"company_type": company_type}, {"company_type": "any"}]}]} if query else {"$or": [{"company_type": company_type}, {"company_type": "any"}]}

        return query

    def _build_broad_query(self, config: dict[str, Any]) -> dict[str, Any]:
        interview_type = str(config.get("interview_type") or "").strip().lower()
        topic_candidates = self._topic_candidates_for(interview_type)

        query: dict[str, Any] = {"interview_type": interview_type} if interview_type else {}
        if topic_candidates:
            query = {"$or": [query, {"topic": {"$in": topic_candidates}}]} if query else {"topic": {"$in": topic_candidates}}

        difficulty = str(config.get("difficulty") or "").strip().lower()
        if difficulty in {"easy", "medium", "hard"}:
            if query:
                query = {"$and": [query, {"difficulty_rating": {"$lte": self._difficulty_threshold(difficulty)}}]}
            else:
                query = {"difficulty_rating": {"$lte": self._difficulty_threshold(difficulty)}}

        role = str(config.get("role") or "").strip().lower()
        if role and role != "any":
            query = {"$and": [query, {"$or": [{"role": role}, {"role": "Any"}]}]} if query else {"$or": [{"role": role}, {"role": "Any"}]}

        experience_level = str(config.get("experience_level") or "").strip().lower()
        if experience_level and experience_level != "any":
            query = {"$and": [query, {"$or": [{"experience_level": experience_level}, {"experience_level": "Any"}]}]} if query else {"$or": [{"experience_level": experience_level}, {"experience_level": "Any"}]}

        company_type = str(config.get("company_type") or "").strip().lower()
        if company_type and company_type != "any":
            query = {"$and": [query, {"$or": [{"company_type": company_type}, {"company_type": "any"}]}]} if query else {"$or": [{"company_type": company_type}, {"company_type": "any"}]}

        return query

    def _build_difficulty_only_query(self, config: dict[str, Any]) -> dict[str, Any]:
        difficulty = str(config.get("difficulty") or "").strip().lower()
        if difficulty in {"easy", "medium", "hard"}:
            return {"difficulty_rating": {"$lte": self._difficulty_threshold(difficulty)}}
        return {}

    def _difficulty_target(self, config: dict[str, Any]) -> float:
        difficulty = str(config.get("difficulty") or "").strip().lower()
        return {
            "easy": 1050.0,
            "medium": 1400.0,
            "hard": 1650.0,
        }.get(difficulty, 1200.0)

    def _topic_candidates_for(self, interview_type: str) -> list[str]:
        mapping = {
            "technical": ["algorithms", "data structures", "problem solving", "system design", "technical"],
            "hr": ["hr", "behavioral", "culture fit", "communication", "leadership", "motivation"],
            "behavioral": ["behavioral", "leadership", "teamwork", "conflict", "situational"],
            "system_design": ["system design", "architecture", "scalability", "distributed systems"],
            "system": ["system design", "architecture", "scalability", "distributed systems"],
            "mixed": ["technical", "hr", "behavioral", "system_design", "general"],
        }
        return mapping.get(interview_type, ["technical", "behavioral", "system design", "general"])

    def _difficulty_threshold(self, difficulty: str) -> float:
        return {"easy": 1100.0, "medium": 1400.0, "hard": 1700.0}.get(difficulty, 1400.0)


class InterviewService:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.groq_client = GroqClientAdapter()
        self.embedding_provider = SimpleEmbeddingProvider()
        self.profile_repo = CandidateProfileRepository(db)
        self.session_repo = SessionRepository(db)
        self.question_repo = QuestionBankRepository(db)
        self.kb_repo = KnowledgeBaseRepository(db)
        self.orchestrator = InterviewOrchestrator(
            evaluation_engine=GroqEvaluationEngine(self.groq_client),
            retrieval_engine=RetrievalEngine(self.embedding_provider, self.kb_repo),
            adaptivity_engine=AdaptivityEngine(),
            dialogue_engine=DialogueEngine(self.groq_client, self.embedding_provider),
            quality_engine=QualityEngine(self.groq_client),
            memory_engine=MemoryEngine(self.session_repo, self.profile_repo),
        )

    async def create_session(
        self,
        candidate_id: str,
        interview_config: dict[str, Any] | str,
        persona: Optional[InterviewerPersona] = None,
    ) -> dict[str, Any]:
        if isinstance(interview_config, str):
            interview_config = {"interview_type": interview_config}

        normalized_config = {k: v for k, v in interview_config.items() if v is not None}
        interview_type = str(normalized_config.get("interview_type") or "technical").strip().lower()
        question_id = normalized_config.get("question_id")
        session_id = uuid.uuid4().hex
        timer_seconds = self._resolve_timer_seconds(normalized_config)
        started_at = utcnow().isoformat()

        interview_state = {
            "session_id": session_id,
            "candidate_id": candidate_id,
            "interview_type": interview_type,
            "question_index": 0,
            "status": "ready",
            "config": normalized_config,
            "timer": {"duration_seconds": timer_seconds, "started": False},
            "started_at": started_at,
        }

        if interview_type == "mixed" and question_id is None:
            mixed_plan = self._build_mixed_plan(normalized_config)
            first_section = mixed_plan[0]
            selected_question = await self._select_mixed_question_for_section(
                first_section,
                asked_question_ids=[],
                exclude_topics=[],
                config=normalized_config,
            )
            interview_state.update(
                {
                    "is_mixed": True,
                    "mixed_plan": mixed_plan,
                    "mixed_current_section": 0,
                    "mixed_asked_question_ids": [selected_question.question_id],
                    "mixed_topics": [selected_question.topic],
                    "question_id": selected_question.question_id,
                    "question_interview_type": first_section["interview_type"],
                }
            )
        else:
            if question_id:
                selected_question = await self.question_repo.get_question(question_id)
            else:
                selected_question = await self.question_repo.select_question(normalized_config)
            interview_state["question_id"] = selected_question.question_id
            interview_state["question_interview_type"] = selected_question.interview_type

        await self.session_repo.create_session(
            session_id=session_id,
            candidate_id=candidate_id,
            question_id=selected_question.question_id,
            persona=persona.model_dump(mode="json") if persona else None,
            state=interview_state,
        )
        return {
            "session_id": session_id,
            "question": selected_question.model_dump(mode="json"),
            "timer": interview_state["timer"],
            "interview_state": interview_state,
        }

    def _resolve_timer_seconds(self, interview_config: dict[str, Any]) -> int:
        duration = str(interview_config.get("duration") or "").strip().lower()
        if duration.endswith("m"):
            try:
                return int(float(duration[:-1])) * 60
            except ValueError:
                return 1800
        if duration.endswith("h"):
            try:
                return int(float(duration[:-1])) * 3600
            except ValueError:
                return 1800
        return 1800

    def _build_mixed_plan(self, config: dict[str, Any]) -> list[dict[str, Any]]:
        role = str(config.get("role") or "").strip().lower()
        experience_level = str(config.get("experience_level") or "").strip().lower()
        duration_seconds = config.get("duration")
        if isinstance(duration_seconds, str) and duration_seconds.endswith("m"):
            try:
                duration_seconds = int(float(duration_seconds[:-1])) * 60
            except Exception:
                duration_seconds = 1800
        elif isinstance(duration_seconds, (int, float)):
            duration_seconds = int(duration_seconds)
        else:
            duration_seconds = 1800

        include_system = self._should_include_system_design(role, experience_level, duration_seconds)
        plan = [
            {
                "section_name": "Introduction",
                "interview_type": "hr",
                "difficulty": "easy",
            },
            {
                "section_name": "Technical Fundamentals",
                "interview_type": "technical",
                "difficulty": "medium" if experience_level != "entry" else "easy",
            },
            {
                "section_name": "Behavioral",
                "interview_type": "behavioral",
                "difficulty": "easy",
            },
            {
                "section_name": "Technical Problem Solving",
                "interview_type": "technical",
                "difficulty": "medium" if experience_level != "entry" else "easy",
            },
        ]
        if include_system:
            plan.append(
                {
                    "section_name": "System Design",
                    "interview_type": "system_design",
                    "difficulty": "medium",
                }
            )
        plan.append(
            {
                "section_name": "HR Closing",
                "interview_type": "hr",
                "difficulty": "easy",
            }
        )
        return plan

    def _should_include_system_design(self, role: str, experience_level: str, duration_seconds: int) -> bool:
        if experience_level in {"senior", "lead", "principal", "architect"}:
            return True
        if any(key in role for key in ["senior", "architect", "lead", "principal"]):
            return True
        if any(key in role for key in ["backend", "frontend", "full stack", "full-stack", "software"]):
            return duration_seconds >= 1500
        return False

    def _compute_mixed_section_difficulty(
        self,
        section: dict[str, Any],
        previous_scores: list[int],
        experience_level: str,
    ) -> str:
        if section["interview_type"] == "technical":
            if previous_scores and sum(previous_scores) / len(previous_scores) >= 75:
                return "hard" if experience_level != "entry" else "medium"
            if previous_scores and sum(previous_scores) / len(previous_scores) >= 55:
                return "medium"
            return "easy"
        if section["interview_type"] == "system_design":
            return "medium" if experience_level != "entry" else "easy"
        return "easy"

    async def _select_mixed_question_for_section(
        self,
        section: dict[str, Any],
        asked_question_ids: list[str],
        exclude_topics: list[str],
        config: dict[str, Any],
    ) -> QuestionMeta:
        return await self.question_repo.select_question_strict(
            interview_type=section["interview_type"],
            difficulty=section["difficulty"],
            asked_question_ids=asked_question_ids,
            exclude_topics=exclude_topics,
            role=str(config.get("role") or "Any").strip(),
            experience_level=str(config.get("experience_level") or "Any").strip(),
            company_type=str(config.get("company_type") or "any").strip(),
        )

    async def _advance_mixed_section(
        self,
        persisted_state: dict[str, Any],
        current_question: QuestionMeta,
        result: Any,
    ) -> None:
        if not persisted_state.get("is_mixed"):
            return

        plan = persisted_state.get("mixed_plan") or []
        current_index = persisted_state.get("mixed_current_section", 0)
        next_index = current_index + 1
        if next_index >= len(plan):
            return

        evaluation_score = int(round(getattr(getattr(result, "verdict", None), "score", 0.0))) if getattr(getattr(result, "verdict", None), "score", None) is not None else 0
        section_result = {
            "section_name": plan[current_index]["section_name"],
            "question_id": current_question.question_id,
            "interview_type": plan[current_index]["interview_type"],
            "score": evaluation_score,
            "communication_score": self._estimate_communication_score(
                getattr(getattr(result, "answer", None), "answer_length_class", AnswerLengthClass.ADEQUATE)
            ),
            "question_topic": current_question.topic,
        }
        persisted_state.setdefault("mixed_section_results", []).append(section_result)

        if next_index >= len(plan):
            persisted_state["mixed_complete"] = True
            return

        previous_scores = [item["score"] for item in persisted_state["mixed_section_results"] if item["interview_type"] == plan[next_index]["interview_type"]]
        if previous_scores:
            plan[next_index]["difficulty"] = self._compute_mixed_section_difficulty(
                plan[next_index], previous_scores, str(persisted_state.get("config", {}).get("experience_level") or "entry").lower()
            )

        next_section = plan[next_index]
        next_question = await self._select_mixed_question_for_section(
            next_section,
            asked_question_ids=list(persisted_state.get("mixed_asked_question_ids") or []),
            exclude_topics=list(persisted_state.get("mixed_topics") or []),
            config=persisted_state.get("config") or {},
        )

        persisted_state["question_id"] = next_question.question_id
        persisted_state["question_interview_type"] = next_section["interview_type"]
        persisted_state["mixed_current_section"] = next_index
        persisted_state.setdefault("mixed_asked_question_ids", []).append(next_question.question_id)
        persisted_state.setdefault("mixed_topics", []).append(next_question.topic)
        persisted_state["mixed_plan"] = plan

    async def _build_mixed_report(self, evaluations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        sections: list[dict[str, Any]] = []
        for evaluation in evaluations:
            sections.append(
                {
                    "interview_type": evaluation.get("question_interview_type"),
                    "question_id": evaluation.get("question_id"),
                    "question_text": evaluation.get("question_text"),
                    "score": evaluation.get("score", 0),
                    "communication_score": evaluation.get("communication_score", 0),
                    "evaluation": evaluation.get("evaluation"),
                }
            )
        return sections

    def _group_performance_by_type(self, evaluations: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        groups: dict[str, list[dict[str, Any]]] = {}
        for evaluation in evaluations:
            key = evaluation.get("question_interview_type", "unknown")
            groups.setdefault(key, []).append(evaluation)
        performance: dict[str, dict[str, Any]] = {}
        for interview_type, items in groups.items():
            scores = [item.get("score", 0) for item in items]
            comms = [item.get("communication_score", 0) for item in items]
            performance[interview_type] = {
                "count": len(items),
                "average_score": int(round(sum(scores) / len(scores))) if scores else 0,
                "average_communication_score": int(round(sum(comms) / len(comms))) if comms else 0,
            }
        return performance

    def _build_turn_evaluation_summary(self, result: Any) -> dict[str, Any]:
        score = int(round(getattr(getattr(result, "verdict", None), "score", 0.0))) if getattr(getattr(result, "verdict", None), "score", None) is not None else 0
        verdict = getattr(getattr(result, "verdict", None), "verdict", None)
        missing_concepts = [getattr(gap, "concept", "") for gap in getattr(result, "gaps", []) or []]
        communication_score = self._estimate_communication_score(
            getattr(getattr(result, "answer", None), "answer_length_class", AnswerLengthClass.ADEQUATE)
        )
        strengths: list[str] = []
        weaknesses: list[str] = []
        if score >= 80:
            strengths.append("Clear, confident coverage of the key concepts.")
        if score >= 60 and score < 80:
            strengths.append("Good understanding with some room for deeper detail.")
        if score < 60:
            weaknesses.append("The response needs stronger clarity and more core coverage.")
        if communication_score < 70:
            weaknesses.append("Answer structure and clarity could be improved.")
        if missing_concepts and not strengths:
            weaknesses.append("Focus on the missing concept areas listed below.")

        evaluation_recommendations = self._recommendations_from_result(result)
        follow_up_reasoning = getattr(getattr(result, "followup", None), "text", None)

        return {
            "score": score,
            "verdict": verdict.value if verdict is not None else None,
            "communication_score": communication_score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": evaluation_recommendations,
            "missing_concepts": missing_concepts,
            "follow_up_reasoning": follow_up_reasoning,
        }

    async def fetch_question(self, question_id: str) -> QuestionMeta:
        return await self.question_repo.get_question(question_id)

    async def complete_session(self, session_id: str, candidate_id: str) -> dict[str, Any]:
        session = await self.session_repo.get_state(session_id)
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found",
            )
        if session.get("candidate_id") != candidate_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this interview session",
            )

        persisted_state = dict(session.get("state") or {})
        if persisted_state.get("status") == "completed" and persisted_state.get("report"):
            return persisted_state["report"]

        persisted_state["status"] = "completed"
        completed_at = utcnow().isoformat()
        persisted_state["completed_at"] = completed_at
        persisted_state.setdefault("started_at", utcnow().isoformat())

        report = self._build_report(session, persisted_state)
        persisted_state["report"] = report
        await self.session_repo.save_state(session_id, persisted_state)
        return report

    async def get_report(self, session_id: str, candidate_id: str) -> dict[str, Any]:
        session = await self.session_repo.get_state(session_id)
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found",
            )
        if session.get("candidate_id") != candidate_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this interview session",
            )

        persisted_state = dict(session.get("state") or {})
        report = persisted_state.get("report")
        if report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview report not found",
            )
        return report

    async def get_history(self, candidate_id: str) -> list[dict[str, Any]]:
        sessions = await self.session_repo.get_history(candidate_id)
        history: list[dict[str, Any]] = []
        for session in sessions:
            state = session.get("state") or {}
            report = state.get("report") or {}
            history.append(
                {
                    "session_id": session.get("session_id", ""),
                    "interview_type": state.get("interview_type"),
                    "role": state.get("config", {}).get("role"),
                    "date": state.get("completed_at") or session.get("updated_at"),
                    "score": report.get("overall_score", 0),
                    "status": state.get("status", "completed"),
                    "duration": self._format_duration(state.get("started_at"), state.get("completed_at")),
                }
            )
        return history

    def _format_duration(self, started_at: Optional[str], completed_at: Optional[str]) -> str:
        try:
            if started_at and completed_at:
                start = datetime.fromisoformat(started_at)
                end = datetime.fromisoformat(completed_at)
                seconds = int((end - start).total_seconds())
                minutes = seconds // 60
                return f"{minutes}m {seconds % 60}s"
        except Exception:
            pass
        return "0m 0s"

    def _build_report(self, session: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        question_evaluations = list(state.get("question_evaluations") or [])
        technical_scores = [item.get("score", 0) for item in question_evaluations]
        communication_scores = [item.get("communication_score", 0) for item in question_evaluations]
        overall_score = 0
        technical_score = 0
        communication_score = 0
        if technical_scores:
            technical_score = int(round(sum(technical_scores) / len(technical_scores)))
        if communication_scores:
            communication_score = int(round(sum(communication_scores) / len(communication_scores)))
        if technical_scores and communication_scores:
            overall_score = int(round((technical_score + communication_score) / 2))
        elif technical_scores:
            overall_score = technical_score
        elif communication_scores:
            overall_score = communication_score

        strengths = self._extract_strengths(question_evaluations)
        weaknesses = self._extract_weaknesses(question_evaluations)
        recommendations = self._extract_recommendations(question_evaluations, weaknesses)
        summary = self._format_summary(
            overall_score,
            technical_score,
            communication_score,
            strengths,
            weaknesses,
            recommendations,
        )

        report: dict[str, Any] = {
            "session_id": session.get("session_id"),
            "candidate_id": session.get("candidate_id"),
            "interview_type": state.get("interview_type"),
            "role": state.get("config", {}).get("role"),
            "completion_status": state.get("status", "completed"),
            "interview_duration_seconds": self._duration_seconds(state.get("started_at"), state.get("completed_at")),
            "overall_score": overall_score,
            "technical_score": technical_score,
            "communication_score": communication_score,
            "summary": summary,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "question_evaluations": question_evaluations,
            "completed_at": state.get("completed_at"),
        }

        if state.get("is_mixed"):
            report["mixed_plan"] = state.get("mixed_plan", [])
            report["mixed_section_results"] = state.get("mixed_section_results", [])
            report["type_performance"] = self._group_performance_by_type(question_evaluations)

        return report

    def _duration_seconds(self, started_at: Optional[str], completed_at: Optional[str]) -> int:
        try:
            if started_at and completed_at:
                start = datetime.fromisoformat(started_at)
                end = datetime.fromisoformat(completed_at)
                return int((end - start).total_seconds())
        except Exception:
            pass
        return 0

    def _estimate_communication_score(self, answer_length_class: AnswerLengthClass) -> int:
        if answer_length_class == AnswerLengthClass.TOO_SHORT:
            return 55
        if answer_length_class == AnswerLengthClass.VERBOSE:
            return 78
        return 88

    def _recommendations_from_result(self, result: Any) -> list[str]:
        recommendations: list[str] = []
        if getattr(getattr(result, "verdict", None), "verdict", None) == Verdict.OFF_TOPIC:
            recommendations.append("Keep answers focused on the question prompt.")
        for gap in getattr(result, "gaps", []) or []:
            recommendations.append(f"Review {gap.concept} to strengthen your response.")
        return list(dict.fromkeys(recommendations))

    def _extract_strengths(self, evaluations: list[dict[str, Any]]) -> list[str]:
        strengths: list[str] = []
        for evaluation in evaluations:
            if evaluation.get("score", 0) >= 80:
                strengths.append(f"Strong response to: {evaluation.get('question_text', '')[:50]}".strip())
        return strengths[:5] or ["Solid knowledge demonstrated across the interview."]

    def _extract_weaknesses(self, evaluations: list[dict[str, Any]]) -> list[str]:
        weaknesses: list[str] = []
        for evaluation in evaluations:
            if evaluation.get("score", 0) < 60:
                weaknesses.append(f"Improve the response to: {evaluation.get('question_text', '')[:50]}".strip())
            if evaluation.get("communication_score", 100) < 70:
                weaknesses.append("Answer clarity and structure could be sharper.")
        return list(dict.fromkeys(weaknesses))[:5] or ["Continue polishing answer structure and depth."]

    def _extract_recommendations(self, evaluations: list[dict[str, Any]], weaknesses: list[str]) -> list[str]:
        recommendations: list[str] = []
        if weaknesses:
            for weak in weaknesses[:3]:
                recommendations.append(weak)
        else:
            recommendations.append("Practice mock interviews regularly to keep performance strong.")
        recommendations.extend(["Review key technical concepts after each interview.", "Focus on concise, structured responses."])
        return list(dict.fromkeys(recommendations))

    def _format_summary(
        self,
        overall_score: int,
        technical_score: int,
        communication_score: int,
        strengths: list[str],
        weaknesses: list[str],
        recommendations: list[str],
    ) -> str:
        confidence = "high confidence" if communication_score >= 80 else "steady confidence" if communication_score >= 65 else "developing confidence"
        technical = "strong technical understanding" if technical_score >= 80 else "good technical grounding" if technical_score >= 65 else "technical foundations that need work"
        return (
            f"This candidate completed the interview with an overall score of {overall_score}/100, "
            f"showing {technical} and {confidence}. "
            f"Strengths include {strengths[0] if strengths else 'well-aligned responses'}. "
            f"Areas for improvement focus on {weaknesses[0] if weaknesses else 'clarity and depth'}. "
            f"Recommended next steps are {recommendations[0] if recommendations else 'targeted practice and review'}."
        )

    async def process_turn(
        self,
        session_id: str,
        candidate_id: str,
        raw_answer: str,
        persona: Optional[InterviewerPersona] = None,
    ) -> Any:
        session = await self.session_repo.get_state(session_id)
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found",
            )

        if session.get("candidate_id") != candidate_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to use this interview session",
            )

        question_id = session.get("state", {}).get("question_id") or session.get("question_id")
        if question_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview session is missing question metadata",
            )

        question = await self.question_repo.get_question(question_id)
        result = await self.orchestrator.process_turn(
            session_id=session_id,
            candidate_id=candidate_id,
            question=question,
            raw_answer=raw_answer,
            persona=persona,
        )

        persisted_state = dict(session.get("state") or {})
        persisted_state.setdefault("transcript", [])
        persisted_state.setdefault("question_evaluations", [])
        persisted_state.setdefault("timer", {"duration_seconds": 1800, "started": True})
        transcript = list(persisted_state.get("transcript") or [])
        transcript_timestamp = utcnow().isoformat()
        if raw_answer:
            transcript.append({"speaker": "You", "text": raw_answer, "timestamp": transcript_timestamp})
        feedback_text = getattr(getattr(result, "feedback", None), "text", None)
        if feedback_text:
            transcript.append({"speaker": "AI", "text": feedback_text, "timestamp": transcript_timestamp})
        followup_text = getattr(getattr(result, "followup", None), "text", None)
        if followup_text:
            transcript.append({"speaker": "AI", "text": followup_text, "timestamp": transcript_timestamp})
        persisted_state["transcript"] = transcript

        communication_score = self._estimate_communication_score(
            getattr(getattr(result, "answer", None), "answer_length_class", AnswerLengthClass.ADEQUATE)
        )
        question_evaluations = list(persisted_state.get("question_evaluations") or [])
        question_evaluations.append(
            {
                "question_id": question.question_id,
                "question_text": question.text,
                "question_interview_type": question.interview_type,
                "question_category": question.category,
                "candidate_answer": raw_answer,
                "evaluation": getattr(getattr(result, "verdict", None), "verdict", None).value if getattr(getattr(result, "verdict", None), "verdict", None) is not None else "unknown",
                "score": int(round(getattr(getattr(result, "verdict", None), "score", 0.0))) if getattr(getattr(result, "verdict", None), "score", None) is not None else 0,
                "feedback": feedback_text,
                "communication_score": communication_score,
                "recommendations": self._recommendations_from_result(result),
                "missing_concepts": [getattr(gap, "concept", "") for gap in getattr(result, "gaps", []) or []],
                "section_name": session.get("state", {}).get("mixed_plan", [])
                    [session.get("state", {}).get("mixed_current_section", 0)]
                    ["section_name"]
                    if session.get("state", {}).get("is_mixed") else None,
            }
        )
        persisted_state["question_evaluations"] = question_evaluations

        if hasattr(result, "state"):
            persisted_state["question_index"] = max(1, int(getattr(result.state, "turn_index", 0)) + 1)
            persisted_state["current_main_question_id"] = getattr(result.state, "current_main_question_id", None) or question_id
            persisted_state["status"] = "in_progress"
            persisted_state["last_verdict"] = getattr(getattr(result.state, "last_verdict", None), "value", None)
            persisted_state["difficulty_band"] = getattr(getattr(result.state, "difficulty_band", None), "value", None)
            persisted_state["skill_estimate"] = getattr(result.state, "skill_estimate", None)
            persisted_state["recent_off_topic_count"] = getattr(result.state, "recent_off_topic_count", 0)
            persisted_state["phase"] = getattr(getattr(result.state, "phase", None), "value", None)
        else:
            persisted_state["question_index"] = int(persisted_state.get("question_index", 0)) + 1
            persisted_state["status"] = "in_progress"

        persisted_state["turn_evaluation"] = self._build_turn_evaluation_summary(result)
        await self._advance_mixed_section(persisted_state, question, result)

        await self.session_repo.save_state(session_id, persisted_state)

        if hasattr(result, "model_dump"):
            response_payload = result.model_dump(mode="json")
        elif isinstance(result, dict):
            response_payload = result
        elif hasattr(result, "dict"):
            response_payload = result.dict()
        else:
            response_payload = {k: v for k, v in getattr(result, "__dict__", {}).items()}

        if not isinstance(response_payload, dict):
            response_payload = dict(response_payload)

        response_payload["turn_evaluation"] = self._build_turn_evaluation_summary(result)
        return response_payload
