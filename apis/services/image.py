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
from models.requests import GenerateImageRequestTransect
import numpy as np

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


def haversine_distance(lat1, lon1, lat2, lon2):
    """Compute haversine distance between two (lat, lon) points in kilometers."""
    R = 6371.0  # Earth radius in kilometers
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c


def generate_transect_image(params: GenerateImageRequestTransect):
    """Generate a transect plot between two points and return PNG bytes.

    The function samples the selected variable along a straight line between
    two geographic points (start_lat/lon and end_lat/lon) for the provided
    time and depth indices.

    Args:
        params (GenerateImageRequestTransect): Parameters for transect generation.

    Returns:
        bytes: PNG image bytes containing the transect plot.
    """
    # Retrieve dataset metadata and load data
    dataset_meta = nc_db.get_dataset_by_id(params.dataset_id)
    if not dataset_meta:
        raise ValueError(f"Dataset with ID {params.dataset_id} not found.")

    data_files = [
        os.path.join(dataset_meta["path"], f)
        for f in os.listdir(dataset_meta["path"])
        if f.endswith(".nc")
    ]
    data = load_data(data_files)

    # Extract the variable data
    data_var = data[params.variable]

    # Select only the requested time index; keep **all** depths for heat-map
    time_dim = str(data_var.dims[0])
    depth_dim = str(data_var.dims[1])
    lat_dim = str(data_var.dims[-2])
    lon_dim = str(data_var.dims[-1])

    slice_3d = data_var.isel({time_dim: params.time_index})  # (depth, lat, lon)

    # Number of points along the transect for sampling/interpolation
    NUM_POINTS = 250
    lat_points = np.linspace(params.start_lat, params.end_lat, NUM_POINTS)
    lon_points = np.linspace(params.start_lon, params.end_lon, NUM_POINTS)

    # Interpolate values along the line for **all** depths at once.  This returns
    # a DataArray with shape (depth, points)
    transect_da = slice_3d.interp(
        {
            lat_dim: xr.DataArray(lat_points, dims="points"),
            lon_dim: xr.DataArray(lon_points, dims="points"),
        },
        method="linear",
    )

    transect_vals = transect_da.values  # ndarray (depth, points)

    # Depth values to use for y-axis (if coordinate not present, use indices)
    if depth_dim in transect_da.coords:
        depth_vals = transect_da.coords[depth_dim].values
    else:
        depth_vals = np.arange(transect_vals.shape[0])

    # Compute cumulative distance along the transect for x-axis (km)
    distances_km = [0.0]
    for i in range(1, NUM_POINTS):
        d = haversine_distance(
            lat_points[i - 1], lon_points[i - 1], lat_points[i], lon_points[i]
        )
        distances_km.append(distances_km[-1] + d)

    # Build Plotly heat-map figure
    fig = go.Figure(
        data=[
            go.Heatmap(
                z=transect_vals,
                x=distances_km,
                y=depth_vals,
                colorscale=select_colormap(params.variable),
                reversescale=True,  # Typically depth increases downward
            )
        ],
        layout=go.Layout(
            title="Transect Heatmap",
            xaxis_title="Distance along transect (km)",
            yaxis_title="Depth",
            margin=dict(l=40, r=20, t=40, b=40),
            template="plotly_dark",
        ),
    )

    # Hide color bar for consistency with other images
    fig.update_traces(showscale=False)

    # Return PNG bytes
    return fig.to_image(format="png")
