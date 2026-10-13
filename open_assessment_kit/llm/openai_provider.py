from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI


class OpenAIProvider:
    """Default LLM provider using OpenAI Chat Completions + JSON mode."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.4,
    ) -> None:
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY is required for OpenAIProvider.")
        self.model = model
        self.temperature = temperature
        self._client = OpenAI(api_key=key)

    def complete_json(self, system: str, user: str) -> dict[str, Any]:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=self.temperature,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("Model did not return a JSON object.")
        return data
