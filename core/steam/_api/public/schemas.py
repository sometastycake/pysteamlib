from pydantic import BaseModel


class ServerTime(BaseModel):
    server_time: int
    skew_tolerance_seconds: int
    large_time_jink: int
    probe_frequency_seconds: int
    adjusted_time_probe_frequency_seconds: int
    hint_probe_frequency_seconds: int
    sync_timeout: int
    try_again_seconds: int
    max_attempts: int


class ServerTimeResponse(BaseModel):
    response: ServerTime
