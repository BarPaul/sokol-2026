"""AI provider abstraction. OpenAI-compatible interface to allow replacing the provider."""

import os
from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    @abstractmethod
    def generate(self, messages: list[dict[str, Any]], **options: Any) -> str:
        """Send messages and return the assistant text reply."""


class OpenCodeProvider(AIProvider):
    """OpenAI-compatible provider pointing at OpenCode API."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ):
        from openai import OpenAI

        self.api_key = api_key or os.getenv("OPENCODE_API_KEY", "")
        self.base_url = base_url or os.getenv("OPENCODE_BASE_URL", "")
        self.model = model or os.getenv("OPENCODE_MODEL", "Deepseek-v4-flash")

        kw: dict[str, Any] = {"api_key": self.api_key}
        if self.base_url:
            kw["base_url"] = self.base_url
        self.client = OpenAI(**kw)

    def generate(self, messages: list[dict[str, Any]], **options: Any) -> str:
        response = self.client.chat.completions.create(
            model=options.get("model", self.model),
            messages=messages,
            temperature=options.get("temperature"),
            max_tokens=options.get("max_tokens"),
        )
        return response.choices[0].message.content or ""


def get_provider(**options: Any) -> AIProvider:
    return OpenCodeProvider(**options)