from fastapi import APIRouter, HTTPException
import os
from utils.constants import DATA_DIR
from models import ErrorType
from services.cache import check_cache, generate_cache_files

router = APIRouter()

BASE_URL = "/cache"


router.prefix = BASE_URL
router.tags = [BASE_URL]


@router.get("/")
async def get_data():

    data_files = check_cache()
    if data_files == ErrorType.CACHE_NOT_FOUND.value:
        raise HTTPException(status_code=404, detail=ErrorType.CACHE_NOT_FOUND.value)
    elif data_files == ErrorType.CACHE_INDEX_ERROR.value:
        raise HTTPException(status_code=500, detail=ErrorType.CACHE_INDEX_ERROR.value)
    else:
        return data_files


@router.get("/generate_cache")
async def generate_cache():
    return generate_cache_files()

    