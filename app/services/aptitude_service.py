import logging
import random
import uuid
from datetime import datetime, timezone
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.aptitude import APTITUDE_QUESTION_COLLECTION, AptitudeQuestionModel

logger = logging.getLogger(__name__)


def _get_total_assessment_seconds(question_count: int | None) -> int:
    return max(0, int(question_count or 0) * 60)


class AptitudeService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.questions_collection = db[APTITUDE_QUESTION_COLLECTION]
        self.sessions_collection = db["aptitude_sessions"]
        self.results_collection = db["aptitude_results"]

    async def create_session(self, user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        test_type = (payload.get("test_type") or "Quantitative Aptitude").strip()
        difficulty = (payload.get("difficulty") or "Easy").strip().lower()
        question_count = int(payload.get("question_count") or 10)

        if test_type == "Mixed Aptitude":
            questions = await self._build_mixed_questions(difficulty, question_count)
        else:
            questions = await self._fetch_questions(test_type=test_type, difficulty=difficulty, question_count=question_count)

        session_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        total_duration_seconds = _get_total_assessment_seconds(question_count)
        session_doc = {
            "session_id": session_id,
            "user_id": user_id,
            "status": "in_progress",
            "test_type": test_type,
            "difficulty": difficulty,
            "question_count": question_count,
            "timer": {"duration_seconds": total_duration_seconds, "started_at": now.isoformat()},
            "questions": [self._serialize_question(q) for q in questions],
            "answers": {},
            "review_flags": {},
            "started_at": now,
            "updated_at": now,
        }
        await self.sessions_collection.insert_one(session_doc)

        return {
            "session_id": session_id,
            "questions": session_doc["questions"],
            "timer": session_doc["timer"],
            "test_metadata": {
                "test_type": test_type,
                "difficulty": difficulty,
                "question_count": question_count,
                "question_count_selected": len(questions),
            },
        }

    async def update_answer(self, session_id: str, user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        session = await self.sessions_collection.find_one({"session_id": session_id, "user_id": user_id})
        if not session:
            raise ValueError("Session not found")

        question_id = payload.get("question_id")
        if question_id is None:
            raise ValueError("question_id is required")

        update_payload: dict[str, Any] = {}
        set_updates: dict[str, Any] = {"updated_at": datetime.now(timezone.utc)}
        unset_updates: dict[str, Any] = {}

        if "answer" in payload:
            if payload["answer"] is None:
                unset_updates[f"answers.{question_id}"] = ""
            else:
                set_updates[f"answers.{question_id}"] = {"answer": payload["answer"]}

        if "review" in payload:
            set_updates[f"review_flags.{question_id}"] = bool(payload["review"])

        if set_updates:
            update_payload["$set"] = set_updates
        if unset_updates:
            update_payload["$unset"] = unset_updates
        if "$set" not in update_payload and "$unset" not in update_payload:
            raise ValueError("No update fields provided")

        await self.sessions_collection.update_one(
            {"session_id": session_id, "user_id": user_id},
            update_payload,
        )

        return {"session_id": session_id, "updated": True}

    async def get_session(self, session_id: str, user_id: str) -> dict[str, Any]:
        session = await self.sessions_collection.find_one({"session_id": session_id, "user_id": user_id})
        if not session:
            raise ValueError("Session not found")

        return {
            "session_id": session["session_id"],
            "user_id": session["user_id"],
            "status": session.get("status"),
            "test_type": session.get("test_type"),
            "difficulty": session.get("difficulty"),
            "question_count": session.get("question_count"),
            "timer": session.get("timer"),
            "questions": session.get("questions", []),
            "answers": session.get("answers", {}),
            "review_flags": session.get("review_flags", {}),
            "result_id": session.get("result_id"),
            "submitted_at": self._format_datetime(session.get("submitted_at")),
        }

    async def clear_answer(self, session_id: str, user_id: str, question_id: str) -> dict[str, Any]:
        session = await self.sessions_collection.find_one({"session_id": session_id, "user_id": user_id})
        if not session:
            raise ValueError("Session not found")

        await self.sessions_collection.update_one(
            {"session_id": session_id, "user_id": user_id},
            {"$unset": {f"answers.{question_id}": ""}, "$set": {"updated_at": datetime.now(timezone.utc)}},
        )
        return {"session_id": session_id, "cleared": True}

    async def submit_session(self, session_id: str, user_id: str) -> dict[str, Any]:
        session = await self.sessions_collection.find_one({"session_id": session_id, "user_id": user_id})
        if not session:
            raise ValueError("Session not found")

        questions = session.get("questions") or []
        answers = session.get("answers") or {}
        review_flags = session.get("review_flags") or {}

        correct = 0
        incorrect = 0
        unanswered = 0
        for question in questions:
            question_id = question.get("question_id")
            user_answer = answers.get(question_id, {}).get("answer") if isinstance(answers.get(question_id), dict) else None
            if user_answer is None:
                unanswered += 1
            elif user_answer == question.get("correct_answer"):
                correct += 1
            else:
                incorrect += 1

        total_attempted = correct + incorrect
        score = round((correct / len(questions) * 100), 1) if questions else 0.0
        accuracy = round((correct / total_attempted * 100), 1) if total_attempted else 0.0
        started_at = session.get("started_at")
        if isinstance(started_at, datetime):
            if started_at.tzinfo is None:
                started_at = started_at.replace(tzinfo=timezone.utc)
        else:
            started_at = datetime.now(timezone.utc)
        time_taken_seconds = int((datetime.now(timezone.utc) - started_at).total_seconds())
        submitted_at = datetime.now(timezone.utc)

        result_doc = {
            "result_id": str(uuid.uuid4()),
            "session_id": session_id,
            "user_id": user_id,
            "test_type": session.get("test_type"),
            "difficulty": session.get("difficulty"),
            "summary": {
                "correct": correct,
                "incorrect": incorrect,
                "unanswered": unanswered,
                "score": score,
                "accuracy": accuracy,
                "time_taken_seconds": time_taken_seconds,
            },
            "questions": [
                {
                    "question_id": question.get("question_id"),
                    "question": question.get("question"),
                    "user_answer": answers.get(question.get("question_id"), {}).get("answer") if isinstance(answers.get(question.get("question_id")), dict) else None,
                    "correct_answer": question.get("correct_answer"),
                    "explanation": question.get("explanation"),
                    "is_correct": (answers.get(question.get("question_id"), {}).get("answer") if isinstance(answers.get(question.get("question_id")), dict) else None) == question.get("correct_answer"),
                    "marked_for_review": bool(review_flags.get(question.get("question_id"))),
                }
                for question in questions
            ],
            "submitted_at": submitted_at,
        }
        await self.results_collection.insert_one(result_doc)
        await self.sessions_collection.update_one(
            {"session_id": session_id, "user_id": user_id},
            {"$set": {"status": "completed", "submitted_at": submitted_at, "result_id": result_doc["result_id"]}},
        )

        return {"result_id": result_doc["result_id"], "summary": result_doc["summary"], "questions": result_doc["questions"]}

    async def get_review(self, session_id: str, user_id: str) -> dict[str, Any]:
        session = await self.sessions_collection.find_one({"session_id": session_id, "user_id": user_id})
        if not session:
            raise ValueError("Session not found")
        return {
            "session_id": session_id,
            "questions": [
                {
                    "question_id": question.get("question_id"),
                    "question": question.get("question"),
                    "user_answer": (session.get("answers") or {}).get(question.get("question_id"), {}).get("answer") if isinstance((session.get("answers") or {}).get(question.get("question_id")), dict) else None,
                    "correct_answer": question.get("correct_answer"),
                    "explanation": question.get("explanation"),
                    "is_correct": ((session.get("answers") or {}).get(question.get("question_id"), {}).get("answer") if isinstance((session.get("answers") or {}).get(question.get("question_id")), dict) else None) == question.get("correct_answer"),
                }
                for question in session.get("questions") or []
            ],
        }

    async def get_history(self, user_id: str) -> list[dict[str, Any]]:
        cursor = self.results_collection.find({"user_id": user_id})
        history = []
        async for doc in cursor:
            history.append({
                "result_id": doc.get("result_id"),
                "session_id": doc.get("session_id"),
                "test_type": doc.get("test_type"),
                "difficulty": doc.get("difficulty"),
                "summary": doc.get("summary"),
                "submitted_at": self._format_datetime(doc.get("submitted_at")),
            })
        history.sort(
            key=lambda item: datetime.fromisoformat(item["submitted_at"].replace("Z", "+00:00")) if item.get("submitted_at") else datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )
        return history

    async def get_result(self, session_id: str, user_id: str) -> dict[str, Any]:
        result = await self.results_collection.find_one({"session_id": session_id, "user_id": user_id})
        if not result:
            raise ValueError("Result not found")
        return {
            "result_id": result.get("result_id"),
            "session_id": result.get("session_id"),
            "user_id": result.get("user_id"),
            "test_type": result.get("test_type"),
            "difficulty": result.get("difficulty"),
            "summary": result.get("summary", {}),
            "questions": result.get("questions", []),
            "submitted_at": self._format_datetime(result.get("submitted_at")),
        }

    async def _fetch_questions(self, *, test_type: str, difficulty: str, question_count: int) -> list[dict[str, Any]]:
        docs = []
        async for document in self.questions_collection.find({}):
            if not self._matches_question(document, difficulty=difficulty, category=test_type):
                continue
            docs.append(document)
        random.shuffle(docs)
        return docs[:question_count]

    def _format_datetime(self, value: Any) -> Any:
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            return value.isoformat()
        return value

    async def _build_mixed_questions(self, difficulty: str, question_count: int) -> list[dict[str, Any]]:
        categories = [
            "Quantitative Aptitude",
            "Logical Reasoning",
            "Verbal Ability",
            "Data Interpretation",
        ]
        selected: list[dict[str, Any]] = []
        per_category = max(1, question_count // len(categories))
        remainder = question_count % len(categories)
        for index, category in enumerate(categories):
            count = per_category + (1 if index < remainder else 0)
            docs = []
            async for document in self.questions_collection.find({}):
                if self._matches_question(document, difficulty=difficulty, category=category):
                    docs.append(document)
            random.shuffle(docs)
            selected.extend(docs[:count])
        random.shuffle(selected)
        return selected[:question_count]

    def _matches_question(self, document: dict[str, Any], *, difficulty: str, category: str) -> bool:
        if document.get("active", True) is not True:
            return False
        if document.get("difficulty", "").lower() != difficulty.lower():
            return False
        if category != "Mixed Aptitude" and document.get("category") != category:
            return False
        return True

    def _serialize_question(self, question: dict[str, Any]) -> dict[str, Any]:
        document = dict(question)
        document.setdefault("topic", "General")
        document.setdefault("options", [])
        document.setdefault("correct_answer", "")
        document.setdefault("explanation", "")
        document.setdefault("company_tags", [])
        document.setdefault("estimated_time", 0)
        document.setdefault("marks", 0)
        document.setdefault("active", True)
        document.setdefault("created_at", datetime.now(timezone.utc))
        document.setdefault("updated_at", datetime.now(timezone.utc))
        model = AptitudeQuestionModel.model_validate(document)
        return {
            "id": model.question_id,
            "question_id": model.question_id,
            "category": model.category,
            "topic": model.topic,
            "difficulty": model.difficulty,
            "question": model.question,
            "options": model.options,
            "correct_answer": model.correct_answer,
            "explanation": model.explanation,
            "correctOption": model.correct_answer,
        }
