"""
Session Models Module

This module defines the data models for session management in the application.
It provides type definitions for session parameters and session objects.
"""

from typing import TypedDict, Optional
from .image import Image
from .cache import CachedDataset

class SessionParams(TypedDict):
    """
    Parameters for a session's visualization settings.
    
    Attributes:
        colorspace (str): The color space to use for visualization
        variable (str): The variable being visualized
    """
    colorspace: str
    variable: str

class Session(TypedDict):
    """
    A session object representing a user's visualization session.
    
    Attributes:
        id (str): Unique identifier for the session
        parent_id (Optional[str]): ID of the parent session if this is a child session
        created_at (str): Timestamp of when the session was created
        dataset_id (str): ID of the dataset associated with this session
        params (list[SessionParams]): List of visualization parameters for the session
        cache (Optional[CachedDataset]): Cached data associated with the session
    """
    id: str
    parent_id: Optional[str]
    created_at: str
    dataset_id: str
    params: list[SessionParams]
    cache: Optional[CachedDataset]