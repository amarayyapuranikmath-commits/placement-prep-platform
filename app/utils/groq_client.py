import json
import logging

import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

_SYSTEM_PROMPT = (
    "You are an experienced software engineer and technical interviewer. "
    "Analyze the submitted code using the problem statement, constraints, runtime, memory, and execution result. "
    "Return ONLY valid JSON matching this schema: "
    '{"correctness": <string>, "algorithm_used": <string>, "explanation": <string>, '
    '"time_complexity": <string>, "space_complexity": <string>, "code_quality": <string>, '
    '"optimization_suggestions": [<string>, ...], "edge_cases_missed": [<string>, ...], '
    '"relevant_edge_cases": [<string>, ...], "interview_tips": [<string>, ...], '
    '"overall_rating": <string>}'
)

_RESUME_SYSTEM_PROMPT = (
    "You are an expert ATS and hiring analyst. Analyze whether the uploaded document is a resume, "
    "and if it is, evaluate the resume quality with evidence from the text. Return ONLY valid JSON, no markdown, "
    "no prose, matching exactly this schema: "
    '{"is_resume": <boolean>, "reason": <string>, "ats_score": <int 0-100>, "quality_label": <string>, '
    '"score_breakdown": {"keywords": <int 0-100>, "formatting": <int 0-100>, "skills": <int 0-100>, '
    '"projects": <int 0-100>, "experience": <int 0-100>, "education": <int 0-100>}, '
    '"strengths": [<string>, ...], "weaknesses": [<string>, ...], "missing_skills": [<string>, ...], '
    '"suggestions": [<string>, ...], "role_match": <int 0-100>, "keyword_match": <int 0-100>, '
    '"section_scores": {"personal_information": <int 0-100>, "education": <int 0-100>, "experience": <int 0-100>, '
    '"projects": <int 0-100>, "skills": <int 0-100>, "certifications": <int 0-100>, "achievements": <int 0-100>, '
    '"formatting": <int 0-100>, "ats_compatibility": <int 0-100>, "structure": <int 0-100>, '
    '"grammar": <int 0-100>, "readability": <int 0-100>, "technical_depth": <int 0-100>}, '
    '"keywords": {"strong": [<string>, ...], "weak": [<string>, ...], "missing": [<string>, ...]}}'
)


async def analyze_resume_with_groq(resume_text: str, target_role: str | None) -> dict:
    if not settings.GROQ_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Resume analysis is temporarily unavailable. Please try again later.",
        )

    role_context = f"The candidate's target role is: {target_role}. " if target_role else ""
    user_prompt = (
        f"{role_context}"
        "You must determine if this document is actually a resume. "
        "Use the presence of sections such as name, email, phone, education, experience, skills, projects, certifications, and achievements. "
        "If it is not a resume, return is_resume=false and a concise reason. "
        "If it is a resume, analyze the content carefully and provide evidence-based feedback.\n\n"
        f"Resume text:\n\n{resume_text[:16000]}"
    )

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": _RESUME_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
    }
    headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(GROQ_CHAT_COMPLETIONS_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        logger.exception("Groq API request failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resume analysis service is currently unavailable",
        ) from exc

    try:
        content = data["choices"][0]["message"]["content"]
        analysis = json.loads(content)
    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        logger.exception("Failed to parse Groq analysis response")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Received an invalid response from the resume analysis service",
        ) from exc

    return analysis


async def generate_coding_problem(category: str, difficulty: str) -> dict:
    if not settings.GROQ_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Coding problem generation is temporarily unavailable.",
        )

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Generate a coding interview problem as valid JSON with fields: "
                    "title, statement, input_format, output_format, constraints, examples, "
                    "visible_test_cases, hidden_test_cases, starter_code, tags, time_limit_ms, "
                    "memory_limit_mb"
                ),
            },
            {
                "role": "user",
                "content": f"Create a {difficulty} {category} coding problem in JSON format.",
            },
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
    }
    headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(GROQ_CHAT_COMPLETIONS_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        logger.exception("Groq coding problem request failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Coding problem generation service is currently unavailable",
        ) from exc

    try:
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        logger.exception("Failed to parse Groq coding problem response")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Received an invalid response from the coding problem service",
        ) from exc


async def analyze_submission_with_groq(problem_statement: str, code: str, language: str, passed: bool) -> dict:
    if not settings.GROQ_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI feedback is temporarily unavailable.",
        )

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Problem statement:\n{problem_statement}\n\n"
                    f"Language: {language}\n\n"
                    f"Submission passed hidden tests: {passed}\n\n"
                    "Use the problem statement, constraints, and the submitted code to produce a detailed review. "
                    "Do not use a generic template. Mention the actual algorithm, why the code works or fails, and discuss only meaningful optimizations.\n\n"
                    f"Code:\n{code[:12000]}"
                ),
            },
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(GROQ_CHAT_COMPLETIONS_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        logger.exception("Groq submission analysis request failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI feedback service is currently unavailable",
        ) from exc

    try:
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        logger.exception("Failed to parse Groq submission analysis response")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Received an invalid response from the AI feedback service",
        ) from exc