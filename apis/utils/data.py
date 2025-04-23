"""
Data Utility Module

This module provides utility functions for working with xarray datasets.
It includes functions for coordinate extraction and data loading.
"""

import xarray as xr
import plotly.graph_objects as go
import numpy as np

def get_all_coords(data: xr.DataArray) -> tuple[xr.DataArray, xr.DataArray, xr.DataArray, xr.DataArray]:
    """
    Extract coordinate arrays from an xarray DataArray.
    
    This function attempts to identify and extract time, depth, latitude, and longitude
    coordinates from the input data based on the number of coordinates present.
    
    Args:
        data (xr.DataArray): Input data array to extract coordinates from
        
    Returns:
        tuple: A tuple containing (times, depth, lats, lons) where each is an xarray DataArray
        
    Note:
        The function makes assumptions about coordinate ordering:
        - For 1 coordinate: assumes it's longitude
        - For 2 coordinates: assumes they're latitude and longitude
        - For 3 coordinates: assumes they're time, latitude, and longitude
        - For 4 coordinates: assumes they're time, depth, latitude, and longitude
    """
    coords = list(data.coords.keys())
    
    # Initialize empty arrays for each coordinate type
    lats = xr.DataArray(np.empty((0, 0)))
    lons = xr.DataArray(np.empty((0, 0)))
    times = xr.DataArray(np.empty((0, 0)))
    depth = xr.DataArray(np.empty((0, 0)))

    # Extract coordinates based on their count
    if len(coords) == 1:  # Assume only longitude
        lons = data[coords[0]]

    if len(coords) >= 2:  # Assume latitude and longitude
        lats = data[coords[-2]]
        lons = data[coords[-1]]

    if len(coords) >= 3:  # Assume time, latitude, longitude
        times = data[coords[0]]

    if len(coords) == 4:  # Assume time, depth, latitude, longitude
        depth = data[coords[1]]

    return times, depth, lats, lons

def load_data() -> xr.Dataset:
    """
    Load a sample dataset for testing and development.
    
    Returns:
        xr.Dataset: The loaded dataset with times not decoded
        
    Note:
        This is a development function and should be replaced with proper data loading
        in production code.
    """
    return xr.open_dataset("../data/gom_t007.nc", decode_times=False)

# Example usage (commented out)
# data = load_data()
# times, zaxis, lats, lons = get_all_coords(data["water_u"][0,:,:,0])
# z_data = data["water_u"][0,0,:,:]
# 
# fig = go.Figure(
#     data=[go.Heatmap(
#         z=z_data,
#         x=lats.values,
#         y=lons.values,
#         colorscale='Viridis',
#         showscale=True,
#     )],
#     layout=go.Layout(
#         title="Hycom GOM",
#         xaxis_title="Longitude",
#         yaxis_title="Latitude",
#     )
# )
# 
# fig.show()
