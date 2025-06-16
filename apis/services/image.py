"""
Image Services Module

This module provides services for generating visualization images from dataset data.
It handles the creation of heatmap visualizations using Plotly for geographical data.
"""

import os
import xarray as xr
import plotly.graph_objects as go
from utils import DATA_DIR, load_data
from models import (
    GenerateImageRequest4D,
    GenerateImageRequest1D,
    GenerateImageRequest3D,
)
from utils import select_colormap, get_all_coords
from services.db import nc_db

def generate_image_1d(params: GenerateImageRequest1D):
    # data = xr.open_dataset(os.path.join(DATA_DIR, dataset), decode_times=False)
    dataset = nc_db.get_dataset_by_id(params.dataset_id)
    if not dataset:
        raise ValueError(f"Dataset with ID {params.dataset_id} not found.")
    data_files = os.listdir(dataset["path"])
    data_files = [os.path.join(dataset["path"], f) for f in data_files if f.endswith(".nc")]
    data = load_data(data_files)
    data_to_visualize = data[params.variable]

    profile = data_to_visualize.values

    figure = go.Figure(
        data=[go.Scatter(x=list(range(len(profile))), y=profile, mode="lines+markers")],
        layout=go.Layout(
            title_x=0.5,
            height=350,
            xaxis=dict(visible=False, showticklabels=False, title=""),
            yaxis=dict(visible=False, showticklabels=False, title=""),
            margin=dict(
                l=0,  # left margin
                r=0,  # right margin
                b=0,  # bottom margin
                t=0,  # top margin
                pad=0,  # padding
            ),
        ),
    )

    # Convert to PNG image
    image_data = figure.to_image(format="png")

    return image_data


def generate_image(params: GenerateImageRequest4D):
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
    dataset = nc_db.get_dataset_by_id(params.dataset_id)
    if not dataset:
        raise ValueError(f"Dataset with ID {params.dataset_id} not found.")
    data_files = os.listdir(dataset["path"])
    data_files = [os.path.join(dataset["path"], f) for f in data_files if f.endswith(".nc")]
    data = load_data(data_files)
    data_to_visualize = data[params.variable]
    times, zaxis, lats, lons = get_all_coords(data_to_visualize)
    # Extract data for the specified indices
    z_data = data_to_visualize[params.time_index, params.depth_index, :, :]

    # Create heatmap figure
    fig = go.Figure(
        data=[
            go.Heatmap(
                z=z_data,
                x=lons.values,  # Longitude on x-axis
                y=lats.values,  # Latitude on y-axis
                colorscale=select_colormap(params.variable),
                showscale=True,
            )
        ],
        layout=go.Layout(
            title="Hycom GOM",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        ),
    )

    # Hide color scale for cleaner visualization
    fig.update_traces(showscale=False)

    # Convert to PNG image
    image_data = fig.to_image(format="png")

    return image_data


def generate_image_3D(params: GenerateImageRequest3D):
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
    dataset = nc_db.get_dataset_by_id(params.dataset_id)
    if not dataset:
        raise ValueError(f"Dataset with ID {params.dataset_id} not found.")
    data_files = os.listdir(dataset["path"])
    data_files = [os.path.join(dataset["path"], f) for f in data_files if f.endswith(".nc")]
    data = load_data(data_files)
    data_to_visualize = data[params.variable]

    # Extract data for the specified time index (all depths)
    z_data = data_to_visualize[params.time_index, :, :]  # shape: (depth, lat, lon)
    times, _, lats, lons = get_all_coords(data_to_visualize)

    # Create 3D surface plot
    fig = go.Figure(
        data=[
            go.Heatmap(
                z=z_data,
                x=lons,
                y=lats,
                colorscale=select_colormap(params.variable),
                showscale=True,
            )
        ],
        layout=go.Layout(
            title="Hycom GOM",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        ),
    )
    # Hide color scale for cleaner visualization
    fig.update_traces(showscale=False)

    # Convert to PNG image
    image_data = fig.to_image(format="png")

    return image_data
