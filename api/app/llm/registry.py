"""Provider registry: maps internal provider names to LiteLLM model prefixes
and enforces a whitelist of allowed models per provider."""

from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings

PROVIDER_NAMES = ("openai", "claude", "gemini", "openrouter", "ollama", "nvidia")

LITELLM_PREFIX: dict[str, str] = {
    "openai": "openai",
    "claude": "anthropic",
    "gemini": "gemini",
    "openrouter": "openrouter",
    "ollama": "ollama",
    "nvidia": "nvidia_nim",
}


@dataclass(frozen=True)
class ProviderEntry:
    name: str
    api_key: str
    base_url: str
    models: tuple[str, ...]


def build_registry(settings: Settings) -> dict[str, ProviderEntry]:
    raw = {
        "openai": (
            settings.openai_enabled,
            settings.openai_api_key.get_secret_value(),
            "",
            settings.openai_models,
        ),
        "claude": (
            settings.claude_enabled,
            settings.claude_api_key.get_secret_value(),
            "",
            settings.claude_models,
        ),
        "gemini": (
            settings.gemini_enabled,
            settings.gemini_api_key.get_secret_value(),
            "",
            settings.gemini_models,
        ),
        "openrouter": (
            settings.openrouter_enabled,
            settings.openrouter_api_key.get_secret_value(),
            settings.openrouter_base_url,
            settings.openrouter_models,
        ),
        "ollama": (
            settings.ollama_enabled,
            "",
            settings.ollama_base_url,
            settings.ollama_models,
        ),
        "nvidia": (
            settings.nvidia_enabled,
            settings.nvidia_api_key.get_secret_value(),
            settings.nvidia_base_url,
            settings.nvidia_models,
        ),
    }
    out: dict[str, ProviderEntry] = {}
    for name, (enabled, key, url, models) in raw.items():
        if not enabled:
            continue
        if name != "ollama" and not key:
            # cloud provider enabled without key — skip with a clear note
            continue
        if not models:
            continue
        out[name] = ProviderEntry(
            name=name, api_key=key, base_url=url, models=tuple(models)
        )
    return out
