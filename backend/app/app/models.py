from typing import List
from pydantic import BaseModel


class ServerMessageResponse(BaseModel):
    message: str


class GenerateRequest(BaseModel):
    url: str


class GenerateResponse(BaseModel):
    title: str
    itinerary: List
    # hashtags: List[str]


class Segments(BaseModel):
    from_time: float
    to_time: float
