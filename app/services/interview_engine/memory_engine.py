"""
AIRE Memory Engine
===================
Implements:
    - LTM (#7)  Cross-session long-term memory (EMA-based concept mastery)
    - LMA (#14) Layered memory architecture (working / session / long-term)

This engine owns the update policy and projection logic; the actual
persistence (MongoDB reads/writes) is delegated to the injected
CandidateProfileRepositoryProtocol / SessionRepositoryProtocol -- wire
these to your existing Motor collections in the application layer.
"""

from __future__ import annotations

from typing import Any, Optional

from . import (
    CandidateProfileRepositoryProtocol,
    ConceptScore,
    InterviewStateSnapshot,
    SessionRepositoryProtocol,
    utcnow,
)

EMA_ALPHA = 0.3
DEFAULT_SEED_K = 5
RECENT_RESPONSE_WINDOW = 3
WEAK_SCORE_THRESHOLD = 0.4


class MemoryEngine:
    def __init__(
        self,
        session_repo: SessionRepositoryProtocol,
        candidate_profile_repo: CandidateProfileRepositoryProtocol,
    ) -> None:
        self._sessions = session_repo
        self._profiles = candidate_profile_repo

    # ------------------------------------------------------------------ #
    # Session memory (LMA tier 2)
    # ------------------------------------------------------------------ #

    async def load_session_state(self, session_id: str) -> Optional[InterviewStateSnapshot]:
        raw = await self._sessions.get_state(session_id)
        if raw is None:
            return None

        state_payload = raw.get("state") if isinstance(raw.get("state"), dict) else raw
        state_payload = dict(state_payload)
        state_payload.setdefault("session_id", session_id)
        if state_payload.get("candidate_id") is None and raw.get("candidate_id") is not None:
            state_payload["candidate_id"] = raw.get("candidate_id")
        if state_payload.get("current_main_question_id") is None and raw.get("question_id") is not None:
            state_payload["current_main_question_id"] = raw.get("question_id")
        if state_payload.get("persona") is None and raw.get("persona") is not None:
            state_payload["persona"] = raw.get("persona")

        return InterviewStateSnapshot.model_validate(state_payload)

    async def save_session_state(self, state: InterviewStateSnapshot) -> None:
        payload = state.model_dump(mode="json")
        # keep the recent-response window bounded before persisting
        payload["recent_response_texts"] = state.recent_response_texts[-RECENT_RESPONSE_WINDOW:]
        await self._sessions.save_state(state.session_id, payload)

    def project_for_prompt(self, state: InterviewStateSnapshot, fields: list[str]) -> dict[str, Any]:
        """Return only the minimal structured slice needed for a prompt -- never dump full state."""
        full = state.model_dump(mode="json")
        return {f: full.get(f) for f in fields if f in full}

    # ------------------------------------------------------------------ #
    # Long-term memory (LMA tier 3, LTM #7)
    # ------------------------------------------------------------------ #

    async def update_long_term_memory(
        self, candidate_id: str, session_concept_scores: dict[str, ConceptScore]
    ) -> None:
        profile = await self._profiles.get_profile(candidate_id)
        mastery: dict[str, Any] = profile.get("concept_mastery", {})

        for concept, cs in session_concept_scores.items():
            existing = mastery.get(concept, {"ema_score": cs.score, "times_tested": 0, "weak_streak": 0})
            new_ema = EMA_ALPHA * cs.score + (1 - EMA_ALPHA) * existing.get("ema_score", cs.score)
            weak_streak = existing.get("weak_streak", 0)
            weak_streak = weak_streak + 1 if cs.score < WEAK_SCORE_THRESHOLD else 0
            mastery[concept] = {
                "ema_score": new_ema,
                "last_seen": utcnow().isoformat(),
                "times_tested": existing.get("times_tested", 0) + 1,
                "weak_streak": weak_streak,
            }

        profile["concept_mastery"] = mastery
        profile["candidate_id"] = candidate_id
        profile["session_count"] = profile.get("session_count", 0) + 1
        profile["last_active"] = utcnow().isoformat()
        await self._profiles.save_profile(candidate_id, profile)

    async def get_session_seed(self, candidate_id: str, k: int = DEFAULT_SEED_K) -> dict[str, list[str]]:
        profile = await self._profiles.get_profile(candidate_id)
        mastery: dict[str, Any] = profile.get("concept_mastery", {})
        if not mastery:
            return {"weak_focus": [], "strong_confidence": []}

        ranked = sorted(mastery.items(), key=lambda kv: kv[1].get("ema_score", 0.0))
        weak = [name for name, _ in ranked[:k]]
        strong = [name for name, _ in ranked[-k:][::-1]]
        return {"weak_focus": weak, "strong_confidence": strong}

    def get_weak_streaks(self, profile: dict[str, Any]) -> dict[str, int]:
        mastery = profile.get("concept_mastery", {})
        return {name: data.get("weak_streak", 0) for name, data in mastery.items()}

    async def get_candidate_history_for_scoring(self, candidate_id: str) -> dict[str, Any]:
        """Convenience accessor used by ComprehensionEngine.score_concepts (CCG, #2)."""
        profile = await self._profiles.get_profile(candidate_id)
        return {"weak_streaks": self.get_weak_streaks(profile)}

    # ------------------------------------------------------------------ #
    # Archival (LMA retention policy)
    # ------------------------------------------------------------------ #

    async def archive_session(self, state: InterviewStateSnapshot) -> None:
        summary = {
            "session_id": state.session_id,
            "candidate_id": state.candidate_id,
            "turn_count": state.turn_index,
            "final_skill_estimate": state.skill_estimate,
            "final_difficulty_band": state.difficulty_band.value,
            "covered_concepts": sorted(state.covered_concepts),
            "archived_at": utcnow().isoformat(),
        }
        await self._sessions.archive_state(state.session_id, summary)
        await self._sessions.delete_state(state.session_id)