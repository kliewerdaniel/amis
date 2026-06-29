import json
import requests
import logging
from typing import Any

logger = logging.getLogger("amis.llm")


class LLMClient:
    def __init__(self, provider: str = "ollama", model: str = "llama3.1:8b",
                 base_url: str = "http://localhost:11434", temperature: float = 0.3,
                 max_tokens: int = 4096):
        self.provider = provider
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.max_tokens = max_tokens

    def complete(self, prompt: str, temperature: float = None, max_tokens: int = None) -> str:
        if self.provider == "ollama":
            return self._ollama_complete(prompt, temperature, max_tokens)
        elif self.provider == "openai":
            return self._openai_complete(prompt, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def complete_json(self, prompt: str, temperature: float = None, max_tokens: int = None) -> dict:
        raw = self.complete(prompt, temperature=temperature, max_tokens=max_tokens)
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()
        return json.loads(cleaned)

    def _ollama_complete(self, prompt: str, temperature: float | None, max_tokens: int | None) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }
        resp = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()["response"]

    def _openai_complete(self, prompt: str, temperature: float | None, max_tokens: int | None) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }
        headers = {"Content-Type": "application/json"}
        resp = requests.post(
            f"{self.base_url}/v1/chat/completions", json=payload, headers=headers, timeout=120
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
