from pydantic import BaseModel


class UnlockVerifyMessage(BaseModel):
    """Schema for Kafka message to verify unlock"""

    attempt_id: str
    photo_url: str
    latitude: float
    longitude: float
    unlock_radius_meters: int
    photo_radius_meters: int


class UnlockVerifyResult(BaseModel):
    """Schema for Kafka message with verification result"""

    attempt_id: str
    photo_url: str
    success: bool
    similarity_score: float | None = None
    error: str | None = None
