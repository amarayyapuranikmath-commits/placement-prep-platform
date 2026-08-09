import asyncio
import logging

import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

DEFAULT_JUDGE0_URL = "https://ce.judge0.com"


async def execute_code(language: str, code: str, stdin: str) -> dict:
    base_url = (settings.JUDGE0_API_URL or DEFAULT_JUDGE0_URL).rstrip('/')

    payload = {
        "source_code": code,
        "language_id": _language_to_id(language),
        "stdin": stdin,
    }

    headers = {"content-type": "application/json"}
    if settings.JUDGE0_API_KEY:
        headers["x-rapidapi-key"] = settings.JUDGE0_API_KEY
        headers["x-rapidapi-host"] = "judge0-ce.p.rapidapi.com"

    logger.debug('Judge0 request payload: %s', payload)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            submit_response = await client.post(
                f"{base_url}/submissions?base64_encoded=false",
                json=payload,
                headers=headers,
            )
            submit_response.raise_for_status()
            token = submit_response.json().get("token")
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Judge0 execution service returned no submission token",
                )

            status_response = await client.get(f"{base_url}/submissions/{token}?base64_encoded=false")
            status_response.raise_for_status()
            data = status_response.json()

            attempts = 0
            while data.get("status", {}).get("id") in {1, 2}:
                attempts += 1
                if attempts > 30:
                    break
                await asyncio.sleep(0.25)
                status_response = await client.get(f"{base_url}/submissions/{token}?base64_encoded=false")
                status_response.raise_for_status()
                data = status_response.json()

            logger.debug('Judge0 response data: %s', data)
    except httpx.HTTPError as exc:
        logger.exception("Judge0 execution request failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Judge0 execution service is currently unavailable",
        ) from exc

    raw_time = data.get("time")
    time_ms = float(raw_time) * 1000 if raw_time is not None else None

    raw_memory = data.get("memory")
    memory_kb = float(raw_memory) if raw_memory is not None else None

    return {
        "status_id": data.get("status", {}).get("id"),
        "stdout": data.get("stdout"),
        "stderr": data.get("stderr"),
        "compile_output": data.get("compile_output"),
        "time_ms": time_ms,
        "memory_kb": memory_kb,
    }


def _language_to_id(language: str) -> int:
    mapping = {
        "python": 71,
        "java": 62,
        "cpp": 54,
        "javascript": 63,
    }
    return mapping.get(language, 71)

