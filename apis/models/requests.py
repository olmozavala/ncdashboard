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
    
class GenerateImageRequestTransect(GenerateImageRequest1D):
    """
    Request payload for generating a transect visualization image.

    Attributes:
        dataset_id (str): ID of the dataset to visualize
        variable (str): Variable to visualize
        start_lat (float): Latitude of the transect start point
        start_lon (float): Longitude of the transect start point
        end_lat (float): Latitude of the transect end point
        end_lon (float): Longitude of the transect end point
        time_index (int): Index for the time dimension
        depth_index (int): Index for the depth dimension
    """
    start_lat: float = Field(..., description="Latitude of the transect start point")
    start_lon: float = Field(..., description="Longitude of the transect start point")
    end_lat: float = Field(..., description="Latitude of the transect end point")
    end_lon: float = Field(..., description="Longitude of the transect end point")
    time_index: int = Field(..., description="Index for the time dimension")
    depth_index: int = Field(..., description="Index for the depth dimension")
    invert_y_axis: bool = Field(False, description="If True, invert the Y axis so it starts at zero at the top of the image")
