import pytest

from app.services.interview_engine.groq_evaluation_engine import GroqEvaluationEngine
from app.services.interview_engine import QuestionMeta, InterviewStateSnapshot
from app.services.interview_engine.prompt_builder import PromptBuilder


class DummyGroq:
    async def complete(self, messages, max_tokens=256, temperature=0.4, json_mode=False):
        return """{
            "overall_score": 88,
            "verdict": "incorrect",
            "technical_accuracy": 90,
            "communication": 85,
            "concept_coverage": 80,
            "strengths": ["Explained the core idea clearly"],
            "weaknesses": ["Did not mention the edge case"],
            "missing_concepts": ["edge case handling"],
            "recommendations": ["Mention the edge case explicitly"],
            "follow_up_question": "How would this behave under high load?",
            "reasoning": "The answer is conceptually strong but incomplete.",
            "hiring_signal": "strong"
        }"""


@pytest.mark.parametrize(
    ("score", "verdict", "expected"),
    [
        (88, "incorrect", "correct"),
        (74, "correct", "partially_correct"),
        (45, "good", "incorrect"),
        (70, "weak", "partially_correct"),
    ],
)
def test_normalize_verdict_matches_score_band(score, verdict, expected):
    engine = GroqEvaluationEngine(DummyGroq())
    normalized = engine._normalize_verdict(verdict, score)
    assert normalized == expected


def test_parse_evaluation_response_keeps_consistent_verdict():
    engine = GroqEvaluationEngine(DummyGroq())
    parsed = engine._parse_evaluation_response(
        """{
            "overall_score": 88,
            "verdict": "incorrect",
            "technical_accuracy": 90,
            "communication": 85,
            "concept_coverage": 80,
            "strengths": ["Explained the core idea clearly"],
            "weaknesses": ["Did not mention the edge case"],
            "missing_concepts": ["edge case handling"],
            "recommendations": ["Mention the edge case explicitly"],
            "follow_up_question": "How would this behave under high load?",
            "reasoning": "The answer is conceptually strong but incomplete.",
            "hiring_signal": "strong"
        }"""
    )

    assert parsed["overall_score"] == 88
    assert parsed["verdict"] == "correct"


def test_prompt_instructs_evidence_based_honest_evaluation():
    builder = PromptBuilder()
    question = QuestionMeta(
        question_id="q1",
        topic="Databases",
        text="Explain indexing",
        expected_concepts=[{"name": "indexing"}, {"name": "trade-offs"}],
        core_concepts=[{"name": "indexing"}],
    )
    state = InterviewStateSnapshot(session_id="s1", candidate_id="c1")
    messages = builder.groq_evaluation_prompt("I used an index to speed up lookups.", question, state)

    content = "\n".join(message["content"] for message in messages if message["role"] in {"system", "user"})

    assert "Do not compare keywords" in content
    assert "Evaluate ONLY the current interview question" in content
    assert "Only required concepts affect scoring" in content
    assert "Every missing concept must satisfy two conditions" in content
    assert "If an item is not directly required by this question, do not include it" in content
    assert "Strengths must cite what the candidate answered well" in content
    assert "Weaknesses must explain exactly what is missing or unclear" in content
