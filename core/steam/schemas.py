from pydantic import BaseModel


class BaseSteamResponse(BaseModel):
    success: int
