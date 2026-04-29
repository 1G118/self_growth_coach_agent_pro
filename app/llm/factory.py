from app.core.config import settings
from app.llm.base import BaseLLMProvider
from app.llm.providers import (
    AnthropicProvider,
    GeminiProvider,
    OpenAICompatibleProvider,
    OpenAIResponsesProvider,
)


def get_llm_provider() -> BaseLLMProvider:
    provider = settings.llm_provider.strip().lower()

    if provider == "openai":
        return OpenAIResponsesProvider()
    if provider in {"openai_compatible", "openai-compatible"}:
        return OpenAICompatibleProvider()
    if provider == "anthropic":
        return AnthropicProvider()
    if provider == "gemini":
        return GeminiProvider()

    supported = ["openai", "openai_compatible", "anthropic", "gemini"]
    raise ValueError(
        f"Unsupported LLM_PROVIDER={settings.llm_provider!r}. "
        f"Supported values: {', '.join(supported)}"
    )
