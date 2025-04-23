"""
Image Models Module

This module defines the data models for image management in the application.
It provides type definitions for image objects used in visualization.
"""

from typing import TypedDict, Optional

class Image(TypedDict):
    """
    An image object representing a generated visualization.
    
    Attributes:
        id (str): Unique identifier for the image
        dataset_id (str): ID of the dataset this image represents
        variable (str): The variable being visualized
        file_path (str): Path to the image file
        created_at (str): Timestamp of when the image was created
        color_map (Optional[str]): The color map used for visualization
    """
    id: str
    dataset_id: str
    variable: str
    file_path: str
    created_at: str
    color_map: Optional[str]