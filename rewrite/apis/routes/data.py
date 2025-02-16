from fastapi import APIRouter, HTTPException
import os
from utils.constants import DATA_DIR
from app_types import ErrorType
from services.data import get_available_datasets

router = APIRouter()

BASE_URL = "/data"

router.prefix = BASE_URL
router.tags = [BASE_URL]


@router.get("/")
async def get_data():
    return {"data": "data"}


@router.get("/list")
async def get_datasets():

    try:
        data_files = get_available_datasets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=ErrorType.INTERNAL_ERROR.value)
    
    if not data_files:
        raise HTTPException(status_code=404, detail=ErrorType.EMPTY_DATASET_DIR.value)

    return {"datasets": data_files}