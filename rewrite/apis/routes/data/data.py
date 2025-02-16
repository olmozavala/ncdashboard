from fastapi import APIRouter, HTTPException
import os
from utils.constants import DATA_DIR
from app_types import ErrorType

router = APIRouter()

BASE_URL = "/data"

router.prefix = BASE_URL
router.tags = [BASE_URL]


@router.get("/")
async def get_data():
    return {"data": "data"}


@router.get("/list")
async def get_data_list():

    if not os.path.exists(DATA_DIR):
        raise HTTPException(
            500,
            detail={
                "error_type": ErrorType.INTERNAL_ERROR.value,
                "msg": "Data directory does not exist",
            },
        )

    data_files = os.listdir(DATA_DIR)
    return {"data": data_files}
