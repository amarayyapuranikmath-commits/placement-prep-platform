"""
AIRE Adaptivity Engine
=======================
Implements ADC (#6): Elo-style adaptive difficulty controller.
Pure arithmetic -- no LLM calls, no external dependencies.
"""

from __future__ import annotations

from . import CorrectnessVerdict, DifficultyBand, DifficultyUpdateResult, Verdict

EARLY_SESSION_TURN_THRESHOLD = 3
K_FACTOR_EARLY = 32.0
K_FACTOR_LATE = 12.0
ELO_SCALE = 400.0

BAND_THRESHOLDS: list[tuple[float, DifficultyBand]] = [
    (1000.0, DifficultyBand.EASY),
    (1300.0, DifficultyBand.MEDIUM),
    (1600.0, DifficultyBand.HARD),
]
BAND_ORDER = [DifficultyBand.EASY, DifficultyBand.MEDIUM, DifficultyBand.HARD, DifficultyBand.EXPERT]

VERDICT_TO_ACTUAL: dict[Verdict, float] = {
    Verdict.CORRECT: 1.0,
    Verdict.PARTIALLY_CORRECT: 0.5,
    Verdict.INCORRECT: 0.0,
    Verdict.OFF_TOPIC: 0.0,
}

OFF_TOPIC_STREAK_GUARD = 2


class AdaptivityEngine:
    def update_difficulty(
        self,
        skill_estimate: float,
        question_difficulty_rating: float,
        verdict: CorrectnessVerdict,
        turn_index: int,
        recent_off_topic_count: int = 0,
    ) -> DifficultyUpdateResult:
        k = K_FACTOR_EARLY if turn_index <= EARLY_SESSION_TURN_THRESHOLD else K_FACTOR_LATE
        expected = 1.0 / (1.0 + 10 ** ((question_difficulty_rating - skill_estimate) / ELO_SCALE))
        actual = VERDICT_TO_ACTUAL[verdict.verdict]

        new_skill = skill_estimate + k * (actual - expected)

        current_band = self._band_from_score(skill_estimate)
        proposed_band = self._band_from_score(new_skill)
        clamped_band = self._clamp_one_step(current_band, proposed_band)

        if verdict.verdict == Verdict.OFF_TOPIC and recent_off_topic_count >= OFF_TOPIC_STREAK_GUARD:
            return DifficultyUpdateResult(
                new_skill_estimate=skill_estimate,
                next_difficulty=current_band,
                reason="held_steady_pending_clarification",
            )

        reason = self._derive_reason(actual, expected)
        return DifficultyUpdateResult(new_skill_estimate=new_skill, next_difficulty=clamped_band, reason=reason)

    def _band_from_score(self, score: float) -> DifficultyBand:
        for threshold, band in BAND_THRESHOLDS:
            if score < threshold:
                return band
        return DifficultyBand.EXPERT

    def _clamp_one_step(self, current: DifficultyBand, proposed: DifficultyBand) -> DifficultyBand:
        current_idx = BAND_ORDER.index(current)
        proposed_idx = BAND_ORDER.index(proposed)
        if abs(proposed_idx - current_idx) <= 1:
            return proposed
        step = 1 if proposed_idx > current_idx else -1
        return BAND_ORDER[current_idx + step]

    def _derive_reason(self, actual: float, expected: float) -> str:
        if actual > expected:
            return "outperformed_expectation"
        if actual < expected:
            return "underperformed_expectation"
        return "matched_expectation"