"""
Session Routes Module

This module defines the API routes for managing user sessions in the application.
It provides endpoints for creating, retrieving, and listing sessions.

Routes:
    - GET /session/create: Create a new session
    - GET /session/get/{session_id}: Retrieve a specific session
    - GET /session/list: List all available sessions
"""

import os
from fastapi import APIRouter, HTTPException
from uuid import uuid4
from models import Session
from datetime import datetime, timezone
from models import ErrorType
from services.db import nc_db

# Initialize the router with base URL and tags
router = APIRouter()
BASE_URL = "/session"
router.prefix = BASE_URL
router.tags = [BASE_URL]

@router.get("/create")
async def create_session(dataset_id=None, parent_id: str = None):
    """
    Create a new session with the specified dataset and optional parent session.
    
    Args:
        dataset_id (str, optional): The ID of the dataset to associate with the session
        parent_id (str, optional): The ID of the parent session if this is a child session
        
    Returns:
        dict: The newly created session object
        
    Raises:
        HTTPException:
            - 400: If dataset_id is not provided
    """
    if not dataset_id:
        raise HTTPException(status_code=400, detail=ErrorType.INVALID_DATASET.value)
    
    # Create a new session with default values
    session = Session()
    session["id"] = uuid4()
    session["parent_id"] = parent_id
    session["dataset_id"] = dataset_id
    session["created_at"] = datetime.now(timezone.utc)
    session["params"] = None
    session["cache"] = None
    
    return nc_db.add_session(session)

@router.get("/get/{session_id}")
async def get_session(session_id: str):
    """
    Retrieve a specific session by its ID.
    
    Args:
        session_id (str): The unique identifier of the session to retrieve
        
    Returns:
        dict: The session object
        
    Raises:
        HTTPException:
            - 404: If the session is not found
    """
    session = nc_db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=ErrorType.SESSION_NOT_FOUND.value)
    return session

@router.get("/list")
async def list_sessions():
    """
    Retrieve a list of all available sessions.
    
    Returns:
        dict: A dictionary containing all sessions in the database
    """
    return nc_db.db['sessions']