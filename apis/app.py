"""
FastAPI Application for NC Dashboard

This module serves as the main entry point for the NC Dashboard API server.
It sets up the FastAPI application, configures middleware, and dynamically loads
all route modules from the routes directory. The application also serves the
frontend static files and handles SPA (Single Page Application) routing.

Key Features:
- Dynamic route loading from the routes directory
- CORS middleware configuration
- Static file serving for the frontend
- SPA routing support
- Database lifecycle management
"""

from typing import Annotated
from fastapi import Depends, FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import importlib
import sys
import os
from contextlib import asynccontextmanager
from services.db import nc_db


# Add the current script's directory to the system path for module imports
sys.path.append(os.path.dirname(__file__))


# Dynamically import and collect all routers from the routes module
router_module = importlib.import_module(".", package="routes")
routers = [
    getattr(router_module, var)
    for var in dir(router_module)
    if not var.startswith("__")
]
routers = [router for router in routers if isinstance(router, APIRouter)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for database operations.
    
    This context manager handles the database lifecycle:
    - Loads the database on application startup
    - Saves the database on application shutdown
    
    Args:
        app (FastAPI): The FastAPI application instance
    
    Yields:
        None: Allows the application to run between startup and shutdown
    """
    nc_db.load_db()
    yield
    await nc_db.save_db()


# Initialize the FastAPI application with lifespan management
app = FastAPI(lifespan=lifespan)

# Configure CORS middleware
# Allow requests from any origin for development purposes
origins: list[str] = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up static file serving for the frontend
dist_path = os.path.join(os.path.dirname(__file__), "../web/dist/")
app.mount(
    "/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets"
)


@app.get("/")
async def serve_index():
    """
    Serve the main index.html file for the SPA.
    
    Returns:
        FileResponse: The index.html file from the dist directory
    """
    return FileResponse(os.path.join(dist_path, "index.html"))


# Register all dynamically loaded routers with the /api prefix
for router in routers:
    app.include_router(router, prefix="/api")
    
@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    """
    Handle SPA routing and static file serving.
    
    This endpoint serves static files if they exist, otherwise returns the index.html
    to support client-side routing in the SPA.
    
    Args:
        full_path (str): The requested path
        
    Returns:
        FileResponse: Either the requested static file or index.html for SPA routing
    """
    target_file = os.path.join(dist_path, full_path)
    if not full_path.startswith("api") and os.path.isfile(os.path.join(dist_path, full_path)):
        return FileResponse(os.path.join(dist_path, full_path))
    return FileResponse(os.path.join(dist_path, "index.html"))


if __name__ == "__main__":
    # Run the application using uvicorn when executed directly
    uvicorn.run(app, host="127.0.0.1", port=3030)
