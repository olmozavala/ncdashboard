import os
from fastapi import APIRouter, HTTPException
from uuid import uuid4
from models import Session
from datetime import datetime, timezone
from models import ErrorType
from services.db import nc_db

router = APIRouter()


BASE_URL = "/session"

router.prefix = BASE_URL
router.tags = [BASE_URL]

@router.get("/create")
async def create_session(dataset_id=None,parent_id: str = None):
    
    if not dataset_id:
        raise HTTPException(status_code=400, detail=ErrorType.INVALID_DATASET.value)
    
    session = Session()
    session["id"] = uuid4()
    session["parent_id"] = parent_id
    session["dataset_id"] = dataset_id
    session["created_at"] = datetime.now(timezone.utc)
    session["params"] = None
    session["cache"] = None
    
    
    
    return nc_db.add_session(session)

@router.get("/get/{session_id}")
async def get_session(session_id:str):
    session = nc_db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=ErrorType.SESSION_NOT_FOUND.value)
    return session

@router.get("/list")
async def list_sessions():
    return nc_db.db['sessions']