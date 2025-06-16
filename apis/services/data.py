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
from models import Dataset, DatasetInfoResponse
from utils.logger import Logger
from services.db import nc_db

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
    # data_files = os.listdir(DATA_DIR)
    # logger.info(f"Found {len(data_files)} files in {DATA_DIR}")

    # Process each file in the data directory
    # for file in data_files:
        # if not file.endswith(".nc"):
            # continue

    dataset_exists = nc_db.get_dataset_by_name(DATA_DIR)
    
    if not dataset_exists:
        # Register new dataset if it doesn't exist
        new_dataset = Dataset(id=str(uuid4()), name=DATA_DIR, path=DATA_DIR)
        nc_db.add_dataset(new_dataset)
        logger.info(f"Registered new dataset: {new_dataset['name']}")
        
    TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), '../../test_data')
    
    dataset_exists = nc_db.get_dataset_by_name(TEST_DATA_DIR)
    
    if not dataset_exists:
        # Register new dataset if it doesn't exist
        new_dataset = Dataset(id=str(uuid4()), name=TEST_DATA_DIR, path=TEST_DATA_DIR)
        nc_db.add_dataset(new_dataset)
        logger.info(f"Registered new dataset: {new_dataset['name']}")

    return nc_db.db["datasets"]


def get_dataset_info_by_id(dataset_id: str) -> DatasetInfoResponse:
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
    if not dataset:
        raise ValueError(f"Dataset with ID {dataset_id} not found.")
    
    data_files = os.listdir(dataset["path"])
    data_files = [os.path.join(dataset["path"], f) for f in data_files if f.endswith(".nc")]
    data = xr.open_mfdataset(data_files, decode_times=False, engine="netcdf4")
    var_info = {var: list(data[var].dims) for var in data.data_vars}

    return DatasetInfoResponse(
        attrs=data.attrs,
        dims=dict(data.dims),
        variables_info=var_info,
        lat=[float(data["lat"].values[0]), float(data["lat"].values[-1])],
        lon=[float(data["lon"].values[0]), float(data["lon"].values[-1])],
    )


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
