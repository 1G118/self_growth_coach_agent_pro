from typing import Any

from fastapi import HTTPException

from app.llm import get_llm_provider
from app.llm.base import LLMRequest


def call_llm_json(system_prompt: str, payload: dict[str, Any]) -> dict[str, Any]:
    try:
        provider = get_llm_provider()
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return provider.generate_json(LLMRequest(system_prompt=system_prompt, payload=payload))
