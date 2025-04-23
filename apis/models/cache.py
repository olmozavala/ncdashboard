"""
Cache Models Module

This module defines the data models for the application's caching system.
It provides type definitions for cached datasets and the cache index structure.
"""

from typing import TypedDict
from .image import Image 

class CachedDataset(TypedDict):
    """
    A cached dataset object containing pre-generated visualizations.
    
    Attributes:
        id (str): Unique identifier for the cached dataset
        name (str): Human-readable name of the dataset
        description (str): Description of the dataset
        created_at (str): Timestamp of when the cache was created
        images (list[Image]): List of pre-generated images for the dataset
    """
    id: str
    name: str
    description: str
    created_at: str
    images: list[Image]

class CacheIndex(TypedDict):
    """
    The cache index structure containing all cached datasets.
    
    Attributes:
        cache (list[CachedDataset]): List of all cached datasets
    """
    cache: list[CachedDataset]