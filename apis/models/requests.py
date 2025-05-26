"""
Request Models Module

This module defines the data models for API requests in the application.
It provides type definitions for various request payloads.
"""

from typing import TypedDict

class GenerateImageRequest(TypedDict):
    """
    Request payload for generating a new visualization image.
    
    Attributes:
        dataset (str): ID of the dataset to visualize
        time_index (int): Index of the time dimension to use
        depth_index (int): Index of the depth dimension to use
        variable (str): The variable to visualize
    """
    dataset_id: str
    time_index: int
    depth_index: int
    variable: str
    
class GenerateImage3DRequest(TypedDict):
    """
    Request payload for generating a 3D visualization image.
    
    Attributes:
        dataset (str): ID of the dataset to visualize
        time_index (int): Index of the time dimension to use
        depth_index (int): Index of the depth dimension to use
        variable (str): The variable to visualize
        view (str): The view type for the 3D visualization
    """
    dataset_id: str
    time_index: int
    variable: str