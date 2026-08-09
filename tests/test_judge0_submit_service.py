import pytest
from unittest.mock import AsyncMock, patch

from app.schemas.coding import SubmitRequest
from app.services import judge0_service


@pytest.mark.asyncio
async def test_submit_code_returns_result_when_ai_feedback_fails(monkeypatch):
    problem = {
        "_id": "problem-1",
        "title": "Sample",
        "difficulty": "easy",
        "statement": "Solve the problem",
        "hidden_test_cases": [{"input": "", "expected_output": "1"}],
    }

    db = object()

    class DummyCollection:
        async def find_one(self, *args, **kwargs):
            return problem

        async def insert_one(self, *args, **kwargs):
            return type("Result", (), {"inserted_id": "submission-1"})()

        async def update_one(self, *args, **kwargs):
            return None

    class DummyDB:
        def __getitem__(self, name):
            return DummyCollection()

    monkeypatch.setattr(judge0_service, "_get_problem_or_404", AsyncMock(return_value=problem))
    monkeypatch.setattr(judge0_service, "execute_code", AsyncMock(return_value={"status_id": 3, "stdout": "1", "stderr": None, "compile_output": None, "time_ms": 10.0, "memory_kb": 100}))
    monkeypatch.setattr(judge0_service, "analyze_submission_with_groq", AsyncMock(side_effect=Exception("boom")))
    monkeypatch.setattr(judge0_service.coding_progress_service, "record_solved", AsyncMock())

    response = await judge0_service.submit_code(DummyDB(), "user-1", "problem-1", SubmitRequest(language="python", code="print(1)"))

    assert response.status == "accepted"
    assert response.submission_id == "submission-1"
    assert response.passed_test_cases == 1
    assert response.total_test_cases == 1


@pytest.mark.asyncio
async def test_submit_code_sets_incorrect_ai_feedback_on_wrong_answer(monkeypatch):
    problem = {
        "_id": "problem-1",
        "title": "Sample",
        "difficulty": "easy",
        "statement": "Solve the problem",
        "hidden_test_cases": [{"input": "1", "expected_output": "2"}],
    }

    db = object()

    class DummyCollection:
        async def find_one(self, *args, **kwargs):
            return problem

        async def insert_one(self, *args, **kwargs):
            return type("Result", (), {"inserted_id": "submission-2"})()

        async def update_one(self, *args, **kwargs):
            return None

    class DummyDB:
        def __getitem__(self, name):
            return DummyCollection()

    monkeypatch.setattr(judge0_service, "_get_problem_or_404", AsyncMock(return_value=problem))
    monkeypatch.setattr(
        judge0_service,
        "execute_code",
        AsyncMock(return_value={
            "status_id": 3,
            "stdout": "1",
            "stderr": None,
            "compile_output": None,
            "time_ms": 10.0,
            "memory_kb": 100,
        }),
    )
    monkeypatch.setattr(
        judge0_service,
        "analyze_submission_with_groq",
        AsyncMock(return_value={"correctness": "Correct"}),
    )
    monkeypatch.setattr(judge0_service.coding_progress_service, "record_solved", AsyncMock())

    response = await judge0_service.submit_code(DummyDB(), "user-1", "problem-1", SubmitRequest(language="python", code="print(1)"))

    assert response.status == "wrong_answer"
    assert response.ai_feedback.correctness == "Incorrect"
    assert response.failed_test_number == 1


@pytest.mark.asyncio
async def test_submit_code_sets_compile_error_ai_feedback(monkeypatch):
    problem = {
        "_id": "problem-1",
        "title": "Sample",
        "difficulty": "easy",
        "statement": "Solve the problem",
        "hidden_test_cases": [{"input": "1", "expected_output": "2"}],
    }

    db = object()

    class DummyCollection:
        async def find_one(self, *args, **kwargs):
            return problem

        async def insert_one(self, *args, **kwargs):
            return type("Result", (), {"inserted_id": "submission-3"})()

        async def update_one(self, *args, **kwargs):
            return None

    class DummyDB:
        def __getitem__(self, name):
            return DummyCollection()

    monkeypatch.setattr(judge0_service, "_get_problem_or_404", AsyncMock(return_value=problem))
    monkeypatch.setattr(
        judge0_service,
        "execute_code",
        AsyncMock(return_value={
            "status_id": 6,
            "stdout": "",
            "stderr": "SyntaxError: invalid syntax",
            "compile_output": "SyntaxError: invalid syntax",
            "time_ms": 0.0,
            "memory_kb": 0.0,
        }),
    )
    monkeypatch.setattr(
        judge0_service,
        "analyze_submission_with_groq",
        AsyncMock(return_value={}),
    )
    monkeypatch.setattr(judge0_service.coding_progress_service, "record_solved", AsyncMock())

    response = await judge0_service.submit_code(DummyDB(), "user-1", "problem-1", SubmitRequest(language="python", code="print(1)"))

    assert response.status == "compile_error"
    assert response.ai_feedback.correctness == "Compilation Error"
    assert response.ai_feedback.explanation is not None
    assert response.ai_feedback.explanation.strip() != ""
    assert "syntaxerror" in response.ai_feedback.explanation.lower() or "compilation" in response.ai_feedback.explanation.lower()


@pytest.mark.asyncio
async def test_submit_code_accepts_legacy_output_field_in_hidden_tests(monkeypatch):
    problem = {
        "_id": "problem-1",
        "title": "Sample",
        "difficulty": "easy",
        "statement": "Solve the problem",
        "hidden_test_cases": [{"input": "1", "output": "1"}],
    }

    db = object()

    class DummyCollection:
        async def find_one(self, *args, **kwargs):
            return problem

        async def insert_one(self, *args, **kwargs):
            return type("Result", (), {"inserted_id": "submission-4"})()

        async def update_one(self, *args, **kwargs):
            return None

    class DummyDB:
        def __getitem__(self, name):
            return DummyCollection()

    monkeypatch.setattr(judge0_service, "_get_problem_or_404", AsyncMock(return_value=problem))
    monkeypatch.setattr(
        judge0_service,
        "execute_code",
        AsyncMock(return_value={
            "status_id": 3,
            "stdout": "1",
            "stderr": None,
            "compile_output": None,
            "time_ms": 10.0,
            "memory_kb": 100,
        }),
    )
    monkeypatch.setattr(
        judge0_service,
        "analyze_submission_with_groq",
        AsyncMock(return_value={"correctness": "Correct"}),
    )
    monkeypatch.setattr(judge0_service.coding_progress_service, "record_solved", AsyncMock())

    response = await judge0_service.submit_code(
        DummyDB(),
        "user-1",
        "problem-1",
        SubmitRequest(language="python", code="print(1)"),
    )

    assert response.status == "accepted"
    assert response.passed_test_cases == 1
    assert response.total_test_cases == 1
