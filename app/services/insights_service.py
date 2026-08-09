from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import json
import logging

import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import get_settings
from app.services.progress_service import ProgressService
from app.utils.groq_client import GROQ_CHAT_COMPLETIONS_URL, GROQ_MODEL

settings = get_settings()
logger = logging.getLogger(__name__)


def _get_module_title(module: dict[str, Any]) -> str:
    return module.get("name") or module.get("key", "this area")


def _format_recommendation(module: dict[str, Any]) -> dict[str, str]:
    key = module.get("key", "coding")
    title = module.get("name", "Continue Preparing")
    detail = module.get("detail", "Continue making progress in this module.")
    route_map = {
        "interview": "/interview",
        "aptitude": "/aptitude",
        "coding": "/coding",
        "resume": "/resume",
        "profile": "/profile",
    }
    return {
        "title": title,
        "description": detail,
        "route": route_map.get(key, "/coding"),
    }


def _build_strengths(modules: list[dict[str, Any]]) -> list[str]:
    strengths: list[str] = []
    for module in modules:
        progress = module.get("progress", 0) or 0
        if progress >= 70 and module.get("key") != "profile":
            strengths.append(
                f"Strong progress in {_get_module_title(module)}: {module.get('detail', 'Keep up the momentum.')}"
            )
    return strengths


def _build_improvement_areas(modules: list[dict[str, Any]]) -> list[str]:
    areas: list[str] = []
    for module in modules:
        progress = module.get("progress", 0) or 0
        if progress < 70:
            areas.append(
                f"{_get_module_title(module)} needs more attention: {module.get('detail', 'Spend some time improving this area.')}"
            )
    return areas


def _build_recommendations(modules: list[dict[str, Any]]) -> list[dict[str, str]]:
    if not modules:
        return [
            {
                "title": "Start your preparation",
                "description": "Explore the modules and begin with the area where you need the most progress.",
                "route": "/dashboard",
            }
        ]

    recommendations: list[dict[str, str]] = []
    low_modules = sorted(
        [m for m in modules if (m.get("progress", 0) or 0) < 70],
        key=lambda item: item.get("progress", 0) or 0,
    )
    high_modules = sorted(
        [m for m in modules if (m.get("progress", 0) or 0) >= 70],
        key=lambda item: -(item.get("progress", 0) or 0),
    )

    for module in low_modules[:3]:
        recommendations.append(_format_recommendation(module))

    if not recommendations and high_modules:
        recommendations.append(
            {
                "title": f"Keep improving your {high_modules[0].get('name')}",
                "description": f"You have good momentum in {high_modules[0].get('name')}. Continue to build consistency.",
                "route": _format_recommendation(high_modules[0])["route"],
            }
        )

    if len(recommendations) < 4:
        profile_module = next((m for m in modules if m.get("key") == "profile"), None)
        if profile_module:
            recommendations.append(
                {
                    "title": "Complete your profile",
                    "description": "A complete profile helps the AI personalize your preparation advice.",
                    "route": "/profile",
                }
            )

    return recommendations[:5]


def _build_summary(progress_data: dict[str, Any]) -> dict[str, str]:
    overview_metrics = progress_data.get("overview", {}) if isinstance(progress_data, dict) else {}
    overall = overview_metrics.get("percentage", 0) or 0
    overview_message = overview_metrics.get("message") or "Use your preparation insights to focus on the next most valuable step."

    if overall >= 85:
        observation = "You are on track for placement readiness. Keep refining your strongest areas and maintaining momentum."
    elif overall >= 50:
        observation = "You are making steady progress. Concentrate on the modules where your scores are lower to improve faster."
    elif overall > 0:
        observation = "Your preparation is getting started. Focus on the modules with the lowest progress to gain momentum."
    else:
        observation = "Your preparation is still getting started. Focus on the most underperforming module to build momentum."

    return {
        "overview": overview_message,
        "progress": f"{int(overall)}%",
        "strengths": "Based on your progress, the modules with the best completion rates are highlighted.",
        "weaknesses": "The AI recommends concentrating on the modules with lower progress and fewer completed activities.",
        "observation": observation,
    }


def _get_last_updated(progress_data: dict[str, Any]) -> str:
    if not isinstance(progress_data, dict):
        return datetime.now(timezone.utc).isoformat()

    activity = progress_data.get("activity")
    if isinstance(activity, list) and activity:
        latest = activity[0]
        if isinstance(latest, dict) and latest.get("timestamp"):
            return datetime.now(timezone.utc).isoformat()

    return datetime.now(timezone.utc).isoformat()


def _extract_module_scores(progress: dict[str, Any]) -> dict[str, int]:
    if not isinstance(progress, dict):
        return {}
    return {
        module.get("key") or module.get("name", "unknown"): int(module.get("progress", 0) or 0)
        for module in progress.get("modules", [])
        if isinstance(module, dict)
    }


def _find_lowest_module(modules: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [m for m in modules if isinstance(m, dict)]
    if not candidates:
        return None
    return min(candidates, key=lambda item: int(item.get("progress", 0) or 0))


def _build_personalized_study_recommendation(modules: list[dict[str, Any]], question: str) -> str:
    lowest = _find_lowest_module(modules)
    if not lowest:
        return "Use the AI insights page to see your current progress and identify the best next step."

    module_name = lowest.get("name") or lowest.get("key", "this area")
    detail = lowest.get("detail") or "This module needs more attention."
    progress = int(lowest.get("progress", 0) or 0)
    key = lowest.get("key")

    if key == "coding":
        return (
            "Your weakest area is Coding Practice. "
            f"With only {progress}% progress, focus on solving more problems in your weakest topics and improving submission accuracy."
        )
    if key == "interview":
        return (
            "Your weakest area is AI Interview. "
            f"With only {progress}% progress, practice mock interviews and work on the topics where your confidence is lowest."
        )
    if key == "aptitude":
        return (
            "Your weakest area is Aptitude. "
            f"With only {progress}% progress, take more timed practice tests and review the concepts you missed."
        )
    if key == "resume":
        return (
            "Your weakest area is Resume Analyzer. "
            f"With only {progress}% progress, improve your resume by matching it to your target role and boosting your ATS score."
        )
    if key == "profile":
        return (
            "Your weakest area is Profile. "
            "Complete your profile details so AI recommendations can be tailored to your target role, skills, and education."
        )

    return f"Focus next on {module_name}. {detail}"


async def generate_insights(db: AsyncIOMotorDatabase, user_id: str) -> dict[str, Any]:
    service = ProgressService(db)
    progress = await service.get_summary(user_id)
    modules = progress.get("modules", []) if isinstance(progress, dict) else []

    strengths = _build_strengths(modules)
    improvement_areas = _build_improvement_areas(modules)
    recommendations = _build_recommendations(modules)
    summary = _build_summary(progress if isinstance(progress, dict) else {})
    last_updated = _get_last_updated(progress)
    module_scores = _extract_module_scores(progress)

    return {
        "lastUpdated": last_updated,
        "last_updated": last_updated,
        "summary": summary,
        "strengths": strengths,
        "improvements": improvement_areas,
        "improvementAreas": improvement_areas,
        "recommendations": recommendations,
        "modules": modules,
        "moduleScores": module_scores,
    }


async def _deterministic_answer_insight_question(db: AsyncIOMotorDatabase, user_id: str, question: str) -> str:
    insights = await generate_insights(db, user_id)
    lower_question = question.lower()
    modules = insights.get("modules", []) if isinstance(insights.get("modules"), list) else []
    module_scores = insights.get("moduleScores", {})

    if "resume" in lower_question:
        score = module_scores.get("resume", 0)
        if score >= 75:
            return "Your resume is in good shape. Keep refining it for your target role and update it with recent accomplishments."
        return "Your resume needs attention. Focus on improving your ATS score and aligning it with the roles you are applying to."

    if "coding" in lower_question or "problem" in lower_question:
        score = module_scores.get("coding", 0)
        if score >= 70:
            return "Your coding practice is strong. Continue solving problems consistently and focus on tougher topics to improve further."
        return "Your coding progress can improve. Solve more problems and review the topics where your accuracy is low."

    if "interview" in lower_question or "conversation" in lower_question:
        score = module_scores.get("interview", 0)
        if score >= 70:
            return "Your interview preparation is progressing well. Practice more mock interviews to build confidence and polish your responses."
        return "Your interview preparation could improve. Review your past interviews and work on the weakest areas."

    if "aptitude" in lower_question or "test" in lower_question:
        score = module_scores.get("aptitude", 0)
        if score >= 70:
            return "Your aptitude practice is solid. Keep practicing timed tests and maintain accuracy under pressure."
        return "Your aptitude preparation needs work. Focus on test-taking speed and revise the concepts where you made mistakes."

    if "profile" in lower_question or "strength" in lower_question:
        profile_score = module_scores.get("profile", 0)
        if profile_score >= 80:
            return "Your profile is well-completed. Keep it up, and make sure your target role and skills remain current."
        return "Complete your profile details to get more personalized insights and better-tailored recommendations."

    if any(token in lower_question for token in ["what should i study next", "what should i study", "study next", "focus next", "what to study next", "what next"]):
        return _build_personalized_study_recommendation(modules, lower_question)

    if "next" in lower_question or "focus" in lower_question or "improve" in lower_question:
        return insights.get("summary", {}).get("observation") or _build_personalized_study_recommendation(modules, lower_question)

    return insights.get("summary", {}).get("overview") or "Use the AI insights page to see your current progress and identify the best next step."


async def answer_insight_question(db: AsyncIOMotorDatabase, user_id: str, question: str) -> str:
    # Generate the deterministic answer first (fast, offline)
    try:
        deterministic = await _deterministic_answer_insight_question(db, user_id, question)
    except Exception:
        logger.exception("Deterministic answer generation failed")
        deterministic = "Unable to generate an answer at this time."

    # If Groq isn't configured, return the deterministic response
    if not settings.GROQ_API_KEY:
        return deterministic

    # Build a concise context for the model
    try:
        insights = await generate_insights(db, user_id)
        context = {"insights": insights_summary_for_groq(insights), "question": question}
    except Exception:
        context = {"question": question}

    system_prompt = (
        "You are a helpful, concise career coach and technical mentor. "
        "Given the user's preparation context and a question, produce a JSON object with keys: answer (string), timestamp (ISO8601 string), sources (array of source names e.g. [\"Resume\", \"Coding\"]). "
        "Keep the answer focused and include actionable next steps when appropriate."
    )

    user_prompt = f"User question:\n{question}\n\nContext:\n{json.dumps(context)[:16000]}"

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
    }

    headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(GROQ_CHAT_COMPLETIONS_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
    except Exception:
        logger.exception("Groq API request failed for insights query")
        return deterministic

    try:
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        answer = parsed.get("answer") or parsed.get("response") or parsed.get("text")
        if answer:
            return answer
    except Exception:
        logger.exception("Failed to parse Groq response for insights query")

    return deterministic


def insights_summary_for_groq(insights: dict[str, Any]) -> dict[str, Any]:
    # Reduce the insights object to a compact summary suitable for prompts
    return {
        "summary": insights.get("summary") if isinstance(insights.get("summary"), dict) else {},
        "strengths": insights.get("strengths", []),
        "improvementAreas": insights.get("improvementAreas", []),
        "recommendations": insights.get("recommendations", []),
        "moduleScores": insights.get("moduleScores", {}),
    }
