import logging
import os
import aiofiles
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from app.models import ServerMessageResponse, GenerateResponse

from app.logger_utils import setup_logging

DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"
LOGLEVEL = logging.DEBUG if DEBUG_MODE else logging.INFO

# INIT SERVER
setup_logging(LOGLEVEL)
if DEBUG_MODE:
    logging.warning("Debug mode is enabled")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    # Open DB connection

    yield
    # Clean up the ML models and release the resources
    # Close DB connection


middleware = [
    Middleware(
        CORSMiddleware,
        allow_headers=["*"],
        allow_origins=["*"],
        allow_methods=["*"],
    ),
]

app = FastAPI(
    title="Cactus API",
    docs_url="/docs",
    redoc_url=None,
    middleware=middleware,
    lifespan=lifespan,
)

router = APIRouter(prefix="/api")


# ENDPOINTS
@app.get("/")
async def get_version():
    return JSONResponse(
        {"version": f"{app.__version__}", "message": "Cactus Backend API"}
    )


@app.get("/health")
async def health_check():
    return JSONResponse({"health_check": "pass"})


@app.post(
    "/upload_file",
    response_model=ServerMessageResponse,
    status_code=200,
)
async def upload_file(file: UploadFile):
    # Save the file to disk
    storage_folder = "/mock_storage"
    async with aiofiles.open(
        f"{storage_folder}/{file.filename}", mode="wb"
    ) as uploaded_file:
        await uploaded_file.write(file.file.read())

    return ServerMessageResponse(message=f"File uploaded successfully!")


@app.post("/generate", status_code=200)
async def generate():
    return {
        "generate_response": GenerateResponse(),
        "reel_file": FileResponse("reel.mp4", media_type="video/mp4"),
    }


app.include_router(router)
