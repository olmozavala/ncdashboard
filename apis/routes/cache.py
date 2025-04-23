"""
Cache Routes Module

This module defines the API routes for managing the application's cache system.
It provides endpoints for checking cache status and generating cache files.

Routes:
    - GET /cache: Check the status of the cache
    - GET /cache/generate_cache: Generate cache files for all datasets
"""

from fastapi import APIRouter, HTTPException
import os
from utils.constants import DATA_DIR
from models import ErrorType
from services.cache import check_cache, generate_cache_files

# Initialize the router with base URL and tags
router = APIRouter()
BASE_URL = "/cache"
router.prefix = BASE_URL
router.tags = [BASE_URL]

@router.get("/")
async def get_data():
    """
    Check the status of the cache and return cached data information.
    
    Returns:
        dict: Information about the cached data
        
    Raises:
        HTTPException:
            - 404: If the cache is not found
            - 500: If there's an error in the cache index
    """
    data_files = check_cache()
    if data_files == ErrorType.CACHE_NOT_FOUND.value:
        raise HTTPException(status_code=404, detail=ErrorType.CACHE_NOT_FOUND.value)
    elif data_files == ErrorType.CACHE_INDEX_ERROR.value:
        raise HTTPException(status_code=500, detail=ErrorType.CACHE_INDEX_ERROR.value)
    else:
        return data_files

@router.get("/generate_cache")
async def generate_cache():
    """
    Generate cache files for all available datasets.
    
    Returns:
        dict: Status information about the cache generation process
    """
    return generate_cache_files()

    