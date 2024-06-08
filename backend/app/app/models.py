from pydantic import BaseModel


class ServerMessageResponse(BaseModel):
    message: str


class GenerateResponse(BaseModel):
    pass
