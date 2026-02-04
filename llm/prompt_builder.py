"""
Prompt builder for LLM-based xarray analysis.

Constructs prompts with xarray metadata (variables, shapes, units, coordinates)
to help LLMs generate accurate Python code.
"""

import xarray as xr
from typing import Optional
from .prompts.base import SYSTEM_PROMPT, ERROR_CORRECTION_PROMPT, CRITICAL_RULES, OUTPUT_FORMAT


class PromptBuilder:
    """Builds prompts for LLM code generation from xarray data."""
    
    def __init__(self, data: xr.DataArray | xr.Dataset):
        """
        Initialize with xarray data.
        
        Args:
            data: xarray DataArray or Dataset to analyze
        """
        self.data = data
    
    def _format_list(self, items: list[str]) -> str:
        """Format list as 'a, b and c'."""
        if len(items) > 1:
            return ', '.join(items[:-1]) + ' and ' + items[-1]
        elif items:
            return items[0]
        return ''
    
    def _get_variables_info(self) -> tuple[list[str], str]:
        """
        Extract detailed variable information from data.
        
        Returns:
            Tuple of (variable names list, formatted info text)
        """
        if isinstance(self.data, xr.Dataset):
            var_names = list(self.data.data_vars)
            vars_info = {}
            for var in var_names:
                da = self.data[var]
                vars_info[var] = {
                    'dims': da.dims,
                    'shape': da.shape,
                    'units': da.attrs.get('units', 'unknown'),
                }
        else:
            # DataArray
            var_names = [self.data.name or 'data']
            vars_info = {
                var_names[0]: {
                    'dims': self.data.dims,
                    'shape': self.data.shape,
                    'units': self.data.attrs.get('units', 'unknown'),
                }
            }
        
        # Format as detailed text
        info_lines = []
        for var, info in vars_info.items():
            dims_str = ', '.join([f"{d}={s}" for d, s in zip(info['dims'], info['shape'])])
            info_lines.append(
                f"  - '{var}': dims=({dims_str}), units='{info['units']}'"
            )
        
        return var_names, '\n'.join(info_lines)
    
    def _get_coordinates_info(self) -> str:
        """Get detailed coordinate information with shapes."""
        coord_lines = []
        for coord_name in self.data.coords:
            coord = self.data.coords[coord_name]
            try:
                if coord.size > 0:
                    min_val = float(coord.min())
                    max_val = float(coord.max())
                    coord_lines.append(
                        f"  - '{coord_name}': shape={coord.shape}, range=[{min_val:.4g}, {max_val:.4g}]"
                    )
                else:
                    coord_lines.append(f"  - '{coord_name}': shape={coord.shape}")
            except (TypeError, ValueError):
                # Non-numeric coordinate (e.g., datetime)
                coord_lines.append(f"  - '{coord_name}': shape={coord.shape}, dtype={coord.dtype}")
        return '\n'.join(coord_lines) if coord_lines else 'No coordinates'
    
    def _get_coordinate_ranges(self) -> str:
        """Get coordinate value ranges for context (legacy method)."""
        ranges = []
        for coord_name in self.data.coords:
            coord = self.data.coords[coord_name]
            if coord.size > 0:
                try:
                    min_val = float(coord.min())
                    max_val = float(coord.max())
                    ranges.append(f"{coord_name}: [{min_val:.2f}, {max_val:.2f}]")
                except (TypeError, ValueError):
                    # Non-numeric coordinate
                    ranges.append(f"{coord_name}: {coord.size} values")
        return ', '.join(ranges) if ranges else 'No coordinate ranges available'
    
    def build_prompt(self, user_request: str, additional_context: str = "") -> str:
        """
        Build a complete prompt for LLM code generation.
        
        Args:
            user_request: Natural language request from user
            additional_context: Optional extra context (e.g., hints, constraints)
        
        Returns:
            Formatted prompt string
        """
        var_names, vars_info_text = self._get_variables_info()
        coords_info = self._get_coordinates_info()
        
        # Determine data type and provide appropriate context
        if isinstance(self.data, xr.Dataset):
            data_type_context = "You have an xarray Dataset named 'data' with multiple variables."
            data_access_hint = "\n6. Access variables using data['variable_name']"
        else:
            # DataArray
            data_type_context = "You have an xarray DataArray named 'data'."
            data_access_hint = "\n6. Work directly with 'data' - it's already a single variable (DataArray)"
        
        prompt = SYSTEM_PROMPT.format(
            data_type_context=data_type_context,
            var_names=self._format_list(var_names),
            vars_info=vars_info_text,
            coords_info=coords_info,
            user_request=user_request,
            additional_context=additional_context,
            data_access_hint=data_access_hint,
            critical_rules=CRITICAL_RULES,
            output_format=OUTPUT_FORMAT,
        )
        
        return prompt
    
    def build_error_correction_prompt(
        self, 
        user_request: str, 
        previous_code: str, 
        error_message: str
    ) -> str:
        """
        Build a prompt for error correction after failed execution.
        
        Args:
            user_request: Original user request
            previous_code: The code that failed
            error_message: Error message from execution
        
        Returns:
            Formatted error correction prompt
        """
        var_names, vars_info_text = self._get_variables_info()
        
        prompt = ERROR_CORRECTION_PROMPT.format(
            var_names=self._format_list(var_names),
            vars_info=vars_info_text,
            user_request=user_request,
            previous_code=previous_code,
            error_message=error_message,
            data_type_context=data_type_context,
            data_access_hint=data_access_hint,
            critical_rules=CRITICAL_RULES,
            output_format=OUTPUT_FORMAT,
        )
        
        return prompt
