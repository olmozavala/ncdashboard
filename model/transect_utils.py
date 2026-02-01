"""
Transect Utilities

This module provides utility functions for extracting data along a transect line.
A transect is a cross-section of data along a user-drawn path across the spatial
dimensions (lat/lon).

Output dimensionality depends on input:
- 2D input (lat, lon) → 1D output (distance)
- 3D input (time/depth, lat, lon) → 2D output (coord, distance)
- 4D input (time, depth, lat, lon) → 3D output (time, depth, distance)
"""

import numpy as np
import xarray as xr
from loguru import logger


def compute_path_points(xs: np.ndarray, ys: np.ndarray, num_points: int = 100) -> tuple:
    """
    Compute evenly spaced points along a polyline path.
    
    Args:
        xs: X coordinates (longitude) of path vertices
        ys: Y coordinates (latitude) of path vertices
        num_points: Number of sample points to generate along the path
        
    Returns:
        tuple: (lons, lats, distances) where:
            - lons: Interpolated longitude values
            - lats: Interpolated latitude values  
            - distances: Cumulative distance along path (in coordinate units)
    """
    xs = np.asarray(xs)
    ys = np.asarray(ys)
    
    if len(xs) < 2:
        raise ValueError("Path must have at least 2 vertices")
    
    # Compute segment lengths using Euclidean distance (acceptable for small areas)
    dx = np.diff(xs)
    dy = np.diff(ys)
    segment_lengths = np.sqrt(dx**2 + dy**2)
    
    # Cumulative distance along path
    cumulative_dist = np.concatenate([[0], np.cumsum(segment_lengths)])
    total_length = cumulative_dist[-1]
    
    if total_length == 0:
        raise ValueError("Path has zero length")
    
    # Generate evenly spaced distances
    target_distances = np.linspace(0, total_length, num_points)
    
    # Interpolate x and y coordinates at target distances
    interp_xs = np.interp(target_distances, cumulative_dist, xs)
    interp_ys = np.interp(target_distances, cumulative_dist, ys)
    
    return interp_xs, interp_ys, target_distances


def extract_transect(data: xr.DataArray, path_xs: list, path_ys: list,
                     num_points: int = 100) -> xr.DataArray:
    """
    Extract data values along a drawn path (transect).
    
    The function interpolates the data at evenly spaced points along the path
    and returns a new DataArray with 'distance' replacing the spatial dimensions.
    
    Args:
        data: xr.DataArray with 2D, 3D, or 4D dimensions.
              Expected dimension order: [..., lat, lon] (spatial dims last)
        path_xs: X coordinates (longitude) of path vertices
        path_ys: Y coordinates (latitude) of path vertices
        num_points: Number of sample points along the transect (default: 100)
        
    Returns:
        xr.DataArray with dimensions:
        - 2D input → 1D output: (distance,)
        - 3D input → 2D output: (coord, distance) 
        - 4D input → 3D output: (time, depth, distance)
        
    Raises:
        ValueError: If path has fewer than 2 vertices or zero length
    """
    path_xs = np.asarray(path_xs)
    path_ys = np.asarray(path_ys)
    
    logger.info(f"Extracting transect: {len(path_xs)} vertices, {num_points} sample points")
    logger.debug(f"Path X range: [{path_xs.min():.2f}, {path_xs.max():.2f}]")
    logger.debug(f"Path Y range: [{path_ys.min():.2f}, {path_ys.max():.2f}]")
    
    # Compute interpolation points along path
    interp_lons, interp_lats, distances = compute_path_points(path_xs, path_ys, num_points)
    
    # Get dimension names - assume last two are spatial (lat, lon)
    dims = list(data.dims)
    if len(dims) < 2:
        raise ValueError(f"Data must have at least 2 dimensions, got {len(dims)}")
    
    lat_dim = dims[-2]
    lon_dim = dims[-1]
    
    logger.debug(f"Data dims: {dims}, lat_dim={lat_dim}, lon_dim={lon_dim}")
    
    # Create xarray DataArrays for interpolation coordinates
    # The 'distance' dimension will be the new coordinate
    interp_lons_da = xr.DataArray(interp_lons, dims=['distance'])
    interp_lats_da = xr.DataArray(interp_lats, dims=['distance'])
    
    # Interpolate data at path points
    # Using xarray's advanced interpolation with vector coordinates
    transect_data = data.interp(
        {lon_dim: interp_lons_da, lat_dim: interp_lats_da},
        method='linear'
    )
    
    # Add distance as a proper coordinate
    transect_data = transect_data.assign_coords(distance=distances)
    
    # Add useful attributes
    transect_data.attrs['transect_path_xs'] = path_xs.tolist()
    transect_data.attrs['transect_path_ys'] = path_ys.tolist()
    transect_data.attrs['transect_num_points'] = num_points
    
    # Copy relevant attributes from original data
    for attr in ['long_name', 'units', 'standard_name']:
        if attr in data.attrs:
            transect_data.attrs[attr] = data.attrs[attr]
    
    logger.info(f"Transect extracted: output shape {transect_data.shape}, dims {transect_data.dims}")
    
    return transect_data


def get_transect_title(parent_title: str, start_point: tuple, end_point: tuple) -> str:
    """
    Generate a descriptive title for a transect plot.
    
    Args:
        parent_title: Title of the parent plot
        start_point: (lon, lat) of transect start
        end_point: (lon, lat) of transect end
        
    Returns:
        Formatted title string
    """
    return (f"{parent_title} Transect: "
            f"({start_point[0]:.2f}, {start_point[1]:.2f}) → "
            f"({end_point[0]:.2f}, {end_point[1]:.2f})")
