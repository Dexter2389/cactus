import logging
import os
import aiofiles
from pathlib import Path
import json
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, UploadFile
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from app.generate_reel import (
    fetch_video_title,
    get_video_id_from_twelve_labs_index,
    generate_segment_itinerary,
    parse_segment_itinerary_into_json,
    select_segments_of_interest,
    stitch_segments_into_single_video,
)
from app.middleware import ProcessTimeMiddleware
from app.models import ServerMessageResponse, GenerateResponse, GenerateRequest

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
    Middleware(ProcessTimeMiddleware),
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
    return JSONResponse({"version": "v0.1", "message": "Cactus Backend API"})


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


@app.get("/stream_file/{file_id}", response_class=FileResponse)
async def stream_file(file_id: str):
    return f"/mock_storage/{file_id}_reel.mp4"


@app.post("/generate", status_code=200)
async def generate(request: GenerateRequest):
    file_name, youtube_video_id = fetch_video_title(request.url)
    if (
        Path(f"/mock_storage/{youtube_video_id}_reel.mp4").is_file()
        and Path(f"/mock_storage/{youtube_video_id}_reel.json").is_file()
    ):
        reel_video_path = f"/mock_storage/{youtube_video_id}_reel.mp4"
        with open(f"/mock_storage/{youtube_video_id}_reel.json", mode="r") as json_file:
            generated_response_dict = json.load(json_file)
        generated_response = GenerateResponse(**generated_response_dict)

    else:
        video_id = await get_video_id_from_twelve_labs_index(file_name=file_name)
        segment_itinerary = await generate_segment_itinerary(video_id=video_id)
        parse_segment_itinerary = await parse_segment_itinerary_into_json(
            segment_itinerary=segment_itinerary
        )
        segments_of_interest = await select_segments_of_interest(
            segment_json=parse_segment_itinerary.get("itinerary"), video_url=request.url
        )
        reel_video_path = stitch_segments_into_single_video(
            segments=segments_of_interest,
            output_path=f"/mock_storage/{youtube_video_id}_reel.mp4",
        )
        generated_response = GenerateResponse(
            title=file_name, itinerary=parse_segment_itinerary.get("itinerary")
        )

        with open(f"/mock_storage/{youtube_video_id}_reel.json", mode="w") as json_file:
            json_file.write(generated_response.model_dump_json())
    # reel_path = convert_video_to_reel(
    #     video_path=reel_video_path,
    #     output_path=f"/mock_storage/{youtube_video_id}_reel.mp4",
    # )

    # return {
    #     "generate_response": generated_response,
    #     "reel_file_id": FileResponse(reel_video_path, media_type="video/mp4"),
    # }
    return {
        "generate_response": generated_response,
        "reel_file_id": youtube_video_id,
    }
    # return ServerMessageResponse(message=f"Worked")


app.include_router(router)
