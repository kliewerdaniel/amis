import json
import re
import requests
import logging
from typing import Any

logger = logging.getLogger("amis.llm")


class LLMClient:
    def __init__(self, provider: str = "ollama", model: str = "llama3.1:8b",
                 base_url: str = "http://localhost:11434", temperature: float = 0.1,
                 max_tokens: int = 8192):
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
        return self._extract_json(raw)

    def _extract_json(self, text: str) -> dict:
        text = text.strip()

        if text.startswith("```"):
            lines = text.split("\n", 1)
            if len(lines) > 1:
                text = lines[1]
            text = text.rsplit("```", 1)[0].strip()

        brace_start = text.find("{")
        brace_end = text.rfind("}")
        if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
            text = text[brace_start:brace_end + 1]

        text = re.sub(r",\s*}", "}", text)
        text = re.sub(r",\s*\]", "]", text)

        return json.loads(text)

    def _ollama_complete(self, prompt: str, temperature: float | None, max_tokens: int | None) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }
        resp = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=300)
        resp.raise_for_status()
        return resp.json()["response"]

    def _openai_complete(self, prompt: str, temperature: float | None, max_tokens: int | None) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }
        headers = {"Content-Type": "application/json"}
        resp = requests.post(
            f"{self.base_url}/v1/chat/completions", json=payload, headers=headers, timeout=300
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
