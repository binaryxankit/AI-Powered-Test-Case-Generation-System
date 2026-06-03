"""Shared exception types for LLM-based services."""
from __future__ import annotations


class LlmServiceError(RuntimeError):
    """Raised when any LLM service cannot produce a valid response."""
