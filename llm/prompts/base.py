"""
Base prompt templates for LLM code generation.

These prompts instruct the LLM on how to generate Python code that
operates on xarray data structures.
"""

CRITICAL_RULES = """
=== CRITICAL RULES ===
1. Store result in variable 'output' (MUST be xarray DataArray)
2. Use ONLY 'data', 'xr', 'np' - NO imports allowed
3. Use .diff(dim) to form the numerator (finite difference). A derivative MUST be da.diff(dim) / coord.diff(dim) (or /dx, /dy for lon/lat).
4. Use .sel(Coord=value, method='nearest') for coordinate selection - values rarely match exactly
5. Handle NaN with skipna=True
6. Access variables using data['variable_name']
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

ERROR_CORRECTION_PROMPT = """You are an expert Python software engineer. Your previous code failed to execute.

{data_type_context}

=== AVAILABLE DATA VARIABLES ===
{var_names}

{vars_info}

=== COORDINATES (dimensions) ===
{coords_info}

{additional_context}

User request: {user_request}

PREVIOUS CODE THAT FAILED:
```python
{previous_code}
```

ERROR MESSAGE:
{error_message}

{output_format}
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
