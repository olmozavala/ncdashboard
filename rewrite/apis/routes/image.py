import os
from fastapi import APIRouter, Response, HTTPException
from models import GenerateImageRequest, ErrorType
from services.image import generate_image
from utils.constants import CACHE_DIR

router = APIRouter()

BASE_URL = "/image"

router.prefix = BASE_URL
router.tags = [BASE_URL]


# TODO: Remove this endpoint
@router.get("/")
async def get_image():
    return {"image": "image"}


@router.post("/generate")
async def generate_image_endpoint(params: GenerateImageRequest):
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
    
    # read the image from the cache
    image_path = os.path.join(CACHE_DIR, dataset_id, f"{image_id}.jpeg")
    
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail=ErrorType.IMAGE_NOT_FOUND.value)
    
    with open(image_path, "rb") as image_file:
        image_data = image_file.read() 
        return Response(content=image_data, media_type="image/jpeg")
    
