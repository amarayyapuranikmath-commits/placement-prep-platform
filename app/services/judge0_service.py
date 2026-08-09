import logging
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.coding_problem import CODING_PROBLEMS_COLLECTION
from app.models.coding_submission import CODING_SUBMISSIONS_COLLECTION
from app.schemas.coding import (
    AIFeedbackResponse,
    RunRequest,
    RunResponse,
    SubmitRequest,
    SubmitResponse,
    TestCaseResult,
)
from app.services import coding_progress_service
from app.utils.groq_client import analyze_submission_with_groq
from app.utils.judge0_client import execute_code

logger = logging.getLogger(__name__)

_STATUS_ACCEPTED = 3
_STATUS_WRONG_ANSWER = 4
_STATUS_TIME_LIMIT_EXCEEDED = 5
_STATUS_COMPILE_ERROR = 6
_STATUS_RUNTIME_ERROR = 7
_STATUS_MEMORY_LIMIT_EXCEEDED = 8


def _get_problem_statement(problem: dict) -> str:
    return str(problem.get("statement") or problem.get("problem_statement") or "").strip()


def _status_id_to_verdict(status_id: int | None) -> str:
    return {
        _STATUS_ACCEPTED: "accepted",
        _STATUS_WRONG_ANSWER: "wrong_answer",
        _STATUS_COMPILE_ERROR: "compile_error",
        _STATUS_TIME_LIMIT_EXCEEDED: "time_limit_exceeded",
        _STATUS_RUNTIME_ERROR: "runtime_error",
        _STATUS_MEMORY_LIMIT_EXCEEDED: "memory_limit_exceeded",
    }.get(status_id, "runtime_error")


def _build_failure_reason(status_result: str, compile_error: str | None, stderr: str | None) -> str:
    if status_result == "compile_error":
        return compile_error or stderr or "Compilation failed."
    if status_result == "wrong_answer":
        return "The submitted code produced an incorrect result for a hidden test."
    if status_result == "runtime_error":
        return stderr or "The submitted code raised a runtime error."
    if status_result == "time_limit_exceeded":
        return "The submitted code exceeded the time limit."
    if status_result == "memory_limit_exceeded":
        return "The submitted code exceeded the memory limit."
    return "Accepted"


def _normalize_ai_feedback(feedback: dict | None, status_result: str, compile_error: str | None, stderr: str | None) -> AIFeedbackResponse | None:
    if not isinstance(feedback, dict):
        return None

    try:
        ai_feedback = AIFeedbackResponse(**feedback)
    except Exception:
        return None

    if status_result == "accepted":
        ai_feedback.correctness = ai_feedback.correctness or "Correct"
    elif status_result == "wrong_answer":
        ai_feedback.correctness = "Incorrect"
    elif status_result == "runtime_error":
        ai_feedback.correctness = ai_feedback.correctness or "Runtime Error"
        ai_feedback.explanation = ai_feedback.explanation or (stderr or "The submission failed because of a runtime error.")
    elif status_result == "compile_error":
        ai_feedback.correctness = ai_feedback.correctness or "Compilation Error"
        ai_feedback.explanation = ai_feedback.explanation or (compile_error or stderr or "The submission failed because of a compilation error.")
    elif status_result == "time_limit_exceeded":
        ai_feedback.correctness = "Incorrect"
        ai_feedback.explanation = ai_feedback.explanation or "The submission did not finish within the allowed time limit."
    elif status_result == "memory_limit_exceeded":
        ai_feedback.correctness = "Incorrect"
        ai_feedback.explanation = ai_feedback.explanation or "The submission used more memory than allowed."

    return ai_feedback


async def _get_problem_or_404(db: AsyncIOMotorDatabase, problem_id: str) -> dict:
    if not ObjectId.is_valid(problem_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid problem identity")

    collection = db[CODING_PROBLEMS_COLLECTION]
    document = await collection.find_one({"_id": ObjectId(problem_id)})
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return document


async def run_code(db: AsyncIOMotorDatabase, problem_id: str, payload: RunRequest) -> RunResponse:
    problem = await _get_problem_or_404(db, problem_id)
    test_cases = problem.get("visible_test_cases") or []

    results: list[TestCaseResult] = []
    compile_error: str | None = None

    for case in test_cases:
        case_input = str(case.get("input", ""))
        case_expected = str(case.get("expected_output") or case.get("output") or "")

        execution = await execute_code(payload.language, payload.code, case_input)

        if execution["status_id"] == _STATUS_COMPILE_ERROR:
            compile_error = execution.get("compile_output") or execution.get("stderr")
            break

        actual_output = (execution.get("stdout") or "").strip()
        expected_output = case_expected.strip()

        results.append(
            TestCaseResult(
                input=case_input,
                expected_output=case_expected,
                actual_output=actual_output,
                passed=actual_output == expected_output,
                runtime_ms=execution.get("time_ms"),
                memory_kb=execution.get("memory_kb"),
                stderr=execution.get("stderr"),
            )
        )

    all_passed = bool(results) and all(result.passed for result in results) and not compile_error

    return RunResponse(results=results, all_passed=all_passed, compile_error=compile_error)


async def submit_code(
    db: AsyncIOMotorDatabase, user_id: str, problem_id: str, payload: SubmitRequest
) -> SubmitResponse:
    problem = await _get_problem_or_404(db, problem_id)
    hidden_cases = problem.get("hidden_test_cases") or problem.get("visible_test_cases") or []
    total_test_cases = len(hidden_cases)
    passed_test_cases = 0

    status_result = "accepted"
    failed_case_index: int | None = None
    failed_input: str | None = None
    failed_expected_output: str | None = None
    failed_actual_output: str | None = None
    compile_error: str | None = None
    stderr: str | None = None
    last_runtime_ms: float | None = None
    last_memory_kb: float | None = None

    for index, case in enumerate(hidden_cases):
        case_input = str(case.get("input", ""))
        case_expected = str(case.get("expected_output") or case.get("output") or "")

        execution = await execute_code(payload.language, payload.code, case_input)
        last_runtime_ms = execution.get("time_ms")
        last_memory_kb = execution.get("memory_kb")

        status_id = execution.get("status_id")
        actual_output = (execution.get("stdout") or "").strip()
        expected_output = case_expected.strip()

        if status_id == _STATUS_COMPILE_ERROR:
            status_result = "compile_error"
            compile_error = execution.get("compile_output") or execution.get("stderr")
            stderr = execution.get("stderr")
            failed_case_index = index
            failed_input = case_input
            failed_expected_output = expected_output or None
            failed_actual_output = actual_output or None
            break

        if status_id == _STATUS_WRONG_ANSWER or actual_output != expected_output:
            status_result = "wrong_answer"
            failed_case_index = index
            failed_input = case_input
            failed_expected_output = expected_output or None
            failed_actual_output = actual_output or None
            stderr = execution.get("stderr")
            break

        if status_id == _STATUS_TIME_LIMIT_EXCEEDED:
            status_result = "time_limit_exceeded"
            stderr = execution.get("stderr")
            failed_case_index = index
            failed_input = case_input
            failed_expected_output = expected_output or None
            failed_actual_output = actual_output or None
            break

        if status_id == _STATUS_MEMORY_LIMIT_EXCEEDED:
            status_result = "memory_limit_exceeded"
            stderr = execution.get("stderr")
            failed_case_index = index
            failed_input = case_input
            failed_expected_output = expected_output or None
            failed_actual_output = actual_output or None
            break

        if status_id == _STATUS_RUNTIME_ERROR:
            status_result = "runtime_error"
            stderr = execution.get("stderr")
            failed_case_index = index
            failed_input = case_input
            failed_expected_output = expected_output or None
            failed_actual_output = actual_output or None
            break

        if status_id != _STATUS_ACCEPTED:
            status_result = _status_id_to_verdict(status_id)
            stderr = execution.get("stderr")
            failed_case_index = index
            failed_input = case_input
            failed_expected_output = expected_output or None
            failed_actual_output = actual_output or None
            break

        passed_test_cases += 1

    passed = status_result == "accepted"

    def _has_ai_feedback_content(feedback: dict | None) -> bool:
        if not isinstance(feedback, dict):
            return False

        for value in feedback.values():
            if isinstance(value, str) and value.strip():
                return True
            if isinstance(value, list) and len(value) > 0:
                return True
            if isinstance(value, (int, float, bool)):
                return True

        return False

    ai_feedback_dict: dict | None = None
    ai_feedback: AIFeedbackResponse | None = None
    try:
        ai_feedback_dict = await analyze_submission_with_groq(
            _get_problem_statement(problem), payload.code, payload.language, passed
        )
        if _has_ai_feedback_content(ai_feedback_dict):
            ai_feedback = _normalize_ai_feedback(ai_feedback_dict, status_result, compile_error, stderr)
        else:
            ai_feedback = _normalize_ai_feedback({}, status_result, compile_error, stderr)
    except Exception:
        logger.warning("AI feedback unavailable for submission (user=%s, problem=%s)", user_id, problem_id)
        ai_feedback = _normalize_ai_feedback({}, status_result, compile_error, stderr)

    if ai_feedback is None:
        ai_feedback = _normalize_ai_feedback({}, status_result, compile_error, stderr)

    submissions_collection = db[CODING_SUBMISSIONS_COLLECTION]
    submission_doc = {
        "user_id": user_id,
        "problem_id": problem_id,
        "language": payload.language,
        "code": payload.code,
        "status": status_result,
        "verdict": status_result,
        "runtime_ms": last_runtime_ms,
        "memory_kb": last_memory_kb,
        "passed_test_cases": passed_test_cases,
        "total_test_cases": total_test_cases,
        "failed_case_index": failed_case_index,
        "failed_test_number": failed_case_index + 1 if failed_case_index is not None else None,
        "compile_error": compile_error,
        "stderr": stderr,
        "failure_reason": _build_failure_reason(status_result, compile_error, stderr),
        "ai_feedback": ai_feedback.model_dump() if ai_feedback else None,
        "submitted_at": datetime.now(timezone.utc),
    }
    result = await submissions_collection.insert_one(submission_doc)

    problems_collection = db[CODING_PROBLEMS_COLLECTION]
    update_payload = {"$inc": {"total_submissions": 1}}
    if passed:
        update_payload["$inc"]["total_accepted"] = 1
        await coding_progress_service.record_solved(db, user_id, problem_id, problem.get("difficulty") or "medium")
    await problems_collection.update_one({"_id": problem["_id"]}, update_payload)

    progress_collection = db["coding_progress"]
    progress_document = await progress_collection.find_one({"user_id": user_id})
    if progress_document:
        total_submissions = progress_document.get("total_submissions", 0) + 1
        total_accepted = progress_document.get("total_accepted", 0)
        if passed:
            total_accepted += 1
        acceptance_rate = (total_accepted / total_submissions) * 100 if total_submissions else 0.0
        await progress_collection.update_one(
            {"user_id": user_id},
            {
                "$inc": {"total_submissions": 1, **({"total_accepted": 1} if passed else {})},
                "$set": {
                    "user_id": user_id,
                    "acceptance_rate": acceptance_rate,
                    "updated_at": datetime.now(timezone.utc),
                },
            },
            upsert=True,
        )
    else:
        acceptance_rate = 100.0 if passed else 0.0
        await progress_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "user_id": user_id,
                    "total_submissions": 1,
                    "total_accepted": 1 if passed else 0,
                    "acceptance_rate": acceptance_rate,
                    "updated_at": datetime.now(timezone.utc),
                },
            },
            upsert=True,
        )

    logger.info(
        "Submission recorded (user=%s, problem=%s, status=%s)", user_id, problem_id, status_result
    )

    return SubmitResponse(
        submission_id=str(result.inserted_id),
        status=status_result,
        verdict=status_result,
        runtime_ms=last_runtime_ms or 0.0,
        memory_kb=last_memory_kb or 0.0,
        passed_test_cases=passed_test_cases,
        total_test_cases=total_test_cases,
        failed_case_index=failed_case_index,
        failed_test_number=failed_case_index + 1 if failed_case_index is not None else None,
        compile_error=compile_error or "",
        stderr=stderr or "",
        failure_reason=_build_failure_reason(status_result, compile_error, stderr),
        ai_feedback=ai_feedback or AIFeedbackResponse(),
    )