"""
AIRE Prompt Builder
====================
Centralizes ALL prompt/message construction and lightweight response
parsing for the AIRE engines. This module never calls Groq itself --
it only builds `list[dict[str, str]]` message payloads for whichever
GroqClientProtocol implementation the caller injects, and parses the
resulting text/JSON back into plain Python structures.

Keeping this in one place means the "voice" of the interviewer (persona,
templates, banned patterns) can be tuned without touching engine logic.
"""

from __future__ import annotations

import json
import re
from typing import Any, Optional

from . import FollowUpIntent, InterviewerPersona, InterviewStateSnapshot, QuestionMeta, ResponseType, StyleGuardrails

FOLLOWUP_TEMPLATES: dict[FollowUpIntent, list[str]] = {
    FollowUpIntent.PROBE: [
        "Interesting — before we move on, how would you handle {concept} here?",
        "One more thing on this: what's your take on {concept}?",
    ],
    FollowUpIntent.EXTEND: [
        "You mentioned {concept} — walk me through why that actually works.",
        "Can you go a bit deeper on {concept}? Why does that hold?",
    ],
    FollowUpIntent.CORRECT: [
        "Let's dig into that a bit — what happens with {concept} in an edge case?",
        "I want to double check something — how does {concept} actually behave here?",
    ],
    FollowUpIntent.CLARIFY: [
        "Just to make sure I follow — can you restate how {concept} fits in?",
    ],
}


def _safe_json_loads(raw: str) -> Optional[dict[str, Any]]:
    raw = raw.strip()
    raw = re.sub(r"^```(json)?|```$", "", raw, flags=re.MULTILINE).strip()
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


class PromptBuilder:
    # ------------------------------------------------------------------ #
    # Concept tagging (used by ComprehensionEngine, SAD #1)
    # ------------------------------------------------------------------ #

    def concept_tagging_prompt(
        self, unmatched: list[tuple[str, str]], expected_concepts: list[str]
    ) -> list[dict[str, str]]:
        spans_block = "\n".join(f"{cid}: {text}" for cid, text in unmatched)
        system = (
            "You are a technical concept tagger for an interview grading system. "
            "Given candidate answer spans and a list of expected concepts, return ONLY "
            "a JSON object mapping each span id to an array of expected concepts it "
            "actually discusses. If a span discusses none of the expected concepts, map "
            "it to an empty array. Do not invent concepts outside the provided list."
        )
        user = (
            f"Expected concepts: {expected_concepts}\n\n"
            f"Spans:\n{spans_block}\n\n"
            'Return format: {"<span_id>": ["concept_a"], ...}'
        )
        return [{"role": "system", "content": system}, {"role": "user", "content": user}]

    def parse_concept_tagging_response(self, raw: str, claim_ids: list[str]) -> dict[str, list[str]]:
        parsed = _safe_json_loads(raw) or {}
        result: dict[str, list[str]] = {}
        for cid in claim_ids:
            value = parsed.get(cid, [])
            result[cid] = value if isinstance(value, list) else []
        return result

    # ------------------------------------------------------------------ #
    # Factuality tiebreak (used by EvaluationEngine, CSE #3)
    # ------------------------------------------------------------------ #

    def factuality_check_prompt(self, answer_text: str, question: QuestionMeta) -> list[dict[str, str]]:
        core_names = [c.get("name") for c in (question.core_concepts or question.expected_concepts)]
        system = (
            "You are a strict technical fact-checker for interview answers. "
            'Return ONLY JSON: {"factual_score": <0.0-1.0>, "contradicts_rubric": <true|false>}. '
            "factual_score reflects how factually sound the answer is with respect to the listed "
            "core concepts, independent of completeness."
        )
        user = f"Core concepts: {core_names}\n\nCandidate answer:\n{answer_text}"
        return [{"role": "system", "content": system}, {"role": "user", "content": user}]

    def parse_factuality_response(self, raw: str) -> Optional[float]:
        parsed = _safe_json_loads(raw)
        if not parsed:
            return None
        score = parsed.get("factual_score")
        try:
            score = float(score)
        except (TypeError, ValueError):
            return None
        return max(0.0, min(1.0, score))

    # ------------------------------------------------------------------ #
    # Groq interview answer evaluation
    # ------------------------------------------------------------------ #

    def groq_evaluation_prompt(
        self,
        raw_answer: str,
        question: QuestionMeta,
        state: InterviewStateSnapshot,
    ) -> list[dict[str, str]]:
        interview_type = question.interview_type or "technical"
        role = question.role or "Any"
        difficulty = question.difficulty or "medium"
        expected_concepts = [c.get("name") for c in question.expected_concepts or []]
        previous_questions = state.asked_question_texts or []
        conversation_history = state.recent_response_texts or []

        system = (
            "You are a senior technical interviewer evaluating a candidate's answer. "
            "Do not compare keywords. Understand the meaning of the answer semantically and "
            "evaluate it against the question, topic, role, difficulty, and expected concepts. "
            "Judge the answer based on clarity, structure, confidence, completeness, technical correctness, "
            "and logical flow. Return ONLY valid JSON with the exact schema described in the user prompt. "
            "Be honest and balanced: call an answer excellent only when it is truly excellent, average when it is average, "
            "and weak when it is weak. Do not inflate scores or invent missing concepts. "
            "Evaluate ONLY the current interview question. First identify the question intent, the expected learning objective, "
            "and the required concepts for this specific question. Ignore concepts that are only related to the broader topic "
            "or to other questions. Do not use previous questions, prior conversation, or general knowledge-base concepts "
            "as if they were required for this answer. "
            "Distinguish between required concepts, optional concepts, and advanced concepts. Only required concepts affect scoring. "
            "Treat optional and advanced concepts as additional knowledge that can raise the score if mentioned, but never as mandatory. "
            "Every strength, weakness, recommendation, and follow-up question must be grounded in evidence from the candidate's answer. "
            "If there is no evidence, omit that point rather than generating a generic or speculative comment. "
            "Do not include markdown, commentary, or any extra fields."
        )

        core_concepts = [c.get("name") for c in question.core_concepts or []]
        user = (
            f"Interview type: {interview_type}\n"
            f"Role: {role}\n"
            f"Difficulty: {difficulty}\n"
            f"Question topic: {question.topic}\n"
            f"Question: {question.text}\n"
            f"Expected concepts: {expected_concepts}\n"
            f"Core concepts: {core_concepts}\n"
            f"Candidate answer:\n{raw_answer.strip()}\n"
        )

        if previous_questions:
            user += f"\nPrevious questions: {previous_questions}\n"
        if conversation_history:
            user += f"\nConversation history: {conversation_history}\n"

        user += (
            "\nReturn JSON matching this schema exactly: "
            "{\"overall_score\": <int 0-100>, \"verdict\": <string>, "
            "\"technical_accuracy\": <int 0-100>, \"communication\": <int 0-100>, "
            "\"concept_coverage\": <int 0-100>, \"strengths\": [<string>, ...], "
            "\"weaknesses\": [<string>, ...], \"missing_concepts\": [<string>, ...], "
            "\"recommendations\": [<string>, ...], \"follow_up_question\": <string>, "
            "\"reasoning\": <string>, \"hiring_signal\": <string>}"
            "\nUse these verdict rules exactly: 95-100 => correct, 85-94 => correct, "
            "70-84 => partially_correct, 50-69 => incorrect, 0-49 => incorrect or off_topic. "
            "The verdict must always match the overall_score. Do NOT return incorrect with a score of 85 or higher. "
            "Only list missing_concepts that are genuinely absent or insufficiently explained. "
            "Every missing concept must satisfy two conditions: it must be required by this specific question and it must be absent from the candidate's answer. "
            "Before listing a concept as missing, verify that the candidate did not already explain it using different wording or a similar idea. "
            "Do not mark optional or advanced concepts as missing. If a candidate mentions an optional or advanced concept, mention it as additional strength or additional knowledge rather than a gap. "
            "Before generating weaknesses, recommendations, or follow-up questions, validate that each item is directly required by this question. "
            "If an item is not directly required by this question, do not include it. "
            "Strengths must cite what the candidate answered well. Weaknesses must explain exactly what is missing or unclear. "
            "Do not invent strengths or weaknesses. If a point is not directly supported by the answer, leave it out. "
            "Recommendations must be actionable and specific. "
            "If the answer is strong, ask a deeper follow-up question that continues this same question. If the answer is average, ask for a clarification or a practical example tied to this question. "
            "If the answer is weak, ask a concept-building follow-up question that helps the candidate answer this same question better. Do not ask about concepts the candidate already explained correctly or concepts unrelated to this question."
        )

        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

    # ------------------------------------------------------------------ #
    # Follow-up generation (DialogueEngine, FGE #5)
    # ------------------------------------------------------------------ #

    def followup_prompt(
        self,
        intent: FollowUpIntent,
        concept: str,
        candidate_claim: str,
        persona: InterviewerPersona,
    ) -> list[dict[str, str]]:
        template = FOLLOWUP_TEMPLATES[intent][0]
        system = (
            f"You are a {persona.tone}, {persona.strictness} technical interviewer. "
            "Rewrite the given template into ONE natural, conversational sentence, "
            "keeping its intent and target concept. No restating the candidate's whole "
            "answer. Output only the sentence, nothing else."
        )
        user = (
            f"Template: {template.format(concept=concept)}\n"
            f"Candidate's relevant statement: {candidate_claim or '(none)'}\n"
            f"Target concept: {concept}"
        )
        return [{"role": "system", "content": system}, {"role": "user", "content": user}]

    def followup_variation_prompt(
        self, original_messages: list[dict[str, str]], previous_attempt: str
    ) -> list[dict[str, str]]:
        variation_note = {
            "role": "user",
            "content": (
                f'That was too similar to a question already asked: "{previous_attempt}". '
                "Ask essentially the same thing but from a clearly different angle or phrasing."
            ),
        }
        return original_messages + [{"role": "assistant", "content": previous_attempt}, variation_note]

    def positive_callout_prompt(self, concept: str, persona: InterviewerPersona) -> list[dict[str, str]]:
        system = (
            f"You are a {persona.tone} technical interviewer. In ONE short sentence, "
            f"acknowledge the candidate's correct handling of '{concept}' specifically -- "
            "no generic praise, no exclamation points, be specific and brief."
        )
        return [{"role": "system", "content": system}, {"role": "user", "content": f"Concept: {concept}"}]

    # ------------------------------------------------------------------ #
    # Self-refinement repair (QualityEngine, SRL #11)
    # ------------------------------------------------------------------ #

    def repair_prompt(
        self, draft_text: str, issues: list[str], guardrails: StyleGuardrails
    ) -> list[dict[str, str]]:
        system = (
            f"Rewrite the text in at most {guardrails.max_sentences} sentence(s). "
            "Keep the same meaning and intent. Do not start with 'That's' or any phrase "
            "already used before. Avoid generic praise phrases entirely. Output only the "
            "rewritten text."
        )
        user = f"Issues found: {issues}\n\nOriginal text:\n{draft_text}"
        return [{"role": "system", "content": system}, {"role": "user", "content": user}]

    # ------------------------------------------------------------------ #
    # Verification repair (QualityEngine, RVL #12)
    # ------------------------------------------------------------------ #

    def verification_repair_prompt(
        self, text: str, reasons: list[str], response_type: ResponseType
    ) -> list[dict[str, str]]:
        system = (
            "Rewrite the following interviewer response to fix the listed problems. "
            "Keep it short and natural. Do not introduce new unverified technical claims. "
            "Output only the corrected text."
        )
        user = f"Response type: {response_type.value}\nProblems: {reasons}\n\nText:\n{text}"
        return [{"role": "system", "content": system}, {"role": "user", "content": user}]

    def repair_and_verify_prompt(
        self,
        text: str,
        issues: list[str],
        reasons: list[str],
        guardrails: StyleGuardrails,
        response_type: ResponseType,
    ) -> list[dict[str, str]]:
        system = (
            f"Rewrite the following interviewer response to fix the listed style issues and verification problems. "
            "Keep the same meaning and intent, keep it short and natural, and do not introduce any new unverified technical claims. "
            f"Keep the response appropriate for a {response_type.value}. Output only the corrected text."
        )
        user = (
            f"Response type: {response_type.value}\n"
            f"Style issues: {issues}\n"
            f"Verification problems: {reasons}\n"
            f"Max sentences: {guardrails.max_sentences}\n"
            f"Banned phrases: {guardrails.banned_phrases}\n\n"
            f"Text:\n{text}"
        )
        return [{"role": "system", "content": system}, {"role": "user", "content": user}]