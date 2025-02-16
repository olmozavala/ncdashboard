from typing import Annotated
from fastapi import Depends, FastAPI, APIRouter
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import importlib 
import sys
import os 

# Add the current script's directory to the system path
sys.path.append(os.path.dirname(__file__))

# Dynamically import the `routes` module and get all routers
router_module = importlib.import_module(".", package="routes")  # Import module
routers = [getattr(router_module, var) for var in dir(router_module) if not var.startswith("__")]
routers = [router for router in routers if isinstance(router, APIRouter)]


app = FastAPI()

# Configure CORS middleware to allow requests from any origin
origins: list[str] = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello Worrrrld"}

# Register all dynamically loaded routers
for router in routers:
    app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3030)