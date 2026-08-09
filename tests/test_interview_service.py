import httpx
import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.services import interview_service
from app.services.interview_engine import ConceptStatus, InterviewerPersona, QuestionMeta


@pytest.mark.asyncio
async def test_initial_question_selection_uses_interview_configuration():
    service = interview_service.InterviewService.__new__(interview_service.InterviewService)
    question = QuestionMeta(
        question_id="q-technical",
        text="Describe how you would design a scalable notification system.",
        topic="system design",
        expected_concepts=[],
        core_concepts=[],
    )
    service.question_repo = SimpleNamespace(select_question=AsyncMock(return_value=question))
    service.session_repo = SimpleNamespace(create_session=AsyncMock())

    result = await service.create_session(
        "candidate-1",
        {
            "interview_type": "technical",
            "role": "Software Engineer",
            "experience_level": "Mid",
            "company_type": "Product",
            "duration": "30m",
            "language": "English",
        },
        persona=InterviewerPersona(),
    )

    assert result["session_id"]
    assert result["question"]["question_id"] == "q-technical"
    assert result["interview_state"]["interview_type"] == "technical"
    assert result["timer"]["duration_seconds"] == 1800
    service.question_repo.select_question.assert_awaited_once()
from app.services.interview_engine.adaptivity_engine import AdaptivityEngine
from app.services.interview_engine.comprehension_engine import ComprehensionEngine
from app.services.interview_engine.dialogue_engine import DialogueEngine
from app.services.interview_engine.evaluation_engine import EvaluationEngine
from app.services.interview_engine.memory_engine import MemoryEngine
from app.services.interview_engine.orchestrator import InterviewOrchestrator
from app.services.interview_engine.prompt_builder import PromptBuilder
from app.services.interview_engine.quality_engine import QualityEngine
from app.services.interview_engine.retrieval_engine import RetrievalEngine


@pytest.mark.asyncio
async def test_groq_non_retryable_rate_limit_fails_fast(monkeypatch):
    request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    response = httpx.Response(
        429,
        headers={"retry-after": "517", "x-should-retry": "false"},
        request=request,
    )
    client = AsyncMock()
    client.post.return_value = response
    adapter = interview_service.GroqClientAdapter()
    adapter._client = client
    sleep = AsyncMock()

    monkeypatch.setattr(interview_service, "settings", SimpleNamespace(GROQ_API_KEY="test-key"))
    monkeypatch.setattr(interview_service.asyncio, "sleep", sleep)
    interview_service.GroqClientAdapter.RATE_LIMIT_HIT_COUNT = 0

    with pytest.raises(interview_service.HTTPException) as exc_info:
        await adapter.complete([{"role": "user", "content": "hello"}])

    assert exc_info.value.status_code == 502
    assert client.post.await_count == 1
    sleep.assert_not_awaited()
    assert interview_service.GroqClientAdapter.RATE_LIMIT_HIT_COUNT == 1


@pytest.mark.asyncio
async def test_comprehension_recognizes_paraphrased_concepts():
    class FakeGroq:
        async def complete(self, messages, max_tokens=256, temperature=0.4, json_mode=False):
            return "{}"

    engine = ComprehensionEngine(
        FakeGroq(),
        PromptBuilder(),
        concept_dictionary={
            "databases": {
                "indexing": ["index", "indexes"],
                "query performance": ["performance", "speed"],
            }
        },
    )

    question = QuestionMeta(
        question_id="q1",
        text="Explain indexing and why it improves query performance.",
        topic="databases",
        expected_concepts=[
            {"name": "indexing", "weight": 1.0, "is_core": True},
            {"name": "query performance", "weight": 1.0, "is_core": True},
        ],
        core_concepts=[
            {"name": "indexing", "weight": 1.0, "is_core": True},
            {"name": "query performance", "weight": 1.0, "is_core": True},
        ],
    )

    answer = await engine.understand_answer(
        "An index is a structure that helps the database find rows quickly. It improves performance when reading data.",
        question,
    )

    assert "indexing" in answer.mentioned_concepts
    assert "query performance" in answer.mentioned_concepts


@pytest.mark.asyncio
async def test_comprehension_uses_question_concepts_when_topic_dictionary_is_missing():
    class FakeGroq:
        async def complete(self, messages, max_tokens=256, temperature=0.4, json_mode=False):
            return "{}"

    engine = ComprehensionEngine(FakeGroq(), PromptBuilder(), concept_dictionary={})

    question = QuestionMeta(
        question_id="q2",
        text="Explain binary search and why it is efficient.",
        topic="algorithms",
        expected_concepts=[
            {"name": "binary search", "weight": 1.0, "is_core": True},
            {"name": "efficiency", "weight": 1.0, "is_core": False},
        ],
        core_concepts=[
            {"name": "binary search", "weight": 1.0, "is_core": True},
            {"name": "efficiency", "weight": 1.0, "is_core": False},
        ],
    )

    answer = await engine.understand_answer(
        "Binary search repeatedly splits a sorted array in half and finds the target efficiently.",
        question,
    )

    assert "binary search" in answer.mentioned_concepts


@pytest.mark.asyncio
async def test_comprehension_scores_core_concepts_when_expected_and_core_differ():
    class FakeGroq:
        async def complete(self, messages, max_tokens=256, temperature=0.4, json_mode=False):
            return "{}"

    engine = ComprehensionEngine(
        FakeGroq(),
        PromptBuilder(),
        concept_dictionary={
            "mongodb": {
                "$match": ["match"],
                "$group": ["group"],
            }
        },
    )

    question = QuestionMeta(
        question_id="tech_medium_03",
        text="Describe the MongoDB aggregation pipeline.",
        topic="mongodb",
        expected_concepts=[
            {"name": "pipeline stages", "weight": 1.0, "is_core": True},
            {"name": "aggregation operators", "weight": 1.0, "is_core": True},
        ],
        core_concepts=[
            {"name": "$match", "weight": 1.0, "is_core": True},
            {"name": "$group", "weight": 1.0, "is_core": True},
        ],
    )

    answer = await engine.understand_answer(
        "The $match stage filters documents and the $group stage groups them.",
        question,
    )

    scores = engine.score_concepts(answer, question)
    assert "$match" in scores
    assert "$group" in scores
    assert scores["$match"].status != ConceptStatus.ABSENT
    assert scores["$group"].status != ConceptStatus.ABSENT


@pytest.mark.asyncio
async def test_process_turn_persists_transcript_and_progress():
    service = interview_service.InterviewService.__new__(interview_service.InterviewService)
    initial_session = {
        "session_id": "session-1",
        "candidate_id": "candidate-1",
        "question_id": "q-1",
        "persona": None,
        "state": {
            "question_index": 0,
            "transcript": [],
            "timer": {"duration_seconds": 1800, "started": False},
        },
    }
    saved_payloads = []

    class FakeSessionRepo:
        async def get_state(self, session_id):
            return initial_session if session_id == "session-1" else None

        async def save_state(self, session_id, state):
            saved_payloads.append(state)

    class FakeQuestionRepo:
        async def get_question(self, question_id):
            return QuestionMeta(question_id=question_id, text="Describe your approach.", topic="technical", expected_concepts=[], core_concepts=[])

    class FakeOrchestrator:
        async def process_turn(self, **kwargs):
            return SimpleNamespace(
                feedback=SimpleNamespace(text="Feedback"),
                followup=SimpleNamespace(text="Next question", targets_gap=None),
                should_advance_to_next_question=True,
                state=SimpleNamespace(session_id="session-1", candidate_id="candidate-1"),
            )

    service.session_repo = FakeSessionRepo()
    service.question_repo = FakeQuestionRepo()
    service.orchestrator = FakeOrchestrator()

    result = await service.process_turn("session-1", "candidate-1", "My answer", persona=InterviewerPersona())

    assert result["turn_evaluation"]
    assert result["turn_evaluation"]["score"] == 0
    assert result["turn_evaluation"]["verdict"] is None
    assert result["turn_evaluation"]["weaknesses"]
    assert result["turn_evaluation"]["follow_up_reasoning"] == "Next question"
    assert result["turn_evaluation"]["missing_concepts"] == []
    assert getattr(result["feedback"], "text", None) == "Feedback"
    assert len(saved_payloads) == 1
    persisted = saved_payloads[0]
    assert persisted["question_index"] == 1
    assert persisted["transcript"][0]["text"] == "My answer"
    assert persisted["transcript"][1]["text"] == "Feedback"
    assert persisted["transcript"][2]["text"] == "Next question"


@pytest.mark.asyncio
async def test_orchestrator_falls_back_when_groq_is_unavailable():
    class FailingGroq:
        async def complete(self, messages, max_tokens=256, temperature=0.4, json_mode=False):
            raise RuntimeError("groq unavailable")

    class FakeEmbedding:
        async def embed(self, text):
            return [0.0] * 8

        async def embed_batch(self, texts):
            return [[0.0] * 8 for _ in texts]

    class FakeSessionRepo:
        def __init__(self):
            self.store = {}

        async def get_state(self, session_id):
            return self.store.get(session_id)

        async def save_state(self, session_id, state):
            self.store[session_id] = state

        async def archive_state(self, session_id, summary):
            pass

        async def delete_state(self, session_id):
            self.store.pop(session_id, None)

    class FakeProfileRepo:
        def __init__(self):
            self.store = {}

        async def get_profile(self, candidate_id):
            return self.store.setdefault(candidate_id, {"user_id": candidate_id, "concept_mastery": {}, "session_count": 0})

        async def save_profile(self, candidate_id, profile):
            self.store[candidate_id] = profile

    class FakeKBRepo:
        async def vector_search(self, query_vector, top_k=10):
            return []

    comprehension = ComprehensionEngine(FailingGroq(), PromptBuilder(), concept_dictionary={"databases": {"indexing": ["index", "indexes"], "query performance": ["performance", "speed"]}})
    evaluation = EvaluationEngine(FailingGroq(), PromptBuilder())
    dialogue = DialogueEngine(FailingGroq(), FakeEmbedding(), PromptBuilder())
    quality = QualityEngine(FailingGroq(), PromptBuilder())
    retrieval = RetrievalEngine(FakeEmbedding(), FakeKBRepo())
    memory = MemoryEngine(FakeSessionRepo(), FakeProfileRepo())
    orchestrator = InterviewOrchestrator(
        comprehension,
        retrieval,
        evaluation,
        AdaptivityEngine(),
        dialogue,
        quality,
        memory,
    )

    question = QuestionMeta(
        question_id="q2",
        text="Explain indexing and why it improves query performance.",
        topic="databases",
        expected_concepts=[
            {"name": "indexing", "weight": 1.0, "is_core": True},
            {"name": "query performance", "weight": 1.0, "is_core": True},
        ],
        core_concepts=[
            {"name": "indexing", "weight": 1.0, "is_core": True},
            {"name": "query performance", "weight": 1.0, "is_core": True},
        ],
    )

    result = await orchestrator.process_turn(
        "session-1",
        "candidate-1",
        question,
        "An index helps the database find rows faster.",
        InterviewerPersona(),
    )

    assert result.feedback.text
    assert result.verdict.verdict.value in {"incorrect", "partially_correct", "correct", "off_topic"}
    assert result.state.session_id == "session-1"