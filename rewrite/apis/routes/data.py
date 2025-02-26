from fastapi import APIRouter, HTTPException
import os
from utils.constants import DATA_DIR
from models import ErrorType
from services.data import get_available_datasets
from services.db import nc_db

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

@router.get("/get")
async def get_dataset(dataset_id:str = None):
    if not dataset_id:
        raise HTTPException(status_code=400, detail=ErrorType.INVALID_DATASET.value)
    try:    
        dataset = nc_db.get_dataset_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail=ErrorType.DATASET_NOT_FOUND.value)
        return dataset
    except Exception as e:
        raise HTTPException(status_code=500, detail=ErrorType.INTERNAL_ERROR.value)