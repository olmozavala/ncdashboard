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


# Add the current script's directory to the system path
sys.path.append(os.path.dirname(__file__))


# Dynamically import the `routes` module and get all routers
router_module = importlib.import_module(".", package="routes")  # Import module
routers = [
    getattr(router_module, var)
    for var in dir(router_module)
    if not var.startswith("__")
]
routers = [router for router in routers if isinstance(router, APIRouter)]


# Create an instance of the database


@asynccontextmanager
async def lifespan(app: FastAPI):
    nc_db.load_db()
    yield
    await nc_db.save_db()


app = FastAPI(lifespan=lifespan)

# Configure CORS middleware to allow requests from any origin
origins: list[str] = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

dist_path = os.path.join(os.path.dirname(__file__), "../web/dist/")
app.mount(
    "/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets"
)


@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(dist_path, "index.html"))


# Register all dynamically loaded routers
for router in routers:
    app.include_router(router, prefix="/api")
    
@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    target_file = os.path.join(dist_path, full_path)
    if not full_path.startswith("api") and os.path.isfile(os.path.join(dist_path, full_path)):
        return FileResponse(os.path.join(dist_path, full_path))
    return FileResponse(os.path.join(dist_path, "index.html"))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3030)
