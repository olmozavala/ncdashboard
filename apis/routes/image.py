"""
Image Routes Module

This module defines the API routes for handling image generation and retrieval in the application.
It provides endpoints for generating new images and accessing cached images.

Routes:
    - GET /image: Root endpoint (deprecated)
    - POST /image/generate: Generate a new image based on parameters
    - GET /image/cached_image/{dataset_id}/{image_id}: Retrieve a cached image
"""

import os
from fastapi import APIRouter, Response, HTTPException
from models import GenerateImageRequest, ErrorType
from services.image import generate_image
from utils.constants import CACHE_DIR

# Initialize the router with base URL and tags
router = APIRouter()
BASE_URL = "/image"
router.prefix = BASE_URL
router.tags = [BASE_URL]

# TODO: Remove this endpoint as it's deprecated
@router.get("/")
async def get_image():
    """
    Root endpoint for the image routes (deprecated).
    
    Returns:
        dict: A simple response indicating the image route is active
    """
    return {"image": "image"}

@router.post("/generate")
async def generate_image_endpoint(params: GenerateImageRequest):
    """
    Generate a new image based on the provided parameters.
    
    Args:
        params (GenerateImageRequest): The parameters for image generation including:
            - dataset: The dataset ID
            - time_index: The time index for the data
            - depth_index: The depth index for the data
            - variable: The variable to visualize
            
    Returns:
        Response: The generated image as a JPEG response
        
    Raises:
        HTTPException:
            - 500: If there's an error during image generation
    """
    try:
        image_data = generate_image(
            params["dataset"],
            params["time_index"],
            params["depth_index"],
            params["variable"],
        )
        return Response(content=image_data, media_type="image/jpeg")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=ErrorType.INTERNAL_ERROR.value)

@router.get("/cached_image/{dataset_id}/{image_id}")
async def get_image(dataset_id: str, image_id: str):
    """
    Retrieve a cached image by its dataset ID and image ID.
    
    Args:
        dataset_id (str): The ID of the dataset
        image_id (str): The ID of the cached image
        
    Returns:
        Response: The cached image as a JPEG response
        
    Raises:
        HTTPException:
            - 404: If the requested image is not found in the cache
    """
    # Construct the path to the cached image
    image_path = os.path.join(CACHE_DIR, dataset_id, f"{image_id}.jpeg")
    
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail=ErrorType.IMAGE_NOT_FOUND.value)
    
    # Read and return the cached image
    with open(image_path, "rb") as image_file:
        image_data = image_file.read() 
        return Response(content=image_data, media_type="image/jpeg")
    
