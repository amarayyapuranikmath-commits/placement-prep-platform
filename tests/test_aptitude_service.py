from types import SimpleNamespace

import pytest

from app.services.aptitude_service import AptitudeService


class FakeCursor:
    def __init__(self, docs):
        self._docs = list(docs)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._docs:
            raise StopAsyncIteration
        return self._docs.pop(0)


class FakeCollection:
    def __init__(self, docs=None):
        self.docs = list(docs or [])
        self.inserted = []
        self.updated = []

    async def insert_one(self, doc):
        self.inserted.append(doc)
        return SimpleNamespace(inserted_id="mock-id")

    async def update_one(self, query, update, upsert=False):
        self.updated.append((query, update, upsert))
        if not self.docs:
            self.docs.append({})
        for doc in self.docs:
            if all(doc.get(k) == v for k, v in query.items()):
                if "$set" in update:
                    doc.update(update["$set"])
                if "$setOnInsert" in update:
                    doc.update(update["$setOnInsert"])
                return SimpleNamespace(modified_count=1, matched_count=1)
        if upsert:
            new_doc = {}
            if "$set" in update:
                new_doc.update(update["$set"])
            if "$setOnInsert" in update:
                new_doc.update(update["$setOnInsert"])
            self.docs.append(new_doc)
        return SimpleNamespace(modified_count=0, matched_count=0)

    async def find_one(self, query):
        for doc in self.docs:
            if all(doc.get(k) == v for k, v in query.items()):
                return doc
        return None

    def find(self, query=None):
        return FakeCursor([doc for doc in self.docs if not query or all(doc.get(k) == v for k, v in query.items())])


class FakeDatabase:
    def __init__(self, collections):
        self.collections = collections

    def __getitem__(self, name):
        return self.collections[name]


@pytest.mark.asyncio
async def test_create_session_selects_unique_questions():
    question_docs = [
        {"question_id": "q1", "category": "Quantitative Aptitude", "difficulty": "easy", "question": "Q1", "options": ["A", "B"], "correct_answer": "A", "explanation": "e"},
        {"question_id": "q2", "category": "Quantitative Aptitude", "difficulty": "easy", "question": "Q2", "options": ["A", "B"], "correct_answer": "A", "explanation": "e"},
        {"question_id": "q3", "category": "Quantitative Aptitude", "difficulty": "easy", "question": "Q3", "options": ["A", "B"], "correct_answer": "A", "explanation": "e"},
        {"question_id": "q4", "category": "Quantitative Aptitude", "difficulty": "easy", "question": "Q4", "options": ["A", "B"], "correct_answer": "A", "explanation": "e"},
        {"question_id": "q5", "category": "Logical Reasoning", "difficulty": "easy", "question": "Q5", "options": ["A", "B"], "correct_answer": "A", "explanation": "e"},
        {"question_id": "q6", "category": "Logical Reasoning", "difficulty": "easy", "question": "Q6", "options": ["A", "B"], "correct_answer": "A", "explanation": "e"},
        {"question_id": "q7", "category": "Verbal Ability", "difficulty": "easy", "question": "Q7", "options": ["A", "B"], "correct_answer": "A", "explanation": "e"},
        {"question_id": "q8", "category": "Data Interpretation", "difficulty": "easy", "question": "Q8", "options": ["A", "B"], "correct_answer": "A", "explanation": "e"},
    ]

    db = FakeDatabase({
        "aptitude_questions": FakeCollection(question_docs),
        "aptitude_sessions": FakeCollection(),
        "aptitude_results": FakeCollection(),
    })

    service = AptitudeService(db)
    session = await service.create_session(
        "user-1",
        {"test_type": "Mixed Aptitude", "difficulty": "easy", "question_count": 4},
    )

    assert session["session_id"]
    assert len(session["questions"]) == 4
    assert len({question["question_id"] for question in session["questions"]}) == 4
    assert session["timer"]["duration_seconds"] == 240


@pytest.mark.asyncio
async def test_submit_session_calculates_summary():
    db = FakeDatabase({
        "aptitude_questions": FakeCollection(),
        "aptitude_sessions": FakeCollection([
            {
                "session_id": "sess-1",
                "user_id": "user-1",
                "status": "in_progress",
                "questions": [
                    {"id": "q1", "question_id": "q1", "correct_answer": "A"},
                    {"id": "q2", "question_id": "q2", "correct_answer": "B"},
                    {"id": "q3", "question_id": "q3", "correct_answer": "C"},
                ],
                "answers": {"q1": {"answer": "A"}, "q2": {"answer": "A"}},
                "review_flags": {"q3": True},
            }
        ]),
        "aptitude_results": FakeCollection(),
    })

    service = AptitudeService(db)
    result = await service.submit_session("sess-1", "user-1")

    assert result["summary"]["correct"] == 1
    assert result["summary"]["incorrect"] == 1
    assert result["summary"]["unanswered"] == 1
    assert result["summary"]["score"] == 33.3
    assert result["summary"]["accuracy"] == 50.0


@pytest.mark.asyncio
async def test_update_answer_sets_answer_and_review_flag():
    db = FakeDatabase({
        "aptitude_questions": FakeCollection(),
        "aptitude_sessions": FakeCollection([
            {
                "session_id": "sess-1",
                "user_id": "user-1",
                "status": "in_progress",
                "answers": {},
                "review_flags": {},
            }
        ]),
        "aptitude_results": FakeCollection(),
    })

    service = AptitudeService(db)
    result = await service.update_answer("sess-1", "user-1", {"question_id": "q1", "answer": "A", "review": False})

    assert result["updated"] is True
    assert db.collections["aptitude_sessions"].updated, "Expected update_one to be called"
    update = db.collections["aptitude_sessions"].updated[0][1]
    assert "$set" in update
    assert update["$set"]["answers.q1"] == {"answer": "A"}
    assert update["$set"]["review_flags.q1"] is False
    assert "updated_at" in update["$set"]
