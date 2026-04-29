import json
from typing import Any

import httpx
from fastapi import HTTPException
from openai import OpenAI, OpenAIError

from app.core.config import settings
from app.llm.base import BaseLLMProvider, LLMRequest


def _require_api_key() -> str:
    api_key = settings.llm_api_key.strip()
    if api_key:
        return api_key

    raise HTTPException(
        status_code=500,
        detail="LLM_API_KEY is missing. Please set it in .env",
    )


def _parse_json_text(raw_text: str) -> dict[str, Any]:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as exc:
        extracted = _extract_json_object(raw_text)
        if extracted is not None:
            try:
                return json.loads(extracted)
            except json.JSONDecodeError:
                pass

        raise HTTPException(
            status_code=500,
            detail=f"LLM did not return valid JSON: {exc}; raw={raw_text}",
        ) from exc


def _build_user_input(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _extract_json_object(raw_text: str) -> str | None:
    text = raw_text.strip()

    fenced_start = text.find("```json")
    if fenced_start != -1:
        fenced_start += len("```json")
        fenced_end = text.find("```", fenced_start)
        if fenced_end != -1:
            candidate = text[fenced_start:fenced_end].strip()
            if candidate.startswith("{") and candidate.endswith("}"):
                return candidate

    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape = False

    for index in range(start, len(text)):
        char = text[index]

        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
            continue

        if char == "{":
            depth += 1
            continue

        if char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    return None


def _extract_text_from_response(response: Any) -> str:
    if isinstance(response, str):
        return response

    if isinstance(response, dict):
        if isinstance(response.get("output_text"), str):
            return response["output_text"]

        choices = response.get("choices")
        if isinstance(choices, list) and choices:
            message = choices[0].get("message", {})
            content = message.get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                text_parts: list[str] = []
                for item in content:
                    if isinstance(item, dict) and isinstance(item.get("text"), str):
                        text_parts.append(item["text"])
                if text_parts:
                    return "".join(text_parts)

        content = response.get("content")
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text" and isinstance(item.get("text"), str):
                    text_parts.append(item["text"])
            if text_parts:
                return "".join(text_parts)

    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str):
        return output_text

    content = getattr(response, "content", None)
    if isinstance(content, list):
        text_parts = []
        for item in content:
            item_text = getattr(item, "text", None)
            item_type = getattr(item, "type", None)
            if item_type == "text" and isinstance(item_text, str):
                text_parts.append(item_text)
        if text_parts:
            return "".join(text_parts)

    choices = getattr(response, "choices", None)
    if isinstance(choices, list) and choices:
        message = getattr(choices[0], "message", None)
        content = getattr(message, "content", None)
        if isinstance(content, str):
            return content

    raise HTTPException(
        status_code=500,
        detail=f"Unsupported LLM response type: {type(response).__name__}",
    )


def _request_json(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, str] | None = None,
    json_body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    try:
        response = httpx.request(
            method,
            url,
            headers=headers,
            params=params,
            json=json_body,
            timeout=settings.llm_timeout_seconds,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM provider request failed: {exc}",
        ) from exc


def _normalize_openai_compatible_base_url(base_url: str) -> list[str]:
    normalized = base_url.rstrip("/")
    candidates = [normalized]

    if not normalized.endswith("/v1"):
        candidates.insert(0, f"{normalized}/v1")

    deduped: list[str] = []
    for candidate in candidates:
        if candidate not in deduped:
            deduped.append(candidate)
    return deduped


class OpenAIResponsesProvider(BaseLLMProvider):
    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=_require_api_key(),
            base_url=settings.llm_base_url or None,
            timeout=settings.llm_timeout_seconds,
        )

    def generate_json(self, request: LLMRequest) -> dict[str, Any]:
        try:
            response = self.client.responses.create(
                model=settings.llm_model,
                instructions=request.system_prompt,
                input=_build_user_input(request.payload),
                text={"format": {"type": "json_object"}},
            )
        except OpenAIError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"LLM provider request failed: {exc}",
            ) from exc
        return _parse_json_text(_extract_text_from_response(response))


class OpenAICompatibleProvider(BaseLLMProvider):
    def __init__(self) -> None:
        self.api_key = _require_api_key()
        self.base_url = (settings.llm_base_url or "").rstrip("/")
        if not self.base_url:
            raise HTTPException(
                status_code=500,
                detail="LLM_BASE_URL is required for openai_compatible provider",
            )

    def generate_json(self, request: LLMRequest) -> dict[str, Any]:
        payload = {
            "model": settings.llm_model,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": _build_user_input(request.payload)},
            ],
            "response_format": {"type": "json_object"},
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        errors: list[str] = []
        for candidate_base_url in _normalize_openai_compatible_base_url(self.base_url):
            endpoint = f"{candidate_base_url}/chat/completions"
            try:
                data = _request_json(
                    "POST",
                    endpoint,
                    headers=headers,
                    json_body=payload,
                )
                raw_text = _extract_text_from_response(data)
                return _parse_json_text(raw_text)
            except HTTPException as exc:
                errors.append(f"{endpoint} -> {exc.detail}")

        raise HTTPException(
            status_code=502,
            detail="LLM provider request failed. Tried endpoints: " + " | ".join(errors),
        )


class AnthropicProvider(BaseLLMProvider):
    def __init__(self) -> None:
        self.api_key = _require_api_key()
        self.base_url = (settings.llm_base_url or "https://api.anthropic.com").rstrip("/")

    def generate_json(self, request: LLMRequest) -> dict[str, Any]:
        payload = {
            "model": settings.llm_model,
            "system": request.system_prompt,
            "messages": [
                {"role": "user", "content": _build_user_input(request.payload)},
            ],
            "max_tokens": settings.llm_max_tokens,
        }

        data = _request_json(
            "POST",
            f"{self.base_url}/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": settings.llm_api_version,
                "content-type": "application/json",
            },
            json_body=payload,
        )
        raw_text = "".join(
            block.get("text", "")
            for block in data.get("content", [])
            if block.get("type") == "text"
        )
        return _parse_json_text(raw_text)


class GeminiProvider(BaseLLMProvider):
    def __init__(self) -> None:
        self.api_key = _require_api_key()
        self.base_url = (settings.llm_base_url or "https://generativelanguage.googleapis.com").rstrip("/")

    def generate_json(self, request: LLMRequest) -> dict[str, Any]:
        payload = {
            "systemInstruction": {
                "parts": [{"text": request.system_prompt}],
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": _build_user_input(request.payload)}],
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
            },
        }

        data = _request_json(
            "POST",
            f"{self.base_url}/v1beta/models/{settings.llm_model}:generateContent",
            params={"key": self.api_key},
            json_body=payload,
        )
        parts = data["candidates"][0]["content"]["parts"]
        raw_text = "".join(part.get("text", "") for part in parts)
        return _parse_json_text(raw_text)
