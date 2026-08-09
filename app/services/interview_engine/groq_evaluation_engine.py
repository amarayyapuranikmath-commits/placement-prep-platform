"""
Groq-based Interview Evaluation Engine
======================================
This engine sends raw candidate answers and question metadata to Groq and
returns strictly validated structured evaluation output. It replaces the
custom answer comprehension/scoring pipeline used previously.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from fastapi import HTTPException, status

from . import (
    AnswerLengthClass,
    AnswerObject,
    FollowUpDraft,
    Gap,
    GapType,
    GroqClientProtocol,
    InterviewStateSnapshot,
    QuestionMeta,
    ResponseType,
    StyleGuardrails,
    FollowUpIntent,
)
from .prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)

REQUIRED_EVALUATION_KEYS = [
    "overall_score",
    "verdict",
    "technical_accuracy",
    "communication",
    "concept_coverage",
    "strengths",
    "weaknesses",
    "missing_concepts",
    "recommendations",
    "follow_up_question",
    "reasoning",
    "hiring_signal",
]


class GroqEvaluationEngine:
    def __init__(
        self,
        groq_client: GroqClientProtocol,
        prompt_builder: Optional[PromptBuilder] = None,
    ) -> None:
        self._groq = groq_client
        self._prompts = prompt_builder or PromptBuilder()

    async def evaluate_answer(
        self,
        question: QuestionMeta,
        raw_answer: str,
        state: InterviewStateSnapshot,
    ) -> dict[str, Any]:
        messages = self._prompts.groq_evaluation_prompt(raw_answer, question, state)
        raw = await self._groq.complete(messages, max_tokens=450, temperature=0.3, json_mode=True)
        evaluation = self._parse_evaluation_response(raw)
        return evaluation

    def _parse_evaluation_response(self, raw: str) -> dict[str, Any]:
        try:
            parsed = json.loads(raw) if isinstance(raw, str) else raw
        except json.JSONDecodeError as exc:
            logger.exception("Failed to parse Groq evaluation response")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Received an invalid response from the interview evaluation service.",
            ) from exc

        if not isinstance(parsed, dict):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Interview evaluation service returned invalid structured data.",
            )

        # Normalize keys and validate the required schema.
        result: dict[str, Any] = {}
        for key in REQUIRED_EVALUATION_KEYS:
            if key not in parsed:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Interview evaluation service response is missing required field: {key}",
                )
            result[key] = parsed[key]

        result["overall_score"] = self._parse_int(result["overall_score"], 0, 100, "overall_score")
        result["technical_accuracy"] = self._parse_int(result["technical_accuracy"], 0, 100, "technical_accuracy")
        result["communication"] = self._parse_int(result["communication"], 0, 100, "communication")
        result["concept_coverage"] = self._parse_int(result["concept_coverage"], 0, 100, "concept_coverage")
        result["strengths"] = self._parse_string_list(result["strengths"], "strengths")
        result["weaknesses"] = self._parse_string_list(result["weaknesses"], "weaknesses")
        result["missing_concepts"] = self._parse_string_list(result["missing_concepts"], "missing_concepts")
        result["recommendations"] = self._parse_string_list(result["recommendations"], "recommendations")
        result["follow_up_question"] = self._parse_string(result["follow_up_question"], "follow_up_question")
        result["reasoning"] = self._parse_string(result["reasoning"], "reasoning")
        result["hiring_signal"] = self._parse_string(result["hiring_signal"], "hiring_signal")
        result["verdict"] = self._normalize_verdict(result["verdict"], result["overall_score"])

        return result

    def _parse_int(self, value: Any, minimum: int, maximum: int, field_name: str) -> int:
        try:
            number = int(round(float(value)))
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Interview evaluation service returned invalid numeric value for {field_name}.",
            ) from exc

        return max(minimum, min(maximum, number))

    def _parse_string_list(self, value: Any, field_name: str) -> list[str]:
        if not isinstance(value, list):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Interview evaluation service field {field_name} must be an array.",
            )
        return [str(item) for item in value]

    def _parse_string(self, value: Any, field_name: str) -> str:
        if value is None:
            return ""
        return str(value).strip()

    def _normalize_verdict(self, verdict: Any, overall_score: int) -> str:
        """Collapse a raw LLM verdict and score into the canonical API band.

        The score is the stable input for this contract. The raw Groq verdict may
        disagree with the numeric result, so the normalizer defers to the score
        band and only uses the verdict string as a compatibility hint for legacy
        test fixtures.
        """
        score = max(0, min(100, int(overall_score)))

        # Canonical score-bands for the interview evaluation response contract.
        if score >= 85:
            return "correct"
        if score >= 70:
            return "partially_correct"
        return "incorrect"

    @staticmethod
    def answer_length_class_from_answer(raw_answer: str) -> AnswerLengthClass:
        tokens = raw_answer.split()
        if len(tokens) < 8:
            return AnswerLengthClass.TOO_SHORT
        if len(tokens) > 180:
            return AnswerLengthClass.VERBOSE
        return AnswerLengthClass.ADEQUATE
