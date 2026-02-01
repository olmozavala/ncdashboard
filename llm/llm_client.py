"""
Multi-provider LLM client for code generation.

Supports:
- Ollama (local, free)
- OpenAI (requires API key)
- Google Gemini (requires API key)
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from netrc import netrc
from typing import Optional
import requests
from loguru import logger


class LLMProviders(Enum):
    """Available LLM providers."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    GEMINI = "gemini"


@dataclass
class LLMConfig:
    """Configuration for LLM client."""
    provider: LLMProviders
    model: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.1  # Low temperature for code generation


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate code from prompt. Returns the generated code string."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM service is available."""
        pass


class OllamaClient(BaseLLMClient):
    """Client for local Ollama server."""
    
    DEFAULT_MODEL = "qwen2.5-coder:3b"
    DEFAULT_URL = "http://localhost:11434"
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or self.DEFAULT_URL
        self.model = config.model or self.DEFAULT_MODEL
    
    def generate(self, prompt: str) -> str:
        """Generate code using Ollama API."""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return self._extract_code(result.get("response", ""))
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            raise ConnectionError(f"Failed to connect to Ollama: {e}")
    
    def is_available(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def _extract_code(self, response: str) -> str:
        """Extract Python code from response, handling markdown and explanations."""
        import re
        
        # First, try to find code blocks with ```python or ``` markers
        # Look for the LAST code block (often the corrected version)
        python_blocks = re.findall(r'```python\s*(.*?)```', response, re.DOTALL)
        if python_blocks:
            return python_blocks[-1].strip()
        
        # Try generic code blocks
        code_blocks = re.findall(r'```\s*(.*?)```', response, re.DOTALL)
        if code_blocks:
            # Filter out blocks that look like they contain the prompt or error message
            for block in reversed(code_blocks):
                block = block.strip()
                if block and not block.startswith('User request:') and 'ERROR MESSAGE' not in block:
                    return block
        
        # No code blocks found - try to use the whole response
        code = response.strip()
        # Remove common LLM preamble phrases
        preambles = [
            "Here is the corrected code:",
            "Here is the code:",
            "Fixed code:",
            "The corrected code is:",
            "Here's the fixed code:",
        ]
        for preamble in preambles:
            if preamble in code:
                code = code.split(preamble, 1)[1].strip()
                break
        
        return code.strip()


class OpenAIClient(BaseLLMClient):
    """Client for OpenAI API."""
    
    DEFAULT_MODEL = "gpt-4o-mini"
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.model = config.model or self.DEFAULT_MODEL
        self.api_key = self._get_api_key(config)
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Add 'machine OPENAI password YOUR_KEY' to .netrc or set OPENAI_API_KEY env var")
    
    def _get_api_key(self, config: LLMConfig) -> Optional[str]:
        """Get API key from config, .netrc, or environment variable (in that order)."""
        if config.api_key:
            return config.api_key
        
        # Try netrc first
        try:
            netrc_obj = netrc()
            auth = netrc_obj.authenticators("OPENAI")
            if auth:
                logger.debug("Using OpenAI API key from .netrc")
                return auth[2]  # password field
        except (FileNotFoundError, TypeError):
            pass
        
        # Fall back to environment variable
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            logger.debug("Using OpenAI API key from OPENAI_API_KEY env var")
            return api_key
        
        return None
    
    def generate(self, prompt: str) -> str:
        """Generate code using OpenAI API."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        client = OpenAI(api_key=self.api_key)
        
        try:
            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful Python code assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
            )
            response = completion.choices[0].message.content or ""
            return self._extract_code(response)
        except Exception as e:
            logger.error(f"OpenAI request failed: {e}")
            raise ConnectionError(f"Failed to call OpenAI API: {e}")
    
    def is_available(self) -> bool:
        """Check if OpenAI API is accessible."""
        return self.api_key is not None
    
    def _extract_code(self, response: str) -> str:
        """Extract Python code from response, removing markdown fences."""
        code = response.strip()
        if code.startswith("```python"):
            code = code[9:]
        elif code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        return code.strip()


class GeminiClient(BaseLLMClient):
    """Client for Google Gemini API."""
    
    DEFAULT_MODEL = "gemini-2.0-flash"
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.model = config.model or self.DEFAULT_MODEL
        self.api_key = self._get_api_key(config)
        
        if not self.api_key:
            raise ValueError("Gemini API key not found. Add 'machine GEMINI password YOUR_KEY' to .netrc or set GEMINI_API_KEY env var")
    
    def _get_api_key(self, config: LLMConfig) -> Optional[str]:
        """Get API key from config, .netrc, or environment variable (in that order)."""
        if config.api_key:
            return config.api_key
        
        # Try netrc first
        try:
            netrc_obj = netrc()
            auth = netrc_obj.authenticators("GEMINI")
            if auth:
                logger.debug("Using Gemini API key from .netrc")
                return auth[2]  # password field
        except (FileNotFoundError, TypeError):
            pass
        
        # Fall back to environment variable
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            logger.debug("Using Gemini API key from GEMINI_API_KEY env var")
            return api_key
        
        return None
    
    def generate(self, prompt: str) -> str:
        """Generate code using Gemini API."""
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
        
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model)
        
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.temperature,
                )
            )
            return self._extract_code(response.text)
        except Exception as e:
            logger.error(f"Gemini request failed: {e}")
            raise ConnectionError(f"Failed to call Gemini API: {e}")
    
    def is_available(self) -> bool:
        """Check if Gemini API is accessible."""
        return self.api_key is not None
    
    def _extract_code(self, response: str) -> str:
        """Extract Python code from response, removing markdown fences."""
        code = response.strip()
        if code.startswith("```python"):
            code = code[9:]
        elif code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        return code.strip()


def get_llm_client(
    provider: str | LLMProviders,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> BaseLLMClient:
    """
    Factory function to get appropriate LLM client.
    
    Args:
        provider: LLM provider name ("ollama", "openai", "gemini")
        model: Optional model name (uses provider defaults if not specified)
        api_key: Optional API key (uses env vars if not specified)
        base_url: Optional base URL (for Ollama)
    
    Returns:
        Configured LLM client instance
    """
    if isinstance(provider, str):
        provider = LLMProviders(provider.lower())
    
    config = LLMConfig(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url,
    )
    
    client_map = {
        LLMProviders.OLLAMA: OllamaClient,
        LLMProviders.OPENAI: OpenAIClient,
        LLMProviders.GEMINI: GeminiClient,
    }
    
    client_class = client_map.get(provider)
    if not client_class:
        raise ValueError(f"Unknown LLM provider: {provider}")
    
    return client_class(config)
