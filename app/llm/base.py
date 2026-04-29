from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class LLMRequest:
    system_prompt: str
    payload: dict[str, Any]


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_json(self, request: LLMRequest) -> dict[str, Any]:
        raise NotImplementedError
