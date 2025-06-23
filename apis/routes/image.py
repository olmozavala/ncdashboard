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
from models import (
    GenerateImageRequest1D,
    ErrorType,
    GenerateImageRequest4D,
    GenerateImageRequest3D,
    GenerateImageRequestTransect,
)
from services.image import (
    generate_image,
    generate_image_3D,
    generate_image_1d,
    generate_transect_image,
)
from services.db import nc_db


# Initialize the router with base URL and tags
router = APIRouter()
BASE_URL = "/image"
router.prefix = BASE_URL
router.tags = [BASE_URL]



@router.post("/generate/1d", name="generate_image_1d")
async def generate_image_endpoint1d(params: GenerateImageRequest1D):
    image_data = generate_image_1d(params)
    return Response(content=image_data, media_type="image/jpeg")



@router.post("/generate/3d", name="generate_image_3d")
async def generate_3d_image_endpoint(params: GenerateImageRequest3D):
    """
    Generate a 3D image based on the provided parameters.

    Args:
        params (GenerateImageRequest): The parameters for image generation including:
            - dataset: The dataset ID
            - time_index: The time index for the data
            - depth_index: The depth index for the data
            - variable: The variable to visualize

    Returns:
        Response: The generated 3D image as a JPEG response

    Raises:
        HTTPException:
            - 500: If there's an error during image generation
    """

    try:
        # Generate the 3D image using the provided parameters
        image_data = generate_image_3D(params)
        return Response(content=image_data, media_type="image/jpeg")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=ErrorType.INTERNAL_ERROR.value)


@router.post("/generate/4d", name="generate_image_4d")
async def generate_image_endpoint(params: GenerateImageRequest4D):
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
    dataset = nc_db.get_dataset_by_id(params.dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail=ErrorType.DATASET_NOT_FOUND.value)

    try:
        # Generate the image using the provided parameters
        image_data = generate_image(params)
        return Response(content=image_data, media_type="image/jpeg")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=ErrorType.INTERNAL_ERROR.value)


# ---------------------------------------------------------------------------
# Transect Image Generation Endpoint
# ---------------------------------------------------------------------------


@router.post("/generate/4d/transect", name="generate_transect_image")
async def generate_transect_image_endpoint(params: GenerateImageRequestTransect):
    """
    Generate a transect plot image based on the provided parameters.

    Args:
        params (GenerateImageRequestTransect): Parameters including dataset id, variable,
            transect start/end coordinates, time index, and depth index.

    Returns:
        Response: PNG image containing the transect plot.

    Raises:
        HTTPException:
            404: Dataset not found.
            500: Internal error during image generation.
    """

    # Validate dataset existence early for clearer 404 handling
    dataset = nc_db.get_dataset_by_id(params.dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail=ErrorType.DATASET_NOT_FOUND.value)

    try:
        image_data = generate_transect_image(params)
        # Return PNG bytes
        return Response(content=image_data, media_type="image/png")
    except Exception as e:
        # Log the error (here we simply print; replace with proper logging if available)
        print(e)
        raise HTTPException(status_code=500, detail=ErrorType.INTERNAL_ERROR.value)

