import os
import requests


class OpenRouterClient:
    def __init__(self, model="openai/gpt-5-chat", api_key=None, url="https://openrouter.ai/api/v1/chat/completions"):
        self.model = model
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.url = url

    def chat(self, system: str, user: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.7,
            "max_tokens": 800
        }
        r = requests.post(self.url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
