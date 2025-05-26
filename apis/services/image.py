"""
Image Services Module

This module provides services for generating visualization images from dataset data.
It handles the creation of heatmap visualizations using Plotly for geographical data.
"""

import os
import xarray as xr
import plotly.graph_objects as go
from utils.constants import DATA_DIR

def generate_image(dataset, time_index, depth_index, variable="water_u", data=None):
    """
    Generate a heatmap visualization from dataset data.
    
    Args:
        dataset (str): Name of the dataset file
        time_index (int): Index for the time dimension
        depth_index (int): Index for the depth dimension
        variable (str, optional): Variable to visualize. Defaults to "water_u"
        data (xarray.Dataset, optional): Pre-loaded dataset. If None, dataset will be loaded from file.
        
    Returns:
        bytes: PNG image data of the visualization
        
    Note:
        The visualization is created as a heatmap with:
        - Longitude on x-axis
        - Latitude on y-axis
        - Viridis colorscale
        - Clean layout with no axes or margins
    """
    # Load dataset if not provided
    data = xr.open_dataset(os.path.join(DATA_DIR, dataset), decode_times=False) if data is None else data
    
    # Extract data for the specified indices
    z_data = data[variable][time_index, depth_index, :, :]
    lats = data["lat"]
    lons = data["lon"]

    # Create heatmap figure
    fig = go.Figure(
        data=[go.Heatmap(
            z=z_data, 
            x=lons.values,  # Longitude on x-axis
            y=lats.values,  # Latitude on y-axis
            colorscale='Viridis',
            showscale=True,
        )],
        layout=go.Layout(
            title="Hycom GOM",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
    )
     
    # Hide color scale for cleaner visualization
    fig.update_traces(showscale=False)

    # Convert to PNG image
    image_data = fig.to_image(format="png")

    return image_data


def generate_image_3D(dataset, time_index, variable="water_u", data=None):
    """
    Generate a 3D surface visualization image from dataset data.
    
    Args:
        dataset (str): Name of the dataset file
        time_index (int): Index for the time dimension
        variable (str, optional): Variable to visualize. Defaults to "water_u"
        data (xarray.Dataset, optional): Pre-loaded dataset. If None, dataset will be loaded from file.
        
    Returns:
        bytes: PNG image data of the 3D visualization
    """
    # Load dataset if not provided
    data = xr.open_dataset(os.path.join(DATA_DIR, dataset), decode_times=False) if data is None else data
    

    # Extract data for the specified time index (all depths)
    z_data = data[variable][time_index, :, :]  # shape: (depth, lat, lon)
    lats = data["lat"]
    lons = data["lon"]

    # Create 3D surface plot
    fig = go.Figure(
        data=[go.Heatmap(
            z=z_data,
            x=lons.values,
            y=lats.values,
            colorscale='Viridis',
            showscale=True,
        )],
        layout=go.Layout(
            title="Hycom GOM",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
    )
    # Hide color scale for cleaner visualization
    fig.update_traces(showscale=False)

    # Convert to PNG image
    image_data = fig.to_image(format="png")

    return image_data
