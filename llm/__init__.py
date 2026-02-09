"""
LLM module for NcDashboard Custom Analysis feature.

Provides multi-provider LLM support (Ollama, OpenAI, Gemini) for generating
Python code that operates on xarray data.
"""

from .llm_client import (
    BaseLLMClient,
    OllamaClient,
    OpenAIClient,
    GeminiClient,
    get_llm_client,
    LLMProviders,
)
from .prompt_builder import PromptBuilder
from .code_executor import CodeExecutor, ExecutionResult, run_with_retry

__all__ = [
    "BaseLLMClient",
    "OllamaClient", 
    "OpenAIClient",
    "GeminiClient",
    "get_llm_client",
    "LLMProviders",
    "PromptBuilder",
    "CodeExecutor",
    "ExecutionResult",
    "run_with_retry",
]
