"""
Request Models Module

This module defines the data models for API requests in the application.
It provides type definitions for various request payloads using Pydantic models.
"""

from pydantic import BaseModel, Field

class GenerateImageRequest1D(BaseModel):
    """
    Request payload for generating a new visualization image.
    
    Attributes:
        dataset_id (str): ID of the dataset to visualize
    """
    dataset_id: str = Field(..., description="ID of the dataset to visualize")
    variable: str = Field(..., description="The variable to visualize")

class GenerateImageRequest4D(GenerateImageRequest1D):
    lat_var: str = Field(..., description="The latitude variable to visualize")
    lon_var: str = Field(..., description="The longitude variable to visualize")
    time_index: int = Field(..., description="Index for the time dimension")
    depth_index: int = Field(..., description="Index for the depth dimension")
    
class GenerateImageRequest3D(GenerateImageRequest1D):
    lat_var: str = Field(..., description="The latitude variable to visualize")
    lon_var: str = Field(..., description="The longitude variable to visualize")
    time_index: int = Field(..., description="Index for the time dimension")
    
