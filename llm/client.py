from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LLMResponse:
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cached: bool


class LLMClient(Protocol):
    def generate(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 256,
        system: str | None = None,
    ) -> LLMResponse:
        """Generate a response given a prompt and configuration parameters."""
        ...


class MockLLMClient:
    """Deterministic mock LLM client without network access."""

    def __init__(self, response_prefix: str = "Mock response to: ") -> None:
        self.response_prefix = response_prefix
        self.call_count: int = 0

    def generate(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 256,
        system: str | None = None,
    ) -> LLMResponse:
        self.call_count += 1
        start_time = time.perf_counter()

        # Deterministic canned response derived from sha256 of the prompt
        prompt_digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:8]
        response_text = f"{self.response_prefix}{prompt} [{prompt_digest}]"

        # Mock token accounting
        input_tokens = len(prompt.split()) + (len(system.split()) if system else 0)
        output_tokens = min(len(response_text.split()), max_tokens)

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return LLMResponse(
            text=response_text,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=round(latency_ms, 3),
            cached=False,
        )


class CachingLLMClient:
    """Wrapper that caches LLM responses on disk keyed by SHA-256 of call parameters."""

    def __init__(self, wrapped_client: LLMClient, cache_dir: str = "llm_cache") -> None:
        self.wrapped = wrapped_client
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def _compute_key(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        system: str | None,
    ) -> str:
        payload = {
            "model": model,
            "system": system or "",
            "prompt": prompt,
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
        }
        raw_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw_bytes).hexdigest()

    def generate(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 256,
        system: str | None = None,
    ) -> LLMResponse:
        cache_key = self._compute_key(prompt, model, temperature, max_tokens, system)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return LLMResponse(
                text=data["text"],
                model=data["model"],
                input_tokens=data["input_tokens"],
                output_tokens=data["output_tokens"],
                latency_ms=data.get("latency_ms", 0.0),
                cached=True,
            )

        resp = self.wrapped.generate(
            prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system=system,
        )

        cache_data = {
            "text": resp.text,
            "model": resp.model,
            "input_tokens": resp.input_tokens,
            "output_tokens": resp.output_tokens,
            "latency_ms": resp.latency_ms,
        }
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2)

        return resp
