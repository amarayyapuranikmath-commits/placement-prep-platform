from datetime import datetime, timezone
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services import coding_progress_service, coding_service, profile_service, resume_service
from app.services.aptitude_service import AptitudeService
from app.services.interview_service import InterviewService


class ProgressService:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.interview_service = InterviewService(db)
        self.aptitude_service = AptitudeService(db)

    @staticmethod
    def _normalize_percent(value: float | int | None) -> int:
        try:
            numeric = int(round(float(value or 0)))
        except (TypeError, ValueError):
            return 0
        return max(0, min(100, numeric))

    @staticmethod
    def _module_status(score: int) -> str:
        if score >= 70:
            return "Completed"
        if score > 0:
            return "In progress"
        return "Not started"

    @staticmethod
    def _format_relative_time(value: str | datetime | None) -> str:
        if value is None:
            return "Recent"
        if isinstance(value, str):
            try:
                if value.endswith("Z"):
                    value = value.replace("Z", "+00:00")
                value = datetime.fromisoformat(value)
            except ValueError:
                return "Recent"
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        diff = now - value.astimezone(timezone.utc)
        diff_days = round(diff.total_seconds() / (60 * 60 * 24))
        if diff_days <= 0:
            return "Today"
        if diff_days == 1:
            return "Yesterday"
        if diff_days < 7:
            return f"{diff_days} Days Ago"
        return value.strftime("%b %d")

    @staticmethod
    def _parse_datetime(value: str | datetime | None) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        try:
            if value.endswith("Z"):
                value = value.replace("Z", "+00:00")
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    @staticmethod
    def _calculate_average(scores: list[float]) -> int:
        if not scores:
            return 0
        return int(round(sum(scores) / len(scores)))

    def _build_modules(self, profile: Any, interview_history: list[dict[str, Any]], aptitude_history: list[dict[str, Any]], coding_progress: Any, resume_history: Any) -> list[dict[str, Any]]:
        try:
            interview_score = self._calculate_average(
                [float(item.get("score") or item.get("summary", {}).get("score") or 0) for item in (interview_history or [])]
            )
        except (TypeError, ValueError):
            interview_score = 0
        
        try:
            aptitude_score = self._calculate_average(
                [float(item.get("summary", {}).get("score") or 0) for item in (aptitude_history or [])]
            )
        except (TypeError, ValueError):
            aptitude_score = 0
        
        try:
            acceptance_rate = getattr(coding_progress, "acceptance_rate", 0.0) if coding_progress else 0.0
            coding_score = self._normalize_percent((acceptance_rate or 0.0) * 100)
        except (TypeError, ValueError, AttributeError):
            coding_score = 0
        
        try:
            profile_completion = getattr(profile, "completion_percentage", None) if profile else None
            profile_score = self._normalize_percent(profile_completion)
        except (TypeError, ValueError, AttributeError):
            profile_score = 0
        
        try:
            resume_scores = [float(getattr(item, "ats_score", 0) or 0) for item in (resume_history or [])]
            resume_score = self._calculate_average(resume_scores)
        except (TypeError, ValueError, AttributeError):
            resume_scores = []
            resume_score = 0

        latest_resume_score = int(round(resume_scores[0])) if resume_scores else 0
        try:
            coding_solved = getattr(coding_progress, "total_solved", 0) if coding_progress else 0
            coding_solved = coding_solved or 0
        except (TypeError, AttributeError):
            coding_solved = 0
        
        try:
            total_submissions = getattr(coding_progress, "total_submissions", 0) if coding_progress else 0
            total_submissions = total_submissions or 0
        except (TypeError, AttributeError):
            total_submissions = 0
        
        modules = [
            {
                "key": "interview",
                "name": "AI Interview",
                "progress": interview_score,
                "status": self._module_status(interview_score),
                "detail": f"{len(interview_history or [])} Interviews Completed" if (interview_history or []) else "No interviews completed yet",
                "attempts": len(interview_history or []),
            },
            {
                "key": "aptitude",
                "name": "Aptitude",
                "progress": aptitude_score,
                "status": self._module_status(aptitude_score),
                "detail": f"{len(aptitude_history or [])} Tests Attempted" if (aptitude_history or []) else "No tests attempted yet",
                "attempts": len(aptitude_history or []),
            },
            {
                "key": "coding",
                "name": "Coding Practice",
                "progress": coding_score,
                "status": self._module_status(coding_score),
                "detail": f"{coding_solved} Problems Solved" if coding_solved else "No problems solved yet",
                "attempts": total_submissions,
            },
            {
                "key": "resume",
                "name": "Resume Analyzer",
                "progress": resume_score,
                "status": self._module_status(resume_score),
                "detail": f"Latest ATS: {latest_resume_score}%" if (resume_history or []) else "No ATS score yet",
                "attempts": len(resume_history or []),
            },
            {
                "key": "profile",
                "name": "Profile",
                "progress": profile_score,
                "status": self._module_status(profile_score),
                "detail": "Profile completed" if profile_score >= 70 else (f"{profile_score}% complete" if profile_score > 0 else "Profile not started"),
                "attempts": 0,
            },
        ]
        return modules

    def _build_activity(self, profile: Any, interview_history: list[dict[str, Any]], aptitude_history: list[dict[str, Any]], coding_submissions: list[Any], resume_history: Any) -> list[dict[str, Any]]:
        activity: list[dict[str, Any]] = []

        try:
            if interview_history:
                latest = interview_history[0]
                score_value = latest.get("score") or latest.get("summary", {}).get("score") or 0
                activity.append(
                    {
                        "title": "Technical Interview",
                        "description": f"Score: {int(round(float(score_value)))}%",
                        "timestamp": self._format_relative_time(latest.get("submitted_at") or latest.get("date")),
                        "sort_key": self._parse_datetime(latest.get("submitted_at") or latest.get("date")) or datetime.now(timezone.utc),
                    }
                )
        except (TypeError, ValueError, KeyError, IndexError, AttributeError):
            pass

        try:
            if aptitude_history:
                latest = aptitude_history[0]
                activity.append(
                    {
                        "title": "Aptitude Test",
                        "description": f"Score: {int(round(float(latest.get('summary', {}).get('score') or 0)))}%",
                        "timestamp": self._format_relative_time(latest.get("submitted_at") or latest.get("date")),
                        "sort_key": self._parse_datetime(latest.get("submitted_at") or latest.get("date")) or datetime.now(timezone.utc),
                    }
                )
        except (TypeError, ValueError, KeyError, IndexError, AttributeError):
            pass

        if coding_submissions:
            try:
                latest = coding_submissions[0]
                status = getattr(latest, 'status', 'submitted')
                submitted_at = getattr(latest, 'submitted_at', None)
                activity.append(
                    {
                        "title": "Coding Practice",
                        "description": f"Status: {status}",
                        "timestamp": self._format_relative_time(submitted_at),
                        "sort_key": self._parse_datetime(submitted_at) or datetime.now(timezone.utc),
                    }
                )
            except (TypeError, ValueError, IndexError, AttributeError):
                pass

        try:
            if resume_history:
                latest = resume_history[0]
                activity.append(
                    {
                        "title": "Resume Analyzed",
                        "description": f"ATS Score: {int(round(float(getattr(latest, 'ats_score', 0) or 0)))}%",
                        "timestamp": self._format_relative_time(getattr(latest, 'uploaded_at', None)),
                        "sort_key": self._parse_datetime(getattr(latest, 'uploaded_at', None)) or datetime.now(timezone.utc),
                    }
                )
        except (TypeError, ValueError, IndexError, AttributeError):
            pass

        try:
            if getattr(profile, "completion_percentage", None) is not None:
                activity.append(
                    {
                        "title": "Profile Updated",
                        "description": f"{getattr(profile, 'completion_percentage', 0)}% completed",
                        "timestamp": self._format_relative_time(datetime.now(timezone.utc)),
                        "sort_key": datetime.now(timezone.utc),
                    }
                )
        except (TypeError, ValueError, AttributeError):
            pass

        try:
            activity.sort(key=lambda item: item["sort_key"], reverse=True)
        except (TypeError, KeyError):
            pass
        
        return [{"title": item["title"], "description": item["description"], "timestamp": item["timestamp"]} for item in activity[:6]]

    async def get_summary(self, user_id: str) -> dict[str, Any]:
        try:
            profile = await profile_service.get_profile(self.db, user_id)
        except Exception:
            profile = None
        
        try:
            interview_history = await self.interview_service.get_history(user_id)
        except Exception:
            interview_history = []
        
        try:
            aptitude_history = await self.aptitude_service.get_history(user_id)
        except Exception:
            aptitude_history = []
        
        try:
            coding_progress = await coding_progress_service.get_progress(self.db, user_id)
        except Exception:
            coding_progress = None
        
        try:
            resume_history_response = await resume_service.get_resume_history(self.db, user_id)
            resume_history = resume_history_response.resumes if resume_history_response else []
        except Exception:
            resume_history = []
        
        try:
            submission_response = await coding_service.get_submission_history(self.db, user_id)
            coding_submissions = submission_response.submissions if submission_response else []
        except Exception:
            coding_submissions = []

        modules = self._build_modules(profile, interview_history, aptitude_history, coding_progress, resume_history)
        overall_percentage = self._calculate_average([module["progress"] for module in modules])
        overview = {
            "percentage": overall_percentage,
            "message": (
                "Excellent progress — you are placement ready!"
                if overall_percentage >= 85
                else "You're making strong progress. Keep going!"
                if overall_percentage >= 50
                else "Keep building momentum with a few more module wins."
                if overall_percentage > 0
                else "Start your placement preparation by completing your first module."
            ),
        }

        return {
            "overview": overview,
            "modules": modules,
            "activity": self._build_activity(profile, interview_history, aptitude_history, coding_submissions, resume_history),
        }

    async def get_analytics(self, user_id: str, module_key: str) -> list[dict[str, Any]]:
        try:
            module_key = (module_key or "interview").lower()
            points = []
            
            if module_key == "aptitude":
                try:
                    history = await self.aptitude_service.get_history(user_id)
                    if history:
                        points = [
                            {
                                "label": item.get("submitted_at") or item.get("date") or "Recent",
                                "value": int(round(float(item.get("summary", {}).get("score") or 0))),
                            }
                            for item in (history or [])[:8]
                        ]
                except (TypeError, ValueError, KeyError, AttributeError):
                    points = []
            
            elif module_key == "coding":
                try:
                    submission_response = await coding_service.get_submission_history(self.db, user_id)
                    submissions = submission_response.submissions if submission_response else []
                    points = [
                        {
                            "label": getattr(item, "submitted_at", "Recent") or "Recent",
                            "value": 100 if getattr(item, "status", None) == "accepted" else 60,
                        }
                        for item in (submissions or [])[:8]
                    ]
                except (TypeError, ValueError, AttributeError):
                    points = []
            
            elif module_key == "resume":
                try:
                    history = await resume_service.get_resume_history(self.db, user_id)
                    resumes = history.resumes if history else []
                    points = [
                        {
                            "label": getattr(item, "uploaded_at", None) or "Recent",
                            "value": int(round(float(getattr(item, "ats_score", 0) or 0))),
                        }
                        for item in (resumes or [])[:8]
                    ]
                except (TypeError, ValueError, AttributeError):
                    points = []
            
            else:
                try:
                    history = await self.interview_service.get_history(user_id)
                    if history:
                        points = [
                            {
                                "label": item.get("submitted_at") or item.get("date") or "Recent",
                                "value": int(round(float(item.get("score") or item.get("summary", {}).get("score") or 0))),
                            }
                            for item in (history or [])[:8]
                        ]
                except (TypeError, ValueError, KeyError, AttributeError):
                    points = []
            
            return list(reversed(points)) if points else []
        except Exception:
            return []

    async def generate_report(self, user_id: str) -> bytes:
        summary = await self.get_summary(user_id)
        from app.services.pdf_service import generate_progress_report_pdf

        return generate_progress_report_pdf(summary)
