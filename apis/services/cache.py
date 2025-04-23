"""
Cache Services Module

This module provides services for managing the application's caching system.
It handles operations for checking cache status, generating cache files, and managing cached visualizations.
"""

import os
import json
from uuid import uuid4 
from datetime import datetime, timezone
import xarray as xr
from utils.constants import CACHE_DIR, DATA_DIR, CACHE_INDEX_FILE
from models import ErrorType, CacheIndex, CachedDataset 

from .image import generate_image

def check_cache():
    """
    Check the status of the cache system.
    
    Returns:
        CacheIndex: The cache index if it exists
        str: ErrorType value if there's an error:
            - CACHE_INDEX_ERROR: If cache index file is missing
            - CACHE_NOT_FOUND: If cache directory is missing
            - INTERNAL_ERROR: If an unexpected error occurs
    """
    try:
        if os.path.exists(CACHE_DIR):
            cache_index_path = CACHE_INDEX_FILE
            if os.path.exists(cache_index_path):
                with open(cache_index_path, 'r') as cache_file:
                    cache_data: CacheIndex = json.load(cache_file)
                    return cache_data
            else:
                return ErrorType.CACHE_INDEX_ERROR.value
        else:
            return ErrorType.CACHE_NOT_FOUND.value
    except Exception as e:
        return ErrorType.INTERNAL_ERROR.value

def generate_cache_files(dataset_name: str = None):
    """
    Generate cache files for all or a specific dataset.
    
    This function:
    1. Creates cache directory structure
    2. Generates visualizations for each time and depth index
    3. Creates a cache index file
    
    Args:
        dataset_name (str, optional): Specific dataset to cache. If None, caches all datasets.
        
    Returns:
        CacheIndex: The generated cache index containing all cached datasets
        
    Note:
        Currently generates only the first time and depth index (t=0, z=0) for each dataset.
    """
    data_files = os.listdir(DATA_DIR)
    
    # Initialize cache index
    index: CacheIndex = {
        'cache': []
    }
    
    # Create metadata for each dataset
    for file in data_files:
        dataset_metadata: CachedDataset = {
            'id': str(uuid4()), 
            "created_at": datetime.now(timezone.utc),
            'description': "",
            "name": file,
            'images': []
        }
        
        index['cache'].append(dataset_metadata)
    
    # Create cache directory structure
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # Process each dataset
    for d in index['cache']:
        # Create dataset-specific cache directory
        dataset_path = os.path.join(CACHE_DIR, d['id'])
        os.makedirs(dataset_path, exist_ok=True)
        
        # Load dataset
        data = xr.open_dataset(os.path.join(DATA_DIR, d['name']), decode_times=False)
        
        # Generate images for each time and depth index
        for t in range(1):  # Currently only generating first time index
            for z in range(1):  # Currently only generating first depth index
                # Create image metadata
                image_index = {
                    'id': str(uuid4()),
                    'dataset_id': d['id'],
                    'variable': f'water_u&t={t}&z={z}',
                    'file_path': os.path.join(dataset_path, f"{t}_{z}.jpeg")
                }
                
                # Generate and save image
                image_data = generate_image(d['name'], t, z, data=data)
                image_path = os.path.join(dataset_path, f"{image_index['id']}.jpeg")
                with open(image_path, 'wb') as image_file:
                    image_file.write(image_data)
                d['images'].append(image_index)
    
    # Save cache index
    with open(CACHE_INDEX_FILE, 'w') as cache_file:
        json.dump(index, cache_file, indent=4, default=str)
    
    return index