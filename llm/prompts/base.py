"""
Base prompt templates for LLM code generation.

These prompts instruct the LLM on how to generate Python code that
operates on xarray data structures.
"""

CRITICAL_RULES = """
=== CRITICAL RULES ===
1. Store result in variable 'output' (MUST be xarray DataArray)
2. Use ONLY 'data', 'xr', 'np' - NO imports allowed
3. Handle NaN with skipna=True
4. Access variables using data['variable_name']
5. For vertical transects, by default use the depth/level coordinate and NOT the time dimension, unless explicitly specified.
6. IMPORTANT: In .sel(), do NOT mix slice objects (e.g. slice(a,b)) with method='nearest'. Split them into two separate .sel() calls if needed.
7. DO NOT use reduction operations (.mean(), .sum(), .std(), etc.) unless the user explicitly asks for it like "mean", "average", "total", or "summary". Preserve the spatial/temporal dimensions requested.
"""

OUTPUT_FORMAT = """
=== OUTPUT FORMAT ===
Return ONLY raw Python code. NO markdown, NO code fences, NO explanation text.
"""

SYSTEM_PROMPT = """You are an expert Python software engineer.

{data_type_context}

=== AVAILABLE DATA VARIABLES ===
{var_names}

{vars_info}

=== COORDINATES (dimensions) ===
{coords_info}

{additional_context}

=== USER REQUEST ===
{user_request}

{critical_rules}
{data_access_hint}

{output_format}
"""

ERROR_CORRECTION_PROMPT = """You are an expert Python software engineer. 
Your previous code failed to execute. You MUST analyze the error message and modify the code to fix it. 

=== ANALYSIS TASK ===
1. Carefully read the ERROR MESSAGE below.
2. Identify why the PREVIOUS CODE triggered this specific error.
3. Rewrite the code to accomplish the USER REQUEST while satisfying all CRITICAL RULES and avoiding the previous error.

{data_type_context}

=== AVAILABLE DATA VARIABLES ===
{var_names}

{vars_info}

=== COORDINATES (dimensions) ===
{coords_info}

{additional_context}

User request: {user_request}

{critical_rules}
{data_access_hint}

{output_format}

=== PREVIOUS CODE THAT FAILED ===
```python
{previous_code}
```

=== ERROR MESSAGE ===
{error_message}

=== REQUIRED ACTION ===
Provide the corrected Python code that fixes the error above. 
Do not repeat the same mistake.
Fixed code:"""


# Domain-specific hints for common operations
HINTS = {
    "gradient": """
For computing gradients:
- Use .diff(dim) to form the numerator (finite difference). A derivative MUST be da.diff(dim) / coord.diff(dim) (or /dx, /dy for lon/lat).
- DO NOT use np.gradient on DataArrays directly
- Handle edge cases appropriately
""",
}


def get_hint_for_request(user_request: str) -> str:
    """
    Get domain-specific hint based on user request keywords.
    
    Args:
        user_request: The user's natural language request
        
    Returns:
        Relevant hint string or empty string if no match
    """
    request_lower = user_request.lower()
    
    hints_to_apply = []
    for keyword, hint in HINTS.items():
        if keyword in request_lower:
            hints_to_apply.append(hint)
    
    return "\n".join(hints_to_apply)


SUMMARY_PROMPT = """You are a helpful data science assistant.
Provide a very brief (1-2 sentences) summary of what this Python code did to the xarray data.
Focus on the transformation performed and the resulting variable.

SUCCESSFUL CODE:
```python
{code}
```

SUMMARY:"""
