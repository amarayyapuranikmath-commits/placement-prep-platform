import logging
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import get_settings
from app.models.resume import RESUMES_COLLECTION
from app.schemas.resume import (
    KeywordAnalysisResponse,
    ResumeAnalysisResponse,
    ResumeHistoryResponse,
    ResumeSummaryResponse,
    ScoreBreakdownResponse,
    SectionScoresResponse,
)
from app.services import profile_service
from app.utils.file_storage import delete_resume_file, save_resume_file
from app.utils.groq_client import analyze_resume_with_groq
from app.utils.pdf_extractor import extract_text_from_pdf

logger = logging.getLogger(__name__)
settings = get_settings()

ALLOWED_CONTENT_TYPE = "application/pdf"


def _max_file_size_bytes() -> int:
    return settings.MAX_RESUME_SIZE_MB * 1024 * 1024


def _to_analysis_response(document: dict) -> ResumeAnalysisResponse:
    return ResumeAnalysisResponse(
        id=str(document["_id"]),
        file_name=document["file_name"],
        file_size_bytes=document["file_size_bytes"],
        version=document["version"],
        is_current=document["is_current"],
        ats_score=document.get("ats_score"),
        quality_label=document.get("quality_label"),
        score_breakdown=ScoreBreakdownResponse(**document.get("score_breakdown", {})),
        strengths=document.get("strengths", []),
        weaknesses=document.get("weaknesses", []),
        missing_skills=document.get("missing_skills", []),
        suggestions=document.get("suggestions", []),
        role_match=document.get("role_match"),
        keyword_match=document.get("keyword_match"),
        section_scores=SectionScoresResponse(**document.get("section_scores", {})),
        keywords=KeywordAnalysisResponse(**document.get("keywords", {})),
        is_resume=document.get("is_resume"),
        reason=document.get("reason"),
        analysis_status=document.get("analysis_status", "pending"),
        uploaded_at=document["uploaded_at"],
    )


def _to_summary_response(document: dict) -> ResumeSummaryResponse:
    return ResumeSummaryResponse(
        id=str(document["_id"]),
        file_name=document["file_name"],
        version=document["version"],
        is_current=document["is_current"],
        ats_score=document.get("ats_score"),
        quality_label=document.get("quality_label"),
        analysis_status=document.get("analysis_status", "pending"),
        uploaded_at=document["uploaded_at"],
    )


def _score_from_quality_label(quality_label: str | None) -> int:
    if quality_label == "Excellent":
        return 92
    if quality_label == "Good":
        return 78
    if quality_label == "Average":
        return 68
    if quality_label == "Poor":
        return 52
    return 70


async def upload_and_analyze_resume(
    db: AsyncIOMotorDatabase, user_id: str, file: UploadFile
) -> ResumeAnalysisResponse:
    if file.content_type != ALLOWED_CONTENT_TYPE:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are supported",
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty"
        )
    if len(file_bytes) > _max_file_size_bytes():
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {settings.MAX_RESUME_SIZE_MB}MB size limit",
        )

    extracted_text = extract_text_from_pdf(file_bytes)
    if not extracted_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract any text from this PDF. Please upload a text-based resume.",
        )

    profile = await profile_service.get_profile(db, user_id)
    analysis = await analyze_resume_with_groq(extracted_text, profile.target_role)

    if not analysis.get("is_resume", False):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="This document does not appear to be a resume.",
        )

    score = int(analysis.get("ats_score") or _score_from_quality_label(analysis.get("quality_label")))
    analysis["ats_score"] = max(40, min(95, score))

    collection = db[RESUMES_COLLECTION]
    previous_count = await collection.count_documents({"user_id": user_id})
    next_version = previous_count + 1

    storage_path = save_resume_file(user_id, file.filename, file_bytes)

    now = datetime.now(timezone.utc)
    resume_doc = {
        "user_id": user_id,
        "file_name": file.filename,
        "file_size_bytes": len(file_bytes),
        "storage_path": storage_path,
        "version": next_version,
        "is_current": True,
        "extracted_text": extracted_text,
        "ats_score": analysis.get("ats_score"),
        "quality_label": analysis.get("quality_label"),
        "score_breakdown": analysis.get("score_breakdown", {}),
        "strengths": analysis.get("strengths", []),
        "weaknesses": analysis.get("weaknesses", []),
        "missing_skills": analysis.get("missing_skills", []),
        "suggestions": analysis.get("suggestions", []),
        "role_match": analysis.get("role_match"),
        "keyword_match": analysis.get("keyword_match"),
        "section_scores": analysis.get("section_scores", {}),
        "keywords": analysis.get("keywords", {}),
        "is_resume": analysis.get("is_resume"),
        "reason": analysis.get("reason"),
        "analysis_status": "completed",
        "uploaded_at": now,
    }

    await collection.update_many(
        {"user_id": user_id, "is_current": True}, {"$set": {"is_current": False}}
    )

    result = await collection.insert_one(resume_doc)
    resume_doc["_id"] = result.inserted_id

    await profile_service.set_resume_id(db, user_id, str(resume_doc["_id"]))

    logger.info("Resume uploaded and analyzed for user: %s (version %s)", user_id, next_version)

    return _to_analysis_response(resume_doc)


async def get_resume_history(db: AsyncIOMotorDatabase, user_id: str) -> ResumeHistoryResponse:
    collection = db[RESUMES_COLLECTION]
    cursor = collection.find({"user_id": user_id}).sort("uploaded_at", -1)
    documents = await cursor.to_list(length=100)
    return ResumeHistoryResponse(resumes=[_to_summary_response(doc) for doc in documents])


async def get_resume_analysis(
    db: AsyncIOMotorDatabase, user_id: str, resume_id: str
) -> ResumeAnalysisResponse:
    if not ObjectId.is_valid(resume_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid resume identity"
        )

    collection = db[RESUMES_COLLECTION]
    document = await collection.find_one({"_id": ObjectId(resume_id), "user_id": user_id})

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    return _to_analysis_response(document)


async def reanalyze_resume(
    db: AsyncIOMotorDatabase, user_id: str, resume_id: str
) -> ResumeAnalysisResponse:
    if not ObjectId.is_valid(resume_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid resume identity"
        )

    collection = db[RESUMES_COLLECTION]
    document = await collection.find_one({"_id": ObjectId(resume_id), "user_id": user_id})

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    profile = await profile_service.get_profile(db, user_id)
    analysis = await analyze_resume_with_groq(document["extracted_text"], profile.target_role)

    if not analysis.get("is_resume", False):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="This document does not appear to be a resume.",
        )

    score = int(analysis.get("ats_score") or _score_from_quality_label(analysis.get("quality_label")))
    analysis["ats_score"] = max(40, min(95, score))

    update_fields = {
        "ats_score": analysis.get("ats_score"),
        "quality_label": analysis.get("quality_label"),
        "score_breakdown": analysis.get("score_breakdown", {}),
        "strengths": analysis.get("strengths", []),
        "weaknesses": analysis.get("weaknesses", []),
        "missing_skills": analysis.get("missing_skills", []),
        "suggestions": analysis.get("suggestions", []),
        "role_match": analysis.get("role_match"),
        "keyword_match": analysis.get("keyword_match"),
        "section_scores": analysis.get("section_scores", {}),
        "keywords": analysis.get("keywords", {}),
        "is_resume": analysis.get("is_resume"),
        "reason": analysis.get("reason"),
        "analysis_status": "completed",
    }

    await collection.update_one({"_id": ObjectId(resume_id)}, {"$set": update_fields})
    document.update(update_fields)

    logger.info("Resume re-analyzed for user: %s (resume_id=%s)", user_id, resume_id)

    return _to_analysis_response(document)


async def delete_resume(db: AsyncIOMotorDatabase, user_id: str, resume_id: str) -> None:
    if not ObjectId.is_valid(resume_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid resume identity"
        )

    collection = db[RESUMES_COLLECTION]
    document = await collection.find_one({"_id": ObjectId(resume_id), "user_id": user_id})

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    delete_resume_file(document["storage_path"])
    await collection.delete_one({"_id": ObjectId(resume_id)})

    if document.get("is_current"):
        latest = await collection.find_one({"user_id": user_id}, sort=[("uploaded_at", -1)])
        if latest:
            await collection.update_one(
                {"_id": latest["_id"]}, {"$set": {"is_current": True}}
            )
            await profile_service.set_resume_id(db, user_id, str(latest["_id"]))
        else:
            await profile_service.set_resume_id(db, user_id, None)

    logger.info("Resume deleted for user: %s (resume_id=%s)", user_id, resume_id)