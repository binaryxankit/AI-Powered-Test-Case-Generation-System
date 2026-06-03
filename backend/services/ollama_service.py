"""LLM service that calls a local Ollama instance for test case generation."""
from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, Dict

import requests

from backend.config import get_settings
from backend.schemas.test_case import TestCase
from backend.services.exceptions import LlmServiceError
from backend.services.gemini_service import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class OllamaServiceError(LlmServiceError):
    """Raised when the Ollama service cannot produce a valid response."""


class OllamaService:
    """Encapsulates all interaction with a local Ollama instance."""

    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        settings = get_settings()
        self._base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self._model_name = model or settings.ollama_model
        self._chat_endpoint = f"{self._base_url}/api/chat"

    @property
    def model_name(self) -> str:
        """Return the configured Ollama model name."""
        return self._model_name

    @property
    def base_url(self) -> str:
        """Return the Ollama server base URL."""
        return self._base_url

    def generate_test_cases(self, requirement: str) -> Dict[str, Any]:
        """Generate structured test cases for the given requirement.

        Returns a dictionary that conforms to the ``TestGenerationResponse``
        schema's ``test_cases`` shape, ready to be persisted.
        """
        user_prompt = (
            f"Requirement:\n\"\"\"\n{requirement.strip()}\n\"\"\"\n\n"
            "Return ONLY the JSON object as specified."
        )

        raw_text = self._call_with_retry(user_prompt)
        payload = self._parse_json(raw_text)
        return self._validate_payload(payload, requirement)

    def _call_with_retry(self, user_prompt: str) -> str:
        """Call Ollama with exponential backoff for transient errors."""
        max_attempts = 3
        backoff = 1.0
        last_exc: Exception | None = None

        for attempt in range(1, max_attempts + 1):
            try:
                response = requests.post(
                    self._chat_endpoint,
                    json={
                        "model": self._model_name,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt},
                        ],
                        "stream": False,
                        "options": {
                            "temperature": 0.4,
                            "num_predict": 2048,
                        },
                    },
                    timeout=120,
                )
                status = response.status_code
                if status == 200:
                    data = response.json()
                    raw = data.get("message", {}).get("content", "")
                    if raw.strip():
                        return raw
                    raise LlmServiceError(
                        "Ollama returned an empty message content."
                    )

                if status not in _RETRYABLE_STATUS or attempt == max_attempts:
                    raise OllamaServiceError(
                        f"Ollama API error (HTTP {status}): {response.text[:300]}"
                    )

                logger.warning(
                    "Ollama transient error (status=%s) on attempt %s; retrying in %.1fs",
                    status,
                    attempt,
                    backoff,
                )
                time.sleep(backoff)
                backoff *= 2

            except requests.ConnectionError as exc:
                last_exc = exc
                if attempt == max_attempts:
                    raise OllamaServiceError(
                        f"Cannot reach Ollama at {self._base_url}. "
                        "Make sure Ollama is running."
                    ) from exc
                logger.warning(
                    "Ollama connection error on attempt %s; retrying in %.1fs",
                    attempt,
                    backoff,
                )
                time.sleep(backoff)
                backoff *= 2

        raise OllamaServiceError(
            f"Ollama API failed after {max_attempts} attempts: {last_exc}"
        )

    @staticmethod
    def _parse_json(raw_text: str) -> Dict[str, Any]:
        """Parse JSON from a model response that may include extra prose."""
        cleaned = raw_text.strip()

        fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
        if fence_match:
            cleaned = fence_match.group(1)

        if not cleaned.startswith("{"):
            brace_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if brace_match:
                cleaned = brace_match.group(0)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse Ollama JSON: %s", cleaned[:500])
            raise OllamaServiceError(
                "Ollama returned a response that could not be parsed as JSON."
            ) from exc

    @staticmethod
    def _validate_payload(
        payload: Dict[str, Any], original_requirement: str
    ) -> Dict[str, Any]:
        """Validate AI output and return a clean dictionary for persistence."""
        if not isinstance(payload, dict):
            raise OllamaServiceError("Ollama JSON must be an object.")

        raw_cases = payload.get("test_cases")
        if not isinstance(raw_cases, list) or not raw_cases:
            raise OllamaServiceError(
                "Ollama JSON must include a non-empty test_cases array."
            )

        validated: list[Dict[str, Any]] = []
        for index, raw_case in enumerate(raw_cases[:5], start=1):
            try:
                case = TestCase.model_validate(raw_case)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Skipping invalid test case #%s: %s", index, exc)
                continue

            case_dict = case.model_dump()
            case_dict["test_case_id"] = f"TC{index:03d}"
            validated.append(case_dict)

        if not validated:
            raise OllamaServiceError("None of the generated test cases were valid.")

        return {
            "requirement": payload.get("requirement") or original_requirement,
            "test_cases": validated,
        }

    @staticmethod
    def check_availability() -> bool:
        """Return ``True`` if the Ollama server is reachable and has at least one model loaded."""
        settings = get_settings()
        base_url = settings.ollama_base_url.rstrip("/")
        try:
            r = requests.get(f"{base_url}/api/tags", timeout=3)
            if r.status_code == 200:
                data = r.json()
                models = data.get("models", [])
                return len(models) > 0
            return False
        except requests.ConnectionError:
            return False
