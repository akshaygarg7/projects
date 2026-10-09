import os
from abc import ABC, abstractmethod
from src.ai.common.llm.gemini_proxy import Gemini
from src.ai.common.llm.groq_proxy import Groq

def get_model(provider_name=None):
    provider = (provider_name or os.getenv("MODEL_PROVIDER", "groq")).lower()
    strategies = {
        "groq": Groq(),
        "gemini": Gemini(),
    }

    try:
        return strategies[provider]
    except KeyError as exc:
        raise ValueError(f"Unsupported model provider: {provider}. Use 'groq' or 'gemini'.") from exc
