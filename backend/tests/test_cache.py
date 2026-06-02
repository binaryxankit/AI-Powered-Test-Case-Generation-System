"""Unit tests for the in-process generation cache."""
from __future__ import annotations

import time

import pytest

from backend.services.cache import GenerationCache, _normalise


class TestNormalise:
    def test_lowercases(self):
        assert _normalise("Hello") == "hello"

    def test_collapses_whitespace(self):
        assert _normalise("hello   world\n\nfoo") == "hello world foo"

    def test_strips_outer_whitespace(self):
        assert _normalise("  hello  ") == "hello"


class TestCache:
    def test_miss_on_empty(self):
        cache = GenerationCache()
        assert cache.get("anything") is None

    def test_set_then_get(self):
        cache = GenerationCache()
        cache.set("Verify login", {"k": "v"})
        assert cache.get("Verify login") == {"k": "v"}

    def test_normalisation_dedupes(self):
        cache = GenerationCache()
        cache.set("Verify login", {"k": "v"})
        assert cache.get("VERIFY   login") == {"k": "v"}

    def test_ttl_expiry(self):
        cache = GenerationCache(max_entries=10, ttl_seconds=0.1)
        cache.set("x", {"k": 1})
        assert cache.get("x") == {"k": 1}
        time.sleep(0.2)
        assert cache.get("x") is None

    def test_lru_eviction(self):
        cache = GenerationCache(max_entries=2, ttl_seconds=60)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)  # evicts a
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3

    def test_recently_used_is_not_evicted(self):
        cache = GenerationCache(max_entries=2, ttl_seconds=60)
        cache.set("a", 1)
        cache.set("b", 2)
        # Touch "a" so it becomes most recently used.
        assert cache.get("a") == 1
        cache.set("c", 3)  # evicts b
        assert cache.get("a") == 1
        assert cache.get("b") is None
        assert cache.get("c") == 3

    def test_clear(self):
        cache = GenerationCache()
        cache.set("a", 1)
        cache.set("b", 2)
        assert len(cache) == 2
        cache.clear()
        assert len(cache) == 0
        assert cache.get("a") is None

    def test_invalid_construction(self):
        with pytest.raises(ValueError):
            GenerationCache(max_entries=0)
        with pytest.raises(ValueError):
            GenerationCache(ttl_seconds=0)
