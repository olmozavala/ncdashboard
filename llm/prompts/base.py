"""
Base prompt templates for LLM code generation.

These prompts instruct the LLM on how to generate Python code that
operates on xarray data structures.
"""

SYSTEM_PROMPT = """You are an expert Python software engineer. You have an xarray object named 'data' (either DataArray or Dataset).

=== AVAILABLE DATA VARIABLES ===
{var_names}

{vars_info}

=== COORDINATES (dimensions) ===
{coords_info}

{additional_context}

=== USER REQUEST ===
{user_request}

=== RULES ===
1. The output MUST be stored in a variable called 'output'
2. 'output' MUST be an xarray DataArray (not Dataset)
3. Use ONLY xarray and numpy libraries (available as 'xr' and 'np')
4. To access a variable from a Dataset, use data['variable_name']
5. To compute mean along a dimension, use .mean(dim='dim_name')
6. Provide ONLY Python code - no imports, no comments, no explanations
7. Handle potential NaN values with skipna=True where appropriate

Provide Python code:"""


ERROR_CORRECTION_PROMPT = """You are an expert Python software engineer. Your previous code failed to execute.

Available variables: {var_names}

Variable details: {vars_info}

User request: {user_request}

PREVIOUS CODE THAT FAILED:
```python
{previous_code}
```

ERROR MESSAGE:
{error_message}

Please fix the code. Remember:
1. Output MUST be stored in 'output' as an xarray DataArray
2. Use only 'xr' (xarray) and 'np' (numpy)
3. 'data' contains the input xarray object
4. Provide ONLY the corrected Python code, no comments or explanations

Fixed code:"""


# Domain-specific hints for common operations
HINTS = {
    "vorticity": """
For vorticity calculations on a lat/lon grid:
- Use proper spherical geometry: dx = dlon * R * cos(lat), dy = dlat * R
- Earth radius R ≈ 6371000 meters
- Vorticity = dv/dx - du/dy (where u=eastward, v=northward velocity)
- Use xr.DataArray.diff() for derivatives
""",

    "unit_conversion": """
For temperature unit conversions:
- Kelvin to Celsius: T_C = T_K - 273.15
- Fahrenheit to Celsius: T_C = (T_F - 32) * 5/9
- Preserve all metadata and coordinates
""",

    "gradient": """
For computing gradients:
- Use np.gradient() or xr.DataArray.diff()
- Account for coordinate spacing
- Handle edge cases appropriately
""",

    "mean": """
For computing means:
- Use .mean(dim='dimension_name') for averaging along specific dimensions
- Use .mean() for global mean
- Consider using skipna=True to handle NaN values
""",

    "anomaly": """
For computing anomalies:
- Anomaly = value - climatological_mean
- Use .groupby('time.month').mean() for monthly climatology
- Or use simple mean subtraction: data - data.mean(dim='time')
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
