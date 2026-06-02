"""In-process cache for generated test cases.

Identical requirements often produce the same (or very similar) Gemini
output. To save API quota and reduce latency, we memoise the result of
recent successful generations for a configurable TTL.

The cache is intentionally simple:

* keyed on the *normalised* requirement (lowercased, whitespace
  collapsed) so trivial phrasing differences still hit the cache.
* bounded to ``max_entries`` items using ``OrderedDict`` for LRU
  eviction.
* thread-safe via a single lock — the underlying ``OrderedDict`` is
  mutated only inside the critical section.

This is an in-process cache only. A production deployment with
multiple workers should swap this for Redis or rely on the
``test_generations`` table, which already de-duplicates history
queries by ID.
"""
from __future__ import annotations

import threading
import time
from collections import OrderedDict
from typing import Any, Dict, Optional


def _normalise(requirement: str) -> str:
    """Return a stable, cache-friendly key for a requirement string."""
    return " ".join(requirement.lower().split())


class GenerationCache:
    """A small, thread-safe, TTL-bounded LRU cache."""

    def __init__(self, max_entries: int = 64, ttl_seconds: float = 600.0) -> None:
        if max_entries <= 0:
            raise ValueError("max_entries must be positive")
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")

        self._max = max_entries
        self._ttl = ttl_seconds
        self._data: "OrderedDict[str, tuple[float, Dict[str, Any]]]" = OrderedDict()
        self._lock = threading.Lock()

    def get(self, requirement: str) -> Optional[Dict[str, Any]]:
        """Return a cached payload, or ``None`` on miss / expiry."""
        key = _normalise(requirement)
        now = time.monotonic()

        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if expires_at < now:
                # Expired: drop and report a miss.
                self._data.pop(key, None)
                return None
            # Move to the end to mark as recently used.
            self._data.move_to_end(key)
            return value

    def set(self, requirement: str, value: Dict[str, Any]) -> None:
        """Store ``value`` under ``requirement`` and evict if necessary."""
        key = _normalise(requirement)
        now = time.monotonic()
        expires_at = now + self._ttl

        with self._lock:
            if key in self._data:
                self._data.move_to_end(key)
            self._data[key] = (expires_at, value)
            while len(self._data) > self._max:
                self._data.popitem(last=False)

    def clear(self) -> None:
        """Remove every entry. Mostly useful for tests."""
        with self._lock:
            self._data.clear()

    def __len__(self) -> int:  # pragma: no cover - trivial
        with self._lock:
            return len(self._data)
