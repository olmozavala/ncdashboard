"""
Tests for the LLM module.

Tests prompt building, code execution, and retry logic.
"""

import pytest
import xarray as xr
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from llm.prompt_builder import PromptBuilder
from llm.code_executor import CodeExecutor, ExecutionResult, run_with_retry
from llm.llm_client import OllamaClient, LLMConfig, LLMProviders, get_llm_client


@pytest.fixture
def sample_dataarray():
    """Create a sample 2D DataArray for testing."""
    data = np.random.rand(10, 20)
    da = xr.DataArray(
        data,
        dims=['lat', 'lon'],
        coords={
            'lat': np.linspace(-45, 45, 10),
            'lon': np.linspace(-90, 90, 20)
        },
        name='temperature',
        attrs={'units': 'K', 'long_name': 'Temperature'}
    )
    return da


@pytest.fixture
def sample_dataset():
    """Create a sample Dataset with multiple variables."""
    data_temp = np.random.rand(10, 20)
    data_salt = np.random.rand(10, 20)
    ds = xr.Dataset({
        'temperature': (['lat', 'lon'], data_temp, {'units': 'K'}),
        'salinity': (['lat', 'lon'], data_salt, {'units': 'PSU'})
    }, coords={
        'lat': np.linspace(-45, 45, 10),
        'lon': np.linspace(-90, 90, 20)
    })
    return ds


class TestPromptBuilder:
    """Tests for PromptBuilder class."""
    
    def test_build_prompt_dataarray(self, sample_dataarray):
        """Test prompt building with a DataArray."""
        builder = PromptBuilder(sample_dataarray)
        prompt = builder.build_prompt("Calculate the mean")
        
        assert "temperature" in prompt
        assert "(10, 20)" in prompt or "10" in prompt
        assert "K" in prompt  # units
        assert "Calculate the mean" in prompt
        assert "output" in prompt.lower()
    
    def test_build_prompt_dataset(self, sample_dataset):
        """Test prompt building with a Dataset."""
        builder = PromptBuilder(sample_dataset)
        prompt = builder.build_prompt("Compute anomalies")
        
        assert "temperature" in prompt
        assert "salinity" in prompt
        assert "Compute anomalies" in prompt
    
    def test_build_error_correction_prompt(self, sample_dataarray):
        """Test error correction prompt generation."""
        builder = PromptBuilder(sample_dataarray)
        prompt = builder.build_error_correction_prompt(
            user_request="Calculate something",
            previous_code="output = data.mean()",
            error_message="NameError: name 'data' is not defined"
        )
        
        assert "Calculate something" in prompt
        assert "output = data.mean()" in prompt
        assert "NameError" in prompt
    
    def test_coordinate_ranges_included(self, sample_dataarray):
        """Test that coordinate ranges are included in prompt."""
        builder = PromptBuilder(sample_dataarray)
        prompt = builder.build_prompt("Test request")
        
        # Should include lat and lon ranges
        assert "lat" in prompt.lower()
        assert "lon" in prompt.lower()


class TestCodeExecutor:
    """Tests for CodeExecutor class."""
    
    def test_execute_valid_code(self, sample_dataarray):
        """Test execution of valid code."""
        executor = CodeExecutor()
        
        code = "output = data.mean(dim='lat')"
        result = executor.execute(code, sample_dataarray)
        
        assert result.success is True
        assert result.output is not None
        assert isinstance(result.output, xr.DataArray)
        assert result.output.shape == (20,)  # Reduced along lat
    
    def test_execute_missing_output(self, sample_dataarray):
        """Test that missing output variable is caught."""
        executor = CodeExecutor()
        
        code = "result = data.mean()"  # Wrong variable name
        result = executor.execute(code, sample_dataarray)
        
        assert result.success is False
        assert "output" in result.error_message.lower()
    
    def test_execute_syntax_error(self, sample_dataarray):
        """Test handling of syntax errors."""
        executor = CodeExecutor()
        
        code = "output = data.mean(("  # Syntax error
        result = executor.execute(code, sample_dataarray)
        
        assert result.success is False
        assert "syntax" in result.error_message.lower()
    
    def test_execute_runtime_error(self, sample_dataarray):
        """Test handling of runtime errors."""
        executor = CodeExecutor()
        
        code = "output = data['nonexistent']"  # KeyError
        result = executor.execute(code, sample_dataarray)
        
        assert result.success is False
        assert result.error_message != ""
    
    def test_execute_wrong_output_type(self, sample_dataarray):
        """Test rejection of non-DataArray output."""
        executor = CodeExecutor()
        
        code = "output = 42"  # Not a DataArray
        result = executor.execute(code, sample_dataarray)
        
        assert result.success is False
        assert "DataArray" in result.error_message
    
    def test_sandbox_restrictions(self, sample_dataarray):
        """Test that dangerous operations are blocked."""
        executor = CodeExecutor()
        
        # Try to import os (should fail)
        code = "import os; output = data"
        result = executor.execute(code, sample_dataarray)
        
        # Should fail because import is not in allowed builtins
        assert result.success is False


class TestRunWithRetry:
    """Tests for run_with_retry function."""
    
    def test_success_first_attempt(self, sample_dataarray):
        """Test success on first attempt."""
        mock_client = Mock()
        mock_client.generate.return_value = "output = data.mean(dim='lat')"
        
        result = run_with_retry(mock_client, sample_dataarray, "Calculate mean", max_attempts=3)
        
        assert result.success is True
        assert mock_client.generate.call_count == 1
    
    def test_retry_on_failure(self, sample_dataarray):
        """Test retry mechanism on failure."""
        mock_client = Mock()
        # First call fails, second succeeds
        mock_client.generate.side_effect = [
            "output = bad_code(",  # Syntax error
            "output = data.mean(dim='lat')"  # Valid code
        ]
        
        result = run_with_retry(mock_client, sample_dataarray, "Calculate mean", max_attempts=3)
        
        assert result.success is True
        assert mock_client.generate.call_count == 2
    
    def test_all_attempts_fail(self, sample_dataarray):
        """Test failure after max attempts."""
        mock_client = Mock()
        mock_client.generate.return_value = "output = bad_code("  # Always fails
        
        result = run_with_retry(mock_client, sample_dataarray, "Calculate mean", max_attempts=3)
        
        assert result.success is False
        assert mock_client.generate.call_count == 3
    
    def test_connection_error_handling(self, sample_dataarray):
        """Test handling of connection errors."""
        mock_client = Mock()
        mock_client.generate.side_effect = ConnectionError("Network error")
        
        result = run_with_retry(mock_client, sample_dataarray, "Calculate mean", max_attempts=3)
        
        assert result.success is False
        assert "connection" in result.error_message.lower()


class TestOllamaClient:
    """Tests for OllamaClient class."""
    
    def test_is_available_when_running(self):
        """Test availability check when server is running."""
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            
            config = LLMConfig(provider=LLMProviders.OLLAMA)
            client = OllamaClient(config)
            
            assert client.is_available() is True
    
    def test_is_available_when_not_running(self):
        """Test availability check when server is not running."""
        import requests
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
            
            config = LLMConfig(provider=LLMProviders.OLLAMA)
            client = OllamaClient(config)
            
            assert client.is_available() is False
    
    def test_extract_code_removes_markdown(self):
        """Test that markdown code blocks are removed."""
        config = LLMConfig(provider=LLMProviders.OLLAMA)
        client = OllamaClient(config)
        
        response = "```python\noutput = data.mean()\n```"
        code = client._extract_code(response)
        
        assert "```" not in code
        assert "python" not in code.lower() or "python" in "output = data.mean()".lower()
        assert "output = data.mean()" in code


class TestGetLLMClient:
    """Tests for get_llm_client factory function."""
    
    def test_get_ollama_client(self):
        """Test getting Ollama client."""
        client = get_llm_client("ollama")
        assert isinstance(client, OllamaClient)
    
    def test_invalid_provider(self):
        """Test error on invalid provider."""
        with pytest.raises(ValueError):
            get_llm_client("invalid_provider")
