"""
Data Routes Module

This module defines the API routes for handling dataset operations in the application.
It provides endpoints for listing available datasets, retrieving dataset information,
and accessing dataset metadata.

Routes:
    - GET /data/list: List all available datasets
    - GET /data/get: Retrieve a specific dataset by ID
    - GET /data/info: Get detailed information about a dataset
    - GET /data/info/lat_lon: Get latitude and longitude information for a dataset
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os
from utils.constants import DATA_DIR
from models import ErrorType
from services.data import get_available_datasets, get_dataset_info_by_id, get_dataset_lat_lon
from services.db import nc_db

# Initialize the router with base URL and tags
router = APIRouter()
BASE_URL = "/data"
router.prefix = BASE_URL
router.tags = [BASE_URL]

@router.get("/")
async def get_data():
    """
    Root endpoint for the data routes.
    
    Returns:
        dict: A simple response indicating the data route is active
    """
    return {"data": "data"}

@router.get("/list")
async def get_datasets():
    """
    Retrieve a list of all available datasets.
    
    Returns:
        dict: A dictionary containing the list of available datasets
        
    Raises:
        HTTPException: 
            - 500: If there's an internal server error
            - 404: If no datasets are found
    """
    try:
        data_files = get_available_datasets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=ErrorType.INTERNAL_ERROR.value)
    
    if not data_files:
        raise HTTPException(status_code=404, detail=ErrorType.EMPTY_DATASET_DIR.value)

    return {"datasets": data_files}

@router.get("/get")
async def get_dataset(dataset_id: str = None):
    """
    Retrieve a specific dataset by its ID.
    
    Args:
        dataset_id (str, optional): The unique identifier of the dataset
        
    Returns:
        dict: The dataset information
        
    Raises:
        HTTPException:
            - 400: If dataset_id is not provided
            - 404: If dataset is not found
            - 500: If there's an internal server error
    """
    if not dataset_id:
        raise HTTPException(status_code=400, detail=ErrorType.INVALID_DATASET.value)
    try:    
        dataset = nc_db.get_dataset_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail=ErrorType.DATASET_NOT_FOUND.value)
        return dataset
    except Exception as e:
        raise HTTPException(status_code=500, detail=ErrorType.INTERNAL_ERROR.value)

@router.get("/info")
async def get_dataset_info(dataset_id: str = None):
    """
    Get detailed information about a specific dataset.
    
    Args:
        dataset_id (str, optional): The unique identifier of the dataset
        
    Returns:
        dict: Detailed information about the dataset
        
    Raises:
        HTTPException:
            - 400: If dataset_id is not provided
            - 500: If there's an internal server error
    """
    if not dataset_id:
        raise HTTPException(status_code=400, detail=ErrorType.INVALID_DATASET.value)
    try:    
        return get_dataset_info_by_id(dataset_id)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=ErrorType.INTERNAL_ERROR.value)
    
@router.get("/info/lat_lon")
async def get_lat_lon(dataset_id: str = None):
    """
    Get latitude and longitude information for a specific dataset.
    
    Args:
        dataset_id (str, optional): The unique identifier of the dataset
        
    Returns:
        dict: Latitude and longitude information for the dataset
        
    Raises:
        HTTPException:
            - 400: If dataset_id is not provided
            - 500: If there's an internal server error
    """
    if not dataset_id:
        raise HTTPException(status_code=400, detail=ErrorType.INVALID_DATASET.value)
    try:    
        return get_dataset_lat_lon(dataset_id)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=ErrorType.INTERNAL_ERROR.value)