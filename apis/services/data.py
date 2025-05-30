"""
Data Services Module

This module provides services for managing and accessing dataset information.
It handles operations like listing available datasets, retrieving dataset metadata,
and accessing geographical coordinates from datasets.
"""

import os
from uuid import uuid4
import xarray as xr
from utils.constants import DATA_DIR
from models import Dataset
from services.db import nc_db
from utils.logger import Logger

# Initialize logger for this module
logger = Logger(__name__)

def get_available_datasets():
    """
    Retrieve and register all available datasets in the data directory.
    
    This function:
    1. Scans the DATA_DIR for .nc files
    2. Registers new datasets in the database if not already present
    3. Returns all registered datasets
    
    Returns:
        list[Dataset]: List of all available datasets
        
    Note:
        New datasets are automatically registered with a UUID and added to the database.
    """
    data_files = os.listdir(DATA_DIR)
    logger.info(f"Found {len(data_files)} files in {DATA_DIR}")
    
    # Process each file in the data directory
    for file in data_files:
        if not file.endswith(".nc"):
            continue
            
        # Check if dataset is already registered
        dataset = nc_db.get_dataset_by_path(os.path.join(DATA_DIR, file))
        if not dataset:
            # Register new dataset
            dataset = Dataset()
            dataset["id"] = str(uuid4())
            dataset["name"] = file
            dataset["path"] = os.path.join(DATA_DIR, file)
            nc_db.add_dataset(dataset)

    return nc_db.db["datasets"]

def get_dataset_info_by_id(dataset_id: str):
    """
    Retrieve detailed information about a specific dataset.
    
    Args:
        dataset_id (str): The unique identifier of the dataset
        
    Returns:
        dict: Dictionary containing:
            - attrs: Dataset attributes
            - dims: Dataset dimensions
            - variables_info: Information about each variable and its dimensions
            
    Note:
        The dataset is opened in read-only mode with times not decoded for efficiency.
    """
    dataset = nc_db.get_dataset_by_id(dataset_id)
    data = xr.open_dataset(dataset["path"], decode_times=False)
    var_info = {var: list(data[var].dims) for var in data.data_vars}
    
    return {
        "attrs": data.attrs,
        "dims": data.dims,
        "variables_info": var_info,
        "lat": data["lat"].values.tolist(),
        "lon": data["lon"].values.tolist(),
    }

def get_dataset_lat_lon(dataset_id: str):
    """
    Retrieve latitude and longitude coordinates from a dataset.
    
    Args:
        dataset_id (str): The unique identifier of the dataset
        
    Returns:
        dict: Dictionary containing:
            - lat: List of latitude values
            - lon: List of longitude values
            
    Note:
        The dataset is opened in read-only mode with times not decoded for efficiency.
    """
    dataset = nc_db.get_dataset_by_id(dataset_id)
    data = xr.open_dataset(dataset["path"], decode_times=False)
    return {
        "lat": data["lat"].values.tolist(),
        "lon": data["lon"].values.tolist(),
    }