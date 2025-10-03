from __future__ import annotations

import os
from typing import Any, Dict

import requests


class OpenRouterClient:
    def __init__(self, model: str = "openai/gpt-5-chat", api_key: str | None = None, url: str = "https://openrouter.ai/api/v1/chat/completions") -> None:
        self.model = model
        self.api_key = (api_key or os.getenv("OPENROUTER_API_KEY", "")).strip()
        self.url = url

    def chat(self, system: str, user: str) -> str:
        if not self.api_key:
            raise ValueError("OpenRouter API key is missing. Set OPENROUTER_API_KEY to enable analysis.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.7,
            "max_tokens": 800,
        }

        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"OpenRouter request failed: {exc}") from exc

        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("OpenRouter response is missing message content") from exc

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("OpenRouter returned empty analysis text")

        return content.strip()
