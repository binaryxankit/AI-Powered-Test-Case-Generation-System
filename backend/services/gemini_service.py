"""Thin wrapper around the Google Gemini SDK for test case generation."""
from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, Dict

from google import genai
from google.genai import errors as genai_errors

from backend.config import get_settings
from backend.schemas.test_case import TestCase

logger = logging.getLogger(__name__)


# Transient errors worth retrying: 429 (rate limit), 5xx, and connection
# failures raised by the SDK. We deliberately do NOT retry on
# ``ValueError`` or invalid-argument errors.
_RETRYABLE_STATUS = {429, 500, 502, 503, 504}


SYSTEM_PROMPT = (
    "You are a senior QA engineer with 15+ years of experience writing "
    "production-grade software test cases. You always think about both "
    "positive (happy-path) and negative (edge / failure) scenarios, and "
    "you prioritize tests based on risk and business impact.\n\n"
    "Generate professional software testing test cases for the user's "
    "requirement. Return STRICT JSON only — no prose, no markdown fences, "
    "no commentary. The JSON MUST match this schema exactly:\n\n"
    "{\n"
    '  "requirement": "<the original requirement>",\n'
    '  "test_cases": [\n'
    "    {\n"
    '      "test_case_id": "TC001",\n'
    '      "title": "<short, descriptive title>",\n'
    '      "priority": "High" | "Medium" | "Low" | "Critical",\n'
    '      "steps": ["step 1", "step 2", "..."],\n'
    '      "expected_result": "<clear, verifiable outcome>",\n'
    '      "edge_cases": ["edge case 1", "edge case 2"]\n'
    "    }\n"
    "  ]\n"
    "}\n\n"
    "Rules:\n"
    "- Generate 3 to 5 test cases.\n"
    "- Include at least one positive and one negative scenario.\n"
    "- test_case_id must be unique, sequential, formatted as TC001, TC002, ...\n"
    "- priority must be exactly one of: Low, Medium, High, Critical.\n"
    "- steps must be an ordered list of short imperative sentences.\n"
    "- edge_cases must be a list of short strings (may be empty).\n"
    "- Do NOT include any text before or after the JSON object."
)


class GeminiServiceError(RuntimeError):
    """Raised when the AI service cannot produce a valid response."""


class GeminiService:
    """Encapsulates all interaction with the Google Gemini API."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        settings = get_settings()
        self._api_key = api_key or settings.gemini_api_key
        self._model_name = model or settings.gemini_model

        if not self._api_key:
            raise GeminiServiceError(
                "GEMINI_API_KEY is not configured. Set it in your .env file."
            )

        self._client = genai.Client(api_key=self._api_key)

    @property
    def model_name(self) -> str:
        """Return the configured Gemini model name."""
        return self._model_name

    def generate_test_cases(self, requirement: str) -> Dict[str, Any]:
        """Generate structured test cases for the given requirement.

        Returns a dictionary that conforms to the ``TestGenerationResponse``
        schema's ``test_cases`` shape, ready to be persisted.
        """
        user_prompt = (
            f"Requirement:\n\"\"\"\n{requirement.strip()}\n\"\"\"\n\n"
            "Return ONLY the JSON object as specified."
        )

        response = self._call_with_retry(user_prompt)
        raw_text = self._extract_text(response)
        payload = self._parse_json(raw_text)
        return self._validate_payload(payload, requirement)

    def _call_with_retry(self, user_prompt: str) -> Any:
        """Call Gemini with exponential backoff for transient errors."""
        max_attempts = 3
        backoff = 1.0
        last_exc: Exception | None = None

        for attempt in range(1, max_attempts + 1):
            try:
                return self._client.models.generate_content(
                    model=self._model_name,
                    contents=user_prompt,
                    config={
                        "system_instruction": SYSTEM_PROMPT,
                        "temperature": 0.4,
                        "top_p": 0.95,
                        "max_output_tokens": 2048,
                        "response_mime_type": "application/json",
                    },
                )
            except genai_errors.APIError as exc:
                status = getattr(exc, "code", None) or 0
                last_exc = exc
                if status not in _RETRYABLE_STATUS or attempt == max_attempts:
                    logger.exception(
                        "Gemini API error on attempt %s: %s", attempt, exc
                    )
                    raise GeminiServiceError(
                        f"Gemini API error: {exc}"
                    ) from exc
                logger.warning(
                    "Gemini transient error (status=%s) on attempt %s; retrying in %.1fs",
                    status,
                    attempt,
                    backoff,
                )
                time.sleep(backoff)
                backoff *= 2

        # Unreachable, but the type checker wants an explicit raise.
        raise GeminiServiceError(
            f"Gemini API failed after {max_attempts} attempts: {last_exc}"
        )

    @staticmethod
    def _extract_text(response: Any) -> str:
        """Pull the textual content out of a Gemini response."""
        text = getattr(response, "text", None)
        if text:
            return text

        # Some responses expose ``candidates`` instead of ``text``.
        candidates = getattr(response, "candidates", None) or []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            if not content:
                continue
            parts = getattr(content, "parts", None) or []
            for part in parts:
                part_text = getattr(part, "text", None)
                if part_text:
                    return part_text

        raise GeminiServiceError("Gemini returned an empty response.")

    @staticmethod
    def _parse_json(raw_text: str) -> Dict[str, Any]:
        """Parse JSON from a model response that may include extra prose."""
        cleaned = raw_text.strip()

        # Strip code fences if the model ignored the instruction.
        fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
        if fence_match:
            cleaned = fence_match.group(1)

        # Last-ditch effort: grab the first {...} block.
        if not cleaned.startswith("{"):
            brace_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if brace_match:
                cleaned = brace_match.group(0)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse Gemini JSON: %s", cleaned[:500])
            raise GeminiServiceError(
                "Gemini returned a response that could not be parsed as JSON."
            ) from exc

    @staticmethod
    def _validate_payload(
        payload: Dict[str, Any], original_requirement: str
    ) -> Dict[str, Any]:
        """Validate AI output and return a clean dictionary for persistence."""
        if not isinstance(payload, dict):
            raise GeminiServiceError("Gemini JSON must be an object.")

        raw_cases = payload.get("test_cases")
        if not isinstance(raw_cases, list) or not raw_cases:
            raise GeminiServiceError("Gemini JSON must include a non-empty test_cases array.")

        validated: list[Dict[str, Any]] = []
        for index, raw_case in enumerate(raw_cases[:5], start=1):
            try:
                case = TestCase.model_validate(raw_case)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Skipping invalid test case #%s: %s", index, exc)
                continue

            # Re-number IDs sequentially in case the model was inconsistent.
            case_dict = case.model_dump()
            case_dict["test_case_id"] = f"TC{index:03d}"
            validated.append(case_dict)

        if not validated:
            raise GeminiServiceError("None of the generated test cases were valid.")

        return {
            "requirement": payload.get("requirement") or original_requirement,
            "test_cases": validated,
        }
