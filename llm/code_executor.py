"""
Safe code executor for LLM-generated Python code.

Executes code in a sandboxed environment with restricted globals,
validates output, and supports retry with error feedback.
"""

import xarray as xr
import numpy as np
from dataclasses import dataclass
from typing import Optional
from loguru import logger

from .llm_client import BaseLLMClient
from .prompt_builder import PromptBuilder
from .prompts.base import get_hint_for_request


@dataclass
class ExecutionResult:
    """Result of code execution."""
    success: bool
    output: Optional[xr.DataArray]
    error_message: str
    code: str  # The code that was executed


class CodeExecutor:
    """
    Executes LLM-generated code in a sandboxed environment.
    
    Only allows access to numpy (np), xarray (xr), and the input data.
    """
    
    # Allowed modules/objects in execution sandbox
    ALLOWED_GLOBALS = {
        'np': np,
        'xr': xr,
        '__builtins__': {
            # Allow only safe built-ins
            'abs': abs,
            'all': all,
            'any': any,
            'bool': bool,
            'dict': dict,
            'enumerate': enumerate,
            'float': float,
            'int': int,
            'len': len,
            'list': list,
            'max': max,
            'min': min,
            'print': print,
            'range': range,
            'round': round,
            'slice': slice,  # Needed for .sel(dim=slice(a, b))
            'sorted': sorted,
            'str': str,
            'sum': sum,
            'tuple': tuple,
            'zip': zip,
        }
    }
    
    def execute(self, code: str, data: xr.DataArray | xr.Dataset) -> ExecutionResult:
        """
        Execute code in sandboxed environment.
        
        Args:
            code: Python code string to execute
            data: xarray data to operate on
            
        Returns:
            ExecutionResult with success status, output, and any error
        """
        # Create sandbox with data
        sandbox = dict(self.ALLOWED_GLOBALS)
        sandbox['data'] = data
        
        try:
            # Execute the code
            exec(code, sandbox)
            
            # Validate output exists
            if 'output' not in sandbox:
                return ExecutionResult(
                    success=False,
                    output=None,
                    error_message="Code did not define 'output' variable",
                    code=code,
                )
            
            output = sandbox['output']
            
            # Validate output type
            if not isinstance(output, xr.DataArray):
                return ExecutionResult(
                    success=False,
                    output=None,
                    error_message=f"'output' must be xarray.DataArray, got {type(output).__name__}",
                    code=code,
                )
            
            logger.info(f"Code executed successfully. Output shape: {output.shape}")
            return ExecutionResult(
                success=True,
                output=output,
                error_message="",
                code=code,
            )
            
        except SyntaxError as e:
            error_msg = f"Syntax error: {e}"
            logger.warning(f"Code execution failed: {error_msg}")
            return ExecutionResult(
                success=False,
                output=None,
                error_message=error_msg,
                code=code,
            )
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.warning(f"Code execution failed: {error_msg}")
            return ExecutionResult(
                success=False,
                output=None,
                error_message=error_msg,
                code=code,
            )


def run_with_retry(
    llm_client: BaseLLMClient,
    data: xr.DataArray | xr.Dataset,
    user_request: str,
    max_attempts: int = 3,
) -> ExecutionResult:
    """
    Execute LLM-generated code with retry on failure.
    
    On failure, sends error message back to LLM to fix the code.
    
    Args:
        llm_client: LLM client to use for code generation
        data: xarray data to operate on
        user_request: Natural language request from user
        max_attempts: Maximum number of attempts (default 3)
        
    Returns:
        ExecutionResult with final success/failure and output
    """
    prompt_builder = PromptBuilder(data)
    executor = CodeExecutor()
    
    # Get domain-specific hints if applicable
    hints = get_hint_for_request(user_request)
    
    # First attempt - build initial prompt
    prompt = prompt_builder.build_prompt(user_request, additional_context=hints)
    logger.info(f"User request: '{user_request}' | Hints applied: {bool(hints)}")
    
    last_result: Optional[ExecutionResult] = None
    
    for attempt in range(1, max_attempts + 1):
        logger.info(f"LLM code generation attempt {attempt}/{max_attempts}")
        
        try:
            # Generate code from LLM
            logger.debug(f"=== PROMPT SENT TO LLM ===\n{prompt}\n=== END PROMPT ===")
            code = llm_client.generate(prompt)
            logger.debug(f"Generated code:\n{code}")
            
            # Execute the code
            result = executor.execute(code, data)
            
            if result.success:
                logger.info(f"Success on attempt {attempt}")
                return result
            
            # Failed - prepare error correction prompt for next attempt
            last_result = result
            
            if attempt < max_attempts:
                logger.info(f"Attempt {attempt} failed: {result.error_message}. Retrying...")
                prompt = prompt_builder.build_error_correction_prompt(
                    user_request=user_request,
                    previous_code=result.code,
                    error_message=result.error_message,
                )
                
        except ConnectionError as e:
            error_msg = str(e)
            logger.error(f"LLM connection error: {error_msg}")
            return ExecutionResult(
                success=False,
                output=None,
                error_message=f"LLM connection failed: {error_msg}",
                code="",
            )
    
    # All attempts failed
    logger.error(f"All {max_attempts} attempts failed")
    if last_result:
        return last_result
    
    return ExecutionResult(
        success=False,
        output=None,
        error_message="All attempts failed with unknown error",
        code="",
    )
