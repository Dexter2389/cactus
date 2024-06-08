from typing import List
from pydantic import BaseModel


class ServerMessageResponse(BaseModel):
    message: str


class GenerateResponse(BaseModel):
    title: str
    itinerary: List[str]
    hashtags: List[str]
