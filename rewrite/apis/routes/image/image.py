from fastapi import APIRouter

router = APIRouter()

BASE_URL = "/image"

@router.get(BASE_URL)
async def get_data():
    return {"image": "image"}