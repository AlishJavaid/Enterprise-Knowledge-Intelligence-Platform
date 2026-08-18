import httpx

from app.core.config import settings


class BaseLLM:
    def generate(self, system: str, prompt: str) -> str:
        raise NotImplementedError


class OpenAILLM(BaseLLM):
    def generate(self, system: str, prompt: str) -> str:
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
        payload = {
            "model": settings.openai_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
        }
        r = httpx.post(
            f"{settings.openai_base_url}/chat/completions",
            json=payload, headers=headers, timeout=60,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


class OllamaLLM(BaseLLM):
    def generate(self, system: str, prompt: str) -> str:
        payload = {
            "model": settings.ollama_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }
        r = httpx.post(f"{settings.ollama_base_url}/api/chat", json=payload, timeout=120)
        r.raise_for_status()
        return r.json()["message"]["content"]


class MockLLM(BaseLLM):
    def generate(self, system: str, prompt: str) -> str:
        return (
            "[MOCK] Based on the provided context, the answer draws on sources [1] and [2]. "
            "Connect a real LLM provider via LLM_PROVIDER to get live generation."
        )


def get_llm() -> BaseLLM:
    return {
        "openai": OpenAILLM,
        "ollama": OllamaLLM,
        "mock": MockLLM,
    }.get(settings.llm_provider, MockLLM)()