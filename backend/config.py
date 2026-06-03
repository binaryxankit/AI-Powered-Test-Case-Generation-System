"""Application configuration loaded from environment variables.

Centralizes all settings in a single Pydantic ``Settings`` instance so
modules can depend on a single, typed source of truth.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the FastAPI backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = Field(
        default="postgresql+psycopg2://testcase_user:testcase_pass@localhost:5432/testcase_ai",
        description="SQLAlchemy connection string for PostgreSQL.",
    )

    gemini_api_key: str = Field(
        default="",
        description="Google Gemini API key.",
    )

    gemini_model: str = Field(
        default="gemini-1.5-flash",
        description="Gemini model name used for generation.",
    )

    llm_provider: str = Field(
        default="auto",
        description="LLM backend to use: 'auto' (try Gemini, fallback Ollama), 'gemini', or 'ollama'.",
    )

    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Base URL for the Ollama API.",
    )

    ollama_model: str = Field(
        default="gemma2:2b",
        description="Ollama model name used for generation.",
    )

    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        description="Allowed CORS origins for the API.",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, value):  # noqa: D401
        """Allow comma-separated strings in env files."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance."""
    return Settings()
