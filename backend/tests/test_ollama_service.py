"""Unit tests for the Ollama service JSON parsing and validation."""
from __future__ import annotations

import json

import pytest

from backend.config import get_settings
from backend.schemas.test_case import TestCase
from backend.services.ollama_service import OllamaService, OllamaServiceError


class TestParseJson:
    @pytest.mark.parametrize(
        "raw,expected_keys",
        [
            ('{"requirement": "r", "test_cases": []}', {"requirement"}),
            ('  \n  {"requirement": "r", "test_cases": []}  ', {"requirement"}),
            ('```json\n{"requirement": "r", "test_cases": []}\n```', {"requirement"}),
            ('prefix text\n{"requirement": "r", "test_cases": []}\nsuffix', {"requirement"}),
        ],
    )
    def test_parses_well_formed_payloads(self, raw: str, expected_keys: set):
        payload = OllamaService._parse_json(raw)
        assert set(payload.keys()) >= expected_keys

    def test_strips_outer_code_fence(self):
        raw = '```\n{"x": 1}\n```'
        assert OllamaService._parse_json(raw) == {"x": 1}

    def test_raises_on_invalid_json(self):
        with pytest.raises(OllamaServiceError):
            OllamaService._parse_json("not json at all")


class TestValidatePayload:
    @pytest.fixture
    def requirement(self) -> str:
        return "Verify login"

    def test_accepts_a_well_formed_payload(self, requirement: str):
        payload = {
            "requirement": requirement,
            "test_cases": [
                {
                    "test_case_id": "TC001",
                    "title": "Test",
                    "priority": "High",
                    "steps": ["s"],
                    "expected_result": "r",
                    "edge_cases": ["e"],
                }
            ],
        }
        validated = OllamaService._validate_payload(payload, requirement)
        assert validated["requirement"] == requirement
        assert len(validated["test_cases"]) == 1

    def test_renumbers_test_case_ids_sequentially(self, requirement: str):
        payload = {
            "requirement": requirement,
            "test_cases": [
                {
                    "test_case_id": "TC999",
                    "title": "First",
                    "priority": "High",
                    "steps": ["s"],
                    "expected_result": "r",
                    "edge_cases": [],
                },
                {
                    "test_case_id": "TC001",
                    "title": "Second",
                    "priority": "Medium",
                    "steps": ["s"],
                    "expected_result": "r",
                    "edge_cases": [],
                },
            ],
        }
        validated = OllamaService._validate_payload(payload, requirement)
        ids = [c["test_case_id"] for c in validated["test_cases"]]
        assert ids == ["TC001", "TC002"]

    def test_caps_at_five_cases(self, requirement: str):
        cases = [
            {
                "test_case_id": f"TC{i:03d}",
                "title": f"t{i}",
                "priority": "High",
                "steps": ["s"],
                "expected_result": "r",
                "edge_cases": [],
            }
            for i in range(1, 8)
        ]
        payload = {"requirement": requirement, "test_cases": cases}
        validated = OllamaService._validate_payload(payload, requirement)
        assert len(validated["test_cases"]) == 5

    def test_skips_invalid_cases_and_keeps_valid(self, requirement: str):
        payload = {
            "requirement": requirement,
            "test_cases": [
                {
                    "test_case_id": "TC001",
                    "title": "valid",
                    "priority": "High",
                    "steps": ["s"],
                    "expected_result": "r",
                },
                {
                    "test_case_id": "TC002",
                    "title": "",
                    "priority": "High",
                    "steps": ["s"],
                    "expected_result": "r",
                },
            ],
        }
        validated = OllamaService._validate_payload(payload, requirement)
        assert len(validated["test_cases"]) == 1

    def test_raises_when_no_cases(self, requirement: str):
        with pytest.raises(OllamaServiceError):
            OllamaService._validate_payload(
                {"requirement": requirement, "test_cases": []}, requirement
            )

    def test_raises_when_every_case_is_invalid(self, requirement: str):
        with pytest.raises(OllamaServiceError):
            OllamaService._validate_payload(
                {
                    "requirement": requirement,
                    "test_cases": [
                        {
                            "test_case_id": "TC001",
                            "title": "",
                            "priority": "High",
                            "steps": ["s"],
                            "expected_result": "r",
                        }
                    ],
                },
                requirement,
            )

    def test_uses_original_requirement_when_missing(self, requirement: str):
        payload = {
            "test_cases": [
                {
                    "test_case_id": "TC001",
                    "title": "t",
                    "priority": "High",
                    "steps": ["s"],
                    "expected_result": "r",
                }
            ]
        }
        validated = OllamaService._validate_payload(payload, requirement)
        assert validated["requirement"] == requirement


class TestCheckAvailability:
    def test_returns_false_when_ollama_unreachable(self, monkeypatch: pytest.MonkeyPatch):
        settings = get_settings()
        monkeypatch.setattr(settings, "ollama_base_url", "http://localhost:19999")
        assert OllamaService.check_availability() is False


def test_ollama_service_init():
    svc = OllamaService(base_url="http://my-ollama:11434", model="llama3:8b")
    assert svc.model_name == "llama3:8b"
    assert svc.base_url == "http://my-ollama:11434"
