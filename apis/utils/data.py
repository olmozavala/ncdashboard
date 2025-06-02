"""
Data Utility Module

This module provides utility functions for working with xarray datasets.
It includes functions for coordinate extraction and data loading.
"""

import xarray as xr
import plotly.graph_objects as go
import numpy as np
from typing import List

def load_data(paths:List[str]) -> xr.Dataset:
    """
    Load a sample dataset for testing and development.
    
    Returns:
        xr.Dataset: The loaded dataset with times not decoded
        
    Note:
        This is a development function and should be replaced with proper data loading
        in production code.
    """
    return xr.open_mfdataset(paths, decode_times=False, engine='netcdf4')

def get_all_coords(data):
    '''
    This method returns the coordinates for a given data 
    '''
    coords =  list(data.coords.keys())
    # Assume the last 2 are the spatial coordinates 
    lats = xr.DataArray(np.empty((0, 0)))
    lons = xr.DataArray(np.empty((0, 0)))
    times = xr.DataArray(np.empty((0, 0)))
    depth = xr.DataArray(np.empty((0, 0)))

    if len(coords) == 1: # In this case we assume we have time, z, lat, lon
        lons = data[coords[0]]

    if len(coords) >= 2: # In this case we assume we have time, z, lat, lon
        lats = data[coords[-2]]
        lons = data[coords[-1]]

    # TODO this should be something smarter, based on the names of the coordinates
    if len(coords) >= 3: # In this case we assume we have time, z, lat, lon
        times = data[coords[0]]

    if len(coords) == 4: # In this case we assume we have time, z, lat, lon
        depth = data[coords[1]]

    return times, depth, lats, lons

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
