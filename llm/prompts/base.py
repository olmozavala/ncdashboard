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

=== CRITICAL RULES ===
1. Store result in variable 'output' (MUST be xarray DataArray)
2. Use ONLY 'data', 'xr', 'np' - NO imports allowed
3. Use .diff('DimensionName') for derivatives (positional arg, NOT dim= keyword)
4. Use .sel(Coord=value, method='nearest') for coordinate selection - values rarely match exactly
5. Handle NaN with skipna=True

=== OUTPUT FORMAT ===
Return ONLY raw Python code. NO markdown, NO code fences, NO explanation text.
BAD: ```python\ncode\n```
BAD: Here is the code:\ncode
GOOD: output = data['var'].mean('MT')

Python code:"""


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
- Vorticity = dv/dx - du/dy (u=eastward velocity, v=northward velocity)  
- Find the velocity variable names from the AVAILABLE DATA VARIABLES section
- Use .diff('Longitude') and .diff('Latitude') for derivatives (positional arg, not keyword)
- The dimension names are: MT (time), Depth, Latitude, Longitude
- DO NOT use groupby for differentiation
- Example code structure:
  u = data['u']  # replace with actual eastward velocity variable name
  v = data['v']  # replace with actual northward velocity variable name
  dv_dx = v.diff('Longitude')
  du_dy = u.diff('Latitude')
  output = (dv_dx - du_dy).isel(Depth=0).mean('MT')  # Select one depth and average over time
""",

    "transect": """
For creating transects/slices along coordinates:
- Use .sel() with method='nearest' for exact locations
- Use .sel() with slice() for ranges
- Example for longitude range at fixed latitude:
  output = data['temp'].sel(Latitude=24, method='nearest').sel(Longitude=slice(-90, -85))
- For a transect along a line, select a slice and keep remaining dimensions
""",

    "slice": """
For slicing data along coordinates:
- Use .sel() with exact values or slice()
- Use method='nearest' when exact coordinate value may not exist
- Example: data['temp'].sel(Longitude=-90, method='nearest')
- For ranges: data.sel(Longitude=slice(-90, -85))
""",

    "unit_conversion": """
For temperature unit conversions:
- Kelvin to Celsius: T_C = T_K - 273.15
- Fahrenheit to Celsius: T_C = (T_F - 32) * 5/9
- Preserve all metadata and coordinates
""",

    "gradient": """
For computing gradients:
- Use .diff(dim='dimension_name') for derivatives along a dimension
- DO NOT use np.gradient on DataArrays directly
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
