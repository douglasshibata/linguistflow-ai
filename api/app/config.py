from __future__ import annotations

from functools import lru_cache

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _csv_to_list(value: str | list[str]) -> list[str]:
    if isinstance(value, list):
        return [v.strip() for v in value if v and v.strip()]
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


# Fields that store CSV strings in env but are exposed as list[str]
_CSV_FIELDS = frozenset({
    "cors_origins", "openai_models", "claude_models",
    "gemini_models", "openrouter_models", "ollama_models",
    "nvidia_models",
})


class ProviderSettings(BaseSettings):
    """Per-provider LLM config. Loaded from env with prefix LLM_<NAME>_."""

    enabled: bool = False
    api_key: SecretStr = SecretStr("")
    base_url: str = ""
    models: str = ""
    timeout_seconds: int = 60
    temperature: float = 0.7
    max_tokens: int = 1024


class Settings(BaseSettings):
    """Application settings. Read from environment or .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = Field("production", alias="APP_ENV")
    log_level: str = Field("INFO", alias="LOG_LEVEL")

    mongo_uri: str = Field(..., alias="MONGO_URI")
    mongo_database: str = Field("linguistflow", alias="MONGO_DATABASE")

    neo4j_uri: str = Field(..., alias="NEO4J_URI")
    neo4j_user: str = Field("neo4j", alias="NEO4J_USER")
    neo4j_password: SecretStr = Field(..., alias="NEO4J_PASSWORD")

    # --- CSV fields: stored as str to avoid pydantic-settings JSON parsing,
    #     converted to list[str] in the model_validator below. ---------------
    cors_origins: str | list[str] = Field("http://localhost:8501")
    rate_limit: str = Field("30/minute", alias="RATE_LIMIT")
    max_upload_bytes: int = Field(10 * 1024 * 1024, alias="MAX_UPLOAD_BYTES")

    whisper_model: str = Field("base", alias="WHISPER_MODEL")

    default_provider: str = Field("ollama", alias="LLM_DEFAULT_PROVIDER")

    openai_enabled: bool = Field(False, alias="LLM_OPENAI_ENABLED")
    openai_api_key: SecretStr = Field(SecretStr(""), alias="LLM_OPENAI_API_KEY")
    openai_models: str | list[str] = Field("", alias="LLM_OPENAI_MODELS")

    claude_enabled: bool = Field(False, alias="LLM_CLAUDE_ENABLED")
    claude_api_key: SecretStr = Field(SecretStr(""), alias="LLM_CLAUDE_API_KEY")
    claude_models: str | list[str] = Field("", alias="LLM_CLAUDE_MODELS")

    gemini_enabled: bool = Field(False, alias="LLM_GEMINI_ENABLED")
    gemini_api_key: SecretStr = Field(SecretStr(""), alias="LLM_GEMINI_API_KEY")
    gemini_models: str | list[str] = Field("", alias="LLM_GEMINI_MODELS")

    openrouter_enabled: bool = Field(False, alias="LLM_OPENROUTER_ENABLED")
    openrouter_api_key: SecretStr = Field(SecretStr(""), alias="LLM_OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(
        "https://openrouter.ai/api/v1", alias="LLM_OPENROUTER_BASE_URL"
    )
    openrouter_models: str | list[str] = Field("", alias="LLM_OPENROUTER_MODELS")

    ollama_enabled: bool = Field(True, alias="LLM_OLLAMA_ENABLED")
    ollama_base_url: str = Field("http://ollama:11434", alias="LLM_OLLAMA_BASE_URL")
    ollama_models: str | list[str] = Field("", alias="LLM_OLLAMA_MODELS")

    nvidia_enabled: bool = Field(False, alias="LLM_NVIDIA_ENABLED")
    nvidia_api_key: SecretStr = Field(SecretStr(""), alias="LLM_NVIDIA_API_KEY")
    nvidia_base_url: str = Field(
        "https://integrate.api.nvidia.com/v1", alias="LLM_NVIDIA_BASE_URL"
    )
    nvidia_models: str | list[str] = Field("", alias="LLM_NVIDIA_MODELS")

    llm_temperature: float = Field(0.7, alias="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(1024, alias="LLM_MAX_TOKENS")
    llm_timeout_seconds: int = Field(120, alias="LLM_TIMEOUT_SECONDS")

    @model_validator(mode="after")
    def _parse_csv_fields(self) -> Settings:
        """Convert CSV string fields to list[str] after env parsing."""
        for field_name in _CSV_FIELDS:
            raw = getattr(self, field_name)
            object.__setattr__(self, field_name, _csv_to_list(raw))
        return self

    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
