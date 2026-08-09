from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import logging

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services import profile_service, resume_service
from app.services import insights_service

logger = logging.getLogger(__name__)


def _safe_iso_timestamp(value: Any) -> str | None:
    if value is None:
        return None

    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()

    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.isoformat()
        except Exception:
            return value

    return str(value)


async def build_dashboard(db: AsyncIOMotorDatabase, user_id: str) -> dict[str, Any]:
    # Profile
    profile = await profile_service.get_profile(db, user_id)

    display_name = profile.user_id
    try:
        collection = db["users"]
        if ObjectId.is_valid(user_id):
            user_doc = await collection.find_one({"_id": ObjectId(user_id)})
        else:
            user_doc = await collection.find_one({"email": user_id})
        if user_doc:
            display_name = user_doc.get("full_name") or user_doc.get("email") or profile.user_id
    except Exception:
        logger.exception("Failed to resolve dashboard display name")

    # Latest resume (summary)
    try:
        resume_history = await resume_service.get_resume_history(db, user_id)
        latest_resume = resume_history.resumes[0] if resume_history.resumes else None
    except Exception:
        latest_resume = None

    # Progress-derived focus: reuse progress service indirectly via insights
    try:
        insights = await insights_service.generate_insights(db, user_id)
    except Exception:
        insights = {}

    module_scores = insights.get("moduleScores", {}) if isinstance(insights, dict) else {}

    # Generate 3 personalized tasks
    today_focus = []
    if module_scores:
        # pick up to 3 lowest modules
        sorted_modules = sorted(module_scores.items(), key=lambda kv: kv[1])
        for key, score in sorted_modules[:3]:
            title = f"Work on {key.capitalize()}"
            desc = "Continue your practice in this area to improve your readiness."
            route = {
                "coding": "/coding",
                "interview": "/interview",
                "aptitude": "/aptitude",
                "resume": "/resume",
                "profile": "/profile",
            }.get(key, "/dashboard")
            today_focus.append({"title": title, "description": desc, "route": route})

    # Fallback generic tasks
    if not today_focus:
        today_focus = [
            {"title": "Complete one AI Interview", "description": "Practice one interview to build confidence.", "route": "/interview"},
            {"title": "Solve two Coding problems", "description": "Sharpen problem solving with targeted practice.", "route": "/coding"},
            {"title": "Take one Aptitude Test", "description": "Improve speed and accuracy with a timed test.", "route": "/aptitude"},
        ]

    # Continue learning cards
    continue_learning = [
        {"name": "Resume Analyzer", "status": "Last analyzed: " + (latest_resume.file_name if latest_resume else "Not analyzed"), "route": "/resume"},
        {"name": "Coding Practice", "status": "Continue solving problems", "route": "/coding"},
        {"name": "AI Interview", "status": "Practice mock interviews", "route": "/interview"},
        {"name": "Aptitude", "status": "Take practice tests", "route": "/aptitude"},
    ]

    # Recent activity: combine resume uploads, coding submissions, interview sessions, aptitude results
    recent_activity = []
    try:
        # resumes
        collection = db["resumes"]
        docs = await collection.find({"user_id": user_id}).sort("uploaded_at", -1).to_list(length=3)
        for d in docs:
            recent_activity.append({
                "type": "resume",
                "title": f"Resume uploaded: {d.get('file_name')}",
                "timestamp": _safe_iso_timestamp(d.get("uploaded_at")),
                "meta": {"resume_id": str(d.get("_id"))},
            })
    except Exception:
        logger.exception("Failed to read resume history for dashboard")

    try:
        collection = db["coding_submissions"]
        docs = await collection.find({"user_id": user_id}).sort("submitted_at", -1).to_list(length=3)
        for d in docs:
            recent_activity.append({
                "type": "coding",
                "title": f"Solved: {d.get('problem_id')}",
                "timestamp": _safe_iso_timestamp(d.get("submitted_at")),
                "meta": {"submission_id": str(d.get("_id"))},
            })
    except Exception:
        logger.exception("Failed to read coding submissions for dashboard")

    try:
        collection = db["interview_sessions"]
        docs = await collection.find({"candidate_id": user_id}).sort("updated_at", -1).to_list(length=3)
        for d in docs:
            recent_activity.append({
                "type": "interview",
                "title": f"Interview session: {d.get('session_id')}",
                "timestamp": _safe_iso_timestamp(d.get("updated_at")),
                "meta": {"session_id": d.get('session_id')},
            })
    except Exception:
        logger.exception("Failed to read interview sessions for dashboard")

    try:
        collection = db["aptitude_results"]
        docs = await collection.find({"user_id": user_id}).sort("submitted_at", -1).to_list(length=3)
        for d in docs:
            recent_activity.append({
                "type": "aptitude",
                "title": f"Aptitude test: {d.get('test_type')}",
                "timestamp": _safe_iso_timestamp(d.get("submitted_at")),
                "meta": {"result_id": d.get('result_id')},
            })
    except Exception:
        logger.exception("Failed to read aptitude results for dashboard")

    # sort recent_activity by timestamp desc and limit 5
    def _ts_key(item: dict[str, Any]):
        return item.get("timestamp") or ""

    recent_activity = sorted(recent_activity, key=_ts_key, reverse=True)[:5]

    # Latest insight
    latest_insight = {"text": None}
    try:
        if insights and isinstance(insights, dict):
            latest_insight["text"] = insights.get("summary", {}).get("overview")
    except Exception:
        logger.exception("Failed to assemble latest insight for dashboard")

    return {
        "user": {
            "user_id": profile.user_id,
            "name": display_name,
        },
        "todayFocus": today_focus,
        "continueLearning": continue_learning,
        "recentActivity": recent_activity,
        "latestInsight": latest_insight,
    }
