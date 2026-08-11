"""AI provider abstraction. Native HTTP client for the local opencode server."""

import json
import urllib.request
from abc import ABC, abstractmethod
from typing import Any

from app.core.config import settings


class AIProvider(ABC):
    @abstractmethod
    def generate(self, messages: list[dict[str, Any]], **options: Any) -> str:
        """Send messages and return the assistant text reply."""


def _default_model() -> str:
    return settings.opencode_model


class OpenCodeProvider(AIProvider):
    """Provider that talks to the opencode server HTTP API (opencode serve)."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ):
        self.api_key = api_key or settings.opencode_api_key
        self.base_url = (base_url or settings.opencode_base_url).rstrip("/")
        self.model = model or _default_model()

    def _resolve_model(self, model: str) -> dict[str, str]:
        provider = "opencode"
        model_id = model.strip()
        if "/" in model_id:
            provider, model_id = model_id.split("/", 1)
        return {"providerID": provider, "modelID": model_id}

    def _post(self, path: str, body: dict[str, Any], timeout: int = 180) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        data = json.dumps(body).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def generate(self, messages: list[dict[str, Any]], **options: Any) -> str:
        model = options.get("model") or self.model
        system_texts = [m["content"] for m in messages if m.get("role") == "system"]
        system = "\n\n".join(system_texts) or ""

        user_text = ""
        for m in messages:
            if m.get("role") in ("user", "assistant"):
                user_text = f"{user_text}\n{m['content']}".strip()
        user_text = user_text.strip()

        session = self._post("/session", {}, timeout=60)
        session_id = session["id"]
        body: dict[str, Any] = {
            "model": self._resolve_model(model),
            "tools": {},
            "parts": [{"type": "text", "text": user_text}],
        }
        if system:
            body["system"] = system

        response = self._post(f"/session/{session_id}/message", body)
        parts = response.get("parts", [])
        texts = [p.get("text", "") for p in parts if p.get("type") == "text" and p.get("text")]
        return "\n".join(texts).strip() or ""


def get_provider(**options: Any) -> AIProvider:
    return OpenCodeProvider(**options)
