"""LLM router backed by LiteLLM. Resolves provider+model from request,
validates against whitelist, and proxies to the unified completion API."""

from __future__ import annotations

import litellm

from app.config import Settings
from app.llm.registry import LITELLM_PREFIX, ProviderEntry, build_registry


class LlmError(Exception):
    """Raised on validation or upstream LLM failure."""


class LlmRouter:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._registry: dict[str, ProviderEntry] = build_registry(settings)
        # LiteLLM global config
        litellm.drop_params = True
        litellm.set_verbose = False
        litellm.suppress_debug_info = True

    @property
    def default_provider(self) -> str:
        return self._settings.default_provider

    def list_providers(self) -> dict[str, list[str]]:
        return {name: list(entry.models) for name, entry in self._registry.items()}

    def _resolve(self, provider: str | None, model: str | None) -> tuple[ProviderEntry, str]:
        name = (provider or self._settings.default_provider).lower()
        entry = self._registry.get(name)
        if entry is None:
            allowed = sorted(self._registry.keys())
            raise LlmError(
                f"provider not enabled: {name!r}. enabled providers: {allowed}"
            )
        chosen = model or (entry.models[0] if entry.models else None)
        if chosen is None or chosen not in entry.models:
            raise LlmError(
                f"model {chosen!r} not allowed for provider {name!r}. "
                f"allowed: {list(entry.models)}"
            )
        return entry, chosen

    async def generate(
        self,
        provider: str | None,
        model: str | None,
        prompt: str | list[dict[str, str]],
    ) -> str:
        messages = prompt if isinstance(prompt, list) else [{"role": "user", "content": prompt}]
        return await self.chat(provider, model, messages)

    async def chat(
        self,
        provider: str | None,
        model: str | None,
        messages: list[dict[str, str]],
    ) -> str:
        entry, chosen = self._resolve(provider, model)
        kwargs: dict = {
            "model": f"{LITELLM_PREFIX[entry.name]}/{chosen}",
            "messages": messages,
            "temperature": self._settings.llm_temperature,
            "max_tokens": self._settings.llm_max_tokens,
            "timeout": self._settings.llm_timeout_seconds,
            "num_retries": 0,
        }
        if entry.name == "ollama":
            kwargs["api_base"] = entry.base_url
        elif entry.name == "openrouter":
            kwargs["api_key"] = entry.api_key
            kwargs["api_base"] = entry.base_url
        else:
            kwargs["api_key"] = entry.api_key

        try:
            # Force no proxy for local Ollama to avoid corporate proxy interception
            if entry.name == "ollama":
                kwargs["proxy"] = None

            response = await litellm.acompletion(**kwargs)
        except Exception as exc:  # noqa: BLE001
            import structlog
            structlog.get_logger("linguistflow").error(
                "llm.error",
                provider=entry.name,
                model=chosen,
                url=entry.base_url,
                error=str(exc),
            )
            raise LlmError(f"LLM upstream error: {exc.__class__.__name__}") from exc

        content = response.choices[0].message.content
        if not content:
            raise LlmError("LLM returned empty response")
        return content
