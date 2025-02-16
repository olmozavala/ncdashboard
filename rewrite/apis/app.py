from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import pkgutil

app = FastAPI()


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


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3030)